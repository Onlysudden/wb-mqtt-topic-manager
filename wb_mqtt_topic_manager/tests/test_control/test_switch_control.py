import time

import pytest

from wb_mqtt_topic_manager.client import MQTTClient
from wb_mqtt_topic_manager.constance import ErrorType
from wb_mqtt_topic_manager.control.base import LocalizedString
from wb_mqtt_topic_manager.control.control_manager import ControlManager


@pytest.mark.skip
def test_switch_driver_control(test_driver_device):
    with MQTTClient(
        broker_host='test.mosquitto.org', broker_port=1883, client_id='test_client2'
    ) as client:
        client.subscribe('/devices/driver_device/#')

        switch_driver_control = ControlManager.create_switch(
            device=test_driver_device,
            control_id='test_control',
            initial_value='0',
            order=0,
            title=LocalizedString(en='Power', ru='Питание'),
        )

        @switch_driver_control.on_change_on
        def on_change_value(value):
            assert value == '1'
            switch_driver_control.change_value(value)

        time.sleep(2)

        client.publish('/devices/driver_device/test_control/on', '1')

        time.sleep(5)


@pytest.mark.skip
def test_both_controls(test_driver_device, test_observer_device):
    switch_driver_control = ControlManager.create_switch(
        device=test_driver_device,
        control_id='test_control',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Power', ru='Питание'),
    )

    @switch_driver_control.on_change_on
    def on_change_value(value):
        assert value == '1'
        switch_driver_control.change_value(value)

    switch_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_control',
    )

    @switch_observer_control.on_change_value
    def on_change_observer(value):
        assert value == '1'

    time.sleep(2)

    assert switch_driver_control.value == '0'
    assert switch_observer_control.meta == {
        'type': 'switch',
        'order': 0,
        'title': {'en': 'Power', 'ru': 'Питание'},
        'readonly': False,
    }
    assert switch_observer_control.value == '0'

    switch_observer_control.on('1')

    time.sleep(2)

    assert switch_driver_control.value == '1'
    assert switch_observer_control.value == '1'


@pytest.mark.skip
def test_control_publish_delete_error(test_driver_device, test_observer_device):
    switch_driver_control = ControlManager.create_switch(
        device=test_driver_device,
        control_id='test_control',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Power', ru='Питание'),
    )

    switch_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_control',
    )

    @switch_observer_control.on_change_meta_error
    def on_change_observer(value):
        assert value in ['', 'r']

    time.sleep(2)

    result = switch_driver_control.publish_error(ErrorType.READ)
    assert result

    failed_result = switch_driver_control.publish_error('b')
    assert not failed_result

    time.sleep(2)

    assert switch_driver_control.meta_error == ErrorType.READ
    assert switch_observer_control.meta_error == ErrorType.READ

    result = switch_driver_control.delete_error(ErrorType.READ)
    assert result

    time.sleep(2)

    assert (
        not switch_driver_control.meta_error and not switch_observer_control.meta_error
    )
