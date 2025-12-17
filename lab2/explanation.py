from __future__ import annotations

"""
Компонента объяснения для построения цепочек вывода.
"""

from typing import List

from working_mem import WorkingMemory


class ExplanationComponent:
    """Формирует объяснение вывода для указанного факта."""

    def __init__(self, working_memory: WorkingMemory) -> None:
        self._wm = working_memory

    def explain(self, fact: str) -> str:
        """Возвращает текстовое объяснение факта."""
        if not self._wm.has_fact(fact):
            raise ValueError(f"Факт '{fact}' отсутствует в рабочей памяти.")

        lines: List[str] = []
        self._build_explanation(fact, lines, depth=0)
        return "\n".join(lines)

    def _build_explanation(self, fact: str, lines: List[str], depth: int) -> None:
        record = self._wm.get_record(fact)
        indent = " " * depth

        if record.source == "user":
            lines.append(f"{indent}- Факт '{fact}' введён пользователем.")
            return

        lines.append(f"{indent}- Факт '{fact}' получен по правилу {record.source}.")
        if not record.supports:
            return

        lines.append(f"{indent}  Обоснование:")
        for support in record.supports:
            self._build_explanation(support, lines, depth + 2)