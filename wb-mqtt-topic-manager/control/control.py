import json
from typing import List

from constance import ErrorType, QosType
from control.base import BaseMeta
from control.control_type import ControlType
from device import Device


class Control:
    def __init__(self, device: Device, control_id: str):
        self.device = device
        self.control_id = control_id

    @property
    def control_topic_value(self) -> dict:
        """Топик значения контрола"""
        return f'/devices/{self.device.id}/{self.control_id}'

    @property
    def control_topic_change_value(self) -> dict:
        """Топик смены значения контрола"""
        return f'/devices/{self.device.id}/{self.control_id}/on'

    @property
    def control_topic_meta(self) -> dict:
        """Топик информации о контроле"""
        return f'/devices/{self.device.id}/{self.control_id}/meta'

    @property
    def control_topic_meta_error(self) -> dict:
        """Топик ошибок контрола"""
        return f'/devices/{self.device.id}/{self.control_id}/meta/error'


class DriverControl(Control):
    """Класс контрола для драйвера"""

    def __init__(self, device: Device, control_id: str, initial_value, meta: BaseMeta):
        super().__init__(device=device, control_id=control_id)
        self._value = initial_value
        self.meta = meta
        self.meta_error: str = ''
        self._publish_meta()
        self._subcribe_on_change()

        # Callbacks
        self._callbacks: List[callable] = []

    def _publish_meta(self):
        """Публикация данных контрола"""
        # Первоначальное значение
        self.device.client.publish(
            topic=self.control_topic_value,
            payload=self._value,
            qos=QosType.QOS_ONE,
            retain=True,
        )
        # Метаданные
        self.device.client.publish(
            topic=self.control_topic_meta,
            payload=self.meta.to_dict(),
            qos=QosType.QOS_ONE,
            retain=True,
        )
        # Метаданные ошибок
        self.device.client.publish(
            topic=self.control_topic_meta_error,
            payload='',
            qos=QosType.QOS_ONE,
            retain=True,
        )

        # Данных для обратной совместимости
        for meta_value, old_conventions_topic in self.old_conventions_data:
            self.device.client.publish(
                topic=old_conventions_topic,
                payload=meta_value,
                qos=QosType.QOS_ONE,
                retain=True,
            )

    @property
    def old_conventions_data(self) -> list:
        """Поля для обратной совместимости"""
        return [
            (self.meta.type.value, f'{self.control_topic_meta}/type'),
            (self.meta.order, f'{self.control_topic_meta}/order'),
            (self.meta.readonly, f'{self.control_topic_meta}/readonly'),
        ]

    def _subcribe_on_change(self):
        """Подписка на топик on"""
        if not self.meta.readonly:

            def on_change(topic, payload):
                for callback_func in self._callbacks:
                    callback_func(payload)

            self.device.client.subscribe(
                self.control_topic_change_value, on_change, qos=QosType.QOS_ZERO
            )

    def on_change_on(self, callback):
        """Декоратор для подписки на изменения значения"""
        if not self.meta.readonly:
            self._callbacks.append(callback)

    def publish_error(self, error: ErrorType):
        """Публикация ошибки в топик meta/error"""
        if error in ErrorType.ERRORS:
            if error not in self.meta_error:
                self.meta_error += error
                self.device.client.publish(
                    topic=self.control_topic_meta_error,
                    payload=self.meta_error,
                    qos=QosType.QOS_ONE,
                    retain=True,
                )
            return True

        return False

    def delete_error(self, error: ErrorType):
        """Удаление ошибки из топика meta/error"""
        if error in ErrorType.ERRORS:
            if error in self.meta_error:
                self.meta_error = self.meta_error.replace(error, '')
                self.device.client.publish(
                    topic=self.control_topic_meta_error,
                    payload=self.meta_error,
                    qos=QosType.QOS_ONE,
                    retain=True,
                )
            return True

        return False

    def change_value(self, value):
        """Изменение значения контрола"""
        if value != self._value and self._validate_value(value):
            self._value = value

            return self.device.client.publish(
                topic=self.control_topic_value,
                payload=value,
                qos=QosType.QOS_ONE,
                retain=True,
            )
        return False

    def _validate_value(self, value):
        """Валидация входящего значения"""
        return value in ['0', '1']

    @property
    def value(self):
        """Текущее значение контрола"""
        return self._value


class RangeDriverControl(DriverControl):
    @property
    def old_conventions_data(self) -> list:
        """Поля для обратной совместимости, переопределен для min/max"""
        return [
            (self.meta.type.value, f'{self.control_topic_meta}/type'),
            (self.meta.order, f'{self.control_topic_meta}/order'),
            (self.meta.readonly, f'{self.control_topic_meta}/readonly'),
            (self.meta.min_value, f'{self.control_topic_meta}/min'),
            (self.meta.max_value, f'{self.control_topic_meta}/max'),
        ]

    def _validate_value(self, value):
        """Валидация входящего значения, переопределен для работы с min/max"""
        return self.meta.min_value <= value <= self.meta.max_value


class ObserverControl(Control):
    """Класс контрола для наблюдателя"""

    def __init__(self, device: Device, control_id: str):
        super().__init__(device=device, control_id=control_id)
        self._value = None
        self.meta: dict = {}
        self.meta_error: str = ''

        # Callbacks
        self._change_value_callbacks: List[callable] = []
        self._meta_error_callbacks: List[callable] = []

        # Подписка на метаданные
        self.get_meta()
        self._subcribe_on_value()
        self._subcribe_meta_error()

    def _subcribe_on_value(self):
        """Подписка на топик значения контрола"""

        def on_change(topic, payload):
            if self._value != payload:
                self._value = (
                    payload
                    if self.meta.get('type') != ControlType.RANGE.value
                    else int(payload)
                )

                for callback_func in self._change_value_callbacks:
                    callback_func(payload)

        self.device.client.subscribe(
            self.control_topic_value, on_change, qos=QosType.QOS_ONE
        )

    def on_change_value(self, callback):
        """Декоратор для подписки на изменения значения"""
        self._change_value_callbacks.append(callback)

    def on(self, value):
        """Отправка сигнала на изменение значения контрола"""
        if self.meta and not self.meta['readonly'] and self._validate_value(value):
            return self.device.client.publish(
                topic=self.control_topic_change_value,
                payload=value,
                qos=QosType.QOS_ZERO,
            )
        return False

    def _validate_value(self, value):
        """Валидация входящего значения"""
        control_type = self.meta.get('type')

        if control_type in [
            ControlType.SWITCH.value,
            ControlType.ALARM.value,
            ControlType.PUSHBUTTON.value,
        ]:
            return value in ['0', '1']

        if control_type == ControlType.RANGE.value:
            return self.meta.get('min') <= value <= self.meta.get('max')

    def get_meta(self) -> dict:
        """Получение meta контрола"""

        def on_meta(topic, payload):
            self.meta = json.loads(payload) if payload else {}

        self.device.client.subscribe(
            self.control_topic_meta, on_meta, qos=QosType.QOS_ONE
        )

        return self.meta

    def _subcribe_meta_error(self):
        """Подписка на meta/error контрола"""

        def on_meta_error(topic, payload):
            if self.meta_error != payload:
                for callback_func in self._meta_error_callbacks:
                    callback_func(payload)

            self.meta_error = payload

        self.device.client.subscribe(
            self.control_topic_meta_error, on_meta_error, qos=QosType.QOS_ONE
        )

    def on_change_meta_error(self, callback):
        """Декоратор для подписки на ошибки контрола"""
        self._meta_error_callbacks.append(callback)

    @property
    def value(self):
        """Текущее значение контрола"""
        return self._value
