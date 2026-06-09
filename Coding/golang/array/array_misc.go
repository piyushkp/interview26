package main

import (
	"fmt"
	"math"
	"math/rand"
	"sort"
	"strconv"
	"strings"
)

// maxProfit returns the max profit with at most one transaction.
func maxProfit(prices []int) int {
	if prices == nil || len(prices) < 2 {
		return 0
	}
	maxDiff := 0
	minElement := prices[0]
	for i := 1; i < len(prices); i++ {
		if prices[i]-minElement > maxDiff {
			maxDiff = prices[i] - minElement
		}
		if prices[i] < minElement {
			minElement = prices[i]
		}
	}
	return maxDiff
}

// maxProfitMultiTrans allows multiple transactions (sell before buying again).
func maxProfitMultiTrans(arr []int) int {
	if len(arr) == 0 {
		return 0
	}
	profit := 0
	localMin := arr[0]
	for i := 1; i < len(arr); i++ {
		if arr[i-1] >= arr[i] {
			localMin = arr[i]
		} else {
			profit += arr[i] - localMin
			localMin = arr[i]
		}
	}
	return profit
}

func maxProfit2(prices []int) int {
	profit := 0
	for i := 1; i < len(prices); i++ {
		diff := prices[i] - prices[i-1]
		if diff > 0 {
			profit += diff
		}
	}
	return profit
}

// maxProfit3 allows at most two transactions.
func maxProfit3(prices []int) int {
	maxProfit1 := 0
	maxProfit2v := 0
	lowestBuyPrice1 := math.MaxInt32
	lowestBuyPrice2 := math.MaxInt32
	for _, p := range prices {
		maxProfit2v = maxInt(maxProfit2v, p-lowestBuyPrice2)
		lowestBuyPrice2 = minInt(lowestBuyPrice2, p-maxProfit1)
		maxProfit1 = maxInt(maxProfit1, p-lowestBuyPrice1)
		lowestBuyPrice1 = minInt(lowestBuyPrice1, p)
	}
	return maxProfit2v
}

// maxProfitAtMostKTrans maximizes profit with at most k transactions.
func maxProfitAtMostKTrans(prices []int, k int) int {
	n := len(prices)
	profit := make([][]int, k+1)
	for i := range profit {
		profit[i] = make([]int, n+1)
	}
	for i := 0; i <= k; i++ {
		profit[i][0] = 0
	}
	for j := 0; j <= n; j++ {
		profit[0][j] = 0
	}
	for i := 1; i <= k; i++ {
		prevDiff := math.MinInt32
		for j := 1; j < n; j++ {
			prevDiff = maxInt(prevDiff, profit[i-1][j-1]-prices[j-1])
			profit[i][j] = maxInt(profit[i][j-1], prices[j]+prevDiff)
		}
	}
	return profit[k][n-1]
}

// stockWithFees maximizes profit with a per-transaction commission fee.
func stockWithFees(prices []int, fee int) int {
	afterBuy := -prices[0]
	afterSell := 0
	for i := 1; i < len(prices); i++ {
		oldBuy := afterBuy
		oldSell := afterSell
		afterBuy = maxInt(oldBuy, oldSell-prices[i])
		afterSell = maxInt(oldSell, oldBuy+prices[i]-fee)
	}
	return afterSell
}

// Ad represents an advertisement with a start, finish and revenue.
type Ad struct {
	start   int
	finish  int
	revenue int
}

// scheduleAds solves the weighted job scheduling problem to maximize revenue.
func scheduleAds(ads []Ad) int {
	sort.Slice(ads, func(i, j int) bool { return ads[i].finish < ads[j].finish })
	n := len(ads)
	table := make([]int, n)
	table[0] = ads[0].revenue
	for i := 1; i < n; i++ {
		inclProf := ads[i].revenue
		l := binarySearch(ads, i)
		if l != -1 {
			inclProf += table[l]
		}
		table[i] = maxInt(inclProf, table[i-1])
	}
	return table[n-1]
}

// binarySearch finds the latest ad (before index) that doesn't conflict.
func binarySearch(ads []Ad, index int) int {
	lo, hi := 0, index-1
	for lo <= hi {
		mid := (lo + hi) / 2
		if ads[mid].finish <= ads[index].start {
			if ads[mid+1].finish <= ads[index].start {
				lo = mid + 1
			} else {
				return mid
			}
		} else {
			hi = mid - 1
		}
	}
	return -1
}

// rob solves the house-robbing problem. Time = O(N), space = O(1).
func rob(num []int) int {
	if num == nil || len(num) == 0 {
		return 0
	}
	even := 0
	odd := 0
	for i := 0; i < len(num); i++ {
		if i%2 == 0 {
			even += num[i]
			if even <= odd {
				even = odd
			}
		} else {
			odd += num[i]
			if odd <= even {
				odd = even
			}
		}
	}
	if even > odd {
		return even
	}
	return odd
}

// findMaxDays uses DP to maximize selected nights with a gap of one. O(N)
func findMaxDays(arr []int) int {
	maxDaysToPos := make([]int, len(arr)+1)
	maxDaysToPos[0] = 0
	maxDaysToPos[1] = arr[0]
	for i := 2; i < len(maxDaysToPos); i++ {
		maxDaysToPos[i] = maxInt(maxDaysToPos[i-1], maxDaysToPos[i-2]+arr[i-1])
	}
	return maxDaysToPos[len(maxDaysToPos)-1]
}

// getMagicIndexDup finds a magic index (A[i]==i) in a sorted array with dups.
func getMagicIndexDup(a []int, start, end int) int {
	if start > end {
		return -1
	}
	mid := start + (end-start)/2
	if a[mid] == mid {
		return mid
	}
	result := getMagicIndexDup(a, start, minInt(mid-1, a[mid]))
	if result == -1 {
		result = getMagicIndexDup(a, maxInt(mid+1, a[mid]), end)
	}
	return result
}

// oddManOut returns the single element that appears once. O(n) time, O(1) space.
func oddManOut(array []int) int {
	val := 0
	for i := 0; i < len(array); i++ {
		val ^= array[i]
	}
	return val
}

// maxproductofThree returns the max product of any three numbers.
func maxproductofThree(a []int) int {
	largest := a[0]
	secondLargest := 0
	thirdLargest := 0
	min1 := 0
	min2 := 0
	for i := 0; i < len(a); i++ {
		number := a[i]
		if number > largest {
			thirdLargest = secondLargest
			secondLargest = largest
			largest = number
		} else if number > secondLargest {
			thirdLargest = secondLargest
			secondLargest = number
		} else if number > thirdLargest {
			thirdLargest = number
		}
		if number < min1 {
			min2 = min1
			min1 = number
		} else if number < min2 {
			min2 = number
		}
	}
	return largest * maxInt(thirdLargest*secondLargest, min1*min2)
}

// areConsecutive reports whether positive numbers form a consecutive set.
func areConsecutive(input []int) bool {
	min := math.MaxInt32
	for i := 0; i < len(input); i++ {
		if input[i] < min {
			min = input[i]
		}
	}
	for i := 0; i < len(input); i++ {
		if absInt(input[i])-min >= len(input) {
			return false
		}
		if input[absInt(input[i])-min] < 0 {
			return false
		}
		input[absInt(input[i])-min] = -input[absInt(input[i])-min]
	}
	for i := 0; i < len(input); i++ {
		input[i] = absInt(input[i])
	}
	return true
}

// getMissingNo returns the missing number from 1..n using XOR.
func getMissingNo(a []int, n int) int {
	x1 := a[0]
	for i := 1; i < n; i++ {
		x1 = x1 ^ a[i]
	}
	for i := 1; i <= n; i++ {
		x1 = x1 ^ i
	}
	return x1
}

// findNumbers prints the two missing numbers from 1..N.
func findNumbers(a []int, N int) {
	x := 0
	for i := 0; i < len(a); i++ {
		x = x ^ a[i]
	}
	for i := 1; i <= N; i++ {
		x = x ^ i
	}
	x = x & (^(x - 1))
	p, q := 0, 0
	for i := 0; i < len(a); i++ {
		if a[i]&x == x {
			p = p ^ a[i]
		} else {
			q = q ^ a[i]
		}
	}
	for i := 1; i <= N; i++ {
		if i&x == x {
			p = p ^ i
		} else {
			q = q ^ i
		}
	}
	fmt.Println("N1:", p, "N2:", q)
}

// getAvg returns the new average after including x.
func getAvg(prevAvg float32, x, n int) float32 {
	return (prevAvg*float32(n) + float32(x)) / float32(n+1)
}

// streamAvg prints the running average of a stream of numbers.
func streamAvg(arr []int, n int) {
	var avg float32 = 0
	for i := 0; i < n; i++ {
		avg = getAvg(avg, arr[i], i)
		fmt.Println("Average of", i+1, "numbers is", avg)
	}
}

// largestNumber arranges numbers to form the largest value.
func largestNumber(num []int) string {
	if num == nil || len(num) == 0 {
		return ""
	}
	array := make([]string, len(num))
	for i := 0; i < len(num); i++ {
		array[i] = strconv.Itoa(num[i])
	}
	sort.Slice(array, func(i, j int) bool {
		return array[i]+array[j] < array[j]+array[i]
	})
	result := ""
	for _, str := range array {
		result = str + result
	}
	return result
}

// randomize shuffles the array (Fisher-Yates). O(n) time.
func randomize(arr []int, n int) {
	for i := n - 1; i > 0; i-- {
		j := rand.Intn(i + 1)
		arr[i], arr[j] = arr[j], arr[i]
	}
}

// serialize encodes an array of strings into one bit string.
func serialize(arr []string) string {
	var sb strings.Builder
	for i := 0; i < len(arr); i++ {
		lenStr := strconv.Itoa(len(arr[i]))
		bData := []byte(arr[i])
		sb.WriteString(fmt.Sprintf("%08b", lenStr[0]))
		for _, item := range bData {
			sb.WriteString(fmt.Sprintf("%08b", item))
		}
	}
	return sb.String()
}

// deSerialize decodes a bit string back into the original array of strings.
func deSerialize(arr string) []string {
	output := []string{}
	bytes := GetBytes(arr)
	s := string(bytes)
	for i := 0; i < len(bytes); {
		length, _ := strconv.Atoi(s[i : i+1])
		i++
		data := s[i : i+length]
		i += length
		output = append(output, data)
	}
	return output
}

// GetBytes converts a bit string into a byte slice.
func GetBytes(bitString string) []byte {
	numBytes := len(bitString) / 8
	if len(bitString)%8 != 0 {
		numBytes++
	}
	bytes := make([]byte, numBytes)
	byteIndex, bitIndex := 0, 0
	for i := 0; i < len(bitString); i++ {
		if bitString[i] == '1' {
			bytes[byteIndex] |= byte(1 << (7 - bitIndex))
		}
		bitIndex++
		if bitIndex == 8 {
			bitIndex = 0
			byteIndex++
		}
	}
	return bytes
}

// areConsecutiveN reports whether arr (length n) holds consecutive numbers.
func areConsecutiveN(arr []int, n int) bool {
	if n < 1 {
		return false
	}
	min := getMin(arr, n)
	max := getMax(arr, n)
	if max-min+1 == n {
		visited := make([]bool, n)
		for i := 0; i < n; i++ {
			if visited[arr[i]-min] != false {
				return false
			}
			visited[arr[i]-min] = true
		}
		return true
	}
	return false
}

func getMin(arr []int, n int) int {
	min := arr[0]
	for i := 1; i < n; i++ {
		if arr[i] < min {
			min = arr[i]
		}
	}
	return min
}

func getMax(arr []int, n int) int {
	max := arr[0]
	for i := 1; i < n; i++ {
		if arr[i] > max {
			max = arr[i]
		}
	}
	return max
}

// SortNearlySorted sorts a list in which each number is at distance k from its
// actual position.
func SortNearlySorted(a []int, k int) []int {
	if k == 0 {
		return a
	}
	count := 0
	for i := 0; i < len(a); i++ {
		Swap(i, i+k, a)
		count++
		if count == k {
			i += k
			count = 0
		}
	}
	return a
}

// minimumCoinBottomUp returns the minimum number of coins to form total.
func minimumCoinBottomUp(total int, coins []int) int {
	dp := make([]int, total+1)
	path := make([]int, total+1)
	dp[0] = 0
	for i := 1; i <= total; i++ {
		dp[i] = total + 1
		path[i] = -1
	}
	for i := 1; i <= total; i++ {
		for j := 0; j < len(coins); j++ {
			if i >= coins[j] {
				dp[i] = minInt(dp[i], dp[i-coins[j]]+1)
			}
		}
	}
	printCoinCombination(path, coins)
	return dp[total]
}

func printCoinCombination(R, coins []int) {
	if R[len(R)-1] == -1 {
		fmt.Print("No solution is possible")
		return
	}
	start := len(R) - 1
	fmt.Print("Coins used to form total ")
	for start != 0 {
		j := R[start]
		fmt.Print(coins[j], " ")
		start = start - coins[j]
	}
	fmt.Print("\n")
}

// countWays counts the number of ways to form total using coins (infinite).
func countWays(total int, arr []int) int {
	dp := make([]int, total+1)
	dp[0] = 1
	for i := 0; i < len(arr); i++ {
		for j := arr[i]; j <= total; j++ {
			dp[j] += dp[j-arr[i]]
		}
	}
	return dp[total]
}

// fizzbuzz prints the classic FizzBuzz (multiples of 5 -> fizz, 7 -> buzz).
func fizzbuzz() {
	for i := 1; i <= 100; i++ {
		if i%5 == 0 && i%7 == 0 {
			fmt.Print("fizzbuzz")
		} else if i%5 == 0 {
			fmt.Print("fizz")
		} else if i%7 == 0 {
			fmt.Print("buzz")
		} else {
			fmt.Print(i)
		}
		fmt.Print(" ")
	}
	fmt.Println()
}

// maxDiff returns the max difference where the larger element appears later.
func maxDiff(arr []int, arrSize int) int {
	mDiff := arr[1] - arr[0]
	minElement := arr[0]
	for i := 1; i < arrSize; i++ {
		if arr[i]-minElement > mDiff {
			mDiff = arr[i] - minElement
		}
		if arr[i] < minElement {
			minElement = arr[i]
		}
	}
	return mDiff
}

// minimum_distance_sum returns the minimum index-distance sum of three values.
func minimum_distance_sum(words []int, a, b, c int) int {
	lastA := -1
	lastB := -1
	lastC := -1
	minDistance := math.MaxInt32
	for i := 0; i < len(words); i++ {
		if words[i] == a {
			lastA = i
		} else if words[i] == b {
			lastB = i
		} else if words[i] == c {
			lastC = i
		}
		if lastA >= 0 && lastB >= 0 && lastC >= 0 {
			minDistance = minInt(minDistance, absInt(lastA-lastC)+absInt(lastA-lastB)+absInt(lastB-lastC))
		}
	}
	return minDistance
}
