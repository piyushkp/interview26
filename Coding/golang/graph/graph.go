package main

import (
	"fmt"
	"strconv"
)

// Graph is a generic graph backed by an adjacency list (Java Graph<T>).
// allEdges preserves insertion order; allVertex maps vertex id -> *Vertex.
type Graph[T any] struct {
	allEdges   []*Edge[T]
	allVertex  map[int64]*Vertex[T]
	isDirected bool
}

func NewGraph[T any](isDirected bool) *Graph[T] {
	return &Graph[T]{
		allEdges:   make([]*Edge[T], 0),
		allVertex:  make(map[int64]*Vertex[T]),
		isDirected: isDirected,
	}
}

// addEdge adds an unweighted edge (weight 0). Renamed from Java overload addEdge(id1,id2).
func (g *Graph[T]) addEdge(id1, id2 int64) {
	g.addEdgeWeighted(id1, id2, 0)
}

// addVertex adds a pre-built vertex and all of its edges.
// Works correctly only for a directed graph (see Java note).
func (g *Graph[T]) addVertex(vertex *Vertex[T]) {
	if _, ok := g.allVertex[vertex.getId()]; ok {
		return
	}
	g.allVertex[vertex.getId()] = vertex
	for _, edge := range vertex.getEdges() {
		g.allEdges = append(g.allEdges, edge)
	}
}

func (g *Graph[T]) addSingleVertex(id int64) *Vertex[T] {
	if v, ok := g.allVertex[id]; ok {
		return v
	}
	v := newVertex[T](id)
	g.allVertex[id] = v
	return v
}

func (g *Graph[T]) getVertex(id int64) *Vertex[T] {
	return g.allVertex[id]
}

// addEdgeWeighted adds a weighted edge. Renamed from Java overload addEdge(id1,id2,weight).
func (g *Graph[T]) addEdgeWeighted(id1, id2 int64, weight int) {
	var vertex1 *Vertex[T]
	if v, ok := g.allVertex[id1]; ok {
		vertex1 = v
	} else {
		vertex1 = newVertex[T](id1)
		g.allVertex[id1] = vertex1
	}
	var vertex2 *Vertex[T]
	if v, ok := g.allVertex[id2]; ok {
		vertex2 = v
	} else {
		vertex2 = newVertex[T](id2)
		g.allVertex[id2] = vertex2
	}

	edge := newEdge[T](vertex1, vertex2, g.isDirected, weight)
	g.allEdges = append(g.allEdges, edge)
	vertex1.addAdjacentVertex(edge, vertex2)
	if !g.isDirected {
		vertex2.addAdjacentVertex(edge, vertex1)
	}
}

func (g *Graph[T]) getAllEdges() []*Edge[T] { return g.allEdges }

func (g *Graph[T]) getAllVertex() []*Vertex[T] {
	out := make([]*Vertex[T], 0, len(g.allVertex))
	for _, v := range g.allVertex {
		out = append(out, v)
	}
	return out
}

func (g *Graph[T]) setDataForVertex(id int64, data T) {
	if v, ok := g.allVertex[id]; ok {
		v.setData(data)
	}
}

func (g *Graph[T]) String() string {
	out := ""
	for _, edge := range g.getAllEdges() {
		out += fmt.Sprintf("%s %s %d\n", edge.getVertex1(), edge.getVertex2(), edge.getWeight())
	}
	return out
}

// Vertex is a graph vertex carrying generic data.
type Vertex[T any] struct {
	id             int64
	data           T
	edges          []*Edge[T]
	adjacentVertex []*Vertex[T]
}

func newVertex[T any](id int64) *Vertex[T] {
	return &Vertex[T]{id: id}
}

func (v *Vertex[T]) getId() int64   { return v.id }
func (v *Vertex[T]) setData(data T) { v.data = data }
func (v *Vertex[T]) getData() T     { return v.data }

func (v *Vertex[T]) addAdjacentVertex(e *Edge[T], to *Vertex[T]) {
	v.edges = append(v.edges, e)
	v.adjacentVertex = append(v.adjacentVertex, to)
}

func (v *Vertex[T]) String() string                    { return strconv.FormatInt(v.id, 10) }
func (v *Vertex[T]) getAdjacentVertexes() []*Vertex[T] { return v.adjacentVertex }
func (v *Vertex[T]) getEdges() []*Edge[T]              { return v.edges }
func (v *Vertex[T]) getDegree() int                    { return len(v.edges) }

// Edge is a (possibly directed, weighted) graph edge.
type Edge[T any] struct {
	isDirected bool
	vertex1    *Vertex[T]
	vertex2    *Vertex[T]
	weight     int
}

func newEdge[T any](vertex1, vertex2 *Vertex[T], isDirected bool, weight int) *Edge[T] {
	return &Edge[T]{vertex1: vertex1, vertex2: vertex2, isDirected: isDirected, weight: weight}
}

func (e *Edge[T]) getVertex1() *Vertex[T] { return e.vertex1 }
func (e *Edge[T]) getVertex2() *Vertex[T] { return e.vertex2 }
func (e *Edge[T]) getWeight() int         { return e.weight }
func (e *Edge[T]) directed() bool         { return e.isDirected }

func (e *Edge[T]) String() string {
	return fmt.Sprintf("Edge [isDirected=%t, vertex1=%s, vertex2=%s, weight=%d]",
		e.isDirected, e.vertex1, e.vertex2, e.weight)
}

func main() {
	fmt.Println("Graph")

	g := NewGraph[string](true)
	g.addEdgeWeighted(1, 2, 5)
	g.addEdgeWeighted(2, 3, 7)
	g.addEdge(3, 1)
	g.setDataForVertex(1, "root")

	fmt.Print(g)
	fmt.Println("Vertex 2 degree:", g.getVertex(2).getDegree())
	fmt.Println("Total vertices:", len(g.getAllVertex()))
}
