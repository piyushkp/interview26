package main

import (
	"fmt"
	"strconv"
)

// iterativeDiameter computes the diameter of a binary tree iteratively.
func iterativeDiameter(root *Node1) int {
	if root == nil {
		return 0
	}
	var S []*Node1
	var O []*Node1
	maxDistance := 0
	S = append(S, root)
	for len(S) > 0 {
		node := S[len(S)-1]
		S = S[:len(S)-1]
		O = append(O, node)
		if node.left != nil {
			S = append(S, node.left)
		}
		if node.right != nil {
			S = append(S, node.right)
		}
	}
	for len(O) > 0 {
		node := O[len(O)-1]
		O = O[:len(O)-1]
		if node.left == nil {
			node.lHeight = 1
			node.maxDistance = 0
		} else {
			node.lHeight = maxInt(node.left.lHeight, node.left.rHeight) + 1
		}
		if node.right == nil {
			node.rHeight = 1
			node.maxDistance = 0
		} else {
			node.rHeight = maxInt(node.right.rHeight, node.right.lHeight) + 1
		}
		if node.left != nil && node.right != nil {
			temp := node.lHeight + node.rHeight - 1
			node.maxDistance = temp
			if maxDistance < temp {
				maxDistance = temp
			}
		}
	}
	return maxDistance
}

// diameterOfBinaryTree returns the diameter using a recursive depth helper.
func diameterOfBinaryTree(root *Node) int {
	maxDepth(root)
	return diameter
}

func maxDepth(root *Node) int {
	if root == nil {
		return 0
	}
	left := maxDepth(root.left)
	right := maxDepth(root.right)
	diameter = maxInt(diameter, left+right+1)
	return maxInt(left, right) + 1
}

// printDiameterOfBinaryTree prints the longest path of a binary tree.
func printDiameterOfBinaryTree(root *Node) string {
	longestPath(root)
	s := ""
	for len(pathStack) > 0 {
		top := pathStack[len(pathStack)-1]
		pathStack = pathStack[:len(pathStack)-1]
		s += strconv.Itoa(top.data) + " "
	}
	return s
}

func longestPath(root *Node) []*Node {
	if root == nil {
		return []*Node{}
	}
	l := longestPath(root.left)
	r := longestPath(root.right)
	if len(l)+len(r)+1 > diameter {
		diameter = len(l) + len(r) + 1
		var tmp []*Node
		tmp = append(tmp, l...)
		tmp = append(tmp, root)
		tmp = append(tmp, r...)
		pathStack = tmp
	}
	l = append(l, root)
	r = append(r, root)
	if len(l) > len(r) {
		return l
	}
	return r
}

// longestPathNaryTree returns the length of the longest path in an n-ary tree.
func longestPathNaryTree(root *NTree) int {
	longestPathNaryTreeUtil(root, make(map[*NTree]bool))
	fmt.Printf("start: - %c End: - %c\n", pathEndpoints[0], pathEndpoints[1])
	return maxSoFar
}

func longestPathNaryTreeUtil(root *NTree, visited map[*NTree]bool) int {
	large := 0
	small := 0
	visited[root] = true
	for _, next := range root.children {
		if !visited[next] {
			val := longestPathNaryTreeUtil(next, visited)
			if val > large {
				small = large
				large = val
				pathEndpoints[1] = pathEndpoints[0]
				pathEndpoints[0] = next.data
			} else if val > small && val != large {
				small = val
				pathEndpoints[1] = next.data
			}
		}
	}
	maxSoFar = maxInt(maxSoFar, small+large)
	return large + 1
}

// countPathsWithSum counts downward paths summing to targetSum. Time O(N).
func countPathsWithSum(node *Node, targetSum, runningSum int, pathCount map[int]int) int {
	if node == nil {
		return 0
	}
	runningSum += node.data
	sum := runningSum - targetSum
	totalPaths := pathCount[sum]
	if runningSum == targetSum {
		totalPaths++
	}
	incrementHashTable(pathCount, runningSum, 1)
	totalPaths += countPathsWithSum(node.left, targetSum, runningSum, pathCount)
	totalPaths += countPathsWithSum(node.right, targetSum, runningSum, pathCount)
	incrementHashTable(pathCount, runningSum, -1)
	return totalPaths
}

func incrementHashTable(hashTable map[int]int, key, delta int) {
	newCount := hashTable[key] + delta
	if newCount == 0 {
		delete(hashTable, key)
	} else {
		hashTable[key] = newCount
	}
}

// findSumUtil prints all paths that sum to a value. Time O(NlogN), space O(logN).
func (t *Tree) findSumUtil(node *Node, sum int, path []int, level int) {
	if node == nil {
		return
	}
	path[level] = node.data
	tsum := 0
	for i := level; i >= 0; i-- {
		tsum += path[i]
		if tsum == sum {
			printArr(path, i, level)
		}
	}
	t.findSumUtil(node.left, sum, path, level+1)
	t.findSumUtil(node.right, sum, path, level+1)
	path[level] = intMin
}

func (t *Tree) findSum(node *Node, sum int) {
	d := t.depth(node)
	path := make([]int, d)
	t.findSumUtil(node, sum, path, 0)
}

func printArr(path []int, start, end int) {
	for i := start; i <= end; i++ {
		fmt.Print(path[i], " ")
	}
	fmt.Println()
}

func (t *Tree) depth(node *Node) int {
	if node == nil {
		return 0
	}
	return 1 + maxInt(t.depth(node.left), t.depth(node.right))
}

// maxPathSum returns the binary tree maximum path sum (downward variant).
func (t *Tree) maxPathSum(root *Node) int {
	if root == nil {
		return 0
	}
	maxLeft := t.maxPathSum(root.left)
	maxRight := t.maxPathSum(root.right)
	leftLen := 0
	rightLen := 0
	if root.left != nil {
		leftLen = maxInt(root.left.data, 0)
	}
	if root.right != nil {
		rightLen = maxInt(root.right.data, 0)
	}
	maxLength := root.data
	if leftLen > 0 {
		maxLength += leftLen
	}
	if rightLen > 0 {
		maxLength += rightLen
	}
	if root.left != nil {
		maxLength = maxInt(maxLeft, maxLength)
	}
	if root.right != nil {
		maxLength = maxInt(maxRight, maxLength)
	}
	root.data = maxInt(leftLen, rightLen) + root.data
	return maxLength
}

// maxSumSubtree returns the root of the subtree with the largest sum.
func (t *Tree) maxSumSubtree(root *Node) *Node {
	if root == nil {
		return nil
	}
	maxsum := 0
	var res *Node
	t.maxSumHelper(root, res, maxsum)
	return res
}

func (t *Tree) maxSumHelper(p *Node, res *Node, maxsum int) int {
	if p == nil {
		return 0
	}
	lsum := t.maxSumHelper(p.left, res, maxsum)
	rsum := t.maxSumHelper(p.right, res, maxsum)
	total := lsum + rsum + p.data
	if total > maxsum {
		maxsum = total
		res = p
	}
	return total
}

// FindMaxSumSubtree returns the maximum sum of any subtree (triangle).
func (t *Tree) FindMaxSumSubtree(root *Node) int {
	maxSum := 0
	maxSum = t.MaxSumSubtree(root, maxSum)
	return maxSum
}

func (t *Tree) MaxSumSubtree(root *Node, maxSum int) int {
	sum := 0
	lsum := 0
	rsum := 0
	if root == nil {
		return 0
	}
	if root.left != nil {
		lsum = t.MaxSumSubtree(root.left, maxSum)
	}
	if root.right != nil {
		rsum = t.MaxSumSubtree(root.right, maxSum)
	}
	sum = root.data + lsum + rsum
	if maxSum < sum {
		maxSum = sum
	}
	return maxSum
}

// getLevel returns the level of a node holding data (root level = 1).
func (t *Tree) getLevel(node *Node, data, level int) int {
	if node == nil {
		return 0
	}
	if node.data == data {
		return level
	}
	downlevel := t.getLevel(node.left, data, level+1)
	if downlevel != 0 {
		return downlevel
	}
	downlevel = t.getLevel(node.right, data, level+1)
	return downlevel
}

// isSibling reports whether a and b are siblings.
func (t *Tree) isSibling(root, a, b *Node) bool {
	if root == nil {
		return false
	}
	return (root.left == a && root.right == b) ||
		(root.left == b && root.right == a) ||
		t.isSibling(root.left, a, b) ||
		t.isSibling(root.right, a, b)
}

// isCousin reports whether a and b are cousins in a binary tree.
func (t *Tree) isCousin(root, a, b *Node) bool {
	if t.getLevel(root, a.data, 1) == t.getLevel(root, b.data, 1) && !t.isSibling(root, a, b) {
		return true
	}
	return false
}

// find_sum finds two BST nodes that add up to search. O(n) time, O(logn) space.
func (t *Tree) find_sum(search int, root *Node) []int {
	var s1, s2 []*Node
	curr1 := root
	curr2 := root
	done1, done2 := false, false
	val1, val2 := 0, 0
	var result []int
	for {
		for !done1 {
			if curr1 != nil {
				s1 = append(s1, curr1)
				curr1 = curr1.left
			} else if len(s1) == 0 {
				done1 = true
			} else {
				curr1 = s1[len(s1)-1]
				s1 = s1[:len(s1)-1]
				val1 = curr1.data
				curr1 = curr1.right
				done1 = true
			}
		}
		for !done2 {
			if curr2 != nil {
				s2 = append(s2, curr2)
				curr2 = curr2.right
			} else if len(s2) == 0 {
				done2 = true
			} else {
				curr2 = s2[len(s2)-1]
				s2 = s2[:len(s2)-1]
				val2 = curr2.data
				curr2 = curr2.left
				done2 = true
			}
		}
		if val1+val2 == search {
			result = append(result, val1)
			result = append(result, val2)
			return result
		} else if val1+val2 > search {
			done2 = false
		} else {
			done1 = false
		}
	}
}

// printSpecificLevelOrder prints a perfect binary tree in a specific order.
func (t *Tree) printSpecificLevelOrder(root *Node) {
	if root == nil {
		return
	}
	fmt.Print(root.data)
	if root.left != nil {
		fmt.Print(root.left.data, " ", root.right.data)
	}
	if root.left.left == nil {
		return
	}
	var q []*Node
	q = append(q, root.left)
	q = append(q, root.right)
	var first, second *Node
	for len(q) > 0 {
		first = q[0]
		q = q[1:]
		second = q[0]
		q = q[1:]
		fmt.Print(first.left.data, " ", second.right.data)
		fmt.Print(first.right.data, " ", second.left.data)
		if first.left.left != nil {
			q = append(q, first.left)
			q = append(q, second.right)
			q = append(q, first.right)
			q = append(q, second.left)
		}
	}
}

// leftLeavesSum returns the sum of all left leaves. O(n).
func (t *Tree) leftLeavesSum(root *Node) int {
	res := 0
	if root != nil {
		if t.isLeaf(root.left) {
			res += root.left.data
		} else {
			res += t.leftLeavesSum(root.left)
		}
		res += t.leftLeavesSum(root.right)
	}
	return res
}

func (t *Tree) isLeaf(node *Node) bool {
	if node == nil {
		return false
	}
	if node.left == nil && node.right == nil {
		return true
	}
	return false
}

// binaryTreePaths returns all root-to-leaf paths as strings.
func (t *Tree) binaryTreePaths(root *Node) []string {
	var res []string
	t.pathsHelper(&res, root, "")
	return res
}

func (t *Tree) pathsHelper(res *[]string, root *Node, path string) {
	if root == nil {
		return
	}
	path += strconv.Itoa(root.data)
	if root.left == nil && root.right == nil {
		*res = append(*res, path)
	} else {
		path += "->"
		t.pathsHelper(res, root.left, path)
		t.pathsHelper(res, root.right, path)
	}
}

// printPaths walks root-to-leaf paths using an explicit stack.
func (t *Tree) printPaths(root *Node) {
	if root == nil {
		return
	}
	s := []*Node{root}
	temp := root.left
	for len(s) != 0 {
		for temp != nil {
			s = append(s, temp)
			temp = temp.left
		}
		top := s[len(s)-1]
		if !top.isVisited {
			top.isVisited = true
			temp = top.right
			if temp == nil {
				t.printThePath(s)
				s = s[:len(s)-1]
			}
		} else {
			s = s[:len(s)-1]
		}
	}
}

func (t *Tree) printThePath(s []*Node) {
	// get an iterator and print the stack
}

// printAllPossiblePath prints every root-to-leaf path.
func printAllPossiblePath(node *Node, nodelist []*Node) {
	if node != nil {
		nodelist = append(nodelist, node)
		if node.left != nil {
			printAllPossiblePath(node.left, nodelist)
		}
		if node.right != nil {
			printAllPossiblePath(node.right, nodelist)
		} else if node.left == nil && node.right == nil {
			for i := 0; i < len(nodelist); i++ {
				fmt.Print(nodelist[i].data)
			}
			fmt.Println()
		}
	}
}

// printLongestPath does a BFS while recording each node's parent.
func (t *Tree) printLongestPath(root *Node) {
	var queue []*Node
	m := make(map[*Node]*Node)
	m[root] = nil
	var tmp *Node
	queue = append(queue, root)
	for len(queue) > 0 {
		tmp = queue[0]
		queue = queue[1:]
		if tmp.left != nil {
			m[tmp.left] = tmp
			queue = append(queue, tmp.left)
		}
		if tmp.right != nil {
			queue = append(queue, tmp.right)
			m[tmp.right] = tmp
		}
	}
	// printTopToBottomPath(tmp, m) would walk the parent map upward from tmp.
}

// RootToLeafPathPrint prints every root-to-leaf path. Time O(n), space O(n).
func RootToLeafPathPrint(root *Node) {
	if root == nil {
		return
	}
	stack := []nodePath{{root, strconv.Itoa(root.data)}}
	for len(stack) > 0 {
		top := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		temp := top.node
		path := top.path
		if temp.right != nil {
			stack = append(stack, nodePath{temp.right, path + strconv.Itoa(temp.right.data)})
		}
		if temp.left != nil {
			stack = append(stack, nodePath{temp.left, path + strconv.Itoa(temp.left.data)})
		}
		if temp.left == nil && temp.right == nil {
			fmt.Println(path)
		}
	}
}

// hasPathSum reports whether a root-to-leaf path sums to sum.
func (t *Tree) hasPathSum(root *Node, sum int) bool {
	if root == nil {
		return false
	}
	if root.data == sum && root.left == nil && root.right == nil {
		return true
	}
	return t.hasPathSum(root.left, sum-root.data) || t.hasPathSum(root.right, sum-root.data)
}

// printAllPathSum prints all paths from root that add up to sum.
func printAllPathSum(root *Node, sum int, path string) {
	if root != nil {
		if root.data > sum {
			return
		}
		path += " " + strconv.Itoa(root.data)
		if root.data == sum && root.left == nil && root.right == nil {
			fmt.Println(path)
		}
		printAllPathSum(root.left, sum-root.data, path)
		printAllPathSum(root.right, sum-root.data, path)
	}
}
