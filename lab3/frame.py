import json
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field


class InheritanceType(Enum):
    """Типы наследования согласно теории Минского"""
    UNIQUE = "U"  # Unique - уникальное значение для каждого экземпляра
    SAME = "S"  # Same - то же самое значение, что у родителя
    RANGE = "R"  # Range - значение из допустимого диапазона
    OVERRIDE = "O"  # Override - может быть переопределено потомком


class DataType(Enum):
    """Типы данных для слотов"""
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    FRAME = "FRAME"
    LIST = "LIST"


class TriggerType(Enum):
    """Типы триггерных процедур"""
    IF_NEEDED = "IF-NEEDED"  # Вызывается при запросе пустого слота
    IF_ADDED = "IF-ADDED"  # Вызывается при добавлении значения
    IF_REMOVED = "IF-REMOVED"  # Вызывается при удаления значения


class Slot:
    """Слот фрейма согласно теории Минского"""

    def __init__(self, name: str, value: Any = None,
                 data_type: DataType = DataType.TEXT,
                 inheritance: InheritanceType = InheritanceType.OVERRIDE,
                 range_values: List[Any] = None,
                 triggers: Dict[TriggerType, Callable] = None):
        self.name = name
        self.value = value
        self.data_type = data_type
        self.inheritance = inheritance
        self.range_values = range_values or []
        self.triggers = triggers or {}
        self.default_value = value

    def _validate_type(self, value: Any) -> bool:
        """Проверка соответствия типа данных"""
        if value is None:
            return True

        if self.data_type == DataType.INTEGER:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif self.data_type == DataType.TEXT:
            return isinstance(value, str)
        elif self.data_type == DataType.BOOLEAN:
            return isinstance(value, bool)
        elif self.data_type == DataType.FRAME:
            return isinstance(value, Frame)
        elif self.data_type == DataType.LIST:
            return isinstance(value, list)
        return True

    def _validate_range(self, value: Any) -> bool:
        """Проверка соответствия диапазону значений"""
        if not self.range_values:
            return True
        return value in self.range_values

    def set_value(self, frame, value: Any):
        """Установка значения с валидацией и триггерами"""
        # Валидация типа
        if not self._validate_type(value):
            raise ValueError(
                f"Неверный тип данных '{type(value).__name__}' для слота {self.name}. Ожидается {self.data_type.value}")

        # Валидация диапазона
        if not self._validate_range(value):
            raise ValueError(
                f"Значение '{value}' не входит в допустимый диапазон {self.range_values} для слота {self.name}")

        old_value = self.value
        self.value = value

        # Вызов IF-ADDED триггера
        if TriggerType.IF_ADDED in self.triggers:
            self.triggers[TriggerType.IF_ADDED](frame, old_value, value)

    def get_value(self, frame) -> Any:
        """Получение значения с поддержкой IF-NEEDED"""
        if self.value is None and self.default_value is not None:
            # Возвращаем значение по умолчанию
            return self.default_value

        if self.value is None:
            # Вызов IF-NEEDED триггера для вычисления значения
            if TriggerType.IF_NEEDED in self.triggers:
                computed_value = self.triggers[TriggerType.IF_NEEDED](frame)
                # Временно устанавливаем вычисленное значение
                if self._validate_type(computed_value) and self._validate_range(computed_value):
                    self.value = computed_value
                    return computed_value
            return None

        return self.value

    def remove_value(self, frame):
        """Удаление значения с вызовом IF-REMOVED"""
        old_value = self.value
        self.value = None

        if TriggerType.IF_REMOVED in self.triggers:
            self.triggers[TriggerType.IF_REMOVED](frame, old_value)


class Frame:
    """Фрейм согласно теории Марвина Минского"""

    def __init__(self, name: str):
        self.name = name
        self.slots: Dict[str, Slot] = {}

        # Системные слоты
        ako_slot = Slot("AKO", None, DataType.FRAME, InheritanceType.SAME)
        self.slots["AKO"] = ako_slot

    def add_slot(self, slot: Slot):
        """Добавление слота во фрейм"""
        self.slots[slot.name] = slot

    def get_slot(self, slot_name: str) -> Optional[Slot]:
        """Получение слота по имени"""
        return self.slots.get(slot_name)

    def get_slot_value(self, slot_name: str) -> Any:
        """Получение значения слота с полной поддержкой наследования"""
        if slot_name in self.slots:
            slot = self.slots[slot_name]
            value = slot.get_value(self)
            if value is not None:
                return value

        # Наследование через AKO
        ako_frame = self.slots["AKO"].value
        if ako_frame and isinstance(ako_frame, Frame):
            return ako_frame.get_slot_value(slot_name)

        return None

    def set_slot_value(self, slot_name: str, value: Any):
        """Установка значения слота"""
        if slot_name not in self.slots:
            # Создаем новый слот по умолчанию
            data_type = DataType.TEXT
            if isinstance(value, bool):
                data_type = DataType.BOOLEAN
            elif isinstance(value, (int, float)):
                data_type = DataType.INTEGER
            elif isinstance(value, Frame):
                data_type = DataType.FRAME
            elif isinstance(value, list):
                data_type = DataType.LIST

            new_slot = Slot(slot_name, value, data_type)
            self.slots[slot_name] = new_slot
        else:
            self.slots[slot_name].set_value(self, value)

    def set_ako(self, parent_frame: 'Frame'):
        """Установка родительского фрейма через AKO"""
        self.slots["AKO"].value = parent_frame

    def is_a(self, frame_type: str) -> bool:
        """Проверяет, является ли фрейм экземпляром указанного типа"""
        current = self
        while current:
            if current.name == frame_type:
                return True
            ako = current.slots["AKO"].value
            if ako and isinstance(ako, Frame):
                current = ako
            else:
                break
        return False

    def create_proto_frame(self) -> 'Frame':
        """Создает протофрейм (незаполненную копию)"""
        proto = Frame(f"Proto_{self.name}")
        proto.set_ako(self)
        return proto

    def __str__(self):
        slots_info = []
        for slot_name, slot in self.slots.items():
            if slot_name == "AKO":
                ako_name = slot.value.name if slot.value else "None"
                slots_info.append(f"{slot_name}: {ako_name}")
            else:
                value = slot.get_value(self)
                slots_info.append(f"{slot_name}: {value}")

        slots_str = ", ".join(slots_info)
        return f"Frame({self.name}, slots: [{slots_str}])"

    def __repr__(self):
        return self.__str__()