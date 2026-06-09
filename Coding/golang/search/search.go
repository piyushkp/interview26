package main

import "fmt"

// Search groups the binary-search variants ported from the Java Search class.
type Search struct{}

// binarySearch is the iterative variant (instance method in Java).
// Time: O(log n), Space: O(1). Returns the index of x or -1 if absent.
func (s *Search) binarySearch(arr []int, x int) int {
	l, r := 0, len(arr)-1
	for l <= r {
		m := l + (r-l)/2
		// Check if x is present at mid.
		if arr[m] == x {
			return m
		}
		if arr[m] < x {
			l = m + 1 // x greater, ignore left half.
		} else {
			r = m - 1 // x smaller, ignore right half.
		}
	}
	// Element not present.
	return -1
}

// binarySearchRecursive is the recursive variant. It is renamed from the
// overloaded static binarySearch in Java, since Go has no method overloading.
// Time: O(log n). Returns the index of x or -1 if absent.
func binarySearchRecursive(arr []int, l, r, x int) int {
	if r >= l {
		mid := l + (r-l)/2
		// Element present at the middle itself.
		if arr[mid] == x {
			return mid
		}
		// Smaller than mid -> search the left subarray.
		if arr[mid] > x {
			return binarySearchRecursive(arr, l, mid-1, x)
		}
		// Otherwise search the right subarray.
		return binarySearchRecursive(arr, mid+1, r, x)
	}
	// Element not present.
	return -1
}

func main() {
	fmt.Print("Search")
}
