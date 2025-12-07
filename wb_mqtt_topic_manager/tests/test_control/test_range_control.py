import time

import pytest

from wb_mqtt_topic_manager.constance import ErrorType
from wb_mqtt_topic_manager.control.base import LocalizedString
from wb_mqtt_topic_manager.control.control_manager import ControlManager


@pytest.mark.skip
def test_range_driver_control(test_driver_device):
    range_driver_control = ControlManager.create_range(
        device=test_driver_device,
        control_id='test_range',
        initial_value=100,
        order=0,
        title=LocalizedString(en='Range', ru='Диапазон'),
        min_value=30,
        max_value=120,
    )

    assert range_driver_control.value == 100

    assert range_driver_control.change_value(50) and range_driver_control.value == 50


@pytest.mark.skip
def test_both_controls(test_driver_device, test_observer_device):
    range_driver_control = ControlManager.create_range(
        device=test_driver_device,
        control_id='test_range',
        initial_value=100,
        order=0,
        title=LocalizedString(en='Range', ru='Диапазон'),
        min_value=30,
        max_value=120,
    )

    @range_driver_control.on_change_on
    def on_change_value(value):
        assert int(value) == 75
        range_driver_control.change_value(int(value))

    range_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_range',
    )

    @range_observer_control.on_change_value
    def on_change_observer(value):
        assert int(value) in [75, 100]

    time.sleep(2)

    assert range_driver_control.value == 100
    assert range_observer_control.meta == {
        'type': 'range',
        'order': 0,
        'title': {'en': 'Range', 'ru': 'Диапазон'},
        'readonly': False,
        'min': 30,
        'max': 120,
    }
    assert range_observer_control.value == 100

    assert (
        not range_driver_control.change_value(150) and range_driver_control.value == 100
    )
    assert not range_observer_control.on(150)
    assert range_observer_control.on(75)

    time.sleep(2)

    assert range_driver_control.value == 75
    assert range_observer_control.value == 75


@pytest.mark.skip
def test_range_publish_delete_error(test_driver_device, test_observer_device):
    range_driver_control = ControlManager.create_range(
        device=test_driver_device,
        control_id='test_range',
        initial_value='0',
        order=0,
        title=LocalizedString(en='Range', ru='Диапазон'),
        min_value=30,
        max_value=120,
    )

    range_observer_control = ControlManager.connect_control(
        device=test_observer_device,
        control_id='test_range',
    )

    @range_observer_control.on_change_meta_error
    def on_change_observer(value):
        assert value in ['', 'r']

    time.sleep(2)

    result = range_driver_control.publish_error(ErrorType.READ)
    assert result

    failed_result = range_driver_control.publish_error('b')
    assert not failed_result

    time.sleep(2)

    assert range_driver_control.meta_error == ErrorType.READ
    assert range_observer_control.meta_error == ErrorType.READ

    result = range_driver_control.delete_error(ErrorType.READ)
    assert result

    time.sleep(2)

    assert not range_driver_control.meta_error and not range_observer_control.meta_error
