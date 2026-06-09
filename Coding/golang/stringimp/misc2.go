package main

import (
	"container/heap"
	"fmt"
	"strconv"
	"strings"
)

// initWords builds a per-word character-count map (Java init(String[])).
func (si *StringImp) initWords(words []string) map[string][]int {
	m := map[string][]int{}
	for i := 0; i < len(words); i++ {
		count := make([]int, 26)
		ch := []byte(words[i])
		for j := 0; j < len(ch); j++ {
			count[ch[j]-'a']++
		}
		m[words[i]] = count
	}
	return m
}

// wordFinder returns dictionary words formable from exactly the given character set.
func (si *StringImp) wordFinder(input map[byte]bool, m map[string][]int) map[string]bool {
	out := map[string]bool{}
	charCount := make([]int, 26)
	for c := range input {
		charCount[c-'a']++
	}
	for key, temp := range m {
		isMatch := true
		for i := 0; i < len(temp); i++ {
			if temp[i] != charCount[i] {
				isMatch = false
				break
			}
		}
		if isMatch {
			out[key] = true
		}
	}
	return out
}

// trieWordFinderRoot mirrors the Java instance field root1.
var trieWordFinderRoot *TrieWordFinder

// TrieWordFinder is a 26-way trie used by the word-finder.
type TrieWordFinder struct {
	letter byte
	child  [26]*TrieWordFinder
	isWord bool
}

func newTrieWordFinder(letter byte) *TrieWordFinder {
	return &TrieWordFinder{letter: letter}
}

func (t *TrieWordFinder) insert(word string) {
	node := trieWordFinderRoot
	ch := []byte(word)
	for i := 0; i < len(ch); i++ {
		if node.child[ch[i]-'a'] == nil {
			node.child[ch[i]-'a'] = newTrieWordFinder(ch[i])
			if i == len(ch)-1 {
				node.child[ch[i]-'a'].isWord = true
			}
		}
		node = node.child[ch[i]-'a']
	}
}

func (t *TrieWordFinder) findUtil(letter []int) map[string]bool {
	out := map[string]bool{}
	node := trieWordFinderRoot
	for i := 0; i < len(letter); i++ {
		word := ""
		for letter[i] > 0 && node.child[letter[i]-'a'] != nil {
			word += string(node.child[letter[i]-'a'].letter)
			if node.child[letter[i]-'a'].isWord {
				out[word] = true
			}
			node = node.child[letter[i]-'a']
		}
	}
	return out
}

func (t *TrieWordFinder) init(words []string) {
	for _, word := range words {
		t.insert(word)
	}
}

func (t *TrieWordFinder) find(letters []byte) map[string]bool {
	let := make([]int, 26)
	for i := 0; i < len(letters); i++ {
		let[letters[i]-'a']++
	}
	return t.findUtil(let)
}

// maxProduct returns the max length product of two words that share no letters.
func (si *StringImp) maxProduct(words []string) int {
	if len(words) <= 1 {
		return 0
	}
	n := len(words)
	encodedWords := make([]int, n)
	for i := 0; i < len(words); i++ {
		word := words[i]
		for j := 0; j < len(word); j++ {
			c := word[j]
			encodedWords[i] |= 1 << (c - 'a')
		}
	}
	maxLen := 0
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			if encodedWords[i]&encodedWords[j] == 0 {
				maxLen = maxInt(maxLen, len(words[i])*len(words[j]))
			}
		}
	}
	return maxLen
}

// canShuffle returns true if the chars can be shuffled with no equal neighbors.
func (si *StringImp) canShuffle(s []byte) bool {
	counter := make([]int, 300)
	for _, c := range s {
		counter[c]++
	}
	maxExistedCharacter := 0
	for c := 'a'; c <= 'z'; c++ {
		maxExistedCharacter = maxInt(counter[c], maxExistedCharacter)
	}
	return maxExistedCharacter <= (len(s)+1)/2
}

// checkIfSortedArray returns true if words are sorted by the given char ordering.
func checkIfSortedArray(strs []string, orderings []byte) bool {
	m := map[byte]int{}
	for i := 0; i < len(orderings); i++ {
		m[orderings[i]] = i
	}
	for i := 1; i < len(strs); i++ {
		word1 := strs[i-1]
		word2 := strs[i]
		for j := 0; j < minInt(len(word1), len(word2)); j++ {
			if word1[j] != word2[j] {
				from := word1[j]
				to := word2[j]
				if m[from] > m[to] {
					return false
				}
			}
		}
	}
	return true
}

// ---------------------------------------------------------------------------
// Alien dictionary (topological sort).
// ---------------------------------------------------------------------------

// Graph is an adjacency-list directed graph for alienOrder.
type Graph struct {
	adjacencyList [][]int
}

func newGraph(nVertices int) *Graph {
	g := &Graph{adjacencyList: make([][]int, nVertices)}
	for v := 0; v < nVertices; v++ {
		g.adjacencyList[v] = []int{}
	}
	return g
}

func (g *Graph) addEdge(startVertex, endVertex int) {
	g.adjacencyList[startVertex] = append(g.adjacencyList[startVertex], endVertex)
}

func (g *Graph) getNoOfVertices() int { return len(g.adjacencyList) }

// alienOrder derives the order of letters from a sorted dictionary.
func alienOrder(words []string, noOfAlpha int) string {
	graph := newGraph(noOfAlpha)
	for i := 0; i < len(words)-1; i++ {
		word1 := words[i]
		word2 := words[i+1]
		for j := 0; j < minInt(len(word1), len(word2)); j++ {
			if word1[j] != word2[j] {
				graph.addEdge(int(word1[j]-'a'), int(word2[j]-'a'))
				break
			}
		}
	}
	return graph.topologicalSort()
}

func (g *Graph) topologicalSort() string {
	stack := []int{}
	visited := map[int]bool{}
	for i := 0; i < g.getNoOfVertices(); i++ {
		if !visited[i] {
			g.topologicalSortUtil(i, visited, &stack)
		}
	}
	var output strings.Builder
	for len(stack) > 0 {
		top := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		output.WriteString(string(byte('a'+top)) + " ")
	}
	return reverseStringGo(output.String())
}

func (g *Graph) topologicalSortUtil(currentVertex int, visited map[int]bool, stack *[]int) {
	visited[currentVertex] = true
	for _, adjacentVertex := range g.adjacencyList[currentVertex] {
		if !visited[adjacentVertex] {
			g.topologicalSortUtil(adjacentVertex, visited, stack)
		}
	}
	*stack = append(*stack, currentVertex)
}

// addBinary returns the sum of two numbers expressed in the given base.
func addBinary(a, b string, base int) string {
	if len(a) == 0 {
		return b
	}
	if len(b) == 0 {
		return a
	}
	var sb strings.Builder
	i := len(a) - 1
	j := len(b) - 1
	carry := 0
	for i >= 0 || j >= 0 {
		sum := 0
		if i >= 0 {
			sum += getNumericValue(a[i])
			i--
		}
		if j >= 0 {
			sum += getNumericValue(b[j])
			j--
		}
		sum += carry
		if sum >= base {
			carry = 1
		} else {
			carry = 0
		}
		sb.WriteByte(byte((sum % base) + '0'))
	}
	if carry == 1 {
		sb.WriteByte('1')
	}
	return reverseStringGo(sb.String())
}

// multiply multiplies two big integers represented as strings. O(nm).
func multiply(str1, str2 string) string {
	output := "0"
	count := 0
	for i := len(str2) - 1; i >= 0; i-- {
		d2 := int(str2[i] - '0')
		carry := 0
		var prod []byte
		for j := len(str1) - 1; j >= 0; j-- {
			d1 := int(str1[j] - '0')
			p := carry + (d1 * d2)
			prod = append(prod, byte((p%10)+'0'))
			carry = p / 10
		}
		if carry != 0 {
			prod = append(prod, byte(carry+'0'))
		}
		for l, r := 0, len(prod)-1; l < r; l, r = l+1, r-1 {
			prod[l], prod[r] = prod[r], prod[l]
		}
		for k := 0; k < count; k++ {
			prod = append(prod, '0')
		}
		output = addBinary(output, string(prod), 10)
		count++
	}
	return output
}

// letterPhoneCombinations returns all letter combinations for a digit string.
func letterPhoneCombinations(digits string) []string {
	queue := []string{}
	if digits == "" {
		return queue
	}
	m := []string{"0", "1", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"}
	queue = append(queue, "")
	for len(queue) > 0 && len(queue[0]) != len(digits) {
		remove := queue[0]
		queue = queue[1:]
		letters := m[digits[len(remove)]-'0']
		for i := 0; i < len(letters); i++ {
			queue = append(queue, remove+string(letters[i]))
		}
	}
	return queue
}

// removeUnbalanceParenthesis removes the fewest characters to balance parentheses.
func removeUnbalanceParenthesis(s string) string {
	str := []byte(s)
	left := 0
	for i := 0; i < len(str); i++ {
		if str[i] == '(' {
			left++
		} else if str[i] == ')' {
			if left > 0 {
				left--
			} else {
				str = append(str[:i], str[i+1:]...)
				i--
			}
		}
	}
	right := 0
	for i := len(str) - 1; i >= 0; i-- {
		if str[i] == ')' {
			right++
		} else if str[i] == '(' {
			if right > 0 {
				right--
			} else {
				str = append(str[:i], str[i+1:]...)
			}
		}
	}
	return string(str)
}

// removeInvalidParentheses1 removes the minimum invalid parentheses (2 passes).
func removeInvalidParentheses1(s string) string {
	r := removeInvalidHelper(s, [2]byte{'(', ')'})
	tmp := removeInvalidHelper(reverseStringGo(r), [2]byte{')', '('})
	return reverseStringGo(tmp)
}

func removeInvalidHelper(s string, p [2]byte) string {
	stack := 0
	for i := 0; i < len(s); i++ {
		if s[i] == p[0] {
			stack++
		}
		if s[i] == p[1] {
			stack--
		}
		if stack < 0 {
			s = s[:i] + s[i+1:]
			i--
			stack = 0
		}
	}
	return s
}

// numberToWords converts an integer to its English words representation.
var oneWords = []string{"", "one", "two", "three", "four", "five", "six",
	"seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
	"fifteen", "sixteen", "seventeen", "eighteen", "nineteen"}
var tenWords = []string{"", "Ten", "twenty", "thirty", "forty", "fifty", "sixty",
	"seventy", "eighty", "ninety"}
var bigWords = []string{"", "thousand", "million", "billion"}

func numberToWords(num int) string {
	if num == 0 {
		return "Zero"
	}
	i := 0
	output := ""
	for num > 0 {
		if num%1000 != 0 {
			output = numberToWordsUtil(num%1000) + bigWords[i] + " " + output
		}
		num /= 1000
		i++
	}
	return strings.TrimSpace(output)
}

func numberToWordsUtil(num int) string {
	if num == 0 {
		return ""
	} else if num < 20 {
		return oneWords[num] + " "
	} else if num < 100 {
		return tenWords[num/10] + " " + numberToWordsUtil(num%10)
	}
	return oneWords[num/100] + " Hundred " + numberToWordsUtil(num%100)
}

// restoreIpAddresses returns all valid IP address combinations of s.
func restoreIpAddresses(s string) []string {
	res := []string{}
	if len(s) == 0 {
		return res
	}
	length := len(s)
	if length < 4 || length > 12 {
		return res
	}
	for i := 1; i < 4; i++ {
		for j := i + 1; j < i+4; j++ {
			for k := j + 1; k < j+4 && k < length; k++ {
				s1 := s[0:i]
				s2 := s[i:j]
				s3 := s[j:k]
				s4 := s[k:length]
				if isValid1(s1) && isValid1(s2) && isValid1(s3) && isValid1(s4) {
					res = append(res, s1+"."+s2+"."+s3+"."+s4)
				}
			}
		}
	}
	return res
}

func isValid1(s string) bool {
	if len(s) > 1 && s[0] == '0' || parseIntSafe(s) > 255 {
		return false
	}
	return true
}

// addOperators returns expressions using + - * over the digits that equal target.
func addOperators(num string, target int) []string {
	res := []string{}
	var sb []byte
	addOperatorsDFS(&res, &sb, []byte(num), 0, int64(target), 0, 0)
	return res
}

func addOperatorsDFS(res *[]string, sb *[]byte, num []byte, pos int, target, prev, multi int64) {
	if pos == len(num) {
		if target == prev {
			*res = append(*res, string(*sb))
		}
		return
	}
	var curr int64 = 0
	for i := pos; i < len(num); i++ {
		if num[pos] == '0' && i != pos {
			break
		}
		curr = 10*curr + int64(num[i]-'0')
		length := len(*sb)
		if pos == 0 {
			*sb = append(*sb, []byte(strconv.FormatInt(curr, 10))...)
			addOperatorsDFS(res, sb, num, i+1, target, curr, curr)
			*sb = (*sb)[:length]
		} else {
			*sb = append(*sb, '+')
			*sb = append(*sb, []byte(strconv.FormatInt(curr, 10))...)
			addOperatorsDFS(res, sb, num, i+1, target, prev+curr, curr)
			*sb = (*sb)[:length]
			*sb = append(*sb, '-')
			*sb = append(*sb, []byte(strconv.FormatInt(curr, 10))...)
			addOperatorsDFS(res, sb, num, i+1, target, prev-curr, -curr)
			*sb = (*sb)[:length]
			*sb = append(*sb, '*')
			*sb = append(*sb, []byte(strconv.FormatInt(curr, 10))...)
			addOperatorsDFS(res, sb, num, i+1, target, prev-multi+multi*curr, multi*curr)
			*sb = (*sb)[:length]
		}
	}
}

// nextClosestTime forms the next closest time reusing the current digits.
func nextClosestTime(time string) string {
	hour := parseIntSafe(time[0:2])
	min := parseIntSafe(time[3:5])
	for {
		min++
		if min == 60 {
			min = 0
			hour++
			hour %= 24
		}
		curr := fmt.Sprintf("%02d:%02d", hour, min)
		valid := true
		for i := 0; i < len(curr); i++ {
			if strings.IndexByte(time, curr[i]) < 0 {
				valid = false
				break
			}
		}
		if valid {
			return curr
		}
	}
}

// wordPattern returns true if str follows pattern.
func wordPattern(pattern, str string) bool {
	words := strings.Split(str, " ")
	if len(words) != len(pattern) {
		return false
	}
	m := map[byte]string{}
	for i := 0; i < len(pattern); i++ {
		key := pattern[i]
		word := words[i]
		if existing, ok := m[key]; ok && existing != word {
			return false
		}
		if _, ok := m[key]; !ok && mapContainsValue(m, word) {
			return false
		}
		m[key] = word
	}
	return true
}

func mapContainsValue(m map[byte]string, value string) bool {
	for _, v := range m {
		if v == value {
			return true
		}
	}
	return false
}

// wordPatternMatch returns true if str follows pattern (with substring mapping).
func wordPatternMatch(pattern, str string) bool {
	m := map[byte]string{}
	return wordPatternIsMatch(str, 0, pattern, 0, m)
}

func wordPatternIsMatch(str string, strIndex int, pat string, patIndex int, m map[byte]string) bool {
	if strIndex == len(str) && patIndex == len(pat) {
		return true
	}
	if strIndex == len(str) || patIndex == len(pat) {
		return false
	}
	patChar := pat[patIndex]
	if s, ok := m[patChar]; ok {
		if !strings.HasPrefix(str[strIndex:], s) {
			return false
		}
		return wordPatternIsMatch(str, strIndex+len(s), pat, patIndex+1, m)
	}
	for k := strIndex; k < len(str); k++ {
		strMatch := str[strIndex : k+1]
		if mapContainsValue(m, strMatch) {
			continue
		}
		m[patChar] = strMatch
		if wordPatternIsMatch(str, k+1, pat, patIndex+1, m) {
			return true
		}
		delete(m, patChar)
	}
	return false
}

// sortSpecialArrayUtil staggers sub-arrays of the form a1..aN b1..bN c1..cN.
func sortSpecialArrayUtil(array []string) {
	N := getNumberOfChar(array[len(array)-1])
	charCount := len(array) / N
	lastIndex := len(array) - 2
	for i := 1; i <= lastIndex; i++ {
		element := array[i]
		swapStrings(array, i, getSwapIndex(charCount, element))
	}
}

func getNumberOfChar(str string) int {
	return parseIntSafe(str[1:len(str)])
}

func getSwapIndex(charCount int, element string) int {
	c := toLowerByte(element[0])
	num := getNumberOfChar(element)
	charDistance := int(c - 'a')
	return charDistance + (charCount * (num - 1))
}

// printJSON pretty-prints a JSON string.
func printJSON(str string) {
	tokens := []byte(str)
	space := ""
	stack := []string{}
	for i := 0; i < len(tokens); i++ {
		temp := tokens[i]
		if temp == '{' {
			space = getTab(len(stack))
			fmt.Print("\n")
			fmt.Print(space + "{")
			fmt.Print("\n" + space)
			stack = append(stack, string(temp))
		} else if temp == '}' {
			stack = stack[:len(stack)-1]
			space = getTab(len(stack))
			fmt.Print("\n")
			fmt.Print(space + "}")
		} else if temp == '[' {
			space = getTab(len(stack))
			fmt.Print("\n")
			fmt.Print(space + "[")
			stack = append(stack, string(temp))
		} else if temp == ']' {
			stack = stack[:len(stack)-1]
			space = getTab(len(stack))
			fmt.Print("\n")
			fmt.Print(space + "]")
		} else if temp == ',' {
			fmt.Print("\n" + space)
		} else {
			fmt.Print(strings.TrimSpace(string(temp)))
		}
	}
}

func getTab(N int) string {
	return strings.Repeat("\t", N)
}

// read4 is a stub for the "Read N Characters Given Read4" problems.
func read4(buf []byte) int {
	return -1
}

// read reads up to n characters using read4.
func read(buf []byte, n int) int {
	eof := false
	total := 0
	tmp := make([]byte, 4)
	for !eof && total < n {
		count := read4(tmp)
		eof = count < 4
		count = minInt(count, n-total)
		for i := 0; i < count; i++ {
			buf[total] = tmp[i]
			total++
		}
	}
	return total
}

// readII reads up to n characters using read4 and may be called multiple times.
func (si *StringImp) readII(buf []byte, n int) int {
	if si.buffer == nil {
		si.buffer = make([]byte, 4)
	}
	totalCharactersRead := 0
	eof := false
	for !eof && totalCharactersRead < n {
		if si.charactersInBuffer == 0 {
			si.charactersInBuffer = read4(si.buffer)
			eof = si.charactersInBuffer < 4
		}
		numCharactersUsed := minInt(si.charactersInBuffer, n-totalCharactersRead)
		for i := 0; i < numCharactersUsed; i++ {
			buf[totalCharactersRead+i] = si.buffer[si.offset+i]
		}
		totalCharactersRead += numCharactersUsed
		si.charactersInBuffer -= numCharactersUsed
		si.offset = (si.offset + numCharactersUsed) % 4
	}
	return totalCharactersRead
}

// Count tracks a word and its transformation depth for ladderLength.
type Count struct {
	str   string
	count int
}

// ladderLength returns the length of the shortest transformation sequence.
func (si *StringImp) ladderLength(start, end string, dict map[string]bool) int {
	visited := map[string]bool{}
	queue := []Count{}
	queue = append(queue, Count{start, 1})
	visited[start] = true
	for len(queue) > 0 {
		c := queue[0]
		queue = queue[1:]
		for i := 0; i < len(start); i++ {
			sb := []byte(c.str)
			sc := c.str[i]
			for cc := byte('a'); cc <= 'z'; cc++ {
				if cc == sc {
					continue
				}
				sb[i] = cc
				tmp := string(sb)
				if !visited[tmp] && dict[tmp] {
					if tmp == end {
						return c.count + 1
					}
					visited[tmp] = true
					queue = append(queue, Count{tmp, c.count + 1})
				}
			}
		}
	}
	return 0
}

// transform finds a word ladder allowing add/remove/change of one character.
func transform(startWord, stopWord string, dictionary map[string]bool) []string {
	startWord = strings.ToUpper(startWord)
	stopWord = strings.ToUpper(stopWord)
	actionQueue := []string{}
	visitedSet := map[string]bool{}
	backtrackMap := map[string]string{}
	actionQueue = append(actionQueue, startWord)
	visitedSet[startWord] = true
	for len(actionQueue) > 0 {
		w := actionQueue[0]
		actionQueue = actionQueue[1:]
		for _, v := range getOneEditWords(w) {
			if v == stopWord {
				list := []string{v}
				cur := w
				for {
					list = append([]string{cur}, list...)
					next, ok := backtrackMap[cur]
					if !ok {
						break
					}
					cur = next
				}
				return list
			}
			if dictionary[v] {
				if !visitedSet[v] {
					actionQueue = append(actionQueue, v)
					visitedSet[v] = true
					backtrackMap[v] = w
				}
			}
		}
	}
	return nil
}

func getOneEditWords(word string) []string {
	wordsSet := map[string]bool{}
	words := []string{}
	for i := 0; i < len(word); i++ {
		for c := byte('A'); c <= 'Z'; c++ {
			if c != word[i] {
				wordArray := []byte(word)
				wordArray[i] = c
				w := string(wordArray)
				if !wordsSet[w] {
					wordsSet[w] = true
					words = append(words, w)
				}
			}
		}
	}
	return words
}

// ValidWordAbbr builds an abbreviation dictionary.
func (si *StringImp) ValidWordAbbr(dictionary []string) {
	si.abbrDict = map[string]string{}
	si.uniqueDict = map[string]bool{}
	for _, word := range dictionary {
		if !si.uniqueDict[word] {
			abbr := getAbbr(word)
			if _, ok := si.abbrDict[abbr]; !ok {
				si.abbrDict[abbr] = word
			} else {
				si.abbrDict[abbr] = ""
			}
			si.uniqueDict[word] = true
		}
	}
}

func (si *StringImp) isUnique(word string) bool {
	if len(word) == 0 {
		return true
	}
	abbr := getAbbr(word)
	if v, ok := si.abbrDict[abbr]; !ok || v == word {
		return true
	}
	return false
}

func getAbbr(word string) string {
	if len(word) < 3 {
		return word
	}
	var sb strings.Builder
	sb.WriteByte(word[0])
	sb.WriteString(strconv.Itoa(len(word) - 2))
	sb.WriteByte(word[len(word)-1])
	return sb.String()
}

// WordFreq pairs a word with its frequency.
type WordFreq struct {
	word string
	freq int
}

// wordFreqHeap is a min-heap of *WordFreq ordered by freq.
type wordFreqHeap []*WordFreq

func (h wordFreqHeap) Len() int            { return len(h) }
func (h wordFreqHeap) Less(i, j int) bool  { return h[i].freq < h[j].freq }
func (h wordFreqHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *wordFreqHeap) Push(x interface{}) { *h = append(*h, x.(*WordFreq)) }
func (h *wordFreqHeap) Pop() interface{} {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[:n-1]
	return item
}

// findTopKFrequentWords prints the frequencies of the k most frequent words.
func (si *StringImp) findTopKFrequentWords(s []string, k int) {
	hash := map[string]int{}
	minHeap := &wordFreqHeap{}
	heap.Init(minHeap)
	for i := 0; i < len(s); i++ {
		hash[s[i]]++
	}
	count := 0
	for word, freq := range hash {
		if count < k {
			heap.Push(minHeap, &WordFreq{word, freq})
			count++
		} else if minHeap.Len() > 0 && freq > (*minHeap)[0].freq {
			heap.Pop(minHeap)
			heap.Push(minHeap, &WordFreq{word, freq})
		}
	}
	for minHeap.Len() > 0 {
		wf := heap.Pop(minHeap).(*WordFreq)
		fmt.Println(hash[wf.word])
	}
}

// naturalOrderCompare compares two strings in natural (numeric-aware) order.
func naturalOrderCompare(o1, o2 string) int {
	for i := 0; i < len(o1) && i < len(o2); i++ {
		if isDigit(o1[i]) || isDigit(o2[i]) {
			dig1, dig2 := "", ""
			for x := i; x < len(o1) && isDigit(o1[i]); x++ {
				dig1 += string(o1[x])
			}
			for x := i; x < len(o2) && isDigit(o2[i]); x++ {
				dig2 += string(o2[x])
			}
			if dig2 == "" || parseIntSafe(dig1) < parseIntSafe(dig2) {
				return -1
			}
			if dig1 == "" || parseIntSafe(dig1) > parseIntSafe(dig2) {
				return 1
			}
		}
		if o1[i] < o2[i] {
			return -1
		}
		if o1[i] > o2[i] {
			return 1
		}
	}
	return 0
}
