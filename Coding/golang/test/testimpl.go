package main

// Ported from Coding/java/test.java (original package code.ds).
// NOTE: file is intentionally named testimpl.go (NOT *_test.go) so Go does not
// treat it as a test file.

import (
	"fmt"
	"math"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

// static List<List<Integer>> data; (declared but unused in the original)
var data [][]int

func main() {
	fmt.Println(countUniqueWords("Java is great. Grails is also great"))
	printUniquedWords("Java is great. Grails is also great")
}

// print builds a 10x10 grid of right-padded numbers. (demo helper, not called in main)
func print(precision int) string {
	var builder strings.Builder
	for r := 0; r < 10; r++ {
		builder.WriteString("| ")
		for c := 0; c < 10; c++ {
			s := strconv.FormatFloat(1233424234, 'G', -1, 64)
			if len(s) < precision {
				for i := 0; i < precision-len(s); i++ {
					builder.WriteByte(' ')
				}
			}
			builder.WriteString(s)
			builder.WriteString("  ")
		}
		builder.WriteString("|\n")
	}
	return builder.String()
}

// iprange2cidrStr returns the minimum list of CIDR blocks covering [ipStart, ipEnd].
// http://stackoverflow.com/questions/5020317
func iprange2cidrStr(ipStart, ipEnd string) []string {
	start := ip2long(ipStart)
	end := ip2long(ipEnd)

	result := []string{}
	for end >= start {
		maxSize := 32
		for maxSize > 0 {
			mask := iMask(maxSize - 1)
			maskBase := start & mask
			if maskBase != start {
				break
			}
			maxSize--
		}
		x := math.Log(float64(end-start+1)) / math.Log(2)
		maxDiff := 32 - int(math.Floor(x))
		if maxSize < maxDiff {
			maxSize = maxDiff
		}
		ip := long2ip(start)
		result = append(result, ip+"/"+strconv.Itoa(maxSize))
		start += int64(math.Pow(2, float64(32-maxSize)))
	}
	return result
}

// iprange2cidrLong is the long/long overload of iprange2cidr.
func iprange2cidrLong(start, end int64) []string {
	result := []string{}
	for end >= start {
		max := 32
		for max > 0 {
			mask := iMask(max - 1)
			maskBase := start & mask
			if maskBase != start {
				break
			}
			max--
		}
		x := math.Log(float64(end-start+1)) / math.Log(2)
		maxDiff := 32 - int(math.Floor(x))
		if max < maxDiff {
			max = maxDiff
		}
		ip := long2ip(start)
		result = append(result, ip+"/"+strconv.Itoa(max))
		start += int64(math.Pow(2, float64(32-max)))
	}
	return result
}

func iMask(s int) int64 {
	return int64(math.Round(math.Pow(2, 32) - math.Pow(2, float64(32-s))))
}

func ip2long(ipstring string) int64 {
	parts := strings.Split(ipstring, ".")
	var num int64 = 0
	var ip int64 = 0
	for x := 3; x >= 0; x-- {
		ip, _ = strconv.ParseInt(parts[3-x], 10, 64)
		num |= ip << (x << 3)
	}
	return num
}

func long2ip(longIP int64) string {
	var sb strings.Builder
	sb.WriteString(strconv.FormatInt(longIP>>24, 10))
	sb.WriteString(".")
	sb.WriteString(strconv.FormatInt((longIP&0x00FFFFFF)>>16, 10))
	sb.WriteString(".")
	sb.WriteString(strconv.FormatInt((longIP&0x0000FFFF)>>8, 10))
	sb.WriteString(".")
	sb.WriteString(strconv.FormatInt(longIP&0x000000FF, 10))
	return sb.String()
}

// pourWater simulates V units of water poured at index K. (demo helper)
func pourWater(heights []int, V, K int) []int {
	for i := 0; i < V; i++ {
		l, r, n := K, K, len(heights)
		for l > 0 && heights[l] >= heights[l-1] {
			l--
		}
		for l < K && heights[l] == heights[l+1] {
			l++
		}
		for r < n-1 && heights[r] >= heights[r+1] {
			r++
		}
		for r > K && heights[r] == heights[r-1] {
			r--
		}
		if heights[l] < heights[K] {
			heights[l]++
		} else {
			heights[r]++
		}
	}
	return heights
}

// countUniqueWords counts words (split on spaces) that occur exactly once.
func countUniqueWords(str string) int {
	m := map[string]int{}
	words := strings.Split(str, " ")
	count := 0
	for _, wrd := range words {
		m[wrd]++
	}
	for _, value := range m {
		if value == 1 {
			count++
		}
	}
	return count
}

// printUniquedWords prints alphabetic words (regex [a-zA-Z]+) that occur exactly once.
func printUniquedWords(str string) {
	p := regexp.MustCompile("[a-zA-Z]+")
	matches := p.FindAllString(str, -1)

	hm := map[string]int{}
	for _, word := range matches {
		hm[word]++
	}

	keys := make([]string, 0, len(hm))
	for w := range hm {
		keys = append(keys, w)
	}
	sort.Strings(keys)
	for _, w := range keys {
		if hm[w] == 1 {
			fmt.Println(w)
		}
	}
}
