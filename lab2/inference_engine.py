from __future__ import annotations

"""
Механизм логического вывода для продукционной ЭС.
"""

from dataclasses import dataclass
from typing import Dict, List, Sequence

from knowledge_base import KnowledgeBase, Rule
from working_mem import WorkingMemory

ConflictStrategy = str


@dataclass
class AppliedRule:
    """Хранит информацию о сработавшем правиле."""

    rule: Rule
    iteration: int


class InferenceEngine:
    """Реализует прямой вывод с несколькими стратегиями разрешения конфликтов."""

    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        self._kb = knowledge_base

    def infer(self, working_memory: WorkingMemory, strategy: ConflictStrategy = "order") -> List[AppliedRule]:
        """
        Выполняет прямой вывод до насыщения.

        Возвращает порядок срабатывания правил.
        """
        applied: List[AppliedRule] = []
        iteration = 0

        while True:
            conflict_set = self._collect_conflict_set(working_memory)
            if not conflict_set:
                break

            rule = self._resolve_conflict(conflict_set, strategy, working_memory)
            if rule is None:
                break

            added = working_memory.add_fact(
                fact=rule.conclusion,
                source=rule.id,
                supports=list(rule.conditions),
            )

            if added:
                iteration += 1
                applied.append(AppliedRule(rule=rule, iteration=iteration))
            else:
                # Если правило не добавило новый факт, исключаем его и продолжаем цикл.
                conflict_set.remove(rule)
                if not conflict_set:
                    break

        return applied

    def _collect_conflict_set(self, working_memory: WorkingMemory) -> List[Rule]:
        """Формирует конфликтное множество правил, условия которых выполнены."""
        conflicts: List[Rule] = []
        for rule in self._kb.rules:
            if working_memory.has_fact(rule.conclusion):
                continue
            if all(working_memory.has_fact(condition) for condition in rule.conditions):
                conflicts.append(rule)
        return conflicts

    def _resolve_conflict(
            self,
            conflicts: Sequence[Rule],
            strategy: ConflictStrategy,
            working_memory: WorkingMemory,
    ) -> Rule | None:
        """
        Выбирает правило из конфликтного множества согласно стратегии.

        Поддерживаются стратегии:
        - order: правила применяются в порядке объявления в БЗ;
        - specificity: выбирается правило с наибольшим числом условий;
        - recency: правило с наиболее «свежими» фактами в предпосылках.
        """
        if not conflicts:
            return None

        strategy = strategy.lower()
        if strategy == "order":
            return conflicts[0]

        if strategy == "specificity":
            return max(conflicts, key=lambda rule: len(rule.conditions))

        if strategy == "recency":
            def recency_score(rule: Rule) -> int:
                timestamps = [
                    working_memory.get_record(condition).timestamp
                    for condition in rule.conditions
                ]
                return max(timestamps) if timestamps else 0

            return max(conflicts, key=recency_score)

        raise ValueError(f"Неизвестная стратегия разрешения конфликтов: {strategy}")