"""Idiomatic Python 3 port of java/Array.java (original package ``code.ds``).

A large collection of array / DSA interview algorithms. Java's single ``Array``
class is translated as follows:

  * static methods                -> module-level functions
  * stateless instance methods    -> module-level functions
  * stateful instance/static groups (median stream, 2-sum cache, max-subarray
    stream) -> small classes (MedianStream, Faster2Sum, MaxSubArrayStream)
  * inner data-holder classes (Triplet, Ad, Task, KSortedList, Pair, MinMaxPair)
    -> module-level classes

Java method overloads are merged or renamed (e.g. ``partition`` /
``partition_chars``, ``are_consecutive`` / ``are_consecutive2``).

NOTE: this module is intentionally named ``array.py``; we never ``import array``
(the stdlib module) to avoid a self-import collision -- plain lists are used.

Several reference algorithms contain intentional interview-style bugs (e.g.
``randomize`` always picks index 0, ``rearrange`` swaps by value, ``find_first_repeating``
reads out of bounds). These are ported faithfully and noted in comments; they
are not exercised by the ``__main__`` demo.
"""
from __future__ import annotations

import functools
import heapq
import math
import random
from collections import deque

INT_MAX = 2 ** 31 - 1
INT_MIN = -(2 ** 31)


def java_round(x):
    """Java ``Math.round``: floor(x + 0.5)."""
    return math.floor(x + 0.5)


# ---------------------------------------------------------------------------
# Small data-holder / helper classes (Java inner classes)
# ---------------------------------------------------------------------------
class Triplet:
    """Heap entry for k-way merge (Java inner class with natural ordering)."""

    def __init__(self, pos=0, val=0, index=0):
        self.pos = pos
        self.val = val
        self.index = index

    def __lt__(self, other):  # PriorityQueue<Triplet> natural ordering by value
        return self.val < other.val


class Pair:
    """Minimal javafx.util.Pair replacement (immutable key/value)."""

    def __init__(self, key, value):
        self._key = key
        self._value = value

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value


class Ad:
    """Advertisement with start, finish, revenue (weighted job scheduling)."""

    def __init__(self, start=0, finish=0, revenue=0):
        self.start = start
        self.finish = finish
        self.revenue = revenue


class Task:
    def __init__(self, id_, frequency):
        self.id = id_
        self.frequency = frequency


class KSortedList:
    def __init__(self, position=0, value=0, k_index=0):
        self.position = position
        self.value = value
        self.k_index = k_index


class MinMaxPair:
    def __init__(self, mn=0, mx=0):
        self.min = mn
        self.max = mx


# ---------------------------------------------------------------------------
# Merge / k-smallest / median
# ---------------------------------------------------------------------------
def merge_array(a, b):
    # Merge two sorted arrays into a sorted array. Time = O(N+M)
    answer = [0] * (len(a) + len(b))
    i = j = k = 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            answer[k] = a[i]
            k += 1
            i += 1
        else:
            answer[k] = b[j]
            k += 1
            j += 1
    while i < len(a):
        answer[k] = a[i]
        k += 1
        i += 1
    while j < len(b):
        answer[k] = b[j]
        k += 1
        j += 1
    return answer


def merge_using_heap(chunks):
    # Merge k sorted lists/arrays using a min heap. O(nk*Logk), space O(k)
    result = []
    min_heap = []
    for i in range(len(chunks)):
        p = Triplet(pos=i, val=chunks[i][0], index=0)
        heapq.heappush(min_heap, p)
    while min_heap:
        p = heapq.heappop(min_heap)
        result.append(p.val)
        if p.index < len(chunks[p.pos]):
            # NOTE: faithful to reference (can read past end -> IndexError if hit)
            p.val = chunks[p.pos][p.index + 1]
            p.index += 1
            heapq.heappush(min_heap, p)
    return result


def merge(a, b, last_a, last_b):
    # Merge sorted b into sorted a (a has trailing buffer). In place.
    index_merged = last_b + last_a - 1
    index_a = last_a - 1
    index_b = last_b - 1
    while index_b >= 0:
        if index_a >= 0 and a[index_a] > b[index_b]:
            a[index_merged] = a[index_a]
            index_a -= 1
        else:
            a[index_merged] = b[index_b]
            index_b -= 1
        index_merged -= 1


def find_k_smallest_element(A, start_a, end_a, B, start_b, end_b, k):
    # k-th smallest element in union of two sorted arrays. Time = O(log(m+n))
    n = end_a - start_a
    m = end_b - start_b
    if n <= 0:
        return B[start_b + k - 1]
    if m <= 0:
        return A[start_a + k - 1]
    if k == 1:
        return A[start_a] if A[start_a] < B[start_b] else B[start_b]
    mid_a = (start_a + end_a) // 2
    mid_b = (start_b + end_b) // 2
    if A[mid_a] <= B[mid_b]:
        if n // 2 + m // 2 + 1 >= k:
            return find_k_smallest_element(A, start_a, end_a, B, start_b, mid_b, k)
        return find_k_smallest_element(A, mid_a + 1, end_a, B, start_b, end_b, k - n // 2 - 1)
    if n // 2 + m // 2 + 1 >= k:
        return find_k_smallest_element(A, start_a, mid_a, B, start_b, end_b, k)
    return find_k_smallest_element(A, start_a, end_a, B, mid_b + 1, end_b, k - m // 2 - 1)


def find_median_sorted_arrays(A, B):
    # Median of two sorted arrays.
    length_a = len(A)
    length_b = len(B)
    if (length_a + length_b) % 2 == 0:
        r1 = float(find_k_smallest_element(A, 0, length_a, B, 0, length_b, (length_a + length_b) // 2))
        r2 = float(find_k_smallest_element(A, 0, length_a, B, 0, length_b, (length_a + length_b) // 2 + 1))
        return (r1 + r2) / 2
    return find_k_smallest_element(A, 0, length_a, B, 0, length_b, (length_a + length_b + 1) // 2)


class MedianStream:
    """Median of an unsorted integer stream. O(1) find, O(log N) insert."""

    def __init__(self):
        self.min_heap = []          # min-heap
        self.max_heap = []          # max-heap stored as negated values
        self.num_of_elements = 0

    def add_number_to_stream(self, num):
        heapq.heappush(self.max_heap, -num)
        if self.num_of_elements % 2 == 0:
            if not self.min_heap:
                self.num_of_elements += 1
                return
            elif -self.max_heap[0] > self.min_heap[0]:
                max_heap_root = -heapq.heappop(self.max_heap)
                min_heap_root = heapq.heappop(self.min_heap)
                heapq.heappush(self.max_heap, -min_heap_root)
                heapq.heappush(self.min_heap, max_heap_root)
        else:
            heapq.heappush(self.min_heap, -heapq.heappop(self.max_heap))
        self.num_of_elements += 1

    def get_median(self):
        if self.num_of_elements % 2 != 0:
            return float(-self.max_heap[0])
        return (-self.max_heap[0] + self.min_heap[0]) / 2.0


def merge_unsorted_array_kth_smallest(A1, A2, K):
    # kth smallest in two unsorted arrays. Avg O(n), worst O(n^2).
    c = [0] * (len(A1) + len(A2))
    length = 0
    for i in range(len(A1)):
        c[i] = A1[i]
        length += 1
    for j in range(len(A2)):
        c[length + j] = A2[j]
    return quickselect(c, 0, len(c) - 1, K - 1)


def quickselect(G, first, last, k):
    if first <= last:
        pivot = random_partition(G, first, last)
        if pivot == k:
            return G[k]
        if pivot > k:
            return quickselect(G, first, pivot - 1, k)
        return quickselect(G, pivot + 1, last, k)
    return 0


def random_partition(arr, l, r):
    pivot = int(java_round(l + random.random() * (r - l)))
    swap(arr, pivot, r)
    return partition(arr, l, r)


def partition(G, first, last):
    pivot = G[last]
    p_index = first
    for i in range(first, last):
        if G[i] < pivot:
            swap(G, i, p_index)
            p_index += 1
    swap(G, p_index, last)
    return p_index


def swap(G, x, y):
    G[x], G[y] = G[y], G[x]


def second_largest(a):
    # Second largest number in array.
    largest = a[0]
    second = INT_MIN
    for i in range(1, len(a)):
        number = a[i]
        if number > largest:
            second = largest
            largest = number
        elif number > second and number != largest:
            second = number
    return -1 if second == INT_MIN else second


def get_top_elements(arr, k):
    # k maximum integers. Time O(k + (n-k)Logk).
    min_heap = []
    for cur in arr:
        if len(min_heap) < k:
            heapq.heappush(min_heap, cur)
        elif cur > min_heap[0]:
            heapq.heappop(min_heap)
            heapq.heappush(min_heap, cur)
    result = []
    while min_heap:
        result.append(heapq.heappop(min_heap))
    return result


def count_zeros(arr, n):
    # Count trailing zeros in an array of 1s then 0s.
    f = first_zero(arr, 0, n - 1)
    if f == -1:
        return 0
    return n - f


def first_zero(arr, low, high):
    # Index of first 0 in sorted-by-ones array. Time O(Logn)
    if high >= low:
        mid = low + (high - low) // 2
        if (mid == 0 or arr[mid - 1] == 1) and arr[mid] == 0:
            return mid
        if arr[mid] == 1:
            return first_zero(arr, mid + 1, high)
        return first_zero(arr, low, mid - 1)
    return -1


def get_number_of_subsets(numbers, sum_target):
    # Number of subsets that sum to a value. O(Sum * N), O(Sum) memory.
    dp = [0] * (sum_target + 1)
    dp[0] = 1
    current_sum = 0
    for i in range(len(numbers)):
        current_sum += numbers[i]
        j = min(sum_target, current_sum)
        while j >= numbers[i]:
            dp[j] += dp[j - numbers[i]]
            j -= 1
    return dp[sum_target]


def combination_sum4(nums, target):
    # Number of combinations adding up to target (order matters).
    comb = [0] * (target + 1)
    comb[0] = 1
    for i in range(1, len(comb)):
        for j in range(len(nums)):
            if i - nums[j] >= 0:
                comb[i] += comb[i - nums[j]]
    return comb[target]


def two_sum_sorted_array(A, target):
    # Sorted array, two numbers summing to target (numbers reusable).
    left, right = 0, len(A) - 1
    while left < right:
        s = A[left] + A[right]
        if A[left] == target // 2 or A[right] == target // 2:
            return [target // 2, target // 2]
        if s == target:
            return [A[left], A[right]]
        elif s > target:
            right -= 1
        else:
            left += 1
    return None


def k_sum(num, k, target, start_index):
    # k-Sum problem. Time = O(N^k)
    result = []
    if k == 0:
        if target == 0:
            result.append([])
        return result
    for i in range(start_index, len(num) - k + 1):
        if i > start_index and num[i] == num[i - 1]:
            continue
        for item in k_sum(num, k - 1, target - num[i], i + 1):
            item.insert(0, i)
            result.append(item)
    return result


def two_sum(numbers, target):
    # Two numbers adding to target (returns 1-based indices). Time/space O(n).
    m = {}
    result = []
    for i in range(len(numbers)):
        if numbers[i] in m:
            index = m[numbers[i]]
            result.append(index + 1)
            result.append(i + 1)
            break
        m[target - numbers[i]] = i
    return result


class Faster2Sum:
    """Stores all pairwise sums so 2-sum lookups become O(1)."""

    def __init__(self):
        self._sums = set()
        self._nums = []

    def store(self, value):
        if self._nums:
            for num in self._nums:
                self._sums.add(value + num)
        self._nums.append(value)

    def faster_2_sum(self, val):
        return val in self._sums


def count_pairs_with_diff_k(arr, n, k):
    # Distinct pairs with difference k. Time O(nlogn), space O(1)
    count = 0
    arr.sort()
    l = r = 0
    while r < n:
        if arr[r] - arr[l] == k:
            count += 1
            l += 1
            r += 1
        elif arr[r] - arr[l] > k:
            l += 1
        else:
            r += 1
    return count


def two_sum_with_duplicates(num, target):
    # All unique ascending pairs adding to target (input may have duplicates).
    res = []
    n = len(num)
    if n < 2:
        return res
    m = {}
    for i in range(n):
        k1, k2 = num[i], target - num[i]
        if k2 in m and m[k2] > 0:
            pair = [k1, k2] if k1 < k2 else [k2, k1]
            if pair not in res:
                res.append(pair)
            m[k2] = m[k2] - 1
        else:
            if k1 not in m:
                m[k1] = 1
            else:
                m[k1] = m[k1] + 1
    return res


def find_triplets(arr):
    # 3Sum: print unique triplets that sum to zero. Time = O(n^2)
    arr.sort()
    n = len(arr)
    for i in range(n):
        j = i + 1
        k = n - 1
        if i > 0 and arr[i] == arr[i - 1]:
            continue
        while j < k:
            sum_two = arr[i] + arr[j]
            if sum_two + arr[k] < 0:
                j += 1
            elif sum_two + arr[k] > 0:
                k -= 1
            else:
                print(str(arr[i]) + " " + str(arr[j]) + " " + str(arr[k]))
                while j < k and arr[j] == arr[j + 1]:
                    j += 1
                while j < k and arr[k] == arr[k - 1]:
                    k -= 1
                j += 1
                k -= 1


def find_triplets_duplicates(arr):
    seen = set()
    for i in range(len(arr)):
        out = two_sum_with_duplicates_index(arr, -arr[i], i)
        for lst in out:
            lst.append(i)
            lst.sort()
            key = tuple(lst)
            if key not in seen:
                print(str(lst[0]) + " " + str(lst[1]) + " " + str(lst[2]))
                seen.add(key)


def two_sum_with_duplicates_index(num, target, exclude):
    res = []
    n = len(num)
    if n < 2:
        return res
    m = {}
    for i in range(n):
        if i == exclude:
            continue
        k1, k2 = num[i], target - num[i]
        if k2 in m:
            res.append([i, m[k2]])
        else:
            if k1 not in m:
                m[k1] = i
    return res


def three_sum_closest(num, target):
    # Sum of three closest to target. Time = O(n^2)
    num.sort()
    mn = INT_MAX
    result = 0
    for i in range(len(num)):
        j = i + 1
        k = len(num) - 1
        while j < k:
            s = num[i] + num[j] + num[k]
            diff = abs(s - target)
            if diff == 0:
                return s
            if diff < mn:
                mn = diff
                result = s
            if s <= target:
                j += 1
            else:
                k -= 1
    return result


def three_sum_multiple(arr):
    # Any 3 integers summing to 0 (numbers reusable).
    arr.sort()
    n = len(arr)
    for i in range(n):
        if arr[i] == 0:
            return [0, 0, 0]
        j = i
        k = n - 1
        while j < k:
            s = arr[i] + arr[j] + arr[k]
            if s < 0:
                j += 1
            elif s > 0:
                k -= 1
            else:
                return [arr[i], arr[j], arr[k]]
    return None


def three_sum_smaller(nums, target):
    # Count index triplets with nums[i]+nums[j]+nums[k] < target. O(n^2)
    nums.sort()
    s = 0
    for i in range(len(nums) - 2):
        s += two_sum_smaller(nums, i + 1, target - nums[i])
    return s


def two_sum_smaller(nums, start_index, target):
    s = 0
    left = start_index
    right = len(nums) - 1
    while left < right:
        if nums[left] + nums[right] < target:
            s += right - left
            left += 1
        else:
            right -= 1
    return s


def sub_array_sum_positive(A, target):
    # Subarray summing to target (positive numbers only). Time O(2n)
    i = j = s = 0
    while i < len(A):
        while j < len(A) and s < target:
            s += A[j]
            j += 1
        if s == target:
            print("Start index: " + str(i) + " End index: " + str(j - 1), end="")
            return
        s -= A[i]
        i += 1
    print("No SubArray Found.", end="")


def is_valid(a, total):
    count = 0
    temp = 0
    for i in range(len(a)):
        temp += a[i]
        while temp > total:
            temp -= a[count]
            count += 1
        if temp == total:
            return True
    return False


def sub_array_sum(arr, target):
    # Subarray summing to target (handles negatives) via prefix-sum map.
    m = {}
    curr_sum = 0
    for i in range(len(arr)):
        curr_sum += arr[i]
        if curr_sum == target:
            print("Sum found at " + str(0) + "and " + str(i), end="")
            return
        if (curr_sum - target) in m:
            # faithful to reference's left-to-right string concatenation quirk
            print("Sum found at " + str(m[curr_sum - target]) + "1" + "and " + str(i), end="")
            return
        m[curr_sum] = i


def all_sub_array_sum(arr, k):
    # Print all subarrays (start,end) summing to k (positive/negative).
    m = {}
    pre_sum = 0
    m[0] = [-1]
    for i in range(len(arr)):
        pre_sum += arr[i]
        if (pre_sum - k) in m:
            start_indices = m[pre_sum - k]
            for start in start_indices:
                print("Start: " + str(start + 1) + "\tEnd: " + str(i))
        new_start = []
        if pre_sum in m:
            new_start = m[pre_sum]
        new_start.append(i)
        m[pre_sum] = new_start


def max_sub_array_sum_len(arr, k):
    # Max length subarray summing to k.
    m = {}
    mx = 0
    curr_sum = 0
    for i in range(len(arr)):
        curr_sum += arr[i]
        if curr_sum == k:
            mx = max(mx, i + 1)
        if (curr_sum - k) in m:
            mx = max(mx, i - m[curr_sum - k])
        else:
            m[curr_sum] = i
    return mx


def min_sub_array_sum(arr, k):
    # Min length subarray summing to k (with duplicates).
    m = {}
    curr_sum = 0
    min_len = INT_MAX
    m[0] = [-1]
    for i in range(len(arr)):
        curr_sum += arr[i]
        if (curr_sum - k) in m:
            for start in m[curr_sum - k]:
                min_len = min(min_len, i - start)
        temp = []
        if curr_sum in m:
            temp = m[curr_sum]
        temp.append(i)
        m[curr_sum] = temp
    return 0 if min_len == INT_MAX else min_len


def max_sub_array_zero(arr):
    # Largest subarray with sum 0.
    h_m = {}
    s = 0
    max_len = 0
    for i in range(len(arr)):
        s += arr[i]
        if arr[i] == 0 and max_len == 0:
            max_len = 1
        if s == 0:
            max_len = i + 1
        prev_i = h_m.get(s)
        if prev_i is not None:
            max_len = max(max_len, i - prev_i)
        else:
            h_m[s] = i
    return max_len


def max_sub_array_sum(a):
    # Largest sum contiguous subarray (Kadane).
    max_so_far = a[0]
    curr_max = a[0]
    for i in range(1, len(a)):
        curr_max = max(a[i], curr_max + a[i])
        max_so_far = max(max_so_far, curr_max)
    return max_so_far


def find_max_sum_index(arr):
    # Largest sum contiguous subarray with [start, end, sum].
    result = [0, 0, 0]
    max_so_far = INT_MIN
    start_index = 0
    curr_max = 0
    for i in range(len(arr)):
        curr_max += arr[i]
        if curr_max > max_so_far:
            max_so_far = curr_max
            result[0] = start_index
            result[1] = i
            result[2] = max_so_far
        if curr_max < 0:
            curr_max = 0
            start_index = i + 1
    return result


class MaxSubArrayStream:
    """Max subarray sum maintained over a stream of inputs."""

    def __init__(self):
        self._stream = []
        self._out = [0, 0, 0]
        self.max_so_far = INT_MIN
        self.curr_max = 0
        self.start_index = 0

    def max_sub_array_sum_of_stream_num(self, num):
        self._stream.append(num)
        if self.curr_max + num > self.max_so_far:
            self.curr_max = 0
            for i in range(self.start_index, len(self._stream)):
                self.curr_max += self._stream[i]
                if self.curr_max > self.max_so_far:
                    self.max_so_far = self.curr_max
                    self._out[0] = self.start_index
                    self._out[1] = i
                    self._out[2] = self.max_so_far
                if self.curr_max < 0:
                    self.curr_max = 0
                    self.start_index = i + 1

    def get_max_sub_array_sum(self):
        return self._out


def max_k_sub_array(nums, k):
    # k non-overlapping subarrays with the largest sum.
    if len(nums) < k:
        return 0
    length = len(nums)
    d = [0] * (length + 1)
    for j in range(1, k + 1):
        for i in range(length, j - 1, -1):
            d[i] = INT_MIN
            end_max = 0
            best = INT_MIN
            for p in range(i - 1, j - 2, -1):
                end_max = max(nums[p], end_max + nums[p])
                best = max(end_max, best)
                if d[i] < d[p] + best:
                    d[i] = d[p] + best
    return d[length]


def max_sub_array_with_k(a, k):
    # Largest sum subarray containing at least k numbers.
    maxendhere = 0
    seen = set()
    i = 0
    for i in range(k):
        maxendhere += a[i]
        seen.add(a[i])
    maxsofar = maxendhere
    sumoflastk = maxendhere
    for i in range(k, len(a)):
        if a[i] in seen:
            maxendhere += a[i]
        sumoflastk += a[i] - a[i - k]
        if maxendhere < sumoflastk:
            maxendhere = sumoflastk
        if maxsofar < maxendhere:
            maxsofar = maxendhere
        seen.add(a[i])
    return maxsofar


def max_sum(arr, n, k):
    # Maximum sum in a subarray (window) of size k.
    if n < k:
        print("Invalid")
        return -1
    res = 0
    for i in range(k):
        res += arr[i]
    curr_sum = res
    for i in range(k, n):
        curr_sum += arr[i] - arr[i - k]
        res = max(res, curr_sum)
    return res


def max_sum1(arr, n, k):
    # Max window sum of size k; marks the chosen window with -1. Returns sum or None.
    if n < k:
        print("Invalid")
        return None
    res = 0
    output = [0, 0]
    for i in range(k):
        res += arr[i]
    output[0] = 0
    output[1] = k - 1
    curr_sum = res
    for i in range(k, n):
        curr_sum += arr[i] - arr[i - k]
        if curr_sum > res:
            res = curr_sum
            output[0] = i - k + 1
            output[1] = i
    for i in range(output[0], output[1] + 1):
        arr[i] = -1
    return res


def max_sum3_non_overlapping(input_, k):
    # Maximum sum of 3 non-overlapping subarrays of size k.
    s = 0
    for _ in range(3):
        s += max_sum1(input_, len(input_), k)
    return s


def smallest_sub_with_sum(arr, n, x):
    # Smallest subarray with sum greater than x. Returns n+1 if none.
    curr_sum = 0
    min_len = n + 1
    start = 0
    end = 0
    while end < n:
        while curr_sum <= x and end < n:
            curr_sum += arr[end]
            end += 1
        while curr_sum > x and start < n:
            if end - start < min_len:
                min_len = end - start
            curr_sum -= arr[start]
            start += 1
    return min_len


def find_len(a):
    # Length of longest increasing subarray.
    mn = a[0]
    max_len = 1
    count = 1
    for i in range(1, len(a)):
        if a[i] > mn:
            count += 1
        else:
            max_len = max(max_len, count)
            count = 1
        mn = a[i]
    max_len = max(max_len, count)
    return max_len


def ceil_index(A, l, r, key):
    while r - l > 1:
        m = l + (r - l) // 2
        if A[m] >= key:
            r = m
        else:
            l = m
    return r


def longest_increasing_subsequence_length(A, size):
    # Longest increasing subsequence. Time O(NlogN)
    temp = [0] * size
    temp[0] = A[0]
    length = 1
    for i in range(1, size):
        if A[i] < temp[0]:
            temp[0] = A[i]
        elif A[i] > temp[length - 1]:
            temp[length] = A[i]
            length += 1
        else:
            temp[ceil_index(temp, -1, length - 1, A[i])] = A[i]
    return length


def max_len_bitonic_sub_array(A):
    # Length of longest bitonic subarray.
    n = len(A)
    if n == 0:
        return 0
    max_len = 0
    i = 0
    while i + 1 < n:
        length = 1
        while i + 1 < n and A[i] < A[i + 1]:
            i += 1
            length += 1
        while i + 1 < n and A[i] > A[i + 1]:
            i += 1
            length += 1
        if length > max_len:
            max_len = length
    return max_len


def max_sum_is(arr, n):
    # Maximum Sum Increasing Subsequence.
    max_sum_val = 0
    msis = [arr[i] for i in range(n)]
    for i in range(1, n):
        for j in range(i):
            if arr[i] > arr[j]:
                msis[i] = max(msis[j] + arr[i], msis[i])
                max_sum_val = max(max_sum_val, msis[i])
    return max_sum_val


def max_subarray_product(arr):
    # Maximum product subarray (positive & negative).
    max_ending_here = 1
    min_ending_here = 1
    max_so_far = 1
    for i in range(len(arr)):
        if arr[i] > 0:
            max_ending_here = max_ending_here * arr[i]
            min_ending_here = min(min_ending_here * arr[i], 1)
        elif arr[i] == 0:
            max_ending_here = 1
            min_ending_here = 1
        else:
            temp = max_ending_here
            max_ending_here = max(min_ending_here * arr[i], 1)
            min_ending_here = temp * arr[i]
        if max_so_far < max_ending_here:
            max_so_far = max_ending_here
    return max_so_far


def max_repeating(arr, n, k):
    # Maximum repeating element (values in 0..k-1) in O(1) extra space.
    for i in range(n):
        arr[arr[i] % k] += k
    mx = arr[0]
    result = 0
    for i in range(1, n):
        if arr[i] > mx:
            mx = arr[i]
            result = i
    return result


def most_frequent(a):
    # Most frequent number and its count, O(1) space.
    a.sort()
    count = 1
    max_count = 1
    num = a[0]
    max_num = a[0]
    for i in range(1, len(a)):
        if num == a[i]:
            count += 1
            if count > max_count:
                max_count = count
                max_num = a[i]
        else:
            count = 1
            num = a[i]
    return str(max_num) + ": " + str(max_count)


def more_than_half_elem(a):
    # Majority element (> n/2 times) via Moore's voting; -1 if none.
    cand = find_candidate(a)
    if is_majority(a, cand):
        return cand
    return -1


def find_candidate(a):
    maj_index = 0
    count = 1
    for i in range(1, len(a)):
        if a[maj_index] == a[i]:
            count += 1
        else:
            count -= 1
        if count == 0:
            maj_index = i
            count = 1
    return a[maj_index]


def is_majority(a, cand):
    count = 0
    for i in range(len(a)):
        if a[i] == cand:
            count += 1
    return count > len(a) // 2


def left_rotate(arr, k):
    n = len(arr)
    reverse_array(arr, 0, k - 1)
    reverse_array(arr, k, n - 1)
    reverse_array(arr, 0, n - 1)


def right_rotate(arr, k):
    n = len(arr)
    reverse_array(arr, 0, n - k - 1)
    reverse_array(arr, n - k, n - 1)
    reverse_array(arr, 0, n - 1)


def reverse_array(arr, start, end):
    # Reverse arr[start..end] using XOR swap (faithful to reference).
    while start < end:
        arr[start] ^= arr[end]
        arr[end] ^= arr[start]
        arr[start] ^= arr[end]
        start += 1
        end -= 1


def rotated_binary_search(nums, N, key):
    # Search in rotated sorted array (no duplicates).
    left = 0
    right = N - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == key:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= key < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if key > nums[mid] and key <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def rotated_array_with_duplicates(nums, target):
    # Search in rotated sorted array allowing duplicates.
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) >> 1
        if nums[mid] == target:
            return True
        if nums[left] == nums[mid] and nums[right] == nums[mid]:
            left += 1
            right -= 1
        elif nums[left] <= nums[mid]:
            if nums[left] <= target and nums[mid] > target:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target and nums[right] >= target:
                left = mid + 1
            else:
                right = mid - 1
    return False


def search_rotated_unknown_times(a, left, right, x):
    # Search in rotated sorted array with duplicates, unknown rotations. Worst O(N)
    mid = (left + right) // 2
    if x == a[mid]:
        return mid
    if right < left:
        return -1
    if a[left] < a[mid]:
        if a[left] <= x <= a[mid]:
            return search_rotated_unknown_times(a, left, mid - 1, x)
        return search_rotated_unknown_times(a, mid + 1, right, x)
    elif a[mid] < a[left]:
        if a[mid] <= x <= a[right]:
            return search_rotated_unknown_times(a, mid + 1, right, x)
        return search_rotated_unknown_times(a, left, mid - 1, x)
    elif a[left] == a[mid]:
        if a[mid] != a[right]:
            return search_rotated_unknown_times(a, mid + 1, right, x)
        result = search_rotated_unknown_times(a, left, mid - 1, x)
        if result == -1:
            return search_rotated_unknown_times(a, mid + 1, right, x)
        return result
    return -1


def find_min(arr, low, high):
    # Minimum in sorted+rotated array (distinct). Time O(logn)
    if high == low:
        return arr[low]
    mid = low + (high - low) // 2
    if mid < high and arr[mid + 1] < arr[mid]:
        return arr[mid + 1]
    if mid > low and arr[mid] < arr[mid - 1]:
        return arr[mid]
    if arr[high] > arr[mid]:
        return find_min(arr, low, mid - 1)
    return find_min(arr, mid + 1, high)


def find_min_duplicate(arr, low, high):
    # Minimum in sorted+rotated array (duplicates). O(n) worst case.
    if high < low:
        return arr[0]
    if high == low:
        return arr[low]
    mid = low + (high - low) // 2
    if mid < high and arr[mid + 1] < arr[mid]:
        return arr[mid + 1]
    if arr[low] == arr[mid] and arr[high] == arr[mid]:
        return min(find_min_duplicate(arr, low, mid - 1), find_min_duplicate(arr, mid + 1, high))
    if mid > low and arr[mid] < arr[mid - 1]:
        return arr[mid]
    if arr[high] > arr[mid]:
        return find_min_duplicate(arr, low, mid - 1)
    return find_min_duplicate(arr, mid + 1, high)


def find_min_of_abc(a, b, c):
    # Minimize |a-b|+|b-c|+|c-a| picking one element from each array.
    mn = INT_MAX
    i = j = k = 0
    index1 = index2 = index3 = 0
    while i < len(a) and j < len(b) and k < len(c):
        n = abs(a[i] - b[j]) + abs(b[j] - c[k]) + abs(c[k] - a[i])
        if n < mn:
            mn = n
            index1, index2, index3 = i, j, k
        if a[i] < b[j] and a[i] < c[k]:
            i += 1
        elif b[j] < a[i] and b[j] < c[k]:
            j += 1
        else:
            k += 1
    print(str(a[index1]) + " " + str(b[index2]) + " " + str(c[index3]), end="")


def find_range(a, num):
    # (startIndex, endIndex) of num in sorted array with duplicates. O(logn)
    i = first(a, 0, len(a) - 1, num, len(a))
    if i == -1:
        return None
    j = last(a, i, len(a) - 1, num, len(a))
    return [i, j]


def first(arr, low, high, x, n):
    if high >= low:
        mid = (low + high) // 2
        if (mid == 0 or x > arr[mid - 1]) and arr[mid] == x:
            return mid
        elif x > arr[mid]:
            return first(arr, mid + 1, high, x, n)
        return first(arr, low, mid - 1, x, n)
    return -1


def last(arr, low, high, x, n):
    if high >= low:
        mid = low + (high - low) // 2
        if (mid == n - 1 or x < arr[mid + 1]) and arr[mid] == x:
            return mid
        elif x < arr[mid]:
            return last(arr, low, mid - 1, x, n)
        return last(arr, mid + 1, high, x, n)
    return -1


def find_numbers_in_range(a, min_, max_):
    # Count of elements in [min_, max_]. Time O(N)
    left = 0
    right = len(a) - 1
    if min_ > a[right] or max_ < a[left]:
        return 0
    while left < right:
        if a[left] < min_:
            left += 1
        if a[right] > max_:
            right -= 1
        if (a[left] == min_ or a[left] > min_) and (a[right] == max_ or a[right] < max_):
            break
    return right - left + 1


def find_numbers_in_range1(a, min_, max_):
    # Count of elements in [min_, max_]. Time O(2logN)
    if min_ > a[len(a) - 1] or max_ < a[0]:
        return 0
    index_left = binary_search_for_left_range(a, 0, len(a) - 1, min_)
    index_right = binary_search_for_right_range(a, index_left, len(a) - 1, max_)
    if index_left == -1 or index_right == -1 or index_left > index_right:
        return 0
    return index_right - index_left + 1


def binary_search_for_left_range(a, start, end, left_range):
    low = start
    high = end
    while low <= high:
        mid = low + (high - low) // 2
        if a[mid] >= left_range:
            high = mid - 1
        else:
            low = mid + 1
    return high + 1


def binary_search_for_right_range(a, start, end, right_range):
    low = start
    high = end
    while low <= high:
        mid = low + (high - low) // 2
        if a[mid] > right_range:
            high = mid - 1
        else:
            low = mid + 1
    return low - 1


def find_duplicate(arr):
    # Find duplicates (values 0..n-1) in O(n) time, O(1) space. Modifies arr.
    for i in range(len(arr)):
        if arr[i] == INT_MIN:
            if arr[0] > 0:
                arr[0] = -arr[0]
            else:
                print("0")
        elif arr[abs(arr[i])] == 0:
            arr[abs(arr[i])] = INT_MIN
        elif arr[abs(arr[i])] > 0:
            arr[abs(arr[i])] = -arr[abs(arr[i])]
        else:
            print(abs(arr[i]))


def find_duplicate1(a):
    # Single duplicated number, O(1) space O(n) time (Floyd's cycle detection).
    if len(a) == 0 or len(a) == 1:
        return -1
    slow = a[0]
    fast = a[a[0]]
    while slow != fast:
        slow = a[slow]
        fast = a[a[fast]]
    fast = 0
    while slow != fast:
        slow = a[slow]
        fast = a[fast]
    return fast


def contains_nearby_duplicate(arr, k):
    # Duplicate within distance k. Time O(n), space O(k)
    if len(arr) == 0:
        return False
    hs = set()
    for i in range(len(arr)):
        if arr[i] in hs:
            return True
        if len(hs) >= k:
            hs.discard(arr[i - k])
        hs.add(arr[i])
    return False


def self_excluding_product(a):
    # Product array (self excluding), no division, O(n).
    temp = 1
    prod = [0] * len(a)
    for i in range(len(a)):
        prod[i] = temp
        temp *= a[i]
    temp = 1
    for i in range(len(a) - 1, -1, -1):
        prod[i] *= temp
        temp *= a[i]
    return prod


def print_intersection(arr1, arr2, m, n):
    # Common intersection of two sorted arrays.
    i = j = 0
    while i < m and j < n:
        if arr1[i] < arr2[j]:
            i += 1
        elif arr2[j] < arr1[i]:
            j += 1
        else:
            print(str(arr2[j]) + " ", end="")
            j += 1
            i += 1


def print_union(arr1, arr2, m, n):
    # Union of two sorted arrays.
    i = j = 0
    while i < m and j < n:
        if arr1[i] < arr2[j]:
            print(str(arr1[i]) + " ", end="")
            i += 1
        elif arr2[j] < arr1[i]:
            print(str(arr2[j]) + " ", end="")
            j += 1
        else:
            print(str(arr2[j]) + " ", end="")
            j += 1
            i += 1
    while i < m:
        print(str(arr1[i]) + " ", end="")
        i += 1
    while j < n:
        print(str(arr2[j]) + " ", end="")
        j += 1
    return 0


def find_common(ar1, ar2, ar3, n1, n2, n3):
    # Common elements in three sorted arrays. Time O(n1+n2+n3)
    i = j = k = 0
    while i < n1 and j < n2 and k < n3:
        if ar1[i] == ar2[j] and ar2[j] == ar3[k]:
            print(ar1[i], end="")
            i += 1
            j += 1
            k += 1
        elif ar1[i] < ar2[j]:
            i += 1
        elif ar2[j] < ar3[k]:
            j += 1
        else:
            k += 1


def min_dist(arr, n, x, y):
    # Minimum distance between values x and y.
    i = 0
    min_dist_val = INT_MAX
    prev = 0
    for i in range(n):
        if arr[i] == x or arr[i] == y:
            prev = i
            break
    while i < n:
        if arr[i] == x or arr[i] == y:
            if arr[prev] != arr[i] and (i - prev) < min_dist_val:
                min_dist_val = i - prev
                prev = i
            else:
                prev = i
        i += 1
    return min_dist_val


def find_first_repeating(a):
    # First repeating element. O(n)
    # NOTE: faithful port; the reference starts at index len(a) (out of bounds).
    mn = -1
    seen = set()
    for i in range(len(a), 0, -1):
        if a[i] in seen:
            mn = i
        else:
            seen.add(a[i])
    return a[mn]


def find_cross_over(arr, low, high, x):
    # Crossover point (last index whose value <= x). Time O(logn)
    if arr[high] <= x:
        return high
    if arr[low] > x:
        return low
    mid = (low + high) // 2
    if arr[mid] <= x and arr[mid + 1] > x:
        return mid
    if arr[mid] < x:
        return find_cross_over(arr, mid + 1, high, x)
    return find_cross_over(arr, low, mid - 1, x)


def print_k_closest(arr, x, k, n):
    # Print k closest elements to x.
    l = find_cross_over(arr, 0, n - 1, x)
    r = l + 1
    count = 0
    if arr[l] == x:
        l -= 1
    while l >= 0 and r < n and count < k:
        if x - arr[l] < arr[r] - x:
            print(arr[l])
            l -= 1
        else:
            print(arr[r])
            r += 1
        count += 1
    while count < k and l >= 0:
        print(arr[l])
        l -= 1
    count += 1
    while count < k and r < n:
        print(arr[r])
        r += 1
    count += 1


def sort_0_and_1(arr, size):
    # Sort array of 0s and 1s.
    left, right = 0, size - 1
    while left < right:
        while arr[left] == 0 and left < right:
            left += 1
        while arr[right] == 1 and left < right:
            right -= 1
        if left < right:
            arr[left] = 0
            arr[right] = 1


def sort_012(a):
    # Dutch national flag sort of 0s, 1s, 2s.
    low = 0
    mid = 0
    high = len(a) - 1
    while mid <= high:
        if a[mid] == 0:
            swap(a, low, mid)
            low += 1
            mid += 1
        elif a[mid] == 1:
            mid += 1
        elif a[mid] == 2:
            swap(a, mid, high)
            high -= 1
    return a


def sort_k_colors2_two_pass(colors, k):
    # Counting sort of k colors (1..k). O(k) space, O(n) time.
    count = [0] * k
    for color in colors:
        count[color - 1] += 1
    index = 0
    for i in range(k):
        while count[i] > 0:
            colors[index] = i + 1
            index += 1
            count[i] -= 1


def sort_k_colors2(colors, k):
    # In-place three-way partition repeated for shrinking [min,max].
    pl = 0
    pr = len(colors) - 1
    i = 0
    mn, mx = 1, k
    while mn < mx:
        while i <= pr:
            if colors[i] == mn:
                swap(colors, pl, i)
                i += 1
                pl += 1
            elif colors[i] == mx:
                swap(colors, pr, i)
                pr -= 1
            else:
                i += 1
        i = pl
        mn += 1
        mx -= 1


def sort_neg_pos(arr):
    # Move negatives to front (relative order of positives not preserved).
    left, right = 0, len(arr) - 1
    while left < right:
        while arr[left] < 0 and left < right:
            left += 1
        while arr[right] > 0 and left < right:
            right -= 1
        if left < right:
            swap(arr, left, right)


def rearrange_with_order(arr, n):
    # Alternate +/- maintaining order. Time O(N), Space O(1)
    outofplace = -1
    for index in range(n):
        if outofplace >= 0:
            if ((arr[index] >= 0 and arr[outofplace] < 0)
                    or (arr[index] < 0 and arr[outofplace] >= 0)):
                right_rotate_range(arr, n, outofplace, index)
                if index - outofplace > 2:
                    outofplace = outofplace + 2
                else:
                    outofplace = -1
        if outofplace == -1:
            if (arr[index] >= 0 and index % 2 == 0) or (arr[index] < 0 and index % 2 != 0):
                outofplace = index


def right_rotate_range(arr, n, outofplace, cur):
    # Right rotate elements between [outofplace, cur].
    tmp = arr[cur]
    for i in range(cur, outofplace, -1):
        arr[i] = arr[i - 1]
    arr[outofplace] = tmp


def rearrange(arr, n):
    # Rearrange +/- alternately, O(n)/O(1).
    # NOTE: faithful to reference, which swaps by *value* (arr[i]) not index.
    i = -1
    for j in range(n):
        if arr[j] < 0:
            i += 1
            swap(arr, arr[i], arr[j])
    pos = i + 1
    neg = 0
    while pos < n and neg < pos and arr[neg] < 0:
        swap(arr, arr[neg], arr[pos])
        pos += 1
        neg += 2


def wiggle_sort(nums):
    # s1 <= s2 >= s3 <= s4 ... (order not maintained).
    if nums is None or len(nums) <= 1:
        return nums
    for i in range(len(nums) - 1):
        if i % 2 == 0:
            if nums[i] > nums[i + 1]:
                swap(nums, i, i + 1)
        else:
            if nums[i] < nums[i + 1]:
                swap(nums, i, i + 1)
    return nums


def wiggle_sort_ll(nums):
    # nums[0] < nums[1] > nums[2] < nums[3] ... (median-based, here median=0).
    median = 0
    n = len(nums)
    left = 0
    i = 0
    right = n - 1
    while i <= right:
        if nums[new_index(i, n)] > median:
            swap(nums, new_index(left, n), new_index(i, n))
            left += 1
            i += 1
        elif nums[new_index(i, n)] < median:
            swap(nums, new_index(right, n), new_index(i, n))
            right -= 1
        else:
            i += 1


def new_index(index, n):
    return (1 + 2 * index) % (n | 1)


def print_two_odd(arr, size):
    # Two numbers with odd occurrences. Time O(n), space O(1)
    xor2 = arr[0]
    for i in range(1, size):
        xor2 = xor2 ^ arr[i]
    set_bit_no = xor2 & ~(xor2 - 1)
    x = 0
    y = 0
    for i in range(size):
        if (arr[i] & set_bit_no) == 0:
            x = x ^ arr[i]
        else:
            y = y ^ arr[i]
    print(str(x) + " " + str(y), end="")


def find_longest_conseq_subseq(arr):
    # Longest consecutive subsequence (any order).
    m = set()
    max_count = 0
    count = 1
    for i in range(len(arr)):
        m.add(arr[i])
    for i in range(len(arr)):
        if (arr[i] - 1) not in m:
            temp = arr[i] + 1
            while temp in m:
                temp += 1
                count += 1
            max_count = max(count, max_count)
            count = 1
    return max_count


def find_length(arr, n):
    # Longest subarray whose distinct elements form a continuous range.
    max_len = 1
    for i in range(n - 1):
        mn, mx = arr[i], arr[i]
        for j in range(i + 1, n):
            mn = min(mn, arr[j])
            mx = max(mx, arr[j])
            if (mx - mn) == j - i:
                max_len = max(max_len, mx - mn + 1)
    return max_len


def find_contiguous_length(a):
    # Largest subarray of contiguous elements (with duplicates). O(n^2)
    n = len(a)
    max_len = 1
    for i in range(n - 1):
        seen = set()
        seen.add(a[i])
        mn, mx = a[i], a[i]
        for j in range(i + 1, n):
            if a[j] in seen:
                break
            seen.add(a[j])
            mn = min(mn, a[j])
            mx = max(mx, a[j])
            if mx - mn == j - i:
                max_len = max(max_len, mx - mn + 1)
    return max_len


def print_closest(ar1, ar2, m, n, x):
    # Pair (one from each sorted array) with sum closest to x.
    diff = INT_MAX
    res_l = 0
    res_r = 0
    l = 0
    r = n - 1
    while l < m and r >= 0:
        if abs(ar1[l] + ar2[r] - x) < diff:
            res_l = l
            res_r = r
            diff = abs(ar1[l] + ar2[r] - x)
        if ar1[l] + ar2[r] > x:
            r -= 1
        else:
            l += 1
    print(str(ar1[res_l]) + " " + str(ar2[res_r]), end="")


def print_max_activities(s, f, n):
    # Activity selection (greedy). Reference sorts only finish times.
    f.sort()
    i = 0
    print(i, end="")
    for j in range(1, n):
        if s[j] >= f[i]:
            print(j)
            i = j


def min_cost(ticket):
    # Minimum cost to reach last station given upper-triangular cost matrix.
    assert ticket is not None and len(ticket) > 0 and len(ticket) == len(ticket[0])
    n = len(ticket)
    T = [0] * n
    T1 = [0] * n
    T1[0] = -1
    for i in range(1, n):
        T[i] = ticket[0][i]
        T1[i] = i - 1
    for i in range(1, n):
        for j in range(i + 1, n):
            if T[j] > T[i] + ticket[i][j]:
                T[j] = T[i] + ticket[i][j]
                T1[j] = i
    i = n - 1
    parts = []
    while i != -1:
        parts.append(str(i))
        i = T1[i]
    print(" ".join(parts))
    return T[n - 1]


def find_platform(arr, dep, n):
    # Minimum platforms for trains. O(nLogn)
    arr.sort()
    dep.sort()
    plat_needed = 1
    result = 1
    i = 1
    j = 0
    while i < n and j < n:
        if arr[i] < dep[j]:
            plat_needed += 1
            i += 1
            if plat_needed > result:
                result = plat_needed
        else:
            plat_needed -= 1
            j += 1
    return result


def max_ones_index(arr, n):
    # Index of 0 to flip for longest run of 1s.
    max_count = 0
    max_index = -1
    prev_zero = -1
    prev_prev_zero = -1
    for curr in range(n):
        if arr[curr] == 0:
            if curr - prev_prev_zero > max_count:
                max_count = curr - prev_prev_zero
                max_index = prev_zero
            prev_prev_zero = prev_zero
            prev_zero = curr
    if n - prev_prev_zero > max_count:
        max_index = prev_zero
    return max_index


def find_max_one(a, k):
    # Longest run of 1s after flipping at most k 0s.
    max_count = 0
    max_index = 0
    curr_count = 0
    for i in range(len(a)):
        if a[i] == 0 and max_index < k:
            curr_count += 1
            max_index += 1
        elif a[i] == 1:
            curr_count += 1
        else:
            max_count = max(max_count, curr_count)
            max_index = 0
            curr_count = 0
    max_count = max(max_count, curr_count)
    return max_count


def match_pairs(nuts, bolts, low, high):
    # Match nuts and bolts (quicksort-like). Time O(nLogn)
    if low < high:
        pivot = partition_chars(nuts, low, high, bolts[high])
        partition_chars(bolts, low, high, nuts[pivot])
        match_pairs(nuts, bolts, low, pivot - 1)
        match_pairs(nuts, bolts, pivot + 1, high)


def partition_chars(arr, low, high, pivot):
    # Partition list of chars around an externally provided pivot.
    i = low
    for j in range(low, high):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
        elif arr[j] == pivot:
            arr[j], arr[high] = arr[high], arr[j]
            j -= 1
    arr[i], arr[high] = arr[high], arr[i]
    return i


def remove_dup(a):
    # Remove duplicates from unsorted array (keeps first occurrences).
    seen = set()
    k = 0
    if len(a) < 2:
        return a
    for i in range(len(a)):
        if a[i] not in seen:
            a[k] = a[i]
            k += 1
            seen.add(a[i])
    return a[:k]


def remove_duplicates(A):
    # Remove duplicates in place from a sorted array; return trimmed copy.
    if len(A) < 2:
        return A
    j = 0
    i = 1
    while i < len(A):
        if A[i] == A[j]:
            i += 1
        else:
            j += 1
            A[j] = A[i]
            i += 1
    return A[:j + 1]


def remove_duplicates1(nums):
    # Allow duplicates at most twice; return new length.
    i = 0
    for n in nums:
        if i < 2 or n > nums[i - 2]:
            nums[i] = n
            i += 1
    return i


def find_unique(a):
    # Integers appearing exactly once (unsorted input).
    m = {}
    out = []
    for i in range(len(a)):
        if a[i] in m:
            m[a[i]] = m[a[i]] + 1
        else:
            m[a[i]] = 1
    for key, value in m.items():
        if value == 1:
            out.append(key)
    return out


def find_unique_sorted(nums):
    # Print integers appearing once in a sorted array.
    count = 0
    for i in range(len(nums)):
        if i == len(nums) - 1:
            if count == 0:
                print(nums[i])
            break
        if nums[i] != nums[i + 1]:
            if count == 0:
                print(nums[i])
            count = 0
        else:
            count += 1


def find_unique_numbers(data):
    # Unique numbers from sorted array using binary search for last occurrence.
    result = []
    i = 0
    while i < len(data):
        temp = last(data, i, len(data) - 1, data[i], len(data))
        if i == temp:
            result.append(data[i])
            i += 1
        else:
            i = temp + 1
    return result


def check_duplicates_within_k(a, k):
    # Contains duplicate within distance k.
    hs = set()
    for i in range(len(a)):
        if a[i] in hs:
            return True
        hs.add(a[i])
        if i >= k:
            hs.discard(a[i - k])
    return False


def contains_nearby_almost_duplicate(nums, k, t):
    # |nums[i]-nums[j]| <= t and |i-j| <= k (bucketing).
    if k < 1 or t < 0:
        return False
    m = {}
    for i in range(len(nums)):
        remapped_num = nums[i] - INT_MIN
        bucket = remapped_num // (t + 1)
        if (bucket in m
                or (bucket - 1 in m and remapped_num - m[bucket - 1] <= t)
                or (bucket + 1 in m and m[bucket + 1] - remapped_num <= t)):
            return True
        if len(m) >= k:
            last_bucket = (nums[i - k] - INT_MIN) // (t + 1)
            m.pop(last_bucket, None)
        m[bucket] = remapped_num
    return False


def can_jump(A):
    # Jump game: can reach last index.
    if len(A) <= 1:
        return True
    mx = A[0]
    for i in range(len(A)):
        if mx <= i and A[i] == 0:
            return False
        if i + A[i] > mx:
            mx = i + A[i]
        if mx >= len(A) - 1:
            return True
    return False


def min_jump(nums):
    # Minimum number of jumps to reach the end.
    if nums is None or len(nums) == 0:
        return 0
    last_reach = 0
    reach = 0
    step = 0
    i = 0
    while i <= reach and i < len(nums):
        if i > last_reach:
            step += 1
            last_reach = reach
        reach = max(reach, nums[i] + i)
        i += 1
    if reach < len(nums) - 1:
        return 0
    return step


def remove_number(A, n):
    # Remove all instances of n in place; return new length.
    if A is None or len(A) == 0:
        return 0
    i = 0
    for j in range(len(A)):
        if A[j] != n:
            A[i] = A[j]
            i += 1
    return i


def find_max_sliding(x, k):
    # Maximum of all subarrays of size k. Time O(n), Aux space O(K)
    q = deque()
    i = 0
    for i in range(k):
        while q and x[q[-1]] <= x[i]:
            q.pop()
        q.append(i)
    for i in range(k, len(x)):
        print(x[q[0]])
        while q and q[0] <= i - k:
            q.popleft()
        while q and x[q[-1]] <= x[i]:
            q.pop()
        q.append(i)
    print(x[q[0]])


def rearrange0(arr, n):
    # Max, min, 2nd max, 2nd min ... using modular encoding. Time O(n)
    arr.sort()
    max_idx = n - 1
    min_idx = 0
    max_elem = arr[n - 1] + 1
    for i in range(n):
        if i % 2 == 0:
            arr[i] += (arr[max_idx] % max_elem) * max_elem
            max_idx -= 1
        else:
            arr[i] += (arr[min_idx] % max_elem) * max_elem
            min_idx += 1
    for i in range(n):
        arr[i] = arr[i] // max_elem


def rearrange1(arr, n):
    # Cyclic in-place rearrange.
    # NOTE: faithful to reference, which uses swap(arr, temp, arr[j]) (by value).
    for i in range(n):
        temp = arr[i]
        while temp > 0:
            j = 2 * i + 1 if i < n // 2 else 2 * (n - 1 - i)
            if i == j:
                arr[i] = -temp
                break
            swap(arr, temp, arr[j])
            arr[j] = -arr[j]
            i = j
    for i in range(n):
        arr[i] = -arr[i]


def max_profit(prices):
    # Best single buy/sell profit.
    if prices is None or len(prices) < 2:
        return 0
    max_diff = 0
    min_element = prices[0]
    for i in range(1, len(prices)):
        if prices[i] - min_element > max_diff:
            max_diff = prices[i] - min_element
        if prices[i] < min_element:
            min_element = prices[i]
    return max_diff


def max_profit_multi_trans(arr):
    # Multiple transactions allowed (sell before buying again).
    if len(arr) == 0:
        return 0
    profit = 0
    local_min = arr[0]
    for i in range(1, len(arr)):
        if arr[i - 1] >= arr[i]:
            local_min = arr[i]
        else:
            profit += arr[i] - local_min
            local_min = arr[i]
    return profit


def max_profit2(prices):
    profit = 0
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            profit += diff
    return profit


def max_profit3(prices):
    # At most two transactions.
    max_profit1 = 0
    max_profit2_ = 0
    lowest_buy_price1 = INT_MAX
    lowest_buy_price2 = INT_MAX
    for p in prices:
        max_profit2_ = max(max_profit2_, p - lowest_buy_price2)
        lowest_buy_price2 = min(lowest_buy_price2, p - max_profit1)
        max_profit1 = max(max_profit1, p - lowest_buy_price1)
        lowest_buy_price1 = min(lowest_buy_price1, p)
    return max_profit2_


def max_profit_at_most_k_trans(prices, k):
    # At most k transactions. Time/space O(k * days)
    n = len(prices)
    profit = [[0] * (n + 1) for _ in range(k + 1)]
    for i in range(k + 1):
        profit[i][0] = 0
    for j in range(n + 1):
        profit[0][j] = 0
    for i in range(1, k + 1):
        prev_diff = INT_MIN
        for j in range(1, n):
            prev_diff = max(prev_diff, profit[i - 1][j - 1] - prices[j - 1])
            profit[i][j] = max(profit[i][j - 1], prices[j] + prev_diff)
    return profit[k][n - 1]


def stock_with_fees(prices, fee):
    # Unlimited transactions with a per-transaction fee.
    after_buy = -prices[0]
    after_sell = 0
    for i in range(1, len(prices)):
        old_buy = after_buy
        old_sell = after_sell
        after_buy = max(old_buy, old_sell - prices[i])
        after_sell = max(old_sell, old_buy + prices[i] - fee)
    return after_sell


def schedule_ads(ads):
    # Weighted job scheduling: maximize revenue from non-overlapping ads.
    ads.sort(key=lambda ad: ad.finish)
    n = len(ads)
    table = [0] * n
    table[0] = ads[0].revenue
    for i in range(1, n):
        incl_prof = ads[i].revenue
        l = binary_search_ad(ads, i)
        if l != -1:
            incl_prof += table[l]
        table[i] = max(incl_prof, table[i - 1])
    return table[n - 1]


def binary_search_ad(ads, index):
    # Latest ad before `index` that does not conflict; -1 if none.
    lo, hi = 0, index - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if ads[mid].finish <= ads[index].start:
            if ads[mid + 1].finish <= ads[index].start:
                lo = mid + 1
            else:
                return mid
        else:
            hi = mid - 1
    return -1


def rob(num):
    # House robbing: max non-adjacent sum. Time O(N), space O(1)
    if num is None or len(num) == 0:
        return 0
    even = 0
    odd = 0
    for i in range(len(num)):
        if i % 2 == 0:
            even += num[i]
            even = even if even > odd else odd
        else:
            odd += num[i]
            odd = even if even > odd else odd
    return even if even > odd else odd


def find_max_days(arr):
    # Max nights you can accommodate with a gap of >= 1 between requests.
    max_days_to_pos = [0] * (len(arr) + 1)
    max_days_to_pos[0] = 0
    max_days_to_pos[1] = arr[0]
    for i in range(2, len(max_days_to_pos)):
        max_days_to_pos[i] = max(max_days_to_pos[i - 1], max_days_to_pos[i - 2] + arr[i - 1])
    return max_days_to_pos[len(max_days_to_pos) - 1]


def get_magic_index_dup(a, start, end):
    # Magic index A[i] == i in sorted array with duplicates.
    if start > end:
        return -1
    mid = start + (end - start) // 2
    if a[mid] == mid:
        return mid
    result = get_magic_index_dup(a, start, min(mid - 1, a[mid]))
    if result == -1:
        result = get_magic_index_dup(a, max(mid + 1, a[mid]), end)
    return result


def odd_man_out(array):
    # The element that appears once (others appear twice). O(n)/O(1)
    val = 0
    for i in range(len(array)):
        val ^= array[i]
    return val


def max_product_of_three(a):
    # Max product of three numbers.
    largest = a[0]
    secondlargest = 0
    thirdlargest = 0
    min1 = 0
    min2 = 0
    for i in range(len(a)):
        number = a[i]
        if number > largest:
            thirdlargest = secondlargest
            secondlargest = largest
            largest = number
        elif number > secondlargest:
            thirdlargest = secondlargest
            secondlargest = number
        elif number > thirdlargest:
            thirdlargest = number
        if number < min1:
            min2 = min1
            min1 = number
        elif number < min2:
            min2 = number
    return largest * max(thirdlargest * secondlargest, min1 * min2)


def are_consecutive(input_):
    # True if positive numbers are consecutive (uses sign marking). Modifies input_.
    mn = INT_MAX
    for i in range(len(input_)):
        if input_[i] < mn:
            mn = input_[i]
    for i in range(len(input_)):
        if abs(input_[i]) - mn >= len(input_):
            return False
        if input_[abs(input_[i]) - mn] < 0:
            return False
        input_[abs(input_[i]) - mn] = -input_[abs(input_[i]) - mn]
    for i in range(len(input_)):
        input_[i] = abs(input_[i])
    return True


def get_missing_no(a, n):
    # Missing number in 1..n via XOR.
    x1 = a[0]
    for i in range(1, n):
        x1 = x1 ^ a[i]
    for i in range(1, n + 1):
        x1 = x1 ^ i
    return x1


def find_numbers(a, N):
    # Two missing (or two repeating) numbers via XOR partitioning.
    x = 0
    for i in range(len(a)):
        x = x ^ a[i]
    for i in range(1, N + 1):
        x = x ^ i
    x = x & (~(x - 1))
    p = 0
    q = 0
    for i in range(len(a)):
        if (a[i] & x) == x:
            p = p ^ a[i]
        else:
            q = q ^ a[i]
    for i in range(1, N + 1):
        if (i & x) == x:
            p = p ^ i
        else:
            q = q ^ i
    print("N1: " + str(p) + " N2: " + str(q))


def get_avg(prev_avg, x, n):
    # New running average after including x.
    return (prev_avg * n + x) / (n + 1)


def stream_avg(arr, n):
    # Print running average of a stream.
    avg = 0
    for i in range(n):
        avg = get_avg(avg, arr[i], i)
        print("Average of" + str(i) + "1" + " numbers is" + str(avg))


def largest_number(num):
    # Arrange numbers to form the largest concatenation.
    if num is None or len(num) == 0:
        return ""
    array = [str(x) for x in num]

    def cmp(o1, o2):
        comb1 = o1 + o2
        comb2 = o2 + o1
        return (comb1 > comb2) - (comb1 < comb2)

    array.sort(key=functools.cmp_to_key(cmp))
    result = ""
    for s in array:
        result = s + result
    return result


def randomize(arr, n):
    # Fisher-Yates shuffle. NOTE: faithful to reference's int(Math.random())==0 bug,
    # so j is always 0 (no real shuffle).
    for i in range(n - 1, 0, -1):
        j = int(random.random()) % (i + 1)
        arr[i] ^= arr[j]
        arr[j] ^= arr[i]
        arr[i] ^= arr[j]


def serialize(arr):
    # Serialize string array into a single bit-string.
    sb = []
    for s in arr:
        b_length = str(len(s)).encode("ascii")
        b_data = s.encode("ascii")
        sb.append(format(b_length[0] & 0xFF, "08b"))
        for item in b_data:
            sb.append(format(item & 0xFF, "08b"))
    return "".join(sb)


def de_serialize(arr):
    # Deserialize bit-string back into a list of strings.
    output = []
    byts = get_bytes(arr)
    s = byts.decode("ascii", errors="replace")
    i = 0
    while i < len(byts):
        length = int(s[i:i + 1])
        i += 1
        data = s[i:i + length]
        i += length
        output.append(data)
    return output


def get_bytes(bit_string):
    num_bytes = len(bit_string) // 8
    if len(bit_string) % 8 != 0:
        num_bytes += 1
    b = bytearray(num_bytes)
    byte_index = 0
    bit_index = 0
    for i in range(len(bit_string)):
        if bit_string[i] == "1":
            b[byte_index] |= (1 << (7 - bit_index))
        bit_index += 1
        if bit_index == 8:
            bit_index = 0
            byte_index += 1
    return bytes(b)


def are_consecutive2(arr, n):
    # True if array elements are consecutive (visited-flag method).
    if n < 1:
        return False
    mn = get_min(arr, n)
    mx = get_max(arr, n)
    if mx - mn + 1 == n:
        visited = [False] * n
        for i in range(n):
            if visited[arr[i] - mn]:
                return False
            visited[arr[i] - mn] = True
        return True
    return False


def get_min(arr, n):
    mn = arr[0]
    for i in range(1, n):
        if arr[i] < mn:
            mn = arr[i]
    return mn


def get_max(arr, n):
    mx = arr[0]
    for i in range(1, n):
        if arr[i] > mx:
            mx = arr[i]
    return mx


def sort_nearly_sorted(a, k):
    # Sort a list where each element is exactly distance k from its position.
    if k == 0:
        return a
    count = 0
    for i in range(len(a)):
        swap2(i, i + k, a)
        count += 1
        if count == k:
            i += k  # noqa: (loop var reassignment is intentional, mirrors reference)
            count = 0
    return a


def swap2(x, y, a):
    # XOR swap a[x], a[y] (Java capital-S Swap).
    a[x] ^= a[y]
    a[y] ^= a[x]
    a[x] ^= a[y]


def minimum_coin_bottom_up(total, coins):
    # Minimum number of coins to form total. Time/space O(coins * total)
    dp = [0] * (total + 1)
    path = [0] * (total + 1)
    dp[0] = 0
    for i in range(1, total + 1):
        dp[i] = total + 1
        path[i] = -1
    for i in range(1, total + 1):
        for j in range(len(coins)):
            if i >= coins[j]:
                dp[i] = min(dp[i], dp[i - coins[j]] + 1)
    print_coin_combination(path, coins)
    return dp[total]


def print_coin_combination(R, coins):
    if R[len(R) - 1] == -1:
        print("No solution is possible", end="")
        return
    start = len(R) - 1
    print("Coins used to form total ", end="")
    while start != 0:
        j = R[start]
        print(str(coins[j]) + " ", end="")
        start = start - coins[j]
    print()


def count_ways(total, arr):
    # Number of ways to form total from coins (unlimited supply).
    dp = [0] * (total + 1)
    dp[0] = 1
    for i in range(len(arr)):
        for j in range(arr[i], total + 1):
            dp[j] += dp[j - arr[i]]
    return dp[total]


def fizzbuzz():
    # Counts to 100: fizz (mult 5), buzz (mult 7), fizzbuzz (both).
    for i in range(1, 101):
        if (i % 5) == 0 and (i % 7) == 0:
            print("fizzbuzz", end="")
        elif (i % 5) == 0:
            print("fizz", end="")
        elif (i % 7) == 0:
            print("buzz", end="")
        else:
            print(i, end="")
        print(" ", end="")
    print()


def max_diff(arr, arr_size):
    # Max diff arr[j]-arr[i] with j>i.
    max_diff_val = arr[1] - arr[0]
    min_element = arr[0]
    for i in range(1, arr_size):
        if arr[i] - min_element > max_diff_val:
            max_diff_val = arr[i] - min_element
        if arr[i] < min_element:
            min_element = arr[i]
    return max_diff_val


def minimum_distance_sum(words, a, b, c):
    # Minimum index-distance sum among three values.
    last_a = -1
    last_b = -1
    last_c = -1
    min_distance = INT_MAX
    for i in range(len(words)):
        if words[i] == a:
            last_a = i
        elif words[i] == b:
            last_b = i
        elif words[i] == c:
            last_c = i
        if last_a >= 0 and last_b >= 0 and last_c >= 0:
            min_distance = min(min_distance,
                               abs(last_a - last_c) + abs(last_a - last_b) + abs(last_b - last_c))
    return min_distance


def minimize_round_sum(input_, T):
    # Round each element up or down so the total equals T while minimizing
    # the sum of |xi - yi|.
    s = 0.0
    output = [0] * len(input_)
    for i in range(len(input_)):
        s += java_round(input_[i])
        output[i] = java_round(input_[i])
    diff = T - s
    if diff != 0:
        # max-heap by delta, stored as (-delta, index) so the largest delta is on top
        max_heap = []
        for i in range(len(input_)):
            delta = abs(input_[i] - output[i])
            if i < abs(diff):
                heapq.heappush(max_heap, (-delta, i))
            elif max_heap and delta > -max_heap[0][0]:
                heapq.heappop(max_heap)
                heapq.heappush(max_heap, (-delta, i))
        while max_heap and diff != 0:
            index = heapq.heappop(max_heap)[1]
            if diff > 0:
                output[index] += 1
                diff -= 1
            else:
                output[index] -= 1
                diff += 1
    return output


def find_next_greater_element(array):
    # Next Greater Element for every element (stack based).
    stack = []
    stack.append(array[0])
    for i in range(1, len(array)):
        while stack and array[i] > stack[-1]:
            popped_element = stack.pop()
            print(str(popped_element) + ", " + str(array[i]))
        stack.append(array[i])
    while stack:
        print(str(stack.pop()) + ", " + str(-1))


def next_greater_element(arr):
    # Next greater element without extra space.
    mx = arr[len(arr) - 1]
    print("for el: " + str(arr[len(arr) - 1]) + " next greater is: " + str(-1))
    for i in range(len(arr) - 2, -1, -1):
        if arr[i] < arr[i + 1]:
            print("for " + str(arr[i]) + " next greater is: " + str(arr[i + 1]))
        elif arr[i] < mx:
            print("for " + str(arr[i]) + " next greater is: " + str(mx))
        else:
            print("for " + str(arr[i]) + " next greater is: " + str(-1))
        if arr[i + 1] > mx:
            mx = arr[i + 1]


def incr_large_number(input_array):
    # Increment an arbitrarily large number stored as a digit array.
    if input_array is None:
        return input_array
    arr_length = len(input_array)
    all9s = True
    for i in range(arr_length):
        if input_array[i] != 9:
            all9s = False
            break
    if all9s:
        new_input_array = [0] * (arr_length + 1)
        new_input_array[0] = 1
        for i in range(1, len(new_input_array)):
            new_input_array[i] = 0
        return new_input_array
    else:
        for i in range(arr_length - 1, -1, -1):
            k = input_array[i]
            if k == 9:
                input_array[i] = 0
            else:
                k += 1
                input_array[i] = k
                return input_array
    return input_array


def get_max_of_max_prefix(a):
    # Max count of consecutive elements greater than a starting element.
    if len(a) < 2:
        return 1
    count = 0
    max_prefix = 0
    temp = a[0]
    for i in range(1, len(a)):
        if a[i] > temp:
            count += 1
        else:
            temp = a[i]
            count = 0
        if count > max_prefix:
            max_prefix = count
    return max_prefix


def sort_partial_list(a, x):
    # Sort an x-sorted list (each element at most x out of position).
    pq = []
    result = [0] * len(a)
    k = 0
    for i in range(len(a)):
        if i < x:
            heapq.heappush(pq, a[i])
        else:
            result[k] = heapq.heappop(pq)
            k += 1
            heapq.heappush(pq, a[i])
    while pq:
        result[k] = heapq.heappop(pq)
        k += 1
    return result


def divide_array(a):
    # True if removing one element splits array into two equal-sum subarrays.
    s = 0
    sum_so_far = 0
    for i in range(len(a)):
        s += a[i]
    for i in range(len(a)):
        if 2 * sum_so_far + a[i] == s:
            return True
        sum_so_far += a[i]
    return False


def max_index_diff(arr, n):
    # Maximum j - i with arr[j] > arr[i].
    r_max = [0] * n
    l_min = [0] * n
    l_min[0] = arr[0]
    for i in range(1, n):
        l_min[i] = min(arr[i], l_min[i - 1])
    r_max[n - 1] = arr[n - 1]
    for j in range(n - 2, -1, -1):
        r_max[j] = max(arr[j], r_max[j + 1])
    i = 0
    j = 0
    max_diff_val = -1
    while j < n and i < n:
        if l_min[i] < r_max[j]:
            max_diff_val = max(max_diff_val, j - i)
            j = j + 1
        else:
            i = i + 1
    return max_diff_val


def push_zeros_to_end(arr):
    # Move all zeroes to end (XOR swap).
    left, right = 0, len(arr) - 1
    while left < right:
        while arr[left] != 0 and left < right:
            left += 1
        while arr[right] == 0 and left < right:
            right -= 1
        if left < right:
            arr[left] ^= arr[right]
            arr[right] ^= arr[left]
            arr[left] ^= arr[right]
    return arr


def move_zero_with_order(input_):
    # Move 0s to the front while keeping non-zero relative order.
    last_non_zero_found_at = len(input_) - 1
    cur = len(input_) - 1
    while cur > 0:
        if input_[cur] != 0:
            swap(input_, last_non_zero_found_at, cur)
            last_non_zero_found_at -= 1
        cur -= 1


def max_sum_non_adjacent(a):
    # Max sum of non-adjacent elements (DP with output array).
    output = [0] * len(a)
    if len(a) == 0:
        return 0
    elif len(a) < 2:
        return a[0]
    elif len(a) == 2:
        return max(a[0], a[1])
    else:
        output[0] = a[0]
        output[1] = max(a[0], a[1])
        for i in range(2, len(a)):
            temp = max(a[i], a[i] + output[i - 2])
            output[i] = max(output[i - 1], temp)
    return output[len(a) - 1]


def find_max_sum_non_adjacent(arr):
    # Max sum of non-adjacent elements (O(1) space).
    incl = arr[0]
    excl = 0
    for i in range(1, len(arr)):
        excl_new = max(incl, excl)
        incl = excl + arr[i]
        excl = excl_new
    return max(incl, excl)


def print_combination(input_):
    # All combinations picking one element from each array (recursive).
    result = []
    combination_util(input_, result, 0, "")
    for num in result:
        print(num)


def combination_util(arr, result, level, current):
    if level == len(arr):
        result.append(int(current))
        return
    for i in range(len(arr[level])):
        combination_util(arr, result, level + 1, current + str(arr[level][i]))


def get_combinations(inputs):
    # All combinations picking one element from each list (iterative).
    output = []
    for i in inputs[0]:
        new_list = [i]
        output.append(new_list)
    index = 1
    while index < len(inputs):
        next_list = inputs[index]
        temp_output = []
        for first_list in output:
            for second in next_list:
                temp_list = list(first_list)
                temp_list.append(second)
                temp_output.append(temp_list)
        output = temp_output
        index += 1
    return output


def abc(votes):
    # Candidate with most votes; ties resolved by last in sorted order.
    counts = {}
    for i in range(len(votes)):
        if votes[i] not in counts:
            counts[votes[i]] = 1
        else:
            counts[votes[i]] = counts[votes[i]] + 1
    mx = INT_MIN
    key = ""
    for k in sorted(counts):
        if counts[k] >= mx:
            key = k
            mx = counts[k]
    return key


def min_swap(a, b):
    # Min swaps to make b equal to a (same multiset).
    m = {}
    count = 0
    for i in range(len(a)):
        m[a[i]] = i
    for j in range(len(b)):
        index = m[b[j]]
        if index != j:
            swap2(index, j, b)
            count += 1
    return count


def k_swap(arr, k):
    # Maximize integer with k swaps (greedy selection-style).
    n = len(arr)
    for i in range(k):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] > arr[min_idx]:
                min_idx = j
        swap(arr, min_idx, i)
    return arr


def find_one_occurance(a, low, high):
    # Element appearing once in a sorted array where others appear twice. O(log n)
    if low > high:
        return -1
    if high == low:
        return a[low]
    mid = low + (high - low) // 2
    if mid % 2 == 0:
        if a[mid] == a[mid + 1]:
            find_one_occurance(a, mid + 2, high)
        else:
            find_one_occurance(a, low, mid)
    else:
        if a[mid] == a[mid - 1]:
            find_one_occurance(a, mid + 1, high)
        else:
            find_one_occurance(a, low, mid - 1)
    return -1


def find_repeating_num(a):
    # In a sorted array where one element repeats, find it.
    low, high = 0, len(a)
    while low != high:
        mid = (low + high) // 2
        if (a[mid] - a[0]) >= mid:
            low = mid + 1
        else:
            high = mid
    return a[low]


def get_min_max(arr, n):
    # Min and max with minimum number of comparisons.
    minmax = MinMaxPair()
    if n % 2 == 0:
        if arr[0] > arr[1]:
            minmax.max = arr[0]
            minmax.min = arr[1]
        else:
            minmax.min = arr[0]
            minmax.max = arr[1]
        i = 2
    else:
        minmax.min = arr[0]
        minmax.max = arr[0]
        i = 1
    while i < n - 1:
        if arr[i] > arr[i + 1]:
            if arr[i] > minmax.max:
                minmax.max = arr[i]
            if arr[i + 1] < minmax.min:
                minmax.min = arr[i + 1]
        else:
            if arr[i + 1] > minmax.max:
                minmax.max = arr[i + 1]
            if arr[i] < minmax.min:
                minmax.min = arr[i]
        i += 2
    return minmax


def make_bricks(small, big, goal):
    # True if goal inches can be made from 1-inch and 5-inch bricks.
    if goal > big * 5 + small:
        return False
    if goal % 5 > small:
        return False
    return True


def longest_island(arr):
    # Longest island buildable by filling one stretch of water ('W') between lands.
    mx = 0
    start = 0
    curr = 0
    for i in range(len(arr)):
        if arr[i] == "L":
            mx = max(mx, i - start + 1)
            if i == 0 or arr[i - 1] == "W":
                curr = i
        else:
            start = curr
    mx = max(mx, len(arr) - start)
    return mx


def single_non_duplicate(nums):
    # Single element in sorted array where all others appear twice (binary search).
    n = len(nums)
    lo, hi = 0, n // 2
    while lo < hi:
        m = (lo + hi) // 2
        if nums[2 * m] != nums[2 * m + 1]:
            hi = m
        else:
            lo = m + 1
    return nums[2 * lo]


def single_non_duplicate1(nums):
    low = 0
    high = len(nums) - 1
    while low < high:
        mid = low + (high - low) // 2
        if nums[mid] != nums[mid + 1] and nums[mid] != nums[mid - 1]:
            return nums[mid]
        elif nums[mid] == nums[mid + 1] and mid % 2 == 0:
            low = mid + 1
        elif nums[mid] == nums[mid - 1] and mid % 2 == 1:
            low = mid + 1
        else:
            high = mid - 1
    return nums[low]


def fin_min_tickets_cost(a):
    # Minimum cost of tickets (1-day=2, 7-day=7, 30-day=25) for travel days.
    day_trip = [False] * 31
    for day in a:
        day_trip[day] = True
    min_cost_dp = [0] * 31
    min_cost_dp[0] = 0
    for d in range(1, 31):
        if not day_trip[d]:
            min_cost_dp[d] = min_cost_dp[d - 1]
            continue
        min_cost_val = min_cost_dp[d - 1] + 2
        for prev_d in range(max(0, d - 7), d - 4 + 1):
            min_cost_val = min(min_cost_val, min_cost_dp[prev_d] + 7)
        min_cost_val = min(min_cost_val, 25)
        min_cost_dp[d] = min_cost_val
    return min_cost_dp[30]


def _search_binary_search(arr, l, h, key):
    # Standalone binary search helper (Search.binarySearch in the reference).
    while l <= h:
        mid = l + (h - l) // 2
        if arr[mid] == key:
            return mid
        elif arr[mid] < key:
            l = mid + 1
        else:
            h = mid - 1
    return -1


def find_pos(arr, key):
    # Find position in a sorted array of unbounded size (exponential search).
    l, h = 0, 1
    val = arr[0]
    while val < key:
        l = h
        h = 2 * h
        val = arr[h]
    return _search_binary_search(arr, l, h, key)


def total_score(a):
    # Compute a game score with a stack ("X" doubles, "Z" undoes, "+" sums).
    stack = []
    total = 0
    for i in range(len(a)):
        if a[i] == "X":
            total += 2 * stack[-1]
            stack.append(2 * stack[-1])
        elif a[i] == "Z":
            total -= stack[-1]
            stack.pop()
        elif a[i] == "+":
            temp = stack.pop()
            t2 = stack[-1] + temp
            total += t2
            stack.append(temp)
            stack.append(t2)
        else:
            total += int(a[i])
            stack.append(int(a[i]))
    return total


def longest_zig_zag_sub_array(a):
    # Longest continuous zig-zag subarray length.
    b = [0] * (len(a) - 1)
    for i in range(len(a) - 1):
        if a[i] > a[i + 1]:
            b[i] = 0
        else:
            b[i] = 1
    count = 1
    for i in range(len(b) - 1):
        if b[i] != b[i + 1]:
            count += 1
    return count + 1


def sum_k_largest(a, k):
    # Sum of k largest elements (quickselect-style partition descending).
    s = 0
    quick(a, 0, len(a) - 1, k)
    for i in range(k):
        s += a[i]
    print(s, end="")
    return s


def quick(a, start, end, k):
    if start <= end:
        pivot = part(a, start, end)
        if pivot < k:
            quick(a, pivot + 1, end, k)
        else:
            quick(a, start, pivot - 1, k)


def part(a, start, end):
    pivot = a[end]
    index = start
    for i in range(start, end):
        if a[i] > pivot:
            swap(a, index, i)
            index += 1
    swap(a, index, end)
    return index


def compute_total_task_time(tasks, k):
    # Total time to run tasks with cool-down k between identical tasks.
    m = {}
    total = 0
    for task in tasks:
        if task in m:
            excepted_time = m[task] + k + 1
            if excepted_time > total:
                total = excepted_time
            else:
                total += 1
        else:
            total += 1
        m[task] = total
    return total


def least_interval(tasks, n):
    # Minimum intervals to run tasks with cool-down n.
    m = [0] * 26
    for c in tasks:
        m[ord(c) - ord("A")] += 1
    m.sort()
    max_val = m[25] - 1
    idle_slots = max_val * n
    for i in range(24, -1, -1):
        if m[i] <= 0:
            break
        idle_slots -= min(m[i], max_val)
    return idle_slots + len(tasks) if idle_slots > 0 else len(tasks)


def find_best_task_arrangement(tasks, k):
    # Rearrange tasks to minimize execution time (greedy max-frequency heap).
    n = len(tasks)
    counts = {}
    for task in tasks:
        counts[task] = counts.get(task, 0) + 1
    heap = []
    order = 0
    for cid, freq in counts.items():
        heapq.heappush(heap, (-freq, order, Task(cid, freq)))
        order += 1
    result = [None] * n
    i = 0
    while heap:
        c = 0
        next_round_task = []
        while c < k and heap:
            c += 1
            _, _, task = heapq.heappop(heap)
            task.frequency -= 1
            result[i] = task.id
            i += 1
            if task.frequency > 0:
                next_round_task.append(task)
        for task in next_round_task:
            heapq.heappush(heap, (-task.frequency, order, task))
            order += 1
    return result


def decode_way(s):
    # Number of ways to decode a digit string (1=a..26=z).
    length = len(s)
    if length == 0:
        raise ValueError("s can't be empty")
    pre = 1
    cur = 0 if s[0] == "0" else 1
    i = 1
    while i < length and cur != 0:
        tmp = cur
        if s[i - 1] == "1" or (s[i - 1] == "2" and s[i] <= "6"):
            if s[i] == "0":
                cur = pre
            else:
                cur += pre
        elif s[i] == "0":
            cur = 0
        pre = tmp
        i += 1
    return cur


def print_noop():
    # Java had an empty `print()` method.
    pass


def is_valid_lottery_number(input_):
    # Valid lottery number: 7 unique digits between 1 and 59 (Fibonacci-like check).
    seen = set()
    if len(input_) == 0 or len(input_) < 7 or len(input_) > 14:
        return False
    prev = 1
    curr = 1
    prev_prev = 1
    for i in range(1, len(input_)):
        if ord(input_[i]) not in seen:
            if (ord(input_[i - 1]) < 5 + 48
                    or (ord(input_[i - 1]) == 5 + 48 and ord(input_[i]) <= 9 + 48)):
                curr = prev + prev_prev
            else:
                curr = prev
            prev_prev = prev
            prev = curr
        seen.add(ord(input_[i]))
    return curr == 7


def sort_squares(arr):
    # Sort array after squaring elements (merge negative & positive halves).
    n = len(arr)
    k = 0
    for k in range(n):
        if arr[k] >= 0:
            break
    else:
        k = n
    i = k - 1
    j = k
    ind = 0
    temp = [0] * n
    while i >= 0 and j < n:
        if arr[i] * arr[i] < arr[j] * arr[j]:
            temp[ind] = arr[i] * arr[i]
            ind += 1
            i -= 1
        else:
            temp[ind] = arr[j] * arr[j]
            ind += 1
            j += 1
    while i >= 0:
        temp[ind] = arr[i] * arr[i]
        ind += 1
        i -= 1
    while j < n:
        temp[ind] = arr[j] * arr[j]
        ind += 1
        j += 1
    for x in range(n):
        arr[x] = temp[x]


def can_complete_circuit(gas, cost):
    # Gas station circuit: starting index or -1.
    sum_gas = 0
    sum_cost = 0
    start = 0
    tank = 0
    for i in range(len(gas)):
        sum_gas += gas[i]
        sum_cost += cost[i]
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    if sum_gas < sum_cost:
        return -1
    return start


def first_missing_positive(nums):
    # Smallest missing positive integer.
    n = len(nums)
    for i in range(n):
        while 0 < nums[i] < n and nums[i] != nums[nums[i]]:
            swap(nums, i, nums[i])
    for i in range(n):
        if nums[i] != i:
            return i
    return n + 1


def combination_sum3(k, n):
    # k numbers (1..9) summing to n, each used once.
    ans = []
    combination(ans, [], k, 1, n)
    return ans


def combination(ans, comb, k, start, n):
    if len(comb) == k and n == 0:
        ans.append(list(comb))
        return
    for i in range(start, 10):
        comb.append(i)
        combination(ans, comb, k, i + 1, n - i)
        comb.pop()


def combination_multiply(n):
    # Combinations of factors multiplying to n.
    ans = []
    combination_multiply_util(ans, [], n, 1, n)
    return ans


def combination_multiply_util(ans, comb, target, start, n):
    if target % n == 0 and start != 1:
        comb.append(n)
        ans.append(list(comb))
        return
    for i in range(start, target + 1):
        if target % i == 0:
            comb.append(i)
            combination_multiply_util(ans, comb, target, i + 1, n // i)
            comb.clear()


def first_bad_version(n):
    # First bad version via binary search.
    left = 1
    right = n
    while left < right:
        mid = left + (right - left) // 2
        if is_bad_version(mid):
            right = mid
        else:
            left = mid + 1
    return left


def is_bad_version(n):
    return True


def sort_transformed_array(nums, a, b, c):
    # Apply f(x)=ax^2+bx+c to a sorted array, return sorted. O(n)
    n = len(nums)
    sorted_arr = [0] * n
    i, j = 0, n - 1
    index = n - 1 if a >= 0 else 0
    while i <= j:
        qi = quad(nums[i], a, b, c)
        qj = quad(nums[j], a, b, c)
        if a >= 0:
            if qi >= qj:
                sorted_arr[index] = quad(nums[i], a, b, c)
                i += 1
            else:
                sorted_arr[index] = quad(nums[j], a, b, c)
                j -= 1
            index -= 1
        else:
            if qi >= qj:
                sorted_arr[index] = quad(nums[j], a, b, c)
                j -= 1
            else:
                sorted_arr[index] = quad(nums[i], a, b, c)
                i += 1
            index += 1
    return sorted_arr


def quad(x, a, b, c):
    return a * x * x + b * x + c


def check_possibility(nums):
    # True if array can become non-decreasing by modifying at most 1 element.
    index = -1
    for i in range(1, len(nums)):
        if nums[i - 1] > nums[i]:
            if index != -1:
                return False
            index = i
    return (index == -1
            or index == 1 or index == len(nums) - 1
            or nums[index - 2] <= nums[index] or nums[index - 1] <= nums[index + 1])


def check_possibility1(nums):
    cnt = 0
    n = len(nums)
    for i in range(n - 1):
        if nums[i] > nums[i + 1]:
            cnt += 1
            if i >= 1 and nums[i + 1] < nums[i - 1]:
                nums[i + 1] = nums[i]
        if cnt > 1:
            return False
    return True


def can_reach_mn(m, n):
    # Can (1,1) reach (m,n) where moves are (x,y)->(x+y,y) or (x,x+y). O(m+n)
    prev = [m, n]
    while prev[0] >= 1 and prev[1] >= 1:
        get_previous_pos(prev)
        if prev[0] == 1 and prev[1] == 1:
            return True
    return False


def get_previous_pos(cur):
    if cur[0] < cur[1]:
        cur[1] -= cur[0]
    else:
        cur[0] -= cur[1]


def count_set_bits(x):
    # Number of set bits (Brian Kernighan).
    count = 0
    while x > 0:
        x = x & (x - 1)
        count += 1
    return count


def count_set_bit(number):
    counter = 0
    while number > 0:
        if number % 2 == 1:
            counter += 1
        number = number // 2
    return counter


def smallest_range(input_):
    # Smallest range covering at least one number from each of k sorted lists.
    # Time = O(K) + O(n * logK)
    heap = []
    order = 0
    mx = INT_MIN
    rng = INT_MAX
    start = -1
    end = -1
    for i in range(len(input_)):
        lst = KSortedList(0, input_[i][0], i)
        heapq.heappush(heap, (lst.value, order, lst))
        order += 1
        mx = max(mx, input_[i][0])
    while len(heap) == len(input_):
        _, _, item = heapq.heappop(heap)
        if mx - item.value < rng:
            rng = mx - item.value
            start = item.value
            end = mx
        if item.position < len(input_[item.k_index]):
            item.value = input_[item.k_index][item.position]
            item.position += 1
            heapq.heappush(heap, (item.value, order, item))
            order += 1
            if item.value > mx:
                mx = item.value
    return [start, end]


def trap_water(input_):
    # Trapping rain water (two-pointer).
    left, right = 0, len(input_) - 1
    ans = 0
    left_max = 0
    right_max = 0
    while left < right:
        if input_[left] < input_[right]:
            if input_[left] >= left_max:
                left_max = input_[left]
            else:
                ans += left_max - input_[left]
            left += 1
        else:
            if input_[right] >= right_max:
                right_max = input_[right]
            else:
                ans += right_max - input_[right]
            right -= 1
    return ans


if __name__ == "__main__":
    # Mirrors the Java main: minimize the rounding so the total equals 8.
    data = [0.70, 2.80, 4.90]
    print(str(minimize_round_sum(data, 8)))
