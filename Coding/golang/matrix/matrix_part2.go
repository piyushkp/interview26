package main

import "fmt"

// numIslands counts the number of islands (connected components of 1s) in a
// boolean grid via BFS. Time O(ROW x COL).
func numIslands(grid [][]int) int {
	row := len(grid)
	if row == 0 {
		return 0
	}
	col := len(grid[0])
	count := 0
	mark := make([][]bool, row)
	for i := range mark {
		mark[i] = make([]bool, col)
	}
	q := []Point{}
	for i := 0; i < row; i++ {
		for j := 0; j < col; j++ {
			if grid[i][j] == 1 && !mark[i][j] {
				q = append(q, Point{i, j})
				mark[i][j] = true
				for len(q) > 0 {
					temp := q[0]
					q = q[1:]
					x := temp.x
					y := temp.y
					if x+1 < row && grid[x+1][y] == 1 && !mark[x+1][y] {
						q = append(q, Point{x + 1, y})
						mark[x+1][y] = true
					}
					if y+1 < col && grid[x][y+1] == 1 && !mark[x][y+1] {
						q = append(q, Point{x, y + 1})
						mark[x][y+1] = true
					}
					if x-1 >= 0 && grid[x-1][y] == 1 && !mark[x-1][y] {
						q = append(q, Point{x - 1, y})
						mark[x-1][y] = true
					}
					if y-1 >= 0 && grid[x][y-1] == 1 && !mark[x][y-1] {
						q = append(q, Point{x, y - 1})
						mark[x][y-1] = true
					}
				}
				count++
			}
		}
	}
	return count
}

// preProcess fills aux[i][j] with the sum of mat from (0,0) to (i,j). Time O(MN).
func (mt *Matrix) preProcess(mat, aux [][]int, M, N int) {
	for i := 0; i < N; i++ {
		aux[0][i] = mat[0][i]
	}
	for i := 1; i < M; i++ {
		for j := 0; j < N; j++ {
			aux[i][j] = mat[i][j] + aux[i-1][j]
		}
	}
	for i := 0; i < M; i++ {
		for j := 1; j < N; j++ {
			aux[i][j] += aux[i][j-1]
		}
	}
}

// sumQuery returns the sum of the submatrix between (tli,tlj) and (rbi,rbj)
// in O(1) using the prefix-sum table aux. 
func (mt *Matrix) sumQuery(aux [][]int, tli, tlj, rbi, rbj int) int {
	res := aux[rbi][rbj]
	if tli > 0 {
		res = res - aux[tli-1][rbj]
	}
	if tlj > 0 {
		res = res - aux[rbi][tlj-1]
	}
	if tli > 0 && tlj > 0 {
		res = res + aux[tli-1][tlj-1]
	}
	return res
}

// numberOfPaths counts paths from (0,0) to (m,n) moving only right or down.
func (mt *Matrix) numberOfPaths(m, n int) int {
	count := make([][]int, m)
	for i := range count {
		count[i] = make([]int, n)
	}
	for i := 0; i < m; i++ {
		count[i][0] = 1
	}
	for j := 0; j < n; j++ {
		count[0][j] = 1
	}
	for i := 1; i < m; i++ {
		for j := 1; j < n; j++ {
			count[i][j] = count[i-1][j] + count[i][j-1]
		}
	}
	return count[m-1][n-1]
}

// rotate rotates an NxN image by 90 degrees clockwise in place. Time O(n^2).
func rotate(matrix [][]int, n int) {
	for layer := 0; layer < n/2; layer++ {
		first := layer
		last := n - 1 - layer
		for i := first; i < last; i++ {
			offset := i - first
			top := matrix[first][i] // save top
			matrix[first][i] = matrix[last-offset][first]
			matrix[last-offset][first] = matrix[last][last-offset]
			matrix[last][last-offset] = matrix[i][last]
			matrix[i][last] = top
		}
	}
}

// setZeroes sets the entire row and column of any zero element to zero.
func (mt *Matrix) setZeroes(matrix [][]int) {
	firstRowZero := false
	firstColumnZero := false
	for i := 0; i < len(matrix); i++ {
		if matrix[i][0] == 0 {
			firstColumnZero = true
			break
		}
	}
	for i := 0; i < len(matrix[0]); i++ {
		if matrix[0][i] == 0 {
			firstRowZero = true
			break
		}
	}
	for i := 1; i < len(matrix); i++ {
		for j := 1; j < len(matrix[0]); j++ {
			if matrix[i][j] == 0 {
				matrix[i][0] = 0
				matrix[0][j] = 0
			}
		}
	}
	for i := 1; i < len(matrix); i++ {
		for j := 1; j < len(matrix[0]); j++ {
			if matrix[i][0] == 0 || matrix[0][j] == 0 {
				matrix[i][j] = 0
			}
		}
	}
	if firstColumnZero {
		for i := 0; i < len(matrix); i++ {
			matrix[i][0] = 0
		}
	}
	if firstRowZero {
		for i := 0; i < len(matrix[0]); i++ {
			matrix[0][i] = 0
		}
	}
}

// countNumZeroes counts zeros in a row-wise and column-wise sorted matrix.
func countNumZeroes(matrix [][]int) int {
	row := len(matrix) - 1
	col := 0
	numZeroes := 0
	for col < len(matrix[0]) {
		for matrix[row][col] != 0 {
			row--
			if row < 0 {
				return numZeroes
			}
		}
		numZeroes += row + 1
		col++
	}
	return numZeroes
}

// countZero counts zeros in a sorted binary matrix using divide and conquer.
func countZero(matrix [][]int) int {
	if matrix == nil || len(matrix) == 0 || len(matrix[0]) == 0 {
		return 0
	}
	m := len(matrix)
	n := len(matrix[0])
	count := 0
	return zeroHelper(matrix, 0, m-1, 0, n-1, count)
}

func zeroHelper(matrix [][]int, rowStart, rowEnd, colStart, colEnd, count int) int {
	if rowStart > rowEnd || colStart > colEnd {
		return count
	}
	rowMid := rowStart + (rowEnd-rowStart)/2
	colMid := colStart + (colEnd-colStart)/2
	if matrix[rowMid][colMid] == 1 {
		return zeroHelper(matrix, rowStart, rowMid-1, colStart, colMid-1, count) +
			zeroHelper(matrix, rowMid, rowEnd, colStart, colMid-1, count) +
			zeroHelper(matrix, rowStart, rowMid-1, colMid, colEnd, count)
	} else if matrix[rowEnd][colEnd] == 0 {
		count += (rowEnd - rowStart + 1) * (colEnd - colStart + 1)
	} else {
		count++
	}
	return count
}

// findElement searches a row/column sorted matrix in O(m+n).
func findElement(matrix [][]int, elem int) bool {
	row := 0
	col := len(matrix[0]) - 1
	for row < len(matrix) && col >= 0 {
		if matrix[row][col] == elem {
			return true
		} else if matrix[row][col] > elem {
			col--
		} else {
			row++
		}
	}
	return false
}

// searchMatrix searches a sorted matrix using quadrant divide and conquer.
func (mt *Matrix) searchMatrix(matrix [][]int, target int) bool {
	if matrix == nil || len(matrix) == 0 || len(matrix[0]) == 0 {
		return false
	}
	m := len(matrix)
	n := len(matrix[0])
	return mt.searchMatrixHelper(matrix, 0, m-1, 0, n-1, target)
}

func (mt *Matrix) searchMatrixHelper(matrix [][]int, rowStart, rowEnd, colStart, colEnd, target int) bool {
	if rowStart > rowEnd || colStart > colEnd {
		return false
	}
	rowMid := rowStart + (rowEnd-rowStart)/2
	colMid := colStart + (colEnd-colStart)/2
	if matrix[rowMid][colMid] == target {
		return true
	}
	if matrix[rowMid][colMid] > target {
		return mt.searchMatrixHelper(matrix, rowStart, rowMid-1, colStart, colMid-1, target) ||
			mt.searchMatrixHelper(matrix, rowMid, rowEnd, colStart, colMid-1, target) ||
			mt.searchMatrixHelper(matrix, rowStart, rowMid-1, colMid, colEnd, target)
	}
	return mt.searchMatrixHelper(matrix, rowMid+1, rowEnd, colMid+1, colEnd, target) ||
		mt.searchMatrixHelper(matrix, rowMid+1, rowEnd, colStart, colMid, target) ||
		mt.searchMatrixHelper(matrix, rowStart, rowMid, colMid+1, colEnd, target)
}

// searchMatrix1 searches a matrix where each row is sorted and the first value
// of each row is greater than the last value of the previous row.
func (mt *Matrix) searchMatrix1(matrix [][]int, target int) bool {
	if matrix == nil || len(matrix) == 0 {
		return false
	}
	m := len(matrix)
	n := len(matrix[0])
	// Step 1: find the rowId of the target number.
	lo := 0
	hi := m - 1
	for lo+1 < hi {
		mid := lo + (hi-lo)/2
		if matrix[mid][0] == target {
			return true
		} else if matrix[mid][0] < target {
			lo = mid
		} else {
			hi = mid - 1
		}
	}
	if matrix[hi][0] == target || matrix[lo][0] == target {
		return true
	}
	var rowId int
	if target > matrix[lo][0] && target <= matrix[lo][n-1] {
		rowId = lo
	} else {
		rowId = hi
	}
	// Step 2: find the target number in rowId.
	lo = 0
	hi = n - 1
	for lo+1 < hi {
		mid := lo + (hi-lo)/2
		if matrix[rowId][mid] == target {
			return true
		} else if matrix[rowId][mid] < target {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	if matrix[rowId][hi] == target || matrix[rowId][lo] == target {
		return true
	}
	return false
}

// patternSearch searches for a word in a character grid in all 8 directions.
func (mt *Matrix) patternSearch(grid [][]byte, word string) {
	R := len(grid)
	C := len(grid[0])
	for row := 0; row < R; row++ {
		for col := 0; col < C; col++ {
			if mt.search2D(grid, row, col, word) {
				fmt.Printf("pattern found at %d, %d", row, col)
			}
		}
	}
}

// search2D checks whether word can be matched starting at (row,col) in any
// of the 8 directions.
func (mt *Matrix) search2D(grid [][]byte, row, col int, word string) bool {
	R := len(grid)
	C := len(grid[0])
	if grid[row][col] != word[0] {
		return false
	}
	length := len(word)
	for dir := 0; dir < 8; dir++ {
		k := 1
		rd := row + search2DX[dir]
		cd := col + search2DY[dir]
		for ; k < length; k++ {
			if rd >= R || rd < 0 || cd >= C || cd < 0 {
				break
			}
			if grid[rd][cd] != word[k] {
				break
			}
			rd += search2DX[dir]
			cd += search2DY[dir]
		}
		if k == length {
			return true
		}
	}
	return false
}

// maximum finds the largest all-ones rectangle in a binary matrix.
func (mt *Matrix) maximum(input [][]int) int {
	temp := make([]int, len(input[0]))
	maxArea := 0
	area := 0
	for i := 0; i < len(input); i++ {
		for j := 0; j < len(temp); j++ {
			if input[i][j] == 0 {
				temp[j] = 0
			} else {
				temp[j] += input[i][j]
			}
		}
		area = largestRectangleArea(temp)
		if area > maxArea {
			maxArea = area
		}
	}
	return maxArea
}

// largestRectangleArea returns the largest rectangle area in a histogram.
// input = [2,1,5,6,2,3] output = 10.
func largestRectangleArea(height []int) int {
	stack := []int{}
	maxArea := 0
	for i := 0; i <= len(height); i++ {
		heightBound := 0
		if i != len(height) {
			heightBound = height[i]
		}
		for len(stack) > 0 {
			h := height[stack[len(stack)-1]]
			if h < heightBound {
				break
			}
			stack = stack[:len(stack)-1]
			index := -1
			if len(stack) != 0 {
				index = i - 1 - stack[len(stack)-1]
			}
			maxArea = maxInt(maxArea, h*index)
		}
		stack = append(stack, i)
	}
	return maxArea
}

// maxSum finds the maximum sum rectangle in a 2D matrix using Kadane per band.
// Time O(row*col*col), space O(row).
func (mt *Matrix) maxSum(input [][]int) {
	maxSum := 0
	leftBound := 0
	rightBound := 0
	upBound := 0
	lowBound := 0
	rows := len(input)
	cols := len(input[0])
	temp := make([]int, rows)
	for left := 0; left < cols; left++ {
		for i := 0; i < rows; i++ {
			temp[i] = 0
		}
		for right := left; right < cols; right++ {
			for i := 0; i < rows; i++ {
				temp[i] += input[i][right]
			}
			kadaneResult := mt.kadane(temp)
			if kadaneResult.maxSum > maxSum {
				maxSum = kadaneResult.maxSum
				leftBound = left
				rightBound = right
				upBound = kadaneResult.start
				lowBound = kadaneResult.end
			}
		}
	}
	fmt.Printf("Result [maxSum=%d, leftBound=%d, rightBound=%d, upBound=%d, lowBound=%d]",
		maxSum, leftBound, rightBound, upBound, lowBound)
}

// kadane returns the maximum-sum subarray together with its boundaries.
func (mt *Matrix) kadane(arr []int) KadaneResult {
	max := 0
	maxStart := -1
	maxEnd := -1
	currentStart := 0
	maxSoFar := 0
	for i := 0; i < len(arr); i++ {
		maxSoFar += arr[i]
		if maxSoFar < 0 {
			maxSoFar = 0
			currentStart = i + 1
		}
		if max < maxSoFar {
			maxStart = currentStart
			maxEnd = i
			max = maxSoFar
		}
	}
	return KadaneResult{maxSum: max, start: maxStart, end: maxEnd}
}
