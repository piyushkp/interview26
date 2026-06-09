package main

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
)

// LongestPalindromeImprove finds the longest palindromic substring via suffix sort.
func LongestPalindromeImprove(s string) string {
	s += "^" + reverseStringGo(s)
	N := len(s)
	suffixes := make([]string, N)
	for i := 0; i < N; i++ {
		suffixes[i] = s[i:N]
	}
	sort.Strings(suffixes)
	m := map[string]int{}
	for i := 0; i < N-1; i++ {
		x := lcp(suffixes[i], suffixes[i+1])
		key := suffixes[i][:x]
		if _, ok := m[key]; !ok {
			m[key] = x
		}
	}
	var maxKey string
	first := true
	maxVal := 0
	for key, val := range m {
		if first || val > maxVal {
			maxKey = key
			maxVal = val
			first = false
		}
	}
	return maxKey
}

// lcp returns the length of the longest common prefix of s and t.
func lcp(s, t string) int {
	N := minInt(len(s), len(t))
	for i := 0; i < N; i++ {
		if s[i] != t[i] {
			return i
		}
	}
	return N
}

// palindromePairs returns index pairs whose concatenation is a palindrome.
func palindromePairs(words []string) [][]int {
	ans := [][]int{}
	m := map[string]int{}
	for i := 0; i < len(words); i++ {
		m[words[i]] = i
	}
	for k := 0; k < len(words); k++ {
		word := words[k]
		n := len(word)
		for i := 0; i < n+1; i++ {
			prefix := reverseStringGo(word[0:i])
			suffix := reverseStringGo(word[i:n])
			if idxS, ok := m[suffix]; i != 0 && ok && idxS != k && isPalindromeStr(prefix) {
				ans = append(ans, []int{idxS, k})
			}
			if idxP, ok := m[prefix]; ok && idxP != k && isPalindromeStr(suffix) {
				ans = append(ans, []int{k, idxP})
			}
		}
	}
	return ans
}

// TrieNode2 is the trie node used by palindromePairsImproved.
type TrieNode2 struct {
	next  [26]*TrieNode2
	index int
	list  []int
}

func newTrieNode2() *TrieNode2 {
	return &TrieNode2{index: -1, list: []int{}}
}

// palindromePairsImproved solves palindrome pairs with a Trie in O(n*k^2).
func (si *StringImp) palindromePairsImproved(words []string) [][]int {
	res := [][]int{}
	root := newTrieNode2()
	for i := 0; i < len(words); i++ {
		si.addWord(root, words[i], i)
	}
	for i := 0; i < len(words); i++ {
		si.searchPalindromePairs(words, i, root, &res)
	}
	return res
}

func (si *StringImp) addWord(root *TrieNode2, word string, index int) {
	for i := len(word) - 1; i >= 0; i-- {
		j := word[i] - 'a'
		if root.next[j] == nil {
			root.next[j] = newTrieNode2()
		}
		if isPalindromeRange(word, 0, i) {
			root.list = append(root.list, index)
		}
		root = root.next[j]
	}
	root.list = append(root.list, index)
	root.index = index
}

func (si *StringImp) searchPalindromePairs(words []string, i int, root *TrieNode2, res *[][]int) {
	for j := 0; j < len(words[i]); j++ {
		if root.index >= 0 && root.index != i && isPalindromeRange(words[i], j, len(words[i])-1) {
			*res = append(*res, []int{i, root.index})
		}
		root = root.next[words[i][j]-'a']
		if root == nil {
			return
		}
	}
	for _, j := range root.list {
		if i == j {
			continue
		}
		*res = append(*res, []int{i, j})
	}
}

// filterList keeps only words that have a palindrome partner in the list.
func filterList(input []string) []string {
	out := []string{}
	m := map[string]int{}
	for i := 0; i < len(input); i++ {
		m[input[i]] = i
	}
	for k := 0; k < len(input); k++ {
		word := input[k]
		n := len(word)
		for i := 0; i < n+1; i++ {
			prefix := reverseStringGo(word[0:i])
			suffix := reverseStringGo(word[i:n])
			if idxS, ok := m[suffix]; i != 0 && ok && idxS != k && isPalindromeStr(prefix) {
				out = append(out, suffix)
			}
			if idxP, ok := m[prefix]; ok && idxP != k && isPalindromeStr(suffix) {
				out = append(out, prefix)
			}
		}
	}
	return out
}

// isPalindromeStr returns true if word is a palindrome.
func isPalindromeStr(word string) bool {
	if len(word) < 2 {
		return true
	}
	for i := 0; i < len(word)/2; i++ {
		if word[i] != word[len(word)-i-1] {
			return false
		}
	}
	return true
}

// isPalindrome1 is case-insensitive and ignores non-alphanumeric characters.
func isPalindrome1(word string) bool {
	word = strings.ToLower(word)
	if len(word) < 2 {
		return true
	}
	l, r := 0, len(word)-1
	for l < r {
		for l < len(word) && !isLetterOrDigit(word[l]) {
			l++
		}
		for r >= 0 && !isLetterOrDigit(word[r]) {
			r--
		}
		if l < r && word[l] != word[r] {
			return false
		}
		l++
		r--
	}
	return true
}

func isPalindromeRange(s string, firstIndex, lastIndex int) bool {
	for i, j := firstIndex, lastIndex; i < j; i, j = i+1, j-1 {
		if s[i] != s[j] {
			return false
		}
	}
	return true
}

// canFormPalindrome checks if chars can be rearranged into a palindrome.
func canFormPalindrome(str string, totalCharsToCheck int) bool {
	m := make([]int, 128)
	count := 0
	for i := 0; i < len(str); i++ {
		m[str[i]]++
		if m[str[i]]%2 == 0 {
			count--
		} else {
			count++
		}
	}
	return count <= totalCharsToCheck+1
}

// hasPalindrome toggles occurrence bits and checks at most one odd count.
func hasPalindrome(s string) bool {
	occurrences := map[int]bool{}
	for i := 0; i < len(s); i++ {
		v := getNumericValue(s[i])
		occurrences[v] = !occurrences[v]
	}
	count := 0
	for _, set := range occurrences {
		if set {
			count++
		}
	}
	return count <= 1
}

// isAlmostPalindrome returns true if removing one char can make s a palindrome.
func isAlmostPalindrome(s string) bool {
	for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
		if s[i] != s[j] {
			return isPalindromeRange(s, i+1, j) || isPalindromeRange(s, i, j-1)
		}
	}
	return true
}

// LongestPalindromeRemoveShuffle returns the longest palindrome formed by
// removing/shuffling characters.
func LongestPalindromeRemoveShuffle(s string) string {
	output := ""
	center := ""
	counter := make([]int, 26)
	for i := 0; i < len(s); i++ {
		counter[int(s[i])-'a']++
	}
	for i := 0; i < len(counter); i++ {
		times := counter[i] / 2
		repeated := strings.Repeat(string(byte(i+'a')), times)
		output += repeated
		if counter[i]%2 != 0 {
			center = string(byte(i + 'a'))
		}
	}
	return output + center + reverseStringGo(output)
}

// areRotations checks if s2 is a rotation of s1.
func (si *StringImp) areRotations(s1, s2 string) bool {
	temp := s1 + s1
	return strings.Contains(temp, s2)
}

// printRec prints the top N positive integers in string comparison order.
func printRec(str string, n int) {
	if parseIntSafe(str) > n {
		return
	}
	fmt.Println(str)
	for i := 0; i < 10; i++ {
		printRec(str+strconv.Itoa(i), n)
	}
}

// removePatternFromString removes "b" and "ac" from a given string.
func removePatternFromString(str []byte) string {
	n := len(str)
	i := -1
	j := 0
	for j < n {
		if j < n-1 && str[j] == 'a' && str[j+1] == 'c' {
			j += 2
		} else if str[j] == 'b' {
			j++
		} else if i >= 0 && str[j] == 'c' && str[i] == 'a' {
			i--
			j++
		} else {
			i++
			str[i] = str[j]
			j++
		}
	}
	return string(str[:i+1])
}

// removeAdjacentDuplicates recursively removes all adjacent duplicates.
func removeAdjacentDuplicates(s string) string {
	if len(s) < 2 {
		return s
	}
	buf := []byte(s)
	lastchar := buf[0]
	j := 1
	for i := 1; i < len(buf); i++ {
		if j > 0 && buf[i] == buf[j-1] {
			lastchar = buf[j-1]
			for j > 0 && buf[j-1] == lastchar {
				j--
			}
		} else if buf[i] != lastchar {
			buf[j] = buf[i]
			j++
		}
	}
	return string(buf[:j])
}
