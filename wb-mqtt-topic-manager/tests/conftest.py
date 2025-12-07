import pytest
from client import MQTTClient
from device import DriverDevice, ObserverDevice


@pytest.fixture
def test_client():
    """Клиент для тестирования"""
    with MQTTClient(
        broker_host='test.mosquitto.org', broker_port=1883, client_id='test_client'
    ) as client:
        yield client


@pytest.fixture
def test_driver_device(test_client):
    """Клиент для тестирования"""
    driver_device = DriverDevice.create(
        client=test_client,
        device_id='driver_device',
        driver_name='driver_device',
        title={
            'ru': 'Русское название',
            'en': 'English title',
        },
    )
    yield driver_device


@pytest.fixture
def test_observer_device(test_client):
    """Клиент для тестирования"""
    observer_device = ObserverDevice.create(
        client=test_client, device_id='driver_device'
    )
    yield observer_device
