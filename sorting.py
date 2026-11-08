"""Python 내장 정렬 API 없이 구현한 안정적인 병합 정렬."""
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def merge_sort(items: list[T], key: Callable[[T], tuple]) -> list[T]:
    """key 오름차순 안정 정렬. 시간 O(n log n), 추가 공간 O(n)."""
    if len(items) <= 1:
        return items[:]
    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    result: list[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
