#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МОДУЛЬ 5: КОМПОНЕНТА ОБЪЯСНЕНИЯ (explanation_component.py)
Компонента объяснения для фреймовой системы
"""

from typing import Dict, List, Any
from inference_engine import InferenceEngine
from frame import Frame


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
        explanation = "ОБЪЯСНЕНИЕ РЕКОМЕНДАЦИИ РЕЦЕПТА '{0}':\n".format(recipe_name)
        explanation += "   Совместимость: {0:.1%}\n\n".format(compatibility)
        explanation += "КРИТЕРИИ СООТВЕТСТВИЯ:\n"

        preferences = self.ie.working_memory.get_preferences()

        # Проверка бюджета
        user_budget = self.ie._determine_budget_category(preferences)
        budget_match = required_budget == user_budget
        explanation += "1. Бюджет: рецепт для '{0}' бюджета, у вас '{1}'".format(required_budget, user_budget)
        explanation += " [СОВПАДАЕТ]" if budget_match else " [НЕ СОВПАДАЕТ]"
        explanation += "\n"

        # Проверка типа блюда
        available_dish_types = self.ie._determine_available_dish_types(preferences)
        dish_type_match = required_dish_type in available_dish_types
        explanation += "2. Тип блюда: рецепт типа '{0}', вам доступны: {1}".format(
            required_dish_type,
            ', '.join(available_dish_types) if available_dish_types else 'нет предпочтений'
        )
        explanation += " [СОВПАДАЕТ]" if dish_type_match else " [НЕ СОВПАДАЕТ]"
        explanation += "\n"

        # Проверка времени приготовления
        user_preferred_time = preferences.get("время_приготовления", "среднее")
        time_match = cooking_time == user_preferred_time
        explanation += "3. Время приготовления: рецепт на '{0}', вы предпочитаете '{1}'".format(cooking_time, user_preferred_time)
        explanation += " [СОВПАДАЕТ]" if time_match else " [НЕ СОВПАДАЕТ]"
        explanation += "\n"

        # Проверка диетических ограничений
        if requires_dietary is not None:
            has_dietary = preferences.get("диетические_ограничения")
            dietary_match = (requires_dietary and has_dietary) or (not requires_dietary)
            explanation += "4. Диетические ограничения: рецепт {0} ограничений, у вас {1} ограничений".format(
                'требует' if requires_dietary else 'не требует',
                'есть' if has_dietary else 'нет'
            )
            explanation += " [СОВПАДАЕТ]" if dietary_match else " [НЕ СОВПАДАЕТ]"
            explanation += "\n"

        # Получаем причину через IF-NEEDED процедуру
        reason_slot = target_proto.get_slot("причина_рекомендации")
        if reason_slot:
            reason = target_proto.get_slot_value("причина_рекомендации")
            if reason:
                explanation += "\nДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:\n   {0}".format(reason)

        # Похожие рецепты
        similar_recipes = self.ie.kb._suggest_similar_recipes(target_proto.slots["AKO"].value)
        if similar_recipes:
            explanation += "\nПОХОЖИЕ РЕЦЕПТЫ:\n   {0}".format(', '.join(similar_recipes))

        return explanation

    def explain_inference_process(self) -> str:
        """Объясняет процесс вывода согласно теории Минского"""
        explanation = "ПРОЦЕСС ВЫВОДА ПО ТЕОРИИ ФРЕЙМОВ МИНСКОГО:\n"
        explanation += "=" * 60 + "\n"

        trace = self.ie.working_memory.get_trace()

        if not trace:
            explanation += "Процесс вывода еще не выполнялся.\n"
            return explanation

        explanation += "1. АНАЛИЗ ВХОДНЫХ ДАННЫХ:\n"
        explanation += "   * Созданы пользовательские предпочтения\n"

        proto_count = len([entry for entry in trace if entry.action == "add_proto_frame"])
        explanation += "\n2. СОЗДАНИЕ ПРОТОФРЕЙМОВ:\n"
        explanation += "   * Создано {0} протофреймов (незаполненные шаблоны)\n".format(proto_count)

        explanation += "\n3. СВЯЗЫВАНИЕ С ЭКЗОФРЕЙМАМИ:\n"
        explanation += "   * Установлены связи AKO от протофреймов к фреймам из БЗ\n"

        explanation += "\n4. ЗАПОЛНЕНИЕ СЛОТОВ:\n"
        explanation += "   * Заполнены слоты протофреймов на основе предпочтений\n"
        explanation += "   * Активированы IF-NEEDED процедуры для вычисления значений\n"

        frame_matches = [entry for entry in trace if entry.action == "frame_match"]
        explanation += "\n5. ОЦЕНКА СОВМЕСТИМОСТИ:\n"
        explanation += "   * Оценено {0} совпадений с рецептами\n".format(len(frame_matches))

        explanation += "\n6. ВЫБОР РЕКОМЕНДАЦИЙ:\n"
        explanation += "   * Отсортированы рецепты по уровню совместимости\n"
        explanation += "   * Выбраны наиболее подходящие варианты\n"

        return explanation

    def get_detailed_trace(self) -> str:
        """Возвращает детальную историю вывода"""
        trace = self.ie.working_memory.get_trace()

        if not trace:
            return "История вывода пуста."

        output = "ДЕТАЛЬНАЯ ИСТОРИЯ ВЫВОДА:\n"
        output += "=" * 60 + "\n"

        for i, entry in enumerate(trace, 1):
            output += "{0}. {1}: {2}\n".format(i, entry.action.upper(), entry.frame_name)
            if entry.details:
                for key, value in entry.details.items():
                    output += "   * {0}: {1}\n".format(key, value)

        return output

    def explain_slot_inheritance(self, frame_name: str, slot_name: str) -> str:
        """Объясняет наследование значения слота"""
        # Находим фрейм
        frame = self.ie.kb.get_frame(frame_name)
        if not frame:
            return "Фрейм '{0}' не найден в базе знаний.".format(frame_name)

        # Получаем значение с объяснением пути наследования
        value = frame.get_slot_value(slot_name)

        explanation = "НАСЛЕДОВАНИЕ ЗНАЧЕНИЯ ДЛЯ СЛОТА '{0}' ВО ФРЕЙМЕ '{1}':\n".format(slot_name, frame_name)

        # Проверяем локальное значение
        local_slot = frame.get_slot(slot_name)
        if local_slot and local_slot.value is not None:
            explanation += "1. Локальное значение: {0}\n".format(local_slot.value)
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
            explanation += "Значение получено через наследование:\n"
            for i, (parent_name, parent_value) in enumerate(inheritance_chain, 1):
                explanation += "   {0}. От '{1}': {2}\n".format(i, parent_name, parent_value)
            explanation += "\nФинальное значение: {0}".format(inheritance_chain[-1][1])
        else:
            explanation += "Значение не найдено ни локально, ни через наследование.\n"

        return explanation

    def explain_frame_hierarchy(self, frame_name: str) -> str:
        """Объясняет иерархию наследования фрейма"""
        frame = self.ie.kb.get_frame(frame_name)
        if not frame:
            return "Фрейм '{0}' не найден в базе знаний.".format(frame_name)

        explanation = "ИЕРАРХИЯ НАСЛЕДОВАНИЯ ФРЕЙМА '{0}':\n".format(frame_name)

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
            explanation += "{0}* {1}\n".format(indent, name)

        return explanation