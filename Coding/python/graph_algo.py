"""Idiomatic Python 3 port of java/Graph_Algo.java (original package code.ds).

Graph algorithms: DFS / BFS traversal, directed-graph cycle detection
(white/gray/black), topological "build order", and cloning of an undirected
graph.

The Java source references ``Vertex`` / ``Edge`` / ``Graph`` from a separate
file; minimal self-contained versions are defined here so the module runs
standalone. Java had two overloaded ``clone`` methods, renamed here to
``clone_unique`` (unique labels, uses an instance map) and
``clone_with_visited`` (possibly duplicate labels, identity-keyed visited map).
The Java source has no ``main``; a demonstrative one is added.
"""

from collections import deque


# ---------------------------------------------------------------------------
# Minimal graph model (Vertex / Edge / Graph)
# ---------------------------------------------------------------------------
class Vertex:
    def __init__(self, vid):
        self.id = vid
        self.adjacent = []

    def get_id(self):
        return self.id

    def get_adjacent_vertexes(self):
        return self.adjacent

    def add_adjacent(self, v):
        self.adjacent.append(v)


class Edge:
    def __init__(self, v1, v2, weight=0):
        self.vertex1 = v1
        self.vertex2 = v2
        self.weight = weight

    def get_vertex1(self):
        return self.vertex1

    def get_vertex2(self):
        return self.vertex2


class Graph:
    def __init__(self, directed=True):
        self.directed = directed
        self.vertices = {}  # id -> Vertex (insertion ordered)

    def _get_or_create(self, vid):
        v = self.vertices.get(vid)
        if v is None:
            v = Vertex(vid)
            self.vertices[vid] = v
        return v

    def add_vertex(self, vid):
        self._get_or_create(vid)

    def add_edge(self, id1, id2):
        v1 = self._get_or_create(id1)
        v2 = self._get_or_create(id2)
        v1.add_adjacent(v2)
        if not self.directed:
            v2.add_adjacent(v1)

    def get_all_vertex(self):
        return list(self.vertices.values())


class UndirectedGraphNode:
    def __init__(self, x):
        self.label = x
        self.neighbors = []


# ---------------------------------------------------------------------------
# Graph algorithms
# ---------------------------------------------------------------------------
class GraphAlgo:
    def __init__(self):
        self.map = {}  # label -> node, used by clone_unique

    # --- DFS traversal ---
    def dfs_traversal(self, graph):
        visited = set()
        for vertex in graph.get_all_vertex():
            if vertex.get_id() not in visited:
                self._dfs_util(vertex, visited)

    def _dfs_util(self, v, visited):
        visited.add(v.get_id())
        print(v.get_id(), end=" ")
        for vertex in v.get_adjacent_vertexes():
            if vertex.get_id() not in visited:
                self._dfs_util(vertex, visited)

    # --- BFS traversal ---
    def bfs_traversal(self, graph):
        visited = set()
        q = deque()
        for vertex in graph.get_all_vertex():
            if vertex.get_id() not in visited:
                q.append(vertex)
                visited.add(vertex.get_id())
                while len(q) != 0:
                    vq = q.popleft()
                    print(vq.get_id(), end=" ")
                    for v in vq.get_adjacent_vertexes():
                        if v.get_id() not in visited:
                            q.append(v)
                            visited.add(v.get_id())

    # --- Cycle detection in a directed graph ---
    def has_cycle(self, graph):
        white_set = set(graph.get_all_vertex())
        gray_set = set()
        black_set = set()

        while len(white_set) > 0:
            current = next(iter(white_set))
            if self._dfs_cycle(current, white_set, gray_set, black_set):
                return True
        return False

    def _dfs_cycle(self, current, white_set, gray_set, black_set):
        # Move current to gray (being explored) from white, then explore it.
        self._move_vertex(current, white_set, gray_set)
        for neighbor in current.get_adjacent_vertexes():
            if neighbor in black_set:  # already fully explored
                continue
            if neighbor in gray_set:  # back edge -> cycle
                return True
            if self._dfs_cycle(neighbor, white_set, gray_set, black_set):
                return True
        # Done exploring: move from gray to black.
        self._move_vertex(current, gray_set, black_set)
        return False

    def _move_vertex(self, vertex, source_set, destination_set):
        source_set.discard(vertex)
        destination_set.add(vertex)

    def get_vertex_for_edge(self, v, e):
        return e.get_vertex2() if e.get_vertex1() is v else e.get_vertex1()

    # --- Clone undirected graph (unique labels) ---
    def clone_unique(self, node):
        if node is None:
            return None
        if node.label in self.map:
            return self.map[node.label]
        tmp = UndirectedGraphNode(node.label)
        self.map[tmp.label] = tmp
        for neighbor in node.neighbors:
            tmp.neighbors.append(self.clone_unique(neighbor))
        return tmp

    # --- Clone undirected graph (labels may repeat; identity visited map) ---
    def clone_with_visited(self, src, visited):
        if src is None:
            return None
        if id(src) in visited:
            return visited[id(src)]
        tmp = UndirectedGraphNode(src.label)
        visited[id(src)] = tmp
        for child in src.neighbors:
            tmp.neighbors.append(self.clone_with_visited(child, visited))
        return tmp


# ---------------------------------------------------------------------------
# Build order via topological sort (Java static methods)
# ---------------------------------------------------------------------------
def build_order(dependencies):
    temporary_marks = set()
    permanent_marks = set()
    result = []
    for i in range(len(dependencies)):
        if i not in permanent_marks:
            visit(i, dependencies, temporary_marks, permanent_marks, result)
    return result


def visit(project, dependencies, temporary_marks, permanent_marks, result):
    if project in temporary_marks:
        raise RuntimeError("Graph is not acyclic")
    if project not in permanent_marks:
        temporary_marks.add(project)
        for i in dependencies[project]:
            visit(i, dependencies, temporary_marks, permanent_marks, result)
        permanent_marks.add(project)
        temporary_marks.discard(project)
        result.append(project)


if __name__ == "__main__":
    algo = GraphAlgo()
    g = Graph(directed=True)
    for a, b in [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]:
        g.add_edge(a, b)

    print("DFS:", end=" ")
    algo.dfs_traversal(g)
    print()

    print("BFS:", end=" ")
    algo.bfs_traversal(g)
    print()

    print("has_cycle:", algo.has_cycle(g))

    deps = [[], [0], [0], [1, 2], [3]]
    print("Build order:", build_order(deps))

    # clone demo (unique labels)
    n0 = UndirectedGraphNode(0)
    n1 = UndirectedGraphNode(1)
    n2 = UndirectedGraphNode(2)
    n0.neighbors = [n1, n2]
    n1.neighbors = [n2]
    cloned = GraphAlgo().clone_unique(n0)
    print("clone label:", cloned.label, "neighbors:", [n.label for n in cloned.neighbors])
