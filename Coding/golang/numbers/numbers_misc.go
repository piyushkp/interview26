package main

import "container/heap"

// Streaming median + nested integer weighted sum.

// intHeap is a binary heap of ints; when max is true it acts as a max-heap,
// otherwise as a min-heap (natural ordering).
type intHeap struct {
	data []int
	max  bool
}

func (h intHeap) Len() int { return len(h.data) }
func (h intHeap) Less(i, j int) bool {
	if h.max {
		return h.data[i] > h.data[j]
	}
	return h.data[i] < h.data[j]
}
func (h intHeap) Swap(i, j int) { h.data[i], h.data[j] = h.data[j], h.data[i] }
func (h *intHeap) Push(x any)   { h.data = append(h.data, x.(int)) }
func (h *intHeap) Pop() any {
	old := h.data
	n := len(old)
	v := old[n-1]
	h.data = old[:n-1]
	return v
}

// Numbers holds the running state for the streaming median problem.
// Given a stream of unsorted integers, find the median element at any time.
type Numbers struct {
	numOfElements int
	minHeap       *intHeap
	maxHeap       *intHeap
}

func newNumbers() *Numbers {
	return &Numbers{
		minHeap: &intHeap{max: false},
		maxHeap: &intHeap{max: true},
	}
}

func (nu *Numbers) addNumberToStream(num int) {
	heap.Push(nu.maxHeap, num)
	if nu.numOfElements%2 == 0 {
		if len(nu.minHeap.data) == 0 {
			nu.numOfElements++
			return
		} else if nu.maxHeap.data[0] > nu.minHeap.data[0] {
			maxHeapRoot := heap.Pop(nu.maxHeap).(int)
			minHeapRoot := heap.Pop(nu.minHeap).(int)
			heap.Push(nu.maxHeap, minHeapRoot)
			heap.Push(nu.minHeap, maxHeapRoot)
		}
	} else {
		heap.Push(nu.minHeap, heap.Pop(nu.maxHeap).(int))
	}
	nu.numOfElements++
}

func (nu *Numbers) getMedian() float64 {
	if nu.numOfElements%2 != 0 {
		return float64(nu.maxHeap.data[0])
	}
	return float64(nu.maxHeap.data[0]+nu.minHeap.data[0]) / 2.0
}

// NestedInteger is a minimal nested-list element (faithful to the reference,
// where every element reports as an integer of value 1).
type NestedInteger struct{}

func (n NestedInteger) isInteger() bool          { return true }
func (n NestedInteger) getInteger() int          { return 1 }
func (n NestedInteger) getList() []NestedInteger { return []NestedInteger{} }

// Sum of all integers in the list weighted by their depth.
func getListSum(lni []NestedInteger, depth int) int {
	sum := 0
	for _, ni := range lni {
		if ni.isInteger() {
			sum += ni.getInteger() * depth
		} else {
			sum += getListSum(ni.getList(), depth+1)
		}
	}
	return sum
}

func getSum(ni NestedInteger) int {
	if ni.isInteger() {
		return ni.getInteger()
	}
	return getListSum(ni.getList(), 1)
}
