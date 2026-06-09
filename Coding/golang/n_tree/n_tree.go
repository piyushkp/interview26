package main

import (
	"fmt"
	"strings"
)

// maxInt returns the larger of two ints (Go 1.19 has no builtin max for ints).
func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// NTree is a node in an n-ary (non-binary) tree.
type NTree struct {
	data     byte
	children []*NTree
}

// NewNTree creates a node holding the given character.
func NewNTree(c byte) *NTree {
	return &NTree{data: c}
}

func (n *NTree) addChild(node *NTree) {
	n.children = append(n.children, node)
}

// Codec holds the serialize/deserialize state that the Java N_Tree kept as
// instance fields (a StringBuffer and a running index).
type Codec struct {
	sb           strings.Builder
	currentIndex int
}

// serialize encodes an n-ary tree to a string. O(n).
func (c *Codec) serialize(root *NTree) string {
	c.serializeRecursive(root)
	return c.sb.String()
}

func (c *Codec) serializeRecursive(root *NTree) {
	if root == nil {
		return
	}
	c.sb.WriteByte(root.data)
	for _, node := range root.children {
		c.serializeRecursive(node)
	}
	c.sb.WriteByte(')')
}

// deserialize decodes a string produced by serialize back into a tree. O(n).
func (c *Codec) deserialize(str string) *NTree {
	return c.deserializeRecursive(str)
}

func (c *Codec) deserializeRecursive(str string) *NTree {
	if c.currentIndex >= len(str) {
		return nil
	} else if str[c.currentIndex] == ')' {
		return nil
	}
	root := NewNTree(str[c.currentIndex])
	for c.currentIndex < len(str) {
		c.currentIndex++
		child := c.deserializeRecursive(str)
		if child == nil {
			break
		}
		root.addChild(child)
	}
	return root
}

// serialize1 is an alternative comma-delimited serialization. O(n).
func serialize1(root *NTree) string {
	var sb strings.Builder
	if root != nil {
		sb.WriteByte(root.data)
		sb.WriteByte(',')
		for _, child := range root.children {
			sb.WriteString(serialize1(child))
		}
		sb.WriteByte(')')
	}
	return sb.String()
}

// simpleDeserialize rebuilds a tree from the comma-delimited form using a stack. O(n).
func simpleDeserialize(str string) *NTree {
	var root *NTree
	var stack []*NTree
	var data strings.Builder
	for i := 0; i < len(str); i++ {
		switch str[i] {
		case ',':
			child := NewNTree(data.String()[0])
			if len(stack) != 0 {
				stack[len(stack)-1].addChild(child)
			} else {
				root = child
			}
			stack = append(stack, child)
			data.Reset()
		case ')':
			stack = stack[:len(stack)-1]
		default:
			data.WriteByte(str[i])
		}
	}
	return root
}

// maxSoFar tracks the longest path found (mirrors the Java static field).
var maxSoFar int

// findLongestPath returns the longest path in an undirected tree. O(n).
func findLongestPath(node *NTree) int {
	set := make(map[int]bool)
	dfs(node, 0, set)
	fmt.Println(maxSoFar)
	return maxSoFar
}

func dfs(node *NTree, idx int, set map[int]bool) int {
	maxFirst := 0
	maxSecond := 0
	set[idx] = true
	for _, next := range node.children {
		if set[int(next.data)] {
			continue
		}
		val := dfs(node, int(next.data), set)
		if val > maxFirst {
			maxSecond = maxFirst
			maxFirst = val
		} else if val > maxSecond {
			maxSecond = val
		}
	}
	maxSoFar = maxInt(maxSoFar, maxSecond+maxFirst)
	return maxFirst + 1
}

func main() {
	codec := &Codec{}
	root := codec.deserialize("ABE)FK)))C)DG)H)I)J)))")
	fmt.Printf("Deserialized n-ary tree: root=%c, children=%d\n", root.data, len(root.children))
}
