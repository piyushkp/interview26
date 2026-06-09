package main

import "fmt"

// Sort groups the instance-based sort routines (quicksort) ported from the
// non-static methods of the Java Sort class.
type Sort struct{}

// mergeSort sorts data[first .. first+n-1] in place using merge sort.
// Time: O(n log n), Space: O(n) for the temporary buffers.
func mergeSort(data []int, first, n int) {
	if n > 1 {
		// Compute sizes of the two halves.
		n1 := n / 2
		n2 := n - n1
		mergeSort(data, first, n1)      // Sort data[first] .. data[first+n1-1].
		mergeSort(data, first+n1, n2)   // Sort data[first+n1] .. end.
		merge(data, first, n1, n2)      // Merge the two sorted halves.
	}
}

// merge combines the two sorted runs data[first..first+n1-1] and
// data[first+n1..first+n1+n2-1] back into data.
func merge(data []int, first, n1, n2 int) {
	temp := make([]int, n1+n2) // Temporary array.
	copied, copied1, copied2 := 0, 0, 0

	// Merge elements from the two halves into temp.
	for copied1 < n1 && copied2 < n2 {
		if data[first+copied1] < data[first+n1+copied2] {
			temp[copied] = data[first+copied1]
			copied++
			copied1++
		} else {
			temp[copied] = data[first+n1+copied2]
			copied++
			copied2++
		}
	}
	// Copy any remaining entries in the left and right subarrays.
	for copied1 < n1 {
		temp[copied] = data[first+copied1]
		copied++
		copied1++
	}
	for copied2 < n2 {
		temp[copied] = data[first+n1+copied2]
		copied++
		copied2++
	}
	// Copy from temp back into data.
	for i := 0; i < n1+n2; i++ {
		data[first+i] = temp[i]
	}
}

// quickSort sorts array[startIdx..endIdx] in place. Average O(n log n).
func (s *Sort) quickSort(array []int, startIdx, endIdx int) {
	idx := s.partition(array, startIdx, endIdx)
	// Recurse into the left part of the partitioned array.
	if startIdx < idx-1 {
		s.quickSort(array, startIdx, idx-1)
	}
	// Recurse into the right part of the partitioned array.
	if endIdx > idx {
		s.quickSort(array, idx, endIdx)
	}
}

func (s *Sort) partition(g []int, first, last int) int {
	pivot := g[last]
	pIndex := first
	for i := first; i < last; i++ {
		if g[i] < pivot {
			s.swap(g, i, pIndex)
			pIndex++
		}
	}
	s.swap(g, pIndex, last)
	return pIndex
}

// swap exchanges g[x] and g[y] using the XOR trick (faithful to the Java
// source; note it zeroes the element when x == y).
func (s *Sort) swap(g []int, x, y int) {
	g[x] ^= g[y]
	g[y] ^= g[x]
	g[x] ^= g[y]
}

// doInsertionSort sorts input in place. Insertion sort is an online algorithm
// that keeps the data seen so far sorted. Time: O(n^2).
func doInsertionSort(input []int) []int {
	for i := 1; i < len(input); i++ {
		for j := i; j > 0; j-- {
			if input[j] < input[j-1] {
				input[j], input[j-1] = input[j-1], input[j]
			}
		}
	}
	return input
}

func main() {
	a := []int{3, 23, 1, 5, 2, 56, 4}
	mergeSort(a, 0, len(a))
	fmt.Println(a)
}
