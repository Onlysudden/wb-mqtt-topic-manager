from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union


class ControlType(Enum):
    """Типы контролов"""

    SWITCH = 'switch'
    ALARM = 'alarm'
    PUSHBUTTON = 'pushbutton'
    RANGE = 'range'
    RGB = 'rgb'
    TEXT = 'text'
    VALUE = 'value'


@dataclass
class LocalizedString:
    """Локализованные строки для заголовков"""

    en: str
    ru: str

    def to_dict(self) -> Dict[str, str]:
        return {'en': self.en, 'ru': self.ru}


@dataclass
class EnumTitle:
    """Заголовки для enum значений"""

    value: Union[int, LocalizedString]


@dataclass
class BaseMeta:
    """Базовый класс для метаданных всех контролов"""

    type: ControlType
    order: Optional[int]
    title: Optional[LocalizedString]
    readonly: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует метаданные в словарь для отправки"""
        result = {'type': self.type.value}

        if self.order is not None:
            result['order'] = self.order
        if self.title:
            result['title'] = self.title.to_dict()

        result['readonly'] = self.readonly if self.readonly else False

        return result
