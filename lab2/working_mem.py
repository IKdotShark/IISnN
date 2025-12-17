from __future__ import annotations

"""
Модуль рабочей памяти — хранит факты и метаданные об их происхождении.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class FactRecord:
    """Метаданные о факте в рабочей памяти."""

    fact: str
    source: str
    supports: List[str]
    timestamp: int


class WorkingMemory:
    """Рабочая память, доступная механизму вывода и компоненте объяснения."""

    def __init__(self) -> None:
        self._facts: Dict[str, FactRecord] = {}
        self._counter: int = 0

    def add_fact(self, fact: str, source: str, supports: Optional[Iterable[str]] = None) -> bool:
        """
        Добавляет новый факт.

        Возвращает True, если факт был добавлен, либо False, если он уже присутствовал.
        """
        if fact in self._facts:
            return False

        self._counter += 1
        record = FactRecord(
            fact=fact,
            source=source,
            supports=list(supports or []),
            timestamp=self._counter,
        )
        self._facts[fact] = record
        return True

    def has_fact(self, fact: str) -> bool:
        """Проверяет наличие факта."""
        return fact in self._facts

    def get_record(self, fact: str) -> FactRecord:
        """Возвращает метаданные факта."""
        return self._facts[fact]

    def facts(self) -> List[str]:
        """Возвращает список фактов в порядке появления."""
        return [record.fact for record in sorted(self._facts.values(), key=lambda item: item.timestamp)]

    def items(self) -> List[FactRecord]:
        """Возвращает записи (для диагностики/объяснений)."""
        return list(sorted(self._facts.values(), key=lambda item: item.timestamp))