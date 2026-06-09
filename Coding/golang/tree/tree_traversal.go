package main

import "fmt"

// insert a node in a BST (recursive). Faithful port of the Java version
// (which, like the original, does not actually re-link the parent on the
// initial empty case).
func (t *Tree) insert(root *Node, value int) {
	if root == nil {
		newNode := &Node{}
		newNode.data = value
		root = newNode
	}
	if value < root.data {
		t.insert(root.left, value)
	} else if value > root.data {
		t.insert(root.right, value)
	}
}

// insertItr inserts a node into a tree iteratively.
func (t *Tree) insertItr(root *Node, data int) {
	newNode := &Node{}
	newNode.data = data
	if root == nil {
		root.data = data
	} else {
		current := root
		for {
			if data < current.data {
				current = current.left
				if current == nil {
					current.left = newNode
					return
				}
			} else {
				current = current.right
				if current == nil {
					current.right = newNode
					return
				}
			}
		}
	}
}

// search performs a recursive search in a BST.
func (t *Tree) search(root *Node, data int) *Node {
	if root == nil {
		return nil
	}
	if root.data == data {
		return root
	}
	if data < root.data {
		t.search(root.left, data)
	} else if data > root.data {
		t.search(root.right, data)
	}
	return nil
}

// DFS implements a depth first search recursively.
func (t *Tree) DFS(root *Node, target int) bool {
	if root == nil {
		return false
	}
	if root.data == target {
		return true
	}
	return t.DFS(root.left, target) || t.DFS(root.right, target)
}

// DFSIterative implements a depth first search iteratively using a stack.
func (t *Tree) DFSIterative(root *Node, target int) bool {
	if root == nil {
		return false
	}
	stack := []*Node{root}
	for len(stack) > 0 {
		temp := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if temp.data == target {
			return true
		}
		if temp.right != nil {
			stack = append(stack, temp.right)
		}
		if temp.left != nil {
			stack = append(stack, temp.left)
		}
	}
	return false
}

// BFS implements a breadth first (level order) search.
func (t *Tree) BFS(root *Node, target int) bool {
	if root == nil {
		return false
	}
	queue := []*Node{root}
	for len(queue) > 0 {
		tmp := queue[0]
		queue = queue[1:]
		if tmp.data == target {
			return true
		}
		if tmp.left != nil {
			queue = append(queue, tmp.left)
		}
		if tmp.right != nil {
			queue = append(queue, tmp.right)
		}
	}
	return false
}

// printLevels prints a binary tree level by level, one level per line.
func printLevels(root *Node) {
	if root == nil {
		return
	}
	q := []*Node{root}
	for len(q) > 0 {
		nodeCount := len(q)
		for nodeCount > 0 {
			node := q[0]
			q = q[1:]
			fmt.Print(node.data)
			if node.left != nil {
				q = append(q, node.left)
			}
			if node.right != nil {
				q = append(q, node.right)
			}
			nodeCount--
		}
		fmt.Println()
	}
}

// printVerticalOrder prints a binary tree vertically from left to right.
// Time = O(n) and space = O(n).
func printVerticalOrder(root *Node) {
	if root == nil {
		return
	}
	m := make(map[int][]int)
	hd := 0
	que := []nodeIntPair{{root, hd}}
	max, min := 0, 0
	for len(que) > 0 {
		temp := que[0]
		que = que[1:]
		hd = temp.val
		node := temp.node

		var list []int
		if existing, ok := m[hd]; ok {
			list = existing
		}
		list = append(list, node.data)
		m[hd] = list
		if node.left != nil {
			que = append(que, nodeIntPair{node.left, hd - 1})
			min = minInt(min, hd-1)
		}
		if node.right != nil {
			que = append(que, nodeIntPair{node.right, hd + 1})
			max = maxInt(max, hd+1)
		}
	}
	for i := min; i <= max; i++ {
		fmt.Println(m[i])
	}
}

// reverseLevelOrder prints a binary tree's nodes in reverse level order.
func (t *Tree) reverseLevelOrder(root *Node) {
	var S []*Node
	var Q []*Node
	Q = append(Q, root)
	// Like normal level order traversal, but push nodes onto a stack and visit
	// the right subtree before the left subtree.
	for len(Q) > 0 {
		root = Q[0]
		Q = Q[1:]
		S = append(S, root)
		if root.right != nil {
			Q = append(Q, root.right) // RIGHT CHILD ENQUEUED BEFORE LEFT
		}
		if root.left != nil {
			Q = append(Q, root.left)
		}
	}
	for len(S) > 0 {
		root = S[len(S)-1]
		S = S[:len(S)-1]
		fmt.Print(root.data)
	}
}

// spiralLevelOrderTraversal prints a binary tree's nodes in spiral fashion.
func (t *Tree) spiralLevelOrderTraversal(root *Node) {
	if root == nil {
		return
	}
	stack1 := []*Node{root}
	var stack2 []*Node
	for len(stack1) > 0 || len(stack2) > 0 {
		for len(stack1) > 0 {
			node := stack1[len(stack1)-1]
			stack1 = stack1[:len(stack1)-1]
			fmt.Print(node.data)
			if node.right != nil {
				stack2 = append(stack2, node.right)
			}
			if node.left != nil {
				stack2 = append(stack2, node.left)
			}
		}
		for len(stack2) > 0 {
			node := stack2[len(stack2)-1]
			stack2 = stack2[:len(stack2)-1]
			fmt.Print(node.data)
			if node.left != nil {
				stack1 = append(stack1, node.left)
			}
			if node.right != nil {
				stack1 = append(stack1, node.right)
			}
		}
	}
}

// inOrder traversal of a BST (recursive).
func (t *Tree) inOrder(root *Node) {
	if root != nil {
		t.inOrder(root.left)
		fmt.Print(root.data)
		t.inOrder(root.right)
	}
}

// preOrder traversal of a BST (recursive).
func (t *Tree) preOrder(root *Node) {
	if root != nil {
		fmt.Print(root.data)
		t.preOrder(root.left)
		t.preOrder(root.right)
	}
}

// MorrisTraversal performs an in-order traversal in O(1) extra space.
func (t *Tree) MorrisTraversal(root *Node) {
	if root == nil {
		return
	}
	var pre *Node
	current := root
	for current != nil {
		if current.left == nil {
			fmt.Print(current.data, " ")
			current = current.right
		} else {
			// Find the inorder predecessor of current.
			pre = current.left
			for pre.right != nil && pre.right != current {
				pre = pre.right
			}
			if pre.right == nil {
				// Make current the right child of its inorder predecessor.
				pre.right = current
				current = current.left
			} else {
				// Revert the change to restore the tree.
				pre.right = nil
				fmt.Print(current.data, " ")
				current = current.right
			}
		}
	}
}

// inorder is an iterative in-order traversal.
func (t *Tree) inorder(root *Node) {
	node := root
	var stack []*Node
	for len(stack) > 0 || node != nil {
		if node != nil {
			stack = append(stack, node)
			node = node.left
		} else {
			node = stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			fmt.Print(node.data, " ")
			node = node.right
		}
	}
}

// iterativePreorder prints a preorder traversal iteratively.
func (t *Tree) iterativePreorder(root *Node) {
	if root == nil {
		return
	}
	nodeStack := []*Node{root}
	// Pop each item; print it, then push right child before left so that left
	// is processed first.
	for len(nodeStack) > 0 {
		node := nodeStack[len(nodeStack)-1]
		nodeStack = nodeStack[:len(nodeStack)-1]
		fmt.Print(node.data)
		if node.right != nil {
			nodeStack = append(nodeStack, node.right)
		}
		if node.left != nil {
			nodeStack = append(nodeStack, node.left)
		}
	}
}

// postOrder traversal of a BST (recursive).
func (t *Tree) postOrder(root *Node) {
	if root != nil {
		t.postOrder(root.left)
		t.postOrder(root.right)
		fmt.Print(root.data)
	}
}

// postOrderIterative performs a post-order traversal using a single stack.
func (t *Tree) postOrderIterative(node *Node) {
	if node == nil {
		return
	}
	S := []*Node{node}
	var prev *Node
	for len(S) > 0 {
		current := S[len(S)-1]
		// Go down the tree in search of a leaf; otherwise move down.
		if prev == nil || prev.left == current || prev.right == current {
			if current.left != nil {
				S = append(S, current.left)
			} else if current.right != nil {
				S = append(S, current.right)
			} else {
				S = S[:len(S)-1]
				fmt.Print(current.data)
			}
		} else if current.left == prev {
			if current.right != nil {
				S = append(S, current.right)
			} else {
				S = S[:len(S)-1]
				fmt.Print(current.data)
			}
		} else if current.right == prev {
			S = S[:len(S)-1]
			fmt.Print(current.data)
		}
		prev = current
	}
}

// rightView prints the right view of a binary tree (uses the instance root).
func (t *Tree) rightView() {
	maxLevel := 0
	t.rightViewUtil(t.root, 1, maxLevel)
}

func (t *Tree) rightViewUtil(root *Node, level int, maxLevel int) {
	if root == nil {
		return
	}
	if maxLevel < level {
		fmt.Print(root.data)
		maxLevel = level
	}
	t.rightViewUtil(root.right, level+1, maxLevel)
	t.rightViewUtil(root.left, level+1, maxLevel)
}

// mirrorTreeIterative walks the tree level by level (Java left/right swap was
// a no-op placeholder, preserved here).
func (t *Tree) mirrorTreeIterative(root *Node) *Node {
	newNode := &Node{}
	if root == nil {
		return nil
	}
	q := []*Node{root}
	for len(q) > 0 {
		newNode = q[0]
		q = q[1:]
		if newNode.left != nil {
			q = append(q, newNode.left)
		}
		if newNode.right != nil {
			q = append(q, newNode.right)
		}
	}
	return newNode
}

// mirrorTree builds a mirrored copy of the tree.
func (t *Tree) mirrorTree(root *Node) *Node {
	newNode := &Node{}
	if root == nil {
		return nil
	}
	newNode.data = root.data
	newNode.left = t.mirrorTree(root.right)
	newNode.right = t.mirrorTree(root.left)
	return newNode
}

// isMirror checks whether two trees are mirror images of each other.
func (t *Tree) isMirror(node1, node2 *Node) bool {
	if node1 == nil && node2 == nil {
		return true
	}
	if node1 != nil && node2 != nil && node1.data == node2.data {
		return t.isMirror(node1.left, node2.right) && t.isMirror(node1.right, node2.left)
	}
	return false
}
