package main

import (
	"fmt"
	"math"
	"math/rand"
	"sort"
)

// Triplet is used while merging k sorted lists with a heap.
type Triplet struct {
	pos   int
	val   int
	index int
}

// MergeArray merges two sorted arrays into one sorted array. Time = O(N+M)
func MergeArray(a, b []int) []int {
	answer := make([]int, len(a)+len(b))
	i, j, k := 0, 0, 0
	for i < len(a) && j < len(b) {
		if a[i] < b[j] {
			answer[k] = a[i]
			k++
			i++
		} else {
			answer[k] = b[j]
			k++
			j++
		}
	}
	for i < len(a) {
		answer[k] = a[i]
		k++
		i++
	}
	for j < len(b) {
		answer[k] = b[j]
		k++
		j++
	}
	return answer
}

// mergeUsingHeap merges k sorted lists in O(nk*Logk) time using a Min Heap.
func mergeUsingHeap(chunks [][]int) []int {
	result := []int{}
	minHeap := newBinHeap[Triplet](func(a, b Triplet) bool { return a.val < b.val })
	// add first element of every chunk into queue
	for i := 0; i < len(chunks); i++ {
		p := Triplet{pos: i, val: chunks[i][0], index: 0}
		minHeap.push(p)
	}
	for !minHeap.isEmpty() {
		p := minHeap.pop()
		result = append(result, p.val)
		if p.index < len(chunks[p.pos]) {
			p.val = chunks[p.pos][p.index+1]
			p.index++
			minHeap.push(p)
		}
	}
	return result
}

// merge merges b into a in sorted order, where a has buffer space at the end.
func merge(a, b []int, lastA, lastB int) {
	indexMerged := lastB + lastA - 1 // Index of last location of merged array
	indexA := lastA - 1              // Index of last element in array a
	indexB := lastB - 1              // Index of last element in array b
	for indexB >= 0 {
		if indexA >= 0 && a[indexA] > b[indexB] {
			a[indexMerged] = a[indexA]
			indexA--
		} else {
			a[indexMerged] = b[indexB]
			indexB--
		}
		indexMerged--
	}
}

// findKSmallestElement finds the k-th smallest element in the union of two
// sorted arrays. Time Complexity: O(log(m + n))
func findKSmallestElement(A []int, startA, endA int, B []int, startB, endB, k int) int {
	n := endA - startA
	m := endB - startB
	if n <= 0 {
		return B[startB+k-1]
	}
	if m <= 0 {
		return A[startA+k-1]
	}
	if k == 1 {
		if A[startA] < B[startB] {
			return A[startA]
		}
		return B[startB]
	}
	midA := (startA + endA) / 2
	midB := (startB + endB) / 2
	if A[midA] <= B[midB] {
		if n/2+m/2+1 >= k {
			return findKSmallestElement(A, startA, endA, B, startB, midB, k)
		}
		return findKSmallestElement(A, midA+1, endA, B, startB, endB, k-n/2-1)
	}
	if n/2+m/2+1 >= k {
		return findKSmallestElement(A, startA, midA, B, startB, endB, k)
	}
	return findKSmallestElement(A, startA, endA, B, midB+1, endB, k-m/2-1)
}

// findMedianSortedArrays returns the median of two sorted arrays.
func findMedianSortedArrays(A, B []int) float64 {
	lengthA := len(A)
	lengthB := len(B)
	if (lengthA+lengthB)%2 == 0 {
		r1 := float64(findKSmallestElement(A, 0, lengthA, B, 0, lengthB, (lengthA+lengthB)/2))
		r2 := float64(findKSmallestElement(A, 0, lengthA, B, 0, lengthB, (lengthA+lengthB)/2+1))
		return (r1 + r2) / 2
	}
	return float64(findKSmallestElement(A, 0, lengthA, B, 0, lengthB, (lengthA+lengthB+1)/2))
}

// MedianFinder maintains the running median of a stream of integers using two
// heaps: O(1) find and O(logN) insert.
type MedianFinder struct {
	minHeap       *binHeap[int]
	maxHeap       *binHeap[int]
	numOfElements int
}

// NewMedianFinder constructs a ready-to-use MedianFinder.
func NewMedianFinder() *MedianFinder {
	return &MedianFinder{
		minHeap: newBinHeap[int](func(a, b int) bool { return a < b }),
		maxHeap: newBinHeap[int](func(a, b int) bool { return a > b }),
	}
}

func (mf *MedianFinder) addNumberToStream(num int) {
	mf.maxHeap.push(num)
	if mf.numOfElements%2 == 0 {
		if mf.minHeap.isEmpty() {
			mf.numOfElements++
			return
		} else if mf.maxHeap.peek() > mf.minHeap.peek() {
			maxHeapRoot := mf.maxHeap.pop()
			minHeapRoot := mf.minHeap.pop()
			mf.maxHeap.push(minHeapRoot)
			mf.minHeap.push(maxHeapRoot)
		}
	} else {
		mf.minHeap.push(mf.maxHeap.pop())
	}
	mf.numOfElements++
}

func (mf *MedianFinder) getMedian() float64 {
	if mf.numOfElements%2 != 0 {
		return float64(mf.maxHeap.peek())
	}
	return float64(mf.maxHeap.peek()+mf.minHeap.peek()) / 2.0
}

// MergeUnsortedArrayKthSmallest finds the kth smallest in the merged array of
// two unsorted distinct arrays. Average O(n), worst O(n^2).
func MergeUnsortedArrayKthSmallest(A1, A2 []int, K int) {
	c := make([]int, len(A1)+len(A2))
	length := 0
	for i := 0; i < len(A1); i++ {
		c[i] = A1[i]
		length++
	}
	for j := 0; j < len(A2); j++ {
		c[length+j] = A2[j]
	}
	quickselect(c, 0, len(c)-1, K-1)
}

func quickselect(g []int, lo, hi, k int) int {
	if lo <= hi {
		pivot := randomPartition(g, lo, hi)
		if pivot == k {
			return g[k]
		}
		if pivot > k {
			return quickselect(g, lo, pivot-1, k)
		}
		return quickselect(g, pivot+1, hi, k)
	}
	return 0
}

// randomPartition picks a random pivot between l and r and partitions.
func randomPartition(arr []int, l, r int) int {
	pivot := int(math.Round(float64(l) + rand.Float64()*float64(r-l)))
	swap(arr, pivot, r)
	return partition(arr, l, r)
}

func partition(g []int, lo, hi int) int {
	pivot := g[hi]
	pIndex := lo
	for i := lo; i < hi; i++ {
		if g[i] < pivot {
			swap(g, i, pIndex)
			pIndex++
		}
	}
	swap(g, pIndex, hi)
	return pIndex
}

// secondlargest finds the second largest number in the array.
func secondlargest(a []int) int {
	largest := a[0]
	secondLargest := math.MinInt32
	for i := 1; i < len(a); i++ {
		number := a[i]
		if number > largest {
			secondLargest = largest
			largest = number
		} else if number > secondLargest && number != largest {
			secondLargest = number
		}
	}
	if secondLargest == math.MinInt32 {
		return -1
	}
	return secondLargest
}

// getTopElements finds the k maximum integers from an array using a min heap.
// Time Complexity: O(k + (n-k)Logk)
func getTopElements(arr []int, k int) []int {
	minHeap := newBinHeap[int](func(a, b int) bool { return a < b })
	for i := 0; i < len(arr); i++ {
		currentNum := arr[i]
		if minHeap.len() < k {
			minHeap.push(currentNum)
		} else if currentNum > minHeap.peek() {
			minHeap.pop()
			minHeap.push(currentNum)
		}
	}
	result := make([]int, minHeap.len())
	index := 0
	for !minHeap.isEmpty() {
		result[index] = minHeap.pop()
		index++
	}
	return result
}

// countZeros counts trailing zeros in an array of leading 1s then 0s.
func countZeros(arr []int, n int) int {
	idx := firstZero(arr, 0, n-1)
	if idx == -1 {
		return 0
	}
	return n - idx
}

// firstZero returns the index of the FIRST occurrence of 0. Time: O(Logn)
func firstZero(arr []int, low, high int) int {
	if high >= low {
		mid := low + (high-low)/2
		if (mid == 0 || arr[mid-1] == 1) && arr[mid] == 0 {
			return mid
		}
		if arr[mid] == 1 {
			return firstZero(arr, mid+1, high)
		}
		return firstZero(arr, low, mid-1)
	}
	return -1
}

// GetmNumberOfSubsets counts subsets that sum to a value. O(Sum * N) time.
func GetmNumberOfSubsets(numbers []int, sum int) int {
	dp := make([]int, sum+1)
	dp[0] = 1
	currentSum := 0
	for i := 0; i < len(numbers); i++ {
		currentSum += numbers[i]
		for j := minInt(sum, currentSum); j >= numbers[i]; j-- {
			dp[j] += dp[j-numbers[i]]
		}
	}
	return dp[sum]
}

// combinationSum4 counts ordered combinations adding up to target.
func combinationSum4(nums []int, target int) int {
	comb := make([]int, target+1)
	comb[0] = 1
	for i := 1; i < len(comb); i++ {
		for j := 0; j < len(nums); j++ {
			if i-nums[j] >= 0 {
				comb[i] += comb[i-nums[j]]
			}
		}
	}
	return comb[target]
}

// twoSumSortedArray finds two numbers (reusable) summing to target.
func twoSumSortedArray(A []int, target int) []int {
	left, right := 0, len(A)-1
	for left < right {
		s := A[left] + A[right]
		if A[left] == target/2 || A[right] == target/2 {
			return []int{target / 2, target / 2}
		}
		if s == target {
			return []int{A[left], A[right]}
		} else if s > target {
			right--
		} else {
			left++
		}
	}
	return nil
}

// kSum solves the k-Sum problem. Time = O(N^k)
func kSum(num []int, k, target, startIndex int) [][]int {
	result := [][]int{}
	if k == 0 {
		if target == 0 {
			result = append(result, []int{})
		}
		return result
	}
	for i := startIndex; i < len(num)-k+1; i++ {
		if i > startIndex && num[i] == num[i-1] {
			continue
		}
		for _, item := range kSum(num, k-1, target-num[i], i+1) {
			item = append([]int{i}, item...)
			result = append(result, item)
		}
	}
	return result
}

// twoSum returns 1-based indices of two numbers adding to target. O(n)
func twoSum(numbers []int, target int) []int {
	m := map[int]int{}
	result := []int{}
	for i := 0; i < len(numbers); i++ {
		if idx, ok := m[numbers[i]]; ok {
			result = append(result, idx+1)
			result = append(result, i+1)
			break
		}
		m[target-numbers[i]] = i
	}
	return result
}

// TwoSumStore supports O(1) 2-sum existence checks by precomputing sums.
type TwoSumStore struct {
	set  map[int]bool
	nums []int
}

// NewTwoSumStore constructs a ready-to-use TwoSumStore.
func NewTwoSumStore() *TwoSumStore {
	return &TwoSumStore{set: map[int]bool{}}
}

func (t *TwoSumStore) store(input int) {
	if len(t.nums) != 0 {
		for _, num := range t.nums {
			t.set[input+num] = true
		}
	}
	t.nums = append(t.nums, input)
}

func (t *TwoSumStore) faster2Sum(val int) bool {
	return t.set[val]
}

// countPairsWithDiffK counts distinct pairs with difference k. O(nlogn)
func countPairsWithDiffK(arr []int, n, k int) int {
	count := 0
	sort.Ints(arr)
	l := 0
	r := 0
	for r < n {
		if arr[r]-arr[l] == k {
			count++
			l++
			r++
		} else if arr[r]-arr[l] > k {
			l++
		} else {
			r++
		}
	}
	return count
}

// twoSumWithDuplicates returns unique ascending pairs adding to target.
func twoSumWithDuplicates(num []int, target int) [][]int {
	list := [][]int{}
	n := len(num)
	if n < 2 {
		return list
	}
	m := map[int]int{}
	for i := 0; i < n; i++ {
		k1, k2 := num[i], target-num[i]
		if cnt, ok := m[k2]; ok && cnt > 0 {
			var pair []int
			if k1 < k2 {
				pair = []int{k1, k2}
			} else {
				pair = []int{k2, k1}
			}
			if !containsPair(list, pair) {
				list = append(list, pair)
			}
			m[k2] = m[k2] - 1
		} else {
			if _, ok := m[k1]; !ok {
				m[k1] = 1
			} else {
				m[k1] = m[k1] + 1
			}
		}
	}
	return list
}

func containsPair(lists [][]int, pair []int) bool {
	for _, l := range lists {
		if len(l) == len(pair) {
			same := true
			for i := range l {
				if l[i] != pair[i] {
					same = false
					break
				}
			}
			if same {
				return true
			}
		}
	}
	return false
}

// find_triplets prints all unique triplets summing to zero. Time = O(n^2)
func find_triplets(arr []int) {
	sort.Ints(arr)
	n := len(arr)
	for i := 0; i < n; i++ {
		j := i + 1
		k := n - 1
		if i > 0 && arr[i] == arr[i-1] {
			continue
		}
		for j < k {
			sumTwo := arr[i] + arr[j]
			if sumTwo+arr[k] < 0 {
				j++
			} else if sumTwo+arr[k] > 0 {
				k--
			} else {
				fmt.Println(arr[i], arr[j], arr[k])
				for j < k && arr[j] == arr[j+1] {
					j++
				}
				for j < k && arr[k] == arr[k-1] {
					k--
				}
				j++
				k--
			}
		}
	}
}

func find_tripletsDuplicates(arr []int) {
	seen := map[string]bool{}
	for i := 0; i < len(arr); i++ {
		out := twoSumWithDuplicatesIndex(arr, -arr[i], i)
		for _, list := range out {
			list = append(list, i)
			sort.Ints(list)
			key := fmt.Sprint(list)
			if !seen[key] {
				fmt.Println(list[0], list[1], list[2])
				seen[key] = true
			}
		}
	}
}

func twoSumWithDuplicatesIndex(num []int, target, exclude int) [][]int {
	list := [][]int{}
	n := len(num)
	if n < 2 {
		return list
	}
	m := map[int]int{}
	for i := 0; i < n; i++ {
		if i == exclude {
			continue
		}
		k1, k2 := num[i], target-num[i]
		if v, ok := m[k2]; ok {
			list = append(list, []int{i, v})
		} else {
			if _, ok := m[k1]; !ok {
				m[k1] = i
			}
		}
	}
	return list
}

// threeSumClosest returns the sum of three integers closest to target. O(n^2)
func threeSumClosest(num []int, target int) int {
	sort.Ints(num)
	min := math.MaxInt32
	result := 0
	for i := 0; i < len(num); i++ {
		j := i + 1
		k := len(num) - 1
		for j < k {
			sum := num[i] + num[j] + num[k]
			diff := absInt(sum - target)
			if diff == 0 {
				return sum
			}
			if diff < min {
				min = diff
				result = sum
			}
			if sum <= target {
				j++
			} else {
				k--
			}
		}
	}
	return result
}

// threeSum_Multiple determines if any 3 integers (reusable) sum to 0.
func threeSum_Multiple(arr []int) []int {
	sort.Ints(arr)
	n := len(arr)
	for i := 0; i < n; i++ {
		if arr[i] == 0 {
			return []int{0, 0, 0}
		}
		j := i
		k := n - 1
		for j < k {
			sum := arr[i] + arr[j] + arr[k]
			if sum < 0 {
				j++
			} else if sum > 0 {
				k--
			} else {
				return []int{arr[i], arr[j], arr[k]}
			}
		}
	}
	return nil
}

// threeSumSmaller counts triplets with sum < target. Time = O(n^2)
func threeSumSmaller(nums []int, target int) int {
	sort.Ints(nums)
	sum := 0
	for i := 0; i < len(nums)-2; i++ {
		sum += twoSumSmaller(nums, i+1, target-nums[i])
	}
	return sum
}

func twoSumSmaller(nums []int, startIndex, target int) int {
	sum := 0
	left := startIndex
	right := len(nums) - 1
	for left < right {
		if nums[left]+nums[right] < target {
			sum += right - left
			left++
		} else {
			right--
		}
	}
	return sum
}
