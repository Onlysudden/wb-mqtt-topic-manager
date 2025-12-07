from dataclasses import dataclass, field
from typing import Any, Dict

from control.base import BaseMeta, ControlType


@dataclass
class SwitchMeta(BaseMeta):
    """Метаданные для switch контрола"""

    type: ControlType = field(default=ControlType.SWITCH, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()


@dataclass
class AlarmMeta(BaseMeta):
    """Метаданные для alarm контрола"""

    type: ControlType = field(default=ControlType.ALARM, init=False)


@dataclass
class PushButtonMeta(BaseMeta):
    """Метаданные для pushbutton контрола"""

    type: ControlType = field(default=ControlType.PUSHBUTTON, init=False)


@dataclass
class RangeMeta(BaseMeta):
    """Метаданные для range контрола"""

    type: ControlType = field(default=ControlType.RANGE, init=False)
    min_value: int = 0
    max_value: int = 255

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result['min'] = self.min_value
        result['max'] = self.max_value
        return result
