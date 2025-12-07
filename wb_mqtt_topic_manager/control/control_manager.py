from typing import Any, Optional

from control.base import LocalizedString
from control.control import DriverControl, ObserverControl, RangeDriverControl
from control.control_type import AlarmMeta, PushButtonMeta, RangeMeta, SwitchMeta
from device import DriverDevice


class ControlManager:
    """Менеджер создания контролов"""

    @staticmethod
    def connect_control(
        device: ObserverControl,
        control_id: str,
    ) -> ObserverControl:
        """Подключение к контролу"""
        return ObserverControl(device=device, control_id=control_id)

    @staticmethod
    def create_switch(
        device: DriverDevice,
        control_id: str,
        initial_value: Any,
        order: Optional[int],
        title: Optional[LocalizedString],
        readonly: bool = False,
    ) -> DriverControl:
        """Создание switch контрола"""
        meta = SwitchMeta(order=order, readonly=readonly, title=title)

        return DriverControl(
            device=device, control_id=control_id, initial_value=initial_value, meta=meta
        )

    @staticmethod
    def create_alarm(
        device: DriverDevice,
        control_id: str,
        initial_value: Any,
        order: Optional[int],
        title: Optional[LocalizedString],
        readonly: bool = False,
    ) -> DriverControl:
        """Создание alarm контрола"""
        meta = AlarmMeta(order=order, readonly=readonly, title=title)

        return DriverControl(
            device=device, control_id=control_id, initial_value=initial_value, meta=meta
        )

    @staticmethod
    def create_button(
        device: DriverDevice,
        control_id: str,
        initial_value: Any,
        order: Optional[int],
        title: Optional[LocalizedString],
        readonly: bool = False,
    ) -> DriverControl:
        """Создание pushbutton контрола"""
        meta = PushButtonMeta(order=order, readonly=readonly, title=title)

        return DriverControl(
            device=device, control_id=control_id, initial_value=initial_value, meta=meta
        )

    @staticmethod
    def create_range(
        device: DriverDevice,
        control_id: str,
        initial_value: Any,
        order: Optional[int],
        title: Optional[LocalizedString],
        min_value: int = 0,
        max_value: int = 255,
        readonly: bool = False,
    ) -> DriverControl:
        """Создание range контрола"""
        meta = RangeMeta(
            order=order,
            readonly=readonly,
            title=title,
            min_value=min_value,
            max_value=max_value,
        )

        return RangeDriverControl(
            device=device, control_id=control_id, initial_value=initial_value, meta=meta
        )
