import threading
import time
from typing import Any, Callable, Dict, Optional

import paho.mqtt.client as mqtt
from constance import QosType


class MQTTClient:
    """MQTT клиент для работы с брокером"""

    def __init__(
        self,
        broker_host: str,
        broker_port: str,
        client_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        keepalive: int = 60,
        clean_session: bool = True,
    ):
        """
        Инициализация MQTT клиента.

        Args:
            broker_host: Хост брокера
            broker_port: Порт брокера
            client_id: Идентификатор клиента (если None, генерируется автоматически)
            username: Имя пользователя для аутентификации
            password: Пароль для аутентификации
            keepalive: Интервал keepalive в секундах
            clean_session: Очищать сессию при переподключении
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.keepalive = keepalive
        self.clean_session = clean_session

        self.client = mqtt.Client(
            client_id=client_id,
            clean_session=clean_session,
            protocol=mqtt.MQTTv311,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )

        # Настройка callback-ов
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Настройка аутентификации
        if username and password:
            self.client.username_pw_set(username, password)

        # Состояние
        self.is_connected = False
        self._connection_lock = threading.Lock()
        self._message_callbacks: Dict[str, list] = {}

        # Таймауты
        self.connect_timeout = 10  # секунд
        self.reconnect_delay = 5  # секунд
        self.max_reconnect_attempts = 5

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Обработчик подключения для API версии 2"""
        if reason_code == 0:
            self.is_connected = True
        else:
            self.is_connected = False

    def connect(self) -> bool:
        """
        Подключение к MQTT брокеру.

        Returns:
            bool: True если подключение успешно, False в противном случае
        """
        with self._connection_lock:
            if self.is_connected:
                return True

            try:
                # Подключение с таймаутом
                self.client.connect(
                    host=self.broker_host,
                    port=self.broker_port,
                    keepalive=self.keepalive,
                )

                # Запуск сетевого цикла в отдельном потоке
                self.client.loop_start()

                # Ожидание подключения
                for _ in range(self.connect_timeout):
                    if self.is_connected:
                        return True
                    time.sleep(1)

                # Таймаут подключения
                self.client.loop_stop()
                return False

            except Exception:
                return False

    def disconnect(self):
        """Отключение от MQTT брокера"""
        with self._connection_lock:
            if not self.is_connected:
                return

            try:
                # Остановка сетевого цикла
                self.client.loop_stop()

                # Отключение
                self.client.disconnect()

                # Ожидание завершения отключения
                time.sleep(1)

                self.is_connected = False

            except Exception:
                pass

    def reconnect(self) -> bool:
        """
        Переподключение к брокеру.

        Returns:
            bool: True если переподключение успешно, False в противном случае
        """
        # Если подключен, сначала отключаемся
        if self.is_connected:
            self.disconnect()

        # Попытки переподключения
        for attempt in range(1, self.max_reconnect_attempts + 1):
            if self.connect():
                return True

            if attempt < self.max_reconnect_attempts:
                delay = self.reconnect_delay * attempt
                time.sleep(delay)

        return False

    def __enter__(self):
        """Поддержка открытия контекстного менеджера"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка закрытия контекстного менеджера"""
        self.disconnect()

    @property
    def connection_info(self) -> Dict[str, Any]:
        """Информация о подключении"""
        return {
            'broker_host': self.broker_host,
            'broker_port': self.broker_port,
            'connected': self.is_connected,
            'client_id': self.client._client_id.decode()
            if self.client._client_id
            else None,
        }

    def publish(
        self,
        topic: str,
        payload: Any,
        qos: int = QosType.QOS_ZERO,
        retain: bool = False,
    ) -> bool:
        """
        Публикация сообщения в топик.

        Args:
            topic: MQTT топик
            payload: Данные для отправки (строка, bytes или JSON-сериализуемый объект)
            qos: Качество обслуживания (0, 1, 2)
            retain: Сохранять сообщение для новых подписчиков

        Returns:
            bool: True если публикация инициирована успешно
        """
        if not self.is_connected:
            return False

        try:
            # Преобразование payload
            if not isinstance(payload, (str, bytes)):
                import json

                payload = json.dumps(payload)

            # Публикация
            result = self.client.publish(topic, payload, qos=qos, retain=retain)

            return result.rc == mqtt.MQTT_ERR_SUCCESS

        except Exception:
            return False

    def subscribe(
        self,
        topic: str,
        callback: Callable[[str, Any], None] = None,
        qos: int = QosType.QOS_ZERO,
    ):
        """
        Подписка на топик.

        Args:
            topic: MQTT топик для подписки
            callback: Функция обратного вызова (topic, payload)
            qos: Качество обслуживания
        """
        if not self.is_connected:
            return

        try:
            # Подписка
            result = self.client.subscribe(topic, qos=qos)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                # Сохранение callback
                if topic not in self._message_callbacks:
                    self._message_callbacks[topic] = []

                if callback:
                    self._message_callbacks[topic].append(callback)

        except Exception:
            pass

    def unsubscribe(self, topic: str, callback: Callable = None):
        """
        Отписка от топика.

        Args:
            topic: MQTT топик для отписки
            callback: Конкретный callback для удаления (если None, удаляются все)
        """
        if topic in self._message_callbacks:
            if callback:
                if callback in self._message_callbacks[topic]:
                    self._message_callbacks[topic].remove(callback)
            else:
                # Удаляем все callback-и для топика
                self._message_callbacks.pop(topic, None)

            # Если больше нет callback-ов для топика, отписываемся от него
            if topic not in self._message_callbacks:
                try:
                    self.client.unsubscribe(topic)
                except Exception:
                    pass

    def _on_message(self, client, userdata, message):
        """Обработчик входящих сообщений для API версии 2"""
        try:
            topic = message.topic
            payload = message.payload.decode('utf-8')

            # Вызов зарегистрированных callback-ов
            if topic in self._message_callbacks:
                for callback in self._message_callbacks[topic]:
                    try:
                        callback(topic, payload)
                    except Exception:
                        pass

        except Exception:
            pass
