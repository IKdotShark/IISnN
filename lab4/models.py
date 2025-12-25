"""
Модели коллективного принятия решений
Реализация различных методов голосования и анализа предпочтений
"""

from collections import defaultdict, Counter
from itertools import combinations
from typing import List, Dict, Tuple, Optional


def relative_majority(profile: List[List[str]], alternatives: List[str]) -> Tuple[str, Dict[str, int]]:
    """
    Метод относительного большинства.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования - список ранжирований для каждого участника
    alternatives : List[str]
        Список всех альтернатив

    Возвращает:
    -----------
    Tuple[str, Dict[str, int]]
        Победитель и словарь с количеством первых мест для каждой альтернативы
    """
    # Считаем первые места
    first_choices = [ranking[0] for ranking in profile]
    counts = Counter(first_choices)

    # Определяем победителя
    winner = max(counts, key=counts.get)

    return winner, dict(counts)


def pairwise_comparison(profile: List[List[str]], a: str, b: str) -> int:
    """
    Попарное сравнение двух альтернатив.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    a : str
        Первая альтернатива
    b : str
        Вторая альтернатива

    Возвращает:
    -----------
    int
        Разность голосов: сколько предпочитают 'a' над 'b' минус наоборот
    """
    score = 0

    for ranking in profile:
        if a in ranking and b in ranking:
            # Сравниваем позиции в рейтинге
            if ranking.index(a) < ranking.index(b):
                score += 1  # 'a' предпочтительнее 'b'
            else:
                score -= 1  # 'b' предпочтительнее 'a'

    return score


def condorcet_winner(profile: List[List[str]], alternatives: List[str]) -> Optional[str]:
    """
    Поиск явного победителя Кондорсе.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    alternatives : List[str]
        Список всех альтернатив

    Возвращает:
    -----------
    Optional[str]
        Победитель Кондорсе или None, если такого нет
    """
    for a in alternatives:
        is_winner = True

        # Проверяем, побеждает ли 'a' всех остальных
        for b in alternatives:
            if a == b:
                continue

            if pairwise_comparison(profile, a, b) <= 0:
                is_winner = False
                break

        if is_winner:
            return a

    return None


def copeland_score(profile: List[List[str]], alternatives: List[str]) -> Dict[str, int]:
    """
    Правило Копленда для определения победителя.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    alternatives : List[str]
        Список всех альтернатив

    Возвращает:
    -----------
    Dict[str, int]
        Словарь с очками Копленда для каждой альтернативы
    """
    scores = {a: 0 for a in alternatives}

    # Сравниваем все пары альтернатив
    for a, b in combinations(alternatives, 2):
        diff = pairwise_comparison(profile, a, b)

        if diff > 0:
            # 'a' побеждает 'b'
            scores[a] += 1
            scores[b] -= 1
        elif diff < 0:
            # 'b' побеждает 'a'
            scores[a] -= 1
            scores[b] += 1
        # При ничье очки не меняются

    return scores


def simpson_score(profile: List[List[str]], alternatives: List[str]) -> Dict[str, int]:
    """
    Правило Симпсона (правило минимальной поддержки).

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    alternatives : List[str]
        Список всех альтернатив

    Возвращает:
    -----------
    Dict[str, int]
        Словарь с минимальной поддержкой для каждой альтернативы
    """
    scores = {}

    for a in alternatives:
        min_wins = float('inf')

        # Находим минимальное количество побед над другими альтернативами
        for b in alternatives:
            if a == b:
                continue

            # Считаем, сколько раз 'a' предпочтительнее 'b'
            wins = sum(1 for ranking in profile
                       if ranking.index(a) < ranking.index(b))

            min_wins = min(min_wins, wins)

        scores[a] = min_wins

    return scores


def borda_count(profile: List[List[str]], alternatives: List[str]) -> Dict[str, int]:
    """
    Метод Борда для подсчета очков.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    alternatives : List[str]
        Список всех альтернатив

    Возвращает:
    -----------
    Dict[str, int]
        Словарь с очками Борда для каждой альтернативы
    """
    p = len(alternatives)
    scores = defaultdict(int)

    for ranking in profile:
        # Присваиваем очки в зависимости от позиции
        for i, alt in enumerate(ranking):
            # N-1 очков за первое место, 0 за последнее
            scores[alt] += (p - 1 - i)

    # Убеждаемся, что все альтернативы присутствуют в результатах
    for alt in alternatives:
        scores.setdefault(alt, 0)

    return dict(scores)


def linear_multi_criteria_score(profile: List[List[str]],
                                alternatives: List[str],
                                weights: List[float]) -> Dict[str, float]:
    """
    Линейная многокритериальная модель выбора.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    alternatives : List[str]
        Список всех альтернатив
    weights : List[float]
        Веса критериев (должны суммироваться в 1)

    Возвращает:
    -----------
    Dict[str, float]
        Словарь с интегральными оценками для каждой альтернативы
    """
    # Нормализуем веса
    total_weight = sum(weights)
    if total_weight == 0:
        weights = [1.0 / len(weights)] * len(weights)
    else:
        weights = [w / total_weight for w in weights]

    # Преобразуем ранжирования в числовые оценки
    p = len(alternatives)
    scores = defaultdict(float)

    for ranking in profile:
        for i, alt in enumerate(ranking):
            # Используем линейную шкалу с учетом весов
            scores[alt] += (p - i) * weights[i % len(weights)]

    # Нормализуем результаты
    max_score = max(scores.values()) if scores else 1
    return {alt: score / max_score for alt, score in scores.items()}


def fuzzy_multi_criteria_score(profile: List[List[str]],
                               alternatives: List[str],
                               membership_func: callable) -> Dict[str, float]:
    """
    Многокритериальная модель с нечеткими множествами.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    alternatives : List[str]
        Список всех альтернатив
    membership_func : callable
        Функция принадлежности для нечеткого множества

    Возвращает:
    -----------
    Dict[str, float]
        Словарь со степенями принадлежности для каждой альтернативы
    """
    p = len(alternatives)
    fuzzy_scores = defaultdict(float)

    # Вычисляем степень принадлежности для каждой альтернативы
    for ranking in profile:
        for i, alt in enumerate(ranking):
            # Нормализуем позицию (от 0 до 1)
            normalized_pos = i / (p - 1) if p > 1 else 0

            # Применяем функции принадлежности
            membership = membership_func(normalized_pos)
            fuzzy_scores[alt] += membership

    # Усредняем по количеству участников
    n_voters = len(profile)
    if n_voters > 0:
        fuzzy_scores = {alt: score / n_voters for alt, score in fuzzy_scores.items()}

    return dict(fuzzy_scores)


def trapezoidal_membership(x: float, a: float = 0, b: float = 0.3,
                           c: float = 0.7, d: float = 1) -> float:
    """
    Трапециевидная функция принадлежности.

    Параметры:
    -----------
    x : float
        Входное значение
    a, b, c, d : float
        Параметры трапеции

    Возвращает:
    -----------
    float
        Степень принадлежности
    """
    if x < a:
        return 0
    elif a <= x < b:
        return (x - a) / (b - a)
    elif b <= x <= c:
        return 1
    elif c < x <= d:
        return (d - x) / (d - c)
    else:
        return 0


def gaussian_membership(x: float, mean: float = 0.5, sigma: float = 0.2) -> float:
    """
    Гауссовская функция принадлежности.

    Параметры:
    -----------
    x : float
        Входное значение
    mean : float
        Центр распределения
    sigma : float
        Ширина распределения

    Возвращает:
    -----------
    float
        Степень принадлежности
    """
    return 2.718281828459045 ** (-((x - mean) ** 2) / (2 * sigma ** 2))


def analyze_profile_consistency(profile: List[List[str]],
                                alternatives: List[str]) -> Dict[str, float]:
    """
    Анализ согласованности профиля голосования.

    Параметры:
    -----------
    profile : List[List[str]]
        Профиль голосования
    alternatives : List[str]
        Список всех альтернатив

    Возвращает:
    -----------
    Dict[str, float]
        Метрики согласованности
    """
    n_voters = len(profile)
    n_alternatives = len(alternatives)

    # Вычисляем матрицу попарных сравнений
    matrix = {}
    for a in alternatives:
        matrix[a] = {}
        for b in alternatives:
            if a == b:
                matrix[a][b] = 0
            else:
                matrix[a][b] = pairwise_comparison(profile, a, b)

    # Проверяем наличие кондорсетовских циклов
    has_condorcet_winner = condorcet_winner(profile, alternatives) is not None

    # Вычисляем индекс согласованности
    consistency_score = 0
    if n_voters > 0 and n_alternatives > 1:
        max_possible = n_voters * (n_alternatives * (n_alternatives - 1)) / 2
        actual = sum(abs(matrix[a][b]) for a in alternatives for b in alternatives if a != b) / 2
        consistency_score = actual / max_possible if max_possible > 0 else 0

    return {
        'has_condorcet_winner': has_condorcet_winner,
        'consistency_score': consistency_score,
        'n_voters': n_voters,
        'n_alternatives': n_alternatives
    }