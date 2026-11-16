from typing import List, TypeVar

T = TypeVar("T")


def bubble_sort(items: List[T]) -> List[T]:
    """Return a new list with the items sorted in ascending order using bubble sort.

    The input list is not modified. The sort is stable, and the function stops
    early once a full pass makes no swaps.
    """
    result = list(items)
    n = len(result)
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            if result[i] > result[i + 1]:
                result[i], result[i + 1] = result[i + 1], result[i]
                swapped = True
        if not swapped:
            break
    return result


if __name__ == "__main__":
    print(bubble_sort([5, 2, 9, 1, 5, 6]))
