#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МОДУЛЬ 6: ОСНОВНОЙ МОДУЛЬ ЗАПУСКА (main.py)
Основной модуль запуска фреймовой экспертной системы
"""

import os
import sys
from typing import Dict, Any
import json

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import KnowledgeBase
from inference_engine import InferenceEngine
from explanation_component import ExplanationComponent


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
                        "name": "максимальная_стоимость",
                        "value": 800,
                        "data_type": "INTEGER",
                        "inheritance": "S"
                    },
                    {
                        "name": "категория_бюджета",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "triggers": {
                            "IF-NEEDED": "determine_budget_category"
                        }
                    }
                ]
            },
            {
                "name": "Блюдо_среднего_бюджета",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "максимальная_стоимость",
                        "value": 2000,
                        "data_type": "INTEGER",
                        "inheritance": "S"
                    },
                    {
                        "name": "категория_бюджета",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "triggers": {
                            "IF-NEEDED": "determine_budget_category"
                        }
                    }
                ]
            },
            {
                "name": "Блюдо_высокого_бюджета",
                "ako": "Блюдо",
                "slots": [
                    {
                        "name": "максимальная_стоимость",
                        "value": 5000,
                        "data_type": "INTEGER",
                        "inheritance": "S"
                    },
                    {
                        "name": "категория_бюджета",
                        "data_type": "TEXT",
                        "inheritance": "O",
                        "triggers": {
                            "IF-NEEDED": "determine_budget_category"
                        }
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

    print("JSON файл базы знаний создан: {0}".format(filename))
    print("Содержит {0} фреймов".format(len(knowledge_base['frames'])))


def get_user_input() -> Dict[str, Any]:
    """Запрашивает у пользователя предпочтения"""
    print("\n" + "=" * 60)
    print("ВВОД ПРЕДПОЧТЕНИЙ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)

    def ask_yes_no(question: str) -> bool:
        while True:
            answer = input("{0} (да/нет): ".format(question)).strip().lower()
            if answer in ['да', 'д', 'yes', 'y']:
                return True
            if answer in ['нет', 'н', 'no', 'n']:
                return False
            print("Пожалуйста, введите 'да' или 'нет'.")

    def ask_int(prompt: str) -> int:
        while True:
            try:
                value = int(input("{0}: ".format(prompt)).strip())
                if value >= 0:
                    return value
                print("Бюджет не может быть отрицательным.")
            except ValueError:
                print("Введите целое число.")

    def ask_cooking_time() -> str:
        print("\nПРЕДПОЧТЕНИЯ ПО ВРЕМЕНИ ПРИГОТОВЛЕНИЯ:")
        print("1. Быстрое приготовление (до 30 мин)")
        print("2. Среднее время (30-60 мин)")
        print("3. Долгое приготовление (более 60 мин)")
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
    print("\n1. БЮДЖЕТ:")
    preferences["бюджет"] = ask_int("  * Введите сумму, которую готовы потратить (в рублях):")

    # Время приготовления
    preferences["время_приготовления"] = ask_cooking_time()

    # Диетические ограничения
    print("\n2. ДИЕТИЧЕСКИЕ ОГРАНИЧЕНИЯ:")
    preferences["диетические_ограничения"] = ask_yes_no("  * Есть ли у вас диетические ограничения?")

    # Предпочтения по типам блюд
    print("\n3. ПРЕДПОЧТЕНИЯ ПО ТИПАМ БЛЮД:")
    preferences["хочу_мясные_блюда"] = ask_yes_no("  * Хотите ли вы мясные блюда?")
    preferences["хочу_супы"] = ask_yes_no("  * Хотите ли вы супы?")
    preferences["хочу_гарниры"] = ask_yes_no("  * Хотите ли вы гарниры?")
    preferences["хочу_салаты"] = ask_yes_no("  * Хотите ли вы салаты?")

    # Наличие специй
    print("\n4. НАЛИЧИЕ СПЕЦИЙ:")
    preferences["есть_специи"] = ask_yes_no("  * Есть ли у вас специи для приготовления?")

    return preferences


def display_welcome():
    """Отображает приветственное сообщение"""
    print("\n" + "=" * 60)
    print("ФРЕЙМОВАЯ ЭКСПЕРТНАЯ СИСТЕМА: ПОДБОР РЕЦЕПТОВ")
    print("Основана на теории фреймов Марвина Минского")
    print("База знаний хранится в формате JSON")
    print("=" * 60)
    print("\nСистема поможет подобрать идеальный рецепт на основе:")
    print("  * Вашего бюджета (указывается суммой)")
    print("  * Диетических ограничений")
    print("  * Предпочтений по типам блюд")
    print("  * Времени приготовления")
    print("  * Наличия ингредиентов и специй")


def main():
    """Основная функция запуска системы"""
    display_welcome()

    # Создаем файл с базой знаний, если его нет
    JSON_FILE = "recipe_frames.json"
    if not os.path.exists(JSON_FILE):
        print("\nСоздаю JSON файл с базой знаний: {0}".format(JSON_FILE))
        create_json_knowledge_base(JSON_FILE)

    try:
        # Создаем компоненты системы
        print("\nЗагрузка базы знаний из JSON...")
        kb = KnowledgeBase(JSON_FILE)
        ie = InferenceEngine(kb)
        ec = ExplanationComponent(ie)

        print("Загружено {0} фреймов из {1}".format(len(kb.get_all_frames()), JSON_FILE))

    except FileNotFoundError:
        print("Ошибка: Файл {0} не найден!".format(JSON_FILE))
        return
    except Exception as e:
        print("Ошибка при загрузке базы знаний: {0}".format(e))
        return

    # Запрашиваем предпочтения пользователя
    user_preferences = get_user_input()

    print("\n" + "=" * 60)
    print("ВЫПОЛНЕНИЕ ЛОГИЧЕСКОГО ВЫВОДА")
    print("=" * 60)

    # Устанавливаем предпочтения и выполняем вывод
    ie.set_user_preferences(user_preferences)
    matched_frames = ie.frame_based_inference()

    # Выводим процесс вывода
    print("\n" + ec.explain_inference_process())

    # Выводим результаты
    if matched_frames:
        best_recommendation = ie.get_best_recommendation()
        all_recommendations = ie.get_all_recommendations(limit=10)

        print("\n" + "=" * 60)
        print("РЕКОМЕНДАЦИИ")
        print("=" * 60)

        if all_recommendations:
            print("\nНайдено {0} подходящих рецептов:".format(len(all_recommendations)))
            for i, rec in enumerate(all_recommendations, 1):
                compatibility_str = "{0:.1%}".format(rec['compatibility']).rjust(6)
                recipe_name = rec['recipe'].replace('_', ' ')
                print("{0}. {1} [совместимость: {2}]".format(i, recipe_name.ljust(25), compatibility_str))

            if best_recommendation:
                best_recipe_name = best_recommendation.replace('_', ' ')
                print("\nЛучшая рекомендация: {0}".format(best_recipe_name))

            print("\n" + "=" * 60)
            print("ОБЪЯСНЕНИЕ РЕКОМЕНДАЦИИ")
            print("=" * 60)

            if best_recommendation:
                detailed_explanation = ec.explain_recommendation(best_recommendation)
                print("\n{0}".format(detailed_explanation))

            # Дополнительные возможности объяснения
            print("\n" + "=" * 60)
            print("ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ")
            print("=" * 60)

            while True:
                print("\nВыберите опцию:")
                print("1. Показать детальную историю вывода")
                print("2. Объяснить наследование слота для конкретного рецепта")
                print("3. Показать иерархию наследования фрейма")
                print("4. Получить все рекомендации с деталями")
                print("5. Выход")

                choice = input("\nВаш выбор (1-5): ").strip()

                if choice == "1":
                    print("\n" + ec.get_detailed_trace())

                elif choice == "2":
                    recipe_name = input("Введите название рецепта (например, Котлеты): ").strip()
                    slot_name = input("Введите название слота (например, категория_бюджета): ").strip()
                    explanation = ec.explain_slot_inheritance(recipe_name, slot_name)
                    print("\n{0}".format(explanation))

                elif choice == "3":
                    frame_name = input("Введите название фрейма (например, Стейк): ").strip()
                    explanation = ec.explain_frame_hierarchy(frame_name)
                    print("\n{0}".format(explanation))

                elif choice == "4":
                    print("\n" + "=" * 60)
                    print("ВСЕ РЕКОМЕНДАЦИИ С ДЕТАЛЯМИ")
                    print("=" * 60)
                    for rec in all_recommendations:
                        recipe_name = rec['recipe'].replace('_', ' ')
                        print("\n{0}:".format(recipe_name))
                        print("   Совместимость: {0:.1%}".format(rec['compatibility']))
                        print("   Категория бюджета: {0}".format(rec['budget']))
                        print("   Тип блюда: {0}".format(rec['dish_type']))
                        print("   Время приготовления: {0}".format(rec['cooking_time']))
                        print("   Сложность: {0}".format(rec['difficulty']))

                elif choice == "5":
                    break

                else:
                    print("Неверный выбор. Попробуйте снова.")
        else:
            print("\nНе удалось найти подходящие рецепты на основе ваших предпочтений.")
    else:
        print("\nНе удалось найти подходящие рецепты на основе ваших предпочтений.")
        print("Попробуйте изменить предпочтения (например, указать больше типов блюд).")

    print("\n" + "=" * 60)
    print("РАБОТА СИСТЕМЫ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    main()