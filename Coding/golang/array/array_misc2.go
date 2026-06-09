package main

import (
	"fmt"
	"math"
	"sort"
	"strconv"
)

// floatIntPair is a small (key, value) pair used by minimizeRoundSum.
type floatIntPair struct {
	key   float64
	value int
}

// minimizeRoundSum rounds each element so the rounded sum equals T while
// minimizing the total |xi - yi|.
func minimizeRoundSum(input []float64, T int) []int64 {
	var sum float64 = 0
	output := make([]int64, len(input))
	for i := 0; i < len(input); i++ {
		sum += math.Round(input[i])
		output[i] = int64(math.Round(input[i]))
	}
	diff := float64(T) - sum
	if diff != 0 {
		// max-heap by key (delta)
		maxHeap := newBinHeap[floatIntPair](func(a, b floatIntPair) bool { return a.key > b.key })
		for i := 0; i < len(input); i++ {
			delta := math.Abs(input[i] - float64(output[i]))
			if float64(i) < math.Abs(diff) {
				maxHeap.push(floatIntPair{key: delta, value: i})
			} else if !maxHeap.isEmpty() && delta > maxHeap.peek().key {
				maxHeap.pop()
				maxHeap.push(floatIntPair{key: delta, value: i})
			}
		}
		for !maxHeap.isEmpty() && diff != 0 {
			index := maxHeap.pop().value
			if diff > 0 {
				output[index] += 1
				diff -= 1
			} else {
				output[index] -= 1
				diff += 1
			}
		}
	}
	return output
}

// FindNextGreaterElement prints the next greater element for each element.
func FindNextGreaterElement(array []int) {
	stack := []int{}
	stack = append(stack, array[0])
	for i := 1; i < len(array); i++ {
		for len(stack) > 0 && array[i] > stack[len(stack)-1] {
			poppedElement := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			fmt.Println(poppedElement, ",", array[i])
		}
		stack = append(stack, array[i])
	}
	for len(stack) > 0 {
		top := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		fmt.Println(top, ",", -1)
	}
}

// nextGreaterElement prints the next greater element without extra space.
func nextGreaterElement(arr []int) {
	max := arr[len(arr)-1]
	fmt.Println("for el:", arr[len(arr)-1], "next greater is:", -1)
	for i := len(arr) - 2; i >= 0; i-- {
		if arr[i] < arr[i+1] {
			fmt.Println("for", arr[i], "next greater is:", arr[i+1])
		} else if arr[i] < max {
			fmt.Println("for", arr[i], "next greater is:", max)
		} else {
			fmt.Println("for", arr[i], "next greater is:", -1)
		}
		if arr[i+1] > max {
			max = arr[i+1]
		}
	}
}

// incrLargeNumber increments a large number represented as a digit array.
func incrLargeNumber(inputArray []int) []int {
	if inputArray == nil {
		return inputArray
	}
	arrLength := len(inputArray)
	all9s := true
	for i := 0; i < arrLength; i++ {
		if inputArray[i] != 9 {
			all9s = false
			break
		}
	}
	if all9s {
		newInputArray := make([]int, arrLength+1)
		newInputArray[0] = 1
		for i := 1; i < len(newInputArray); i++ {
			newInputArray[i] = 0
		}
		return newInputArray
	}
	for i := arrLength - 1; i > -1; i-- {
		k := inputArray[i]
		if k == 9 {
			inputArray[i] = 0
		} else {
			k++
			inputArray[i] = k
			return inputArray
		}
	}
	return inputArray
}

// getMaxOfMaxPrefix returns the max count of greater elements to the right.
func getMaxOfMaxPrefix(a []int) int {
	if len(a) < 2 {
		return 1
	}
	count := 0
	maxPrefix := 0
	temp := a[0]
	for i := 1; i < len(a); i++ {
		if a[i] > temp {
			count++
		} else {
			temp = a[i]
			count = 0
		}
		if count > maxPrefix {
			maxPrefix = count
		}
	}
	return maxPrefix
}

// sortPartialList sorts an x-sorted list (each element at most x out of place).
func sortPartialList(a []int, x int) []int {
	pq := newBinHeap[int](func(p, q int) bool { return p < q })
	result := make([]int, len(a))
	k := 0
	for i := 0; i < len(a); i++ {
		if i < x {
			pq.push(a[i])
		} else {
			result[k] = pq.pop()
			k++
			pq.push(a[i])
		}
	}
	for !pq.isEmpty() {
		result[k] = pq.pop()
		k++
	}
	return result
}

// divideArray reports whether removing one element splits the array into two
// equal-sum parts.
func divideArray(a []int) bool {
	sum := 0
	sumSoFar := 0
	for i := 0; i < len(a); i++ {
		sum += a[i]
	}
	for i := 0; i < len(a); i++ {
		if 2*sumSoFar+a[i] == sum {
			return true
		}
		sumSoFar += a[i]
	}
	return false
}

// maxIndexDiff finds the maximum j - i such that arr[j] > arr[i].
func maxIndexDiff(arr []int, n int) int {
	var maxDiff int
	var i, j int
	RMax := make([]int, n)
	LMin := make([]int, n)
	LMin[0] = arr[0]
	for i = 1; i < n; i++ {
		LMin[i] = minInt(arr[i], LMin[i-1])
	}
	RMax[n-1] = arr[n-1]
	for j = n - 2; j >= 0; j-- {
		RMax[j] = maxInt(arr[j], RMax[j+1])
	}
	i = 0
	j = 0
	maxDiff = -1
	for j < n && i < n {
		if LMin[i] < RMax[j] {
			maxDiff = maxInt(maxDiff, j-i)
			j = j + 1
		} else {
			i = i + 1
		}
	}
	return maxDiff
}

// pushZerosToEnd moves all zeroes to the end of the array.
func pushZerosToEnd(arr []int) []int {
	left, right := 0, len(arr)-1
	for left < right {
		for arr[left] != 0 && left < right {
			left++
		}
		for arr[right] == 0 && left < right {
			right--
		}
		if left < right {
			arr[left] ^= arr[right]
			arr[right] ^= arr[left]
			arr[left] ^= arr[right]
		}
	}
	return arr
}

// moveZeroWithOrder moves all 0s to the front maintaining non-zero order.
func moveZeroWithOrder(input []int) {
	for lastNonZeroFoundAt, cur := len(input)-1, len(input)-1; cur > 0; cur-- {
		if input[cur] != 0 {
			swap(input, lastNonZeroFoundAt, cur)
			lastNonZeroFoundAt--
		}
	}
}

// MaxSumNonAdjacent returns the max sum of non-adjacent elements (DP, O(n) space).
func MaxSumNonAdjacent(a []int) int {
	output := make([]int, len(a))
	if len(a) == 0 {
		return 0
	} else if len(a) < 2 {
		return a[0]
	} else if len(a) == 2 {
		return maxInt(a[0], a[1])
	} else {
		output[0] = a[0]
		output[1] = maxInt(a[0], a[1])
		for i := 2; i < len(a); i++ {
			temp := maxInt(a[i], a[i]+output[i-2])
			output[i] = maxInt(output[i-1], temp)
		}
	}
	return output[len(a)-1]
}

// FindMaxSumNonAdjacent returns the max sum of non-adjacent elements (O(1) space).
func FindMaxSumNonAdjacent(arr []int) int {
	incl := arr[0]
	excl := 0
	var exclNew int
	for i := 1; i < len(arr); i++ {
		exclNew = maxInt(incl, excl)
		incl = excl + arr[i]
		excl = exclNew
	}
	return maxInt(incl, excl)
}

// printCombination prints all combinations of one element from each array.
func printCombination(input [][]int) {
	result := []int{}
	result = combinationUtil(input, result, 0, "")
	for _, num := range result {
		fmt.Println(num)
	}
}

func combinationUtil(arr [][]int, result []int, level int, current string) []int {
	if level == len(arr) {
		n, _ := strconv.Atoi(current)
		result = append(result, n)
		return result
	}
	for i := 0; i < len(arr[level]); i++ {
		result = combinationUtil(arr, result, level+1, current+strconv.Itoa(arr[level][i]))
	}
	return result
}

// getCombinations returns the cartesian product of the input lists (iterative).
func getCombinations[T any](inputs [][]T) [][]T {
	output := [][]T{}
	index := 0
	for _, i := range inputs[0] {
		newList := []T{i}
		output = append(output, newList)
	}
	index++
	for index < len(inputs) {
		nextList := inputs[index]
		tempOutput := [][]T{}
		for _, prefix := range output {
			for _, second := range nextList {
				tempList := []T{}
				tempList = append(tempList, prefix...)
				tempList = append(tempList, second)
				tempOutput = append(tempOutput, tempList)
			}
		}
		output = tempOutput
		index++
	}
	return output
}

// abc returns the candidate with most votes (ties broken by largest key).
func abc(votes []string) string {
	m := map[string]int{}
	for i := 0; i < len(votes); i++ {
		m[votes[i]]++
	}
	keys := make([]string, 0, len(m))
	for kk := range m {
		keys = append(keys, kk)
	}
	sort.Strings(keys)
	max := math.MinInt32
	key := ""
	for _, entry := range keys {
		if m[entry] >= max {
			key = entry
			max = m[entry]
		}
	}
	return key
}

// MinSwap returns the minimum number of swaps to make b equal to a.
func MinSwap(a, b []int) int {
	m := map[int]int{}
	count := 0
	for i := 0; i < len(a); i++ {
		m[a[i]] = i
	}
	for j := 0; j < len(b); j++ {
		index := m[b[j]]
		if index != j {
			Swap(index, j, b)
			count++
		}
	}
	return count
}

// Kswap performs k swaps to maximize the integer represented by the digits.
func Kswap(arr []int, k int) []int {
	n := len(arr)
	for i := 0; i < k; i++ {
		minIdx := i
		for j := i + 1; j < n; j++ {
			if arr[j] > arr[minIdx] {
				minIdx = j
			}
		}
		swap(arr, minIdx, i)
	}
	return arr
}

// findOneOccurance finds the element that appears once in a sorted array where
// all others appear twice. O(log n)
func findOneOccurance(a []int, low, high int) int {
	if low > high {
		return -1
	}
	if high == low {
		return a[low]
	}
	mid := low + (high-low)/2
	if mid%2 == 0 {
		if a[mid] == a[mid+1] {
			findOneOccurance(a, mid+2, high)
		} else {
			findOneOccurance(a, low, mid)
		}
	} else {
		if a[mid] == a[mid-1] {
			findOneOccurance(a, mid+1, high)
		} else {
			findOneOccurance(a, low, mid-1)
		}
	}
	return -1
}

// findRepeatingNum returns the element that repeats in a sorted array.
func findRepeatingNum(a []int) int {
	low, high := 0, len(a)
	for low != high {
		mid := (low + high) / 2
		if (a[mid] - a[0]) >= mid {
			low = mid + 1
		} else {
			high = mid
		}
	}
	return a[low]
}

// minMaxPair holds a min and max value.
type minMaxPair struct {
	min int
	max int
}

// getMinMax finds min and max using a minimum number of comparisons.
func getMinMax(arr []int, n int) minMaxPair {
	var minmax minMaxPair
	var i int
	if n%2 == 0 {
		if arr[0] > arr[1] {
			minmax.max = arr[0]
			minmax.min = arr[1]
		} else {
			minmax.min = arr[0]
			minmax.max = arr[1]
		}
		i = 2
	} else {
		minmax.min = arr[0]
		minmax.max = arr[0]
		i = 1
	}
	for i < n-1 {
		if arr[i] > arr[i+1] {
			if arr[i] > minmax.max {
				minmax.max = arr[i]
			}
			if arr[i+1] < minmax.min {
				minmax.min = arr[i+1]
			}
		} else {
			if arr[i+1] > minmax.max {
				minmax.max = arr[i+1]
			}
			if arr[i] < minmax.min {
				minmax.min = arr[i]
			}
		}
		i += 2
	}
	return minmax
}

// makeBricks reports whether a goal-inch row can be made from small/big bricks.
func makeBricks(small, big, goal int) bool {
	if goal > big*5+small {
		return false
	}
	if goal%5 > small {
		return false
	}
	return true
}

// longestIsland returns the longest island achievable by filling water (W).
func longestIsland(arr []byte) int {
	max := 0
	start := 0
	curr := 0
	for i := 0; i < len(arr); i++ {
		if arr[i] == 'L' {
			max = maxInt(max, i-start+1)
			if i == 0 || arr[i-1] == 'W' {
				curr = i
			}
		} else {
			start = curr
		}
	}
	max = maxInt(max, len(arr)-start)
	return max
}

// singleNonDuplicate finds the single element in a sorted array (binary search).
func singleNonDuplicate(nums []int) int {
	n := len(nums)
	lo := 0
	hi := n / 2
	for lo < hi {
		m := (lo + hi) / 2
		if nums[2*m] != nums[2*m+1] {
			hi = m
		} else {
			lo = m + 1
		}
	}
	return nums[2*lo]
}

func singleNonDuplicate1(nums []int) int {
	low := 0
	high := len(nums) - 1
	for low < high {
		mid := low + (high-low)/2
		if nums[mid] != nums[mid+1] && nums[mid] != nums[mid-1] {
			return nums[mid]
		} else if nums[mid] == nums[mid+1] && mid%2 == 0 {
			low = mid + 1
		} else if nums[mid] == nums[mid-1] && mid%2 == 1 {
			low = mid + 1
		} else {
			high = mid - 1
		}
	}
	return nums[low]
}

// finMinTicketsCost returns the min cost of tickets for given travel days.
func finMinTicketsCost(a []int) int {
	dayTrip := make([]bool, 31)
	for _, day := range a {
		dayTrip[day] = true
	}
	minCostDP := make([]int, 31)
	minCostDP[0] = 0
	for d := 1; d <= 30; d++ {
		if !dayTrip[d] {
			minCostDP[d] = minCostDP[d-1]
			continue
		}
		var minCost int
		// Possibility #1: one-day pass on day d
		minCost = minCostDP[d-1] + 2
		// Possibility #2: seven-day pass ending on or after day d
		for prevD := maxInt(0, d-7); prevD <= d-4; prevD++ {
			minCost = minInt(minCost, minCostDP[prevD]+7)
		}
		// Possibility #3: 30-day pass for the whole period
		minCost = minInt(minCost, 25)
		minCostDP[d] = minCost
	}
	return minCostDP[30]
}

// findPos finds an element in a sorted array of infinite size.
func findPos(arr []int, key int) int {
	l, h := 0, 1
	val := arr[0]
	for val < key {
		l = h
		h = 2 * h
		val = arr[h]
	}
	return searchBinary(arr, l, h, key)
}

// searchBinary is a standard binary search (replaces the external Search class).
func searchBinary(arr []int, l, h, key int) int {
	for l <= h {
		mid := l + (h-l)/2
		if arr[mid] == key {
			return mid
		} else if arr[mid] < key {
			l = mid + 1
		} else {
			h = mid - 1
		}
	}
	return -1
}

// totalScore computes a running game score using a stack of tokens.
func totalScore(a []string) int {
	stack := []int{}
	total := 0
	for i := 0; i < len(a); i++ {
		if a[i] == "X" {
			total += 2 * stack[len(stack)-1]
			stack = append(stack, 2*stack[len(stack)-1])
		} else if a[i] == "Z" {
			total -= stack[len(stack)-1]
			stack = stack[:len(stack)-1]
		} else if a[i] == "+" {
			temp := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			t2 := stack[len(stack)-1] + temp
			total += t2
			stack = append(stack, temp)
			stack = append(stack, t2)
		} else {
			v, _ := strconv.Atoi(a[i])
			total += v
			stack = append(stack, v)
		}
	}
	return total
}

// longestZigZagSubArray returns the longest continuous zig-zag subarray length.
func longestZigZagSubArray(a []int) int {
	b := make([]int, len(a)-1)
	for i := 0; i < len(a)-1; i++ {
		if a[i] > a[i+1] {
			b[i] = 0
		} else {
			b[i] = 1
		}
	}
	count := 1
	for i := 0; i < len(b)-1; i++ {
		if b[i] != b[i+1] {
			count++
		}
	}
	return count + 1
}

// SumkLargest prints and returns the sum of the k largest elements.
func SumkLargest(a []int, k int) int {
	sum := 0
	quick(a, 0, len(a)-1, k)
	for i := 0; i < k; i++ {
		sum += a[i]
	}
	fmt.Print(sum)
	return sum
}

func quick(a []int, start, end, k int) {
	if start <= end {
		pivot := part(a, start, end)
		if pivot < k {
			quick(a, pivot+1, end, k)
		} else {
			quick(a, start, pivot-1, k)
		}
	}
}

func part(a []int, start, end int) int {
	pivot := a[end]
	index := start
	for i := start; i < end; i++ {
		if a[i] > pivot {
			swap(a, index, i)
			index++
		}
	}
	swap(a, index, end)
	return index
}

// computeTotalTaskTime computes the total execution time with cool down k.
func computeTotalTaskTime(tasks []byte, k int) int {
	m := map[byte]int{}
	total := 0
	for _, task := range tasks {
		if v, ok := m[task]; ok {
			exceptedTime := v + k + 1
			if exceptedTime > total {
				total = exceptedTime
			} else {
				total++
			}
		} else {
			total++
		}
		m[task] = total
	}
	return total
}

// leastInterval returns the least interval to finish tasks with cool down n.
func leastInterval(tasks []byte, n int) int {
	m := make([]int, 26)
	for _, c := range tasks {
		m[c-'A']++
	}
	sort.Ints(m)
	maxVal := m[25] - 1
	idleSlots := maxVal * n
	for i := 24; i >= 0 && m[i] > 0; i-- {
		idleSlots -= minInt(m[i], maxVal)
	}
	if idleSlots > 0 {
		return idleSlots + len(tasks)
	}
	return len(tasks)
}

// Task pairs a task id with its remaining frequency.
type Task struct {
	id        byte
	frequency int
}

// findBestTaskArrangement rearranges tasks to minimize execution time.
func findBestTaskArrangement(tasks []byte, k int) []byte {
	n := len(tasks)
	queue := newBinHeap[Task](func(a, b Task) bool { return a.frequency > b.frequency })
	m := map[byte]int{}
	for _, task := range tasks {
		m[task] = m[task] + 1
	}
	for id, freq := range m {
		queue.push(Task{id: id, frequency: freq})
	}
	tasks = make([]byte, n)
	i := 0
	for !queue.isEmpty() {
		c := 0
		nextRoundTask := []Task{}
		for c < k && !queue.isEmpty() {
			c++
			task := queue.pop()
			task.frequency--
			tasks[i] = task.id
			i++
			if task.frequency > 0 {
				nextRoundTask = append(nextRoundTask, task)
			}
		}
		for _, task := range nextRoundTask {
			queue.push(task)
		}
	}
	return tasks
}

// decodeWay returns the number of ways to decode a digit string (a=1..z=26).
func decodeWay(s string) int {
	length := len(s)
	if length == 0 {
		panic("s can't be empty")
	}
	pre := 1
	cur := 1
	if s[0] == '0' {
		cur = 0
	}
	var tmp int
	for i := 1; i < length && cur != 0; i++ {
		tmp = cur
		if s[i-1] == '1' || (s[i-1] == '2' && s[i] <= '6') {
			if s[i] == '0' {
				cur = pre
			} else {
				cur += pre
			}
		} else if s[i] == '0' {
			cur = 0
		}
		pre = tmp
	}
	return cur
}

// printEmpty is the empty placeholder from the original code.
func printEmpty() {
}

// isValidLotteryNUmber reports whether the input forms a valid lottery number
// (7 unique digits between 1 and 59).
func isValidLotteryNUmber(input string) bool {
	set := map[int]bool{}
	if len(input) == 0 || len(input) < 7 || len(input) > 14 {
		return false
	}
	prev, curr, prevPrev := 1, 1, 1
	for i := 1; i < len(input); i++ {
		if !set[int(input[i])] {
			if int(input[i-1]) < 5+48 || (int(input[i-1]) == 5+48 && int(input[i]) <= 9+48) {
				curr = prev + prevPrev
			} else {
				curr = prev
			}
			prevPrev = prev
			prev = curr
		}
		set[int(input[i])] = true
	}
	return curr == 7
}

// sortSquares sorts the array after converting each element to its square.
func sortSquares(arr []int) {
	n := len(arr)
	var k int
	for k = 0; k < n; k++ {
		if arr[k] >= 0 {
			break
		}
	}
	i := k - 1
	j := k
	ind := 0
	temp := make([]int, n)
	for i >= 0 && j < n {
		if arr[i]*arr[i] < arr[j]*arr[j] {
			temp[ind] = arr[i] * arr[i]
			ind++
			i--
		} else {
			temp[ind] = arr[j] * arr[j]
			ind++
			j++
		}
	}
	for i >= 0 {
		temp[ind] = arr[i] * arr[i]
		ind++
		i--
	}
	for j < n {
		temp[ind] = arr[j] * arr[j]
		ind++
		j++
	}
	for x := 0; x < n; x++ {
		arr[x] = temp[x]
	}
}

// canCompleteCircuit returns the starting gas station index, or -1.
func canCompleteCircuit(gas, cost []int) int {
	sumGas, sumCost, start, tank := 0, 0, 0, 0
	for i := 0; i < len(gas); i++ {
		sumGas += gas[i]
		sumCost += cost[i]
		tank += gas[i] - cost[i]
		if tank < 0 {
			start = i + 1
			tank = 0
		}
	}
	if sumGas < sumCost {
		return -1
	}
	return start
}

// firstMissingPositive returns the smallest missing positive number.
func firstMissingPositive(nums []int) int {
	n := len(nums)
	for i := 0; i < n; i++ {
		for nums[i] > 0 && nums[i] < n && nums[i] != nums[nums[i]] {
			swap(nums, i, nums[i])
		}
	}
	for i := 0; i < n; i++ {
		if nums[i] != i {
			return i
		}
	}
	return n + 1
}

// combinationSum3 finds combinations of k numbers (1..9) that sum to n.
func combinationSum3(k, n int) [][]int {
	ans := [][]int{}
	ans = combination(ans, []int{}, k, 1, n)
	return ans
}

func combination(ans [][]int, comb []int, k, start, n int) [][]int {
	if len(comb) == k && n == 0 {
		li := make([]int, len(comb))
		copy(li, comb)
		ans = append(ans, li)
		return ans
	}
	for i := start; i <= 9; i++ {
		comb = append(comb, i)
		ans = combination(ans, comb, k, i+1, n-i)
		comb = comb[:len(comb)-1]
	}
	return ans
}

// combinationMultiply finds multiplicative factor combinations of n.
func combinationMultiply(n int) [][]int {
	ans := [][]int{}
	ans = combinationMultiplyUtil(ans, []int{}, n, 1, n)
	return ans
}

func combinationMultiplyUtil(ans [][]int, comb []int, target, start, n int) [][]int {
	if target%n == 0 && start != 1 {
		comb = append(comb, n)
		li := make([]int, len(comb))
		copy(li, comb)
		ans = append(ans, li)
		return ans
	}
	for i := start; i <= target; i++ {
		if target%i == 0 {
			comb = append(comb, i)
			ans = combinationMultiplyUtil(ans, comb, target, i+1, n/i)
			comb = comb[:0]
		}
	}
	return ans
}

// firstBadVersion finds the first bad version using binary search.
func firstBadVersion(n int) int {
	left := 1
	right := n
	for left < right {
		mid := left + (right-left)/2
		if isBadVersion(mid) {
			right = mid
		} else {
			left = mid + 1
		}
	}
	return left
}

func isBadVersion(n int) bool {
	return true
}

// sortTransformedArray applies f(x)=ax^2+bx+c to a sorted array, sorted. O(n)
func sortTransformedArray(nums []int, a, b, c int) []int {
	n := len(nums)
	sorted := make([]int, n)
	i, j := 0, n-1
	index := 0
	if a >= 0 {
		index = n - 1
	} else {
		index = 0
	}
	for i <= j {
		if a >= 0 {
			if quad(nums[i], a, b, c) >= quad(nums[j], a, b, c) {
				sorted[index] = quad(nums[i], a, b, c)
				i++
			} else {
				sorted[index] = quad(nums[j], a, b, c)
				j--
			}
			index--
		} else {
			if quad(nums[i], a, b, c) >= quad(nums[j], a, b, c) {
				sorted[index] = quad(nums[j], a, b, c)
				j--
			} else {
				sorted[index] = quad(nums[i], a, b, c)
				i++
			}
			index++
		}
	}
	return sorted
}

func quad(x, a, b, c int) int {
	return a*x*x + b*x + c
}

// checkPossibility reports if the array can be made non-decreasing by changing
// at most one element.
func checkPossibility(nums []int) bool {
	index := -1
	for i := 1; i < len(nums); i++ {
		if nums[i-1] > nums[i] {
			if index != -1 {
				return false
			}
			index = i
		}
	}
	return index == -1 ||
		index == 1 || index == len(nums)-1 ||
		nums[index-2] <= nums[index] || nums[index-1] <= nums[index+1]
}

func checkPossibility1(nums []int) bool {
	cnt := 0
	n := len(nums)
	for i := 0; i < n-1; i++ {
		if nums[i] > nums[i+1] {
			cnt++
			if i >= 1 && nums[i+1] < nums[i-1] {
				nums[i+1] = nums[i]
			}
		}
		if cnt > 1 {
			return false
		}
	}
	return true
}

// canReachMN reports whether (1,1) can reach (m,n) via (x,y)->(x+y,y)|(x,x+y).
func canReachMN(m, n int) bool {
	prev := []int{m, n}
	for prev[0] >= 1 && prev[1] >= 1 {
		getPreviousPos(prev)
		if prev[0] == 1 && prev[1] == 1 {
			return true
		}
	}
	return false
}

func getPreviousPos(cur []int) {
	if cur[0] < cur[1] {
		cur[1] -= cur[0]
	} else {
		cur[0] -= cur[1]
	}
}

// countSetBits counts set bits using Brian Kernighan's algorithm.
func countSetBits(x int) int {
	count := 0
	for x > 0 {
		x = x & (x - 1)
		count++
	}
	return count
}

func countSetBit(number int) int {
	counter := 0
	for number > 0 {
		if number%2 == 1 {
			counter++
		}
		number = number / 2
	}
	return counter
}

// KSortedList tracks a position within one of the k sorted lists.
type KSortedList struct {
	position int
	value    int
	kIndex   int
}

// smallestRange finds the smallest range covering at least one number from each
// of the k sorted lists. Time = O(K) + O(n*logK)
func smallestRange(input [][]int) []int {
	minHeap := newBinHeap[KSortedList](func(a, b KSortedList) bool { return a.value < b.value })
	max := math.MinInt32
	rng := math.MaxInt32
	start, end := -1, -1
	for i := 0; i < len(input); i++ {
		list := KSortedList{position: 0, value: input[i][0], kIndex: i}
		minHeap.push(list)
		max = maxInt(max, input[i][0])
	}
	for minHeap.len() == len(input) {
		item := minHeap.pop()
		if max-item.value < rng {
			rng = max - item.value
			start = item.value
			end = max
		}
		if item.position < len(input[item.kIndex]) {
			item.value = input[item.kIndex][item.position]
			item.position += 1
			minHeap.push(item)
			if item.value > max {
				max = item.value
			}
		}
	}
	return []int{start, end}
}

// trapWater computes the trapped rain water using two pointers.
func trapWater(input []int) int {
	left, right := 0, len(input)-1
	ans := 0
	leftMax, rightMax := 0, 0
	for left < right {
		if input[left] < input[right] {
			if input[left] >= leftMax {
				leftMax = input[left]
			} else {
				ans += leftMax - input[left]
			}
			left++
		} else {
			if input[right] >= rightMax {
				rightMax = input[right]
			} else {
				ans += rightMax - input[right]
			}
			right--
		}
	}
	return ans
}
