// Package main is an idiomatic Go port of the Java reference file MISC.java
// (originally package code.ds). It is a grab-bag of interview / DSA snippets.
//
// Java classes become Go structs, instance methods become methods with a
// receiver, and static methods become package-level functions. The code is
// split across several files in this directory; only this file declares main().
package main

import (
	"container/heap"
	"fmt"
	"sort"
)

// ---------------------------------------------------------------------------
// small integer helpers (Go 1.19 has no built-in min/max for ints)
// ---------------------------------------------------------------------------

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// ---------------------------------------------------------------------------
// Interval and ordering helpers
// ---------------------------------------------------------------------------

// Interval represents a closed range [start, end].
type Interval struct {
	start int
	end   int
}

// intervalHeap is a min-heap of intervals ordered by start (PriorityQueue).
type intervalHeap []*Interval

func (h intervalHeap) Len() int           { return len(h) }
func (h intervalHeap) Less(i, j int) bool { return h[i].start < h[j].start }
func (h intervalHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *intervalHeap) Push(x any)        { *h = append(*h, x.(*Interval)) }
func (h *intervalHeap) Pop() any {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[:n-1]
	return item
}

// intHeap is a min-heap of ints (PriorityQueue<Integer>).
type intHeap []int

func (h intHeap) Len() int           { return len(h) }
func (h intHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h intHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *intHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *intHeap) Pop() any {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[:n-1]
	return item
}

func main() {
	i1 := &Interval{10, 15}
	i2 := &Interval{25, 35}
	i3 := &Interval{45, 65}
	i4 := &Interval{85, 95}
	list := []*Interval{i3, i2, i4, i1}
	target := &Interval{17, 100}
	// System.out.print(find_min_intervals(list, target));
	// drawCircle(2);
	for _, i := range findInterval(list, target) {
		fmt.Println(i.start, i.end)
	}
}

// Given a set of time intervals in any order, merge all overlapping intervals
// into one. Time Complexity: O(n Log n).
//
// in place merge interval with space O(1) and time O(nlogn) by modifying input
func mergeIntervalsInPlace(intervals []*Interval) []*Interval {
	if intervals == nil {
		panic("IllegalArgumentException")
	}
	sort.Slice(intervals, func(i, j int) bool { return intervals[i].start < intervals[j].start })
	var result []*Interval
	var prev *Interval
	for _, next := range intervals {
		if prev != nil && prev.end >= next.start {
			prev.end = maxInt(prev.end, next.end)
		} else {
			result = append(result, next)
			prev = next
		}
	}
	return result
}

// Space is O(n)
func mergeIntervals(intervals []*Interval) []*Interval {
	sort.Slice(intervals, func(i, j int) bool { return intervals[i].start < intervals[j].start })
	var merged []*Interval
	for _, interval := range intervals {
		// if the list of merged intervals is empty or if the current interval
		// does not overlap with the previous, simply append it.
		if len(merged) == 0 || merged[len(merged)-1].end < interval.start {
			merged = append(merged, interval)
		} else {
			// otherwise there is overlap, so merge the current and previous.
			if interval.end > merged[len(merged)-1].end {
				merged[len(merged)-1].end = interval.end
			}
		}
	}
	return merged
}

// Find least number of intervals from A that can fully cover B.
// A =[[0,3],[3,4],[4,6],[2,7]] B =[0,6] return 2
func findMinIntervals(intervals []*Interval, target *Interval) int {
	// Sort intervals ascending by start, and descending by end when equal.
	sort.Slice(intervals, func(a, b int) bool {
		if intervals[a].start == intervals[b].start {
			return intervals[a].end > intervals[b].end
		}
		return intervals[a].start < intervals[b].start
	})
	i := 0
	start := target.start
	maxEnd := -1
	num := 0
	for i < len(intervals) && maxEnd < target.end {
		if intervals[i].end <= start {
			i++
		} else {
			if intervals[i].start > start {
				break
			}
			for i < len(intervals) && maxEnd < target.end && intervals[i].start <= start {
				maxEnd = maxInt(maxEnd, intervals[i].end)
				i++
			}
			if start != maxEnd {
				start = maxEnd
				num++
			}
		}
	}
	if maxEnd < target.end {
		return 0
	}
	return num
}

// Russian doll envelopes: maximum number of envelopes you can nest.
func maxEnvelope(intervals []*Interval) int {
	if len(intervals) == 0 || len(intervals) == 1 {
		return 0
	}
	// Sort ascending on width and descending on height when width is same.
	sort.Slice(intervals, func(a, b int) bool {
		if intervals[a].start == intervals[b].start {
			return intervals[a].end > intervals[b].end
		}
		return intervals[a].start < intervals[b].start
	})
	first := intervals[0]
	width := first.start
	height := first.end
	count := 0
	for i := 1; i < len(intervals); i++ {
		curr := intervals[i]
		if width < curr.start && height < curr.end {
			count++
		}
		width = curr.start
		height = curr.end
	}
	return count + 1
}

// Adds an interval [from, to] into an internal structure.
var globalIntervals []*Interval
var coverage = 0

func addInterval(from, to int) {
	interval := &Interval{from, to}
	globalIntervals = append(globalIntervals, interval)
}

// in place add interval, time = O(n) space O(1)
func addInterval1(from, to int) {
	newInterval := &Interval{from, to}
	if len(globalIntervals) == 0 {
		globalIntervals = append(globalIntervals, newInterval)
		coverage = newInterval.end - newInterval.start
		return
	}
	var remaining []*Interval
	for _, prev := range globalIntervals {
		if prev.end >= newInterval.start {
			newInterval.end = maxInt(prev.end, newInterval.end)
			newInterval.start = minInt(prev.start, newInterval.start)
			coverage -= prev.end - prev.start
		} else {
			remaining = append(remaining, prev)
		}
	}
	remaining = append(remaining, newInterval)
	coverage += newInterval.end - newInterval.start
	globalIntervals = remaining
}

func getCoverage() int {
	return coverage
}

// Given a list of intervals, return the range these unique intervals covered.
func getCoverageOfIntervals(intervals []*Interval) int {
	if len(intervals) == 0 {
		return 0
	}
	sort.Slice(intervals, func(i, j int) bool { return intervals[i].start < intervals[j].start })
	length := 0
	prev := intervals[0]
	for i := 1; i < len(intervals); i++ {
		curr := intervals[i]
		if prev.end > curr.start {
			prev.end = maxInt(prev.end, curr.end)
		} else {
			length += prev.end - prev.start
			prev = curr
		}
	}
	length += prev.end - prev.start // Be very careful to check this case.
	return length
}

// Given a set of non-overlapping intervals and a requestInterval, find all
// non-overlapping intervals within the request range.
func findInterval(intervals []*Interval, requestInterval *Interval) []*Interval {
	result := []*Interval{}
	if len(intervals) == 0 || requestInterval.end < requestInterval.start {
		return result
	}
	pq := &intervalHeap{}
	heap.Init(pq)
	for _, interval := range intervals {
		heap.Push(pq, interval)
	}
	for requestInterval.start >= (*pq)[0].end {
		heap.Pop(pq)
	}
	start := requestInterval.start
	if start < (*pq)[0].start {
		if requestInterval.end <= (*pq)[0].start {
			result = append(result, requestInterval)
			return result
		}
		result = append(result, &Interval{start, (*pq)[0].start})
	}
	start = maxInt(start, heap.Pop(pq).(*Interval).end)
	for pq.Len() > 0 && (*pq)[0].start < requestInterval.end {
		current := heap.Pop(pq).(*Interval)
		result = append(result, &Interval{start, current.start})
		start = current.end
	}
	if requestInterval.end > start {
		result = append(result, &Interval{start, requestInterval.end})
	}
	return result
}

// Determine if a person could attend all meetings.
func canAttend(intervals []*Interval) bool {
	sort.Slice(intervals, func(i, j int) bool { return intervals[i].start < intervals[j].start })
	if len(intervals) == 0 {
		return true
	}
	for i := 0; i < len(intervals)-1; i++ {
		if intervals[i].end > intervals[i+1].start {
			return false
		}
	}
	return true
}

// minimum meeting rooms required
func minMeetingRooms(intervals []*Interval) int {
	if len(intervals) == 0 {
		return 0
	}
	sort.Slice(intervals, func(i, j int) bool { return intervals[i].start < intervals[j].start })
	queue := &intHeap{}
	heap.Init(queue)
	count := 1
	heap.Push(queue, intervals[0].end)
	for i := 1; i < len(intervals); i++ {
		if intervals[i].start < (*queue)[0] {
			count++
		} else {
			heap.Pop(queue)
		}
		heap.Push(queue, intervals[i].end)
	}
	return count
}

// Solution 1: greedy
func minMeetingRooms1(intervals []*Interval) int {
	start := make([]int, len(intervals))
	end := make([]int, len(intervals))
	for i := 0; i < len(intervals); i++ {
		start[i] = intervals[i].start
		end[i] = intervals[i].end
	}
	sort.Ints(start)
	sort.Ints(end)
	endIdx, res := 0, 0
	for i := 0; i < len(start); i++ {
		if start[i] < end[endIdx] {
			res++
		} else {
			endIdx++
		}
	}
	return res
}

// Given a list of driver intervals, find the maximum number of active drivers.
func findMaxDriver(input []*Interval) int {
	if len(input) < 1 {
		return 0
	}
	start := make([]int, len(input))
	end := make([]int, len(input))
	for i := 0; i < len(input); i++ {
		start[i] = input[i].start
		end[i] = input[i].end
	}
	sort.Ints(start)
	sort.Ints(end)
	driverIn, maxDriver := 1, 1
	i, j := 1, 0
	for i < len(input) && j < len(input) {
		if start[i] < end[j] {
			driverIn++
			maxDriver = maxInt(driverIn, maxDriver)
			i++
		} else {
			driverIn--
			j++
		}
	}
	return maxDriver
}
