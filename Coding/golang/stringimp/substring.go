package main

import (
	"fmt"
	"sort"
	"strings"
)

// intMaxValue / intMinValue replace Java's Integer.MAX_VALUE / MIN_VALUE.
const intMaxValue = int(^uint(0) >> 1)
const intMinValue = -intMaxValue - 1

// minSubString returns the shortest window in s containing all chars in t.
func minSubString(s, t string) string {
	m := make([]int, 128)
	for i := 0; i < len(t); i++ {
		m[t[i]]++
	}
	start, end, minStart, minLen, counter := 0, 0, 0, intMaxValue, len(t)
	for end < len(s) {
		c1 := s[end]
		if m[c1] > 0 {
			counter--
		}
		m[c1]--
		end++
		for counter == 0 {
			if minLen > end-start {
				minLen = end - start
				minStart = start
			}
			c2 := s[start]
			m[c2]++
			if m[c2] > 0 {
				counter++
			}
			start++
		}
	}
	if minLen == intMaxValue {
		return ""
	}
	return s[minStart : minStart+minLen]
}

// lengthOfLongestSubstring returns the length of the longest substring without
// repeating characters.
func (si *StringImp) lengthOfLongestSubstring(s string) int {
	m := make([]int, 128)
	start, end, maxLen, counter := 0, 0, 0, 0
	for end < len(s) {
		c1 := s[end]
		if m[c1] > 0 {
			counter++
		}
		m[c1]++
		end++
		for counter > 0 {
			c2 := s[start]
			if m[c2] > 1 {
				counter--
			}
			m[c2]--
			start++
		}
		maxLen = maxInt(maxLen, end-start)
	}
	return maxLen
}

// lengthOfLongestSubstringKDistinct returns the length of the longest substring
// with at most k distinct characters.
func lengthOfLongestSubstringKDistinct(s string, k int) int {
	m := make([]int, 256)
	start, end, maxLen, counter := 0, 0, intMinValue, 0
	for end < len(s) {
		c1 := s[end]
		if m[c1] == 0 {
			counter++
		}
		m[c1]++
		end++
		for counter > k {
			c2 := s[start]
			if m[c2] == 1 {
				counter--
			}
			m[c2]--
			start++
		}
		maxLen = maxInt(maxLen, end-start)
	}
	return maxLen
}

// lrs prints all repeating substrings of the given length (sorted).
func lrs(s string, sequenceLength int) {
	N := len(s)
	suffixes := make([]string, N)
	for i := 0; i < N; i++ {
		suffixes[i] = s[i:N]
	}
	sort.Strings(suffixes)
	for i := 0; i < N-1; i++ {
		x := lrsUtil(suffixes[i], suffixes[i+1], sequenceLength)
		if len(x) == sequenceLength {
			fmt.Println(x)
		}
	}
}

func lrsUtil(s, t string, sequenceLength int) string {
	n := minInt(len(s), len(t))
	if n >= sequenceLength {
		if s[:sequenceLength] == t[:sequenceLength] {
			return s[:sequenceLength]
		}
	}
	return ""
}

// count_runs counts the number of individual occurrences of repeated letters.
func count_runs(target string) int {
	prev := target[0]
	rpt := 0
	for i := 1; i < len(target); i++ {
		curr := target[i]
		if curr == prev {
			rpt++
			for i < len(target)-1 && (target[i+1] == curr || target[i+1] == ' ' || target[i+1] == '.') {
				i++
			}
		} else {
			prev = curr
		}
	}
	return rpt
}

// strStr returns the first index of target in source, or -1.
func strStr(source, target string) int {
	var i, j int
	for i = 0; i < len(source)-len(target)+1; i++ {
		for j = 0; j < len(target); j++ {
			if source[i+j] != target[j] {
				break
			}
		}
		if j == len(target) {
			return i
		}
	}
	return -1
}

// findSubOccur counts occurrences of findStr in str.
func findSubOccur(str, findStr string) int {
	lastIndex := 0
	count := 0
	for lastIndex != -1 {
		idx := strings.Index(str[lastIndex:], findStr)
		if idx != -1 {
			lastIndex += idx
			count++
			lastIndex += len(findStr)
		} else {
			lastIndex = -1
		}
	}
	fmt.Println(count)
	return count
}

// searchNaive is naive pattern searching. Best O(n), worst O(m*(n-m+1)).
func (si *StringImp) searchNaive(pat, txt string) {
	M := len(pat)
	N := len(txt)
	for i := 0; i <= N-M; i++ {
		j := 0
		for j = 0; j < M; j++ {
			if txt[i+j] != pat[j] {
				break
			}
		}
		if j == M {
			fmt.Print("Pattern found at index ", i)
		}
	}
}

// searchSubString is the KMP algorithm. Time O(m + n).
func (si *StringImp) searchSubString(text, ptrn []byte) {
	i, j := 0, 0
	ptrnLen := len(ptrn)
	txtLen := len(text)
	b := si.preProcessPattern(ptrn)
	for i < txtLen {
		for j >= 0 && text[i] != ptrn[j] {
			j = b[j]
		}
		i++
		j++
		if j == ptrnLen {
			fmt.Println("found substring at index:", i-ptrnLen)
			j = b[j]
		}
	}
}

func (si *StringImp) preProcessPattern(ptrn []byte) []int {
	i, j := 0, -1
	ptrnLen := len(ptrn)
	b := make([]int, ptrnLen+1)
	b[i] = j
	for i < ptrnLen {
		for j >= 0 && ptrn[i] != ptrn[j] {
			j = b[j]
		}
		i++
		j++
		b[i] = j
	}
	return b
}

// isRepeat returns true if str is a repetition of one of its substrings.
func (si *StringImp) isRepeat(str []byte) bool {
	n := len(str)
	lps := make([]int, n)
	si.computeLPSArray(str, n, lps)
	length := lps[n-1]
	return length > 0 && n%(n-length) == 0
}

// computeLPSArray fills lps[] (KMP prefix function).
func (si *StringImp) computeLPSArray(str []byte, M int, lps []int) {
	length := 0
	lps[0] = 0
	i := 1
	for i < M {
		if str[i] == str[length] {
			length++
			lps[i] = length
			i++
		} else {
			if length != 0 {
				length = lps[length-1]
			} else {
				lps[i] = 0
				i++
			}
		}
	}
}

// isSubSequence returns true if str1 is a subsequence of str2.
func (si *StringImp) isSubSequence(str1, str2 []byte, m, n int) bool {
	j := 0
	for i := 0; i < n && j < m; i++ {
		if str1[j] == str2[i] {
			j++
		}
	}
	return j == m
}

// smallest_character returns the smallest char strictly larger than c, wrapping
// to the smallest char in the sorted string.
func (si *StringImp) smallest_character(str string, c byte) byte {
	l, r := 0, len(str)-1
	ret := str[0]
	for l <= r {
		m := l + (r-l)/2
		if str[m] > c {
			ret = str[m]
			r = m - 1
		} else {
			l = m + 1
		}
	}
	return ret
}

// searchI finds str in a sorted array interspersed with empty strings.
func searchI(arr []string, str string, first, last int) int {
	for first <= last {
		mid := (last + first) / 2
		if arr[mid] == "" {
			left := mid - 1
			right := mid + 1
			for {
				if left < first && right > last {
					return -1
				} else if right <= last && arr[right] != "" {
					mid = right
					break
				} else if left >= first && arr[left] != "" {
					mid = left
					break
				}
				right++
				left--
			}
		}
		res := strings.Compare(arr[mid], str)
		if res == 0 {
			return mid
		} else if res < 0 {
			first = mid + 1
		} else {
			last = mid - 1
		}
	}
	return -1
}

// longPrefix finds the longest shared prefix of all space-separated words.
func (si *StringImp) longPrefix(str string) string {
	arr := strings.Split(str, " ")
	length := len(arr[0])
	for i := 1; i < len(arr); i++ {
		p := 0
		for p < length && p < len(arr[i]) && arr[0][p] == arr[i][p] {
			p++
		}
		length = p
	}
	return arr[0][:length]
}
