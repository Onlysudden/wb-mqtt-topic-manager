import time

import pytest

from wb_mqtt_topic_manager.constance import ErrorType
from wb_mqtt_topic_manager.control.base import LocalizedString
from wb_mqtt_topic_manager.control.control_manager import ControlManager


@pytest.mark.skip
def test_alarm_driver_control(test_driver_device):
    alarm_driver_control = ControlManager.create_alarm(
        device=test_driver_device,
        control_id='test_alarm',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Alarm', ru='Тревога'),
        readonly=True,
    )

    assert alarm_driver_control.value == '0'

    alarm_driver_control.change_value('1')

    assert alarm_driver_control.value == '1'


@pytest.mark.skip
def test_both_controls(test_driver_device, test_observer_device):
    alarm_driver_control = ControlManager.create_alarm(
        device=test_driver_device,
        control_id='test_alarm',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Alarm', ru='Тревога'),
        readonly=True,
    )

    alarm_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_alarm',
    )

    @alarm_observer_control.on_change_value
    def on_change_observer(value):
        assert value == '1'

    time.sleep(2)

    assert alarm_driver_control.value == '0'
    assert alarm_observer_control.meta == {
        'type': 'alarm',
        'order': 0,
        'title': {'en': 'Alarm', 'ru': 'Тревога'},
        'readonly': True,
    }
    assert alarm_observer_control.value == '0'

    alarm_driver_control.change_value('1')

    time.sleep(2)

    assert alarm_driver_control.value == '1'
    assert alarm_observer_control.value == '1'


@pytest.mark.skip
def test_alarm_publish_delete_error(test_driver_device, test_observer_device):
    alarm_driver_control = ControlManager.create_alarm(
        device=test_driver_device,
        control_id='test_alarm',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Alarm', ru='Тревога'),
        readonly=True,
    )

    alarm_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_alarm',
    )

    @alarm_observer_control.on_change_meta_error
    def on_change_observer(value):
        assert value in ['', 'r']

    time.sleep(2)

    result = alarm_driver_control.publish_error(ErrorType.READ)
    assert result

    failed_result = alarm_driver_control.publish_error('b')
    assert not failed_result

    time.sleep(2)

    assert alarm_driver_control.meta_error == ErrorType.READ
    assert alarm_observer_control.meta_error == ErrorType.READ

    result = alarm_driver_control.delete_error(ErrorType.READ)
    assert result

    time.sleep(2)

    assert not alarm_driver_control.meta_error and not alarm_observer_control.meta_error
