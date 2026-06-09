package main

import "fmt"

// DisjointUnionSets implements union-find with path compression + union by rank.
// find/union are ~O(α(n)) amortized.
type DisjointUnionSets struct {
	rank   []int
	parent []int
	n      int
}

func NewDisjointUnionSets(n int) *DisjointUnionSets {
	d := &DisjointUnionSets{
		rank:   make([]int, n),
		parent: make([]int, n),
		n:      n,
	}
	d.makeSet()
	return d
}

// makeSet creates n singleton sets (each element is its own parent).
func (d *DisjointUnionSets) makeSet() {
	for i := 0; i < d.n; i++ {
		d.parent[i] = i
	}
}

// find returns the representative of x's set (with path compression).
func (d *DisjointUnionSets) find(x int) int {
	if d.parent[x] != x {
		d.parent[x] = d.find(d.parent[x])
	}
	return d.parent[x]
}

// union merges the sets containing x and y (by rank).
func (d *DisjointUnionSets) union(x, y int) {
	xRoot, yRoot := d.find(x), d.find(y)
	if xRoot == yRoot {
		return
	}
	if d.rank[xRoot] < d.rank[yRoot] {
		d.parent[xRoot] = yRoot
	} else if d.rank[yRoot] < d.rank[xRoot] {
		d.parent[yRoot] = xRoot
	} else {
		d.parent[yRoot] = xRoot
		d.rank[xRoot]++
	}
}

// countIslands counts connected groups of 1s using 8-neighbour connectivity.
func countIslands(a [][]int) int {
	n := len(a)
	m := len(a[0])
	dus := NewDisjointUnionSets(n * m)

	// Check each cell's 8 neighbours and union them if both are land (1).
	for j := 0; j < n; j++ {
		for k := 0; k < m; k++ {
			if a[j][k] == 0 {
				continue
			}
			if j+1 < n && a[j+1][k] == 1 {
				dus.union(j*m+k, (j+1)*m+k)
			}
			if j-1 >= 0 && a[j-1][k] == 1 {
				dus.union(j*m+k, (j-1)*m+k)
			}
			if k+1 < m && a[j][k+1] == 1 {
				dus.union(j*m+k, j*m+k+1)
			}
			if k-1 >= 0 && a[j][k-1] == 1 {
				dus.union(j*m+k, j*m+k-1)
			}
			if j+1 < n && k+1 < m && a[j+1][k+1] == 1 {
				dus.union(j*m+k, (j+1)*m+k+1)
			}
			if j+1 < n && k-1 >= 0 && a[j+1][k-1] == 1 {
				dus.union(j*m+k, (j+1)*m+k-1)
			}
			if j-1 >= 0 && k+1 < m && a[j-1][k+1] == 1 {
				dus.union(j*m+k, (j-1)*m+k+1)
			}
			if j-1 >= 0 && k-1 >= 0 && a[j-1][k-1] == 1 {
				dus.union(j*m+k, (j-1)*m+k-1)
			}
		}
	}

	// Count distinct representatives among land cells.
	c := make([]int, n*m)
	numberOfIslands := 0
	for j := 0; j < n; j++ {
		for k := 0; k < m; k++ {
			if a[j][k] == 1 {
				x := dus.find(j*m + k)
				if c[x] == 0 {
					numberOfIslands++
				}
				c[x]++
			}
		}
	}
	return numberOfIslands
}

// getStacks groups "service stacks" that share a common service into disjoint sets.
func getStacks(input [][]int, n int) [][]string {
	result := make([][]string, 0)
	set := make(map[string]bool)
	dus := NewDisjointUnionSets(n)
	dus.union(0, 1)
	dus.union(1, 2)
	dus.union(2, 0)
	for i := 0; i < len(input); i++ {
		key := fmt.Sprintf("Stack %d", i+1)
		if !set[key] {
			temp := []string{key}
			set[key] = true
			for j := i + 1; j < len(input); j++ {
				if dus.find(input[i][0]) == dus.find(input[j][0]) {
					sj := fmt.Sprintf("Stack %d", j+1)
					temp = append(temp, sj)
					set[sj] = true
				}
			}
			result = append(result, temp)
		}
	}
	return result
}

// findFriendCircles counts friend circles in a char matrix ('x' links row i and col j).
func findFriendCircles(mat [][]byte) int {
	m := len(mat)
	n := len(mat[0])
	set := make(map[int]bool)
	dus := NewDisjointUnionSets(m * n)
	for i := 0; i < m; i++ {
		for j := 0; j < n; j++ {
			if mat[i][j] == 'x' {
				dus.union(i, j)
			}
		}
	}
	for i := 0; i < m; i++ {
		set[dus.find(i)] = true
	}
	return len(set)
}

// findCircleNum counts friend circles via DFS over an adjacency matrix.
func (d *DisjointUnionSets) findCircleNum(m [][]int) int {
	visited := make([]bool, len(m)) // visited[i] => person i already grouped
	count := 0
	for i := 0; i < len(m); i++ {
		if !visited[i] {
			d.dfs(m, visited, i)
			count++
		}
	}
	return count
}

func (d *DisjointUnionSets) dfs(m [][]int, visited []bool, person int) {
	for other := 0; other < len(m); other++ {
		if m[person][other] == 1 && !visited[other] {
			visited[other] = true
			d.dfs(m, visited, other)
		}
	}
}

func main() {
	input := [][]int{{0, 1}, {1, 2}, {2, 1}}
	out := getStacks(input, 3)
	fmt.Println("Disjoint stacks:", out)

	mat := [][]byte{
		{'x', '.', '.', 'x'},
		{'.', 'x', '.', '.'},
		{'.', '.', 'x', 'x'},
		{'x', '.', 'x', 'x'},
	}
	fmt.Println(findFriendCircles(mat))
}
