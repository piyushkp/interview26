package main

import (
	"fmt"
	"math"
	"math/rand"
)

// mergeAlternate merges nodes of list q into the receiver list at alternate
// positions (Java overloaded `merge(LinkList q)`).
func (l *LinkList) mergeAlternate(q *LinkList) {
	pCurr, qCurr := l.head, q.head
	var pNext, qNext *Node
	for pCurr != nil && qCurr != nil {
		pNext = pCurr.next
		qNext = qCurr.next
		qCurr.next = pNext
		pCurr.next = qCurr
		pCurr = pNext
		qCurr = qNext
	}
	q.head = qCurr
}

// printrandom prints a random node using reservoir sampling.
func (l *LinkList) printrandom(node *Node) {
	if node == nil {
		return
	}
	// (Java seeded with a UUID here; omitted as it was a discarded expression.)
	result := node.data
	current := node
	for n := 2; current != nil; n++ {
		// change result with probability 1/n
		if math.Mod(rand.Float64(), float64(n)) == 0 {
			result = current.data
		}
		current = current.next
	}
	fmt.Println("Randomly selected key is", result)
}

// removeDuplicatesUnsorted removes duplicates from an unsorted list.
// Time O(n^2) space O(1).
func (l *LinkList) removeDuplicatesUnsorted() {
	var ptr1, ptr2 *Node
	ptr1 = l.head
	for ptr1 != nil && ptr1.next != nil {
		ptr2 = ptr1
		for ptr2.next != nil {
			if ptr1.data == ptr2.next.data {
				ptr2.next = ptr2.next.next
			} else {
				ptr2 = ptr2.next
			}
		}
		ptr1 = ptr1.next
	}
}

// removeDuplicates removes duplicates from a sorted list.
func (l *LinkList) removeDuplicates() {
	current := l.head
	var nextNext *Node
	if l.head == nil {
		return
	}
	for current.next != nil {
		if current.data == current.next.data {
			nextNext = current.next.next
			current.next = nil
			current.next = nextNext
		} else {
			current = current.next
		}
	}
}

// addList adds two numbers stored in linked lists into result (faithful port).
func (l *LinkList) addList(head1, head2, result *Node) {
	var cur *Node
	if head1 == nil {
		result = head2
		return
	} else if head2 == nil {
		result = head1
		return
	}
	size1 := l.getSize(head1)
	size2 := l.getSize(head2)
	carry := 0
	if size1 == size2 {
		result = l.addSameSize(head1, head2, carry)
	} else {
		diff := absInt(size1 - size2)
		if size1 < size2 {
			l.swapPointer(head1, head2)
		}
		cur = head1
		for diff > 0 {
			cur = cur.next
			diff--
		}
		result = l.addSameSize(cur, head2, carry)
		l.addCarryToRemaining(head1, cur, carry, result)
	}
}

// swapPointer swaps two local pointer copies (no observable effect, as in Java).
func (l *LinkList) swapPointer(a, b *Node) {
	t := a
	a = b
	b = t
}

// getSize returns the number of nodes in the list.
func (l *LinkList) getSize(node *Node) int {
	size := 0
	for node != nil {
		node = node.next
		size++
	}
	return size
}

// addSameSize adds two equal-length lists, propagating the carry on return.
func (l *LinkList) addSameSize(head1, head2 *Node, carry int) *Node {
	if head1 == nil {
		return nil
	}
	result := &Node{}
	result.next = l.addSameSize(head1.next, head2.next, carry)
	sum := head1.data + head2.data + carry
	carry = sum / 10
	sum = sum % 10
	result.data = sum
	return result
}

// addCarryToRemaining adds the carry to the remaining (longer) list's prefix.
func (l *LinkList) addCarryToRemaining(head1, cur *Node, carry int, result *Node) {
	if head1 != cur {
		l.addCarryToRemaining(head1.next, cur, carry, result)
		sum := head1.data + carry
		carry = sum / 10
		sum %= 10
	}
}

// sortedInsert inserts a node into a sorted circular linked list.
func (l *LinkList) sortedInsert(newNd *Node) {
	current := l.head
	if current == nil {
		newNd.next = newNd
		l.head = newNd
	} else if current.data >= newNd.data {
		for current.next != l.head {
			current = current.next
		}
		current.next = newNd
		newNd.next = l.head
		l.head = newNd
	} else {
		for current.next != l.head && current.next.data < newNd.data {
			current = current.next
		}
		newNd.next = current.next
		current.next = newNd
	}
}

// insert inserts a value into a sorted cyclic list given any node in the list.
func (l *LinkList) insert(node *Node, x int) {
	if node == nil {
		node = newNode(x)
		node.next = node
		return
	}
	curr := node
	var prev *Node
	for {
		prev = curr
		curr = curr.next
		if x <= curr.data && x >= prev.data {
			break // case 1
		}
		if prev.data > curr.data && (x < curr.data || x > prev.data) {
			break // case 2
		}
		if curr == node {
			break // case 3: back to start
		}
	}
	newNd := newNode(x)
	newNd.next = curr
	prev.next = newNd
}

// removeDLL removes a single occurrence of a value from a doubly linked list.
func (l *LinkList) removeDLL(head *Node, value int) {
	cur := head
	if head == nil {
		return
	}
	if head.data == value {
		head = cur.next
	}
	for cur != nil {
		if cur.data == value {
			if cur.prev != nil {
				cur.prev.next = cur.next
			}
			if cur.next != nil {
				cur.next.prev = cur.prev
			}
			break
		}
		cur = cur.next
	}
}

// getInterSectionNode returns the intersection value of two lists.
func (l *LinkList) getInterSectionNode(head1, head2 *Node) int {
	c1 := l.getCount(head1)
	c2 := l.getCount(head2)
	var d int
	if c1 > c2 {
		d = c1 - c2
		return l.getIntersectionNodeUtil(d, head1, head2)
	}
	d = c2 - c1
	return l.getIntersectionNodeUtil(d, head2, head1)
}

// getIntersectionNodeUtil finds the intersection where node1 has d more nodes.
func (l *LinkList) getIntersectionNodeUtil(d int, node1, node2 *Node) int {
	current1 := node1
	current2 := node2
	for i := 0; i < d; i++ {
		current1 = current1.next
	}
	for current1 != nil && current2 != nil {
		if current1.data == current2.data {
			return current1.data
		}
		current1 = current1.next
		current2 = current2.next
	}
	return -1
}

// getCount returns the number of nodes in the list.
func (l *LinkList) getCount(node *Node) int {
	current := node
	count := 0
	for current != nil {
		current = current.next
		count++
	}
	return count
}

// addOne adds 1 to a number represented as a linked list, in linear time.
func (l *LinkList) addOne(head *Node) *Node {
	head = reverselist(head)
	head = l.addOneToList(head)
	return reverselist(head)
}

// addOneToList adds 1 to a list whose digits are stored least-significant first.
func (l *LinkList) addOneToList(head *Node) *Node {
	res := head
	var temp *Node
	carry := 1
	for head != nil {
		sum := carry + head.data
		if sum >= 10 {
			carry = 1
		} else {
			carry = 0
		}
		sum = sum % 10
		head.data = sum
		temp = head
		head = head.next
	}
	if carry > 0 {
		node := &Node{}
		node.data = carry
		temp.next = node
	}
	return res
}

// addOneToList1 adds 1 using recursion from the end towards the beginning.
func (l *LinkList) addOneToList1(head *Node) *Node {
	carry := addWithCarry(head)
	if carry > 0 {
		newNd := &Node{}
		newNd.data = carry
		newNd.next = head
		return newNd // new node becomes head
	}
	return head
}

// addWithCarry adds 1 recursively and returns the carry.
func addWithCarry(head *Node) int {
	if head == nil {
		return 1
	}
	sum := head.data + addWithCarry(head.next)
	head.data = sum % 10
	return sum / 10
}

// searchListfast finds an element in fewer than n probes.
func searchListfast(head *Node, target int) bool {
	var prev *Node
	ptr := head
	if head == nil {
		return false
	}
	for ptr != nil {
		if ptr.data == target {
			return true
		} else if ptr.data > target {
			return search(prev, ptr, target)
		}
		prev = ptr
		if ptr.next != nil && ptr.next.next != nil {
			ptr = ptr.next.next
		} else if ptr.next != nil && ptr.next.data == target {
			return true
		} else {
			return false
		}
	}
	return false
}

// search linearly scans the range [start, end) for the target.
func search(start, end *Node, target int) bool {
	if start == nil {
		return false
	}
	for start != end {
		if start.data == target {
			return true
		}
		start = start.next
	}
	return false
}

// removeOdd removes odd numbers from the list.
func removeOdd(head *Node) *Node {
	if head == nil {
		return nil
	}
	curr := head
	for curr.data%2 != 0 {
		head = curr.next
		curr = curr.next
	}
	curr = curr.next
	prev := head
	for curr != nil {
		if curr.data%2 != 0 {
			prev.next = curr.next
		} else {
			prev = curr
		}
		curr = curr.next
	}
	return head
}

// interleave interleaves two lists (deck-of-cards shuffle).
// Input: 1..10 Output: 6 1 7 2 8 3 9 4 10 5.
func interleave(first, second *Node) {
	var tail *Node
	for second != nil {
		if tail == nil {
			tail = second
		} else {
			tail.next = second
			tail = second
		}
		next := second.next
		second.next = nil
		second = next
		// Swap the two lists.
		temp := first
		first = second
		second = temp
	}
}

// MergeLists merges two sorted lists in place.
func (l *LinkList) MergeLists(list1, list2 *Node) *Node {
	if list1 == nil {
		return list2
	}
	if list2 == nil {
		return list1
	}
	var head *Node
	if list1.data < list2.data {
		head = list1
	} else {
		head = list2
		list2 = list1
		list1 = head
	}
	for list1.next != nil && list2 != nil {
		if list1.next.data <= list2.data {
			list1 = list1.next
		} else {
			tmp := list1.next
			list1.next = list2
			list2 = tmp
		}
	}
	if list1.next == nil {
		list1.next = list2
	}
	return head
}

// sortedListToBSTRecur builds a balanced BST from a sorted list, consuming the
// receiver's head pointer as it goes (root uses prev=left, next=right).
func (l *LinkList) sortedListToBSTRecur(n int) *Node {
	if n <= 0 {
		return nil
	}
	left := l.sortedListToBSTRecur(n / 2)
	root := l.head
	root.prev = left
	l.head = l.head.next
	root.next = l.sortedListToBSTRecur(n - n/2 - 1)
	return root
}

// flattenLinkedList flattens a multi-level linked list (next + down pointers).
func (l *LinkList) flattenLinkedList(head *flatList) *flatList {
	stack := []*flatList{}
	stack = append(stack, head)
	for len(stack) > 0 {
		node := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if node.down != nil && node.next != nil {
			stack = append(stack, node.next)
			stack = append(stack, node.down)
			node.next = node.down
			node.down = nil
		} else if node.next != nil {
			stack = append(stack, node.next)
		} else if node.down != nil {
			stack = append(stack, node.down)
			node.next = node.down
			node.down = nil
		} else if len(stack) > 0 {
			node.next = stack[len(stack)-1]
		}
	}
	return head
}
