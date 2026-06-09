package main

import (
	"container/heap"
	"math"
	"math/rand"
	"sort"
)

// K Nearest Points on a plane + selection (kth smallest) algorithms.

// Point on a plane; distance is precomputed relative to an origin.
type Point struct {
	x, y     int
	distance float64
}

func newPoint(x, y int, original *Point) *Point {
	p := &Point{x: x, y: y}
	// sqrt(x^2 + y^2)
	p.distance = math.Hypot(float64(x-original.x), float64(y-original.y))
	return p
}

// pointHeap is a min-heap ordered by ascending distance (natural ordering).
type pointHeap []*Point

func (h pointHeap) Len() int           { return len(h) }
func (h pointHeap) Less(i, j int) bool { return h[i].distance < h[j].distance }
func (h pointHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *pointHeap) Push(x any)        { *h = append(*h, x.(*Point)) }
func (h *pointHeap) Pop() any {
	old := *h
	n := len(old)
	v := old[n-1]
	*h = old[:n-1]
	return v
}

// Find K Nearest points on a plane O(nlogk).
func findKNearestPoints(points []*Point, original *Point, k int) []*Point {
	result := []*Point{}
	if len(points) == 0 || original == nil || k <= 0 {
		return result
	}
	pq := &pointHeap{}
	heap.Init(pq)
	for _, point := range points {
		if pq.Len() < k {
			heap.Push(pq, point)
		} else if (*pq)[0].distance > point.distance {
			heap.Pop(pq)
			heap.Push(pq, point)
		}
	}
	for _, p := range *pq {
		result = append(result, p)
	}
	return result
}

// K nearest points using selection algorithm. Time = O(n), worst O(n^2).
func findKNearestPointsSelection(points []*Point, k int) []*Point {
	n := len(points)
	dist := make([]float64, n)
	for i := 0; i < n; i++ {
		dist[i] = math.Sqrt(float64(points[i].x*points[i].x + points[i].y*points[i].y))
	}
	kthMin := kthSmallest(dist, 0, n-1, k-1)
	result := []*Point{}
	for i := 0; i < n; i++ {
		d := math.Sqrt(float64(points[i].x*points[i].x + points[i].y*points[i].y))
		if d <= kthMin {
			result = append(result, points[i])
		}
	}
	return result
}

// Median Of Medians worst case time O(n).
func MedianOfMediansSelect(A []float64, low, high, k int) float64 {
	if high-low+1 <= 5 {
		sort.Float64s(A[low:high])
		return A[low+k-1]
	}
	noOfGroups := (high - low + 1) / 5
	medianArray := make([]float64, noOfGroups)
	for i := 0; i < noOfGroups; i++ {
		medianArray[i] = MedianOfMediansSelect(A, low+i*5, low+(i*5)+4, 3)
	}
	medianOfMedians := MedianOfMediansSelect(medianArray, 0, len(medianArray)-1, noOfGroups/2+1)
	medianOfMediansPosition := partition1(A, low, high, medianOfMedians)
	if medianOfMediansPosition-low+1 == k {
		return A[low+k-1]
	} else if k < medianOfMediansPosition-low+1 {
		return MedianOfMediansSelect(A, low, medianOfMediansPosition-1, k)
	}
	return MedianOfMediansSelect(A, medianOfMediansPosition+1, high, k-(medianOfMediansPosition-low+1))
}

func partition1(G []float64, first, last int, pivot float64) int {
	i := first
	for ; i < last; i++ {
		if G[i] == pivot {
			break
		}
	}
	swapFloat64(G, i, last-1)
	pIndex := first
	for i = first; i < last; i++ {
		if G[i] < pivot {
			swapFloat64(G, i, pIndex)
			pIndex++
		}
	}
	swapFloat64(G, pIndex, last-1)
	return pIndex
}

// kth smallest element in unsorted array.
func kthSmallest(G []float64, first, last, k int) float64 {
	if first <= last {
		pivot := randomPartition(G, first, last)
		if pivot == k {
			return G[k]
		}
		if pivot > k {
			return kthSmallest(G, first, pivot-1, k)
		}
		return kthSmallest(G, pivot+1, last, k)
	}
	return 0
}

// Picks a random pivot element between l and r and partitions.
func randomPartition(arr []float64, l, r int) int {
	pivot := int(math.Round(float64(l) + rand.Float64()*float64(r-l)))
	swapFloat64(arr, pivot, r)
	return partition(arr, l, r)
}

func partition(G []float64, first, last int) int {
	pivot := G[last]
	pIndex := first
	for i := first; i < last; i++ {
		if G[i] < pivot {
			swapFloat64(G, i, pIndex)
			pIndex++
		}
	}
	swapFloat64(G, pIndex, last)
	return pIndex
}

func swapFloat64(G []float64, x, y int) {
	G[x], G[y] = G[y], G[x]
}
