package main

// Ported from Coding/java/Hasher.java (original package code.ds).
// Hash table with separate chaining + MiniCassandra + ConsistentHash.

import (
	"fmt"
	"sort"
)

func main() {
	fmt.Print("Hasher")
}

func absInt(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// llNode is a doubly-linked-list node used for separate chaining.
type llNode[K comparable, V any] struct {
	next  *llNode[K, V]
	prev  *llNode[K, V]
	key   K
	value V
}

func (n *llNode[K, V]) printForward() string {
	data := fmt.Sprintf("(%v,%v)", n.key, n.value)
	if n.next != nil {
		return data + "->" + n.next.printForward()
	}
	return data
}

// Hasher is a hash table with separate chaining. A hash function for K must be
// supplied (Go has no built-in Object.hashCode for arbitrary keys).
type Hasher[K comparable, V any] struct {
	arr    []*llNode[K, V]
	hashFn func(K) int
}

func NewHasher[K comparable, V any](capacity int, hashFn func(K) int) *Hasher[K, V] {
	h := &Hasher[K, V]{hashFn: hashFn}
	h.arr = make([]*llNode[K, V], capacity)
	return h
}

// put inserts key/value, returning the previous value (zero value if new).
func (h *Hasher[K, V]) put(key K, value V) V {
	var zero V
	node := h.getNodeForKey(key)
	if node != nil {
		oldValue := node.value
		node.value = value // just update the value.
		return oldValue
	}

	node = &llNode[K, V]{key: key, value: value}
	index := h.getIndexForKey(key)
	if h.arr[index] != nil {
		node.next = h.arr[index]
		node.next.prev = node
	}
	h.arr[index] = node
	return zero
}

// remove deletes the node for key and returns its value (zero value if absent).
func (h *Hasher[K, V]) remove(key K) V {
	var zero V
	node := h.getNodeForKey(key)
	if node == nil {
		return zero
	}

	if node.prev != nil {
		node.prev.next = node.next
	} else {
		// Removing head - update.
		hashKey := h.getIndexForKey(key)
		h.arr[hashKey] = node.next
	}

	if node.next != nil {
		node.next.prev = node.prev
	}
	return node.value
}

func (h *Hasher[K, V]) get(key K) V {
	var zero V
	node := h.getNodeForKey(key)
	if node == nil {
		return zero
	}
	return node.value
}

func (h *Hasher[K, V]) getNodeForKey(key K) *llNode[K, V] {
	index := h.getIndexForKey(key)
	current := h.arr[index]
	for current != nil {
		if current.key == key {
			return current
		}
		current = current.next
	}
	return nil
}

func (h *Hasher[K, V]) getIndexForKey(key K) int {
	return absInt(h.hashFn(key) % len(h.arr))
}

func (h *Hasher[K, V]) printTable() {
	for i := 0; i < len(h.arr); i++ {
		s := ""
		if h.arr[i] != nil {
			s = h.arr[i].printForward()
		}
		fmt.Printf("%d: %s\n", i, s)
	}
}

// MiniCassandra is a two-level key/value store (raw_key -> column_key -> value).
type Column struct {
	key   int
	value string
}

func newColumn(key int, value string) *Column {
	return &Column{key: key, value: value}
}

type MiniCassandra struct {
	m map[string]map[int]string
}

func newMiniCassandra() *MiniCassandra {
	return &MiniCassandra{m: make(map[string]map[int]string)}
}

func (c *MiniCassandra) insert(rawKey string, columnKey int, columnValue string) {
	tm := c.m[rawKey]
	if tm == nil {
		tm = make(map[int]string)
		c.m[rawKey] = tm
	}
	tm[columnKey] = columnValue
}

// query returns columns in the inclusive range [columnStart, columnEnd], sorted by key.
func (c *MiniCassandra) query(rawKey string, columnStart, columnEnd int) []*Column {
	results := []*Column{}
	tm := c.m[rawKey]
	if tm == nil {
		return results
	}
	keys := []int{}
	for k := range tm {
		if k >= columnStart && k <= columnEnd {
			keys = append(keys, k)
		}
	}
	sort.Ints(keys)
	for _, k := range keys {
		results = append(results, newColumn(k, tm[k]))
	}
	return results
}

// hashFunction is a placeholder hash (matches the Java stub which returns 0).
type hashFunction struct{}

func (hashFunction) hash(key interface{}) int {
	return 0
}

// ConsistentHash maps nodes around a hash ring with virtual replicas.
type ConsistentHash[T any] struct {
	hashFunction     hashFunction
	numberOfReplicas int
	circle           map[int]T
}

func newConsistentHash[T any](hf hashFunction, numberOfReplicas int, nodes []T) *ConsistentHash[T] {
	c := &ConsistentHash[T]{
		hashFunction:     hf,
		numberOfReplicas: numberOfReplicas,
		circle:           make(map[int]T),
	}
	for _, node := range nodes {
		c.add(node)
	}
	return c
}

func (c *ConsistentHash[T]) add(node T) {
	for i := 0; i < c.numberOfReplicas; i++ {
		c.circle[c.hashFunction.hash(fmt.Sprintf("%v%d", node, i))] = node
	}
}

func (c *ConsistentHash[T]) remove(node T) {
	for i := 0; i < c.numberOfReplicas; i++ {
		delete(c.circle, c.hashFunction.hash(fmt.Sprintf("%v%d", node, i)))
	}
}

func (c *ConsistentHash[T]) get(key interface{}) (T, bool) {
	var zero T
	if len(c.circle) == 0 {
		return zero, false
	}
	hash := c.hashFunction.hash(key)
	if _, ok := c.circle[hash]; !ok {
		keys := c.sortedKeys()
		// tailMap: smallest key >= hash, else wrap to firstKey.
		idx := -1
		for i, k := range keys {
			if k >= hash {
				idx = i
				break
			}
		}
		if idx == -1 {
			hash = keys[0]
		} else {
			hash = keys[idx]
		}
	}
	return c.circle[hash], true
}

func (c *ConsistentHash[T]) sortedKeys() []int {
	keys := make([]int, 0, len(c.circle))
	for k := range c.circle {
		keys = append(keys, k)
	}
	sort.Ints(keys)
	return keys
}
