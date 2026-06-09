"""
matrix.py

Idiomatic Python 3 port of java/Matrix.java (original package code.ds).
A collection of 2D-matrix interview problems (islands, region sums, rotations,
search, spirals, mazes, paint-house DP, sparse multiply, etc.).

Notes
-----
* The Java ``Matrix`` class becomes the Python ``Matrix`` class. ``static``
  methods become ``@staticmethod`` (calling one another via ``Matrix.<name>``);
  instance methods keep ``self``. The two ``int x[]`` / ``int y[]`` direction
  fields used by ``search_2d`` are initialised in ``__init__``.
* ``java.awt.Point`` -> the small ``Point`` class below; ``Queue`` ->
  ``collections.deque``; ``Stack`` -> ``list``.
* Java overloads were renamed:
    - ``minCost(cost, m, n)`` (static DP) -> ``min_cost_path``
    - ``minCost(costs)``       (paint house) -> ``min_cost``
    - ``minCostII(costs)``                   -> ``min_cost_ii``
    - ``helper`` (searchMatrix) -> ``_search_matrix_helper``
    - ``zeroHelper``            -> ``_zero_helper``
    - ``kadane``                -> ``_kadane``
* ``main`` originally built an unused array and called ``printMatrix(5000)``;
  the unused array is dropped and the demo uses ``print_matrix(24)`` so the
  output matches the documented 5x5 spiral example.
"""

import math
import random
from collections import deque

INT_MAX = 2147483647  # Integer.MAX_VALUE


class Point:
    """Minimal stand-in for java.awt.Point."""

    def __init__(self, x, y):
        self.x = x
        self.y = y


class KadaneResult:
    """Result of a 1D max-subarray (Kadane) pass."""

    def __init__(self, max_sum, start, end):
        self.max_sum = max_sum
        self.start = start
        self.end = end


class Matrix:

    # Java static final fields
    ROW = 18
    COL = 20
    M = 4
    N = 4
    EMPTY = INT_MAX          # an empty room (Walls and Gates)
    GATE = 0                 # a gate
    DIRECTIONS = [[1, 0], [-1, 0], [0, 1], [0, -1]]

    def __init__(self):
        # For searching in all 8 directions (used by search_2d / pattern_search)
        self.x = [-1, -1, -1, 0, 0, 1, 1, 1]
        self.y = [-1, 0, 1, -1, 1, -1, 0, 1]

    # Find the number of islands in a boolean 2D matrix. Time O(ROW x COL).
    @staticmethod
    def num_islands(grid):
        row = len(grid)
        if row == 0:
            return 0
        col = len(grid[0])
        count = 0
        mark = [[False] * col for _ in range(row)]
        q = deque()
        for i in range(row):
            for j in range(col):
                if grid[i][j] == 1 and not mark[i][j]:
                    q.append(Point(i, j))
                    mark[i][j] = True
                    while q:
                        temp = q.popleft()
                        x = temp.x
                        y = temp.y
                        if x + 1 < row and grid[x + 1][y] == 1 and not mark[x + 1][y]:
                            q.append(Point(x + 1, y))
                            mark[x + 1][y] = True
                        if y + 1 < col and grid[x][y + 1] == 1 and not mark[x][y + 1]:
                            q.append(Point(x, y + 1))
                            mark[x][y + 1] = True
                        if x - 1 >= 0 and grid[x - 1][y] == 1 and not mark[x - 1][y]:
                            q.append(Point(x - 1, y))
                            mark[x - 1][y] = True
                        if y - 1 >= 0 and grid[x][y - 1] == 1 and not mark[x][y - 1]:
                            q.append(Point(x, y - 1))
                            mark[x][y - 1] = True
                    count += 1
        return count

    # Preprocess mat[M][N] -> aux[i][j] holds the sum from (0,0) to (i,j). O(MN)
    def pre_process(self, mat, aux, m, n):
        for i in range(n):
            aux[0][i] = mat[0][i]
        for i in range(1, m):
            for j in range(n):
                aux[i][j] = mat[i][j] + aux[i - 1][j]
        for i in range(m):
            for j in range(1, n):
                aux[i][j] += aux[i][j - 1]

    # O(1) sum of submatrix between (tli, tlj) and (rbi, rbj) using aux[][].
    def sum_query(self, aux, tli, tlj, rbi, rbj):
        res = aux[rbi][rbj]
        if tli > 0:
            res = res - aux[tli - 1][rbj]
        if tlj > 0:
            res = res - aux[rbi][tlj - 1]
        if tli > 0 and tlj > 0:
            res = res + aux[tli - 1][tlj - 1]
        return res

    # Number of paths from (0,0) to (m,n) moving only horizontally/vertically.
    def number_of_paths(self, m, n):
        count = [[0] * n for _ in range(m)]
        for i in range(m):
            count[i][0] = 1
        for j in range(n):
            count[0][j] = 1
        for i in range(1, m):
            for j in range(1, n):
                count[i][j] = count[i - 1][j] + count[i][j - 1]
        return count[m - 1][n - 1]

    # Rotate an NxN image by 90 degrees clockwise, in place. O(n^2), O(1).
    @staticmethod
    def rotate(matrix, n):
        for layer in range(n // 2):
            first = layer
            last = n - 1 - layer
            for i in range(first, last):
                offset = i - first
                top = matrix[first][i]  # save top
                # left -> top
                matrix[first][i] = matrix[last - offset][first]
                # bottom -> left
                matrix[last - offset][first] = matrix[last][last - offset]
                # right -> bottom
                matrix[last][last - offset] = matrix[i][last]
                # top -> right
                matrix[i][last] = top

    # If an element in an MxN matrix is 0, set its entire row and column to 0.
    def set_zeroes(self, matrix):
        first_row_zero = False
        first_column_zero = False
        for i in range(len(matrix)):
            if matrix[i][0] == 0:
                first_column_zero = True
                break
        for i in range(len(matrix[0])):
            if matrix[0][i] == 0:
                first_row_zero = True
                break
        for i in range(1, len(matrix)):
            for j in range(1, len(matrix[0])):
                if matrix[i][j] == 0:
                    matrix[i][0] = 0
                    matrix[0][j] = 0
        for i in range(1, len(matrix)):
            for j in range(1, len(matrix[0])):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
        if first_column_zero:
            for i in range(len(matrix)):
                matrix[i][0] = 0
        if first_row_zero:
            for i in range(len(matrix[0])):
                matrix[0][i] = 0

    # Count zeros in a row-wise and column-wise sorted matrix.
    @staticmethod
    def count_num_zeroes(matrix):
        row = len(matrix) - 1
        col = 0
        num_zeroes = 0
        while col < len(matrix[0]):
            while matrix[row][col] != 0:
                row -= 1
                if row < 0:
                    return num_zeroes
            num_zeroes += row + 1
            col += 1
        return num_zeroes

    @staticmethod
    def count_zero(matrix):
        if matrix is None or len(matrix) == 0 or len(matrix[0]) == 0:
            return 0
        m = len(matrix)
        n = len(matrix[0])
        count = 0
        return Matrix._zero_helper(matrix, 0, m - 1, 0, n - 1, count)

    @staticmethod
    def _zero_helper(matrix, row_start, row_end, col_start, col_end, count):
        if row_start > row_end or col_start > col_end:
            return count
        row_mid = row_start + (row_end - row_start) // 2
        col_mid = col_start + (col_end - col_start) // 2
        if matrix[row_mid][col_mid] == 1:
            return (Matrix._zero_helper(matrix, row_start, row_mid - 1, col_start, col_mid - 1, count) +
                    Matrix._zero_helper(matrix, row_mid, row_end, col_start, col_mid - 1, count) +
                    Matrix._zero_helper(matrix, row_start, row_mid - 1, col_mid, col_end, count))
        elif matrix[row_end][col_end] == 0:
            count += (row_end - row_start + 1) * (col_end - col_start + 1)
        else:
            count += 1
        return count

    # Find an element in a row- and column-sorted matrix. O(m + n).
    @staticmethod
    def find_element(matrix, elem):
        row = 0
        col = len(matrix[0]) - 1
        while row < len(matrix) and col >= 0:
            if matrix[row][col] == elem:
                return True
            elif matrix[row][col] > elem:
                col -= 1
            else:
                row += 1
        return False

    # Quadrant-elimination search of a sorted matrix.
    def search_matrix(self, matrix, target):
        if matrix is None or len(matrix) == 0 or len(matrix[0]) == 0:
            return False
        m = len(matrix)
        n = len(matrix[0])
        return self._search_matrix_helper(matrix, 0, m - 1, 0, n - 1, target)

    def _search_matrix_helper(self, matrix, row_start, row_end, col_start, col_end, target):
        if row_start > row_end or col_start > col_end:
            return False
        row_mid = row_start + (row_end - row_start) // 2
        col_mid = col_start + (col_end - col_start) // 2
        if matrix[row_mid][col_mid] == target:
            return True
        if matrix[row_mid][col_mid] > target:
            return (self._search_matrix_helper(matrix, row_start, row_mid - 1, col_start, col_mid - 1, target) or
                    self._search_matrix_helper(matrix, row_mid, row_end, col_start, col_mid - 1, target) or
                    self._search_matrix_helper(matrix, row_start, row_mid - 1, col_mid, col_end, target))
        else:
            return (self._search_matrix_helper(matrix, row_mid + 1, row_end, col_mid + 1, col_end, target) or
                    self._search_matrix_helper(matrix, row_mid + 1, row_end, col_start, col_mid, target) or
                    self._search_matrix_helper(matrix, row_start, row_mid, col_mid + 1, col_end, target))

    # Search a matrix where each row is sorted and first of each row > last of
    # the previous row.
    def search_matrix1(self, matrix, target):
        if matrix is None or len(matrix) == 0:
            return False
        m = len(matrix)
        n = len(matrix[0])
        # Step 1: find the rowId of the target number
        lo = 0
        hi = m - 1
        while lo + 1 < hi:
            mid = lo + (hi - lo) // 2
            if matrix[mid][0] == target:
                return True
            elif matrix[mid][0] < target:
                lo = mid
            else:
                hi = mid - 1
        if matrix[hi][0] == target or matrix[lo][0] == target:
            return True
        if target > matrix[lo][0] and target <= matrix[lo][n - 1]:
            row_id = lo
        else:
            row_id = hi
        # Step 2: find the target number in row_id
        lo = 0
        hi = n - 1
        while lo + 1 < hi:
            mid = lo + (hi - lo) // 2
            if matrix[row_id][mid] == target:
                return True
            elif matrix[row_id][mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        if matrix[row_id][hi] == target or matrix[row_id][lo] == target:
            return True
        return False

    # Print a 2D matrix in spiral order.
    @staticmethod
    def spiral_print(matrix):
        if matrix is None or len(matrix) == 0 or len(matrix[0]) == 0:
            return
        left = 0
        right = len(matrix[0]) - 1
        up = 0
        down = len(matrix) - 1
        while left < right and up < down:
            for i in range(left, right + 1):
                print(str(matrix[up][i]) + " ", end="")
            up += 1
            for i in range(up, down + 1):
                print(str(matrix[i][right]) + " ", end="")
            right -= 1
            for i in range(right, left - 1, -1):
                print(str(matrix[down][i]) + " ", end="")
            down -= 1
            for i in range(down, up - 1, -1):
                print(str(matrix[i][left]) + " ", end="")
            left += 1

    # Print integers 0..n in a spiral layout, e.g. n = 24 produces a 5x5 grid.
    @staticmethod
    def print_matrix(n):
        sqrt = math.sqrt(n + 1)
        k = int(sqrt)
        if math.pow(sqrt, 2) != math.pow(k, 2):
            k += 1
        result = [[None] * k for _ in range(k)]
        top, bottom, left, right = 0, k - 1, 0, k - 1
        m = k * k
        flag = False
        while n >= 0:
            for i in range(right, left - 1, -1):
                if not flag and n + 1 < m:
                    m -= 1
                    continue
                flag = True
                result[top][i] = n
                n -= 1
            top += 1
            for i in range(top, bottom + 1):
                if not flag and n + 1 < m:
                    m -= 1
                    continue
                flag = True
                result[i][left] = n
                n -= 1
            left += 1
            for i in range(left, right + 1):
                if not flag and n + 1 < m:
                    m -= 1
                    continue
                flag = True
                result[bottom][i] = n
                n -= 1
            bottom -= 1
            for i in range(bottom, top - 1, -1):
                if not flag and n + 1 < m:
                    m -= 1
                    continue
                flag = True
                result[i][right] = n
                n -= 1
            right -= 1
        for i in range(k):
            for j in range(k):
                if result[i][j] is not None:
                    print(str(result[i][j]) + " ", end="")
            print()

    # Print matrix diagonally (bottom-left triangle then top-right triangle).
    @staticmethod
    def print_mat(mat):
        if mat is None or len(mat) == 0:
            return
        left = 0
        up = 0
        down = len(mat) - 1
        right = len(mat[0]) - 1
        for i in range(down, -1, -1):
            x = i
            y = left
            while x <= down and y <= down:
                print(str(mat[x][y]) + " ", end="")
                x += 1
                y += 1
            print()
        left += 1
        for i in range(left, right + 1):
            x = up
            y = i
            while x <= right and y <= right:
                print(str(mat[x][y]) + " ", end="")
                x += 1
                y += 1
            print()

    # Shift each element of an NxN matrix one position along concentric rings.
    def rotate_matrix(self, mat):
        up = 0
        left = 0
        right = len(mat[0]) - 1
        down = len(mat) - 1
        while up < down and left < right:
            if up + 1 == down or left + 1 == right:
                break
            prev = mat[up + 1][left]
            for i in range(left, right):
                curr = mat[up][i]
                mat[up][i] = prev
                prev = curr
            up += 1
            for i in range(up, down):
                curr = mat[i][right - 1]
                mat[i][right - 1] = prev
                prev = curr
            right -= 1
            if up < down:
                for i in range(right - 1, left - 1, -1):
                    curr = mat[down - 1][i]
                    mat[down - 1][i] = prev
                    prev = curr
            down -= 1
            if left < right:
                for i in range(down - 1, up - 1, -1):
                    curr = mat[i][left]
                    mat[i][left] = prev
                    prev = curr
            left += 1
        for i in range(len(mat)):
            for j in range(len(mat[0])):
                print(str(mat[i][j]) + " ", end="")
            print()

    # Find all occurrences of a word in a char grid (8 directions).
    def pattern_search(self, grid, word):
        r = len(grid)
        c = len(grid[0])
        for row in range(r):
            for col in range(c):
                if self.search_2d(grid, row, col, word):
                    print("pattern found at " + str(row) + ", " + str(col), end="")

    def search_2d(self, grid, row, col, word):
        r = len(grid)
        c = len(grid[0])
        if grid[row][col] != word[0]:
            return False
        length = len(word)
        for dir in range(8):
            k = 1
            rd = row + self.x[dir]
            cd = col + self.y[dir]
            while k < length:
                if rd >= r or rd < 0 or cd >= c or cd < 0:
                    break
                if grid[rd][cd] != word[k]:
                    break
                rd += self.x[dir]
                cd += self.y[dir]
                k += 1
            if k == length:
                return True
        return False

    # Largest rectangle of all 1s in a 0/1 matrix.
    def maximum(self, input_mat):
        temp = [0] * len(input_mat[0])
        max_area = 0
        for i in range(len(input_mat)):
            for j in range(len(temp)):
                if input_mat[i][j] == 0:
                    temp[j] = 0
                else:
                    temp[j] += input_mat[i][j]
            area = Matrix.largest_rectangle_area(temp)
            if area > max_area:
                max_area = area
        return max_area

    # Largest rectangle area in a histogram. input [2,1,5,6,2,3] -> 10
    @staticmethod
    def largest_rectangle_area(height):
        stack = []
        max_area = 0
        for i in range(len(height) + 1):
            height_bound = 0 if i == len(height) else height[i]
            while stack:
                h = height[stack[-1]]
                if h < height_bound:
                    break
                stack.pop()
                index = -1 if not stack else i - 1 - stack[-1]
                max_area = max(max_area, h * index)
            stack.append(i)
        return max_area

    # Maximum-sum rectangle in a 2D matrix (temp array + Kadane).
    # Time O(row*col*col), space O(row).
    def max_sum(self, input_mat):
        max_sum_val = 0
        left_bound = 0
        right_bound = 0
        up_bound = 0
        low_bound = 0
        rows = len(input_mat)
        cols = len(input_mat[0])
        temp = [0] * rows
        for left in range(cols):
            for i in range(rows):
                temp[i] = 0
            for right in range(left, cols):
                for i in range(rows):
                    temp[i] += input_mat[i][right]
                kadane_result = self._kadane(temp)
                if kadane_result.max_sum > max_sum_val:
                    max_sum_val = kadane_result.max_sum
                    left_bound = left
                    right_bound = right
                    up_bound = kadane_result.start
                    low_bound = kadane_result.end
        print("Result [maxSum=" + str(max_sum_val) + ", leftBound=" + str(left_bound) +
              ", rightBound=" + str(right_bound) + ", upBound=" + str(up_bound) +
              ", lowBound=" + str(low_bound) + "]", end="")

    # 1D max-subarray (Kadane) returning sum and [start, end].
    def _kadane(self, arr):
        max_val = 0
        max_start = -1
        max_end = -1
        current_start = 0
        max_so_far = 0
        for i in range(len(arr)):
            max_so_far += arr[i]
            if max_so_far < 0:
                max_so_far = 0
                current_start = i + 1
            if max_val < max_so_far:
                max_start = current_start
                max_end = i
                max_val = max_so_far
        return KadaneResult(max_val, max_start, max_end)

    # Flood-fill the ocean (BFS), changing target cells to replace.
    @staticmethod
    def flood_fill(m, x, y, target, replace):
        if m[x][y] == replace:
            return None  # current is same as replacement
        q = deque()
        q.append(Point(x, y))
        while q:
            temp = q.popleft()
            x = temp.x
            y = temp.y
            if m[x][y] != replace and m[x][y] == target:
                m[x][y] = replace
                if y < len(m[x]) - 1:
                    q.append(Point(x, y + 1))
                if y > 0:
                    q.append(Point(x, y - 1))
                if x < len(m) - 1:
                    q.append(Point(x + 1, y))
                if x > 0:
                    q.append(Point(x - 1, y))
        return m

    # Is (x, y) a valid open cell of an MxN maze?
    def is_safe(self, maze, x, y):
        return 0 <= x < Matrix.M and 0 <= y < Matrix.N and maze[x][y] == 1

    # Shortest path length in a 0/1 maze (BFS) from (0,0) to bottom-right.
    @staticmethod
    def get_shortest_path_length(maze):
        if maze is None or len(maze) == 0:
            return 0
        queue = deque()
        visited = [[False] * len(maze[0]) for _ in range(len(maze))]
        queue.append(Point(0, 0))
        level = 0
        while len(queue) > 0:
            count = len(queue)
            while count > 0:
                count -= 1
                pt = queue.popleft()
                if pt.x == len(maze) - 1 and pt.y == len(maze[0]) - 1:
                    return level
                visited[pt.x][pt.y] = True
                if pt.x - 1 >= 0 and maze[pt.x - 1][pt.y] == 0 and not visited[pt.x - 1][pt.y]:
                    queue.append(Point(pt.x - 1, pt.y))
                if pt.x + 1 < len(maze) and not visited[pt.x + 1][pt.y] and maze[pt.x + 1][pt.y] == 0:
                    queue.append(Point(pt.x + 1, pt.y))
                if pt.y - 1 >= 0 and not visited[pt.x][pt.y - 1] and maze[pt.x][pt.y - 1] == 0:
                    queue.append(Point(pt.x, pt.y - 1))
                if pt.y + 1 < len(maze[0]) and not visited[pt.x][pt.y + 1] and maze[pt.x][pt.y + 1] == 0:
                    queue.append(Point(pt.x, pt.y + 1))
            level += 1
        return -1

    # Count all paths in a maze (DP). Blocked cells are 0.
    @staticmethod
    def count_all_maze_path_dp(maze):
        result = maze  # aliases maze (as in the original)
        for i in range(1, len(result)):
            for j in range(1, len(result)):
                if result[i][j] != 0:
                    result[i][j] = 0
                    if result[i - 1][j] > 0:
                        result[i][j] += result[i - 1][j]
                    if result[i][j - 1] > 0:
                        result[i][j] += result[i][j - 1]
        return result[len(maze) - 1][len(maze) - 1]

    # A matrix is Toeplitz if each descending diagonal is constant.
    @staticmethod
    def is_toepliz(mat):
        for i in range(Matrix.M):
            if not Matrix.check_diagonal(mat, 0, i):
                return False
        for i in range(1, Matrix.N):
            if not Matrix.check_diagonal(mat, i, 0):
                return False
        return True

    @staticmethod
    def check_diagonal(mat, i, j):
        res = mat[i][j]
        i += 1
        j += 1
        while i < Matrix.N and j < Matrix.M:
            if mat[i][j] != res:
                return False
            i += 1
            j += 1
        return True

    # Sort a 2D matrix so every row and column is ascending (flatten + sort).
    @staticmethod
    def sort_matrix(a):
        row_count = len(a)
        col_count = len(a[0])
        temp = [0] * (row_count * col_count)
        for r in range(row_count):
            for c in range(col_count):
                temp[r * col_count + c] = a[r][c]
        temp.sort()
        for r in range(row_count):
            k = 0
            for c in range(col_count):
                a[r][c] = temp[r + 2 * k]
                k += 1
        return a

    # Check if a Sudoku board (chars) is valid.
    @staticmethod
    def is_valid_sudoku(board):
        if board is None or len(board) != 9 or len(board[0]) != 9:
            return False
        rows = set()
        cols = set()
        cubes = set()
        for i in range(len(board)):
            for j in range(len(board[0])):
                current = board[i][j]
                if current.isdigit():
                    cube = 3 * (i // 3) + (j // 3)
                    added_row = ord(current) not in rows
                    rows.add(ord(current))
                    added_col = ord(current) not in cols
                    cols.add(ord(current))
                    added_cube = cube not in cubes
                    cubes.add(cube)
                    if not added_row or not added_col or not added_cube:
                        return False
                elif not current.isspace():
                    return False
        return True

    # Min-cost path DP from (0,0) to (m,n). (was static minCost(cost,m,n))
    @staticmethod
    def min_cost_path(cost, m, n):
        tc = [[0] * (n + 1) for _ in range(m + 1)]
        tc[0][0] = cost[0][0]
        for i in range(1, m + 1):
            tc[i][0] = tc[i - 1][0] + cost[i][0]
        for j in range(1, n + 1):
            tc[0][j] = tc[0][j - 1] + cost[0][j]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                tc[i][j] = min(min(tc[i - 1][j - 1], tc[i - 1][j]), tc[i][j - 1]) + cost[i][j]
        return tc[m][n]

    # Multiply two matrices A x B. O(N^3) with a zero-skip optimisation.
    @staticmethod
    def multiply(a, b):
        if a is None or b is None:
            return [[]]
        result = [[0] * len(b[0]) for _ in range(len(a))]
        for i in range(len(a)):
            for k in range(len(a[0])):
                if a[i][k] != 0:
                    for j in range(len(b[0])):
                        if b[k][j] != 0:
                            result[i][j] += a[i][k] * b[k][j]
        return result

    # Sparse matrix multiply storing only nonzero (col, value) pairs of A.
    @staticmethod
    def multiply_sparse(a, b):
        m = len(a)
        n = len(a[0])
        n_b = len(b[0])
        result = [[0] * n_b for _ in range(m)]
        index_a = [None] * m
        for i in range(m):
            nums_a = []
            for j in range(n):
                if a[i][j] != 0:
                    nums_a.append(j)
                    nums_a.append(a[i][j])
            index_a[i] = nums_a
        for i in range(m):
            nums_a = index_a[i]
            p = 0
            while p < len(nums_a) - 1:
                col_a = nums_a[p]
                val_a = nums_a[p + 1]
                for j in range(n_b):
                    val_b = b[col_a][j]
                    result[i][j] += val_a * val_b
                p += 2
        return result

    # Minesweeper: place ``count`` bombs in an h x w field (reservoir sampling).
    def put_bomb(self, h, w, count):
        bomb_locs = [0] * count
        for i in range(count):
            bomb_locs[i] = i
        for i in range(count, h * w):
            j = random.randint(0, i)
            if j < count:
                bomb_locs[j] = i
        res = [[0] * w for _ in range(h)]
        for i in range(len(bomb_locs)):
            x = bomb_locs[i] // w
            y = bomb_locs[i] % w
            res[x][y] = 1
        return res

    # Walls and Gates: fill each empty room with distance to its nearest gate.
    def walls_and_gates(self, rooms):
        m = len(rooms)
        if m == 0:
            return
        n = len(rooms[0])
        q = deque()
        for row in range(m):
            for col in range(n):
                if rooms[row][col] == Matrix.GATE:
                    q.append([row, col])
        while q:
            point = q.popleft()
            row = point[0]
            col = point[1]
            for direction in Matrix.DIRECTIONS:
                r = row + direction[0]
                c = col + direction[1]
                if r < 0 or c < 0 or r >= m or c >= n or rooms[r][c] != Matrix.EMPTY:
                    continue
                rooms[r][c] = rooms[row][col] + 1
                q.append([r, c])

    # Paint House (3 colors): min cost so no two adjacent houses share a color.
    def min_cost(self, costs):
        if costs is None or len(costs) == 0:
            return 0
        for i in range(1, len(costs)):
            costs[i][0] += min(costs[i - 1][1], costs[i - 1][2])
            costs[i][1] += min(costs[i - 1][0], costs[i - 1][2])
            costs[i][2] += min(costs[i - 1][0], costs[i - 1][1])
        m = len(costs) - 1
        return min(min(costs[m][0], costs[m][1]), costs[m][2])

    # Paint House II (k colors): min cost using 1st/2nd smallest tracking.
    def min_cost_ii(self, costs):
        if costs is None or len(costs) == 0:
            return 0
        n = len(costs)
        k = len(costs[0])
        min1 = -1
        min2 = -1
        for i in range(n):
            last1 = min1
            last2 = min2
            min1 = -1
            min2 = -1
            for j in range(k):
                if j != last1:
                    costs[i][j] += 0 if last1 < 0 else costs[i - 1][last1]
                else:
                    costs[i][j] += 0 if last2 < 0 else costs[i - 1][last2]
                if min1 < 0 or costs[i][j] < costs[i][min1]:
                    min2 = min1
                    min1 = j
                elif min2 < 0 or costs[i][j] < costs[i][min2]:
                    min2 = j
        return costs[n - 1][min1]

    # Is the graph (adjacency lists) bipartite? BFS 2-coloring.
    def is_bipartite(self, g):
        colors = [0] * len(g)
        for i in range(len(g)):
            if colors[i] == 0:
                q = deque()
                q.append(i)
                colors[i] = 1
                while q:
                    node = q.popleft()
                    for adjacent in g[node]:
                        if colors[adjacent] == colors[node]:
                            return False
                        elif colors[adjacent] == 0:
                            q.append(adjacent)
                            colors[adjacent] = -colors[node]
        return True


if __name__ == "__main__":
    # Original main built an unused array and called printMatrix(5000); the
    # demo prints 0..24 in a spiral (the documented 5x5 example).
    Matrix.print_matrix(24)
