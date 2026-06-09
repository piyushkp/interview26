package main

import (
	"fmt"
	"math"
)

const (
	intMax    = 2147483647
	matrixM   = 4
	matrixN   = 4
	matrixROW = 18 // from reference (declared but unused)
	matrixCOL = 20 // from reference (declared but unused)
	emptyRoom = intMax
	gateVal   = 0
)

// Point mirrors java.awt.Point.
type Point struct {
	x, y int
}

// Matrix is the receiver type for the ported instance methods.
type Matrix struct{}

// KadaneResult holds the result of Kadane's max-subarray algorithm.
type KadaneResult struct {
	maxSum int
	start  int
	end    int
}

// Direction vectors used by search2D (all 8 directions).
var search2DX = []int{-1, -1, -1, 0, 0, 1, 1, 1}
var search2DY = []int{-1, 0, 1, -1, 1, -1, 0, 1}

// directions used by wallsAndGates (4-neighborhood).
var directions = [][]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}

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

func isDigitByte(b byte) bool {
	return b >= '0' && b <= '9'
}

func isWhitespaceByte(b byte) bool {
	return b == ' ' || b == '\t' || b == '\n' || b == '\r' || b == '\f' || b == '\v'
}

func main() {
	// Java built an unused `int[] in = {2,1,5,6,2,3};` (dropped: Go rejects
	// unused locals) and called printMatrix(5000). We use 24 to print the
	// documented 5x5 spiral demo instead of 5000 numbers.
	printMatrix(24)
}

// printMatrix prints integers 0..n laid out in an inward spiral.
func printMatrix(n int) {
	sqrt := math.Sqrt(float64(n + 1))
	k := int(sqrt)
	if math.Pow(sqrt, 2) != math.Pow(float64(k), 2) {
		k++
	}
	result := make([][]int, k)
	filled := make([][]bool, k)
	for i := range result {
		result[i] = make([]int, k)
		filled[i] = make([]bool, k)
	}
	top, bottom, left, right := 0, k-1, 0, k-1
	m := k * k
	flag := false
	for n >= 0 {
		for i := right; i >= left; i-- {
			if !flag && n+1 < m {
				m--
				continue
			}
			flag = true
			result[top][i] = n
			filled[top][i] = true
			n--
		}
		top++
		for i := top; i <= bottom; i++ {
			if !flag && n+1 < m {
				m--
				continue
			}
			flag = true
			result[i][left] = n
			filled[i][left] = true
			n--
		}
		left++
		for i := left; i <= right; i++ {
			if !flag && n+1 < m {
				m--
				continue
			}
			flag = true
			result[bottom][i] = n
			filled[bottom][i] = true
			n--
		}
		bottom--
		for i := bottom; i >= top; i-- {
			if !flag && n+1 < m {
				m--
				continue
			}
			flag = true
			result[i][right] = n
			filled[i][right] = true
			n--
		}
		right--
	}
	for i := 0; i < k; i++ {
		for j := 0; j < k; j++ {
			if filled[i][j] {
				fmt.Print(result[i][j], " ")
			}
		}
		fmt.Println()
	}
}

// spiralprint prints a 2D matrix in spiral order.
// e.g. {{1,2,3},{4,5,6},{7,8,9}} -> 1 2 3 6 9 8 7 4 5.
func spiralprint(matrix [][]int) {
	if matrix == nil || len(matrix) == 0 || len(matrix[0]) == 0 {
		return
	}
	left := 0
	right := len(matrix[0]) - 1
	up := 0
	down := len(matrix) - 1
	for left < right && up < down {
		for i := left; i <= right; i++ {
			fmt.Print(matrix[up][i], " ")
		}
		up++
		for i := up; i <= down; i++ {
			fmt.Print(matrix[i][right], " ")
		}
		right--
		for i := right; i >= left; i-- {
			fmt.Print(matrix[down][i], " ")
		}
		down--
		for i := down; i >= up; i-- {
			fmt.Print(matrix[i][left], " ")
		}
		left++
	}
}

// printMat prints a matrix along its anti-diagonals.
func printMat(mat [][]int) {
	if mat == nil || len(mat) == 0 {
		return
	}
	left, up := 0, 0
	down := len(mat) - 1
	right := len(mat[0]) - 1
	for i := down; i >= 0; i-- {
		x := i
		y := left
		for x <= down && y <= down {
			fmt.Print(mat[x][y], " ")
			x++
			y++
		}
		fmt.Println()
	}
	left++
	for i := left; i <= right; i++ {
		x := up
		y := i
		for x <= right && y <= right {
			fmt.Print(mat[x][y], " ")
			x++
			y++
		}
		fmt.Println()
	}
}

// rotatematrix shifts each element of the concentric rings by one position.
func (mt *Matrix) rotatematrix(mat [][]int) {
	up, left := 0, 0
	right := len(mat[0]) - 1
	down := len(mat) - 1
	var prev, curr int
	for up < down && left < right {
		if up+1 == down || left+1 == right {
			break
		}
		prev = mat[up+1][left]
		for i := left; i < right; i++ {
			curr = mat[up][i]
			mat[up][i] = prev
			prev = curr
		}
		up++
		for i := up; i < down; i++ {
			curr = mat[i][right-1]
			mat[i][right-1] = prev
			prev = curr
		}
		right--
		if up < down {
			for i := right - 1; i >= left; i-- {
				curr = mat[down-1][i]
				mat[down-1][i] = prev
				prev = curr
			}
		}
		down--
		if left < right {
			for i := down - 1; i >= up; i-- {
				curr = mat[i][left]
				mat[i][left] = prev
				prev = curr
			}
		}
		left++
	}
	for i := 0; i < len(mat); i++ {
		for j := 0; j < len(mat[0]); j++ {
			fmt.Print(mat[i][j], " ")
		}
		fmt.Println()
	}
}
