package main

import (
	"fmt"
	"strings"
)

// displayPages displays entries paginated by host id (max 12 per page).
func displayPages(input []string) {
	if len(input) == 0 {
		return
	}
	visited := map[string]bool{}
	pageNum := 1
	fmt.Println("Page", pageNum)
	idx := 0
	for idx < len(input) {
		curr := input[idx]
		hostId := strings.Split(curr, ",")[0]
		removed := false
		if !visited[hostId] {
			fmt.Println(curr)
			visited[hostId] = true
			input = append(input[:idx], input[idx+1:]...)
			removed = true
		}
		if !removed {
			idx++
		}
		if len(visited) == 12 || idx >= len(input) {
			visited = map[string]bool{}
			idx = 0
			if len(input) > 0 {
				pageNum++
				fmt.Println("Page", pageNum)
			} else {
				break
			}
		}
	}
}

// ---------------------------------------------------------------------------
// Boggle (word search II) with a Trie.
// ---------------------------------------------------------------------------

// TrieNode1 is the trie node used by Boggle.
type TrieNode1 struct {
	next [26]*TrieNode1
	word string
}

// Boggle finds all dictionary words on a board.
type Boggle struct{}

func (b *Boggle) buildTrie(words []string) *TrieNode1 {
	root := &TrieNode1{}
	for _, w := range words {
		p := root
		for i := 0; i < len(w); i++ {
			idx := w[i] - 'a'
			if p.next[idx] == nil {
				p.next[idx] = &TrieNode1{}
			}
			p = p.next[idx]
		}
		p.word = w
	}
	return root
}

func (b *Boggle) findWords(board [][]byte, words []string) []string {
	res := []string{}
	root := b.buildTrie(words)
	for i := 0; i < len(board); i++ {
		for j := 0; j < len(board[0]); j++ {
			b.dfs(board, i, j, root, &res)
		}
	}
	return res
}

func (b *Boggle) dfs(board [][]byte, i, j int, p *TrieNode1, res *[]string) {
	c := board[i][j]
	if c == '#' || p.next[c-'a'] == nil {
		return
	}
	p = p.next[c-'a']
	if p.word != "" {
		*res = append(*res, p.word)
		p.word = "" // de-duplicate
	}
	board[i][j] = '#'
	if i > 0 {
		b.dfs(board, i-1, j, p, res)
	}
	if j > 0 {
		b.dfs(board, i, j-1, p, res)
	}
	if i < len(board)-1 {
		b.dfs(board, i+1, j, p, res)
	}
	if j < len(board[0])-1 {
		b.dfs(board, i, j+1, p, res)
	}
	board[i][j] = c
}

// ---------------------------------------------------------------------------
// Boggle with Trie + DP (uses package-level root/board to mirror Java statics).
// ---------------------------------------------------------------------------

var boggleDictRoot *DictNode
var boggleBoard [][]byte

// DictNode is the trie node for the DP boggle variant.
type DictNode struct {
	letter    byte
	nextNodes [26]*DictNode
	wordEnd   bool
}

func newDictNode(letter byte) *DictNode {
	return &DictNode{letter: letter}
}

func (d *DictNode) insert(word string) {
	node := boggleDictRoot
	letters := []byte(word)
	for i := 0; i < len(letters); i++ {
		if node.nextNodes[letters[i]-'a'] == nil {
			node.nextNodes[letters[i]-'a'] = newDictNode(letters[i])
			if i == len(letters)-1 {
				node.nextNodes[letters[i]-'a'].wordEnd = true
			}
		}
		node = node.nextNodes[letters[i]-'a']
	}
}

func (d *DictNode) contains(word string) bool {
	node := boggleDictRoot
	letters := []byte(word)
	i := 0
	for i < len(letters) && node.nextNodes[letters[i]-'a'] != nil {
		node = node.nextNodes[letters[i]-'a']
		i++
	}
	return i == len(letters) && node.wordEnd
}

func boggleTrieDynamic(node *DictNode, currentBranch []byte, currentHeight int) {
	if node == nil {
		return
	}
	if node.wordEnd && currentHeight > 3 {
		word := string(currentBranch[:currentHeight-1])
		if isInBoard(boggleBoard, word) {
			fmt.Println(word)
		}
	}
	for i := 0; i < len(node.nextNodes); i++ {
		if node.nextNodes[i] != nil {
			currentBranch[currentHeight] = byte(i + 'a')
			boggleTrieDynamic(node.nextNodes[i], currentBranch, currentHeight+1)
		}
	}
}

func isInBoard(board [][]byte, word string) bool {
	M := len(board)
	N := len(board[0])
	dx := []int{1, 1, 0, -1, -1, -1, 0, 1}
	dy := []int{0, 1, 1, 1, 0, -1, -1, -1}
	visited := make([][]bool, M)
	for i := range visited {
		visited[i] = make([]bool, N)
	}
	letters := []byte(word)
	dp := make([][][]bool, len(letters))
	for k := range dp {
		dp[k] = make([][]bool, M)
		for i := range dp[k] {
			dp[k][i] = make([]bool, N)
		}
	}
	for k := 0; k < len(letters); k++ {
		for i := 0; i < M; i++ {
			for j := 0; j < N; j++ {
				if k == 0 {
					dp[k][i][j] = true
				} else if !visited[i][j] && dp[k-1][i][j] {
					for l := 0; l < 8; l++ {
						x := i + dx[l]
						y := j + dy[l]
						if x >= 0 && x < M && y >= 0 && y < N && dp[k-1][x][y] && board[i][j] == letters[k] {
							dp[k][i][j] = true
							visited[x][y] = true
							if k == len(letters)-1 {
								return true
							}
						}
					}
				}
			}
		}
	}
	return false
}

// ---------------------------------------------------------------------------
// Tiny URL.
// ---------------------------------------------------------------------------

const tinyURLAlphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
const tinyURLBase = len(tinyURLAlphabet)

// encodeTinyURL converts an integer id to a short string (Java encode(int)).
func encodeTinyURL(num int) string {
	var sb strings.Builder
	for num > 0 {
		sb.WriteByte(tinyURLAlphabet[num%tinyURLBase])
		num /= tinyURLBase
	}
	return sb.String()
}

// decode1 converts a short string back to its integer id.
func decode1(str string) int {
	num := 0
	for i := len(str) - 1; i >= 0; i-- {
		num = num*tinyURLBase + strings.IndexByte(tinyURLAlphabet, str[i])
	}
	return num
}

// numberCanFit returns how many words fit in row x col by stringing them together.
func numberCanFit(words []string, row, col int) int {
	wordCount := 0
	rowIterator := 0
	wordIterator := 0
	for rowIterator < row {
		remainingCol := col
		for remainingCol > 0 && len(words[wordIterator]) <= remainingCol {
			wordCount++
			remainingCol = remainingCol - len(words[wordIterator]) - 1
			wordIterator++
			if wordIterator == len(words) {
				wordIterator = 0
			}
		}
		rowIterator++
	}
	return wordCount
}

// getCamelCaseMatchingStrings returns class names matching a CamelCase pattern.
func getCamelCaseMatchingStrings(list []string, pattern string) []string {
	patternList := []string{}
	for i := 0; i < len(list); i++ {
		s := list[i]
		length := 0
		patternLen := len(pattern) - 1
		patIndex := 0
		for length != len(s)-1 && patIndex <= patternLen {
			if s[length] == pattern[patIndex] {
				length++
				if patIndex == patternLen {
					patternList = append(patternList, s)
					break
				}
				patIndex++
				continue
			} else if !(pattern[patIndex] >= 'A' && pattern[patIndex] <= 'Z') {
				break
			}
			length++
		}
	}
	return patternList
}

// printNonOverlapping prints non-overlapping in-order groupings of a number.
func printNonOverlapping(number, prefix string) {
	fmt.Println(prefix + "(" + number + ")")
	for i := 1; i < len(number); i++ {
		newPrefix := prefix + "(" + number[0:i] + ")"
		printNonOverlapping(number[i:len(number)], newPrefix)
	}
}

// findLongestParanthesisLen returns the length of the longest valid parenthesis
// substring.
func findLongestParanthesisLen(str string) int {
	cnt := 0
	ans := 0
	maxLen := 0
	for i := 0; i < len(str); i++ {
		if str[i] == '(' {
			cnt++
		} else {
			if cnt <= 0 {
				maxLen = maxInt(maxLen, ans)
				cnt = 0
				ans = 0
			} else {
				cnt--
				ans += 2
			}
		}
	}
	if cnt >= 0 {
		maxLen = maxInt(maxLen, ans)
	}
	return maxLen
}

// isOrderingStringPresent returns true if ordering's relative order holds in s.
func isOrderingStringPresent(s, ordering string) bool {
	label := make([]int, 256)
	order := 1
	for i := 0; i < len(ordering); i++ {
		label[ordering[i]] = order
		order++
	}
	last := 0
	for i := 0; i < len(s); i++ {
		if label[s[i]] > 0 {
			if label[s[i]] < last {
				return false
			}
			last = label[s[i]]
		}
	}
	return true
}

// ransomNote1 checks if note can be built from mag (single pass over mag).
func ransomNote1(note, mag string) bool {
	count := make([]int, 256)
	for i := 0; i < len(mag); i++ {
		count[mag[i]]++
	}
	for j := 0; j < len(note); j++ {
		count[note[j]]--
		if count[note[j]] < 0 {
			return false
		}
	}
	return true
}

// ransomNote2 scans note and magazine simultaneously.
func ransomNote2(str, pattern string) bool {
	count := make([]int, 256)
	n := 0
	m := 0
	for n < len(str) {
		nchar := str[n]
		if count[nchar] > 0 {
			count[nchar]--
			n++
		} else {
			for m < len(pattern) && pattern[m] != nchar {
				mchar := pattern[m]
				count[mchar]++
				m++
			}
			if m >= len(pattern) {
				return false
			}
			n++
			m++
		}
	}
	return true
}

// Token represents a value or operator token for evalExpr.
type Token struct {
	typ   string
	value float64
}

// evalExpr evaluates an expression token list honoring * / precedence over + -.
func evalExpr(tokenList []Token) float64 {
	i := 0
	left := tokenList[i].value
	i++
	for i < len(tokenList) {
		operator := tokenList[i].typ
		i++
		right := tokenList[i].value
		i++
		switch operator {
		case "*":
			left = left * right
		case "/":
			left = left / right
		case "+", "-":
			for i < len(tokenList) {
				operator2 := tokenList[i].typ
				i++
				if operator2 == "+" || operator2 == "-" {
					i--
					break
				}
				if operator2 == "*" {
					right = right * tokenList[i].value
					i++
				}
				if operator2 == "/" {
					right = right / tokenList[i].value
					i++
				}
			}
			if operator == "+" {
				left = left + right
			} else {
				left = left - right
			}
		}
	}
	return left
}
