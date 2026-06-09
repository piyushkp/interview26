// Package main contains idiomatic Go conversions of the Java reference
// implementation originally in package code.ds (Array.java).
//
// Created by Piyush Patel.
// Reference: https://github.com/tongzhang1994/Facebook-Interview-Coding
//
// The original Java file was a single large class with a mix of static and
// instance methods. In Go these are flattened to package-level functions,
// except for a couple of genuinely stateful helpers (MedianFinder and
// TwoSumStore) which are modeled as their own structs.
package main

import "fmt"

func main() {
	// Integer[] input = {1,2,1,2,6,7,5,1};
	// System.out.print(maxSum3NonOverlapping(input, 2));
	input := []float64{.70, 2.80, 4.90}
	fmt.Println(minimizeRoundSum(input, 8))
}

// ---------------------------------------------------------------------------
// Small numeric helpers (Go 1.19 has no built-in min/max/abs for int).
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

func absInt(a int) int {
	if a < 0 {
		return -a
	}
	return a
}

// ---------------------------------------------------------------------------
// binHeap is a generic binary heap used wherever the Java code used a
// java.util.PriorityQueue. The ordering is defined by the supplied less
// function: pop() returns the element that is "smallest" according to less.
// ---------------------------------------------------------------------------

type binHeap[T any] struct {
	data []T
	less func(a, b T) bool
}

func newBinHeap[T any](less func(a, b T) bool) *binHeap[T] {
	return &binHeap[T]{less: less}
}

func (h *binHeap[T]) len() int { return len(h.data) }

func (h *binHeap[T]) isEmpty() bool { return len(h.data) == 0 }

func (h *binHeap[T]) peek() T { return h.data[0] }

func (h *binHeap[T]) push(v T) {
	h.data = append(h.data, v)
	i := len(h.data) - 1
	for i > 0 {
		parent := (i - 1) / 2
		if h.less(h.data[i], h.data[parent]) {
			h.data[i], h.data[parent] = h.data[parent], h.data[i]
			i = parent
		} else {
			break
		}
	}
}

func (h *binHeap[T]) pop() T {
	n := len(h.data)
	top := h.data[0]
	h.data[0] = h.data[n-1]
	h.data = h.data[:n-1]
	n--
	i := 0
	for {
		l, r := 2*i+1, 2*i+2
		best := i
		if l < n && h.less(h.data[l], h.data[best]) {
			best = l
		}
		if r < n && h.less(h.data[r], h.data[best]) {
			best = r
		}
		if best == i {
			break
		}
		h.data[i], h.data[best] = h.data[best], h.data[i]
		i = best
	}
	return top
}

// ---------------------------------------------------------------------------
// swap helpers. The Java code had two distinct helpers (lower-case index swap
// and a capitalized XOR swap), kept separate here to preserve call sites.
// ---------------------------------------------------------------------------

func swap(g []int, x, y int) {
	temp := g[y]
	g[y] = g[x]
	g[x] = temp
}

// Swap exchanges a[x] and a[y] using the XOR trick (matches Java Swap).
func Swap(x, y int, a []int) {
	a[x] ^= a[y]
	a[y] ^= a[x]
	a[x] ^= a[y]
}
