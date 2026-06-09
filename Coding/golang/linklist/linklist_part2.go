package main

import (
	"fmt"
	"math"
)

// printReverse1 prints the list backwards in O(n) time and O(sqrt(n)) space,
// without modifying the list. Faithful port of the reference implementation,
// including its quirks.
func printReverse1(head *Node) {
	node := head
	n := 0
	for node != nil {
		node = node.next
		n++
	}
	node = head
	k := int(math.Sqrt(float64(n)))
	stack := []*Node{}
	stack = append(stack, node)
	temp := 0
	for i := 0; i < n; i++ {
		if temp == k {
			stack = append(stack, node)
			temp = 0
		}
		node = node.next
		temp++
	}
	stack2 := []*Node{}
	for len(stack) > 0 {
		t := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		stack2 = append(stack2, t)
		for i := 1; i < k; i++ {
			stack2 = append(stack2, t.next)
			t = t.next
		}
		for len(stack2) > 0 {
			top := stack2[len(stack2)-1]
			stack2 = stack2[:len(stack2)-1]
			fmt.Print(top.data)
		}
	}
}

// printReverse prints the reverse of a list recursively. Time O(n) space O(n).
func printReverse(head *Node) {
	if head == nil {
		return
	}
	printReverse(head.next)
	fmt.Printf("%d ", head.data)
}

// Reverse reverses the list iteratively. Time O(n) space O(1).
func Reverse(head *Node) {
	currentNode := head
	var prevNode *Node
	var nextNode *Node
	for currentNode != nil {
		nextNode = currentNode.next
		currentNode.next = prevNode
		prevNode = currentNode
		currentNode = nextNode
	}
	head = prevNode
}

// reverseUtil reverses a singly linked list recursively.
func (l *LinkList) reverseUtil(curr, prev *Node) *Node {
	if curr.next == nil {
		l.head = curr
		curr.next = prev
		return nil
	}
	next1 := curr.next
	curr.next = prev
	l.reverseUtil(next1, curr)
	return l.head
}

// reverseKGroup reverses a linked list in groups of a given size.
// Input: 1->2->3->4->5->6->7->8 and k = 3  Output: 3->2->1->6->5->4->8->7.
func reverseKGroup(head *Node, k int) *Node {
	var begin *Node
	if head == nil || head.next == nil || k == 1 {
		return head
	}
	dummyhead := newNode(-1)
	dummyhead.next = head
	begin = dummyhead
	i := 0
	for head != nil {
		i++
		if i%k == 0 {
			begin = reverse(begin, head.next)
			head = begin.next
		} else {
			head = head.next
		}
	}
	return dummyhead.next
}

// reverse reverses the sublist (begin, end) exclusive and returns its new tail.
func reverse(begin, end *Node) *Node {
	curr := begin.next
	var next, first *Node
	prev := begin
	first = curr
	for curr != end {
		next = curr.next
		curr.next = prev
		prev = curr
		curr = next
	}
	begin.next = prev
	first.next = curr
	return first
}

// findCircular detects a cycle. Time O(n) space O(1).
func (l *LinkList) findCircular(head *Node) bool {
	slower, faster := head, head
	for slower != nil && faster != nil && faster.next != nil {
		slower = slower.next
		faster = faster.next.next
		if faster == slower {
			return true
		}
	}
	return false
}

// detectAndRemoveLoop detects a loop and removes it from the list.
func (l *LinkList) detectAndRemoveLoop(node *Node) {
	slow := l.head
	fast := l.head
	for fast != nil && fast.next != nil {
		slow = slow.next
		fast = fast.next.next
		if slow == fast {
			slow = l.head
			for slow != fast.next {
				slow = slow.next
				fast = fast.next
			}
			fast.next = nil
		}
	}
}

// printNthFromLast prints the kth node from the end of the list.
func (l *LinkList) printNthFromLast(head *Node, k int) {
	mainPtr := head
	refPtr := head
	count := 0
	if head != nil {
		for count < k {
			if refPtr == nil {
				fmt.Print("n is greater than the no. of nodes in list")
				return
			}
			refPtr = refPtr.next
			count++
		}
		for refPtr != nil {
			mainPtr = mainPtr.next
			refPtr = refPtr.next
		}
		fmt.Print("Node no. n from last is ", mainPtr.data)
	}
}

// copyList copies a linked list with next and random pointers (faithful port).
func (l *LinkList) copyList(head *Node) *Node {
	var copyHead, temp *Node
	ptr := head
	for ptr != nil {
		temp = ptr
		ptr.next = temp
		ptr = ptr.next.next
	}
	ptr = head
	for ptr != nil && ptr.next != nil {
		ptr.next.random = ptr.random.next
		ptr = ptr.next.next
	}
	ptr = head
	var prev *Node
	for ptr != nil {
		if copyHead == nil {
			copyHead = ptr.next
		} else {
			prev.next = ptr.next
		}
		prev = ptr.next
		ptr = ptr.next.next
	}
	return copyHead
}

// isPalindrome checks whether a list is a palindrome.
func (l *LinkList) isPalindrome(head *Node) bool {
	if head == nil {
		return false
	}
	p1, p2 := head, head
	s := []int{}
	for p2 != nil && p2.next != nil {
		s = append(s, p1.data)
		p1 = p1.next
		p2 = p2.next.next
	}
	// handle odd nodes
	if p2 != nil {
		p1 = p1.next
	}
	for p1 != nil {
		top := s[len(s)-1]
		s = s[:len(s)-1]
		if p1.data != top {
			return false
		}
		p1 = p1.next
	}
	return true
}

// oddEvenList groups all odd-indexed nodes followed by the even-indexed nodes.
// Input: 1->2->3->4->5  Output: 1->3->5->2->4.
func oddEvenList(head *Node) *Node {
	if head == nil || head.next == nil {
		return head
	}
	odd := head
	even := head.next
	evenHead := even
	for even != nil && even.next != nil {
		odd.next = even.next
		odd = odd.next
		even.next = odd.next
		even = even.next
	}
	odd.next = evenHead
	return head
}

// rearrange reverses alternate nodes and appends them to the end of the list.
// Input: 1->2->3->4->5->6  Output: 1->3->5->6->4->2.
func (l *LinkList) rearrange(odd *Node) {
	if odd == nil || odd.next == nil || odd.next.next == nil {
		return
	}
	even := odd.next
	odd.next = odd.next.next
	odd = odd.next
	even.next = nil
	for odd != nil && odd.next != nil {
		temp := odd.next.next
		odd.next.next = even
		even = odd.next
		odd.next = temp
		if temp != nil {
			odd = temp
		}
	}
	odd.next = even
}

// rearrange1 reorders L0->L1->...->Ln into L0->Ln->L1->Ln-1->...
// Input: 1->2->3->4  Output: 1->4->2->3.
func (l *LinkList) rearrange1(node *Node) {
	// 1) Find the middle point using tortoise and hare method
	slow, fast := node, node.next
	for fast != nil && fast.next != nil {
		slow = slow.next
		fast = fast.next.next
	}
	// 2) Split the list in two halves
	node1 := node
	node2 := slow.next
	slow.next = nil
	// 3) Reverse the second half
	node2 = reverselist(node2)
	// 4) Merge alternate nodes
	node = newNode(0) // dummy node
	curr := node
	for node1 != nil || node2 != nil {
		if node1 != nil {
			curr.next = node1
			curr = curr.next
			node1 = node1.next
		}
		if node2 != nil {
			curr.next = node2
			curr = curr.next
			node2 = node2.next
		}
	}
	node = node.next
}

// reverselist reverses a list iteratively and returns the new head.
func reverselist(node *Node) *Node {
	var prev, next *Node
	curr := node
	for curr != nil {
		next = curr.next
		curr.next = prev
		prev = curr
		curr = next
	}
	node = prev
	return node
}

// skipMdeleteN retains M nodes then deletes the next N nodes, repeatedly.
// M = 2, N = 2 Input: 1->2->3->4->5->6->7->8  Output: 1->2->5->6.
func (l *LinkList) skipMdeleteN(head *Node, M, N int) {
	curr := head
	var t *Node
	for curr != nil {
		// Skip M nodes
		for count := 1; count < M && curr != nil; count++ {
			curr = curr.next
		}
		if curr == nil {
			return
		}
		// Start from the next node and delete N nodes
		t = curr.next
		for count := 1; count <= N && t != nil; count++ {
			t = t.next
		}
		curr.next = t
		curr = t
	}
}

// swapNode swaps two nodes (by value x and y) without swapping their data.
// Input: 10->15->12->13->20->14, x=12, y=20  Output: 10->15->20->13->12->14.
func (l *LinkList) swapNode(head *Node, x, y int) {
	if x == y {
		return
	}
	var prevX *Node
	currX := head
	for currX != nil && currX.data != x {
		prevX = currX
		currX = currX.next
	}
	var prevY *Node
	currY := head
	for currY != nil && currY.data != y {
		prevY = currY
		currY = currY.next
	}
	if prevX != nil {
		prevX.next = currY
	} else {
		head = currY
	}
	if prevY != nil {
		prevY.next = currX
	} else {
		head = currX
	}
	temp := currY.next
	currY.next = currX.next
	currX.next = temp
}

// compare compares two strings represented as linked lists.
func (l *LinkList) compare(node1, node2 *Node) int {
	if node1 == nil && node2 == nil {
		return 1
	}
	for node1 != nil && node2 != nil && node1.data == node2.data {
		node1 = node1.next
		node2 = node2.next
	}
	// if the lists differ in size
	if node1 != nil && node2 != nil {
		if node1.data > node2.data {
			return 1
		}
		return -1
	}
	if node1 != nil && node2 == nil {
		return -1
	}
	if node1 == nil && node2 != nil {
		return -1
	}
	return 0
}
