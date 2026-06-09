// Package main is an idiomatic Go port of the Java reference file StringImp.java
// (originally package code.ds). It collects a large number of string / DSA
// interview implementations. Java static methods become package-level functions,
// instance methods become methods on the StringImp struct, and inner classes
// become standalone structs.
package main

import (
	"container/list"
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

// StringImp holds the small amount of per-instance state that the original
// Java instance methods relied on.
type StringImp struct {
	wordBreakMemo      map[string][]string // Java field `map` for wordBreakII/III
	wordDistMap        map[string][]int    // Java `_map` for WordDistanceFinder
	abbrDict           map[string]string   // ValidWordAbbr
	uniqueDict         map[string]bool     // ValidWordAbbr
	buffer             []byte              // readII state
	offset             int                 // readII state
	charactersInBuffer int                 // readII state
}

// Pair is a small helper type to replace Java's Pair / Map.Entry usages.
type Pair struct {
	First, Second int
}

// ---------------------------------------------------------------------------
// Shared helpers (defined ONCE for the whole package).
// ---------------------------------------------------------------------------

func isDigit(c byte) bool { return c >= '0' && c <= '9' }

func isLetter(c byte) bool {
	return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
}

func isLetterOrDigit(c byte) bool { return isLetter(c) || isDigit(c) }

func toLowerByte(c byte) byte {
	if c >= 'A' && c <= 'Z' {
		return c + 32
	}
	return c
}

func toUpperByte(c byte) byte {
	if c >= 'a' && c <= 'z' {
		return c - 32
	}
	return c
}

// getNumericValue mimics Java's Character.getNumericValue for the ASCII range.
func getNumericValue(c byte) int {
	if c >= '0' && c <= '9' {
		return int(c - '0')
	}
	if c >= 'a' && c <= 'z' {
		return int(c-'a') + 10
	}
	if c >= 'A' && c <= 'Z' {
		return int(c-'A') + 10
	}
	return -1
}

// parseIntSafe returns 0 on error instead of panicking (Java would throw).
func parseIntSafe(s string) int {
	n, err := strconv.Atoi(strings.TrimSpace(s))
	if err != nil {
		return 0
	}
	return n
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func maxInt(a, b int) int {
	if a > b {
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

// reverseStringGo reverses an ASCII string (replaces Java's XOR ReverseString and
// StringBuilder.reverse()).
func reverseStringGo(s string) string {
	b := []byte(s)
	for i, j := 0, len(b)-1; i < j; i, j = i+1, j-1 {
		b[i], b[j] = b[j], b[i]
	}
	return string(b)
}

func indexOfByte(s []byte, b byte) int {
	for i, c := range s {
		if c == b {
			return i
		}
	}
	return -1
}

// ---------------------------------------------------------------------------
// main: port of the Java public static void main(...) demo.
// ---------------------------------------------------------------------------

func main() {
	strs := []string{"apple7", "apple01", "pear07", "peach01", "apple10",
		"apple0002", "zzz000", "appl9"}
	sort.SliceStable(strs, func(i, j int) bool {
		return naturalOrderCompare(strs[i], strs[j]) < 0
	})
	fmt.Println("Sorted:", strs)
}

// ---------------------------------------------------------------------------
// Compression / encoding.
// ---------------------------------------------------------------------------

// compressString compresses a given string. Input: aaaaabbccc Output: a5b2c3
// Time = O(n) space O(n).
func compressString(s string) string {
	if len(s) < 3 {
		return s
	}
	var sb strings.Builder
	for i := 0; i < len(s); i++ {
		sb.WriteByte(s[i])
		count := 1
		for i+1 < len(s) && s[i+1] == s[i] {
			i++
			count++
		}
		sb.WriteString(strconv.Itoa(count))
	}
	if sb.Len() >= len(s) {
		return s
	}
	return sb.String()
}

// compressInPlace compresses in place. Time = O(n) space O(1).
func compressInPlace(chars []byte) string {
	j := 0
	cnt := 1
	for i := 1; i <= len(chars); i++ {
		if i < len(chars) && chars[i] == chars[i-1] {
			cnt++
		} else {
			chars[j] = chars[i-1]
			j++
			if cnt != 1 {
				for _, c := range []byte(strconv.Itoa(cnt)) {
					chars[j] = c
					j++
				}
				cnt = 1
			}
		}
	}
	return string(chars[:j])
}

// encodeRLE: input = aabcccccaaa output = ab5c3a (Java encode(String)).
func encodeRLE(source string) string {
	var dest strings.Builder
	for i := 0; i < len(source); i++ {
		runLength := 1
		for i+1 < len(source) && source[i] == source[i+1] {
			runLength++
			i++
		}
		if runLength >= 3 {
			dest.WriteString(strconv.Itoa(runLength))
		}
		dest.WriteByte(source[i])
	}
	return dest.String()
}

// decode reverses encodeRLE-style strings using a regex tokenizer.
func decode(source string) string {
	var dest strings.Builder
	pattern := regexp.MustCompile(`[0-9]+|[a-zA-Z]`)
	matches := pattern.FindAllString(source, -1)
	i := 0
	for i < len(matches) {
		number := parseIntSafe(matches[i])
		i++
		if i < len(matches) {
			ch := matches[i]
			i++
			for n := 0; n < number; n++ {
				dest.WriteString(ch)
			}
		}
	}
	return dest.String()
}

// ---------------------------------------------------------------------------
// Character frequency.
// ---------------------------------------------------------------------------

// getFirstNotRepeatedChar finds first non repeated character in one pass over
// flags. Returns (char, true) or (0, false).
func getFirstNotRepeatedChar(input string) (byte, bool) {
	flags := make([]int, 256)
	for i := 0; i < len(input); i++ {
		flags[input[i]]++
	}
	for i := 0; i < len(flags); i++ {
		if flags[i] == 1 {
			if i < len(input) {
				return input[i], true
			}
		}
	}
	return 0, false
}

func firstNonRepeatingChar(word string) byte {
	repeating := map[byte]bool{}
	nonrepeating := []byte{}
	for i := 0; i < len(word); i++ {
		letter := word[i]
		if repeating[letter] {
			continue
		}
		if idx := indexOfByte(nonrepeating, letter); idx >= 0 {
			nonrepeating = append(nonrepeating[:idx], nonrepeating[idx+1:]...)
			repeating[letter] = true
		} else {
			nonrepeating = append(nonrepeating, letter)
		}
	}
	if len(nonrepeating) == 0 {
		return 0
	}
	return nonrepeating[0]
}

// streamNonRepeatingChar finds first non repeating character in a stream using a
// doubly linked list plus a map for O(1) deletion.
type streamNonRepeatingChar struct {
	lst     *list.List
	elemMap map[byte]*list.Element
	set     map[byte]bool // chars seen more than once
}

func newStreamNonRepeatingChar() *streamNonRepeatingChar {
	return &streamNonRepeatingChar{
		lst:     list.New(),
		elemMap: map[byte]*list.Element{},
		set:     map[byte]bool{},
	}
}

func (s *streamNonRepeatingChar) insert(c byte) {
	if s.set[c] {
		return
	}
	if e, ok := s.elemMap[c]; ok {
		s.lst.Remove(e)
		delete(s.elemMap, c)
		s.set[c] = true
	} else {
		s.elemMap[c] = s.lst.PushBack(c)
	}
}

func (s *streamNonRepeatingChar) getNonRepeating() byte {
	return s.lst.Back().Value.(byte)
}

// findMostFrequent returns the maximum occurring character in the input string.
func (si *StringImp) findMostFrequent(s string) byte {
	m := map[byte]int{}
	count := 0
	var res byte = ' '
	for i := 0; i < len(s); i++ {
		c := s[i]
		// Java called Character.toLowerCase(c) here but discarded the result (no-op).
		if !isLetterOrDigit(c) {
			continue
		}
		if c == ' ' {
			continue
		}
		m[c]++
		if m[c] > count {
			count = m[c]
			res = c
		}
	}
	return res
}

// getSecondMostChar returns the 2nd most frequently occurring char.
func getSecondMostChar(s string) byte {
	count := make([]int, 256)
	for i := 0; i < len(s); i++ {
		count[s[i]]++
	}
	largest, second := 0, 0
	for i := 0; i < 256; i++ {
		if count[i] > count[largest] {
			second = largest
			largest = i
		} else if count[i] > count[second] && count[i] != count[largest] {
			second = i
		}
	}
	return byte(second)
}

// ---------------------------------------------------------------------------
// Bracket / parenthesis validation.
// ---------------------------------------------------------------------------

// isRedudantExpresssion detects duplicate parenthesis in a balanced expression.
func isRedudantExpresssion(s string) bool {
	stack := []byte{}
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c == ')' {
			top := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			if top == '(' {
				return true
			}
			for top != '(' {
				top = stack[len(stack)-1]
				stack = stack[:len(stack)-1]
			}
		} else {
			stack = append(stack, c)
		}
	}
	return false
}

// isBalanced determines if all delimiters in an expression are matched/closed.
func isBalanced(input string) bool {
	stack := []byte{}
	for i := 0; i < len(input); i++ {
		c := input[i]
		if isOpeningBracket(c) {
			stack = append(stack, c)
		} else if isClosingBracket(c) {
			if len(stack) == 0 {
				return false
			}
			top := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			if !isMatchingBrackets(top, c) {
				return false
			}
		}
	}
	return len(stack) == 0
}

func isOpeningBracket(c byte) bool { return strings.IndexByte("({[", c) > -1 }

func isClosingBracket(c byte) bool { return strings.IndexByte(")}]", c) > -1 }

func isMatchingBrackets(opening, closing byte) bool {
	switch opening {
	case '(':
		return closing == ')'
	case '{':
		return closing == '}'
	case '[':
		return closing == ']'
	default:
		return false
	}
}
