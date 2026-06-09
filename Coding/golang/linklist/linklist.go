package main

import "fmt"

// Node is a linked-list node. It carries the optional `random` and `prev`
// pointers so the same type can model singly, doubly and random-pointer lists.
type Node struct {
	data   int
	next   *Node
	random *Node
	prev   *Node
}

// newNode mirrors the Java `new Node(data)` constructor.
func newNode(data int) *Node {
	return &Node{data: data}
}

// flatList is a multi-level linked-list node (next + child/down pointer).
type flatList struct {
	data int
	next *flatList
	down *flatList
}

// LinkList mirrors the Java class holding the list `head` field.
type LinkList struct {
	head *Node
}

func absInt(a int) int {
	if a < 0 {
		return -a
	}
	return a
}

func main() {
	head := newNode(1)
	head.next = newNode(2)
	head.next.next = newNode(3)
	head.next.next.next = newNode(4)
	printReverse1(head)
	fmt.Println()
}

// PrintLinkedList traverses and prints the list.
func (l *LinkList) PrintLinkedList(start *Node) {
	fmt.Print("\nHEAD .")
	for start != nil {
		fmt.Print(start.data)
		start = start.next
	}
	fmt.Print("null\n\n")
}

// InsertNodeInLinkedListAtFront inserts a node at the beginning of the list.
func (l *LinkList) InsertNodeInLinkedListAtFront(data int) {
	temp := newNode(data)
	temp.data = data
	temp.next = l.head
	l.head = temp
}

// InsertNodeInLinkedListAtEnd inserts a node at the end of the list.
func (l *LinkList) InsertNodeInLinkedListAtEnd(data int) {
	temp := newNode(data)
	temp.data = data
	temp.next = nil
	if l.head == nil {
		l.head = temp
		return
	}
	traveller := l.head
	for traveller.next != nil {
		traveller = traveller.next
	}
	traveller.next = temp
}

// InsertNodeInLinkedList inserts a node at a given 1-based position.
func (l *LinkList) InsertNodeInLinkedList(data, position int) {
	temp := newNode(data)
	temp.data = data
	temp.next = nil
	if position == 1 || l.head == nil {
		temp.next = l.head
		l.head = temp
		return
	}
	t := l.head
	currPos := 2
	for currPos < position && t.next != nil {
		t = t.next
		currPos++
	}
	temp.next = t.next
	t.next = temp
}

// DeleteNodeFromLinkedList deletes the node at a 1-based position.
func (l *LinkList) DeleteNodeFromLinkedList(position int) int {
	if l.head == nil {
		return 0
	}
	if position == 1 {
		l.head = l.head.next
	} else {
		t := l.head
		currPos := 2
		for currPos < position && t.next != nil {
			t = t.next
			currPos++
		}
		if t.next != nil {
			t.next = t.next.next // NOTE THIS
		} else {
			return 0 // could not find the correct node
		}
	}
	return 1
}

// deleteNode deletes a middle node given only access to that node by copying
// the next node's data into it.
func deleteNode(n *Node) bool {
	if n == nil || n.next == nil {
		return false // Failure
	}
	next := n.next
	n.data = next.data
	n.next = next.next
	return true
}

// Sort sorts the list in place (selection-style, O(n^2)).
func (l *LinkList) Sort() {
	for list := l.head; list.next != nil; list = list.next {
		for pass := list.next; pass != nil; pass = pass.next {
			if list.data > pass.data {
				list.data, pass.data = pass.data, list.data
			}
		}
	}
}

// mergeSort sorts a list with merge sort. Time complexity O(n log n).
func mergeSort(head *Node) *Node {
	if head == nil || head.next == nil {
		return head
	}
	first := head
	middle := findMiddle(head)
	second := middle.next
	middle.next = nil
	return merge(mergeSort(first), mergeSort(second))
}

// merge merges two sorted lists recursively.
func merge(first, second *Node) *Node {
	var result *Node
	if first == nil {
		return second
	} else if second == nil {
		return first
	}
	if first.data <= second.data {
		result = first
		result.next = merge(first.next, second)
	} else {
		result = second
		result.next = merge(first, second.next)
	}
	return result
}

// findMiddle returns the middle node using the slow/fast pointer technique.
func findMiddle(head *Node) *Node {
	slow := head
	fast := head
	for slow.next != nil && fast.next.next != nil {
		slow = slow.next
		fast = fast.next.next
	}
	return slow
}

// Find searches for an element in the list.
func (l *LinkList) Find(value int) *Node {
	currentNode := l.head
	for currentNode != nil {
		if currentNode.data == value {
			return currentNode
		}
		currentNode = currentNode.next
	}
	return nil
}

// MaxMinInList finds the maximum and minimum value in the list.
func (l *LinkList) MaxMinInList(max, min int) int {
	currentNode := l.head
	if currentNode == nil {
		return 0 // list is empty
	}
	max = currentNode.data
	min = currentNode.data
	for currentNode.next != nil {
		currentNode = currentNode.next
		if currentNode.data > max {
			max = currentNode.data
		} else if currentNode.data < min {
			min = currentNode.data
		}
	}
	return 1
}
