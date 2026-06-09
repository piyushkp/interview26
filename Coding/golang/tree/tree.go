// Package main is an idiomatic Go port of the Java reference file Tree.java
// (originally package code.ds). It collects a large set of binary tree / BST
// interview algorithms. The code is split across several files in this same
// directory; only this file contains func main().
package main

import "fmt"

// ---------------------------------------------------------------------------
// Constants mirroring Java's Integer bounds and a couple of magic numbers.
// ---------------------------------------------------------------------------

const (
	intMin   = -2147483648 // Integer.MIN_VALUE
	intMax   = 2147483647  // Integer.MAX_VALUE
	hdOffset = 16          // HD_OFFSET used by vertical sum
	splitter = ","         // serialize/deserialize separator
)

// ---------------------------------------------------------------------------
// Core node / helper types. Java classes become Go structs with pointer
// fields so that left/right/parent links can be nil.
// ---------------------------------------------------------------------------

// Node is the standard binary tree / BST node.
type Node struct {
	data      int
	left      *Node
	right     *Node
	parent    *Node
	isVisited bool
}

// Node1 carries extra bookkeeping fields used by the iterative diameter algo.
type Node1 struct {
	data        int
	left        *Node1
	right       *Node1
	maxDistance int
	rHeight     int
	lHeight     int
}

// NTree is an n-ary tree node (ported from N_Tree.NTree). Java stored a char;
// we keep an int so the demo char codes still work.
type NTree struct {
	data     int
	children []*NTree
}

func (n *NTree) addChild(child *NTree) {
	n.children = append(n.children, child)
}

// BNode pairs a node with the (open) value range allowed below it.
type BNode struct {
	n     *Node
	left  float64
	right float64
}

// DLL is a doubly linked list node used for vertical sums.
type DLL struct {
	data int
	next *DLL
	prev *DLL
}

// NodeT augments a BST node with a left-subtree count (Java Node_t).
type NodeT struct {
	data   int
	lCount int
	left   *NodeT
	right  *NodeT
}

// RankNode supports order-statistic style rank queries.
type RankNode struct {
	leftSize int
	left     *RankNode
	right    *RankNode
	data     int
}

// Relation describes a child -> parent edge (parent nil means root).
type Relation struct {
	parent *int
	child  int
	isLeft bool
}

// nodeIntPair is a small local replacement for javafx.util.Pair<Node,Integer>.
type nodeIntPair struct {
	node *Node
	val  int
}

// nodePath bundles a node with the path string leading to it (for printing).
type nodePath struct {
	node *Node
	path string
}

// Tree holds the instance level state that several Java instance methods rely
// on (root pointer plus a handful of mutable counters).
type Tree struct {
	root         *Node
	prev         *Node
	head         *Node
	count        int
	deepestLevel int
	value        int
}

// ---------------------------------------------------------------------------
// Package level state mirroring Java's static fields.
// ---------------------------------------------------------------------------

var (
	countN        int
	diameter      int
	preIndex      int
	maxSoFar      int
	currentIndex  int
	maxSize       = 1
	pathStack     []*Node
	pathEndpoints [2]int
)

// ---------------------------------------------------------------------------
// Small numeric helpers (Java Math.max / Math.min / Math.abs on ints).
// ---------------------------------------------------------------------------

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func absInt(a int) int {
	if a < 0 {
		return -a
	}
	return a
}

// ---------------------------------------------------------------------------
// Entry point: ported from Java's public static void main.
// ---------------------------------------------------------------------------

func main() {
	tree := &Node{data: 1}
	tree.right = &Node{data: 0}
	tree.right.left = &Node{data: 0}
	tree.right.right = &Node{data: 1}

	pruned := pruneTree(tree)
	if pruned != nil {
		fmt.Println("Pruned tree root:", pruned.data)
	} else {
		fmt.Println("Pruned tree is empty")
	}
}
