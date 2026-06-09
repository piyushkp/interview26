package main

// Ported from Coding/java/Graph_Algo.java (original package code.ds).
// The original referenced Graph/Vertex/Edge from another file; minimal generic
// versions are defined here so the package is self-contained.

import "fmt"

// Vertex is a graph vertex with an id and adjacency list.
type Vertex[T any] struct {
	id       int64
	adjacent []*Vertex[T]
}

func (v *Vertex[T]) getId() int64                  { return v.id }
func (v *Vertex[T]) getAdjacentVertexes() []*Vertex[T] { return v.adjacent }

// Edge connects two vertices.
type Edge[T any] struct {
	v1 *Vertex[T]
	v2 *Vertex[T]
}

func (e *Edge[T]) getVertex1() *Vertex[T] { return e.v1 }
func (e *Edge[T]) getVertex2() *Vertex[T] { return e.v2 }

// Graph holds all vertices.
type Graph[T any] struct {
	vertices []*Vertex[T]
}

func (g *Graph[T]) getAllVertex() []*Vertex[T] { return g.vertices }

// UndirectedGraphNode is used by the graph-cloning routines.
type UndirectedGraphNode struct {
	label     int
	neighbors []*UndirectedGraphNode
}

func newUndirectedGraphNode(x int) *UndirectedGraphNode {
	return &UndirectedGraphNode{label: x, neighbors: []*UndirectedGraphNode{}}
}

// GraphAlgo groups the graph algorithms (mirrors the Java instance class).
type GraphAlgo struct {
	cloneMap map[int]*UndirectedGraphNode
}

func main() {
	// Build Order via topological sort:
	//   0:        1: 0   2: 0   3: 1,2   4: 3
	dependencies := [][]int{{}, {0}, {0}, {1, 2}, {3}}
	order := buildOrder(dependencies)
	fmt.Println("Build order:", order)
}

// DFS traversal.
func (ga *GraphAlgo) DFS(graph *Graph[int]) {
	visited := map[int64]bool{}
	for _, vertex := range graph.getAllVertex() {
		if !visited[vertex.getId()] {
			ga.DFSUtil(vertex, visited)
		}
	}
}

func (ga *GraphAlgo) DFSUtil(v *Vertex[int], visited map[int64]bool) {
	visited[v.getId()] = true
	fmt.Print(v.getId(), " ")
	for _, vertex := range v.getAdjacentVertexes() {
		if !visited[vertex.getId()] {
			ga.DFSUtil(vertex, visited)
		}
	}
}

// BFS traversal.
func (ga *GraphAlgo) BFS(graph *Graph[int]) {
	visited := map[int64]bool{}
	q := []*Vertex[int]{}
	for _, vertex := range graph.getAllVertex() {
		if !visited[vertex.getId()] {
			q = append(q, vertex)
			visited[vertex.getId()] = true
			for len(q) != 0 {
				vq := q[0]
				q = q[1:]
				fmt.Print(vq.getId(), " ")
				for _, v := range vq.getAdjacentVertexes() {
					if !visited[v.getId()] {
						q = append(q, v)
						visited[v.getId()] = true
					}
				}
			}
		}
	}
}

// hasCycle detects a cycle in a directed graph (white/gray/black sets).
func (ga *GraphAlgo) hasCycle(graph *Graph[int]) bool {
	whiteSet := map[*Vertex[int]]bool{}
	graySet := map[*Vertex[int]]bool{}
	blackSet := map[*Vertex[int]]bool{}

	for _, vertex := range graph.getAllVertex() {
		whiteSet[vertex] = true
	}

	for len(whiteSet) > 0 {
		var current *Vertex[int]
		for v := range whiteSet {
			current = v
			break
		}
		if ga.dfs(current, whiteSet, graySet, blackSet) {
			return true
		}
	}
	return false
}

func (ga *GraphAlgo) dfs(current *Vertex[int], whiteSet, graySet, blackSet map[*Vertex[int]]bool) bool {
	// move current to gray set from white set and then explore it.
	ga.moveVertex(current, whiteSet, graySet)
	for _, neighbor := range current.getAdjacentVertexes() {
		// if in black set means already explored so continue.
		if blackSet[neighbor] {
			continue
		}
		// if in gray set then cycle found.
		if graySet[neighbor] {
			return true
		}
		if ga.dfs(neighbor, whiteSet, graySet, blackSet) {
			return true
		}
	}
	// move vertex from gray set to black set when done exploring.
	ga.moveVertex(current, graySet, blackSet)
	return false
}

func (ga *GraphAlgo) moveVertex(vertex *Vertex[int], sourceSet, destinationSet map[*Vertex[int]]bool) {
	delete(sourceSet, vertex)
	destinationSet[vertex] = true
}

// Find single source shortest path using Dijkstra's algorithm helper.
func (ga *GraphAlgo) getVertexForEdge(v *Vertex[int], e *Edge[int]) *Vertex[int] {
	if e.getVertex1() == v {
		return e.getVertex2()
	}
	return e.getVertex1()
}

// buildOrder returns a valid build order using topological sort. The index is
// the process number; the value is the list of processes it depends on.
func buildOrder(dependencies [][]int) []int {
	temporaryMarks := map[int]bool{}
	permanentMarks := map[int]bool{}
	result := []int{}
	for i := 0; i < len(dependencies); i++ {
		if !permanentMarks[i] {
			result = visit(i, dependencies, temporaryMarks, permanentMarks, result)
		}
	}
	return result
}

// visit searches all unmarked nodes accessible from project.
func visit(project int, dependencies [][]int, temporaryMarks, permanentMarks map[int]bool, result []int) []int {
	// Throw an error if we find a cycle.
	if temporaryMarks[project] {
		panic("Graph is not acyclic")
	}

	if !permanentMarks[project] {
		temporaryMarks[project] = true
		for _, i := range dependencies[project] {
			result = visit(i, dependencies, temporaryMarks, permanentMarks, result)
		}
		permanentMarks[project] = true
		delete(temporaryMarks, project)
		result = append(result, project)
	}
	return result
}

// clone clones a graph when node labels are unique.
func (ga *GraphAlgo) clone(node *UndirectedGraphNode) *UndirectedGraphNode {
	if node == nil {
		return nil
	}
	if ga.cloneMap == nil {
		ga.cloneMap = map[int]*UndirectedGraphNode{}
	}
	if v, ok := ga.cloneMap[node.label]; ok {
		return v
	}
	tmp := newUndirectedGraphNode(node.label)
	ga.cloneMap[tmp.label] = tmp
	for _, neighbor := range node.neighbors {
		tmp.neighbors = append(tmp.neighbors, ga.clone(neighbor))
	}
	return tmp
}

// cloneWithVisited clones a graph that may contain duplicate labels.
func cloneWithVisited(src *UndirectedGraphNode, visited map[*UndirectedGraphNode]*UndirectedGraphNode) *UndirectedGraphNode {
	if src == nil {
		return nil
	}
	if v, ok := visited[src]; ok {
		return v
	}
	tmp := newUndirectedGraphNode(src.label)
	visited[src] = tmp
	for _, child := range src.neighbors {
		tmp.neighbors = append(tmp.neighbors, cloneWithVisited(child, visited))
	}
	return tmp
}
