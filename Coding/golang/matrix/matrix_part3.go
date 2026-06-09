package main

import (
	"math/rand"
	"sort"
)

// floodFill marks an ocean region via BFS, replacing target with replace.
func floodFill(m [][]byte, x, y int, target, replace byte) [][]byte {
	if m[x][y] == replace {
		return nil // current is same as replacement
	}
	q := []Point{}
	q = append(q, Point{x, y})
	for len(q) > 0 {
		temp := q[0]
		q = q[1:]
		x = temp.x
		y = temp.y
		if m[x][y] != replace && m[x][y] == target {
			m[x][y] = replace
			if y < len(m[x])-1 {
				q = append(q, Point{x, y + 1})
			}
			if y > 0 {
				q = append(q, Point{x, y - 1})
			}
			if x < len(m)-1 {
				q = append(q, Point{x + 1, y})
			}
			if x > 0 {
				q = append(q, Point{x - 1, y})
			}
		}
	}
	return m
}

// isSafe reports whether (x,y) is a valid, open cell of the maze.
func (mt *Matrix) isSafe(maze [][]int, x, y int) bool {
	return x >= 0 && x < matrixM && y >= 0 && y < matrixN && maze[x][y] == 1
}

// getShortestPathLength returns the BFS shortest path length through a maze of
// open (0) cells, or -1 if the destination is unreachable.
func getShortestPathLength(maze [][]int) int {
	if maze == nil || len(maze) == 0 {
		return 0
	}
	queue := []Point{}
	visited := make([][]bool, len(maze))
	for i := range visited {
		visited[i] = make([]bool, len(maze[0]))
	}
	queue = append(queue, Point{0, 0})
	level := 0
	for len(queue) > 0 {
		count := len(queue)
		for count > 0 {
			count--
			pt := queue[0]
			queue = queue[1:]
			if pt.x == len(maze)-1 && pt.y == len(maze[0])-1 {
				return level
			}
			visited[pt.x][pt.y] = true
			if pt.x-1 >= 0 && maze[pt.x-1][pt.y] == 0 && !visited[pt.x-1][pt.y] {
				queue = append(queue, Point{pt.x - 1, pt.y})
			}
			if pt.x+1 < len(maze) && !visited[pt.x+1][pt.y] && maze[pt.x+1][pt.y] == 0 {
				queue = append(queue, Point{pt.x + 1, pt.y})
			}
			if pt.y-1 >= 0 && !visited[pt.x][pt.y-1] && maze[pt.x][pt.y-1] == 0 {
				queue = append(queue, Point{pt.x, pt.y - 1})
			}
			if pt.y+1 < len(maze[0]) && !visited[pt.x][pt.y+1] && maze[pt.x][pt.y+1] == 0 {
				queue = append(queue, Point{pt.x, pt.y + 1})
			}
		}
		level++
	}
	return -1
}

// countAllMazePathDP counts paths in a maze using dynamic programming.
func countAllMazePathDP(maze [][]int) int {
	result := maze
	for i := 1; i < len(result); i++ {
		for j := 1; j < len(result); j++ {
			if result[i][j] != 0 {
				result[i][j] = 0
				if result[i-1][j] > 0 {
					result[i][j] += result[i-1][j]
				}
				if result[i][j-1] > 0 {
					result[i][j] += result[i][j-1]
				}
			}
		}
	}
	return result[len(maze)-1][len(maze)-1]
}

// isToepliz reports whether each descending diagonal of the matrix is constant.
func isToepliz(mat [][]int) bool {
	for i := 0; i < matrixM; i++ {
		if !checkDiagonal(mat, 0, i) {
			return false
		}
	}
	for i := 1; i < matrixN; i++ {
		if !checkDiagonal(mat, i, 0) {
			return false
		}
	}
	return true
}

// checkDiagonal reports whether the descending diagonal from (i,j) is constant.
func checkDiagonal(mat [][]int, i, j int) bool {
	res := mat[i][j]
	for {
		i++
		if !(i < matrixN) {
			break
		}
		j++
		if !(j < matrixM) {
			break
		}
		if mat[i][j] != res {
			return false
		}
	}
	return true
}

// sortMatrix sorts all values and lays them back into the matrix (faithful port
// of the reference, including its row-fill quirk).
func sortMatrix(a [][]int) [][]int {
	rowCount := len(a)
	colCount := len(a[0])
	temp := make([]int, rowCount*colCount)
	for r := 0; r < rowCount; r++ {
		for c := 0; c < colCount; c++ {
			temp[r*colCount+c] = a[r][c]
		}
	}
	sort.Ints(temp)
	for r := 0; r < rowCount; r++ {
		k := 0
		for c := 0; c < colCount; c++ {
			a[r][c] = temp[r+2*k]
			k++
		}
	}
	return a
}

// isValidSudoku checks whether a Sudoku board is valid (faithful port).
func isValidSudoku(board [][]byte) bool {
	if board == nil || len(board) != 9 || len(board[0]) != 9 {
		return false
	}
	rows := map[int]bool{}
	cols := map[int]bool{}
	cubes := map[int]bool{}
	for i := 0; i < len(board); i++ {
		for j := 0; j < len(board[0]); j++ {
			current := board[i][j]
			if isDigitByte(current) {
				cube := 3*(i/3) + (j / 3)
				if !addToSet(rows, int(current)) || !addToSet(cols, int(current)) || !addToSet(cubes, cube) {
					return false
				}
			} else if !isWhitespaceByte(current) {
				return false
			}
		}
	}
	return true
}

// addToSet adds v to set and reports whether it was newly added (like Set.add).
func addToSet(set map[int]bool, v int) bool {
	if set[v] {
		return false
	}
	set[v] = true
	return true
}

// minCostPath returns the minimum cost path from (0,0) to (m,n).
func minCostPath(cost [][]int, m, n int) int {
	tc := make([][]int, m+1)
	for i := range tc {
		tc[i] = make([]int, n+1)
	}
	tc[0][0] = cost[0][0]
	for i := 1; i <= m; i++ {
		tc[i][0] = tc[i-1][0] + cost[i][0]
	}
	for j := 1; j <= n; j++ {
		tc[0][j] = tc[0][j-1] + cost[0][j]
	}
	for i := 1; i <= m; i++ {
		for j := 1; j <= n; j++ {
			tc[i][j] = minInt(minInt(tc[i-1][j-1], tc[i-1][j]), tc[i][j-1]) + cost[i][j]
		}
	}
	return tc[m][n]
}

// multiply multiplies two matrices, skipping zero entries. Time O(N^2).
func multiply(A, B [][]int) [][]int {
	if A == nil || B == nil {
		return [][]int{}
	}
	result := make([][]int, len(A))
	for i := range result {
		result[i] = make([]int, len(B[0]))
	}
	for i := 0; i < len(A); i++ {
		for k := 0; k < len(A[0]); k++ {
			if A[i][k] != 0 {
				for j := 0; j < len(B[0]); j++ {
					if B[k][j] != 0 {
						result[i][j] += A[i][k] * B[k][j]
					}
				}
			}
		}
	}
	return result
}

// multiplySparse multiplies two matrices using a sparse representation of A.
func multiplySparse(A, B [][]int) [][]int {
	m := len(A)
	n := len(A[0])
	nB := len(B[0])
	result := make([][]int, m)
	for i := range result {
		result[i] = make([]int, nB)
	}
	indexA := make([][]int, m)
	for i := 0; i < m; i++ {
		numsA := []int{}
		for j := 0; j < n; j++ {
			if A[i][j] != 0 {
				numsA = append(numsA, j)
				numsA = append(numsA, A[i][j])
			}
		}
		indexA[i] = numsA
	}
	for i := 0; i < m; i++ {
		numsA := indexA[i]
		for p := 0; p < len(numsA)-1; p += 2 {
			colA := numsA[p]
			valA := numsA[p+1]
			for j := 0; j < nB; j++ {
				valB := B[colA][j]
				result[i][j] += valA * valB
			}
		}
	}
	return result
}

// putBomb randomly places `count` bombs on an h x w minesweeper field.
func (mt *Matrix) putBomb(h, w, count int) [][]int {
	bombLocs := make([]int, count)
	for i := 0; i < count; i++ {
		bombLocs[i] = i
	}
	for i := count; i < h*w; i++ {
		j := rand.Intn(i + 1)
		if j < count {
			bombLocs[j] = i
		}
	}
	res := make([][]int, h)
	for i := range res {
		res[i] = make([]int, w)
	}
	for i := 0; i < len(bombLocs); i++ {
		x := bombLocs[i] / w
		y := bombLocs[i] % w
		res[x][y] = 1
	}
	return res
}

// wallsAndGates fills each empty room with the distance to its nearest gate.
func (mt *Matrix) wallsAndGates(rooms [][]int) {
	m := len(rooms)
	if m == 0 {
		return
	}
	n := len(rooms[0])
	q := []Point{}
	for row := 0; row < m; row++ {
		for col := 0; col < n; col++ {
			if rooms[row][col] == gateVal {
				q = append(q, Point{row, col})
			}
		}
	}
	for len(q) > 0 {
		point := q[0]
		q = q[1:]
		row := point.x
		col := point.y
		for _, direction := range directions {
			r := row + direction[0]
			c := col + direction[1]
			if r < 0 || c < 0 || r >= m || c >= n || rooms[r][c] != emptyRoom {
				continue
			}
			rooms[r][c] = rooms[row][col] + 1
			q = append(q, Point{r, c})
		}
	}
}

// minCost solves Paint House with three colors.
func (mt *Matrix) minCost(costs [][]int) int {
	if costs == nil || len(costs) == 0 {
		return 0
	}
	for i := 1; i < len(costs); i++ {
		costs[i][0] += minInt(costs[i-1][1], costs[i-1][2])
		costs[i][1] += minInt(costs[i-1][0], costs[i-1][2])
		costs[i][2] += minInt(costs[i-1][0], costs[i-1][1])
	}
	m := len(costs) - 1
	return minInt(minInt(costs[m][0], costs[m][1]), costs[m][2])
}

// minCostII solves Paint House II with k colors.
func (mt *Matrix) minCostII(costs [][]int) int {
	if costs == nil || len(costs) == 0 {
		return 0
	}
	n, k := len(costs), len(costs[0])
	// min1/min2 track the indices of the 1st/2nd smallest cost so far.
	min1, min2 := -1, -1
	for i := 0; i < n; i++ {
		last1, last2 := min1, min2
		min1 = -1
		min2 = -1
		for j := 0; j < k; j++ {
			if j != last1 {
				if last1 >= 0 {
					costs[i][j] += costs[i-1][last1]
				}
			} else {
				if last2 >= 0 {
					costs[i][j] += costs[i-1][last2]
				}
			}
			if min1 < 0 || costs[i][j] < costs[i][min1] {
				min2 = min1
				min1 = j
			} else if min2 < 0 || costs[i][j] < costs[i][min2] {
				min2 = j
			}
		}
	}
	return costs[n-1][min1]
}

// isBipartite reports whether the graph (adjacency lists) is bipartite (BFS).
func (mt *Matrix) isBipartite(g [][]int) bool {
	colors := make([]int, len(g))
	for i := 0; i < len(g); i++ {
		if colors[i] == 0 {
			q := []int{}
			q = append(q, i)
			colors[i] = 1
			for len(q) > 0 {
				node := q[0]
				q = q[1:]
				for _, adjacent := range g[node] {
					if colors[adjacent] == colors[node] {
						return false
					} else if colors[adjacent] == 0 {
						q = append(q, adjacent)
						colors[adjacent] = -colors[node]
					}
				}
			}
		}
	}
	return true
}
