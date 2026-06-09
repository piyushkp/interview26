package main

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
)

// isIsomorphic returns true if s1 and s2 are isomorphic (ordered encoding).
func isIsomorphic(s1, s2 string) bool {
	if len(s1) != len(s2) {
		return false
	} else if len(s1) == 1 {
		return true
	}
	map1 := map[byte]int{}
	var enc1 strings.Builder
	map2 := map[byte]int{}
	var enc2 strings.Builder
	for i := 0; i < len(s1); i++ {
		if _, ok := map1[s1[i]]; !ok {
			map1[s1[i]] = i
		}
		enc1.WriteString(strconv.Itoa(map1[s1[i]]))
		if _, ok := map2[s2[i]]; !ok {
			map2[s2[i]] = i
		}
		enc2.WriteString(strconv.Itoa(map2[s2[i]]))
	}
	return enc1.String() == enc2.String()
}

// WordDistanceFinder pre-processes word positions for distance queries.
func (si *StringImp) WordDistanceFinder(words []string) {
	if si.wordDistMap == nil {
		si.wordDistMap = map[string][]int{}
	}
	for i := 0; i < len(words); i++ {
		si.wordDistMap[words[i]] = append(si.wordDistMap[words[i]], i)
	}
}

// distance returns the minimum index distance between two words (any order).
func (si *StringImp) distance(wordOne, wordTwo string) int {
	if si.wordDistMap == nil {
		return -1
	}
	l1, ok1 := si.wordDistMap[wordOne]
	l2, ok2 := si.wordDistMap[wordTwo]
	if !ok1 || !ok2 {
		return -1
	}
	if wordOne == wordTwo {
		return 0
	}
	minDistance := intMaxValue
	for _, i := range l1 {
		for _, j := range l2 {
			minDistance = minInt(minDistance, absInt(i-j))
		}
	}
	return minDistance
}

// minDistanceFinder finds the min distance between two words in O(n)/O(1).
func minDistanceFinder(strs []string, targetString, targetString2 string) int {
	index1 := -1
	index2 := -1
	minDistance := intMaxValue
	tempDistance := 0
	for x := 0; x < len(strs); x++ {
		if strs[x] == targetString {
			index1 = x
		}
		if strs[x] == targetString2 {
			index2 = x
		}
		if index1 != -1 && index2 != -1 {
			tempDistance = absInt(index2 - index1)
			if tempDistance < minDistance {
				minDistance = tempDistance
			}
		}
	}
	return minDistance
}

// areAnagram checks whether two strings are anagrams.
func areAnagram(s1, s2 string) bool {
	if len(s1) != len(s2) {
		return false
	}
	counter := make([]int, 256)
	for i := 0; i < len(s1); i++ {
		counter[s1[i]]++
		counter[s2[i]]--
	}
	for i := 0; i < 256; i++ {
		if counter[i] != 0 {
			return false
		}
	}
	return true
}

// areKAnagram checks whether two strings are k-anagrams.
func areKAnagram(s1, s2 string, K int) bool {
	if len(s1) != len(s2) {
		return false
	}
	counter := make([]int, 256)
	for i := 0; i < len(s1); i++ {
		counter[s1[i]]++
	}
	count := 0
	for i := 0; i < len(s2); i++ {
		if counter[s2[i]] > 0 {
			counter[s2[i]]--
		} else {
			count++
		}
	}
	return count <= K
}

// anagramsMatch prints and returns start indices of anagrams of p inside s.
func anagramsMatch(s, p string) []int {
	list := []int{}
	count := make([]int, 256)
	tc := make([]int, 256)
	for i := 0; i < len(p); i++ {
		count[p[i]]++
		tc[s[i]]++
	}
	if matchCount(count, tc) {
		list = append(list, 0)
	}
	for i := len(p); i < len(s); i++ {
		tc[s[i-len(p)]]--
		tc[s[i]]++
		if matchCount(count, tc) {
			list = append(list, i-len(p)+1)
		}
	}
	for _, num := range list {
		fmt.Print("Found at Index ", num)
	}
	return list
}

func matchCount(a, b []int) bool {
	for i := 0; i < len(a); i++ {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

// printUtil groups words with their reverse.
func printUtil(input []string) [][]string {
	m := map[string]int{}
	output := [][]string{}
	for i := 0; i < len(input); i++ {
		key := reverseStringGo(input[i])
		if _, ok := m[key]; !ok {
			m[key] = i
		}
	}
	for i := 0; i < len(input); i++ {
		out := []string{}
		if idx, ok := m[input[i]]; ok && idx != i {
			out = append(out, input[i])
			out = append(out, input[idx])
		}
		output = append(output, out)
	}
	return output
}

// printAnagramsUtil prints all anagrams grouped together.
func printAnagramsUtil(input []string) {
	m := map[string][]int{}
	for i := 0; i < len(input); i++ {
		content := []byte(input[i])
		sort.Slice(content, func(a, b int) bool { return content[a] < content[b] })
		key := string(content)
		m[key] = append(m[key], i)
	}
	for _, indices := range m {
		if len(indices) > 1 {
			for i := 0; i < len(indices); i++ {
				fmt.Print(input[indices[i]] + " ")
			}
			fmt.Println()
		}
	}
}

// reverseWordsInPlace reverses words in a sentence in place. Time O(n) space O(1).
func reverseWordsInPlace(s []byte) {
	reverseCharRange(s, 0, len(s)-1)
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == ' ' {
			reverseCharRange(s, start, i-1)
			start = i + 1
		}
	}
	reverseCharRange(s, start, len(s)-1)
}

func reverseCharRange(s []byte, start, end int) {
	for start < end {
		s[start], s[end] = s[end], s[start]
		start++
		end--
	}
}

// reverseWordsSentence reverses the order of words in a sentence.
func reverseWordsSentence(sentence string) string {
	var sb strings.Builder
	words := strings.Split(sentence, " ")
	for i := len(words) - 1; i >= 0; i-- {
		sb.WriteString(words[i])
		sb.WriteByte(' ')
	}
	result := sb.String()
	if len(result) > 0 {
		result = result[:len(result)-1] // strip trailing space
	}
	return result
}

// CountOfCommonCharacters prints chars of s that appear in both S1 and S2.
func (si *StringImp) CountOfCommonCharacters(s, S1, S2 string) {
	set := map[string]bool{}
	for i := 0; i < len(s); i++ {
		c := s[i]
		if strings.IndexByte(S1, c) != -1 && strings.IndexByte(S2, c) != -1 {
			set[string(c)] = true
		}
	}
	for str := range set {
		fmt.Println(str)
	}
}

// wrapthis performs word wrapping with a minimum-cost layout and prints it.
func (si *StringImp) wrapthis(para string, w int) {
	c := strings.Split(para, " ")
	n := len(c)
	cost := make([]int, n)
	espace := make([][]int, n)
	for i := range espace {
		espace[i] = make([]int, n)
	}
	line := make([]int, n)
	for i := 0; i < n; i++ {
		for j := 0; j <= i; j++ {
			t := 0
			if i == j {
				t = len(c[i])
			} else {
				if i > j {
					for k := j; k <= i; k++ {
						t = t + len(c[k])
					}
				} else {
					for k := i; k <= j; k++ {
						t = t + len(c[k])
					}
				}
			}
			if t > w {
				espace[i][j] = -1
				espace[j][i] = -1
			} else {
				espace[i][j] = w - t - (i - j)
				espace[j][i] = w - t - (i - j)
			}
			fmt.Print(" ", espace[i][j])
		}
		fmt.Println()
	}
	es := w - len(c[0])
	cost[0] = es * es * es
	for j := 1; j < n; j++ {
		var t int
		cost[j] = intMaxValue
		for i := 1; i <= j; i++ {
			if espace[i][j] != -1 {
				t = cost[i-1] + espace[i][j]*espace[i][j]*espace[i][j]
				if t < cost[j] {
					cost[j] = t
					line[j] = i
				}
			}
		}
		fmt.Println("optimal line", line[j])
	}
	fmt.Println("optimal cost", cost[n-1])
	pre := 0
	fmt.Print(" ", c[0])
	for i := 1; i < n; i++ {
		if line[i] == pre {
			fmt.Print(" ", c[i])
		} else {
			fmt.Println()
			fmt.Print(" ", c[i])
			pre = line[i]
		}
	}
}
