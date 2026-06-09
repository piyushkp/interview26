package main

import (
	"fmt"
	"strconv"
	"strings"
)

// removeDuplicate removes duplicate characters keeping first occurrences.
func (si *StringImp) removeDuplicate(s string) string {
	set := map[byte]bool{}
	var result strings.Builder
	ch := []byte(s)
	for i := 0; i < len(ch); i++ {
		if !set[ch[i]] {
			set[ch[i]] = true
			result.WriteByte(ch[i])
		}
	}
	return result.String()
}

// RemoveDuplicates removes duplicates in O(n) and no extra space (bitmask), then
// prints the result. Works for lowercase a-z.
func RemoveDuplicates(str []byte) {
	check := 0
	for i := 0; i < len(str); i++ {
		val := int(str[i] - 'a')
		if check&(1<<val) > 0 {
			str[i] = 0
			continue
		}
		check = check | (1 << val)
	}
	for j := 0; j < len(str); j++ {
		if str[j] == 0 {
			continue
		}
		fmt.Print(string(str[j]))
	}
}

// permute prints all permutations of the string.
func permute(str string) {
	length := len(str)
	in := []byte(str)
	doPermute(in, length, 0)
}

func doPermute(in []byte, length, level int) {
	if level == length {
		fmt.Println(string(in))
		return
	}
	for i := level; i < length; i++ {
		swapChars(in, i, level)
		doPermute(in, length, level+1)
		swapChars(in, i, level)
	}
}

// getDerangement finds all derangements of in (no element in its original spot).
func getDerangement(in []byte) [][]byte {
	m := map[int]byte{}
	result := [][]byte{}
	ori := make([]byte, len(in))
	for i := 0; i < len(in); i++ {
		m[i] = in[i]
		ori[i] = in[i]
	}
	return getDerangementUtil(in, ori, m, 0, result)
}

func getDerangementUtil(in, ori []byte, m map[int]byte, level int, result [][]byte) [][]byte {
	if level == len(in) {
		cp := make([]byte, len(in))
		copy(cp, in)
		result = append(result, cp)
		fmt.Println(string(in))
		return result
	}
	for i := level; i < len(in); i++ {
		if m[i] != in[level] {
			if i != level && (in[i] == ori[level] || in[level] == ori[i]) {
				continue // for duplicates
			}
			swapChars(in, i, level)
			result = getDerangementUtil(in, ori, m, level+1, result)
			swapChars(in, i, level)
		}
	}
	return result
}

func swapChars(chars []byte, i, j int) {
	chars[i], chars[j] = chars[j], chars[i]
}

func swapStrings(arr []string, i, j int) {
	arr[i], arr[j] = arr[j], arr[i]
}

// printCombinations prints all combinations of r elements from arr.
func printCombinations(arr []int, start, end, r int, sb *[]byte) {
	if r == 0 {
		fmt.Println(string(*sb))
		return
	}
	for i := start; i <= end-r+1; i++ {
		*sb = append(*sb, []byte(strconv.Itoa(arr[i])+" ")...)
		printCombinations(arr, i+1, end, r-1, sb)
		*sb = (*sb)[:len(*sb)-2]
	}
}

// combine prints every combination of the characters of str.
func combine(str string) {
	length := len(str)
	instr := []byte(str)
	outstr := []byte{}
	doCombine(instr, &outstr, length, 0, 0)
}

func doCombine(instr []byte, outstr *[]byte, length, level, start int) {
	for i := start; i < length; i++ {
		*outstr = append(*outstr, instr[i])
		fmt.Println(string(*outstr))
		if i < length-1 {
			doCombine(instr, outstr, length, level+1, i+1)
		}
		*outstr = (*outstr)[:len(*outstr)-1]
	}
}

// kLengthCount mirrors the Java static counter used by printAllKLengthRec.
var kLengthCount = 0

// printAllKLength prints all strings of length k from set with the b/cc constraints.
func printAllKLength(set []byte, k int) {
	n := len(set)
	fmt.Print(printAllKLengthRec(set, "", n, k))
}

func printAllKLengthRec(set []byte, prefix string, n, k int) int {
	if k == 0 {
		kLengthCount++
		fmt.Println(prefix)
		return kLengthCount
	}
	for i := 0; i < n; i++ {
		lastTwo := prefix[maxInt(len(prefix)-2, 0):]
		if !(strings.Contains(prefix, "b") && set[i] == 'b') &&
			!(lastTwo == "cc" && set[i] == 'c') {
			newPrefix := prefix + string(set[i])
			printAllKLengthRec(set, newPrefix, n, k-1)
		}
	}
	return kLengthCount
}

// findRank returns the lexicographic rank of str among its permutations.
func findRank(str []byte) int {
	length := len(str)
	mul := factorial(length)
	rank := 1
	count := make([]int, 256)
	populateAndIncreaseCount(count, str)
	for i := 0; i < length; i++ {
		mul /= int64(length - i)
		rank += int(int64(count[str[i]-1]) * mul)
		updatecount(count, str[i])
	}
	return rank
}

func factorial(n int) int64 {
	if n <= 1 {
		return 1
	}
	return int64(n) * factorial(n-1)
}

func findSmallerInRight(A string, low, high int) int {
	countRight := 0
	for i := low + 1; i <= high; i++ {
		if A[i] < A[low] {
			countRight++
		}
	}
	return countRight
}

func populateAndIncreaseCount(count []int, str []byte) {
	i := 0
	for i = 0; i < len(str) && str[i] >= 'a' && str[i] <= 'z'; i++ {
		count[str[i]]++
	}
	for i = 1; i < 256; i++ {
		count[i] += count[i-1]
	}
}

func updatecount(count []int, ch byte) {
	for i := int(ch); i < 256; i++ {
		count[i]--
	}
}

// removeDuplicates removes consecutive duplicate characters in place and returns
// the new length. e.g. AABBCDDAAB -> ABCDAB.
func (si *StringImp) removeDuplicates(input []byte) int {
	slow := 0
	fast := 0
	index := 0
	for fast < len(input) {
		for fast < len(input) && input[slow] == input[fast] {
			fast++
		}
		input[index] = input[slow]
		index++
		slow = fast
	}
	return index
}
