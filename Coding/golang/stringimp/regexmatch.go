package main

import (
	"strconv"
	"strings"
)

// matchRegex implements regex matching with '.' and '*' via DP. O(M*N).
func matchRegex(s, p string) bool {
	dp := make([][]bool, len(s)+1)
	for i := range dp {
		dp[i] = make([]bool, len(p)+1)
	}
	dp[0][0] = true
	for i := 0; i < len(p); i++ {
		if p[i] == '*' && i >= 1 && dp[0][i-1] {
			dp[0][i+1] = true
		}
	}
	for i := 1; i <= len(s); i++ {
		for j := 1; j <= len(p); j++ {
			if p[j-1] == '.' || p[j-1] == s[i-1] {
				dp[i][j] = dp[i-1][j-1]
			}
			if p[j-1] == '*' {
				if j >= 2 && p[j-2] != s[i-1] && p[j-2] != '.' {
					dp[i][j] = dp[i][j-2]
				} else if j >= 2 {
					dp[i][j] = dp[i][j-1] || dp[i][j-2] || dp[i-1][j]
				}
			}
		}
	}
	return dp[len(s)][len(p)]
}

// isMatch1 implements regex matching with '*' (zero+), '.' (any) and '+' (one+).
func isMatch1(s, p string) bool {
	if len(p) == 0 {
		return len(s) == 0
	}
	if len(p) == 1 {
		if len(s) < 1 {
			return false
		} else if p[0] != s[0] && p[0] != '.' {
			return false
		}
		return isMatch1(s[1:], p[1:])
	}
	if p[1] != '*' && p[1] != '+' {
		if len(s) < 1 {
			return false
		}
		if p[0] != s[0] && p[0] != '.' {
			return false
		}
		return isMatch1(s[1:], p[1:])
	} else if p[1] == '*' {
		if isMatch1(s, p[2:]) {
			return true
		}
		i := 0
		for i < len(s) && (s[i] == p[0] || p[0] == '.') {
			if isMatch1(s[i+1:], p[2:]) {
				return true
			}
			i++
		}
		return false
	} else if p[1] == '+' {
		i := 0
		for i < len(s) && (s[i] == p[0] || p[0] == '.') {
			if isMatch1(s[i+1:], p[2:]) {
				return true
			}
			i++
		}
		return false
	}
	return false
}

// WildCardcomparison implements wildcard matching with '?' and '*'.
func WildCardcomparison(str, pattern string) bool {
	s, p, starIdx := 0, 0, -1
	for s < len(str) {
		if p < len(pattern) && (pattern[p] == '?' || str[s] == pattern[p]) {
			s++
			p++
		} else if p < len(pattern) && pattern[p] == '*' {
			starIdx = p
			p++
		} else if starIdx != -1 {
			s++
		} else {
			return false
		}
	}
	for p < len(pattern) && pattern[p] == '*' {
		p++
	}
	return p == len(pattern)
}

// splitText splits a message into annotated chunks without cutting words.
func splitText(message string, charLimit int) []string {
	return splitTextAuxUsingSplit(message, charLimit)
}

func splitTextAuxUsingSplit(message string, charLimitOriginal int) []string {
	// Reserve room for the chunk suffix like (1/3).
	charLimit := charLimitOriginal - 5
	result := []string{}
	splitted := strings.Split(message, " ")
	var temp string
	for i := 0; i < len(splitted)-1; i++ {
		temp = splitted[i]
		for i+1 < len(splitted)-1 && len(temp+"1"+splitted[i+1]) <= charLimit {
			temp = temp + " " + splitted[i+1]
			i++
		}
		result = append(result, temp)
	}
	if len(result) == 0 {
		return result
	}
	lastElement := result[len(result)-1]
	if len(lastElement)+1+len(splitted[len(splitted)-1]) < charLimit {
		result[len(result)-1] = lastElement + " " + splitted[len(splitted)-1]
	} else {
		result = append(result, splitted[len(splitted)-1])
	}
	resultSize := len(result)
	for i := 0; i < resultSize; i++ {
		result[i] = result[i] + "(" + strconv.Itoa(i+1) + "/" + strconv.Itoa(resultSize) + ")"
	}
	return result
}

// decodeCSV parses a CSV line honoring quoted fields.
func (si *StringImp) decodeCSV(s string) []string {
	if len(s) == 0 {
		return nil
	}
	result := []string{}
	inQuotes := false
	var sb strings.Builder
	for i := 0; i < len(s); i++ {
		value := s[i]
		if inQuotes {
			if value == '"' {
				if i == len(s)-1 {
					result = append(result, sb.String())
					return result
				} else if s[i+1] == '"' {
					sb.WriteByte('"')
					i++
				} else {
					result = append(result, sb.String())
					sb.Reset()
					inQuotes = false
					i++
				}
			} else {
				sb.WriteByte(value)
			}
		} else if value == '"' {
			inQuotes = true
		} else if value == ',' {
			result = append(result, sb.String())
			sb.Reset()
		} else {
			sb.WriteByte(value)
		}
	}
	result = append(result, sb.String())
	return result
}

// decodeFindHelper tries lower/upper case combinations to decode a string.
// Returns (value, true) on success.
func decodeFindHelper(start int, curr *[]byte, badEncString string) (int, bool) {
	if start == len(badEncString) {
		return decodeString(string(*curr))
	}
	c := badEncString[start]
	if !isLetter(c) {
		*curr = append(*curr, c)
		if result, ok := decodeFindHelper(start+1, curr, badEncString); ok {
			return result, true
		}
		*curr = (*curr)[:len(*curr)-1]
	} else {
		lower := toLowerByte(c)
		*curr = append(*curr, lower)
		if result, ok := decodeFindHelper(start+1, curr, badEncString); ok {
			return result, true
		}
		*curr = (*curr)[:len(*curr)-1]
		upper := toUpperByte(c)
		*curr = append(*curr, upper)
		if result, ok := decodeFindHelper(start+1, curr, badEncString); ok {
			return result, true
		}
		*curr = (*curr)[:len(*curr)-1]
	}
	return 0, false
}

func decodeString(testEncStr string) (int, bool) {
	truth := "kljJJ324hijkS_"
	if testEncStr == truth {
		return 848662, true
	}
	return 0, false
}

// removeKdigits removes k digits to make the smallest possible number.
func (si *StringImp) removeKdigits(num string, k int) string {
	digits := len(num) - k
	stk := make([]byte, len(num))
	top := 0
	for i := 0; i < len(num); i++ {
		c := num[i]
		for top > 0 && stk[top-1] > c && k > 0 {
			top--
			k--
		}
		stk[top] = c
		top++
	}
	idx := 0
	for idx < digits && stk[idx] == '0' {
		idx++
	}
	if idx == digits {
		return "0"
	}
	return string(stk[idx:digits])
}
