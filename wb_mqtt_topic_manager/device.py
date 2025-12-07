import json
from typing import Callable, List

from wb_mqtt_topic_manager.client import MQTTClient
from wb_mqtt_topic_manager.constance import ErrorType, QosType


class Device:
    """Представление устройства"""

    def __init__(self, client: MQTTClient, device_id: str):
        self.client = client
        self.id = device_id
        self.controls: dict = {}
        self.meta: dict = {}
        self.meta_error: str = ''

        # Callbacks
        self._on_meta_error_change: List[Callable[[str], None]] = []

        self._subcribe_meta_error()

    @property
    def device_topic_meta(self) -> dict:
        """Топик информации о устройстве"""
        return f'/devices/{self.id}/meta'

    @property
    def device_topic_meta_error(self) -> dict:
        """Топик ошибок устройства"""
        return f'/devices/{self.id}/meta/error'

    def _subcribe_meta_error(self):
        """Подпись на топик meta/error устройства"""

        def on_meta_error(topic, payload):
            if self.meta_error != payload:
                for callback_func in self._on_meta_error_change:
                    callback_func(payload)

            self.meta_error = payload

        self.client.subscribe(
            self.device_topic_meta_error, on_meta_error, qos=QosType.QOS_ONE
        )

    def on_change_meta_error(self, callback):
        """Декоратор для подписки на изменения"""
        self._on_meta_error_change.append(callback)


class DriverDevice(Device):
    """Устройства драйвера"""

    def __init__(self, client: MQTTClient, device_id: str, meta: dict):
        super().__init__(client, device_id)
        self.meta: dict = meta
        self._publish_meta()

    def _publish_meta(self):
        """Публикация метаданных устройства"""
        self.client.publish(
            topic=self.device_topic_meta,
            payload=self.meta,
            qos=QosType.QOS_ONE,
            retain=True,
        )
        self.client.publish(
            topic=self.device_topic_meta_error,
            payload='',
            qos=QosType.QOS_ONE,
            retain=True,
        )

        # Публикация имени для обратной совместимости
        old_conventions_topic = f'{self.device_topic_meta}/name'
        self.client.publish(
            topic=old_conventions_topic,
            payload=self.meta['title'].get('en'),
            qos=QosType.QOS_ONE,
            retain=True,
        )

    @classmethod
    def create(
        cls,
        client: MQTTClient,
        device_id: str,
        driver_name: str,
        title: dict,
    ) -> 'DriverDevice':
        """Создание экземпляра устройства"""

        meta = {
            'driver': driver_name,
            'title': title,
        }

        return cls(client, device_id, meta)

    def publish_error(self, error: ErrorType):
        """Публикация ошибки в топик meta/error"""
        if error in ErrorType.ERRORS:
            if error not in self.meta_error:
                self.meta_error += error
                self.client.publish(
                    topic=self.device_topic_meta_error,
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
                self.client.publish(
                    topic=self.device_topic_meta_error,
                    payload=self.meta_error,
                    qos=QosType.QOS_ONE,
                    retain=True,
                )
            return True

        return False


class ObserverDevice(Device):
    """Устройства для наблюдателя"""

    def __init__(self, client: MQTTClient, device_id: str):
        super().__init__(client, device_id)

    @classmethod
    def create(
        cls,
        client: MQTTClient,
        device_id: str,
    ) -> 'ObserverDevice':
        """Создание экземпляра устройства для наблюдателя"""
        device = cls(client, device_id)
        device.get_meta()

        return device

    def get_meta(self) -> dict:
        """Получение meta"""

        def on_meta(topic, payload):
            self.meta = json.loads(payload) if payload else {}

        self.client.subscribe(self.device_topic_meta, on_meta, qos=QosType.QOS_ONE)

        return self.meta
