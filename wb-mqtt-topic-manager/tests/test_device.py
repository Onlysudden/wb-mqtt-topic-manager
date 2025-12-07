import time

import pytest
from client import MQTTClient
from constance import ErrorType
from device import DriverDevice, ObserverDevice


@pytest.mark.skip
def test_both_devices(test_client: MQTTClient):
    driver_device = DriverDevice.create(
        client=test_client,
        device_id='driver_device',
        driver_name='driver_device',
        title={
            'ru': 'Русское название',
            'en': 'English title',
        },
    )

    observer_device = ObserverDevice.create(
        client=test_client, device_id='driver_device'
    )

    time.sleep(2)

    assert observer_device.meta == {
        'driver': 'driver_device',
        'title': {'en': 'English title', 'ru': 'Русское название'},
    }

    assert observer_device.meta == driver_device.meta


@pytest.mark.skip
def test_publish_delete_error(test_client: MQTTClient):
    driver_device = DriverDevice.create(
        client=test_client,
        device_id='driver_device',
        driver_name='driver_device',
        title={
            'ru': 'Русское название',
            'en': 'English title',
        },
    )

    result = driver_device.publish_error(ErrorType.READ)
    assert result

    failed_result = driver_device.publish_error('b')
    assert not failed_result

    observer_device = ObserverDevice.create(
        client=test_client, device_id='driver_device'
    )

    time.sleep(2)

    assert observer_device.meta_error == ErrorType.READ

    result = driver_device.delete_error(ErrorType.READ)
    assert result

    failed_result = driver_device.publish_error('b')
    assert not failed_result

    time.sleep(2)

    assert not observer_device.meta_error and not driver_device.meta_error


@pytest.mark.skip
def test_on_meta_error_change(test_client: MQTTClient):
    driver_device = DriverDevice.create(
        client=test_client,
        device_id='driver_device',
        driver_name='driver_device',
        title={
            'ru': 'Русское название',
            'en': 'English title',
        },
    )

    observer_device = ObserverDevice.create(
        client=test_client, device_id='driver_device'
    )

    # Счетчик вызовов и история
    call_count = 0
    call_history = []
    all_errors_received = []

    @observer_device.on_change_meta_error
    def on_error_change(error):
        nonlocal call_count
        call_count += 1
        call_history.append((call_count, error))
        all_errors_received.append(error)

    driver_device.publish_error(ErrorType.READ)

    time.sleep(1)

    driver_device.publish_error(ErrorType.READ)

    time.sleep(1)

    driver_device.delete_error(ErrorType.READ)

    time.sleep(1)

    driver_device.publish_error(ErrorType.WRITE)
    driver_device.publish_error(ErrorType.PERIOD)

    time.sleep(1)

    driver_device.delete_error(ErrorType.WRITE)
    driver_device.delete_error(ErrorType.PERIOD)

    time.sleep(1)

    assert call_count == 6
    assert all_errors_received == ['r', '', 'w', 'wp', 'p', '']

    assert call_history[0][1] == 'r'
    assert call_history[1][1] == ''
    assert call_history[2][1] == 'w'
    assert call_history[3][1] == 'wp'
    assert call_history[4][1] == 'p'
    assert call_history[5][1] == ''
