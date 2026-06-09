package main

import (
	"regexp"
	"sort"
	"strconv"
)

// String / digit oriented number algorithms.

// Returns true if the input string is a number and false otherwise.
func isNumber(toTest string) bool {
	// Java's String.matches requires a full match, so anchor the pattern.
	re := regexp.MustCompile(`^-?\d+(\.\d+)?$`)
	return re.MatchString(toTest)
}

// Returns the negabinary (negative 2-base) representation of x as a string.
func negaBinary(x int) string {
	digits := []byte{}
	for x != 0 {
		rem := x % -2
		x = x / -2
		if rem < 0 {
			rem += 2
			x += 1
		}
		digits = append(digits, byte('0'+rem))
	}
	// reverse
	for i, j := 0, len(digits)-1; i < j; i, j = i+1, j-1 {
		digits[i], digits[j] = digits[j], digits[i]
	}
	return string(digits)
}

// Arrange Given Numbers To Form The Biggest Number Possible.
func biggestNumber(number int) int {
	digits := numbertoDigits(number)
	sort.Ints(digits)
	return digitToNumber(digits)
}

func digitToNumber(digits []int) int {
	number := 0
	base := 1
	for i := len(digits) - 1; i >= 0; i-- {
		number += digits[i] * base
		base *= 10
	}
	return number
}

func numbertoDigits(number int) []int {
	digits := []int{}
	for number > 0 {
		digits = append([]int{number % 10}, digits...) // add at front
		number /= 10
	}
	return digits
}

// Next greater number with the same set of digits.
func nextGreaterNumber(number int) int {
	digits := numbertoDigits(number)
	for i := len(digits) - 2; i >= 0; i-- {
		if digits[i] < digits[i+1] {
			for j := len(digits) - 1; j > i; j-- {
				if digits[j] > digits[i] {
					digits[j], digits[i] = digits[i], digits[j]
					sort.Ints(digits[i+1:])
					return digitToNumber(digits)
				}
			}
		}
	}
	return -1
}

// Count and say: nth number in a "Look and Say" sequence starting with num.
func lookandsayUtil(num string, n int) string {
	for i := 0; i < n; i++ {
		num = lookandsay(num)
	}
	return num
}

func lookandsay(number string) string {
	result := []byte{}
	say := number[0]
	times := 1
	for i := 1; i < len(number); i++ {
		actual := number[i]
		if actual != say {
			result = append(result, []byte(strconv.Itoa(times))...)
			result = append(result, say)
			times = 1
			say = actual
		} else {
			times++
		}
	}
	result = append(result, []byte(strconv.Itoa(times))...)
	result = append(result, say)
	return string(result)
}

// String to integer (atoi).
func atoi(str string) int {
	index, sign, total := 0, 1, 0
	// 1. Empty string
	if len(str) == 0 {
		return 0
	}
	// 2. Remove Spaces
	for index < len(str) && str[index] == ' ' {
		index++
	}
	// 3. Handle signs
	if index < len(str) && (str[index] == '+' || str[index] == '-') {
		if str[index] == '+' {
			sign = 1
		} else {
			sign = -1
		}
		index++
	}
	// 4. Convert number and avoid overflow
	for index < len(str) {
		digit := int(str[index]) - '0'
		if digit < 0 || digit > 9 {
			break
		}
		// check if total will overflow after 10 times and add digit
		if maxInt32/10 < total || (maxInt32/10 == total && maxInt32%10 < digit) {
			if sign == 1 {
				return maxInt32
			}
			return minInt32
		}
		total = 10*total + digit
		index++
	}
	return total * sign
}
