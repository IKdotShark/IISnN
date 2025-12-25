#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МОДУЛЬ 2: БАЗА ЗНАНИЙ (knowledge_base.py)
База знаний, хранящая фреймы согласно теории Минского в формате JSON
"""

import json
from typing import Dict, List, Any, Optional, Callable
from frame import Frame, Slot, InheritanceType, DataType, TriggerType


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
        self._procedures["determine_budget_category"] = self._determine_budget_category

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

    def _determine_budget_category(self, frame) -> str:
        """IF-NEEDED: Определяет категорию бюджета на основе стоимости"""
        max_cost = frame.get_slot_value("максимальная_стоимость")
        if max_cost is None:
            return "средний"

        if max_cost < 1000:
            return "низкий"
        elif max_cost <= 3000:
            return "средний"
        else:
            return "высокий"

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
        recipes = []
        for name in recipe_names:
            if name in self.frames:
                recipes.append(self.frames[name])
        return recipes