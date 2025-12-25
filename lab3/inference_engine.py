#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МОДУЛЬ 4: МЕХАНИЗМ ЛОГИЧЕСКОГО ВЫВОДА (inference_engine.py)
Механизм логического вывода для фреймовой системы
"""

from typing import Dict, List, Any, Optional
from frame import Frame
from knowledge_base import KnowledgeBase
from working_memory import WorkingMemory


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
        self.working_memory.set_preferences(preferences)

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
        """Определяет категорию бюджета пользователя на основе суммы"""
        budget = preferences.get("бюджет", 0)

        if budget < 1000:
            return "низкий"
        elif budget <= 3000:
            return "средний"
        else:
            return "высокий"

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
        user_preferred_time = preferences.get("время_приготовления", "среднее")
        if recommended_time:
            total_possible += 0.15
            if recommended_time == user_preferred_time:
                score += 0.15
            elif (recommended_time == "быстро" and user_preferred_time == "среднее") or \
                    (recommended_time == "среднее" and user_preferred_time in ["быстро", "долго"]):
                score += 0.08  # Частичное совпадение

        return score / total_possible if total_possible > 0 else 0.0

    def get_best_recommendation(self) -> Optional[str]:
        """Возвращает лучшую рекомендацию"""
        proto_frames = self.working_memory.get_proto_frames()
        if not proto_frames:
            return None

        # Находим все протофреймы с ненулевой совместимостью
        valid_frames = [f for f in proto_frames if
                        f.get_slot_value("совместимость") and f.get_slot_value("совместимость") > 0]
        if not valid_frames:
            return None

        # Берем наиболее совместимый протофрейм
        best_proto = max(
            valid_frames,
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

        # Фильтруем только те, у которых есть совместимость
        valid_protos = [p for p in proto_frames if
                        p.get_slot_value("совместимость") and p.get_slot_value("совместимость") > 0]

        for proto in valid_protos[:limit]:
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