package main

import (
	"fmt"
	"math"
)

// subArraySumPositive prints a subarray (positive numbers) summing to target.
func subArraySumPositive(A []int, target int) {
	for i, j, sum := 0, 0, 0; i < len(A); i++ {
		for ; j < len(A) && sum < target; j++ {
			sum += A[j]
		}
		if sum == target {
			fmt.Print("Start index: ", i, " End index: ", j-1)
			return
		}
		sum -= A[i]
	}
	fmt.Print("No SubArray Found.")
}

func isValid(a []int, sum int) bool {
	count, temp := 0, 0
	for i := 0; i < len(a); i++ {
		temp += a[i]
		for temp > sum {
			temp -= a[count]
			count++
		}
		if temp == sum {
			return true
		}
	}
	return false
}

// subArraySum prints a subarray (with negatives) summing to sum.
func subArraySum(arr []int, sum int) {
	m := map[int]int{}
	currSum := 0
	for i := 0; i < len(arr); i++ {
		currSum += arr[i]
		if currSum == sum {
			fmt.Print("Sum found at ", 0, "and ", i)
			return
		}
		if v, ok := m[currSum-sum]; ok {
			fmt.Print("Sum found at ", v, 1, "and ", i)
			return
		}
		m[currSum] = i
	}
}

// allSubArraySum prints all subarrays summing to k (handles negatives).
func allSubArraySum(arr []int, k int) {
	m := map[int][]int{}
	preSum := 0
	m[0] = []int{-1}
	for i := 0; i < len(arr); i++ {
		preSum += arr[i]
		if starts, ok := m[preSum-k]; ok {
			for _, start := range starts {
				fmt.Println("Start:", start+1, "\tEnd:", i)
			}
		}
		newStart := []int{}
		if v, ok := m[preSum]; ok {
			newStart = v
		}
		newStart = append(newStart, i)
		m[preSum] = newStart
	}
}

// maxSubArraySumLen returns the max length subarray summing to k.
func maxSubArraySumLen(arr []int, k int) int {
	m := map[int]int{}
	max := 0
	currSum := 0
	for i := 0; i < len(arr); i++ {
		currSum += arr[i]
		if currSum == k {
			max = maxInt(max, i+1)
		}
		if v, ok := m[currSum-k]; ok {
			max = maxInt(max, i-v)
		} else {
			m[currSum] = i
		}
	}
	return max
}

// minSubArraySum returns the minimum length subarray summing to k.
func minSubArraySum(arr []int, k int) int {
	m := map[int][]int{}
	currSum := 0
	minLen := math.MaxInt32
	m[0] = []int{-1}
	for i := 0; i < len(arr); i++ {
		currSum += arr[i]
		if items, ok := m[currSum-k]; ok {
			for _, start := range items {
				minLen = minInt(minLen, i-start)
			}
		}
		temp := []int{}
		if v, ok := m[currSum]; ok {
			temp = v
		}
		temp = append(temp, i)
		m[currSum] = temp
	}
	if minLen == math.MaxInt32 {
		return 0
	}
	return minLen
}

// maxSubArrayZero finds the largest subarray with 0 sum.
func maxSubArrayZero(arr []int) int {
	hM := map[int]int{}
	sum := 0
	maxLen := 0
	for i := 0; i < len(arr); i++ {
		sum += arr[i]
		if arr[i] == 0 && maxLen == 0 {
			maxLen = 1
		}
		if sum == 0 {
			maxLen = i + 1
		}
		if prevI, ok := hM[sum]; ok {
			maxLen = maxInt(maxLen, i-prevI)
		} else {
			hM[sum] = i
		}
	}
	return maxLen
}

// maxSubArraySum is Kadane's algorithm for the largest contiguous sum.
func maxSubArraySum(a []int) int {
	maxSoFar := a[0]
	currMax := a[0]
	for i := 1; i < len(a); i++ {
		currMax = maxInt(a[i], currMax+a[i])
		maxSoFar = maxInt(maxSoFar, currMax)
	}
	return maxSoFar
}

// findMaxSumIndex returns {startIndex, endIndex, largestSum}.
func findMaxSumIndex(arr []int) []int {
	result := make([]int, 3)
	maxSoFar := math.MinInt32
	startIndex := 0
	currMax := 0
	for i := 0; i < len(arr); i++ {
		currMax = currMax + arr[i]
		if currMax > maxSoFar {
			maxSoFar = currMax
			result[0] = startIndex
			result[1] = i
			result[2] = maxSoFar
		}
		if currMax < 0 {
			currMax = 0
			startIndex = i + 1
		}
	}
	return result
}

// Stream state for max subarray sum over a stream of input numbers.
var (
	streamList       []int
	streamOut        = make([]int, 3)
	streamMaxSoFar   = math.MinInt32
	streamCurrMax    = 0
	streamStartIndex = 0
)

func maxSubArraySumOfStreamNum(num int) {
	streamList = append(streamList, num)
	if streamCurrMax+num > streamMaxSoFar {
		streamCurrMax = 0
		for i := streamStartIndex; i < len(streamList); i++ {
			streamCurrMax = streamCurrMax + streamList[i]
			if streamCurrMax > streamMaxSoFar {
				streamMaxSoFar = streamCurrMax
				streamOut[0] = streamStartIndex
				streamOut[1] = i
				streamOut[2] = streamMaxSoFar
			}
			if streamCurrMax < 0 {
				streamCurrMax = 0
				streamStartIndex = i + 1
			}
		}
	}
}

func getMaxSubArraySum() []int {
	return streamOut
}

// maxKSubArray finds k non-overlapping subarrays with the largest sum.
func maxKSubArray(nums []int, k int) int {
	if len(nums) < k {
		return 0
	}
	length := len(nums)
	// d[i]: select j subarrays from the first i elements, the max sum.
	d := make([]int, length+1)
	for j := 1; j <= k; j++ {
		for i := length; i >= j; i-- {
			d[i] = math.MinInt32
			endMax := 0
			max := math.MinInt32
			for p := i - 1; p >= j-1; p-- {
				endMax = maxInt(nums[p], endMax+nums[p])
				max = maxInt(endMax, max)
				if d[i] < d[p]+max {
					d[i] = d[p] + max
				}
			}
		}
	}
	return d[length]
}

// maxSubArrayWithK finds the subarray (containing at least k numbers) with the
// largest sum. Time O(n).
func maxSubArrayWithK(a []int, k int) int {
	var i, maxendhere, maxsofar, sumoflastk int
	set := map[int]bool{}
	for i = 0; i < k; i++ {
		maxendhere += a[i]
		set[a[i]] = true
	}
	maxsofar = maxendhere
	sumoflastk = maxendhere
	for ; i < len(a); i++ {
		if set[a[i]] {
			maxendhere += a[i]
		}
		sumoflastk += a[i] - a[i-k]
		if maxendhere < sumoflastk {
			maxendhere = sumoflastk
		}
		if maxsofar < maxendhere {
			maxsofar = maxendhere
		}
		set[a[i]] = true
	}
	return maxsofar
}

// maxSum returns the maximum sum in a subarray of size k.
func maxSum(arr []int, n, k int) int {
	if n < k {
		fmt.Println("Invalid")
		return -1
	}
	res := 0
	for i := 0; i < k; i++ {
		res += arr[i]
	}
	currSum := res
	for i := k; i < n; i++ {
		currSum += arr[i] - arr[i-k]
		res = maxInt(res, currSum)
	}
	return res
}

// maxSum1 returns the max sum window of size k and marks the window as used
// (-1). Simplified: returns 0 on invalid input rather than Java's null.
func maxSum1(arr []int, n, k int) int {
	if n < k {
		fmt.Println("Invalid")
		return 0
	}
	res := 0
	output := make([]int, 2)
	for i := 0; i < k; i++ {
		res += arr[i]
	}
	output[0] = 0
	output[1] = k - 1
	currSum := res
	for i := k; i < n; i++ {
		currSum += arr[i] - arr[i-k]
		if currSum > res {
			res = currSum
			output[0] = i - k + 1
			output[1] = i
		}
	}
	for i := output[0]; i <= output[1]; i++ {
		arr[i] = -1
	}
	return res
}

// maxSum3NonOverlapping sums the three best non-overlapping windows of size k.
func maxSum3NonOverlapping(input []int, k int) int {
	sum := 0
	for i := 0; i < 3; i++ {
		sum += maxSum1(input, len(input), k)
	}
	return sum
}

// smallestSubWithSum returns the smallest subarray length with sum > x.
func smallestSubWithSum(arr []int, n, x int) int {
	currSum := 0
	minLen := n + 1
	start := 0
	end := 0
	for end < n {
		for currSum <= x && end < n {
			currSum += arr[end]
			end++
		}
		for currSum > x && start < n {
			if end-start < minLen {
				minLen = end - start
			}
			currSum -= arr[start]
			start++
		}
	}
	return minLen
}

// findlen returns the length of the longest increasing subarray.
func findlen(a []int) int {
	min := a[0]
	maxLen := 1
	count := 1
	for i := 1; i < len(a); i++ {
		if a[i] > min {
			count++
		} else {
			maxLen = maxInt(maxLen, count)
			count = 1
		}
		min = a[i]
	}
	maxLen = maxInt(maxLen, count)
	return maxLen
}

func CeilIndex(A []int, l, r, key int) int {
	for r-l > 1 {
		m := l + (r-l)/2
		if A[m] >= key {
			r = m
		} else {
			l = m
		}
	}
	return r
}

// LongestIncreasingSubsequenceLength returns the LIS length. Time O(NlogN).
func LongestIncreasingSubsequenceLength(A []int, size int) int {
	temp := make([]int, size)
	var length int
	temp[0] = A[0]
	length = 1
	for i := 1; i < size; i++ {
		if A[i] < temp[0] {
			temp[0] = A[i]
		} else if A[i] > temp[length-1] {
			temp[length] = A[i]
			length++
		} else {
			temp[CeilIndex(temp, -1, length-1, A[i])] = A[i]
		}
	}
	return length
}

// maxLenBitonicSubArray returns the length of the longest bitonic subarray.
func maxLenBitonicSubArray(A []int) int {
	n := len(A)
	if n == 0 {
		return 0
	}
	maxLen := 0
	i := 0
	for i+1 < n {
		length := 1
		// run till sequence is increasing
		for i+1 < n && A[i] < A[i+1] {
			i++
			length++
		}
		// run till sequence is decreasing
		for i+1 < n && A[i] > A[i+1] {
			i++
			length++
		}
		if length > maxLen {
			maxLen = length
		}
	}
	return maxLen
}

// maxSumIS returns the Maximum Sum Increasing Subsequence.
func maxSumIS(arr []int, n int) int {
	var i, j, max int
	msis := make([]int, n)
	for i = 0; i < n; i++ {
		msis[i] = arr[i]
	}
	for i = 1; i < n; i++ {
		for j = 0; j < i; j++ {
			if arr[i] > arr[j] {
				msis[i] = maxInt(msis[j]+arr[i], msis[i])
				max = maxInt(max, msis[i])
			}
		}
	}
	return max
}

// maxSubarrayProduct returns the maximum product of a contiguous subarray.
func maxSubarrayProduct(arr []int) int {
	maxEndingHere := 1
	minEndingHere := 1
	maxSoFar := 1
	for i := 0; i < len(arr); i++ {
		if arr[i] > 0 {
			maxEndingHere = maxEndingHere * arr[i]
			minEndingHere = minInt(minEndingHere*arr[i], 1)
		} else if arr[i] == 0 {
			maxEndingHere = 1
			minEndingHere = 1
		} else {
			temp := maxEndingHere
			maxEndingHere = maxInt(minEndingHere*arr[i], 1)
			minEndingHere = temp * arr[i]
		}
		if maxSoFar < maxEndingHere {
			maxSoFar = maxEndingHere
		}
	}
	return maxSoFar
}
