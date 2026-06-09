package main

import "strings"

// ---------------------------------------------------------------------------
// Edit distance / Levenshtein.
// ---------------------------------------------------------------------------

// editDistDP computes the Levenshtein distance between str1 and str2.
// Time O(m x n), space O(m x n).
func (si *StringImp) editDistDP(str1, str2 string, m, n int) int {
	dp := make([][]int, m+1)
	for i := range dp {
		dp[i] = make([]int, n+1)
	}
	if n == 0 {
		return m
	}
	if m == 0 {
		return n
	}
	for i := 0; i <= m; i++ {
		dp[i][0] = i
	}
	for j := 0; j <= n; j++ {
		dp[0][j] = j
	}
	for i := 1; i <= m; i++ {
		for j := 1; j <= n; j++ {
			if str1[i-1] == str2[j-1] {
				dp[i][j] = dp[i-1][j-1]
			} else {
				dp[i][j] = 1 + minInt(minInt(dp[i][j-1], dp[i-1][j]), dp[i-1][j-1])
			}
		}
	}
	return dp[m][n]
}

// ---------------------------------------------------------------------------
// K edit distance using a Trie.
// ---------------------------------------------------------------------------

// TrieNode is a 26-way trie node used by getKEditDistance.
type TrieNode struct {
	children [26]*TrieNode
	isLeaf   bool
}

// Trie wraps a TrieNode root.
type Trie struct {
	root *TrieNode
}

func newTrie() *Trie { return &Trie{root: &TrieNode{}} }

// add inserts a word into the trie.
func (t *Trie) add(s string) {
	if len(s) == 0 {
		return
	}
	p := t.root
	for i := 0; i < len(s); i++ {
		c := s[i]
		if p.children[c-'a'] == nil {
			p.children[c-'a'] = &TrieNode{}
		}
		if i == len(s)-1 {
			p.children[c-'a'].isLeaf = true
		}
		p = p.children[c-'a']
	}
}

// getKEditDistance returns all words whose edit distance with target is <= k.
func (si *StringImp) getKEditDistance(words []string, target string, k int) []string {
	result := []string{}
	if len(words) == 0 || len(target) == 0 || k < 0 {
		return result
	}
	trie := newTrie()
	for _, word := range words {
		trie.add(word)
	}
	root := trie.root
	prev := make([]int, len(target)+1)
	for i := range prev {
		prev[i] = i
	}
	si.getKEditDistanceHelper("", target, k, root, prev, &result)
	return result
}

func (si *StringImp) getKEditDistanceHelper(curr, target string, k int, root *TrieNode, prevDist []int, result *[]string) {
	if root.isLeaf {
		if prevDist[len(target)] <= k {
			*result = append(*result, curr)
		} else {
			return
		}
	}
	for i := 0; i < 26; i++ {
		if root.children[i] == nil {
			continue
		}
		currDist := make([]int, len(target)+1)
		currDist[0] = len(curr) + 1
		for j := 1; j < len(prevDist); j++ {
			if target[j-1] == byte(i+'a') {
				currDist[j] = prevDist[j-1]
			} else {
				currDist[j] = minInt(minInt(prevDist[j-1], prevDist[j]), currDist[j-1]) + 1
			}
		}
		si.getKEditDistanceHelper(curr+string(byte(i+'a')), target, k, root.children[i], currDist, result)
	}
}

// ---------------------------------------------------------------------------
// BK tree (spell checker).
// ---------------------------------------------------------------------------

type bkNode struct {
	rootWord string
	children map[int]*bkNode
}

func newBKNode(word string) *bkNode {
	return &bkNode{rootWord: word, children: map[int]*bkNode{}}
}

func (n *bkNode) add(word string) {
	distance := levenshteinDistance(word, n.rootWord)
	child := n.children[distance]
	if child != nil {
		child.add(word)
	} else {
		n.children[distance] = newBKNode(word)
	}
}

// BKTree is a metric tree for fuzzy string matching.
type BKTree struct {
	root *bkNode
}

func (t *BKTree) add(word string) {
	if t.root != nil {
		t.root.add(word)
	} else {
		t.root = newBKNode(word)
	}
}

func (t *BKTree) search(query string, maxDistance int) []string {
	matches := []string{}
	if maxDistance < 0 {
		return matches
	}
	queue := []*bkNode{t.root}
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		element := node.rootWord
		distance := levenshteinDistance(element, query)
		if distance <= maxDistance {
			matches = append(matches, element)
		}
		for i := distance - maxDistance; i <= distance+maxDistance; i++ {
			if i > 0 {
				if childNode := node.children[i]; childNode != nil {
					queue = append(queue, childNode)
				}
			}
		}
	}
	return matches
}

func levenshteinDistance(first, second string) int {
	if len(first) == 0 {
		return len(second)
	}
	if len(second) == 0 {
		return len(first)
	}
	lenFirst := len(first)
	lenSecond := len(second)
	d := make([][]int, lenFirst+1)
	for i := range d {
		d[i] = make([]int, lenSecond+1)
	}
	for i := 0; i <= lenFirst; i++ {
		d[i][0] = i
	}
	for i := 0; i <= lenSecond; i++ {
		d[0][i] = i
	}
	for i := 1; i <= lenFirst; i++ {
		for j := 1; j <= lenSecond; j++ {
			match := 1
			if first[i-1] == second[j-1] {
				match = 0
			}
			d[i][j] = minInt(minInt(d[i-1][j]+1, d[i][j-1]+1), d[i-1][j-1]+match)
		}
	}
	return d[lenFirst][lenSecond]
}

// isEditDistanceOne returns true if s1 can be converted to s2 with exactly one edit.
func isEditDistanceOne(s1, s2 string) bool {
	m, n := len(s1), len(s2)
	if absInt(m-n) > 1 {
		return false
	}
	count := 0
	i, j := 0, 0
	for i < m && j < n {
		if s1[i] != s2[j] {
			if count == 1 {
				return false
			}
			if m > n {
				i++
			} else if m < n {
				j++
			} else {
				i++
				j++
			}
			count++
		} else {
			i++
			j++
		}
	}
	if i < m || j < n {
		count++
	}
	return count == 1
}

// numberofMinDeletion finds the minimum number of deletions to make word a valid
// dictionary word.
func numberofMinDeletion(word string, dic map[string]bool) int {
	mindelete := len(word)
	for item := range dic {
		if word == item {
			return 0
		} else if len(item) >= len(word) {
			continue
		} else {
			mindelete = minInt(mindelete, minDeletionToTransformWord(word, item))
		}
	}
	if mindelete == len(word) {
		return -1
	}
	return mindelete
}

func minDeletionToTransformWord(s1, s2 string) int {
	m, n := len(s1), len(s2)
	count := 0
	i, j := 0, 0
	for i < m && j < n {
		if s1[i] != s2[j] {
			if m > n {
				i++
			}
			count++
		} else {
			i++
			j++
		}
	}
	for i < m {
		count++
		i++
	}
	if j < n {
		return m
	}
	return count
}

// ---------------------------------------------------------------------------
// Word break.
// ---------------------------------------------------------------------------

// WordBreakMaxTwo splits input into at most two dictionary words in O(n).
func WordBreakMaxTwo(input string, dict map[string]bool) string {
	length := len(input)
	for i := 1; i < length; i++ {
		prefix := input[:i]
		if dict[prefix] {
			suffix := input[i:length]
			if dict[suffix] {
				return prefix + " " + suffix
			}
		}
	}
	return ""
}

// memoized stores already-solved word-break inputs (empty string means "no solution").
var memoized = map[string]string{}
var memoizedHas = map[string]bool{}

// wordBreakUsingDP returns a single space-separated segmentation, or "" if none.
func wordBreakUsingDP(input string, dict map[string]bool) string {
	if dict[input] {
		return input
	}
	if memoizedHas[input] {
		return memoized[input]
	}
	length := len(input)
	for i := 1; i < length; i++ {
		prefix := input[:i]
		if dict[prefix] {
			suffix := input[i:length]
			segSuffix := wordBreakUsingDP(suffix, dict)
			if segSuffix != "" {
				return prefix + " " + segSuffix
			}
		}
		memoized[input] = ""
		memoizedHas[input] = true
	}
	return ""
}

// wordBreak returns true if s can be segmented into dictionary words.
func wordBreak(s string, dict map[string]bool) bool {
	f := make([]bool, len(s)+1)
	f[0] = true
	for i := 1; i <= len(s); i++ {
		for j := 0; j < i; j++ {
			if f[j] && dict[s[j:i]] {
				f[i] = true
				break
			}
		}
	}
	return f[len(s)]
}

// wordBreakII returns all possible sentences (memoized).
func (si *StringImp) wordBreakII(s string, wordDict map[string]bool) []string {
	if si.wordBreakMemo == nil {
		si.wordBreakMemo = map[string][]string{}
	}
	if v, ok := si.wordBreakMemo[s]; ok {
		return v
	}
	res := []string{}
	if len(s) == 0 {
		res = append(res, "")
		return res
	}
	for word := range wordDict {
		if strings.HasPrefix(s, word) {
			sublist := si.wordBreakII(s[len(word):], wordDict)
			for _, sub := range sublist {
				sep := ""
				if sub != "" {
					sep = " "
				}
				res = append(res, word+sep+sub)
			}
		}
	}
	si.wordBreakMemo[s] = res
	return res
}

// wordBreakIII is a second approach to enumerating sentences.
func (si *StringImp) wordBreakIII(s string, wordDict map[string]bool) []string {
	if si.wordBreakMemo == nil {
		si.wordBreakMemo = map[string][]string{}
	}
	if v, ok := si.wordBreakMemo[s]; ok {
		return v
	}
	length := len(s)
	ret := []string{}
	if wordDict[s] {
		ret = append(ret, s)
	}
	for i := 1; i < length; i++ {
		curr := s[i:]
		if wordDict[curr] {
			strs := si.wordBreakIII(s[:i], wordDict)
			if len(strs) != 0 {
				for _, st := range strs {
					ret = append(ret, st+" "+curr)
				}
			}
		}
	}
	si.wordBreakMemo[s] = ret
	return ret
}

// dictionaryContains checks a hard-coded sample dictionary.
func (si *StringImp) dictionaryContains(word string) bool {
	dictionary := []string{"mobile", "samsung", "sam", "sung", "man", "mango",
		"icecream", "and", "go", "i", "like", "ice", "cream"}
	for i := 0; i < len(dictionary); i++ {
		if dictionary[i] == word {
			return true
		}
	}
	return false
}

// lcs returns the length of the longest common subsequence of X and Y. Time O(mn).
func (si *StringImp) lcs(X, Y []byte, m, n int) int {
	L := make([][]int, m+1)
	for i := range L {
		L[i] = make([]int, n+1)
	}
	for i := 0; i <= m; i++ {
		for j := 0; j <= n; j++ {
			if i == 0 || j == 0 {
				L[i][j] = 0
			} else if X[i-1] == Y[j-1] {
				L[i][j] = L[i-1][j-1] + 1
			} else {
				L[i][j] = maxInt(L[i-1][j], L[i][j-1])
			}
		}
	}
	return L[m][n]
}
