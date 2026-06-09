package main

import (
	"fmt"
	"math"
)

// ---------------------------------------------------------------------------
// Egg dropping problem
// Time Complexity: O(nk^2), Auxiliary Space: O(nk).
// ---------------------------------------------------------------------------

func calculate(eggs, floors int) int {
	T := make([][]int, eggs+1)
	for i := range T {
		T[i] = make([]int, floors+1)
	}
	c := 0
	for i := 0; i <= floors; i++ {
		T[1][i] = i
	}
	for e := 2; e <= eggs; e++ {
		for f := 1; f <= floors; f++ {
			T[e][f] = math.MaxInt32
			for k := 1; k <= f; k++ {
				c = 1 + maxInt(T[e-1][k-1], T[e][f-k])
				if c < T[e][f] {
					T[e][f] = c
				}
			}
		}
	}
	return T[eggs][floors]
}

// ---------------------------------------------------------------------------
// Closest pair of points (divide and conquer skeleton)
// ---------------------------------------------------------------------------

// Point is a 2-D coordinate.
type Point struct {
	x int
	y int
}

func closestPairOfPoints(px, py []*Point, start, end int) int {
	if end-start < 3 {
		// brute force (omitted in the original reference)
	}
	mid := (start + end) / 2
	pyLeft := make([]*Point, mid-start+1)
	pyRight := make([]*Point, end-mid)
	i, j := 0, 0
	for _, p := range px {
		if p.x <= px[mid].x {
			pyLeft[i] = p
			i++
		} else {
			pyRight[j] = p
			j++
		}
	}
	d1 := closestPairOfPoints(px, pyLeft, start, mid)
	d2 := closestPairOfPoints(px, pyRight, mid+1, end)
	d := minInt(d1, d2)

	var deltaPoints []*Point
	for _, p := range px {
		if math.Sqrt(float64(distance(p, px[mid]))) < math.Sqrt(float64(d)) {
			deltaPoints = append(deltaPoints, p)
		}
	}
	d3 := closest(deltaPoints)
	return minInt(d3, d)
}

func closest(deltaPoints []*Point) int {
	minDistance := math.MaxInt32
	for i := 0; i < len(deltaPoints); i++ {
		for j := i + 1; j <= i+7 && j < len(deltaPoints); j++ {
			dist := distance(deltaPoints[i], deltaPoints[j])
			if minDistance < dist {
				minDistance = dist
			}
		}
	}
	return minDistance
}

func distance(p1, p2 *Point) int {
	return (p1.x-p2.x)*(p1.x-p2.x) + (p1.y-p2.y)*(p1.y-p2.y)
}

// ---------------------------------------------------------------------------
// Draw a circle
// ---------------------------------------------------------------------------

func drawCircle(r int) {
	x := 0.0
	y := float64(r)
	draw(x, y)
	draw(-x, y)
	draw(x, -y)
	draw(-x, -y)
	draw(y, x)
	draw(-y, x)
	draw(y, -x)
	draw(-y, -x)
	for x < y {
		y = math.Sqrt(y*y - x*x)
		x++
		draw(x, y)
		draw(-x, y)
		draw(x, -y)
		draw(-x, -y)
		draw(y, x)
		draw(-y, x)
		draw(y, -x)
		draw(-y, -x)
	}
}

func drawCircle1(n int) {
	for i := -n; i <= n; i++ {
		for j := -n; j <= n; j++ {
			if i*i+j*j <= n*n+1 {
				fmt.Print("* ")
			} else {
				fmt.Print("  ")
			}
		}
		fmt.Println()
	}
}

func draw(x, y float64) {
}

// ---------------------------------------------------------------------------
// Museum problem: label each cell with distance to nearest guard.
// Space complexity O(n*m), time O(#guards * m * n).
// ---------------------------------------------------------------------------

// Room is the state of a museum cell.
type Room int

const (
	RoomOpen Room = iota
	RoomClosed
	RoomGuard
)

func findShortest(input [][]Room) [][]int {
	distance := make([][]int, len(input))
	for i := range distance {
		distance[i] = make([]int, len(input[0]))
	}
	for i := 0; i < len(input); i++ {
		for j := 0; j < len(input[0]); j++ {
			distance[i][j] = math.MaxInt32
		}
	}
	for i := 0; i < len(input); i++ {
		for j := 0; j < len(input[i]); j++ {
			// for every guard, do a BFS starting at this guard.
			if input[i][j] == RoomGuard {
				distance[i][j] = 0
				setDistance(input, i, j, distance)
			}
		}
	}
	return distance
}

func setDistance(input [][]Room, x, y int, distance [][]int) {
	visited := make([][]bool, len(input))
	for i := range visited {
		visited[i] = make([]bool, len(input[0]))
	}
	var q []*Point
	q = append(q, &Point{x, y})
	// Do a BFS and keep updating distance.
	for len(q) > 0 {
		p := q[0]
		q = q[1:]
		q = setDistanceUtil(q, input, p, getNeighbor(input, p.x+1, p.y), distance, visited)
		q = setDistanceUtil(q, input, p, getNeighbor(input, p.x, p.y+1), distance, visited)
		q = setDistanceUtil(q, input, p, getNeighbor(input, p.x-1, p.y), distance, visited)
		q = setDistanceUtil(q, input, p, getNeighbor(input, p.x, p.y-1), distance, visited)
	}
}

func setDistanceUtil(q []*Point, input [][]Room, p *Point, newPoint *Point,
	distance [][]int, visited [][]bool) []*Point {
	if newPoint != nil && !visited[newPoint.x][newPoint.y] {
		if input[newPoint.x][newPoint.y] != RoomGuard &&
			input[newPoint.x][newPoint.y] != RoomClosed {
			distance[newPoint.x][newPoint.y] = minInt(
				distance[newPoint.x][newPoint.y], 1+distance[p.x][p.y])
			visited[newPoint.x][newPoint.y] = true
			q = append(q, newPoint)
		}
	}
	return q
}

func getNeighbor(input [][]Room, x, y int) *Point {
	if x < 0 || x >= len(input) || y < 0 || y >= len(input[0]) {
		return nil
	}
	return &Point{x, y}
}
