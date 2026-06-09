package main

import (
	"fmt"
	"math"
)

// buildTreeFromInPre constructs a tree from inorder and preorder traversals.
func (t *Tree) buildTreeFromInPre(in, pre []int, inStrt, inEnd int) *Node {
	if inStrt > inEnd {
		return nil
	}
	// Pick the current node from preorder using preIndex and increment it.
	tNode := &Node{data: pre[preIndex]}
	preIndex++
	if inStrt == inEnd {
		return tNode
	}
	// Find the index of this node in inorder traversal.
	inIndex := searchIndex(in, inStrt, inEnd, tNode.data)
	tNode.left = t.buildTreeFromInPre(in, pre, inStrt, inIndex-1)
	tNode.right = t.buildTreeFromInPre(in, pre, inIndex+1, inEnd)
	return tNode
}

// searchIndex returns the index of value in arr[start..end].
func searchIndex(arr []int, start, end, value int) int {
	i := start
	for ; i <= end; i++ {
		if arr[i] == value {
			return i
		}
	}
	return i
}

// delete removes a node (by key) from the binary tree rooted at t.root.
func (t *Tree) delete(key int) {
	var parent *Node
	var nodetoDelete *Node
	if t.root.data == key {
		nodetoDelete = t.root
	} else {
		parent = t.getParent(t.root, key, nodetoDelete)
	}
	if nodetoDelete.left == nil && nodetoDelete.right == nil {
		if parent != nil {
			if parent.left == nodetoDelete {
				parent.left = nil
			} else {
				parent.right = nil
			}
		} else {
			t.root = nil
		}
	} else if nodetoDelete.left == nil {
		if parent != nil {
			if parent.left == nodetoDelete {
				parent.left = nodetoDelete.right
			} else {
				parent.right = nodetoDelete.right
			}
		} else {
			t.root = nodetoDelete.right
		}
	} else if nodetoDelete.right == nil {
		if parent != nil {
			if parent.left == nodetoDelete {
				parent.left = nodetoDelete.left
			} else {
				parent.right = nodetoDelete.left
			}
		} else {
			t.root = nodetoDelete.left
		}
	} else {
		successor := t.FinMinValue(nodetoDelete.right)
		if parent != nil {
			if parent.right == nodetoDelete {
				parent.right = successor
			} else {
				parent.left = successor
			}
		} else {
			t.root = successor
		}
	}
}

func (t *Tree) getParent(root *Node, target int, nodetoDelete *Node) *Node {
	if root != nil {
		if root.left != nil {
			if root.left.data == target {
				nodetoDelete = root.left
				return root
			}
		}
		if root.right != nil {
			if root.right.data == target {
				nodetoDelete = root.right
				return root
			}
		}
		t.getParent(root.left, target, nodetoDelete)
		t.getParent(root.right, target, nodetoDelete)
	}
	return root
}

func (t *Tree) FinMinValue(startNode *Node) *Node {
	var parent *Node
	for startNode.left != nil {
		parent = startNode
		startNode = startNode.left
	}
	if parent != nil {
		parent.left = nil
	}
	return startNode
}

// deleteRec deletes a key from a BST and returns the new root.
func (t *Tree) deleteRec(root *Node, key int) *Node {
	if root == nil {
		return root
	}
	if key < root.data {
		root.left = t.deleteRec(root.left, key)
	} else if key > root.data {
		root.right = t.deleteRec(root.right, key)
	} else {
		if root.left == nil {
			return root.right
		} else if root.right == nil {
			return root.left
		}
		// Node with two children: use the inorder successor.
		root.data = t.minValuedata(root.right)
		root.right = t.deleteRec(root.right, root.data)
	}
	return root
}

func (t *Tree) minValuedata(root *Node) int {
	minv := root.data
	for root.left != nil {
		minv = root.left.data
		root = root.left
	}
	return minv
}

// FindLCA finds the lowest common ancestor in a BST.
func (t *Tree) FindLCA(root, one, two *Node) *Node {
	for root != nil {
		if root.data < one.data && root.data < two.data {
			return root.right
		} else if root.data > one.data && root.data > two.data {
			return root.left
		} else {
			return root
		}
	}
	return nil
}

// FindLCA_BTree finds the LCA of a binary tree using parent pointers and a set.
// Run time O(h), space O(h).
func (t *Tree) FindLCA_BTree(root, one, two *Node) *Node {
	hash := make(map[*Node]bool)
	for one != nil || two != nil {
		if one != nil {
			if hash[one] {
				return one
			}
			hash[one] = true
			one = one.parent
		}
		if two != nil {
			if hash[two] {
				return two
			}
			hash[two] = true
			two = two.parent
		}
	}
	return nil
}

// FindLCA_Best finds the LCA using parent pointers without extra space.
func (t *Tree) FindLCA_Best(root, one, two *Node) *Node {
	h1 := t.getHeight(one)
	h2 := t.getHeight(two)
	if h1 > h2 {
		// swap h1 and h2 via XOR
		h1 ^= h2
		h2 ^= h1
		h1 ^= h2
		t.swap(one.data, two.data)
	}
	dh := h2 - h1
	for i := 0; i < dh; i++ {
		two = two.parent
	}
	for one != nil && two != nil {
		if one.data == two.data {
			return one
		}
		one = one.parent
		two = two.parent
	}
	return nil
}

func (t *Tree) getHeight(node *Node) int {
	height := 0
	for node != nil {
		height++
		node = node.parent
	}
	return height
}

// FindLowestCommonAncestor finds the LCA without a parent pointer.
func FindLowestCommonAncestor(n *Node, n1, n2 int) *Node {
	if n == nil {
		return nil
	}
	if n.data == n1 || n.data == n2 {
		return n
	}
	left := FindLowestCommonAncestor(n.left, n1, n2)
	right := FindLowestCommonAncestor(n.right, n1, n2)
	if left == nil && right == nil {
		return nil
	}
	if left != nil && right != nil {
		return n
	}
	if left != nil {
		return left
	}
	if right != nil {
		return right
	}
	return nil
}

// findFirstCommonAncestor finds the LCA of a binary tree.
func findFirstCommonAncestor(root, n1, n2 *Node) *Node {
	if root == nil {
		return nil
	}
	if !contains(root, n1) || !contains(root, n2) {
		return nil
	}
	if root == n1 || root == n2 {
		return root
	}
	n1OnLeft := contains(root.left, n1)
	n2OnLeft := contains(root.left, n2)
	if n1OnLeft != n2OnLeft {
		return root
	} else if n1OnLeft && n2OnLeft {
		return findFirstCommonAncestor(root.left, n1, n2)
	} else if !n1OnLeft && !n2OnLeft {
		return findFirstCommonAncestor(root.right, n1, n2)
	}
	return nil
}

func contains(root, n *Node) bool {
	if root == nil {
		return false
	}
	if root == n {
		return true
	}
	return contains(root.left, n) || contains(root.right, n)
}

// isValidBST validates a BST using Morris traversal in O(n) time, O(1) space.
func isValidBST(root *Node) bool {
	var pre *Node
	cur := root
	var tmp *Node
	for cur != nil {
		if cur.left == nil {
			if pre != nil && pre.data >= cur.data {
				return false
			}
			pre = cur
			cur = cur.right
		} else {
			tmp = cur.left
			for tmp.right != nil && tmp.right != cur {
				tmp = tmp.right
			}
			if tmp.right == nil {
				tmp.right = cur
				cur = cur.left
			} else {
				tmp.right = nil
				if pre != nil && pre.data >= cur.data {
					return false
				}
				pre = cur
				cur = cur.right
			}
		}
	}
	return true
}

// validateBST validates a BST within an (exclusive) range.
func validateBST(root *Node, min, max int) bool {
	if root == nil {
		return true
	}
	if root.data <= min || root.data >= max {
		return false
	}
	return validateBST(root.left, min, root.data) && validateBST(root.right, root.data, max)
}

// isValidBST1 validates a BST iteratively with explicit numeric bounds.
func isValidBST1(root *Node) bool {
	if root == nil {
		return true
	}
	queue := []BNode{{root, math.Inf(-1), math.Inf(1)}}
	for len(queue) > 0 {
		b := queue[0]
		queue = queue[1:]
		if float64(b.n.data) <= b.left || float64(b.n.data) >= b.right {
			return false
		}
		if b.n.left != nil {
			queue = append(queue, BNode{b.n.left, b.left, float64(b.n.data)})
		}
		if b.n.right != nil {
			queue = append(queue, BNode{b.n.right, float64(b.n.data), b.right})
		}
	}
	return true
}

// findSecondLargestValueInBST returns the second largest value in a BST in O(h).
func findSecondLargestValueInBST(root *Node) int {
	var secondMax int
	pre := root
	cur := root
	for cur.right != nil {
		pre = cur
		cur = cur.right
	}
	if cur.left != nil {
		cur = cur.left
		for cur.right != nil {
			cur = cur.right
		}
		secondMax = cur.data
	} else {
		if cur == root && pre == root {
			secondMax = intMin
		} else {
			secondMax = pre.data
		}
	}
	return secondMax
}

// secondLargestUtil prints the second largest element via reverse inorder.
func (t *Tree) secondLargestUtil(root *Node, c int) {
	if root == nil || c >= 2 {
		return
	}
	t.secondLargestUtil(root.right, c)
	c++
	if c == 2 {
		fmt.Print("2nd largest element is ", root.data)
		return
	}
	t.secondLargestUtil(root.left, c)
}

// KSmallestUsingMorris returns the k'th smallest element in O(1) extra space.
func (t *Tree) KSmallestUsingMorris(root *Node, k int) int {
	count := 0
	ksmall := intMin
	curr := root
	for curr != nil {
		if curr.left == nil {
			count++
			if count == k {
				ksmall = curr.data
			}
			curr = curr.right
		} else {
			pre := curr.left
			for pre.right != nil && pre.right != curr {
				pre = pre.right
			}
			if pre.right == nil {
				pre.right = curr
				curr = curr.left
			} else {
				pre.right = nil
				count++
				if count == k {
					ksmall = curr.data
				}
				curr = curr.right
			}
		}
	}
	return ksmall
}

// findKthNode_SMALLEST finds the kth smallest element in a BST.
func (t *Tree) findKthNode_SMALLEST(root *Node, k int) *Node {
	if root == nil {
		return nil
	}
	leftSize := t.findLeftTreeSize(root.left)
	if leftSize == k-1 {
		return root
	} else if leftSize < k-1 {
		t.findKthNode_SMALLEST(root.left, k)
	} else {
		t.findKthNode_SMALLEST(root.right, k-leftSize-1)
	}
	return nil
}

func (t *Tree) findLeftTreeSize(root *Node) int {
	if root == nil {
		return 0
	}
	return 1 + t.findLeftTreeSize(root.left) + t.findLeftTreeSize(root.right)
}

// insert_node builds a tree while counting left subtree nodes in each node.
func (t *Tree) insert_node(root *NodeT, node *NodeT) *NodeT {
	pTraverse := root
	currentParent := root
	for pTraverse != nil {
		currentParent = pTraverse
		if node.data < pTraverse.data {
			pTraverse.lCount++
			pTraverse = pTraverse.left
		} else {
			pTraverse = pTraverse.right
		}
	}
	if root == nil {
		root = node
	} else if node.data < currentParent.data {
		currentParent.left = node
	} else {
		currentParent.right = node
	}
	return root
}

// k_smallest_element returns the k'th smallest using maintained left counts.
func (t *Tree) k_smallest_element(root *NodeT, k int) int {
	ret := -1
	if root != nil {
		pTraverse := root
		for pTraverse != nil {
			if (pTraverse.lCount + 1) == k {
				ret = pTraverse.data
				break
			} else if k > pTraverse.lCount {
				k = k - (pTraverse.lCount + 1)
				pTraverse = pTraverse.right
			} else {
				pTraverse = pTraverse.left
			}
		}
	}
	return ret
}

// sortedArraytoBST builds a balanced BST from a sorted array.
func sortedArraytoBST(arr []int, start, end int) *Node {
	if end < start {
		return nil
	}
	mid := start + (end-start)/2
	tree := &Node{}
	tree.data = arr[mid]
	tree.left = sortedArraytoBST(arr, start, mid-1)
	tree.right = sortedArraytoBST(arr, mid+1, end)
	return tree
}

// constructBST builds a BST from a preorder traversal in O(n).
func (t *Tree) constructBST(pre []int) *Node {
	root := &Node{data: pre[0]}
	s := []*Node{root}
	for i := 1; i < len(pre); i++ {
		var temp *Node
		// Keep popping while the next value is greater than the stack's top.
		for len(s) > 0 && pre[i] > s[len(s)-1].data {
			temp = s[len(s)-1]
			s = s[:len(s)-1]
		}
		if temp != nil {
			temp.right = &Node{data: pre[i]}
			s = append(s, temp.right)
		} else {
			temp = s[len(s)-1]
			temp.left = &Node{data: pre[i]}
			s = append(s, temp.left)
		}
	}
	return root
}

// inOrderFromPreOrderBST prints the inorder traversal given a BST preorder.
func inOrderFromPreOrderBST(pre []int) {
	if pre == nil {
		return
	}
	if len(pre) < 2 {
		fmt.Println(pre[0])
	}
	var s []int
	s = append(s, pre[0])
	for i := 1; i < len(pre); i++ {
		for len(s) > 0 && pre[i] > s[len(s)-1] {
			fmt.Println(s[len(s)-1])
			s = s[:len(s)-1]
		}
		s = append(s, pre[i])
	}
	fmt.Println(s[len(s)-1])
}

// CorrectBST corrects a BST where two nodes were swapped.
func (t *Tree) CorrectBST(root *Node) {
	var first, middle, last, prev *Node
	t.CorrectBSTUtil(root, first, middle, last, prev)
	if first != nil && last != nil {
		t.swap(first.data, last.data)
	} else if first != nil && middle != nil {
		t.swap(first.data, middle.data)
	}
}

func (t *Tree) CorrectBSTUtil(root, first, middle, last, prev *Node) {
	if root != nil {
		t.CorrectBSTUtil(root.left, first, middle, last, prev)
		if prev != nil && root.data < prev.data {
			if first == nil {
				first = prev
				middle = root
			} else {
				last = root
			}
		}
		prev = root
		t.CorrectBSTUtil(root.right, first, middle, last, prev)
	}
}

// swap is a value swap (no-op on the caller's data, matching the Java source).
func (t *Tree) swap(a, b int) {
	tmp := a
	a = b
	b = tmp
	_, _ = a, b
}

// inorderSuccessor returns the inorder successor of p in a BST.
func (t *Tree) inorderSuccessor(root, p *Node) *Node {
	if root == nil || p == nil {
		return nil
	}
	var successor *Node
	for root != nil {
		if p.data < root.data {
			successor = root
			root = root.left
		} else {
			root = root.right
		}
	}
	return successor
}

// inorderSuccessorWithParent returns the inorder successor using parent links.
func inorderSuccessorWithParent(n *Node) *Node {
	if n == nil {
		return nil
	}
	if n.right != nil {
		return leftmostChild(n.right)
	}
	for n.parent != nil && n.parent.right == n {
		n = n.parent
	}
	return n.parent
}

func leftmostChild(n *Node) *Node {
	if n.left == nil {
		return n
	}
	return leftmostChild(n.left)
}

// preorderSuccessor returns the preorder successor using parent links.
func preorderSuccessor(n *Node) *Node {
	if n == nil {
		return nil
	}
	if n.left != nil {
		return n.left
	} else if n.right != nil {
		return n.right
	}
	for n.parent != nil && (n.parent.right == nil || n.parent.right == n) {
		n = n.parent
	}
	if n.parent == nil {
		return nil
	}
	return n.parent.right
}

// postorderSuccessor returns the postorder successor using parent links.
func postorderSuccessor(n *Node) *Node {
	if n == nil || n.parent == nil {
		return nil
	}
	if n.parent.right == n || n.parent.right == nil {
		return n.parent
	}
	return leftmostBottomChild(n.parent.right)
}

func leftmostBottomChild(n *Node) *Node {
	if n.left == nil && n.right == nil {
		return n
	}
	if n.left != nil {
		return leftmostBottomChild(n.left)
	}
	return leftmostBottomChild(n.right)
}

// createBST builds a minimal-height BST from a sorted, unique array.
func (t *Tree) createBST(a []int, start, end int) *Node {
	if start > end {
		return nil
	}
	mid := start + (end-start)/2
	n := &Node{data: a[mid]}
	n.left = t.createBST(a, start, mid-1)
	n.right = t.createBST(a, mid+1, end)
	return n
}
