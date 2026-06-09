"""Idiomatic Python 3 port of java/Numbers.java (original package code.ds).

Interview / DSA reference implementation covering number theory, bit
manipulation, combinatorics and assorted numeric puzzles: Fibonacci,
factorials, fast power, Roman numerals, k-nearest points (heap + selection),
median-of-medians selection, streaming median, 0/1 knapsack, division without
``/``, nega-binary, weighted random sampling, look-and-say, ``atoi`` etc.

Notes on the port:
  * Java method overloading does not exist in Python; the two ``power``
    overloads became :meth:`Numbers.power_int` and :meth:`Numbers.power_float`,
    and the private ``sqrt`` became :meth:`Numbers.sqrt_int` (also avoids any
    confusion with :func:`math.sqrt`).
  * Java ``int[]`` / ``List`` -> Python ``list``; ``PriorityQueue`` -> ``heapq``
    (a max-heap is simulated by pushing negated values); ``HashMap`` /
    ``HashSet`` -> ``dict`` / ``set``.
  * Python ints are arbitrary precision, so the 32-bit ``INT_MIN`` / ``INT_MAX``
    overflow guards are retained purely for faithfulness (see :func:`atoi`,
    :func:`divide`).
  * The median-of-medians helpers are deliberately entangled in the original;
    they are ported faithfully and exercised lightly from ``__main__``.

This module is intentionally named ``numbers_impl`` so it does not shadow (or
get shadowed by) the standard library ``numbers`` module.
"""

from __future__ import annotations

import heapq
import math
import random
import re

INT_MIN = -2147483648
INT_MAX = 2147483647


def _java_divmod(a, b):
    """(quotient, remainder) using Java integer semantics.

    Java truncates the quotient toward zero and the remainder takes the sign of
    the dividend ``a`` - unlike Python's floor-based ``//`` and ``%``.
    """
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q, a - q * b


# ---------------------------------------------------------------------------
# Helper classes (Java nested classes -> module-level classes)
# ---------------------------------------------------------------------------
class Point:
    """2-D point carrying its Euclidean distance from a reference point.

    Java's ``Point implements Comparable<Point>`` ordered on ``distance``; here
    we expose ``__lt__`` (consumed by :mod:`heapq`) plus an explicit
    ``compare_to`` returning -1/0/1 to mirror ``Comparable.compareTo``.
    """

    def __init__(self, x, y, original=None):
        self.x = x
        self.y = y
        ox = original.x if original is not None else 0
        oy = original.y if original is not None else 0
        # sqrt((x-ox)^2 + (y-oy)^2)
        self.distance = math.hypot(x - ox, y - oy)

    def compare_to(self, that):
        return (self.distance > that.distance) - (self.distance < that.distance)

    def __lt__(self, that):
        return self.distance < that.distance

    def __repr__(self):
        return f"({self.x}, {self.y})"


class NestedInteger:
    """Stand-in for the Java nested ``NestedInteger`` contract.

    The Java original was a stub (``isInteger`` always ``true``, ``getInteger``
    always ``1``).  Here it is made functional so the depth-weighted sum can be
    demonstrated, while keeping the same three-method interface.
    """

    def __init__(self, value=None, items=None):
        self._value = value
        self._items = items

    def is_integer(self):
        return self._items is None

    def get_integer(self):
        return 1 if self._value is None else self._value

    def get_list(self):
        return self._items if self._items is not None else []


class Numbers:
    """Container for the numeric algorithms ported from ``Numbers.java``.

    Java ``static`` methods became ``@staticmethod``; Java instance methods
    remain instance methods.  Streaming-median state lives on the instance.
    """

    def __init__(self):
        # Streaming-median state.  ``max_heap`` stores negated values so that
        # heapq (a min-heap) behaves as a max-heap.
        self.num_of_elements = 0
        self.min_heap = []   # min-heap of the larger half
        self.max_heap = []   # max-heap (negated) of the smaller half

    # ------------------------------------------------------------------
    # Fibonacci
    # ------------------------------------------------------------------
    @staticmethod
    def fib(n):
        """Return a list with a Fibonacci sequence of length ``n``.

        Time O(n), Space O(n).  Returns ``None`` for ``n == 0`` (Java returned
        ``null``).
        """
        if n == 0:
            return None
        if n == 1:
            return [0]
        f = [0] * n
        f[0] = 0
        f[1] = 1
        for i in range(2, n):
            f[i] = f[i - 1] + f[i - 2]
        return f

    @staticmethod
    def fib1(n):
        """nth Fibonacci number.  Time O(n), Space O(1)."""
        a, b = 0, 1
        if n == 0:
            return a
        for _ in range(2, n + 1):
            c = a + b
            a = b
            b = c
        return b

    @staticmethod
    def get_fibonnaci_numbers(given):
        """Largest subsequence of ``given`` whose elements are Fibonacci numbers."""
        output = []
        for x in given:
            nearest_fib = Numbers.get_nth_fibonacci_number(x)
            if x == nearest_fib:
                output.append(x)
        return output

    @staticmethod
    def get_nth_fibonacci_number(given):
        f_n = 1
        f_n_prev = 1
        while f_n < given:
            temp = f_n
            f_n = f_n + f_n_prev
            f_n_prev = temp
        print(f"Neartest to {given} is {f_n}")
        return f_n

    # ------------------------------------------------------------------
    # Factorial
    # ------------------------------------------------------------------
    @staticmethod
    def factorial(n):
        """Return a list of factorials of length ``n``.  Time/Space O(n)."""
        if n == 0:
            return [1]
        result = [0] * n
        result[0] = 1
        for i in range(1, n):
            result[i] = i * result[i - 1]
        return result

    @staticmethod
    def factorial1(n):
        """nth factorial.  Time O(n), Space O(1)."""
        b, c = 1, 1
        if n == 0 or n == 1:
            return b
        for i in range(2, n + 1):
            b = i * c
            c = b
        return b

    # ------------------------------------------------------------------
    # Fast power (Java overloads -> two named methods)
    # ------------------------------------------------------------------
    def power_int(self, x, y):
        """x ** y for integers in O(log n) (y assumed non-negative)."""
        if y == 0:
            return 1
        temp = self.power_int(x, y // 2)
        if y % 2 == 0:
            return temp * temp
        return x * temp * temp

    def power_float(self, x, y):
        """x ** y supporting float ``x`` and negative integer ``y``."""
        if y == 0:
            return 1
        # int(y / 2) truncates toward zero, matching Java integer division.
        temp = self.power_float(x, int(y / 2))
        if y % 2 == 0:
            return temp * temp
        if y > 0:
            return x * temp * temp
        return (temp * temp) / x

    # ------------------------------------------------------------------
    # Roman numerals
    # ------------------------------------------------------------------
    def roman_to_int(self, s):
        romans = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
                  'C': 100, 'D': 500, 'M': 1000}
        int_num = 0
        prev = 0
        for i in range(len(s) - 1, -1, -1):
            temp = romans[s[i]]
            if temp < prev:
                int_num -= temp
            else:
                int_num += temp
            prev = temp
        return int_num

    @staticmethod
    def integer_to_roman_numeral(input_value):
        if input_value < 1 or input_value > 3999:
            return "Invalid Roman Number Value"
        # (value, symbol) pairs in descending order -> compact greedy build.
        table = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
        ]
        s = []
        for value, symbol in table:
            while input_value >= value:
                s.append(symbol)
                input_value -= value
        return "".join(s)

    # ------------------------------------------------------------------
    # K nearest points
    # ------------------------------------------------------------------
    def find_k_nearest_points(self, points, original, k):
        """K nearest points using a heap.  Time O(n log k).

        Faithful port: a min-heap is kept and an incoming point that is closer
        than the current minimum evicts that minimum.
        """
        result = []
        if not points or original is None or k <= 0:
            return result
        pq = []
        for point in points:
            if len(pq) < k:
                heapq.heappush(pq, point)
            else:
                if pq[0].compare_to(point) > 0:
                    heapq.heappop(pq)
                    heapq.heappush(pq, point)
        result.extend(pq)
        return result

    @staticmethod
    def find_k_nearest_points_selection(points, k):
        """K nearest points via selection.  Average O(n), worst O(n^2)."""
        n = len(points)
        dist = [0.0] * n
        for i in range(n):
            dist[i] = math.sqrt(points[i].x * points[i].x +
                                points[i].y * points[i].y)
        kth_min = Numbers.kth_smallest(dist, 0, n - 1, k - 1)
        result = []
        for i in range(n):
            d = math.sqrt(points[i].x * points[i].x +
                          points[i].y * points[i].y)
            if d <= kth_min:
                result.append(points[i])
        return result

    # ------------------------------------------------------------------
    # Median of medians (worst case O(n)) and quickselect helpers
    # ------------------------------------------------------------------
    @staticmethod
    def median_of_medians_select(A, low, high, k):
        if high - low + 1 <= 5:
            # Java Arrays.sort(A, low, high) sorts the [low, high) slice.
            A[low:high] = sorted(A[low:high])
            return A[low + k - 1]
        no_of_groups = (high - low + 1) // 5
        median_array = [0.0] * no_of_groups
        for i in range(no_of_groups):
            median_array[i] = Numbers.median_of_medians_select(
                A, low + i * 5, low + (i * 5) + 4, 3)
        median_of_medians = Numbers.median_of_medians_select(
            median_array, 0, len(median_array) - 1, no_of_groups // 2 + 1)
        pos = Numbers.partition1(A, low, high, median_of_medians)
        if pos - low + 1 == k:
            return A[low + k - 1]
        elif k < pos - low + 1:
            return Numbers.median_of_medians_select(A, low, pos - 1, k)
        else:
            return Numbers.median_of_medians_select(
                A, pos + 1, high, k - (pos - low + 1))

    @staticmethod
    def partition1(G, first, last, pivot):
        i = first
        while i < last:
            if G[i] == pivot:
                break
            i += 1
        Numbers._swap(G, i, last - 1)
        p_index = first
        for i in range(first, last):
            if G[i] < pivot:
                Numbers._swap(G, i, p_index)
                p_index += 1
        Numbers._swap(G, p_index, last - 1)
        return p_index

    @staticmethod
    def kth_smallest(G, first, last, k):
        """kth (0-indexed) smallest element in an unsorted slice."""
        if first <= last:
            pivot = Numbers.random_partition(G, first, last)
            if pivot == k:
                return G[k]
            if pivot > k:
                return Numbers.kth_smallest(G, first, pivot - 1, k)
            return Numbers.kth_smallest(G, pivot + 1, last, k)
        return 0

    @staticmethod
    def random_partition(arr, l, r):
        pivot = int(round(l + random.random() * (r - l)))
        Numbers._swap(arr, pivot, r)
        return Numbers.partition(arr, l, r)

    @staticmethod
    def partition(G, first, last):
        pivot = G[last]
        p_index = first
        for i in range(first, last):
            if G[i] < pivot:
                Numbers._swap(G, i, p_index)
                p_index += 1
        Numbers._swap(G, p_index, last)
        return p_index

    @staticmethod
    def _swap(G, x, y):
        G[x], G[y] = G[y], G[x]

    # ------------------------------------------------------------------
    # Clock angle
    # ------------------------------------------------------------------
    def calc_angle(self, h, m):
        if h < 0 or m < 0 or h > 12 or m > 60:
            print("Wrong input")
        if h == 12:
            h = 0
        if m == 60:
            m = 0
        hour_angle = (h * 60 + m) // 2
        minute_angle = 6 * m
        angle = abs(hour_angle - minute_angle)
        # The smaller of the two possible angles.
        return min(360 - angle, angle)

    # ------------------------------------------------------------------
    # Numeric string test
    # ------------------------------------------------------------------
    @staticmethod
    def is_number(to_test):
        """True iff the whole string is an (optionally signed/decimal) number."""
        return re.fullmatch(r"-?\d+(\.\d+)?", to_test) is not None

    # ------------------------------------------------------------------
    # Depth-weighted nested integer sum
    # ------------------------------------------------------------------
    def get_list_sum(self, lni, depth):
        total = 0
        for ni in lni:
            if ni.is_integer():
                total += ni.get_integer() * depth
            else:
                total += self.get_list_sum(ni.get_list(), depth + 1)
        return total

    def get_sum(self, ni):
        if ni.is_integer():
            return ni.get_integer()
        return self.get_list_sum(ni.get_list(), 1)

    # ------------------------------------------------------------------
    # Integer square root (binary search) - O(log n)
    # ------------------------------------------------------------------
    def sqrt_int(self, num):
        if num < 0:
            return 0
        if num == 1:
            return 1
        low = 0
        high = 1 + (num // 2)
        while low + 1 < high:
            mid = low + (high - low) // 2
            square = mid * mid
            if square == num:
                return mid
            elif square < num:
                low = mid
            else:
                high = mid
        return low

    # ------------------------------------------------------------------
    # The "100 game"
    # ------------------------------------------------------------------
    def can_i_win(self, max_choosable_integer, desired_total):
        numbers = [i + 1 for i in range(max_choosable_integer)]
        return self.can_win(numbers, desired_total, 0)

    def can_win(self, numbers, desired_total, total):
        for value in numbers:
            temp = total + value
            if (desired_total - temp) % 11 == 0:
                total = temp
        return total >= 100

    # ------------------------------------------------------------------
    # Streaming median (two heaps)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 0/1 Knapsack
    # ------------------------------------------------------------------
    def knap_sack(self, W, wt, val, n):
        K = [[0] * (W + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            for j in range(W + 1):
                if i == 0 or j == 0:
                    K[i][j] = 0
                elif wt[i - 1] <= j:
                    K[i][j] = max(val[i - 1] + K[i - 1][j - wt[i - 1]],
                                  K[i - 1][j])
                else:
                    K[i][j] = K[i - 1][j]
        return K[n][W]

    # ------------------------------------------------------------------
    # Division without using '/'
    # ------------------------------------------------------------------
    @staticmethod
    def divide(dividend, divisor):
        if divisor == 0 or (dividend == INT_MIN and divisor == -1):
            return INT_MAX
        sign = -1 if (dividend < 0) ^ (divisor < 0) else 1
        dvd = abs(dividend)
        dvs = abs(divisor)
        res = 0
        while dvs <= dvd:
            temp, mul = dvs, 1
            while dvd >= temp << 1:
                temp <<= 1
                mul <<= 1
            dvd -= temp
            res += mul
        return res if sign == 1 else -res

    def divide1(self, N, D):
        result = 0
        if D == 0:
            print("Cannot divide by 0")
        elif N == 0:
            print(0)
        elif N == D:
            print(1)
        elif N > 0 and D > 0 and N < D:
            print(0)
        else:
            if N < 0 and D < 0:
                while N <= D:
                    N += -1 * D
                    result += 1
                print(result)
            elif N < 0 or D < 0:
                if N < 0:
                    N = -1 * N
                else:
                    D = -1 * D
                while N >= D:
                    N -= D
                    result -= 1
                print(result)
            else:
                while N >= D:
                    N -= D
                    result += 1
                print(result)

    # ------------------------------------------------------------------
    # Nega-binary (base -2) representation
    # ------------------------------------------------------------------
    @staticmethod
    def nega_binary(x):
        sb = []
        while x != 0:
            # Java uses truncated division with a dividend-signed remainder.
            x, rem = _java_divmod(x, -2)
            if rem < 0:
                rem += 2
                x += 1
            sb.append(str(rem))
        return "".join(reversed(sb))

    # ------------------------------------------------------------------
    # Random sampling utilities
    # ------------------------------------------------------------------
    @staticmethod
    def random_sample(items, m):
        """Uniform sample of ``m`` items (returned as a set)."""
        res = set()
        n = len(items)
        for i in range(n - m, n):
            pos = random.randint(0, i)  # nextInt(i+1) -> 0..i inclusive
            item = items[pos]
            if item in res:
                res.add(items[i])
            else:
                res.add(item)
        return res

    @staticmethod
    def reservoir_sample(items, m):
        """Reservoir sample of ``m`` items from a (possibly streaming) iterable."""
        res = []
        count = 0
        for item in items:
            count += 1
            if count <= m:
                res.append(item)
            else:
                r = random.randint(0, count - 1)  # nextInt(count) -> 0..count-1
                if r < m:
                    res[r] = item
        return res

    @staticmethod
    def random_by_weight(input_list, weight_func):
        """Return a value with probability proportional to its weight."""
        total_weight = 0
        selected = input_list[0]
        for data in input_list:
            weight = weight_func[data]
            r = int(random.random() * (total_weight + weight))
            if r >= total_weight:
                selected = data
            total_weight += weight
        return selected

    @staticmethod
    def random_number(weights):
        """Return an index in 0..n-1 with probability proportional to weight.

        NOTE: mutates ``weights`` into its prefix-sum form, exactly like the
        Java original.
        """
        if not weights:
            return 0
        n = len(weights)
        for i in range(1, n):
            weights[i] += weights[i - 1]  # [1,2,4,5,1,3] -> [1,3,7,12,13,16]
        num = random.randint(0, weights[n - 1] - 1)  # 0 .. total-1
        return Numbers.binary_search(weights, 0, n - 1, num)

    @staticmethod
    def binary_search(weights, start, end, target):
        """Leftmost index where ``target <= weights[mid]``."""
        while start < end:
            mid = start + (end - start) // 2
            if target <= weights[mid]:
                end = mid
            else:
                start = mid + 1
        return start

    # ------------------------------------------------------------------
    # Primality
    # ------------------------------------------------------------------
    def is_prime(self, n):
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True

    # ------------------------------------------------------------------
    # Digit re-arrangement puzzles
    # ------------------------------------------------------------------
    @staticmethod
    def biggest_number(number):
        digits = Numbers.number_to_digits(number)
        digits.sort()
        return Numbers.digit_to_number(digits)

    @staticmethod
    def digit_to_number(digits):
        number = 0
        base = 1
        for i in range(len(digits) - 1, -1, -1):
            number += digits[i] * base
            base *= 10
        return number

    @staticmethod
    def number_to_digits(number):
        digits = []
        while number > 0:
            digits.insert(0, number % 10)
            number //= 10
        return digits

    @staticmethod
    def next_greater_number(number):
        digits = Numbers.number_to_digits(number)
        for i in range(len(digits) - 2, -1, -1):
            if digits[i] < digits[i + 1]:
                for j in range(len(digits) - 1, i, -1):
                    if digits[j] > digits[i]:
                        digits[j], digits[i] = digits[i], digits[j]
                        digits[i + 1:] = sorted(digits[i + 1:])
                        return Numbers.digit_to_number(digits)
        return -1

    # ------------------------------------------------------------------
    # Look-and-say
    # ------------------------------------------------------------------
    @staticmethod
    def lookandsay_util(num, n):
        for _ in range(n):
            num = Numbers.lookandsay(num)
        return num

    @staticmethod
    def lookandsay(number):
        result = []
        say = number[0]
        times = 1
        for i in range(1, len(number)):
            actual = number[i]
            if actual != say:
                result.append(str(times) + say)
                times = 1
                say = actual
            else:
                times += 1
        result.append(str(times) + say)
        return "".join(result)

    # ------------------------------------------------------------------
    # String -> integer (atoi) with 32-bit overflow clamping
    # ------------------------------------------------------------------
    @staticmethod
    def atoi(s):
        index = 0
        sign = 1
        total = 0
        if len(s) == 0:
            return 0
        # Skip leading spaces (guard the bound first to avoid IndexError).
        while index < len(s) and s[index] == ' ':
            index += 1
        if index < len(s) and (s[index] == '+' or s[index] == '-'):
            sign = 1 if s[index] == '+' else -1
            index += 1
        while index < len(s):
            digit = ord(s[index]) - ord('0')
            if digit < 0 or digit > 9:
                break
            # Clamp on 32-bit overflow, mirroring the Java reference.
            if (INT_MAX // 10 < total or
                    (INT_MAX // 10 == total and INT_MAX % 10 < digit)):
                return INT_MAX if sign == 1 else INT_MIN
            total = 10 * total + digit
            index += 1
        return total * sign

    # ------------------------------------------------------------------
    # Factors of a number
    # ------------------------------------------------------------------
    @staticmethod
    def find_factors(num):
        for i in range(1, int(math.sqrt(num)) + 1):
            if num % i == 0:
                print(i)
                if i != num // i:
                    print(num // i)


if __name__ == "__main__":
    nums = Numbers()

    # Primary behaviour from the Java main: look-and-say starting at "1", 4 iters.
    print(Numbers.lookandsay_util("1", 4))          # 111221

    # --- Extra deterministic demonstrations -------------------------------
    print("fib(10):", Numbers.fib(10))
    print("fib1(10):", Numbers.fib1(10))
    print("factorial(7):", Numbers.factorial(7))
    print("factorial1(6):", Numbers.factorial1(6))
    print("power_int(2, 10):", nums.power_int(2, 10))
    print("power_float(2.0, -3):", round(nums.power_float(2.0, -3), 5))
    print("roman_to_int('MCMXCIV'):", nums.roman_to_int("MCMXCIV"))
    print("integer_to_roman_numeral(1994):", Numbers.integer_to_roman_numeral(1994))
    print("calc_angle(3, 30):", nums.calc_angle(3, 30))
    print("is_number('-12.34'):", Numbers.is_number("-12.34"))
    print("is_number('12a'):", Numbers.is_number("12a"))
    print("sqrt_int(50):", nums.sqrt_int(50))
    print("is_prime(17):", nums.is_prime(17))
    print("can_i_win(10, 100):", nums.can_i_win(10, 100))
    print("knap_sack:", nums.knap_sack(50, [10, 20, 30], [60, 100, 120], 3))
    print("divide(43, 5):", Numbers.divide(43, 5))
    print("divide(-22, 4):", Numbers.divide(-22, 4))
    print("nega_binary(15):", Numbers.nega_binary(15))
    print("biggest_number(4271):", Numbers.biggest_number(4271))
    print("next_greater_number(12543):", Numbers.next_greater_number(12543))
    print("atoi('  -2147483648'):", Numbers.atoi("  -2147483648"))
    print("atoi('99999999999'):", Numbers.atoi("99999999999"))  # overflow clamp

    # Streaming median.
    for n in [5, 15, 1, 3, 8, 7, 9, 10, 20, 12]:
        nums.add_number_to_stream(n)
    print("streaming median:", nums.get_median())

    # k-nearest points (heap + selection algorithm).
    origin = Point(0, 0)
    pts = [Point(0, 1, origin), Point(0, 2, origin), Point(0, 3, origin),
           Point(0, 4, origin), Point(0, 5, origin)]
    print("find_k_nearest_points k=3:", nums.find_k_nearest_points(pts, origin, 3))
    sel_pts = [Point(0, 1), Point(0, 2), Point(0, 3), Point(0, 4), Point(0, 5)]
    print("find_k_nearest_points_selection k=3:",
          Numbers.find_k_nearest_points_selection(sel_pts, 3))

    # Quickselect on a copy (3rd smallest, 0-indexed k=2).
    data = [7.0, 2.0, 5.0, 1.0, 9.0, 3.0]
    print("kth_smallest(k=2):", Numbers.kth_smallest(list(data), 0, len(data) - 1, 2))

    # Nested-integer depth-weighted sum: {{1,1},2,{1,1}} -> 10
    nested = NestedInteger(items=[
        NestedInteger(items=[NestedInteger(1), NestedInteger(1)]),
        NestedInteger(2),
        NestedInteger(items=[NestedInteger(1), NestedInteger(1)]),
    ])
    print("get_sum(nested {{1,1},2,{1,1}}):", nums.get_sum(nested))

    # Weighted random helpers (seeded for determinism).
    random.seed(0)
    print("random_by_weight:", Numbers.random_by_weight(
        ["a", "b", "c"], {"a": 1, "b": 5, "c": 2}))
    print("random_number (index):", Numbers.random_number([1, 2, 4, 5, 1, 3]))
    print("reservoir_sample(range(20), 5):",
          sorted(Numbers.reservoir_sample(range(20), 5)))

    # divide1 prints its result directly.
    print("divide1(20, 4):", end=" ")
    nums.divide1(20, 4)

    # find_factors prints each divisor of 36.
    print("find_factors(36):")
    Numbers.find_factors(36)
