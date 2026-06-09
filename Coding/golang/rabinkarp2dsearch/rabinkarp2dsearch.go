package main

import "fmt"

/*
Given a 2D array of digits, find the occurrence of a given 2D pattern of digits.
For example, consider the following 2D matrix:

	1234567890
	0987654321
	1111111111
	1111111111
	2222222222

Look for the following 2D pattern:

	876543
	111111
	111111
*/

// MODULUS is a large prime (Integer.MAX_VALUE).
const MODULUS int64 = 2147483647

// RADIX is the radix of the alphabet (assumes ASCII characters).
const RADIX int64 = 256

// RabinKarp2DSearch performs 2D Rabin-Karp pattern matching over a char matrix.
type RabinKarp2DSearch struct {
	// factors holds powers of RADIX (factors[i] == RADIX^i mod MODULUS), used to
	// update the rolling hash when the pattern window is shifted.
	factors     []int64
	height      int
	pattern     [][]byte
	patternHash int64
	width       int
}

// NewRabinKarp2DSearch builds the searcher for the given pattern.
func NewRabinKarp2DSearch(pattern [][]byte) *RabinKarp2DSearch {
	r := &RabinKarp2DSearch{pattern: pattern}
	r.height = len(pattern)
	r.width = len(pattern[0])
	r.factors = make([]int64, (r.height-1)+(r.width-1)+1)
	r.factors[0] = 1
	for i := 1; i < len(r.factors); i++ {
		r.factors[i] = (RADIX * r.factors[i-1]) % MODULUS
	}
	r.patternHash = r.hash(pattern)
	return r
}

// check returns true if pattern matches text at position i, j.
func (r *RabinKarp2DSearch) check(text [][]byte, i, j int) bool {
	x, y := i, j
	for a := 0; a < r.height; a++ {
		for b := 0; b < r.width; b++ {
			if text[x][y] != r.pattern[a][b] {
				return false
			}
			y++
		}
		x++
		y = j
	}
	return true
}

// getFactors returns powers of RADIX, modulo MODULUS.
func (r *RabinKarp2DSearch) getFactors() []int64 {
	return r.factors
}

// hash computes (from scratch) the hash of the upper-left height*width block of data.
func (r *RabinKarp2DSearch) hash(data [][]byte) int64 {
	var result int64
	for i := 0; i < r.height; i++ {
		var rowHash int64
		for j := 0; j < r.width; j++ {
			rowHash = (RADIX*rowHash + int64(data[i][j])) % MODULUS
		}
		result = (RADIX*result + rowHash) % MODULUS
	}
	return result
}

// search returns [i, j] coordinates of a match of pattern in text, or nil if none.
func (r *RabinKarp2DSearch) search(text [][]byte) []int {
	rowStartHash := r.hash(text)
	hash := rowStartHash
	for i := 0; i <= len(text)-r.height-1; i++ { // -1 added by the reference
		if hash == r.patternHash && r.check(text, i, 0) {
			return []int{i, 0}
		}
		for j := 0; j < len(text[0])-r.width; j++ {
			hash = r.shiftRight(hash, text, i, j)
			if hash == r.patternHash && r.check(text, i, j+1) {
				return []int{i, j + 1}
			}
		}
		rowStartHash = r.shiftDown(rowStartHash, text, i)
		hash = rowStartHash
	}
	return nil
}

// shiftDown returns the hash of the block at i+1, j given the hash of the block at i, j.
func (r *RabinKarp2DSearch) shiftDown(hash int64, text [][]byte, i int) int64 {
	// compute the hash of row i
	var xi int64
	for j := 0; j < r.width; j++ {
		xi = (RADIX*xi + int64(text[i][j])) % MODULUS
	}
	// shift the hash of row i out of the hash of the block
	hash = (hash + MODULUS - r.factors[r.width-1]*xi) % MODULUS
	// add the hash of row i+height to the hash of the block
	var x int64
	for j := 0; j < r.width; j++ {
		x = (RADIX*x + int64(text[i+r.height][j])) % MODULUS
	}
	hash = (hash*RADIX + x) % MODULUS
	return hash
}

// shiftRight returns the hash of the block at i, j+1 given the hash of the block at i, j.
func (r *RabinKarp2DSearch) shiftRight(hash int64, text [][]byte, i, j int) int64 {
	result := hash
	degree := r.height + r.width - 2 // the exponent to keep track of

	// subtract first column
	var xi int64
	for offset := 0; offset < r.height; offset++ {
		xi = (xi + int64(text[i+offset][j])*r.factors[degree]) % MODULUS
		degree--
	}

	result = (result + MODULUS - xi) % MODULUS
	// multiply by RADIX
	result *= RADIX

	var x int64
	for k := 0; k < r.height; k++ {
		x = (RADIX*x + int64(text[i+k][j+r.width])) % MODULUS
	}
	result = (result + x) % MODULUS
	return result
}

// toMatrix converts rows of equal-length strings into a char matrix.
func toMatrix(rows []string) [][]byte {
	m := make([][]byte, len(rows))
	for i, row := range rows {
		m[i] = []byte(row)
	}
	return m
}

func main() {
	text := toMatrix([]string{
		"1234567890",
		"0987654321",
		"1111111111",
		"1111111111",
		"2222222222",
	})
	pattern := toMatrix([]string{
		"876543",
		"111111",
		"111111",
	})

	rk := NewRabinKarp2DSearch(pattern)
	result := rk.search(text)
	if result == nil {
		fmt.Println("pattern not found")
	} else {
		fmt.Printf("pattern found at [%d, %d]\n", result[0], result[1])
	}
}
