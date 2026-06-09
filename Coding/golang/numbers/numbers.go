package main

import (
	"fmt"
	"math"
)

// Ported from Coding/java/Numbers.java (package code.ds).
// Math / bit-manipulation algorithms.

const (
	minInt32 = -2147483648
	maxInt32 = 2147483647
)

// ---- small helpers (Go 1.19 has no built-in min/max for ints) ----

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

func absInt64(a int64) int64 {
	if a < 0 {
		return -a
	}
	return a
}

func main() {
	// Original Java declared an input array used only by commented-out demos.
	in := []int{0, 2, 8, 5, 2, 1, 4, 13, 23}
	_ = in
	// System.out.println(nextGreaterNumber(12543));
	fmt.Println(lookandsayUtil("1", 4))
}

// Write a function that takes a number n and returns an array containing a
// Fibonacci sequence of length n. Time = O(n), Space = O(n).
func fib(n int) []int {
	if n == 0 {
		return nil
	} else if n == 1 {
		f := make([]int, 1)
		f[0] = 0
		return f
	}
	f := make([]int, n)
	f[0] = 0
	f[1] = 1
	for i := 2; i < n; i++ {
		f[i] = f[i-1] + f[i-2]
	}
	return f
}

// Print nth Fibonacci number. Time = O(n), space = O(1).
func fib1(n int) int {
	a, b := 0, 1
	if n == 0 {
		return a
	}
	for i := 2; i <= n; i++ {
		c := a + b
		a = b
		b = c
	}
	return b
}

// Find the largest subsequence from array that contains Fibonacci numbers.
func getFibonnaciNumbers(given []int) []int {
	output := []int{}
	for _, x := range given {
		nearestFib := getNthFibonacciNumber(x)
		if x == nearestFib {
			output = append(output, x)
		}
	}
	return output
}

func getNthFibonacciNumber(given int) int {
	fN := 1
	fNPrev := 1
	for fN < given {
		temp := fN
		fN = fN + fNPrev
		fNPrev = temp
	}
	fmt.Println("Neartest to", given, "is", fN)
	return fN
}

// Factorial sequence of length n. Time = O(n), Space = O(n).
func factorial(n int) []int {
	if n == 0 {
		result := make([]int, 1)
		result[0] = 1
		return result
	}
	result := make([]int, n)
	result[0] = 1
	for i := 1; i < n; i++ {
		result[i] = i * result[i-1]
	}
	return result
}

// Print nth Factorial number. Time = O(n), space = O(1).
func factorial1(n int) int {
	b, c := 1, 1
	if n == 0 || n == 1 {
		return b
	}
	for i := 2; i <= n; i++ {
		b = i * c
		c = b
	}
	return b
}

// Calculate x raised to the power y in O(logn).
func powerInt(x, y int) int {
	if y == 0 {
		return 1
	}
	temp := powerInt(x, y/2)
	if y%2 == 0 {
		return temp * temp
	}
	return x * temp * temp
}

// Extended version of power that can work for float x and negative y.
func powerFloat(x float64, y int) float64 {
	if y == 0 {
		return 1
	}
	temp := powerFloat(x, y/2)
	if y%2 == 0 {
		return temp * temp
	}
	if y > 0 {
		return x * temp * temp
	}
	return (temp * temp) / x
}

// Calculate the angle between hour hand and minute hand.
func calcAngle(h, m int) int {
	if h < 0 || m < 0 || h > 12 || m > 60 {
		fmt.Print("Wrong input")
	}
	if h == 12 {
		h = 0
	}
	if m == 60 {
		m = 0
	}
	hourAngle := (h*60 + m) / 2
	minuteAngle := 6 * m
	// Find the difference between two angles.
	angle := absInt(hourAngle - minuteAngle)
	// Return the smaller angle of two possible angles.
	angle = minInt(360-angle, angle)
	return angle
}

// Squareroot of a Number - O(logN).
func sqrtInt(num int) int {
	if num < 0 {
		return 0
	}
	if num == 1 {
		return 1
	}
	low := 0
	high := 1 + (num / 2)
	for low+1 < high {
		mid := low + (high-low)/2
		square := mid * mid
		if square == num {
			return mid
		} else if square < num {
			low = mid
		} else {
			high = mid
		}
	}
	return low
}

// checks whether an int is prime or not.
func isPrime(n int) bool {
	// check if n is a multiple of 2
	if n%2 == 0 {
		return false
	}
	// if not, then just check the odds
	for i := 3; i*i <= n; i += 2 {
		if n%i == 0 {
			return false
		}
	}
	return true
}

// Returns the maximum value that can be put in a knapsack of capacity W.
func knapSack(W int, wt, val []int, n int) int {
	K := make([][]int, n+1)
	for i := range K {
		K[i] = make([]int, W+1)
	}
	// Build table K[][] in bottom up manner.
	for i := 0; i <= n; i++ {
		for j := 0; j <= W; j++ {
			if i == 0 || j == 0 {
				K[i][j] = 0
			} else if wt[i-1] <= j {
				K[i][j] = maxInt(val[i-1]+K[i-1][j-wt[i-1]], K[i-1][j])
			} else {
				K[i][j] = K[i-1][j]
			}
		}
	}
	return K[n][W]
}

// In "the 100 game" two players take turns adding 1..10 to a running total.
func canIWin(maxChoosableInteger, desiredTotal int) bool {
	numbers := make([]int, maxChoosableInteger)
	for i := 0; i < maxChoosableInteger; i++ {
		numbers[i] = i + 1
	}
	return canWin(numbers, desiredTotal, 0)
}

func canWin(numbers []int, desiredTotal, sum int) bool {
	for i := 0; i < len(numbers); i++ {
		temp := sum + numbers[i]
		if (desiredTotal-temp)%11 == 0 {
			sum = temp
		}
	}
	return sum >= 100
}

// Divide without Division.
func divide(dividend, divisor int) int {
	if divisor == 0 || (dividend == minInt32 && divisor == -1) {
		return maxInt32
	}
	res := 0
	sign := 1
	if (dividend < 0) != (divisor < 0) {
		sign = -1
	}
	dvd := absInt64(int64(dividend))
	dvs := absInt64(int64(divisor))
	for dvs <= dvd {
		temp := dvs
		mul := int64(1)
		for dvd >= temp<<1 {
			temp <<= 1
			mul <<= 1
		}
		dvd -= temp
		res += int(mul)
	}
	if sign == 1 {
		return res
	}
	return -res
}

func divide1(N, D int) {
	result := 0
	if D == 0 {
		fmt.Println("Cannot divide by 0")
	} else if N == 0 {
		fmt.Println(0)
	} else if N == D {
		fmt.Println(1)
	} else if N > 0 && D > 0 && N < D {
		fmt.Println(0)
	} else {
		// both negative
		if N < 0 && D < 0 {
			for N <= D {
				N += -1 * D
				result++
			}
			fmt.Println(result)
		} else if N < 0 || D < 0 { // either N or D negative
			if N < 0 {
				N = -1 * N
			} else {
				D = -1 * D
			}
			for N >= D {
				N -= D
				result--
			}
			fmt.Println(result)
		} else { // both positive
			for N >= D {
				N -= D
				result++
			}
			fmt.Println(result)
		}
	}
}

// find factors of number
func findFactors(num int) {
	for i := int64(1); i <= int64(math.Sqrt(float64(num))); i++ {
		if int64(num)%i == 0 {
			fmt.Println(i)
			if i != int64(num)/i {
				fmt.Println(int64(num) / i)
			}
		}
	}
}
