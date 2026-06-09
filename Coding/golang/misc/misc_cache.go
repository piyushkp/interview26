package main

import "sync"

// ---------------------------------------------------------------------------
// LRU cache backed by a hash map and a doubly linked list (O(1) ops).
// Uses pseudo head/tail nodes to avoid nil checks.
// ---------------------------------------------------------------------------

type DoublyNode struct {
	data int
	key  int
	next *DoublyNode
	prev *DoublyNode
}

type LRU struct {
	mp       map[int]*DoublyNode
	capacity int
	head     *DoublyNode
	tail     *DoublyNode
}

func newLRU(capacity int) *LRU {
	l := &LRU{
		mp:       make(map[int]*DoublyNode),
		capacity: capacity,
		head:     &DoublyNode{},
		tail:     &DoublyNode{},
	}
	l.head.prev = nil
	l.tail.next = nil
	l.head.next = l.tail
	l.tail.prev = l.head
	return l
}

func (l *LRU) add(item *DoublyNode) {
	item.prev = l.head
	item.next = l.head.next
	l.head.next.prev = item
	l.head.next = item
}

func (l *LRU) remove(item *DoublyNode) {
	pre := item.prev
	post := item.next
	pre.next = post
	post.prev = pre
}

func (l *LRU) moveFirst(item *DoublyNode) {
	l.remove(item)
	l.add(item)
}

func (l *LRU) removeLast() *DoublyNode {
	res := l.tail.prev
	l.remove(res)
	return res
}

func (l *LRU) get(key int) int {
	if node, ok := l.mp[key]; ok {
		l.moveFirst(node)
		return node.data
	}
	return -1
}

func (l *LRU) set(key, value int) {
	// cache hit
	if node, ok := l.mp[key]; ok {
		l.moveFirst(node)
		node.data = value
		l.mp[key] = node
		return
	}
	// cache is full and cache miss
	if len(l.mp) >= l.capacity {
		end := l.removeLast()
		delete(l.mp, end.key)
	}
	node := &DoublyNode{key: key, data: value}
	l.add(node)
	l.mp[key] = node
}

func (l *LRU) removeCache(key int) {
	if node, ok := l.mp[key]; ok {
		delete(l.mp, key)
		l.remove(node)
	}
}

// ---------------------------------------------------------------------------
// Thread-safe LRU cache using a read/write lock.
// ---------------------------------------------------------------------------

type LRUThreadSafe[K comparable, V any] struct {
	queue    []K
	mp       map[K]V
	mu       sync.RWMutex
	capacity int64
	total    int64
}

func newLRUThreadSafe[K comparable, V any](capacity int64) *LRUThreadSafe[K, V] {
	return &LRUThreadSafe[K, V]{mp: make(map[K]V), capacity: capacity}
}

func (l *LRUThreadSafe[K, V]) get(key K) (V, bool) {
	l.mu.Lock()
	defer l.mu.Unlock()
	if v, ok := l.mp[key]; ok {
		l.removeFromQueue(key)
		l.queue = append(l.queue, key)
		return v, true
	}
	var zero V
	return zero, false
}

func (l *LRUThreadSafe[K, V]) set(key K, value V) V {
	l.mu.Lock()
	defer l.mu.Unlock()
	if _, ok := l.mp[key]; ok {
		l.removeFromQueue(key)
	}
	for l.total >= l.capacity {
		if len(l.queue) == 0 {
			break
		}
		queueKey := l.queue[0]
		l.queue = l.queue[1:]
		delete(l.mp, queueKey)
	}
	// New elements are inserted at the tail of the queue.
	l.queue = append(l.queue, key)
	l.total++
	l.mp[key] = value
	return value
}

func (l *LRUThreadSafe[K, V]) removeKey(key K) (V, bool) {
	l.mu.Lock()
	defer l.mu.Unlock()
	if v, ok := l.mp[key]; ok {
		delete(l.mp, key)
		l.removeFromQueue(key)
		return v, true
	}
	var zero V
	return zero, false
}

func (l *LRUThreadSafe[K, V]) removeFromQueue(key K) {
	for i, k := range l.queue {
		if k == key {
			l.queue = append(l.queue[:i], l.queue[i+1:]...)
			return
		}
	}
}

// ---------------------------------------------------------------------------
// PeekingIterator: implement peek() on top of an existing iterator.
// ---------------------------------------------------------------------------

// seqIterator is the minimal iterator contract used by PeekingIterator.
type seqIterator[E any] interface {
	hasNext() bool
	next() E
	remove()
}

type PeekingIterator[E any] struct {
	iter       seqIterator[E]
	exhausted  bool
	slotFilled bool
	slot       E
}

func newPeekingIterator[E any](iter seqIterator[E]) *PeekingIterator[E] {
	return &PeekingIterator[E]{iter: iter}
}

func (p *PeekingIterator[E]) fill() {
	if p.exhausted || p.slotFilled {
		return
	}
	if p.iter.hasNext() {
		p.slot = p.iter.next()
		p.slotFilled = true
	} else {
		p.exhausted = true
		var zero E
		p.slot = zero
		p.slotFilled = false
	}
}

// peek returns the next element without advancing the iterator.
func (p *PeekingIterator[E]) peek() E {
	p.fill()
	if p.exhausted {
		var zero E
		return zero
	}
	return p.slot
}

func (p *PeekingIterator[E]) next() E {
	if !p.hasNext() {
		panic("NoSuchElementException")
	}
	var x E
	if p.slotFilled {
		x = p.slot
	} else {
		x = p.iter.next()
	}
	var zero E
	p.slot = zero
	p.slotFilled = false
	return x
}

func (p *PeekingIterator[E]) hasNext() bool {
	if p.exhausted {
		return false
	}
	if p.slotFilled {
		return true
	}
	return p.iter.hasNext()
}

func (p *PeekingIterator[E]) remove() {
	if p.slotFilled {
		panic("IllegalStateException: peek() or element() called before remove()")
	}
	p.iter.remove()
}

// ---------------------------------------------------------------------------
// Reverse a stack using recursion (no loops, no extra data structure).
// ---------------------------------------------------------------------------

func reverseStack(stack *[]int) {
	if len(*stack) == 0 || len(*stack) == 1 {
		return
	}
	top := (*stack)[len(*stack)-1]
	*stack = (*stack)[:len(*stack)-1]
	reverseStack(stack)
	insertAtBottom(stack, top)
}

func insertAtBottom(stack *[]int, val int) {
	if len(*stack) == 0 {
		*stack = append(*stack, val)
		return
	}
	temp := (*stack)[len(*stack)-1]
	*stack = (*stack)[:len(*stack)-1]
	insertAtBottom(stack, val)
	*stack = append(*stack, temp)
}
