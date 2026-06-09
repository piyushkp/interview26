"""Disjoint set (union-find) and problems solved with it.

Idiomatic Python 3 port of java/DisjointUnionSets.java (original package code.ds).
"""


class DisjointUnionSets:
    def __init__(self, n):
        self.n = n
        self.rank = [0] * n
        self.parent = [0] * n
        self.make_set()

    # Create n sets, each containing a single item.
    def make_set(self):
        for i in range(self.n):
            self.parent[i] = i

    # Return the representative of x's set (with path compression).
    def find(self, x):
        if self.parent[x] != x:
            # x is not the representative of its set, so recurse on its parent
            # and hook x directly under the representative.
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    # Unite the set containing x with the set containing y (union by rank).
    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root == y_root:
            return  # already in the same set
        if self.rank[x_root] < self.rank[y_root]:
            self.parent[x_root] = y_root
        elif self.rank[y_root] < self.rank[x_root]:
            self.parent[y_root] = x_root
        else:  # equal ranks: attach y under x and bump x's rank
            self.parent[y_root] = x_root
            self.rank[x_root] += 1

    # Count the number of islands in a 0/1 grid (8-connectivity).
    @staticmethod
    def count_islands(a):
        n = len(a)
        m = len(a[0])
        dus = DisjointUnionSets(n * m)

        # For each cell that is 1, union it with any neighbour that is also 1.
        for j in range(n):
            for k in range(m):
                if a[j][k] == 0:
                    continue
                if j + 1 < n and a[j + 1][k] == 1:
                    dus.union(j * m + k, (j + 1) * m + k)
                if j - 1 >= 0 and a[j - 1][k] == 1:
                    dus.union(j * m + k, (j - 1) * m + k)
                if k + 1 < m and a[j][k + 1] == 1:
                    dus.union(j * m + k, j * m + k + 1)
                if k - 1 >= 0 and a[j][k - 1] == 1:
                    dus.union(j * m + k, j * m + k - 1)
                if j + 1 < n and k + 1 < m and a[j + 1][k + 1] == 1:
                    dus.union(j * m + k, (j + 1) * m + k + 1)
                if j + 1 < n and k - 1 >= 0 and a[j + 1][k - 1] == 1:
                    dus.union(j * m + k, (j + 1) * m + k - 1)
                if j - 1 >= 0 and k + 1 < m and a[j - 1][k + 1] == 1:
                    dus.union(j * m + k, (j - 1) * m + k + 1)
                if j - 1 >= 0 and k - 1 >= 0 and a[j - 1][k - 1] == 1:
                    dus.union(j * m + k, (j - 1) * m + k - 1)

        c = [0] * (n * m)  # frequency of each set representative
        number_of_islands = 0
        for j in range(n):
            for k in range(m):
                if a[j][k] == 1:
                    x = dus.find(j * m + k)
                    if c[x] == 0:
                        number_of_islands += 1
                    c[x] += 1
        return number_of_islands

    # Given stacks of services, find which stacks can be deployed disjointly
    # (share no service in common).
    @staticmethod
    def get_stacks(input_, n):
        result = []
        seen = set()
        dus = DisjointUnionSets(n)
        dus.union(0, 1)
        dus.union(1, 2)
        dus.union(2, 0)
        for i in range(len(input_)):
            key_i = "Stack " + str(i + 1)
            if key_i not in seen:
                temp = [key_i]
                seen.add(key_i)
                for j in range(i + 1, len(input_)):
                    if dus.find(input_[i][0]) == dus.find(input_[j][0]):
                        key_j = "Stack " + str(j + 1)
                        temp.append(key_j)
                        seen.add(key_j)
                result.append(temp)
        return result

    # Bloomberg: number of friend circles in a char matrix ('x' marks a relation).
    @staticmethod
    def find_friend_circles(mat):
        m = len(mat)
        n = len(mat[0])
        seen = set()
        dus = DisjointUnionSets(m * n)
        for i in range(m):
            for j in range(n):
                if mat[i][j] == 'x':
                    dus.union(i, j)
        for i in range(m):
            seen.add(dus.find(i))
        return len(seen)

    # DFS-based count of friend circles in an adjacency matrix.
    def find_circle_num(self, M):
        visited = [False] * len(M)  # visited[i]: is person i already counted
        count = 0
        for i in range(len(M)):
            if not visited[i]:
                self._dfs(M, visited, i)
                count += 1
        return count

    def _dfs(self, M, visited, person):
        for other in range(len(M)):
            if M[person][other] == 1 and not visited[other]:
                # Found an unvisited person in the current friend cycle.
                visited[other] = True
                self._dfs(M, visited, other)


if __name__ == "__main__":
    input_ = [[0, 1], [1, 2], [2, 1]]
    out = DisjointUnionSets.get_stacks(input_, 3)
    print("getStacks:", out)

    mat = [
        ['x', '.', '.', 'x'],
        ['.', 'x', '.', '.'],
        ['.', '.', 'x', 'x'],
        ['x', '.', 'x', 'x'],
    ]
    print("findFriendCircles:", DisjointUnionSets.find_friend_circles(mat))

    grid = [
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1],
    ]
    print("countIslands:", DisjointUnionSets.count_islands(grid))

    M = [
        [1, 1, 0],
        [1, 1, 0],
        [0, 0, 1],
    ]
    print("findCircleNum:", DisjointUnionSets(len(M)).find_circle_num(M))
