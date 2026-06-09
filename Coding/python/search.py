"""Binary search ported from Search.java (original Java package code.ds).

Java overloaded the name `binarySearch`; Python has no overloading, so the
recursive variant is renamed to `binary_search_recursive`.
"""


def binary_search(arr, x):
    """Iterative binary search over a sorted list; returns index of x or -1.

    O(log n) time, O(1) space.
    """
    l, r = 0, len(arr) - 1
    while l <= r:
        m = l + (r - l) // 2
        if arr[m] == x:          # x found at mid
            return m
        if arr[m] < x:           # x is greater -> ignore the left half
            l = m + 1
        else:                    # x is smaller -> ignore the right half
            r = m - 1
    return -1                    # not present


def binary_search_recursive(arr, l, r, x):
    """Recursive binary search over arr[l..r]; returns index of x or -1."""
    if r >= l:
        mid = l + (r - l) // 2
        if arr[mid] == x:                # present at the middle
            return mid
        if arr[mid] > x:                 # only possible in the left subarray
            return binary_search_recursive(arr, l, mid - 1, x)
        return binary_search_recursive(arr, mid + 1, r, x)  # right subarray
    return -1                            # not present


if __name__ == "__main__":
    print("Search")
    data = [2, 3, 4, 10, 40]
    print("iterative  binary_search(40) ->", binary_search(data, 40))
    print("recursive  binary_search(10) ->",
          binary_search_recursive(data, 0, len(data) - 1, 10))
    print("missing    binary_search(7)  ->", binary_search(data, 7))
