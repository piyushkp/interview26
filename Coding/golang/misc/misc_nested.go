package main

import (
	"fmt"
	"strconv"
	"strings"
)

// ---------------------------------------------------------------------------
// Mini parser for a nested list of integers (Airbnb)
// e.g. "[123,456, [788,799,833], [[]], 10, []]"
// ---------------------------------------------------------------------------

// NestedIntList is either a number or a list of NestedIntList.
type NestedIntList struct {
	value    int
	isNumber bool
	intList  []*NestedIntList
}

// newNestedIntListNumber constructs a number node.
func newNestedIntListNumber(value int) *NestedIntList {
	return &NestedIntList{value: value, isNumber: true}
}

// newNestedIntList constructs an (empty) list node.
func newNestedIntList() *NestedIntList {
	return &NestedIntList{intList: []*NestedIntList{}, isNumber: false}
}

func (n *NestedIntList) add(num *NestedIntList) {
	n.intList = append(n.intList, num)
}

func (n *NestedIntList) miniParser(s string) *NestedIntList {
	if len(s) == 0 {
		return nil
	}
	// Corner case "123"
	if s[0] != '[' {
		return newNestedIntListNumber(parseIntSafe(s))
	}
	i := 0
	counter := 1
	var stack []*NestedIntList
	var result *NestedIntList
	for i < len(s) {
		c := s[i]
		if c == '[' {
			num := newNestedIntListNumber(parseIntSafe(substr(s, counter, i)))
			if len(stack) > 0 {
				stack[len(stack)-1].add(num)
			}
			stack = append(stack, num)
			counter = i + 1
		} else if c == ',' || c == ']' {
			if counter != i {
				value := parseIntSafe(substr(s, counter, i))
				num := newNestedIntListNumber(value)
				stack[len(stack)-1].add(num)
			}
			counter = i + 1
			if c == ']' {
				result = stack[len(stack)-1]
				stack = stack[:len(stack)-1]
			}
		}
		i++
	}
	return result
}

func (n *NestedIntList) String() string {
	if n.isNumber {
		return strconv.Itoa(n.value)
	}
	parts := make([]string, len(n.intList))
	for i, item := range n.intList {
		parts[i] = item.String()
	}
	return "[" + strings.Join(parts, ", ") + "]"
}

// substr mimics Java's String.substring(begin, end) without panicking.
func substr(s string, begin, end int) string {
	if begin < 0 {
		begin = 0
	}
	if end > len(s) {
		end = len(s)
	}
	if begin >= end {
		return ""
	}
	return s[begin:end]
}

// parseIntSafe parses an int, returning 0 on failure.
func parseIntSafe(s string) int {
	n, err := strconv.Atoi(strings.TrimSpace(s))
	if err != nil {
		return 0
	}
	return n
}

// depthNestedIntSum returns the sum of all integers weighted by their depth.
func depthNestedIntSum(input []*NestedIntList, level int) int {
	if len(input) == 0 {
		return 0
	}
	sum := 0
	for i := 0; i < len(input); i++ {
		if input[i].isNumber {
			sum += input[i].value * level
		} else {
			sum += depthNestedIntSum(input[i].intList, level+1)
		}
	}
	return sum
}

// ---------------------------------------------------------------------------
// Rectangle overlap
// ---------------------------------------------------------------------------

func doOverlap(l1, r1, l2, r2 *Point) bool {
	// If one rectangle is on the left side of the other.
	if l1.x > r2.x || l2.x > r1.x {
		return false
	}
	// If one rectangle is above the other.
	if l1.y < r2.y || l2.y < r1.y {
		return false
	}
	return true
}

// ---------------------------------------------------------------------------
// Interval tree: find all conflicting appointments.
// ---------------------------------------------------------------------------

type Interval1 struct {
	start int
	end   int
	max   int
	left  *Interval1
	right *Interval1
}

func newInterval1(start, end int) *Interval1 {
	return &Interval1{start: start, end: end, max: end}
}

func (i *Interval1) compareTo(other *Interval1) int {
	if i.start < other.start {
		return -1
	} else if i.start == other.start {
		if i.end <= other.end {
			return -1
		}
		return 1
	}
	return 1
}

type IntervalTree struct {
	root *Interval1
}

func (t *IntervalTree) insert(root, newNode *Interval1) *Interval1 {
	if root == nil {
		return newNode
	}
	// Low value of interval at root.
	l := root.start
	// If root's low value is smaller, the new interval goes left.
	if newNode.start < l {
		root.left = t.insert(root.left, newNode)
	} else {
		root.right = t.insert(root.right, newNode)
	}
	// Update the max value of this ancestor if needed.
	if root.max < newNode.end {
		root.max = newNode.end
	}
	return root
}

// intersectInterval finds all overlapping intervals for the given interval.
func (t *IntervalTree) intersectInterval(root, i *Interval1, output *[]*Interval1) {
	if root == nil {
		return
	}
	if !(root.start > i.end) || (root.end < i.start) {
		*output = append(*output, root)
	}
	if root.left != nil && root.left.max >= i.start {
		t.intersectInterval(root.left, i, output)
	}
	t.intersectInterval(root.right, i, output)
}

// nonOverlappingInterval finds all non-overlapping intervals for the interval.
func (t *IntervalTree) nonOverlappingInterval(root, i *Interval1, output *[]*Interval1) {
	if root == nil {
		return
	}
	if !(root.start < i.end) || (root.end > i.start) {
		*output = append(*output, root)
	}
	if root.left != nil && root.left.max <= i.start {
		t.intersectInterval(root.left, i, output)
	}
	t.intersectInterval(root.right, i, output)
}

func (t *IntervalTree) doOVerlap(i1, i2 *Interval1) bool {
	return i1.start <= i2.end && i2.start <= i1.end
}

func (t *IntervalTree) overlapSearch(root, i *Interval1) *Interval1 {
	if root == nil {
		return nil
	}
	if t.doOVerlap(root, i) {
		return root
	}
	if root.left != nil && root.left.max >= i.start {
		return t.overlapSearch(root.left, i)
	}
	return t.overlapSearch(root.right, i)
}

// printConflicting prints all conflicting appointments.
func (t *IntervalTree) printConflicting(appt []*Interval1, n int) {
	var root *Interval1
	root = t.insert(root, appt[0])
	for i := 1; i < n; i++ {
		res := t.overlapSearch(root, appt[i])
		if res != nil {
			fmt.Println("[" + strconv.Itoa(appt[i].start) + "," +
				strconv.Itoa(appt[i].end) + "] Conflicts with [" +
				strconv.Itoa(res.start) + "," + strconv.Itoa(res.end) + "]")
		}
		root = t.insert(root, appt[i])
	}
}
