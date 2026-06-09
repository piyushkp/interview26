package main

import (
	"fmt"
	"math"
	"sort"
)

// sort0and1 sorts an array of only 0s and 1s in place.
func sort0and1(arr []int, size int) {
	left, right := 0, size-1
	for left < right {
		for arr[left] == 0 && left < right {
			left++
		}
		for arr[right] == 1 && left < right {
			right--
		}
		if left < right {
			arr[left] = 0
			arr[right] = 1
		}
	}
}

// sort012 sorts an array of 0s, 1s and 2s (Dutch national flag).
func sort012(a []int) []int {
	low := 0
	mid := 0
	high := len(a) - 1
	for mid <= high {
		if a[mid] == 0 {
			swap(a, low, mid)
			low++
			mid++
		} else if a[mid] == 1 {
			mid++
		} else if a[mid] == 2 {
			swap(a, mid, high)
			high--
		}
	}
	return a
}

// sortKColors2TwoPass sorts k colors using counting sort. O(k) space, O(n) time.
func sortKColors2TwoPass(colors []int, k int) {
	count := make([]int, k)
	for _, color := range colors {
		count[color-1]++
	}
	index := 0
	for i := 0; i < k; i++ {
		for count[i] > 0 {
			colors[index] = i + 1
			index++
			count[i]--
		}
	}
}

// sortKColors2 sorts k colors by repeatedly partitioning into min/middle/max.
func sortKColors2(colors []int, k int) {
	pl := 0
	pr := len(colors) - 1
	i := 0
	min := 1
	max := k
	for min < max {
		for i <= pr {
			if colors[i] == min {
				swap(colors, pl, i)
				i++
				pl++
			} else if colors[i] == max {
				swap(colors, pr, i)
				pr--
			} else {
				i++
			}
		}
		i = pl
		min++
		max--
	}
}

// sortNegPos moves negatives to the front (order not preserved). O(n) time.
func sortNegPos(arr []int) {
	left, right := 0, len(arr)-1
	for left < right {
		for arr[left] < 0 && left < right {
			left++
		}
		for arr[right] > 0 && left < right {
			right--
		}
		if left < right {
			swap(arr, left, right)
		}
	}
}

// rearrangeWithOrder alternates positive/negative numbers preserving order.
func rearrangeWithOrder(arr []int, n int) {
	outofplace := -1
	for index := 0; index < n; index++ {
		if outofplace >= 0 {
			if (arr[index] >= 0 && arr[outofplace] < 0) || (arr[index] < 0 && arr[outofplace] >= 0) {
				rightrotate(arr, n, outofplace, index)
				if index-outofplace > 2 {
					outofplace = outofplace + 2
				} else {
					outofplace = -1
				}
			}
		}
		if outofplace == -1 {
			if (arr[index] >= 0 && index%2 == 0) || (arr[index] < 0 && index%2 != 0) {
				outofplace = index
			}
		}
	}
}

// rightrotate right-rotates elements between [outofplace, cur]. (n is unused,
// kept to mirror the original signature.)
func rightrotate(arr []int, n, outofplace, cur int) {
	tmp := arr[cur]
	for i := cur; i > outofplace; i-- {
		arr[i] = arr[i-1]
	}
	arr[outofplace] = tmp
}

// rearrange places positive/negative numbers alternately. O(n) time, O(1) space.
func rearrange(arr []int, n int) {
	i := -1
	for j := 0; j < n; j++ {
		if arr[j] < 0 {
			i++
			swap(arr, arr[i], arr[j])
		}
	}
	pos := i + 1
	neg := 0
	for pos < n && neg < pos && arr[neg] < 0 {
		swap(arr, arr[neg], arr[pos])
		pos++
		neg += 2
	}
}

// wiggleSort arranges so that s1 <= s2 >= s3 <= s4 ...
func wiggleSort(nums []int) []int {
	if nums == nil || len(nums) <= 1 {
		return nums
	}
	for i := 0; i < len(nums)-1; i++ {
		if i%2 == 0 {
			if nums[i] > nums[i+1] {
				swap(nums, i, i+1)
			}
		} else {
			if nums[i] < nums[i+1] {
				swap(nums, i, i+1)
			}
		}
	}
	return nums
}

// wiggleSortll reorders so that nums[0] < nums[1] > nums[2] < nums[3] ...
func wiggleSortll(nums []int) {
	median := 0
	n := len(nums)
	left, i, right := 0, 0, n-1
	for i <= right {
		if nums[newIndex(i, n)] > median {
			swap(nums, newIndex(left, n), newIndex(i, n))
			left++
			i++
		} else if nums[newIndex(i, n)] < median {
			swap(nums, newIndex(right, n), newIndex(i, n))
			right--
		} else {
			i++
		}
	}
}

func newIndex(index, n int) int {
	return (1 + 2*index) % (n | 1)
}

// printTwoOdd prints the two numbers with odd occurrences.
func printTwoOdd(arr []int, size int) {
	xor2 := arr[0]
	var setBitNo, x, y int
	for i := 1; i < size; i++ {
		xor2 = xor2 ^ arr[i]
	}
	setBitNo = xor2 & ^(xor2 - 1)
	for i := 0; i < size; i++ {
		if arr[i]&setBitNo == 0 {
			x = x ^ arr[i]
		} else {
			y = y ^ arr[i]
		}
	}
	fmt.Print(x, " ", y)
}

// findLongestConseqSubseq returns the length of the longest consecutive
// subsequence (elements may be in any order).
func findLongestConseqSubseq(arr []int) int {
	m := map[int]bool{}
	maxCount := 0
	count := 1
	for i := 0; i < len(arr); i++ {
		m[arr[i]] = true
	}
	for i := 0; i < len(arr); i++ {
		if !m[arr[i]-1] {
			temp := arr[i] + 1
			for m[temp] {
				temp++
				count++
			}
			maxCount = maxInt(count, maxCount)
			count = 1
		}
	}
	return maxCount
}

// findLength returns the longest subarray of distinct contiguous numbers.
func findLength(arr []int, n int) int {
	maxLen := 1
	for i := 0; i < n-1; i++ {
		mn := arr[i]
		mx := arr[i]
		for j := i + 1; j < n; j++ {
			mn = minInt(mn, arr[j])
			mx = maxInt(mx, arr[j])
			if (mx - mn) == j-i {
				maxLen = maxInt(maxLen, mx-mn+1)
			}
		}
	}
	return maxLen
}

// findContiguousLength returns the largest subarray with contiguous elements
// (duplicates allowed). Time Complexity: O(n^2)
func findContiguousLength(a []int) int {
	n := len(a)
	maxLen := 1
	for i := 0; i < n-1; i++ {
		set := map[int]bool{}
		set[a[i]] = true
		mn := a[i]
		mx := a[i]
		for j := i + 1; j < n; j++ {
			if set[a[j]] {
				break
			}
			set[a[j]] = true
			mn = minInt(mn, a[j])
			mx = maxInt(mx, a[j])
			if mx-mn == j-i {
				maxLen = maxInt(maxLen, mx-mn+1)
			}
		}
	}
	return maxLen
}

// printClosest prints the pair (one from each sorted array) closest to x.
func printClosest(ar1, ar2 []int, m, n, x int) {
	diff := math.MaxInt32
	resL, resR := 0, 0
	l, r := 0, n-1
	for l < m && r >= 0 {
		if absInt(ar1[l]+ar2[r]-x) < diff {
			resL = l
			resR = r
			diff = absInt(ar1[l] + ar2[r] - x)
		}
		if ar1[l]+ar2[r] > x {
			r--
		} else {
			l++
		}
	}
	fmt.Print(ar1[resL], " ", ar2[resR])
}

// printMaxActivities prints the max set of non-overlapping activities (greedy).
func printMaxActivities(s, f []int, n int) {
	sort.Ints(f)
	i := 0
	fmt.Print(i)
	for j := 1; j < n; j++ {
		if s[j] >= f[i] {
			fmt.Println(j)
			i = j
		}
	}
}

// minCost finds the minimum cost to travel from station 0 to N-1.
func minCost(ticket [][]int) int {
	T := make([]int, len(ticket))
	T1 := make([]int, len(ticket))
	T1[0] = -1
	for i := 1; i < len(T); i++ {
		T[i] = ticket[0][i]
		T1[i] = i - 1
	}
	for i := 1; i < len(T); i++ {
		for j := i + 1; j < len(T); j++ {
			if T[j] > T[i]+ticket[i][j] {
				T[j] = T[i] + ticket[i][j]
				T1[j] = i
			}
		}
	}
	i := len(ticket) - 1
	for i != -1 {
		fmt.Print(i, " ")
		i = T1[i]
	}
	fmt.Println()
	return T[len(ticket)-1]
}

// findPlatform finds the minimum number of platforms required. O(nLogn)
func findPlatform(arr, dep []int, n int) int {
	sort.Ints(arr)
	sort.Ints(dep)
	platNeeded := 1
	result := 1
	i, j := 1, 0
	for i < n && j < n {
		if arr[i] < dep[j] {
			platNeeded++
			i++
			if platNeeded > result {
				result = platNeeded
			}
		} else {
			platNeeded--
			j++
		}
	}
	return result
}

// maxOnesIndex finds the index of the 0 to flip to get the longest run of 1s.
func maxOnesIndex(arr []int, n int) int {
	maxCount := 0
	maxIndex := -1
	prevZero := -1
	prevPrevZero := -1
	for curr := 0; curr < n; curr++ {
		if arr[curr] == 0 {
			if curr-prevPrevZero > maxCount {
				maxCount = curr - prevPrevZero
				maxIndex = prevZero
			}
			prevPrevZero = prevZero
			prevZero = curr
		}
	}
	if n-prevPrevZero > maxCount {
		maxIndex = prevZero
	}
	return maxIndex
}

// findmaxOne returns the longest run of 1s after flipping at most k zeros.
func findmaxOne(a []int, k int) int {
	maxCount := 0
	maxIndex := 0
	currCount := 0
	for i := 0; i < len(a); i++ {
		if a[i] == 0 && maxIndex < k {
			currCount++
			maxIndex++
		} else if a[i] == 1 {
			currCount++
		} else {
			maxCount = maxInt(maxCount, currCount)
			maxIndex = 0
			currCount = 0
		}
	}
	maxCount = maxInt(maxCount, currCount)
	return maxCount
}

// matchPairs matches nuts and bolts (quicksort style). Time = O(nlogn)
func matchPairs(nuts, bolts []byte, low, high int) {
	if low < high {
		pivot := partitionChar(nuts, low, high, bolts[high])
		partitionChar(bolts, low, high, nuts[pivot])
		matchPairs(nuts, bolts, low, pivot-1)
		matchPairs(nuts, bolts, pivot+1, high)
	}
}

// partitionChar partitions a char array around an externally supplied pivot.
func partitionChar(arr []byte, low, high int, pivot byte) int {
	i := low
	var temp1, temp2 byte
	for j := low; j < high; j++ {
		if arr[j] < pivot {
			temp1 = arr[i]
			arr[i] = arr[j]
			arr[j] = temp1
			i++
		} else if arr[j] == pivot {
			temp1 = arr[j]
			arr[j] = arr[high]
			arr[high] = temp1
			j--
		}
	}
	temp2 = arr[i]
	arr[i] = arr[high]
	arr[high] = temp2
	return i
}

// removeDup removes duplicates from an unsorted array.
func removeDup(a []int) []int {
	set := map[int]bool{}
	k := 0
	if len(a) < 2 {
		return a
	}
	for i := 0; i < len(a); i++ {
		if !set[a[i]] {
			a[k] = a[i]
			k++
			set[a[i]] = true
		}
	}
	return a[:k]
}

// removeDuplicates removes duplicates in place from a sorted array.
func removeDuplicates(A []int) []int {
	if len(A) < 2 {
		return A
	}
	j := 0
	i := 1
	for i < len(A) {
		if A[i] == A[j] {
			i++
		} else {
			j++
			A[j] = A[i]
			i++
		}
	}
	return A[:j+1]
}

// removeDuplicates1 allows each element at most twice.
func removeDuplicates1(nums []int) int {
	i := 0
	for _, n := range nums {
		if i < 2 || n > nums[i-2] {
			nums[i] = n
			i++
		}
	}
	return i
}

// findUnique returns integers that appear exactly once (unsorted input).
func findUnique(a []int) []int {
	m := map[int]int{}
	out := []int{}
	for i := 0; i < len(a); i++ {
		m[a[i]]++
	}
	for key, value := range m {
		if value == 1 {
			out = append(out, key)
		}
	}
	return out
}

// findUniqueSorted prints integers that appear exactly once (sorted input).
func findUniqueSorted(nums []int) {
	count := 0
	for i := 0; i < len(nums); i++ {
		if i == len(nums)-1 {
			if count == 0 {
				fmt.Println(nums[i])
			}
			break
		}
		if nums[i] != nums[i+1] {
			if count == 0 {
				fmt.Println(nums[i])
			}
			count = 0
		} else {
			count++
		}
	}
}

// findUniqueNumbers returns unique numbers from a sorted array using binary
// search. Average O(logn), worst O(N).
func findUniqueNumbers(data []int) []int {
	result := []int{}
	for i := 0; i < len(data); {
		temp := last(data, i, len(data)-1, data[i], len(data))
		if i == temp {
			result = append(result, data[i])
			i++
		} else {
			i = temp + 1
		}
	}
	return result
}

// checkDuplicatesWithinK reports a duplicate within distance k.
func checkDuplicatesWithinK(a []int, k int) bool {
	hash := map[int]bool{}
	for i := 0; i < len(a); i++ {
		if hash[a[i]] {
			return true
		}
		hash[a[i]] = true
		if i >= k {
			delete(hash, a[i-k])
		}
	}
	return false
}

// containsNearbyAlmostDuplicate reports indices i,j with |nums[i]-nums[j]|<=t
// and |i-j|<=k using bucketing.
func containsNearbyAlmostDuplicate(nums []int, k, t int) bool {
	if k < 1 || t < 0 {
		return false
	}
	m := map[int64]int64{}
	for i := 0; i < len(nums); i++ {
		remappedNum := int64(nums[i]) - int64(math.MinInt32)
		bucket := remappedNum / (int64(t) + 1)
		if _, ok := m[bucket]; ok {
			return true
		}
		if v, ok := m[bucket-1]; ok && remappedNum-v <= int64(t) {
			return true
		}
		if v, ok := m[bucket+1]; ok && v-remappedNum <= int64(t) {
			return true
		}
		if len(m) >= k {
			lastBucket := (int64(nums[i-k]) - int64(math.MinInt32)) / (int64(t) + 1)
			delete(m, lastBucket)
		}
		m[bucket] = remappedNum
	}
	return false
}

// canJump reports whether the last index is reachable.
func canJump(A []int) bool {
	if len(A) <= 1 {
		return true
	}
	max := A[0] // largest index that can be reached
	for i := 0; i < len(A); i++ {
		if max <= i && A[i] == 0 {
			return false
		}
		if i+A[i] > max {
			max = i + A[i]
		}
		if max >= len(A)-1 {
			return true
		}
	}
	return false
}

// minJump returns the minimum number of jumps to reach the last index.
func minJump(nums []int) int {
	if nums == nil || len(nums) == 0 {
		return 0
	}
	lastReach := 0
	reach := 0
	step := 0
	for i := 0; i <= reach && i < len(nums); i++ {
		if i > lastReach {
			step++
			lastReach = reach
		}
		reach = maxInt(reach, nums[i]+i)
	}
	if reach < len(nums)-1 {
		return 0
	}
	return step
}

// removeNumber removes all instances of n in place, returning the new length.
func removeNumber(A []int, n int) int {
	if A == nil || len(A) == 0 {
		return 0
	}
	i := 0
	for j := 0; j < len(A); j++ {
		if A[j] != n {
			A[i] = A[j]
			i++
		}
	}
	return i
}

// findMaxSliding prints the maximum of every window of size k. O(n) time.
func findMaxSliding(x []int, k int) {
	q := []int{} // holds indices, front at q[0], back at q[len-1]
	i := 0
	for ; i < k; i++ {
		for len(q) > 0 && x[q[len(q)-1]] <= x[i] {
			q = q[:len(q)-1]
		}
		q = append(q, i)
	}
	for ; i < len(x); i++ {
		fmt.Println(x[q[0]])
		for len(q) > 0 && q[0] <= i-k {
			q = q[1:]
		}
		for len(q) > 0 && x[q[len(q)-1]] <= x[i] {
			q = q[:len(q)-1]
		}
		q = append(q, i)
	}
	fmt.Println(x[q[0]])
}

// rearrange0 arranges max, min, second-max, second-min ... in place. O(n)
func rearrange0(arr []int, n int) {
	sort.Ints(arr)
	maxIdx := n - 1
	minIdx := 0
	maxElem := arr[n-1] + 1
	for i := 0; i < n; i++ {
		if i%2 == 0 {
			arr[i] += (arr[maxIdx] % maxElem) * maxElem
			maxIdx--
		} else {
			arr[i] += (arr[minIdx] % maxElem) * maxElem
			minIdx++
		}
	}
	for i := 0; i < n; i++ {
		arr[i] = arr[i] / maxElem
	}
}

// rearrange1 arranges max, min, ... in place using cyclic replacements.
func rearrange1(arr []int, n int) {
	for i := 0; i < n; i++ {
		temp := arr[i]
		for temp > 0 {
			j := 0
			if i < n/2 {
				j = 2*i + 1
			} else {
				j = 2 * (n - 1 - i)
			}
			if i == j {
				arr[i] = -temp
				break
			}
			swap(arr, temp, arr[j])
			arr[j] = -arr[j]
			i = j
		}
	}
	for i := 0; i < n; i++ {
		arr[i] = -arr[i]
	}
}
