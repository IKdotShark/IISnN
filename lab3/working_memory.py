#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МОДУЛЬ 3: РАБОЧАЯ ПАМЯТЬ (working_memory.py)
Рабочая память экспертной системы
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from frame import Frame


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