package main

import (
	"fmt"
	"strconv"
	"strings"
)

// BSTIterator yields BST values in ascending order with O(h) memory.
type BSTIterator struct {
	stack []*Node
}

// BSTIteratorUsingMorris yields BST values using Morris traversal in O(1) space.
type BSTIteratorUsingMorris struct {
	root *Node
	cur  *Node
}

// Serialize encodes a binary tree to a string. A trailing ' marks an internal
// node and '/' marks a missing child of a single-child node.
func Serialize(root *Node) string {
	if root == nil {
		return ""
	}
	nodeStack := []*Node{root}
	var sb strings.Builder
	for len(nodeStack) > 0 {
		node := nodeStack[len(nodeStack)-1]
		nodeStack = nodeStack[:len(nodeStack)-1]
		if node != nil {
			if node.left != nil && node.right != nil {
				sb.WriteString(strconv.Itoa(node.data) + "'")
				nodeStack = append(nodeStack, node.right)
				nodeStack = append(nodeStack, node.left)
			} else if node.left == nil && node.right == nil {
				sb.WriteString(strconv.Itoa(node.data))
			} else {
				sb.WriteString(strconv.Itoa(node.data) + "'")
				nodeStack = append(nodeStack, node.right)
				nodeStack = append(nodeStack, node.left)
			}
		} else {
			sb.WriteString("/")
		}
	}
	return sb.String()
}

// Deserialize rebuilds a tree from the Serialize encoding (uses currentIndex).
func Deserialize(str string) *Node {
	var root *Node
	if currentIndex > len(str) {
		return nil
	} else if str[currentIndex] == '/' {
		return nil
	} else if str[currentIndex+1] == '\'' {
		root = &Node{data: int(str[currentIndex])}
		currentIndex += 2
		root.left = Deserialize(str)
		root.right = Deserialize(str)
	} else {
		root = &Node{data: int(str[currentIndex])}
		root.left = nil
		root.right = nil
		currentIndex++
		return root
	}
	return root
}

// serialize encodes a BST to a single string using splitter.
func (t *Tree) serialize(root *Node) string {
	var sb strings.Builder
	t.buildString(root, &sb)
	return sb.String()
}

func (t *Tree) buildString(root *Node, sb *strings.Builder) {
	if root == nil {
		return
	}
	sb.WriteString(strconv.Itoa(root.data))
	sb.WriteString(splitter)
	t.buildString(root.left, sb)
	t.buildString(root.right, sb)
}

// deserialize decodes the serialize() encoding back into a BST.
func (t *Tree) deserialize(data string) *Node {
	if len(data) == 0 {
		return nil
	}
	pos := []int{0}
	return t.buildTreeFromNodes(strings.Split(data, splitter), pos, intMin, intMax)
}

func (t *Tree) buildTreeFromNodes(nodes []string, pos []int, min, max int) *Node {
	if pos[0] == len(nodes) {
		return nil
	}
	val, _ := strconv.Atoi(nodes[pos[0]])
	if val < min || val > max {
		return nil // outside of the boundary
	}
	cur := &Node{data: val}
	pos[0]++
	cur.left = t.buildTreeFromNodes(nodes, pos, min, val)
	cur.right = t.buildTreeFromNodes(nodes, pos, val, max)
	return cur
}

// verticalSumDLL prints the vertical sum of a binary tree using a DLL.
func verticalSumDLL(root *Node) {
	dllNode := &DLL{data: 0}
	verticalSumDLLUtil(root, dllNode)
	for dllNode.prev != nil {
		dllNode = dllNode.prev
	}
	for dllNode != nil {
		fmt.Print(dllNode.data, " ")
		dllNode = dllNode.next
	}
}

func verticalSumDLLUtil(tnode *Node, dllNode *DLL) {
	dllNode.data = dllNode.data + tnode.data
	if tnode.left != nil {
		if dllNode.prev == nil {
			dllNode.prev = &DLL{data: 0}
			dllNode.prev.next = dllNode
		}
		verticalSumDLLUtil(tnode.left, dllNode.prev)
	}
	if tnode.right != nil {
		if dllNode.next == nil {
			dllNode.next = &DLL{data: 0}
			dllNode.next.prev = dllNode
		}
		verticalSumDLLUtil(tnode.right, dllNode.next)
	}
}

// verticalSUM accumulates node data into sum buckets keyed by horizontal dist.
func (t *Tree) verticalSUM(root *Node, sum []int, hd, min, max int) {
	index := hd + hdOffset/2
	if index < min {
		min = index
	}
	if index > max {
		max = index
	}
	sum[index] += root.data
	t.verticalSUM(root.left, sum, hd-1, min, max)
	t.verticalSUM(root.right, sum, hd+1, min, max)
}

// FlipTree flips a tree (whose right nodes are leaves) upside down.
func (t *Tree) FlipTree(root *Node) *Node {
	if root == nil {
		return nil
	}
	if root.left == nil && root.right == nil {
		return root.left
	}
	newRoot := t.FlipTree(root.left)
	root.left.left = root.right
	root.left.right = root
	root.left = nil
	root.right = nil
	return newRoot
}

// BuildMaxHeap builds a max-heap in place.
func BuildMaxHeap(arr []int) {
	for i := len(arr) - 1; i >= 0; i-- {
		MaxHeapify(arr, i)
	}
}

func MaxHeapify(arr []int, i int) {
	left := 2*i + 1
	right := 2*i + 2
	largest := i
	if left < len(arr) && arr[left] > arr[largest] {
		largest = left
	}
	if right < len(arr) && arr[right] > arr[largest] {
		largest = right
	}
	if largest != i {
		arr[i], arr[largest] = arr[largest], arr[i]
		MaxHeapify(arr, largest)
	}
}

// isBalanced3 checks whether a tree is height balanced in O(N) time, O(H) space.
func isBalanced3(n *Node) bool {
	return getHeightBalanced(n) != -1
}

func getHeightBalanced(n *Node) int {
	if n == nil {
		return 0
	}
	leftHeight := getHeightBalanced(n.left)
	if leftHeight == -1 {
		return -1
	}
	rightHeight := getHeightBalanced(n.right)
	if rightHeight == -1 {
		return -1
	}
	if absInt(leftHeight-rightHeight) > 1 {
		return -1
	}
	return 1 + maxInt(leftHeight, rightHeight)
}

// isSuperBalanced checks whether any two leaf depths differ by more than one.
func isSuperBalanced(root *Node) bool {
	if root == nil {
		return true
	}
	stack := []nodeIntPair{{root, 0}}
	var set []int
	for len(stack) > 0 {
		node := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		depth := node.val
		if node.node.left == nil && node.node.right == nil {
			found := false
			for _, d := range set {
				if d == depth {
					found = true
					break
				}
			}
			if !found {
				set = append(set, depth)
			}
			if len(set) > 2 || (len(set) == 2 && absInt(set[0]-set[1]) > 1) {
				return false
			}
		} else {
			if node.node.left != nil {
				stack = append(stack, nodeIntPair{node.node.left, depth + 1})
			}
			if node.node.right != nil {
				stack = append(stack, nodeIntPair{node.node.right, depth + 1})
			}
		}
	}
	return true
}

// morrisTraverse prints an in-order traversal using Morris traversal.
func (t *Tree) morrisTraverse(root *Node) {
	for root != nil {
		if root.left == nil {
			fmt.Println(root.data)
			root = root.right
		} else {
			ptr := root.left
			for ptr.right != nil && ptr.right != root {
				ptr = ptr.right
			}
			if ptr.right == nil {
				ptr.right = root
				root = root.left
			} else {
				ptr.right = nil
				fmt.Println(root.data)
				root = root.right
			}
		}
	}
}

// BTtoDLLmorris converts a binary tree to a doubly linked list via Morris.
func (t *Tree) BTtoDLLmorris(root, head, prev *Node) {
	if root == nil {
		return
	}
	curr := root
	for curr != nil {
		if curr.left == nil {
			if head == nil {
				head = curr
				prev = curr
			} else {
				prev.right = curr
				curr.left = prev
				prev = curr
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
				if head == nil {
					head = curr
					prev = curr
				} else {
					prev.right = curr
					curr.left = prev
					prev = curr
				}
				pre.right = nil
				curr = curr.right
			}
		}
	}
}

// treeToDoublyList converts a binary tree to a circular doubly linked list.
func (t *Tree) treeToDoublyList(root, prev, head *Node) {
	if root == nil {
		return
	}
	t.treeToDoublyList(root.left, prev, head)
	root.left = prev
	if prev != nil {
		prev.right = root
	} else {
		head = root
	}
	right := root.right
	head.left = root
	root.right = head
	prev = root
	t.treeToDoublyList(right, prev, head)
}

// min_diff returns whichever of a or b is closer to key.
func (t *Tree) min_diff(a, b, key int) int {
	if absInt(a-key) <= absInt(b-key) {
		return a
	}
	return b
}

// searchClosest finds the value in a BST closest to key.
func (t *Tree) searchClosest(root *Node, key int) int {
	closeVal := intMax
	if root == nil {
		return 0
	}
	if key == root.data {
		return key
	}
	closeVal = t.min_diff(closeVal, root.data, key)
	if key > root.data && root.right != nil {
		closeVal = t.min_diff(closeVal, t.searchClosest(root.right, key), key)
	}
	if key < root.data && root.left != nil {
		closeVal = t.min_diff(closeVal, t.searchClosest(root.left, key), key)
	}
	return closeVal
}

// trimBST trims a BST so all values lie within [minValue, maxValue].
func (t *Tree) trimBST(root *Node, minValue, maxValue int) *Node {
	if root == nil {
		return nil
	}
	root.left = t.trimBST(root.left, minValue, maxValue)
	root.right = t.trimBST(root.right, minValue, maxValue)
	if minValue <= root.data && root.data <= maxValue {
		return root
	}
	if root.data < minValue {
		return root.right
	}
	if root.data > maxValue {
		return root.left
	}
	return nil
}

// maxDepthIter returns the maximum depth of a binary tree iteratively.
func (t *Tree) maxDepthIter(root *Node) int {
	if root == nil {
		return 0
	}
	queue := []*Node{root}
	count := 0
	for len(queue) > 0 {
		size := len(queue)
		for size > 0 {
			node := queue[0]
			queue = queue[1:]
			if node.left != nil {
				queue = append(queue, node.left)
			}
			if node.right != nil {
				queue = append(queue, node.right)
			}
			size--
		}
		count++
	}
	return count
}

// deepestLeftLeaf returns the deepest left leaf via right-to-left BFS.
func (t *Tree) deepestLeftLeaf(root *Node) *Node {
	queue := []*Node{root}
	for len(queue) > 0 {
		root = queue[0]
		queue = queue[1:]
		if root.right != nil {
			queue = append(queue, root.right)
		}
		if root.left != nil {
			queue = append(queue, root.left)
		}
	}
	return root
}

// deepestNode returns the deepest node in a binary tree.
func (t *Tree) deepestNode(root *Node) *Node {
	if root == nil {
		return nil
	}
	var queue []*Node
	var tmp *Node
	queue = append(queue, root)
	for len(queue) > 0 {
		tmp = queue[0]
		queue = queue[1:]
		if tmp.left != nil {
			queue = append(queue, tmp.left)
		}
		if tmp.right != nil {
			queue = append(queue, tmp.right)
		}
	}
	return tmp
}

// find records the value of the deepest node (uses instance bookkeeping).
func (t *Tree) find(root *Node, level int) {
	if root != nil {
		t.find(root.left, level+1)
		if level > t.deepestLevel {
			t.value = root.data
			t.deepestLevel = level
		}
		t.find(root.right, level+1)
	}
}

// createLevelLinkedList builds a list of nodes for each depth of the tree.
func createLevelLinkedList(root *Node) [][]*Node {
	var result [][]*Node
	var current []*Node
	if root != nil {
		current = append(current, root)
	}
	for len(current) > 0 {
		result = append(result, current)
		parents := current
		current = nil
		for _, parent := range parents {
			if parent.left != nil {
				current = append(current, parent.left)
			}
			if parent.right != nil {
				current = append(current, parent.right)
			}
		}
	}
	return result
}

// containsTree reports whether t2 is a subtree of tl.
func (t *Tree) containsTree(tl, t2 *Node) bool {
	if t2 == nil {
		return true
	}
	return t.subTree(tl, t2)
}

func (t *Tree) subTree(rl, r2 *Node) bool {
	if rl == nil {
		return false
	}
	if rl.data == r2.data {
		if t.matchTree(rl, r2) {
			return true
		}
	}
	return t.subTree(rl.left, r2) || t.subTree(rl.right, r2)
}

func (t *Tree) matchTree(rl, r2 *Node) bool {
	if r2 == nil && rl == nil {
		return true
	}
	if rl == nil || r2 == nil {
		return false
	}
	if rl.data != r2.data {
		return false
	}
	return t.matchTree(rl.left, r2.left) && t.matchTree(rl.right, r2.right)
}

// isTreeUnivalRoot reports whether the whole tree is single-valued.
func isTreeUnivalRoot(root *Node) bool {
	if root == nil {
		return true
	}
	return isTreeUnival(root.left, root.data) && isTreeUnival(root.right, root.data)
}

func isTreeUnival(n *Node, val int) bool {
	if n == nil {
		return true
	}
	if n.data != val {
		return false
	}
	return isTreeUnival(n.left, val) && isTreeUnival(n.right, val)
}

// countSingleRec counts single-valued (unival) subtrees via t.count.
func (t *Tree) countSingleRec(node *Node) bool {
	if node == nil {
		return true
	}
	left := t.countSingleRec(node.left)
	right := t.countSingleRec(node.right)
	if left == false || right == false {
		return false
	}
	if node.left != nil && node.data != node.left.data {
		return false
	}
	if node.right != nil && node.data != node.right.data {
		return false
	}
	t.count++
	return true
}

// findNodesCountBelowLevel counts nodes below a given level (uses countN).
func findNodesCountBelowLevel(root *Node, curr, level int) int {
	if root == nil {
		return 0
	}
	if curr > level {
		countN++
	}
	findNodesCountBelowLevel(root.left, curr+1, level)
	findNodesCountBelowLevel(root.right, curr+1, level)
	return countN
}

// findLevelWithMaxNodes returns the level (0-based) with the most nodes.
func findLevelWithMaxNodes(root *NTree) int {
	if root == nil {
		return 0
	}
	q := []*NTree{root}
	maxNodes := 1
	level := 0
	maxLevel := 0
	for {
		nodeCount := len(q)
		if nodeCount > maxNodes {
			maxNodes = nodeCount
			maxLevel = level
		}
		if nodeCount == 0 {
			break
		}
		for nodeCount > 0 {
			node := q[0]
			q = q[1:]
			for _, child := range node.children {
				q = append(q, child)
			}
			nodeCount--
		}
		level++
	}
	return maxLevel
}

// convertTtoBT converts a ternary expression to a binary tree (parent links).
func convertTtoBT(values []rune) *Node {
	n := &Node{data: int(values[0])}
	for i := 1; i < len(values); i += 2 {
		if values[i] == '?' {
			n.left = &Node{data: int(values[i+1])}
			n.left.parent = n
			n = n.left
		} else if values[i] == ':' {
			n = n.parent
			for n.right != nil && n.parent != nil {
				n = n.parent
			}
			n.right = &Node{data: int(values[i+1])}
			n.right.parent = n
			n = n.right
		}
	}
	return n
}

// convert builds a binary tree from a ternary expression using a stack.
func convert(expr []rune) *Node {
	if len(expr) == 0 {
		return nil
	}
	root := &Node{data: int(expr[0])}
	stack := []*Node{root}
	for i := 1; i < len(expr); i += 2 {
		node := &Node{data: int(expr[i+1])}
		if expr[i] == '?' {
			stack[len(stack)-1].left = node
		} else if expr[i] == ':' {
			stack = stack[:len(stack)-1]
			for stack[len(stack)-1].right != nil {
				stack = stack[:len(stack)-1]
			}
			stack[len(stack)-1].right = node
		}
		stack = append(stack, node)
	}
	return root
}

// convertBack converts a binary tree back into a ternary expression string.
func convertBack(root *Node) string {
	stack := []*Node{root}
	var sb strings.Builder
	for len(stack) > 0 {
		node := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if node.left != nil && node.right != nil {
			stack = append(stack, node.right)
			stack = append(stack, node.left)
			sb.WriteString(strconv.Itoa(node.data) + "?")
		} else if node.left == nil && node.right == nil {
			sb.WriteString(strconv.Itoa(node.data) + ":")
		}
	}
	s := sb.String()
	if len(s) > 0 {
		s = s[:len(s)-1]
	}
	return s
}

// upsideDownBinaryTree flips a {1,2,3,4,5}-style tree upside down.
func (t *Tree) upsideDownBinaryTree(root *Node) *Node {
	curr := root
	var next *Node
	var temp *Node
	var prev *Node
	for curr != nil {
		next = curr.left
		curr.left = temp
		temp = curr.right
		curr.right = prev
		prev = curr
		curr = next
	}
	return prev
}

// getLargestSizeOfPerfactTree returns the largest perfect subtree size.
func getLargestSizeOfPerfactTree(root *Node) int {
	if root.left == nil && root.right == nil {
		return 1
	}
	if root.left == nil || root.right == nil {
		return 0
	}
	left := getLargestSizeOfPerfactTree(root.left)
	right := getLargestSizeOfPerfactTree(root.right)
	if left < 1 || right < 1 {
		return 1
	}
	if left == right {
		maxSize = left + right + 1
	} else {
		maxSize = maxInt(left, right)
	}
	return maxSize
}

// countSubtrees counts subtrees having an odd count of even numbers.
func (t *Tree) countSubtrees(root *Node) int {
	if root == nil {
		return 0
	}
	c := t.countSubtrees(root.left)
	c += t.countSubtrees(root.right)
	if root.data%2 == 0 {
		c += 1
	}
	if c%2 != 0 {
		t.count++
	}
	return c
}

// leafSimilar reports whether two trees have the same leaf value sequence.
func leafSimilar(root1, root2 *Node) bool {
	s1 := []*Node{root1}
	s2 := []*Node{root2}
	for len(s1) > 0 && len(s2) > 0 {
		var d1, d2 int
		d1, s1 = dfs(s1)
		d2, s2 = dfs(s2)
		if d1 != d2 {
			return false
		}
	}
	return len(s1) == 0 && len(s2) == 0
}

// dfs pops the stack until a leaf is found and returns its data plus the
// updated stack (Go can't mutate the caller's slice header, so we return it).
func dfs(s []*Node) (int, []*Node) {
	for {
		node := s[len(s)-1]
		s = s[:len(s)-1]
		if node.right != nil {
			s = append(s, node.right)
		}
		if node.left != nil {
			s = append(s, node.left)
		}
		if node.left == nil && node.right == nil {
			return node.data, s
		}
	}
}

// pruneTree removes every subtree that does not contain a 1.
func pruneTree(root *Node) *Node {
	if root == nil {
		return nil
	}
	root.left = pruneTree(root.left)
	root.right = pruneTree(root.right)
	if root.left == nil && root.right == nil && root.data == 0 {
		return nil
	}
	return root
}

// buildTreeFromRelations builds a binary tree from child->parent relationships.
func buildTreeFromRelations(data []Relation) *Node {
	m := make(map[int]*Node)
	var root *Node
	for _, r := range data {
		child := m[r.child]
		if child == nil {
			child = &Node{}
			child.data = r.child
			m[r.child] = child
		}
		if r.parent == nil {
			root = child
			continue
		}
		parent := m[*r.parent]
		if parent == nil {
			parent = &Node{}
			parent.data = *r.parent
			m[*r.parent] = parent
		}
		if r.isLeft {
			parent.left = child
		} else {
			parent.right = child
		}
	}
	return root
}

// validTree checks whether the given undirected edges form a valid tree.
func (t *Tree) validTree(n int, edges [][]int) bool {
	nums := make([]int, n)
	for i := range nums {
		nums[i] = -1
	}
	for i := 0; i < len(edges); i++ {
		x := t.findUF(nums, edges[i][0])
		y := t.findUF(nums, edges[i][1])
		if x == y {
			return false
		}
		nums[x] = y
	}
	return len(edges) == n-1
}

func (t *Tree) findUF(nums []int, i int) int {
	if nums[i] == -1 {
		return i
	}
	return t.findUF(nums, nums[i])
}

// insert adds a value into a RankNode order-statistics tree.
func (r *RankNode) insert(d int) {
	if d <= r.data {
		if r.left != nil {
			r.left.insert(d)
		} else {
			r.left = &RankNode{data: d}
		}
		r.leftSize++
	} else {
		if r.right != nil {
			r.right.insert(d)
		} else {
			r.right = &RankNode{data: d}
		}
	}
}

// getRank returns the rank (count of smaller-or-equal values) of d.
func (r *RankNode) getRank(d int) int {
	if d == r.data {
		return r.leftSize
	} else if d < r.data {
		if r.left == nil {
			return -1
		}
		return r.left.getRank(d)
	}
	rightRank := -1
	if r.right != nil {
		rightRank = r.right.getRank(d)
	}
	if rightRank == -1 {
		return -1
	}
	return r.leftSize + 1 + rightRank
}

// newBSTIterator builds an in-order BST iterator seeded from root.
func newBSTIterator(root *Node) *BSTIterator {
	it := &BSTIterator{}
	it.pushAll(root)
	return it
}

func (it *BSTIterator) hasNext() bool {
	return len(it.stack) != 0
}

func (it *BSTIterator) next() int {
	tmpNode := it.stack[len(it.stack)-1]
	it.stack = it.stack[:len(it.stack)-1]
	it.pushAll(tmpNode.right)
	return tmpNode.data
}

func (it *BSTIterator) pushAll(node *Node) {
	for node != nil {
		it.stack = append(it.stack, node)
		node = node.left
	}
}

// newBSTIteratorUsingMorris builds a Morris-based BST iterator.
func newBSTIteratorUsingMorris(root *Node) *BSTIteratorUsingMorris {
	return &BSTIteratorUsingMorris{root: root, cur: root}
}

func (it *BSTIteratorUsingMorris) hasNext() bool {
	return it.cur != nil
}

func (it *BSTIteratorUsingMorris) next() int {
	r := 0
	for it.cur != nil {
		if it.cur.left == nil {
			r = it.cur.data
			it.cur = it.cur.right
			break
		}
		node := it.cur.left
		for node.right != nil && node.right != it.cur {
			node = node.right
		}
		if node.right == nil {
			node.right = it.cur
			it.cur = it.cur.left
		} else {
			node.right = nil
			r = it.cur.data
			it.cur = it.cur.right
			break
		}
	}
	return r
}
