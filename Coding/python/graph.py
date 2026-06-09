"""Generic graph backed by an adjacency list.

Idiomatic Python 3 port of java/Graph.java (original package code.ds).
Java generics ``Graph<T>``/``Vertex<T>``/``Edge<T>`` become plain Python classes.
"""


class Vertex:
    def __init__(self, vertex_id):
        self.id = vertex_id
        self._data = None
        self._edges = []            # list of Edge
        self._adjacent_vertex = []  # list of Vertex

    def get_id(self):
        return self.id

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def add_adjacent_vertex(self, e, v):
        self._edges.append(e)
        self._adjacent_vertex.append(v)

    def get_adjacent_vertexes(self):
        return self._adjacent_vertex

    def get_edges(self):
        return self._edges

    def get_degree(self):
        return len(self._edges)

    def __str__(self):
        return str(self.id)

    def __hash__(self):
        # Mirrors the Java hashCode, which keys purely on the vertex id.
        return hash(self.id)

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Vertex):
            return False
        return self.id == other.id


class Edge:
    # The three Java constructors are merged here via default arguments.
    def __init__(self, vertex1, vertex2, is_directed=False, weight=0):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.is_directed = is_directed
        self.weight = weight

    def get_vertex1(self):
        return self.vertex1

    def get_vertex2(self):
        return self.vertex2

    def get_weight(self):
        return self.weight

    def __hash__(self):
        return hash((self.vertex1, self.vertex2))

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Edge):
            return False
        return self.vertex1 == other.vertex1 and self.vertex2 == other.vertex2

    def __str__(self):
        return "Edge [isDirected={}, vertex1={}, vertex2={}, weight={}]".format(
            self.is_directed, self.vertex1, self.vertex2, self.weight)


class Graph:
    def __init__(self, is_directed):
        self.all_edges = []   # list of Edge
        self.all_vertex = {}  # dict[int, Vertex]
        self.is_directed = is_directed

    # addEdge(id1, id2) and addEdge(id1, id2, weight) merged via default weight.
    def add_edge(self, id1, id2, weight=0):
        if id1 in self.all_vertex:
            vertex1 = self.all_vertex[id1]
        else:
            vertex1 = Vertex(id1)
            self.all_vertex[id1] = vertex1
        if id2 in self.all_vertex:
            vertex2 = self.all_vertex[id2]
        else:
            vertex2 = Vertex(id2)
            self.all_vertex[id2] = vertex2

        edge = Edge(vertex1, vertex2, self.is_directed, weight)
        self.all_edges.append(edge)
        vertex1.add_adjacent_vertex(edge, vertex2)
        if not self.is_directed:
            vertex2.add_adjacent_vertex(edge, vertex1)

    # Works only for a directed graph; for an undirected one this would add the
    # vertex's edges to all_edges twice.
    def add_vertex(self, vertex):
        if vertex.get_id() in self.all_vertex:
            return
        self.all_vertex[vertex.get_id()] = vertex
        for edge in vertex.get_edges():
            self.all_edges.append(edge)

    def add_single_vertex(self, vertex_id):
        if vertex_id in self.all_vertex:
            return self.all_vertex[vertex_id]
        v = Vertex(vertex_id)
        self.all_vertex[vertex_id] = v
        return v

    def get_vertex(self, vertex_id):
        return self.all_vertex.get(vertex_id)

    def get_all_edges(self):
        return self.all_edges

    def get_all_vertex(self):
        return list(self.all_vertex.values())

    def set_data_for_vertex(self, vertex_id, data):
        if vertex_id in self.all_vertex:
            self.all_vertex[vertex_id].set_data(data)

    def __str__(self):
        parts = []
        for edge in self.get_all_edges():
            parts.append("{} {} {}\n".format(
                edge.get_vertex1(), edge.get_vertex2(), edge.get_weight()))
        return "".join(parts)


if __name__ == "__main__":
    print("Graph")

    g = Graph(False)  # undirected
    g.add_edge(1, 2)
    g.add_edge(2, 3, 5)
    g.add_edge(1, 3, 2)
    g.add_edge(3, 4)

    print("Edges [v1 v2 weight]:")
    print(str(g), end="")

    print("Vertices:", sorted(v.get_id() for v in g.get_all_vertex()))

    v3 = g.get_vertex(3)
    print("Degree of vertex 3:", v3.get_degree())
    print("Adjacent to vertex 3:",
          sorted(x.get_id() for x in v3.get_adjacent_vertexes()))

    g.set_data_for_vertex(1, "root")
    print("Data at vertex 1:", g.get_vertex(1).get_data())
