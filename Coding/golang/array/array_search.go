package main

import (
	"fmt"
	"math"
	"sort"
)

// maxRepeating finds the maximum repeating element in range [0, k-1].
func maxRepeating(arr []int, n, k int) int {
	for i := 0; i < n; i++ {
		arr[arr[i]%k] += k
	}
	max := arr[0]
	result := 0
	for i := 1; i < n; i++ {
		if arr[i] > max {
			max = arr[i]
			result = i
		}
	}
	return result
}

// mostFrequent returns the most frequent number and its count. O(1) space.
func mostFrequent(a []int) string {
	sort.Ints(a)
	count := 1
	maxCount := 1
	num := a[0]
	maxNum := a[0]
	for i := 1; i < len(a); i++ {
		if num == a[i] {
			count++
			if count > maxCount {
				maxCount = count
				maxNum = a[i]
			}
		} else {
			count = 1
			num = a[i]
		}
	}
	return fmt.Sprintf("%d: %d", maxNum, maxCount)
}

// MoreThanHalfElem returns the majority element (>n/2 times) or -1.
func MoreThanHalfElem(a []int) int {
	cand := findCandidate(a)
	if isMajority(a, cand) {
		return cand
	}
	return -1
}

// findCandidate finds the majority candidate using Moore's Voting Algorithm.
func findCandidate(a []int) int {
	majIndex := 0
	count := 1
	for i := 1; i < len(a); i++ {
		if a[majIndex] == a[i] {
			count++
		} else {
			count--
		}
		if count == 0 {
			majIndex = i
			count = 1
		}
	}
	return a[majIndex]
}

func isMajority(a []int, cand int) bool {
	count := 0
	for i := 0; i < len(a); i++ {
		if a[i] == cand {
			count++
		}
	}
	return count > len(a)/2
}

// leftRotate rotates elements to the left k times.
func leftRotate(arr []int, k int) {
	n := len(arr)
	rvereseArray(arr, 0, k-1)
	rvereseArray(arr, k, n-1)
	rvereseArray(arr, 0, n-1)
}

func rightRotate(arr []int, k int) {
	n := len(arr)
	rvereseArray(arr, 0, n-k-1)
	rvereseArray(arr, n-k, n-1)
	rvereseArray(arr, 0, n-1)
}

func rvereseArray(arr []int, start, end int) {
	for start < end {
		arr[start] ^= arr[end]
		arr[end] ^= arr[start]
		arr[start] ^= arr[end]
		start++
		end--
	}
}

// rotated_binary_search searches a rotated sorted array (no duplicates).
func rotated_binary_search(nums []int, N, key int) int {
	left := 0
	right := N - 1
	for left <= right {
		mid := left + (right-left)/2
		if nums[mid] == key {
			return mid
		}
		if nums[left] <= nums[mid] { // the bottom half is sorted
			if nums[left] <= key && key < nums[mid] {
				right = mid - 1
			} else {
				left = mid + 1
			}
		} else { // the upper half is sorted
			if key > nums[mid] && key <= nums[right] {
				left = mid + 1
			} else {
				right = mid - 1
			}
		}
	}
	return -1
}

// rotatedArrayWithDuplicates searches a rotated sorted array with duplicates.
func rotatedArrayWithDuplicates(nums []int, target int) bool {
	left := 0
	right := len(nums) - 1
	for left <= right {
		mid := (left + right) >> 1
		if nums[mid] == target {
			return true
		}
		if nums[left] == nums[mid] && nums[right] == nums[mid] {
			left++
			right--
		} else if nums[left] <= nums[mid] {
			if nums[left] <= target && nums[mid] > target {
				right = mid - 1
			} else {
				left = mid + 1
			}
		} else {
			if nums[mid] < target && nums[right] >= target {
				left = mid + 1
			} else {
				right = mid - 1
			}
		}
	}
	return false
}

// searchRotatedUnknowntimes searches a rotated sorted array with duplicates,
// rotated an unknown number of times. Worst case O(N).
func searchRotatedUnknowntimes(a []int, left, right, x int) int {
	mid := (left + right) / 2
	if x == a[mid] {
		return mid
	}
	if right < left {
		return -1
	}
	if a[left] < a[mid] { // Left is normally ordered.
		if x >= a[left] && x <= a[mid] {
			return searchRotatedUnknowntimes(a, left, mid-1, x)
		}
		return searchRotatedUnknowntimes(a, mid+1, right, x)
	} else if a[mid] < a[left] { // Right is normally ordered.
		if x >= a[mid] && x <= a[right] {
			return searchRotatedUnknowntimes(a, mid+1, right, x)
		}
		return searchRotatedUnknowntimes(a, left, mid-1, x)
	} else if a[left] == a[mid] {
		if a[mid] != a[right] {
			return searchRotatedUnknowntimes(a, mid+1, right, x)
		}
		result := searchRotatedUnknowntimes(a, left, mid-1, x)
		if result == -1 {
			return searchRotatedUnknowntimes(a, mid+1, right, x)
		}
		return result
	}
	return -1
}

// findMin finds the minimum in a sorted+rotated array (distinct). O(logn).
func findMin(arr []int, low, high int) int {
	if high == low {
		return arr[low]
	}
	mid := low + (high-low)/2
	if mid < high && arr[mid+1] < arr[mid] {
		return arr[mid+1]
	}
	if mid > low && arr[mid] < arr[mid-1] {
		return arr[mid]
	}
	if arr[high] > arr[mid] {
		return findMin(arr, low, mid-1)
	}
	return findMin(arr, mid+1, high)
}

// findMinDuplicate handles duplicates; can be O(n) in worst case.
func findMinDuplicate(arr []int, low, high int) int {
	if high < low {
		return arr[0]
	}
	if high == low {
		return arr[low]
	}
	mid := low + (high-low)/2
	if mid < high && arr[mid+1] < arr[mid] {
		return arr[mid+1]
	}
	if arr[low] == arr[mid] && arr[high] == arr[mid] {
		return minInt(findMinDuplicate(arr, low, mid-1), findMinDuplicate(arr, mid+1, high))
	}
	if mid > low && arr[mid] < arr[mid-1] {
		return arr[mid]
	}
	if arr[high] > arr[mid] {
		return findMinDuplicate(arr, low, mid-1)
	}
	return findMinDuplicate(arr, mid+1, high)
}

// findMinOfabc picks one number from each array minimizing the abs-diff sum.
func findMinOfabc(a, b, c []int) {
	min := math.MaxInt32
	i, j, k := 0, 0, 0
	index1, index2, index3 := 0, 0, 0
	for i < len(a) && j < len(b) && k < len(c) {
		n := absInt(a[i]-b[j]) + absInt(b[j]-c[k]) + absInt(c[k]-a[i])
		if n < min {
			min = n
			index1 = i
			index2 = j
			index3 = k
		}
		if a[i] < b[j] && a[i] < c[k] {
			i++
		} else if b[j] < a[i] && b[j] < c[k] {
			j++
		} else {
			k++
		}
	}
	fmt.Print(a[index1], " ", b[index2], " ", c[index3])
}

// findRange returns {startIndex, endIndex} of num in a sorted array. O(logn).
func findRange(a []int, num int) []int {
	i := first(a, 0, len(a)-1, num, len(a))
	if i == -1 {
		return nil
	}
	j := last(a, i, len(a)-1, num, len(a))
	return []int{i, j}
}

// first returns the index of the FIRST occurrence of x, or -1.
func first(arr []int, low, high, x, n int) int {
	if high >= low {
		mid := (low + high) / 2
		if (mid == 0 || x > arr[mid-1]) && arr[mid] == x {
			return mid
		} else if x > arr[mid] {
			return first(arr, mid+1, high, x, n)
		}
		return first(arr, low, mid-1, x, n)
	}
	return -1
}

// last returns the index of the LAST occurrence of x, or -1.
func last(arr []int, low, high, x, n int) int {
	if high >= low {
		mid := low + (high-low)/2
		if (mid == n-1 || x < arr[mid+1]) && arr[mid] == x {
			return mid
		} else if x < arr[mid] {
			return last(arr, low, mid-1, x, n)
		}
		return last(arr, mid+1, high, x, n)
	}
	return -1
}

// findNumbersInRange counts elements in [min, max]. Time O(N).
func findNumbersInRange(a []int, min, max int) int {
	left := 0
	right := len(a) - 1
	if min > a[right] || max < a[left] {
		return 0
	}
	for left < right {
		if a[left] < min {
			left++
		}
		if a[right] > max {
			right--
		}
		if (a[left] == min || a[left] > min) && (a[right] == max || a[right] < max) {
			break
		}
	}
	return right - left + 1
}

// findNumbersInRange1 counts elements in [min, max]. Time O(2logN).
func findNumbersInRange1(a []int, min, max int) int {
	if min > a[len(a)-1] || max < a[0] {
		return 0
	}
	indexLeft := binarySearchForLeftRange(a, 0, len(a)-1, min)
	indexRight := binarySearchForRightRange(a, indexLeft, len(a)-1, max)
	if indexLeft == -1 || indexRight == -1 || indexLeft > indexRight {
		return 0
	}
	return indexRight - indexLeft + 1
}

func binarySearchForLeftRange(a []int, start, end, leftRange int) int {
	low := start
	high := end
	for low <= high {
		mid := low + (high-low)/2
		if a[mid] >= leftRange {
			high = mid - 1
		} else {
			low = mid + 1
		}
	}
	return high + 1
}

func binarySearchForRightRange(a []int, start, end, rightRange int) int {
	low := start
	high := end
	for low <= high {
		mid := low + (high-low)/2
		if a[mid] > rightRange {
			high = mid - 1
		} else {
			low = mid + 1
		}
	}
	return low - 1
}

// findDuplicate prints duplicates in an array with elements from 0..n-1.
// Note: modifies the original array. Uses math.MinInt32 as the marker.
func findDuplicate(arr []int) {
	for i := 0; i < len(arr); i++ {
		if arr[i] == math.MinInt32 {
			if arr[0] > 0 {
				arr[0] = -arr[0]
			} else {
				fmt.Println("0")
			}
		} else if arr[absInt(arr[i])] == 0 {
			arr[absInt(arr[i])] = math.MinInt32
		} else if arr[absInt(arr[i])] > 0 {
			arr[absInt(arr[i])] = -arr[absInt(arr[i])]
		} else {
			fmt.Println(absInt(arr[i]))
		}
	}
}

// findDuplicate1 finds a duplicate using Floyd's cycle detection. O(n) time.
func findDuplicate1(a []int) int {
	if len(a) == 0 || len(a) == 1 {
		return -1
	}
	slow := a[0]
	fast := a[a[0]]
	for slow != fast {
		slow = a[slow]
		fast = a[a[fast]]
	}
	fast = 0
	for slow != fast {
		slow = a[slow]
		fast = a[fast]
	}
	return fast
}

// containsNearbyDuplicate reports a duplicate within distance k. O(n)
func containsNearbyDuplicate(arr []int, k int) bool {
	if len(arr) == 0 {
		return false
	}
	hs := map[int]bool{}
	for i := 0; i < len(arr); i++ {
		if hs[arr[i]] {
			return true
		}
		if len(hs) >= k {
			delete(hs, arr[i-k])
		}
		hs[arr[i]] = true
	}
	return false
}

// selfExcludingProduct builds a product array without division. O(n)
func selfExcludingProduct(a []int) []int {
	temp := 1
	prod := make([]int, len(a))
	for i := 0; i < len(a); i++ {
		prod[i] = temp
		temp *= a[i]
	}
	temp = 1
	for i := len(a) - 1; i >= 0; i-- {
		prod[i] *= temp
		temp *= a[i]
	}
	return prod
}

// printIntersection prints the intersection of two sorted arrays.
func printIntersection(arr1, arr2 []int, m, n int) {
	i, j := 0, 0
	for i < m && j < n {
		if arr1[i] < arr2[j] {
			i++
		} else if arr2[j] < arr1[i] {
			j++
		} else {
			fmt.Print(arr2[j], " ")
			j++
			i++
		}
	}
}

// printUnion prints the union of two sorted arrays.
func printUnion(arr1, arr2 []int, m, n int) int {
	i, j := 0, 0
	for i < m && j < n {
		if arr1[i] < arr2[j] {
			fmt.Print(arr1[i], " ")
			i++
		} else if arr2[j] < arr1[i] {
			fmt.Print(arr2[j], " ")
			j++
		} else {
			fmt.Print(arr2[j], " ")
			j++
			i++
		}
	}
	for i < m {
		fmt.Print(arr1[i], " ")
		i++
	}
	for j < n {
		fmt.Print(arr2[j], " ")
		j++
	}
	return 0
}

// findCommon prints common elements in three sorted arrays. O(n1+n2+n3)
func findCommon(ar1, ar2, ar3 []int, n1, n2, n3 int) {
	i, j, k := 0, 0, 0
	for i < n1 && j < n2 && k < n3 {
		if ar1[i] == ar2[j] && ar2[j] == ar3[k] {
			fmt.Print(ar1[i])
			i++
			j++
			k++
		} else if ar1[i] < ar2[j] {
			i++
		} else if ar2[j] < ar3[k] {
			j++
		} else {
			k++
		}
	}
}

// minDist returns the minimum distance between values x and y in arr.
func minDist(arr []int, n, x, y int) int {
	i := 0
	minD := math.MaxInt32
	prev := 0
	for i = 0; i < n; i++ {
		if arr[i] == x || arr[i] == y {
			prev = i
			break
		}
	}
	for ; i < n; i++ {
		if arr[i] == x || arr[i] == y {
			if arr[prev] != arr[i] && (i-prev) < minD {
				minD = i - prev
				prev = i
			} else {
				prev = i
			}
		}
	}
	return minD
}

// findFirstRepeating returns the first repeating element. O(n)
func findFirstRepeating(a []int) int {
	min := -1
	hash := map[int]bool{}
	for i := len(a); i > 0; i-- {
		if hash[a[i]] {
			min = i
		} else {
			hash[a[i]] = true
		}
	}
	return a[min]
}

// findCrossOver finds the cross over point for k-closest searches.
func findCrossOver(arr []int, low, high, x int) int {
	if arr[high] <= x { // x is greater than all
		return high
	}
	if arr[low] > x { // x is smaller than all
		return low
	}
	mid := (low + high) / 2
	if arr[mid] <= x && arr[mid+1] > x {
		return mid
	}
	if arr[mid] < x {
		return findCrossOver(arr, mid+1, high, x)
	}
	return findCrossOver(arr, low, mid-1, x)
}

// printKclosest prints the k elements closest to x in arr.
func printKclosest(arr []int, x, k, n int) {
	l := findCrossOver(arr, 0, n-1, x)
	r := l + 1
	count := 0
	if arr[l] == x {
		l--
	}
	for l >= 0 && r < n && count < k {
		if x-arr[l] < arr[r]-x {
			fmt.Println(arr[l])
			l--
		} else {
			fmt.Println(arr[r])
			r++
		}
		count++
	}
	for count < k && l >= 0 {
		fmt.Println(arr[l])
		l--
	}
	count++
	for count < k && r < n {
		fmt.Println(arr[r])
		r++
	}
	count++
}
