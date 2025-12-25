from __future__ import annotations

"""
CLI-оболочка экспертной системы для подбора рецептов.
"""

from pathlib import Path
from typing import Dict, Tuple

from explanation import ExplanationComponent
from inference_engine import InferenceEngine
from knowledge_base import KnowledgeBase
from working_mem import WorkingMemory

RULES_PATH = Path(__file__).with_name("rules.json")  # Изменено с .yaml на .json


def ask_yes_no(prompt: str) -> bool:
    """Возвращает True/False в зависимости от ответа пользователя."""
    while True:
        answer = input(f"{prompt} (да/нет): ").strip().lower()
        if answer in {"да", "д", "yes", "y"}:
            return True
        if answer in {"нет", "н", "no", "n"}:
            return False
        print("Пожалуйста, введите 'да' или 'нет'.")


def ask_int(prompt: str) -> int:
    """Запрашивает целое число."""
    while True:
        value = input(f"{prompt}: ").strip()
        try:
            return int(value)
        except ValueError:
            print("Введите целое число.")


def collect_initial_facts(wm: WorkingMemory) -> None:
    """Собирает исходные факты на основе ответов пользователя."""
    # Бюджет
    budget = ask_int("Введите ваш бюджет (в рублях)")
    if budget < 1000:
        wm.add_fact("Бюджет = <1000", "user")
    if budget >= 1000:
        wm.add_fact("Бюджет = >=1000", "user")
    if budget <= 3000:
        wm.add_fact("Бюджет = <=3000", "user")
    if budget > 3000:
        wm.add_fact("Бюджет = >3000", "user")

    # Диетические ограничения
    wm.add_fact(
        fact=f"Диетические ограничения = {'да' if ask_yes_no('Есть ли у вас диетические ограничения?') else 'нет'}",
        source="user",
    )

    # Предпочтения по типам блюд
    wm.add_fact(
        fact=f"Хочу мясные блюда = {'да' if ask_yes_no('Хотите ли вы мясные блюда?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Хочу супы = {'да' if ask_yes_no('Хотите ли вы супы?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Хочу гарниры = {'да' if ask_yes_no('Хотите ли вы гарниры?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Хочу салаты = {'да' if ask_yes_no('Хотите ли вы салаты?') else 'нет'}",
        source="user",
    )

    # Наличие специй
    wm.add_fact(
        fact=f"Есть специи = {'да' if ask_yes_no('Есть ли у вас специи?') else 'нет'}",
        source="user",
    )

    # Время приготовления
    wm.add_fact(
        fact=f"Быстрое приготовление = {'да' if ask_yes_no('Предпочитаете быстрое приготовление?') else 'нет'}",
        source="user",
    )


def choose_strategy() -> str:
    """Позволяет выбрать стратегию разрешения конфликтов."""
    strategies: Dict[str, Tuple[str, str]] = {
        "1": ("order", "По порядку правил"),
        "2": ("specificity", "По специфичности (больше условий)"),
        "3": ("recency", "По недавности фактов"),
    }

    print("\nВыберите стратегию разрешения конфликтов:")
    for key, (_, description) in strategies.items():
        print(f"  {key}. {description}")

    while True:
        choice = input("Ваш выбор [1-3]: ").strip()
        if choice in strategies:
            return strategies[choice][0]
        print("Недопустимый выбор, повторите ввод.")


def print_results(wm: WorkingMemory) -> None:
    """Выводит все полученные факты и итоговые рекомендации."""
    print("\nПолученные факты:")
    for record in wm.items():
        source = "пользователь" if record.source == "user" else f"правило {record.source}"
        print(f"  - {record.fact} (источник: {source})")

    recommendations = [fact for fact in wm.facts() if fact.startswith("Результат = ")]
    if recommendations:
        print("\nРекомендации:")
        for fact in recommendations:
            # Извлекаем только название блюда
            dish = fact.replace("Результат = ", "")
            print(f"  * {dish}")
    else:
        print("\nРекомендаций получить не удалось. Попробуйте изменить исходные факты.")


def explanation_loop(explainer: ExplanationComponent) -> None:
    """Интерактивный цикл запросов объяснений."""
    print("\nВведите интересующий факт для объяснения (пустая строка — выход).")
    while True:
        fact = input("Факт: ").strip()
        if not fact:
            break
        try:
            print("\n" + explainer.explain(fact) + "\n")
        except ValueError as error:
            print(f"Ошибка: {error}\n")


def main() -> None:
    # Загрузка базы знаний
    try:
        kb = KnowledgeBase.from_json(RULES_PATH)  # Изменено с from_yaml на from_json
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        return
    except ValueError as e:
        print(f"Ошибка в формате правил: {e}")
        return

    # Инициализация рабочей памяти
    wm = WorkingMemory()

    # Сбор исходных фактов
    print("=" * 50)
    print("СИСТЕМА ВЫБОРА РЕЦЕПТА")
    print("=" * 50)
    collect_initial_facts(wm)

    # Выбор стратегии разрешения конфликтов
    strategy = choose_strategy()

    # Механизм логического вывода
    engine = InferenceEngine(kb)
    applied_rules = engine.infer(wm, strategy=strategy)

    # Вывод сработавших правил
    if applied_rules:
        print("\nСработавшие правила (в порядке применения):")
        for applied in applied_rules:
            print(f"  {applied.iteration}. {applied.rule.id} -> {applied.rule.conclusion}")
    else:
        print("\nНи одно правило не сработало.")

    # Вывод результатов
    print_results(wm)

    # Компонента объяснения
    explainer = ExplanationComponent(wm)
    explanation_loop(explainer)

    print("\nРабота системы завершена. До свидания!")


if __name__ == "__main__":
    main()