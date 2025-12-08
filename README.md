- [Цель библиотеки](#цель-библиотеки)
- [Что реализовано?](#что-реализовано)
- [Примеры](#примеры)
- [Установка библиотеки](#установка-библиотеки)
- [Что планируется доработать](#что-планируется-доработать)

# Цель библиотеки

Python-модуль (библиотека) для работы с MQTT-брокером,
которая полностью инкапсулирует логику топиков в соответствии с конвенцией
Wiren Board: https://github.com/wirenboard/conventions

Модуль должен предоставить высокоуровневый, удобный API для работы с
устройствами и их контролами, а также с мета топиками в meta и error:

- создания и удаления устройств и их контролов;
- записи (публикация) и чтения значений из контролов;
- подписки на изменение значений в контролах;
- подписки на ошибки в контролах

## Что реализовано?

- [x] Создание устройств и их контролов.
- [ ] Удаление устройств и их контролов (Очистка retained сообщений).
- [x] Запись (публикация) и чтение значений из контролов.
- [x] Подписки на изменение значений в контролах.
- [x] Подписки на ошибки в устройствах.
- [x] Подписки на ошибки в контролах.
- [x] Тесты.

Реализовано синхронное соединение через библиотеку paho-mqtt к устройствам и их контролам по цепочке, через открытие клиента, добавление устройства (Для наблюдателя класс ObserverDevice, для драйвера DriverDevice) и добавление контрола (Для наблюдателя один вход через connect_control, для драйвера это отдельные функции для создания определенного контрола). Поддерживаемые контролы: Switch, Alarm, Push button, Range.

## Примеры

Пример подключения к клиенту через контекстный менеджер или в try-finally блоке:

```python
from wb_mqtt_topic_manager.client import MQTTClient

# Пример try-finally блока
client = MQTTClient(
        broker_host="test.mosquitto.org", broker_port=1883, client_id="test_client"
    )

if client.connect():
    try:
        # Do some logic
    finally:
        client.disconnect()

# Пример через контекстный менеджер
with MQTTClient(
        broker_host="test.mosquitto.org", broker_port=1883, client_id="test_client"
    ) as client:
        # Do some logic
```

Пример разделенного подключения к устройству:

```python
from wb_mqtt_topic_manager.device import DriverDevice, ObserverDevice
from wb_mqtt_topic_manager.constance import ErrorType

# Подключение для наблюдателя
observer_device = ObserverDevice.create(client=client, device_id="driver_device")

# Доступ к meta
observer_device.meta
# Доступ к meta/error
observer_device.meta_error
# Подписка на изменение meta/error
@observer_device.on_change_meta_error
def on_change_meta_error(value):
    # Do some logic

# Подключение для драйвера
driver_device = DriverDevice.create(
    client=client,
    device_id="driver_device",
    driver_name="driver_device",
    title={
        "ru": "Русское название",
        "en": "English title",
    },
)

# Публикация ошибки
driver_device.publish_error(ErrorType.READ)
# Удаление ошибки
driver_device.delete_error(ErrorType.READ)

```

Пример разделенного подключения к контролам устройствами:

```python
from wb_mqtt_topic_manager.control.base import LocalizedString
from wb_mqtt_topic_manager.control.control_manager import ControlManager

# Подключение для наблюдателя
observer_control = ControlManager.connect_control(
    device=test_observer_device,
    control_id="test_control",
)

# Доступ к meta
observer_device.meta
# Доступ к meta/error
observer_device.meta_error
# Доступ к текущему значению контрола
observer_device.value

# Подписка на изменение значения контрола
@observer_control.on_change_value
def on_change_observer(value):
    # Do some logic

# Подписка на изменение meta/error
@observer_control.on_change_meta_error
def on_change_meta_error(value):
    # Do some logic

# Подключение для драйвера
driver_control = ControlManager.create_switch(
    device=test_driver_device,
    control_id="test_control",
    initial_value="0",
    order=0,
    title=LocalizedString(en="Power", ru="Питание"),
)

# Подписка на получение значения в /on
@driver_control.on_change_on
    def on_change_value(value):
        # Пример обновления значения контрола
        driver_control.change_value(value)

# Публикация ошибки
driver_control.publish_error(ErrorType.READ)
# Удаление ошибки
driver_control.delete_error(ErrorType.READ)
```

## Установка библиотеки

`uv add git+https://github.com/Onlysudden/wb-mqtt-topic-manager.git`

### Что планируется доработать

- Добавить поддержку остальных типов контролов: RGB color control, Text, Generic value type control.
- Добавить удаление устройств и их контролов (Очистка retained сообщений).
- Добавить вывод ошибок.
- Добавить поддержку защищенных соединений TLS/SSL.
- Перейти на асинхронную библиотеку для подключения к брокеру MQTT.
- Изменить подход подключения к устройствам и контролам. Добавить поиск устройств. Добавить подключение к контролам без инициализации устройства, добавить поиск контролов устройства. Добавить отложенный старт, для первоначальной настройки и подписки на события.
