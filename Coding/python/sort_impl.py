"""Sorting algorithms ported from Sort.java (original Java package code.ds).

The original Java class held no instance state, so every method becomes a
module-level function (snake_case). Algorithms covered: merge sort, quick sort
and insertion sort.
"""


# ---------------------------------------------------------------------------
# Merge sort -- O(n log n) time, O(n) auxiliary space.
# ---------------------------------------------------------------------------
def merge_sort(data, first, n):
    """Sort the slice data[first : first + n] in place using merge sort."""
    if n > 1:
        n1 = n // 2        # size of the first half
        n2 = n - n1        # size of the second half
        merge_sort(data, first, n1)        # sort the left half
        merge_sort(data, first + n1, n2)   # sort the right half
        _merge(data, first, n1, n2)        # merge the two sorted halves


def _merge(data, first, n1, n2):
    """Merge two adjacent sorted runs: data[first:first+n1] and the next n2."""
    temp = [0] * (n1 + n2)   # temporary array
    copied = 0               # elements copied into temp
    copied1 = 0              # copied from the first half
    copied2 = 0              # copied from the second half

    # Merge while both halves still have elements.
    while copied1 < n1 and copied2 < n2:
        if data[first + copied1] < data[first + n1 + copied2]:
            temp[copied] = data[first + copied1]
            copied += 1
            copied1 += 1
        else:
            temp[copied] = data[first + n1 + copied2]
            copied += 1
            copied2 += 1

    # Copy whatever remains in either half.
    while copied1 < n1:
        temp[copied] = data[first + copied1]
        copied += 1
        copied1 += 1
    while copied2 < n2:
        temp[copied] = data[first + n1 + copied2]
        copied += 1
        copied2 += 1

    # Copy the merged result back into data.
    for i in range(n1 + n2):
        data[first + i] = temp[i]


# ---------------------------------------------------------------------------
# Quick sort -- average O(n log n).
# NOTE: this is a faithful port that keeps the reference's XOR swap, which
# zeroes an element whenever x == y (a latent bug in the original). It is left
# defined for completeness but is intentionally NOT exercised by the demo.
# ---------------------------------------------------------------------------
def quick_sort(array, start_idx, end_idx):
    idx = _partition(array, start_idx, end_idx)
    # Recurse on the left part of the partitioned array.
    if start_idx < idx - 1:
        quick_sort(array, start_idx, idx - 1)
    # Recurse on the right part of the partitioned array.
    if end_idx > idx:
        quick_sort(array, idx, end_idx)


def _partition(g, first, last):
    pivot = g[last]
    p_index = first
    for i in range(first, last):
        if g[i] < pivot:
            _swap(g, i, p_index)
            p_index += 1
    _swap(g, p_index, last)
    return p_index


def _swap(g, x, y):
    # XOR swap, faithful to the Java reference (corrupts the element when x == y).
    g[x] ^= g[y]
    g[y] ^= g[x]
    g[x] ^= g[y]


# ---------------------------------------------------------------------------
# Insertion sort -- O(n^2); an online algorithm (sorts the data seen so far).
# ---------------------------------------------------------------------------
def do_insertion_sort(values):
    for i in range(1, len(values)):
        for j in range(i, 0, -1):
            if values[j] < values[j - 1]:
                values[j], values[j - 1] = values[j - 1], values[j]
    return values


if __name__ == "__main__":
    a = [3, 23, 1, 5, 2, 56, 4]
    merge_sort(a, 0, len(a))
    print("merge_sort:    ", a)

    b = [3, 23, 1, 5, 2, 56, 4]
    print("insertion_sort:", do_insertion_sort(b))
