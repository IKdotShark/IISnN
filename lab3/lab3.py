#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФРЕЙМОВАЯ ЭКСПЕРТНАЯ СИСТЕМА ДЛЯ ПОДБОРА РЕЦЕПТОВ
Основана на теории фреймов Марвина Минского
База знаний хранится в формате JSON

Состав системы:
1. frame.py - реализация фреймов согласно теории Минского
2. knowledge_base.py - база знаний с фреймами (хранится в JSON)
3. working_memory.py - рабочая память системы
4. inference_engine.py - механизм логического вывода
5. explanation_component.py - компонента объяснения
6. main.py - основной модуль запуска

Вариант: Фреймовое представление знаний
"""

import json
import os
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, field


# ============================================================================
# МОДУЛЬ 1: ФРЕЙМЫ (frame.py)
# ============================================================================

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


# ============================================================================
# МОДУЛЬ 2: БАЗА ЗНАНИЙ (knowledge_base.py)
# ============================================================================

class KnowledgeBase:
    """База знаний, хранящая фреймы согласно теории Минского в формате JSON"""

    def __init__(self, json_file: str):
        self.frames: Dict[str, Frame] = {}
        self._procedures = {}
        self.load_from_json(json_file)

    def _register_procedures(self):
        """Регистрация встроенных процедур"""
        # IF-NEEDED процедуры
        self._procedures["calculate_compatibility"] = self._calculate_compatibility
        self._procedures["get_recommendation_reason"] = self._get_recommendation_reason
        self._procedures["determine_recipe_time"] = self._determine_recipe_time
        self._procedures["suggest_similar_recipes"] = self._suggest_similar_recipes
        self._procedures["calculate_difficulty"] = self._calculate_difficulty

        # IF-ADDED процедуры
        self._procedures["validate_budget"] = self._validate_budget
        self._procedures["validate_cooking_time"] = self._validate_cooking_time
        self._procedures["update_category"] = self._update_category

    def _calculate_compatibility(self, frame) -> float:
        """IF-NEEDED: Вычисляет совместимость рецепта с пользователем"""
        compatibility = 0.0

        # Проверяем категорию бюджета
        budget = frame.get_slot_value("категория_бюджета")
        if budget:
            compatibility += 0.3

        # Проверяем тип блюда
        dish_type = frame.get_slot_value("тип_блюда")
        if dish_type:
            compatibility += 0.3

        # Проверяем время приготовления
        cooking_time = frame.get_slot_value("время_приготовления")
        if cooking_time:
            compatibility += 0.2

        # Проверяем диетические ограничения
        dietary = frame.get_slot_value("диетические_ограничения")
        if dietary is not None:
            compatibility += 0.2

        return compatibility

    def _get_recommendation_reason(self, frame) -> str:
        """IF-NEEDED: Формирует причину рекомендации рецепта"""
        reasons = []

        budget = frame.get_slot_value("категория_бюджета")
        if budget:
            reasons.append(f"Бюджет: {budget}")

        dish_type = frame.get_slot_value("тип_блюда")
        if dish_type:
            reasons.append(f"Тип блюда: {dish_type}")

        cooking_time = frame.get_slot_value("время_приготовления")
        if cooking_time:
            reasons.append(f"Время приготовления: {cooking_time}")

        dietary = frame.get_slot_value("диетические_ограничения")
        if dietary:
            reasons.append("Соответствует диетическим ограничениям")

        difficulty = frame.get_slot_value("сложность")
        if difficulty:
            reasons.append(f"Сложность: {difficulty}")

        return "; ".join(reasons) if reasons else "Общая совместимость"

    def _determine_recipe_time(self, frame) -> str:
        """IF-NEEDED: Определяет время приготовления на основе сложности"""
        difficulty = frame.get_slot_value("сложность")
        if difficulty == "низкая":
            return "быстро"
        elif difficulty == "средняя":
            return "среднее"
        elif difficulty == "высокая":
            return "долго"
        return "среднее"

    def _suggest_similar_recipes(self, frame) -> List[str]:
        """IF-NEEDED: Предлагает похожие рецепты"""
        recipe_name = frame.name
        similar_map = {
            "Котлеты": ["Бифштексы", "Шницель"],
            "Гуляш": ["Рагу", "Соте"],
            "Стейк": ["Медальоны", "Антрекот"],
            "Утка_по_пекински": ["Утка в апельсинах", "Фуа-гра"],
            "Куриный_суп": ["Бульон", "Суп-лапша"],
            "Борщ": ["Щи", "Солянка"],
            "Том_ям": ["Тайский суп", "Куриный суп с кокосом"],
            "Гречка": ["Рис", "Киноа"],
            "Рис_с_овощами": ["Плов", "Паэлья"],
            "Овощной_салат": ["Салат из свежих овощей", "Греческий салат"],
            "Цезарь": ["Салат с креветками", "Греческий салат"],
            "Греческий_салат": ["Овощной салат", "Салат Шопский"]
        }
        return similar_map.get(recipe_name, [])

    def _calculate_difficulty(self, frame) -> str:
        """IF-NEEDED: Вычисляет сложность приготовления"""
        ingredients_count = frame.get_slot_value("количество_ингредиентов")
        cooking_time = frame.get_slot_value("время_приготовления")

        if ingredients_count and cooking_time:
            if ingredients_count <= 5 and cooking_time == "быстро":
                return "низкая"
            elif ingredients_count <= 8 and cooking_time in ["быстро", "среднее"]:
                return "средняя"
            else:
                return "высокая"
        return "средняя"

    def _validate_budget(self, frame, old_value, new_value):
        """IF-ADDED: Валидирует значение бюджета"""
        if new_value not in ["низкий", "средний", "высокий"]:
            raise ValueError(f"Недопустимое значение бюджета: {new_value}")

    def _validate_cooking_time(self, frame, old_value, new_value):
        """IF-ADDED: Валидирует время приготовления"""
        if new_value not in ["быстро", "среднее", "долго"]:
            raise ValueError(f"Недопустимое время приготовления: {new_value}")

    def _update_category(self, frame, old_value, new_value):
        """IF-ADDED: Обновляет категорию при изменении типа"""
        print(f"Обновление категории для типа: {new_value}")

    def _parse_triggers(self, trigger_data: Dict[str, Any]) -> Dict[TriggerType, Callable]:
        """Парсит триггеры из JSON"""
        triggers = {}
        if not trigger_data:
            return triggers

        for trigger_str, proc_name in trigger_data.items():
            try:
                trigger_type = TriggerType(trigger_str)
                if proc_name in self._procedures:
                    triggers[trigger_type] = self._procedures[proc_name]
            except ValueError:
                continue  # Пропускаем неизвестные триггеры

        return triggers

    def _resolve_frame_reference(self, frame_objects: Dict[str, Frame], ref: Any) -> Any:
        """Разрешает ссылки на другие фреймы"""
        if isinstance(ref, str) and ref.startswith("!ref:"):
            frame_name = ref[5:]  # Убираем "!ref:"
            return frame_objects.get(frame_name)
        return ref

    def load_from_json(self, json_file: str):
        """Загружает фреймы из JSON файла"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Регистрируем процедуры
        self._register_procedures()

        # Создаем все фреймы
        frame_objects = {}
        for frame_data in data['frames']:
            name = frame_data['name']
            frame_objects[name] = Frame(name)

        # Устанавливаем слоты и AKO связи
        for frame_data in data['frames']:
            name = frame_data['name']
            frame = frame_objects[name]

            # Устанавливаем AKO
            if 'ako' in frame_data and frame_data['ako']:
                parent_name = frame_data['ako']
                if parent_name in frame_objects:
                    frame.set_ako(frame_objects[parent_name])

            # Устанавливаем слоты
            if 'slots' in frame_data:
                for slot_data in frame_data['slots']:
                    slot_name = slot_data['name']

                    # Определяем тип данных
                    data_type = DataType(slot_data.get('data_type', 'TEXT'))

                    # Определяем тип наследования
                    inheritance_str = slot_data.get('inheritance', 'O')
                    inheritance = InheritanceType(inheritance_str)

                    # Получаем значение (разрешаем ссылки на фреймы)
                    raw_value = slot_data.get('value')
                    value = self._resolve_frame_reference(frame_objects, raw_value)

                    # Получаем диапазон значений
                    range_values = slot_data.get('range', [])

                    # Парсим триггеры
                    triggers_data = slot_data.get('triggers', {})
                    triggers = self._parse_triggers(triggers_data)

                    # Создаем слот
                    slot = Slot(
                        name=slot_name,
                        value=value,
                        data_type=data_type,
                        inheritance=inheritance,
                        range_values=range_values,
                        triggers=triggers
                    )

                    frame.add_slot(slot)

        self.frames = frame_objects

    def get_frame(self, name: str) -> Optional[Frame]:
        """Возвращает фрейм по имени"""
        return self.frames.get(name)

    def get_all_frames(self) -> List[Frame]:
        """Возвращает все фреймы"""
        return list(self.frames.values())

    def get_recipe_frames(self) -> List[Frame]:
        """Возвращает только фреймы конкретных рецептов"""
        recipe_names = [
            "Котлеты", "Гуляш", "Стейк", "Утка_по_пекински",
            "Куриный_суп", "Борщ", "Том_ям", "Гречка",
            "Рис_с_овощами", "Овощной_салат", "Цезарь", "Греческий_салат"
        ]
        return [self.frames[name] for name in recipe_names if name in self.frames]


# ============================================================================
# МОДУЛЬ 3: РАБОЧАЯ ПАМЯТЬ (working_memory.py)
# ============================================================================

@dataclass
class TraceEntry:
    """Запись в истории вывода"""
    action: str
    frame_name: str
    details: Dict[str, Any] = field(default_factory=dict)


class WorkingMemory:
    """Рабочая память экспертной системы"""

    def __init__(self):
        self.user_preferences: Dict[str, Any] = {}
        self.proto_frames: List[Frame] = []  # Протофреймы пользователя
        self.exo_frames: List[Frame] = []  # Экзофреймы из БЗ
        self.trace: List[TraceEntry] = []  # История вывода

    def set_preferences(self, preferences: Dict[str, Any]):
        """Устанавливает предпочтения пользователя"""
        self.user_preferences = preferences
        self.add_trace("set_preferences", "System", {"preferences": preferences})

    def add_proto_frame(self, proto_frame: Frame):
        """Добавляет протофрейм"""
        self.proto_frames.append(proto_frame)
        self.add_trace("add_proto_frame", proto_frame.name, {})

    def add_exo_frame(self, exo_frame: Frame):
        """Добавляет экзофрейм"""
        self.exo_frames.append(exo_frame)

    def add_trace(self, action: str, frame_name: str, details: Dict[str, Any]):
        """Добавляет запись в историю вывода"""
        entry = TraceEntry(action, frame_name, details)
        self.trace.append(entry)

    def get_preferences(self) -> Dict[str, Any]:
        """Возвращает предпочтения пользователя"""
        return self.user_preferences

    def get_proto_frames(self) -> List[Frame]:
        """Возвращает протофреймы"""
        return self.proto_frames

    def get_exo_frames(self) -> List[Frame]:
        """Возвращает экзофреймы"""
        return self.exo_frames

    def get_trace(self) -> List[TraceEntry]:
        """Возвращает историю вывода"""
        return self.trace

    def clear(self):
        """Очищает рабочую память"""
        self.user_preferences = {}
        self.proto_frames = []
        self.exo_frames = []
        self.trace = []


# ============================================================================
# МОДУЛЬ 4: МЕХАНИЗМ ЛОГИЧЕСКОГО ВЫВОДА (inference_engine.py)
# ============================================================================

class InferenceEngine:
    """Механизм логического вывода для фреймовой системы"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.working_memory = WorkingMemory()

    def reset(self):
        """Сбрасывает рабочую память"""
        self.working_memory.clear()

    def set_user_preferences(self, preferences: Dict[str, Any]):
        """Устанавливает предпочтения пользователя"""
        # Преобразуем ответы в формат для системы
        processed_preferences = {
            "бюджет": preferences.get("бюджет", "средний"),
            "диетические_ограничения": preferences.get("диетические_ограничения", False),
            "хочу_мясные_блюда": preferences.get("хочу_мясные_блюда", True),
            "хочу_супы": preferences.get("хочу_супы", True),
            "хочу_гарниры": preferences.get("хочу_гарниры", True),
            "хочу_салаты": preferences.get("хочу_салаты", True),
            "есть_специи": preferences.get("есть_специи", True),
            "быстрое_приготовление": preferences.get("быстрое_приготовление", True),
            "время_приготовления": preferences.get("время_приготовления", "среднее")
        }

        self.working_memory.set_preferences(processed_preferences)

    def frame_based_inference(self) -> List[Frame]:
        """Выполняет вывод на основе фреймов"""
        preferences = self.working_memory.get_preferences()
        recipe_frames = self.kb.get_recipe_frames()

        # Определяем категорию бюджета пользователя
        budget_category = self._determine_budget_category(preferences)

        # Определяем доступные типы блюд
        available_dish_types = self._determine_available_dish_types(preferences)

        # Создаем протофреймы и оцениваем совместимость
        matched_frames = []

        for recipe_frame in recipe_frames:
            # Создаем протофрейм
            proto_frame = recipe_frame.create_proto_frame()
            self.working_memory.add_proto_frame(proto_frame)
            self.working_memory.add_exo_frame(recipe_frame)

            # Устанавливаем категорию бюджета рецепта
            recipe_budget = recipe_frame.get_slot_value("категория_бюджета")
            if recipe_budget:
                proto_frame.set_slot_value("требуемая_категория_бюджета", recipe_budget)

            # Устанавливаем тип блюда
            dish_type = recipe_frame.get_slot_value("тип_блюда")
            if dish_type:
                proto_frame.set_slot_value("требуемый_тип_блюда", dish_type)

            # Устанавливаем время приготовления
            cooking_time = recipe_frame.get_slot_value("время_приготовления")
            if cooking_time:
                proto_frame.set_slot_value("требуемое_время_приготовления", cooking_time)

            # Устанавливаем диетические ограничения
            dietary = recipe_frame.get_slot_value("диетические_ограничения")
            if dietary is not None:
                proto_frame.set_slot_value("требует_диетических_ограничений", dietary)

            # Устанавливаем сложность
            difficulty = recipe_frame.get_slot_value("сложность")
            if difficulty:
                proto_frame.set_slot_value("сложность", difficulty)

            # Вычисляем совместимость
            compatibility = self._calculate_compatibility(
                proto_frame, budget_category, available_dish_types, preferences
            )

            if compatibility > 0.3:  # Порог совместимости
                proto_frame.set_slot_value("совместимость", compatibility)
                matched_frames.append(proto_frame)

                self.working_memory.add_trace(
                    "frame_match",
                    proto_frame.name,
                    {
                        "compatibility": compatibility,
                        "budget_match": recipe_budget == budget_category,
                        "dish_type_match": dish_type in available_dish_types
                    }
                )

        # Сортируем по совместимости
        matched_frames.sort(
            key=lambda f: f.get_slot_value("совместимость") or 0,
            reverse=True
        )

        return matched_frames

    def _determine_budget_category(self, preferences: Dict[str, Any]) -> str:
        """Определяет категорию бюджета пользователя"""
        budget = preferences.get("бюджет", "средний")
        if budget == "низкий":
            return "низкий"
        elif budget == "высокий":
            return "высокий"
        return "средний"

    def _determine_available_dish_types(self, preferences: Dict[str, Any]) -> List[str]:
        """Определяет доступные типы блюд"""
        dish_types = []

        if preferences.get("хочу_мясные_блюда"):
            dish_types.append("мясное")

        if preferences.get("хочу_супы"):
            dish_types.append("суп")

        if preferences.get("хочу_гарниры"):
            dish_types.append("гарнир")

        if preferences.get("хочу_салаты") and preferences.get("есть_специи"):
            dish_types.append("салат")

        return dish_types

    def _calculate_compatibility(self, proto_frame: Frame, user_budget: str,
                                 available_dish_types: List[str], preferences: Dict[str, Any]) -> float:
        """Вычисляет совместимость рецепта с пользователем"""
        score = 0.0
        total_possible = 0.0

        # Проверка бюджета (вес 0.35)
        required_budget = proto_frame.get_slot_value("требуемая_категория_бюджета")
        if required_budget:
            total_possible += 0.35
            if required_budget == user_budget:
                score += 0.35
            elif user_budget == "средний" and required_budget in ["низкий", "высокий"]:
                score += 0.15  # Частичное совпадение

        # Проверка типа блюда (вес 0.35)
        required_dish_type = proto_frame.get_slot_value("требуемый_тип_блюда")
        if required_dish_type:
            total_possible += 0.35
            if required_dish_type in available_dish_types:
                score += 0.35

        # Проверка диетических ограничений (вес 0.15)
        requires_dietary = proto_frame.get_slot_value("требует_диетических_ограничений")
        if requires_dietary is not None:
            total_possible += 0.15
            has_dietary = preferences.get("диетические_ограничения")
            if (requires_dietary and has_dietary) or (not requires_dietary):
                score += 0.15
            elif not requires_dietary:  # Рецепт не требует ограничений
                score += 0.1  # Частичное совпадение

        # Проверка времени приготовления (вес 0.15)
        recommended_time = proto_frame.get_slot_value("требуемое_время_приготовления")
        user_prefers_fast = preferences.get("быстрое_приготовление")
        user_preferred_time = preferences.get("время_приготовления", "среднее")
        if recommended_time:
            total_possible += 0.15
            if recommended_time == user_preferred_time:
                score += 0.15
            elif (recommended_time == "быстро" and user_prefers_fast) or \
                    (recommended_time == "долго" and not user_prefers_fast):
                score += 0.1  # Частичное совпадение

        return score / total_possible if total_possible > 0 else 0.0

    def get_best_recommendation(self) -> Optional[str]:
        """Возвращает лучшую рекомендацию"""
        proto_frames = self.working_memory.get_proto_frames()
        if not proto_frames:
            return None

        # Берем наиболее совместимый протофрейм
        best_proto = max(
            proto_frames,
            key=lambda f: f.get_slot_value("совместимость") or 0
        )

        # Получаем имя исходного рецепта
        ako_frame = best_proto.slots["AKO"].value
        if ako_frame:
            return ako_frame.name

        return None

    def get_all_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Возвращает все рекомендации с деталями"""
        proto_frames = self.working_memory.get_proto_frames()
        recommendations = []

        for proto in proto_frames[:limit]:
            compatibility = proto.get_slot_value("совместимость") or 0
            ako_frame = proto.slots["AKO"].value

            if ako_frame:
                recommendations.append({
                    "recipe": ako_frame.name,
                    "compatibility": compatibility,
                    "budget": proto.get_slot_value("требуемая_категория_бюджета"),
                    "dish_type": proto.get_slot_value("требуемый_тип_блюда"),
                    "cooking_time": proto.get_slot_value("требуемое_время_приготовления"),
                    "difficulty": proto.get_slot_value("сложность")
                })

        return recommendations


# ============================================================================
# МОДУЛЬ 5: КОМПОНЕНТА ОБЪЯСНЕНИЯ (explanation_component.py)
# ============================================================================

class ExplanationComponent:
    """Компонента объяснения для фреймовой системы"""

    def __init__(self, inference_engine: InferenceEngine):
        self.ie = inference_engine

    def explain_recommendation(self, recipe_name: str) -> str:
        """Объясняет, почему данный рецепт был рекомендован"""
        # Находим соответствующий протофрейм
        proto_frames = self.ie.working_memory.get_proto_frames()
        target_proto = None

        for proto in proto_frames:
            ako_frame = proto.slots["AKO"].value
            if ako_frame and ako_frame.name == recipe_name:
                target_proto = proto
                break

        if not target_proto:
            return f"Рецепт '{recipe_name}' не найден среди рекомендаций"

        # Получаем сведения о совместимости
        compatibility = target_proto.get_slot_value("совместимость") or 0
        required_budget = target_proto.get_slot_value("требуемая_категория_бюджета") or "любой"
        required_dish_type = target_proto.get_slot_value("требуемый_тип_блюда") or "любой"
        cooking_time = target_proto.get_slot_value("требуемое_время_приготовления") or "любое"
        requires_dietary = target_proto.get_slot_value("требует_диетических_ограничений")

        # Формируем объяснение
        explanation = f"📊 ОБЪЯСНЕНИЕ РЕКОМЕНДАЦИИ РЕЦЕПТА '{recipe_name}':\n"
        explanation += f"   Совместимость: {compatibility:.1%}\n\n"
        explanation += "🔍 КРИТЕРИИ СООТВЕТСТВИЯ:\n"

        preferences = self.ie.working_memory.get_preferences()

        # Проверка бюджета
        user_budget = self.ie._determine_budget_category(preferences)
        budget_match = required_budget == user_budget
        explanation += f"1. 💰 Бюджет: рецепт для '{required_budget}' бюджета, у вас '{user_budget}'"
        explanation += f" {'✓' if budget_match else '✗'}\n"

        # Проверка типа блюда
        available_dish_types = self.ie._determine_available_dish_types(preferences)
        dish_type_match = required_dish_type in available_dish_types
        explanation += f"2. 🍽️ Тип блюда: рецепт типа '{required_dish_type}', вам доступны: {', '.join(available_dish_types) if available_dish_types else 'нет предпочтений'}"
        explanation += f" {'✓' if dish_type_match else '✗'}\n"

        # Проверка времени приготовления
        user_prefers_fast = preferences.get("быстрое_приготовление")
        user_preferred_time = preferences.get("время_приготовления", "среднее")
        time_match = cooking_time == user_preferred_time
        explanation += f"3. ⏱️ Время приготовления: рецепт на '{cooking_time}', вы предпочитаете '{user_preferred_time}'"
        explanation += f" {'✓' if time_match else '✗'}\n"

        # Проверка диетических ограничений
        if requires_dietary is not None:
            has_dietary = preferences.get("диетические_ограничения")
            dietary_match = (requires_dietary and has_dietary) or (not requires_dietary)
            explanation += f"4. 🥗 Диетические ограничения: рецепт {'требует' if requires_dietary else 'не требует'} ограничений, у вас {'есть' if has_dietary else 'нет'} ограничений"
            explanation += f" {'✓' if dietary_match else '✗'}\n"

        # Получаем причину через IF-NEEDED процедуру
        reason_slot = target_proto.get_slot("причина_рекомендации")
        if reason_slot:
            reason = target_proto.get_slot_value("причина_рекомендации")
            if reason:
                explanation += f"\n💡 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:\n   {reason}"

        # Похожие рецепты
        similar_recipes = self.ie.kb._suggest_similar_recipes(target_proto.slots["AKO"].value)
        if similar_recipes:
            explanation += f"\n🍳 ПОХОЖИЕ РЕЦЕПТЫ:\n   {', '.join(similar_recipes)}"

        return explanation

    def explain_inference_process(self) -> str:
        """Объясняет процесс вывода согласно теории Минского"""
        explanation = "🧠 ПРОЦЕСС ВЫВОДА ПО ТЕОРИИ ФРЕЙМОВ МИНСКОГО:\n"
        explanation += "═" * 60 + "\n"

        trace = self.ie.working_memory.get_trace()

        if not trace:
            explanation += "Процесс вывода еще не выполнялся.\n"
            return explanation

        explanation += "1. 📥 АНАЛИЗ ВХОДНЫХ ДАННЫХ:\n"
        explanation += "   • Созданы пользовательские предпочтения\n"

        proto_count = len([entry for entry in trace if entry.action == "add_proto_frame"])
        explanation += f"\n2. 🏗️ СОЗДАНИЕ ПРОТОФРЕЙМОВ:\n"
        explanation += f"   • Создано {proto_count} протофреймов (незаполненные шаблоны)\n"

        explanation += "\n3. 🔗 СВЯЗЫВАНИЕ С ЭКЗОФРЕЙМАМИ:\n"
        explanation += "   • Установлены связи AKO от протофреймов к фреймам из БЗ\n"

        explanation += "\n4. 📝 ЗАПОЛНЕНИЕ СЛОТОВ:\n"
        explanation += "   • Заполнены слоты протофреймов на основе предпочтений\n"
        explanation += "   • Активированы IF-NEEDED процедуры для вычисления значений\n"

        frame_matches = [entry for entry in trace if entry.action == "frame_match"]
        explanation += f"\n5. 📊 ОЦЕНКА СОВМЕСТИМОСТИ:\n"
        explanation += f"   • Оценено {len(frame_matches)} совпадений с рецептами\n"

        explanation += "\n6. 🏆 ВЫБОР РЕКОМЕНДАЦИЙ:\n"
        explanation += "   • Отсортированы рецепты по уровню совместимости\n"
        explanation += "   • Выбраны наиболее подходящие варианты\n"

        return explanation

    def get_detailed_trace(self) -> str:
        """Возвращает детальную историю вывода"""
        trace = self.ie.working_memory.get_trace()

        if not trace:
            return "История вывода пуста."

        output = "📋 ДЕТАЛЬНАЯ ИСТОРИЯ ВЫВОДА:\n"
        output += "═" * 60 + "\n"

        for i, entry in enumerate(trace, 1):
            output += f"{i}. {entry.action.upper()}: {entry.frame_name}\n"
            if entry.details:
                for key, value in entry.details.items():
                    output += f"   • {key}: {value}\n"

        return output

    def explain_slot_inheritance(self, frame_name: str, slot_name: str) -> str:
        """Объясняет наследование значения слота"""
        # Находим фрейм
        frame = self.ie.kb.get_frame(frame_name)
        if not frame:
            return f"Фрейм '{frame_name}' не найден в базе знаний."

        # Получаем значение с объяснением пути наследования
        value = frame.get_slot_value(slot_name)

        explanation = f"🔗 НАСЛЕДОВАНИЕ ЗНАЧЕНИЯ ДЛЯ СЛОТА '{slot_name}' ВО ФРЕЙМЕ '{frame_name}':\n"

        # Проверяем локальное значение
        local_slot = frame.get_slot(slot_name)
        if local_slot and local_slot.value is not None:
            explanation += f"1. 📍 Локальное значение: {local_slot.value}\n"
            return explanation

        # Ищем значение в цепочке наследования
        current = frame
        level = 1
        inheritance_chain = []

        while current:
            ako = current.slots["AKO"].value
            if not ako:
                break

            parent_slot = ako.get_slot(slot_name)
            if parent_slot and parent_slot.get_value(ako) is not None:
                parent_value = parent_slot.get_value(ako)
                inheritance_chain.append((ako.name, parent_value))

            current = ako

        if inheritance_chain:
            explanation += "📍 Значение получено через наследование:\n"
            for i, (parent_name, parent_value) in enumerate(inheritance_chain, 1):
                explanation += f"   {i}. От '{parent_name}': {parent_value}\n"
            explanation += f"\n🎯 Финальное значение: {inheritance_chain[-1][1]}"
        else:
            explanation += "❌ Значение не найдено ни локально, ни через наследование.\n"

        return explanation

    def explain_frame_hierarchy(self, frame_name: str) -> str:
        """Объясняет иерархию наследования фрейма"""
        frame = self.ie.kb.get_frame(frame_name)
        if not frame:
            return f"Фрейм '{frame_name}' не найден в базе знаний."

        explanation = f"🌳 ИЕРАРХИЯ НАСЛЕДОВАНИЯ ФРЕЙМА '{frame_name}':\n"

        current = frame
        level = 0
        hierarchy = []

        while current:
            hierarchy.append((level, current.name))
            ako = current.slots["AKO"].value
            if not ako:
                break
            current = ako
            level += 1

        for level, name in hierarchy:
            indent = "  " * level
            explanation += f"{indent}• {name}\n"

        return explanation


# ============================================================================
# МОДУЛЬ 6: ОСНОВНОЙ МОДУЛЬ ЗАПУСКА (main.py)
# ============================================================================

def create_json_knowledge_base(filename: str = "recipe_frames.json"):
    """Создает JSON файл с базой знаний фреймов"""
    knowledge_base = {
        "name": "Фреймовая база знаний рецептов",
        "description": "База знаний для подбора рецептов на основе теории фреймов Минского",
        "frames": [
            # ==================== АБСТРАКТНЫЕ ФРЕЙМЫ (уровень 1) ====================
            {
                "name": "Блюдо",
                "ako": None,
                "slots": [
                    {
                        "name": "название",
                        "data_type": "TEXT",
                        "inheritance": "U"
                    },
                    {
                        "name": "кухня",
                        "data_type": "TEXT",
                        "inheritance": "O"
                    },
                    {
                        "name": "количество_порций",
                        "data_type": "INTEGER",
                        "inheritance": "O"
                    }
                ]
            },

            # ==================== ТИПЫ БЛЮД ПО БЮДЖЕТУ (уровень 2) ====================
            {
                "name": "Блюдо_низкого_бюджета",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "категория_бюджета",
                        "value": "низкий",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "range": ["низкий"]
                    },
                    {
                        "name": "максимальная_стоимость",
                        "data_type": "INTEGER",
                        "inheritance": "O"
                    }
                ]
            },
            {
                "name": "Блюдо_среднего_бюджета",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "категория_бюджета",
                        "value": "средний",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "range": ["средний"]
                    }
                ]
            },
            {
                "name": "Блюдо_высокого_бюджета",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "категория_бюджета",
                        "value": "высокий",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "range": ["высокий"]
                    }
                ]
            },

            # ==================== ТИПЫ БЛЮД ПО КАТЕГОРИИ (уровень 2) ====================
            {
                "name": "Мясное_блюдо",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "тип_блюда",
                        "value": "мясное",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    },
                    {
                        "name": "основной_ингредиент",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "range": ["говядина", "свинина", "курица", "индейка"]
                    }
                ]
            },
            {
                "name": "Суп",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "тип_блюда",
                        "value": "суп",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    },
                    {
                        "name": "консистенция",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "range": ["прозрачный", "густой", "крем-суп"]
                    }
                ]
            },
            {
                "name": "Гарнир",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "тип_блюда",
                        "value": "гарнир",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    },
                    {
                        "name": "основа",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "range": ["крупа", "овощи", "макароны", "картофель"]
                    }
                ]
            },
            {
                "name": "Салат",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "тип_блюда",
                        "value": "салат",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    },
                    {
                        "name": "заправка",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "range": ["майонез", "оливковое масло", "сметана", "йогурт"]
                    }
                ]
            },

            # ==================== КОНКРЕТНЫЕ РЕЦЕПТЫ (уровень 3) ====================
            # Мясные блюда низкого бюджета
            {
                "name": "Котлеты",
                "ako": "Мясное_блюдо",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_низкого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "быстро",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": False,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "низкая",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    },
                    {
                        "name": "количество_ингредиентов",
                        "value": 5,
                        "data_type": "INTEGER",
                        "inheritance": "S"
                    },
                    {
                        "name": "причина_рекомендации",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "triggers": {
                            "IF-NEEDED": "get_recommendation_reason"
                        }
                    }
                ]
            },
            {
                "name": "Гуляш",
                "ako": "Мясное_блюдо",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_низкого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "долго",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": False,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "средняя",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    },
                    {
                        "name": "количество_ингредиентов",
                        "value": 8,
                        "data_type": "INTEGER",
                        "inheritance": "S"
                    }
                ]
            },

            # Мясные блюда высокого бюджета
            {
                "name": "Стейк",
                "ako": "Мясное_блюдо",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_высокого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "быстро",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": False,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "средняя",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },
            {
                "name": "Утка_по_пекински",
                "ako": "Мясное_блюдо",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_высокого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "долго",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": False,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "высокая",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },

            # Супы низкого бюджета
            {
                "name": "Куриный_суп",
                "ako": "Суп",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_низкого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "быстро",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": True,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "низкая",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },
            {
                "name": "Борщ",
                "ako": "Суп",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_низкого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "долго",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": True,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "средняя",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },

            # Супы высокого бюджета
            {
                "name": "Том_ям",
                "ako": "Суп",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_высокого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "среднее",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": True,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "высокая",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },

            # Гарниры низкого бюджета
            {
                "name": "Гречка",
                "ako": "Гарнир",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_низкого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "быстро",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": True,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "низкая",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },
            {
                "name": "Рис_с_овощами",
                "ako": "Гарнир",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_среднего_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "среднее",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": True,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "средняя",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },

            # Салаты
            {
                "name": "Овощной_салат",
                "ako": "Салат",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_низкого_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "быстро",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": True,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "низкая",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },
            {
                "name": "Цезарь",
                "ako": "Салат",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_среднего_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "среднее",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": False,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "средняя",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            },
            {
                "name": "Греческий_салат",
                "ako": "Салат",
                "slots": [
                    {
                        "name": "AKO",
                        "value": "!ref:Блюдо_среднего_бюджета",
                        "data_type": "FRAME",
                        "inheritance": "S"
                    },
                    {
                        "name": "время_приготовления",
                        "value": "быстро",
                        "data_type": "TEXT",
                        "inheritance": "S",
                        "triggers": {
                            "IF-ADDED": "validate_cooking_time"
                        }
                    },
                    {
                        "name": "диетические_ограничения",
                        "value": True,
                        "data_type": "BOOLEAN",
                        "inheritance": "S"
                    },
                    {
                        "name": "сложность",
                        "value": "низкая",
                        "data_type": "TEXT",
                        "inheritance": "S"
                    }
                ]
            }
        ]
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

    print(f"✓ JSON файл базы знаний создан: {filename}")
    print(f"  Содержит {len(knowledge_base['frames'])} фреймов")


def get_user_input() -> Dict[str, Any]:
    """Запрашивает у пользователя предпочтения"""
    print("\n" + "=" * 60)
    print("ВВОД ПРЕДПОЧТЕНИЙ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)

    def ask_yes_no(question: str) -> bool:
        while True:
            answer = input(f"{question} (да/нет): ").strip().lower()
            if answer in ['да', 'д', 'yes', 'y']:
                return True
            if answer in ['нет', 'н', 'no', 'n']:
                return False
            print("Пожалуйста, введите 'да' или 'нет'.")

    def ask_budget() -> str:
        print("\n1. 💰 БЮДЖЕТ:")
        print("   1. Низкий (до 1000 руб)")
        print("   2. Средний (1000-3000 руб)")
        print("   3. Высокий (более 3000 руб)")
        while True:
            choice = input("Ваш выбор (1-3): ").strip()
            if choice == "1":
                return "низкий"
            elif choice == "2":
                return "средний"
            elif choice == "3":
                return "высокий"
            print("Пожалуйста, введите 1, 2 или 3.")

    def ask_cooking_time() -> str:
        print("\n2. ⏱️ ПРЕДПОЧТЕНИЯ ПО ВРЕМЕНИ ПРИГОТОВЛЕНИЯ:")
        print("   1. Быстрое приготовление (до 30 мин)")
        print("   2. Среднее время (30-60 мин)")
        print("   3. Долгое приготовление (более 60 мин)")
        while True:
            choice = input("Ваш выбор (1-3): ").strip()
            if choice == "1":
                return "быстро"
            elif choice == "2":
                return "среднее"
            elif choice == "3":
                return "долго"
            print("Пожалуйста, введите 1, 2 или 3.")

    preferences = {}

    # Бюджет
    preferences["бюджет"] = ask_budget()

    # Время приготовления
    preferences["время_приготовления"] = ask_cooking_time()

    # Диетические ограничения
    print("\n3. 🥗 ДИЕТИЧЕСКИЕ ОГРАНИЧЕНИЯ:")
    preferences["диетические_ограничения"] = ask_yes_no("  • Есть ли у вас диетические ограничения?")

    # Предпочтения по типам блюд
    print("\n4. 🍽️ ПРЕДПОЧТЕНИЯ ПО ТИПАМ БЛЮД:")
    preferences["хочу_мясные_блюда"] = ask_yes_no("  • Хотите ли вы мясные блюда?")
    preferences["хочу_супы"] = ask_yes_no("  • Хотите ли вы супы?")
    preferences["хочу_гарниры"] = ask_yes_no("  • Хотите ли вы гарниры?")
    preferences["хочу_салаты"] = ask_yes_no("  • Хотите ли вы салаты?")

    # Наличие специй
    print("\n5. 🌶️ НАЛИЧИЕ СПЕЦИЙ:")
    preferences["есть_специи"] = ask_yes_no("  • Есть ли у вас специи для приготовления?")

    # Быстрое приготовление
    print("\n6. ⚡ ПРЕДПОЧТЕНИЯ ПО СКОРОСТИ:")
    preferences["быстрое_приготовление"] = ask_yes_no("  • Предпочитаете быстрое приготовление?")

    return preferences


def display_welcome():
    """Отображает приветственное сообщение"""
    print("\n" + "=" * 60)
    print("🍳 ФРЕЙМОВАЯ ЭКСПЕРТНАЯ СИСТЕМА: ПОДБОР РЕЦЕПТОВ")
    print("📚 Основана на теории фреймов Марвина Минского")
    print("💾 База знаний хранится в формате JSON")
    print("=" * 60)
    print("\nСистема поможет подобрать идеальный рецепт на основе:")
    print("  • Вашего бюджета")
    print("  • Диетических ограничений")
    print("  • Предпочтений по типам блюд")
    print("  • Времени приготовления")
    print("  • Наличия ингредиентов и специй")


def main():
    """Основная функция запуска системы"""
    display_welcome()

    # Создаем файл с базой знаний, если его нет
    JSON_FILE = "recipe_frames.json"
    if not os.path.exists(JSON_FILE):
        print(f"\nСоздаю JSON файл с базой знаний: {JSON_FILE}")
        create_json_knowledge_base(JSON_FILE)

    try:
        # Создаем компоненты системы
        print("\nЗагрузка базы знаний из JSON...")
        kb = KnowledgeBase(JSON_FILE)
        ie = InferenceEngine(kb)
        ec = ExplanationComponent(ie)

        print(f"✓ Загружено {len(kb.get_all_frames())} фреймов из {JSON_FILE}")

    except FileNotFoundError:
        print(f"✗ Ошибка: Файл {JSON_FILE} не найден!")
        return
    except Exception as e:
        print(f"✗ Ошибка при загрузке базы знаний: {e}")
        return

    # Запрашиваем предпочтения пользователя
    user_preferences = get_user_input()

    print("\n" + "=" * 60)
    print("🔍 ВЫПОЛНЕНИЕ ЛОГИЧЕСКОГО ВЫВОДА")
    print("=" * 60)

    # Устанавливаем предпочтения и выполняем вывод
    ie.set_user_preferences(user_preferences)
    matched_frames = ie.frame_based_inference()

    # Выводим процесс вывода
    print("\n" + ec.explain_inference_process())

    # Выводим результаты
    if matched_frames:
        best_recommendation = ie.get_best_recommendation()
        all_recommendations = ie.get_all_recommendations(limit=5)

        print("\n" + "=" * 60)
        print("🏆 РЕКОМЕНДАЦИИ")
        print("=" * 60)

        print(f"\nНайдено {len(matched_frames)} подходящих рецептов:")
        for i, rec in enumerate(all_recommendations, 1):
            compatibility_str = f"{rec['compatibility']:.1%}".rjust(6)
            recipe_name = rec['recipe'].replace('_', ' ')
            print(f"{i}. {recipe_name.ljust(25)} [совместимость: {compatibility_str}]")

        if best_recommendation:
            best_recipe_name = best_recommendation.replace('_', ' ')
            print(f"\n🎯 Лучшая рекомендация: {best_recipe_name}")

        print("\n" + "=" * 60)
        print("📊 ОБЪЯСНЕНИЕ РЕКОМЕНДАЦИИ")
        print("=" * 60)

        if best_recommendation:
            detailed_explanation = ec.explain_recommendation(best_recommendation)
            print(f"\n{detailed_explanation}")

        # Дополнительные возможности объяснения
        print("\n" + "=" * 60)
        print("🔧 ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ")
        print("=" * 60)

        while True:
            print("\nВыберите опцию:")
            print("1. 📋 Показать детальную историю вывода")
            print("2. 🔗 Объяснить наследование слота для конкретного рецепта")
            print("3. 🌳 Показать иерархию наследования фрейма")
            print("4. 🍽️ Получить все рекомендации с деталями")
            print("5. 🚪 Выход")

            choice = input("\nВаш выбор (1-5): ").strip()

            if choice == "1":
                print("\n" + ec.get_detailed_trace())

            elif choice == "2":
                recipe_name = input("Введите название рецепта (например, Котлеты): ").strip()
                slot_name = input("Введите название слота (например, категория_бюджета): ").strip()
                explanation = ec.explain_slot_inheritance(recipe_name, slot_name)
                print(f"\n{explanation}")

            elif choice == "3":
                frame_name = input("Введите название фрейма (например, Стейк): ").strip()
                explanation = ec.explain_frame_hierarchy(frame_name)
                print(f"\n{explanation}")

            elif choice == "4":
                print("\n" + "=" * 60)
                print("📈 ВСЕ РЕКОМЕНДАЦИИ С ДЕТАЛЯМИ")
                print("=" * 60)
                for rec in all_recommendations:
                    recipe_name = rec['recipe'].replace('_', ' ')
                    print(f"\n🍳 {recipe_name}:")
                    print(f"   Совместимость: {rec['compatibility']:.1%}")
                    print(f"   Категория бюджета: {rec['budget']}")
                    print(f"   Тип блюда: {rec['dish_type']}")
                    print(f"   Время приготовления: {rec['cooking_time']}")
                    print(f"   Сложность: {rec['difficulty']}")

            elif choice == "5":
                break

            else:
                print("Неверный выбор. Попробуйте снова.")

    else:
        print("\n⚠ Не удалось найти подходящие рецепты на основе ваших предпочтений.")
        print("Попробуйте изменить предпочтения (например, указать больше типов блюд).")

    print("\n" + "=" * 60)
    print("✅ РАБОТА СИСТЕМЫ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    main()