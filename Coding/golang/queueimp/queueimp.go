package main

// Ported from Coding/java/QueueImp.java (original package code.ds).

import (
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"unsafe"
)

func main() {
	fmt.Print("QueueImp")
}

// TwoStackQueue implements a Queue using two stacks. (Java inner class Queue)
type TwoStackQueue struct {
	s1    []int
	s2    []int
	front int
	size  int
}

func (q *TwoStackQueue) EnQueue(item int) {
	if len(q.s1) == 0 {
		q.front = item
	}
	q.s1 = append(q.s1, item)
	q.size++
}

func (q *TwoStackQueue) Dequeue() int {
	if len(q.s2) == 0 {
		for len(q.s1) != 0 {
			top := q.s1[len(q.s1)-1]
			q.s1 = q.s1[:len(q.s1)-1]
			q.s2 = append(q.s2, top)
		}
	}
	q.size--
	top := q.s2[len(q.s2)-1]
	q.s2 = q.s2[:len(q.s2)-1]
	return top
}

func (q *TwoStackQueue) empty() bool {
	return len(q.s1) == 0 && len(q.s2) == 0
}

func (q *TwoStackQueue) peek() int {
	if len(q.s2) != 0 {
		return q.s2[len(q.s2)-1]
	}
	return q.front
}

// getSize renamed from size() to avoid clashing with the size field.
func (q *TwoStackQueue) getSize() int {
	return q.size
}

// BoundedBuffer is a blocking queue that blocks on dequeue when empty and on
// enqueue when full. (Java inner class BoundedBuffer using Lock/Condition)
type BoundedBuffer struct {
	mu       sync.Mutex
	notFull  *sync.Cond
	notEmpty *sync.Cond
	items    []interface{}
	putptr   int
	takeptr  int
	count    int
}

func newBoundedBuffer() *BoundedBuffer {
	b := &BoundedBuffer{items: make([]interface{}, 100)}
	b.notFull = sync.NewCond(&b.mu)
	b.notEmpty = sync.NewCond(&b.mu)
	return b
}

func (b *BoundedBuffer) put(x interface{}) {
	b.mu.Lock()
	defer b.mu.Unlock()
	for b.count == len(b.items) {
		b.notFull.Wait()
	}
	b.items[b.putptr] = x
	b.putptr++
	if b.putptr == len(b.items) {
		b.putptr = 0
	}
	b.count++
	b.notEmpty.Signal()
}

func (b *BoundedBuffer) take() interface{} {
	b.mu.Lock()
	defer b.mu.Unlock()
	for b.count == 0 {
		b.notEmpty.Wait()
	}
	x := b.items[b.takeptr]
	b.takeptr++
	if b.takeptr == len(b.items) {
		b.takeptr = 0
	}
	b.count--
	b.notFull.Signal()
	return x
}

// lqNode is a node for the non-blocking LinkedQueue. The next link is stored as
// an unsafe.Pointer (to *lqNode[E]) because Go 1.19 cannot have an
// atomic.Pointer[T] field inside the recursive type T itself.
type lqNode[E any] struct {
	item E
	next unsafe.Pointer // atomically-accessed *lqNode[E]
}

func (n *lqNode[E]) loadNext() *lqNode[E] {
	return (*lqNode[E])(atomic.LoadPointer(&n.next))
}

func (n *lqNode[E]) casNext(oldNode, newNode *lqNode[E]) bool {
	return atomic.CompareAndSwapPointer(&n.next, unsafe.Pointer(oldNode), unsafe.Pointer(newNode))
}

// LinkedQueue is a non-blocking (lock-free) queue using CAS.
// https://www.ibm.com/developerworks/java/library/j-jtp04186/
type LinkedQueue[E any] struct {
	head unsafe.Pointer // atomically-accessed *lqNode[E]
	tail unsafe.Pointer // atomically-accessed *lqNode[E]
}

func newLinkedQueue[E any]() *LinkedQueue[E] {
	q := &LinkedQueue[E]{}
	sentinel := &lqNode[E]{}
	q.head = unsafe.Pointer(sentinel)
	q.tail = unsafe.Pointer(sentinel)
	return q
}

func (q *LinkedQueue[E]) loadTail() *lqNode[E] {
	return (*lqNode[E])(atomic.LoadPointer(&q.tail))
}

func (q *LinkedQueue[E]) casTail(oldNode, newNode *lqNode[E]) bool {
	return atomic.CompareAndSwapPointer(&q.tail, unsafe.Pointer(oldNode), unsafe.Pointer(newNode))
}

func (q *LinkedQueue[E]) put(item E) bool {
	newNode := &lqNode[E]{item: item}
	for {
		curTail := q.loadTail()
		residue := curTail.loadNext()
		if curTail == q.loadTail() {
			if residue == nil { /* A */
				if curTail.casNext(nil, newNode) { /* C */
					q.casTail(curTail, newNode) /* D */
					return true
				}
			} else {
				q.casTail(curTail, residue) /* B */
			}
		}
	}
}

const defaultCapacity = 100

// CircularArrayQueue is a simple fixed-then-growable circular queue.
type CircularArrayQueue[T any] struct {
	front int
	rear  int
	count int
	queue []T
}

func newCircularArrayQueue[T any]() *CircularArrayQueue[T] {
	return &CircularArrayQueue[T]{queue: make([]T, defaultCapacity)}
}

func newCircularArrayQueueCap[T any](initialCapacity int) *CircularArrayQueue[T] {
	return &CircularArrayQueue[T]{queue: make([]T, initialCapacity)}
}

func (q *CircularArrayQueue[T]) enqueue(element T) {
	if q.size() == len(q.queue) {
		q.expandCapacity()
	}
	q.queue[q.rear] = element
	q.rear = (q.rear + 1) % len(q.queue)
	q.count++
}

func (q *CircularArrayQueue[T]) dequeue() (T, error) {
	var zero T
	if q.isEmpty() {
		return zero, errors.New("queue is Empty")
	}
	result := q.queue[q.front]
	q.queue[q.front] = zero
	q.front = (q.front + 1) % len(q.queue)
	q.count--
	return result, nil
}

func (q *CircularArrayQueue[T]) first() (T, error) {
	var zero T
	if q.isEmpty() {
		return zero, errors.New("queue is Empty= ")
	}
	return q.queue[q.front], nil
}

func (q *CircularArrayQueue[T]) isEmpty() bool {
	return q.count == 0
}

func (q *CircularArrayQueue[T]) size() int {
	return q.count
}

func (q *CircularArrayQueue[T]) String() string {
	result := ""
	scan := 0
	for scan < q.count {
		result += fmt.Sprintf("%v", q.queue[scan]) + "\n"
		scan++
	}
	return result
}

func (q *CircularArrayQueue[T]) expandCapacity() {
	larger := make([]T, len(q.queue)*2)
	for scan := 0; scan < q.count; scan++ {
		larger[scan] = q.queue[q.front]
		q.front = (q.front + 1) % len(q.queue)
	}
	q.front = 0
	q.rear = q.count
	q.queue = larger
}
