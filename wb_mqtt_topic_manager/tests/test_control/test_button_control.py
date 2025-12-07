import time

import pytest
from client import MQTTClient
from constance import ErrorType
from control.base import LocalizedString
from control.control_manager import ControlManager


@pytest.mark.skip
def test_button_driver_control(test_driver_device):
    with MQTTClient(
        broker_host='test.mosquitto.org', broker_port=1883, client_id='test_client2'
    ) as client:
        client.subscribe('/devices/driver_device/#')

        button_driver_control = ControlManager.create_button(
            device=test_driver_device,
            control_id='test_control',
            initial_value='0',
            order=0,
            title=LocalizedString(en='Button', ru='Кнопка'),
        )

        @button_driver_control.on_change_on
        def on_change_value(value):
            assert value == '1'
            button_driver_control.change_value(value)

        time.sleep(2)

        client.publish('/devices/driver_device/test_control/on', '1')

        time.sleep(5)


@pytest.mark.skip
def test_both_controls(test_driver_device, test_observer_device):
    button_driver_control = ControlManager.create_button(
        device=test_driver_device,
        control_id='test_control',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Button', ru='Кнопка'),
    )

    @button_driver_control.on_change_on
    def on_change_value(value):
        assert value == '1'
        button_driver_control.change_value(value)

    button_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_control',
    )

    @button_observer_control.on_change_value
    def on_change_observer(value):
        assert value == '1'

    time.sleep(2)

    assert button_driver_control.value == '0'
    assert button_observer_control.meta == {
        'type': 'pushbutton',
        'order': 0,
        'title': {'en': 'Button', 'ru': 'Кнопка'},
        'readonly': False,
    }
    assert button_observer_control.value == '0'

    button_observer_control.on('1')

    time.sleep(2)

    assert button_driver_control.value == '1'
    assert button_observer_control.value == '1'


@pytest.mark.skip
def test_control_publish_delete_error(test_driver_device, test_observer_device):
    button_driver_control = ControlManager.create_button(
        device=test_driver_device,
        control_id='test_control',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Button', ru='Кнопка'),
    )

    button_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_control',
    )

    @button_observer_control.on_change_meta_error
    def on_change_observer(value):
        assert value in ['', 'r']

    time.sleep(2)

    result = button_driver_control.publish_error(ErrorType.READ)
    assert result

    failed_result = button_driver_control.publish_error('b')
    assert not failed_result

    time.sleep(2)

    assert button_driver_control.meta_error == ErrorType.READ
    assert button_observer_control.meta_error == ErrorType.READ

    result = button_driver_control.delete_error(ErrorType.READ)
    assert result

    time.sleep(2)

    assert (
        not button_driver_control.meta_error and not button_observer_control.meta_error
    )
