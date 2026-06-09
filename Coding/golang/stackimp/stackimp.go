package main

import (
	"fmt"
	"sync/atomic"
)

// Stacker is the generic stack contract (Java interface Stack<T>).
// Java's `int size = 0;` constant is omitted (Go interfaces hold no fields).
type Stacker[T any] interface {
	Push(ele T) Stacker[T]
	Pop() T
}

// Compile-time checks that the array/linked implementations satisfy Stacker.
var (
	_ Stacker[int] = (*StackArray[int])(nil)
	_ Stacker[int] = (*StackLinkedList[int])(nil)
)

// StackQueue implements a stack using a single queue. push is O(n), pop O(1).
type StackQueue struct {
	q1 []int
}

func (s *StackQueue) Push(x int) {
	s.q1 = append(s.q1, x)
	sz := len(s.q1)
	for sz > 1 {
		front := s.q1[0]
		s.q1 = s.q1[1:]
		s.q1 = append(s.q1, front)
		sz--
	}
}

func (s *StackQueue) Pop() int {
	v := s.q1[0]
	s.q1 = s.q1[1:]
	return v
}

func (s *StackQueue) Empty() bool { return len(s.q1) == 0 }

func (s *StackQueue) Top() int { return s.q1[0] }

// StackArray is a slice-backed stack that grows/shrinks. Amortized O(1).
type StackArray[T any] struct {
	arr   []T
	total int
}

func NewStackArray[T any]() *StackArray[T] {
	return &StackArray[T]{arr: make([]T, 2)}
}

func (s *StackArray[T]) resize(capacity int) {
	tmp := make([]T, capacity)
	copy(tmp, s.arr[:s.total])
	s.arr = tmp
}

func (s *StackArray[T]) Push(ele T) Stacker[T] {
	if len(s.arr) == s.total {
		s.resize(len(s.arr) * 2)
	}
	s.arr[s.total] = ele
	s.total++
	return s
}

func (s *StackArray[T]) Pop() T {
	if s.total == 0 {
		panic("NoSuchElement")
	}
	s.total--
	ele := s.arr[s.total]
	var zero T
	s.arr[s.total] = zero
	if s.total > 0 && s.total == len(s.arr)/4 {
		s.resize(len(s.arr) / 2)
	}
	return ele
}

func (s *StackArray[T]) String() string { return fmt.Sprintf("%v", s.arr) }

// llNode is a node of StackLinkedList.
type llNode[T any] struct {
	ele  T
	next *llNode[T]
}

// StackLinkedList is a singly-linked-list stack. push/pop are O(1).
type StackLinkedList[T any] struct {
	total int
	head  *llNode[T]
}

func (s *StackLinkedList[T]) Push(ele T) Stacker[T] {
	current := s.head
	s.head = &llNode[T]{ele: ele, next: current}
	s.total++
	return s
}

func (s *StackLinkedList[T]) Pop() T {
	var zero T
	if s.head == nil {
		// Java created (but never threw) NoSuchElementException here; return zero value.
		return zero
	}
	ele := s.head.ele
	s.head = s.head.next
	s.total--
	return ele
}

func (s *StackLinkedList[T]) String() string {
	out := ""
	for tmp := s.head; tmp != nil; tmp = tmp.next {
		out += fmt.Sprintf("%v, ", tmp.ele)
	}
	return out
}

// cnode is a node of the lock-free concurrentStack.
type cnode[E any] struct {
	item E
	next *cnode[E]
}

// concurrentStack is a non-blocking (CAS) stack using atomic.Pointer (Go 1.19).
type concurrentStack[E any] struct {
	top atomic.Pointer[cnode[E]]
}

func (s *concurrentStack[E]) push(item E) {
	newHead := &cnode[E]{item: item}
	for {
		oldHead := s.top.Load()
		newHead.next = oldHead
		if s.top.CompareAndSwap(oldHead, newHead) {
			return
		}
	}
}

func (s *concurrentStack[E]) pop() (E, bool) {
	for {
		oldHead := s.top.Load()
		if oldHead == nil {
			var zero E
			return zero, false
		}
		newHead := oldHead.next
		if s.top.CompareAndSwap(oldHead, newHead) {
			return oldHead.item, true
		}
	}
}

// sortStack sorts a stack ascending (top = largest) using one auxiliary stack.
// Time O(n^2), space O(n).
func sortStack(inputStack []int) []int {
	if inputStack == nil {
		return nil
	}
	var tempStack []int
	for len(inputStack) > 0 {
		temp := inputStack[len(inputStack)-1]
		inputStack = inputStack[:len(inputStack)-1]
		for len(tempStack) > 0 && tempStack[len(tempStack)-1] > temp {
			inputStack = append(inputStack, tempStack[len(tempStack)-1])
			tempStack = tempStack[:len(tempStack)-1]
		}
		tempStack = append(tempStack, temp)
	}
	return tempStack
}

// StackWithMin supports push/pop/min all in O(1) using a secondary min-stack.
type StackWithMin struct {
	data []int
	s2   []int
}

func (s *StackWithMin) Push(value int) {
	if m, ok := s.Min(); !ok || value <= m {
		s.s2 = append(s.s2, value)
	}
	s.data = append(s.data, value)
}

func (s *StackWithMin) Pop() int {
	value := s.data[len(s.data)-1]
	s.data = s.data[:len(s.data)-1]
	if m, ok := s.Min(); ok && value == m {
		s.s2 = s.s2[:len(s.s2)-1]
	}
	return value
}

func (s *StackWithMin) Min() (int, bool) {
	if len(s.s2) == 0 {
		return 0, false
	}
	return s.s2[len(s.s2)-1], true
}

// SetOfStacks splits a logical stack into several physical stacks of fixed capacity.
type SetOfStacks struct {
	stacks   [][]int
	capacity int
}

func NewSetOfStacks(capacity int) *SetOfStacks {
	return &SetOfStacks{capacity: capacity}
}

func (s *SetOfStacks) getLastStack() []int {
	if len(s.stacks) == 0 {
		return nil
	}
	return s.stacks[len(s.stacks)-1]
}

func (s *SetOfStacks) push(v int) {
	if last := s.getLastStack(); last != nil && len(last) != s.capacity {
		i := len(s.stacks) - 1
		s.stacks[i] = append(s.stacks[i], v)
	} else {
		s.stacks = append(s.stacks, []int{v})
	}
}

func (s *SetOfStacks) pop() int {
	if len(s.stacks) == 0 {
		panic("EmptyStack")
	}
	i := len(s.stacks) - 1
	last := s.stacks[i]
	v := last[len(last)-1]
	s.stacks[i] = last[:len(last)-1]
	if len(s.stacks[i]) == 0 {
		s.stacks = s.stacks[:i]
	}
	return v
}

func main() {
	fmt.Println("Stack Imp")

	sa := NewStackArray[int]()
	sa.Push(1).Push(2).Push(3)
	fmt.Println("StackArray:", sa)
	fmt.Println("StackArray pop:", sa.Pop())

	sll := &StackLinkedList[string]{}
	sll.Push("a").Push("b").Push("c")
	fmt.Println("StackLinkedList:", sll)

	sq := &StackQueue{}
	sq.Push(10)
	sq.Push(20)
	sq.Push(30)
	fmt.Println("StackQueue top:", sq.Top(), "pop:", sq.Pop())

	fmt.Println("sortStack:", sortStack([]int{3, 1, 4, 1, 5, 9, 2, 6}))

	swm := &StackWithMin{}
	swm.Push(5)
	swm.Push(3)
	swm.Push(7)
	if m, ok := swm.Min(); ok {
		fmt.Println("StackWithMin min:", m)
	}

	sos := NewSetOfStacks(2)
	for i := 1; i <= 5; i++ {
		sos.push(i)
	}
	fmt.Println("SetOfStacks pop:", sos.pop())

	cs := &concurrentStack[int]{}
	cs.push(100)
	cs.push(200)
	if v, ok := cs.pop(); ok {
		fmt.Println("ConcurrentStack pop:", v)
	}
}
