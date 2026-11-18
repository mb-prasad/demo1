from typing import List, TypeVar

T = TypeVar("T")


def bubble_sort(items: List[T]) -> List[T]:
    """Return a new list with the items in ascending order using bubble sort.

    The input list is not modified. Items must be mutually comparable with "<".
    """
    result = list(items)
    n = len(result)
    for i in range(n - 1):
        swapped = False
        # After each pass the largest remaining item sits at the end, so skip it.
        for j in range(n - 1 - i):
            if result[j + 1] < result[j]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break
    return result
