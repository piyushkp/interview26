package main

import (
	"container/heap"
	"fmt"
)

// DelayObject is a queue item with a logical start time (in seconds). It is the
// Go analogue of the Java Delayed implementation.
type DelayObject struct {
	data      string
	startTime int64
}

// getDelay returns the remaining seconds relative to the given logical "now".
func (d *DelayObject) getDelay(now int64) int64 {
	return d.startTime - now
}

// compareTo orders objects by startTime (-1, 0, 1), mirroring Delayed.compareTo.
func (d *DelayObject) compareTo(o *DelayObject) int {
	switch {
	case d.startTime < o.startTime:
		return -1
	case d.startTime > o.startTime:
		return 1
	default:
		return 0
	}
}

func (d *DelayObject) String() string {
	return fmt.Sprintf("{data='%s', startTime=%d}", d.data, d.startTime)
}

// delayHeap is a min-heap of *DelayObject keyed on startTime. It backs the
// priority-queue behaviour of java.util.concurrent.DelayQueue.
type delayHeap []*DelayObject

func (h delayHeap) Len() int           { return len(h) }
func (h delayHeap) Less(i, j int) bool { return h[i].startTime < h[j].startTime }
func (h delayHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *delayHeap) Push(x any) {
	*h = append(*h, x.(*DelayObject))
}

func (h *delayHeap) Pop() any {
	old := *h
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	*h = old[:n-1]
	return item
}

// DelayQueueTest holds a DelayQueue plus a dedup set of data values, mirroring
// the static fields of the Java class.
type DelayQueueTest struct {
	dq  delayHeap
	set map[string]bool
}

func newDelayQueueTest() *DelayQueueTest {
	t := &DelayQueueTest{set: make(map[string]bool)}
	heap.Init(&t.dq)
	return t
}

// add offers a new DelayObject with the given start time, skipping duplicates
// by data value.
func (t *DelayQueueTest) add(data string, startTime int64) {
	ob := &DelayObject{data: data, startTime: startTime}
	if !t.set[ob.data] {
		t.set[ob.data] = true
		heap.Push(&t.dq, ob)
	}
}

// get inspects the queue at logical time `now` (the Java code slept 5s before
// iterating). Items still pending are printed and kept; expired items are
// dropped from both the queue and the dedup set. The remaining size is printed.
func (t *DelayQueueTest) get(now int64) []string {
	out := []string{}
	kept := make([]*DelayObject, 0, len(t.dq))
	for _, dt := range t.dq {
		if dt.getDelay(now) > 0 {
			fmt.Println(dt.data)
			out = append(out, dt.data)
			kept = append(kept, dt)
		} else {
			delete(t.set, dt.data)
		}
	}
	t.dq = kept
	heap.Init(&t.dq)
	fmt.Println(len(t.dq))
	return out
}

func main() {
	t := newDelayQueueTest()
	// startTime values are "base + delay"; we inspect at base+5, which is the
	// deterministic equivalent of the original Thread.sleep(5000).
	var base int64 = 0
	t.add("foo", base+10)
	t.add("bar", base+4)
	t.add("bar2", base+14)
	t.add("bar3", base+12)
	t.add("foo1", base+7)
	t.add("foo2", base+8)
	t.add("foo3", base+9)
	t.add("foo4", base+3)

	t.get(base + 5)
}
