package main

import "math/rand"

// Random sampling / weighted selection utilities.

// getting random items from a collection in constant time.
func randomSample[T comparable](items []T, m int) map[T]bool {
	res := make(map[T]bool, m)
	n := len(items)
	for i := n - m; i < n; i++ {
		pos := rand.Intn(i + 1)
		item := items[pos]
		if res[item] {
			res[items[i]] = true
		} else {
			res[item] = true
		}
	}
	return res
}

// for stream of collection items (reservoir sampling).
func reservoirSample[T any](items []T, m int) []T {
	res := make([]T, 0, m)
	count := 0
	for _, item := range items {
		count++
		if count <= m {
			res = append(res, item)
		} else {
			r := rand.Intn(count)
			if r < m {
				res[r] = item
			}
		}
	}
	return res
}

// Returns values randomly, according to their weight.
func RandomByWeight(input []string, weightFunc map[string]int) string {
	totalWeight := 0 // sum of weights of all elements before current
	selected := input[0]
	for _, data := range input {
		weight := weightFunc[data]
		r := int(rand.Float64() * float64(totalWeight+weight)) // random value
		if r >= totalWeight {                                  // probability weight/(totalWeight+weight)
			selected = data
		}
		totalWeight += weight
	}
	return selected
}

// return a random number from (0,...,n-1) with given weights.
func randomNumber(weights []int) int {
	if weights == nil || len(weights) == 0 {
		return 0
	}
	n := len(weights)
	for i := 1; i < n; i++ {
		weights[i] += weights[i-1] // [1,2,4,5,1,3] -> [1,3,7,12,13,16]
	}
	num := rand.Intn(weights[n-1]) // num is from 0 to 15
	return binarySearch(weights, 0, n-1, num)
}

// find the leftmost mid such that target <= weights[mid].
func binarySearch(weights []int, start, end, target int) int {
	for start < end {
		mid := start + (end-start)/2
		if target <= weights[mid] {
			end = mid
		} else {
			start = mid + 1
		}
	}
	return start
}
