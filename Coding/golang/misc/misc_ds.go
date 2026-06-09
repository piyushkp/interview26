package main

import (
	"math/rand"
	"sort"
	"strconv"
	"strings"
)

// ---------------------------------------------------------------------------
// Palantir magic box: maximize the number of identical rows after flipping
// arbitrary columns.
// ---------------------------------------------------------------------------

var columnFlippingStat = map[string]int{}
var maxWishes = -1

func findFlippingSet(row []byte) {
	var allP strings.Builder
	var allT strings.Builder
	for i := 0; i < len(row); i++ {
		if row[i] == 'P' {
			allP.WriteByte('0')
			allT.WriteByte('1')
		} else {
			allP.WriteByte('1')
			allT.WriteByte('0')
		}
	}
	allPFreq := updateSet(allP.String())
	allTFreq := updateSet(allT.String())
	maxWishes = maxInt(maxWishes, maxInt(allPFreq, allTFreq))
}

func updateSet(flippedCols string) int {
	freq := 0
	if v, ok := columnFlippingStat[flippedCols]; ok {
		freq = v
	}
	columnFlippingStat[flippedCols] = freq + 1
	return freq + 1
}

// ---------------------------------------------------------------------------
// Connect4: decode a compressed board string into a 6x7 board.
// CFN: 9_r4_brbrbr_3b2rb_b2r2br_r2b3rb
// ---------------------------------------------------------------------------

func decodeBoard(str string) [][]byte {
	input := []byte(str)
	output := make([][]byte, 6)
	for i := range output {
		output[i] = make([]byte, 7)
	}
	temp := make([]byte, 42)
	index := 0
	for i := 0; i < len(input); i++ {
		if isInteger(string(input[i])) {
			number := int(input[i] - '0')
			for l := 0; l < number; l++ {
				temp[index+l] = input[i+1]
			}
			index += number
			i++
		} else {
			temp[index] = input[i]
			index++
		}
	}
	for k := 0; k < 6; k++ {
		for j := 0; j < 7; j++ {
			output[k][j] = temp[7*k+j]
		}
	}
	return output
}

func isInteger(s string) bool {
	_, err := strconv.Atoi(s)
	return err == nil
}

// ---------------------------------------------------------------------------
// CustomMap: insert/delete/get/getRandomKey in O(1).
// ---------------------------------------------------------------------------

type CustomMap struct {
	mp    map[string][]int
	arr   []string
	index int
	size  int
}

func newCustomMap() *CustomMap {
	return &CustomMap{mp: make(map[string][]int)}
}

func (c *CustomMap) Insert(key string, value int) {
	if _, ok := c.mp[key]; !ok {
		c.index = c.size
		c.mp[key] = []int{value, c.index}
		c.arr = append(c.arr, key)
		c.size++
	} else {
		list := c.mp[key]
		list[0] = value
		c.mp[key] = list
	}
}

func (c *CustomMap) Get(key string) int {
	return c.mp[key][0]
}

func (c *CustomMap) Delete(key string) {
	c.index = c.mp[key][1]
	// copy last element at array index and remove last element (O(1)).
	c.arr[c.index] = c.arr[c.size-1]
	c.arr = c.arr[:c.size-1]
	c.size--
	delete(c.mp, key)
	// update the index of the swapped key.
	c.mp[c.arr[c.index]][1] = c.index
}

func (c *CustomMap) GetRandomKey() string {
	r := int(rand.Float64()*float64(c.size) + 1)
	return c.arr[r]
}

func (c *CustomMap) clear() {
	c.size = 0
}

// ---------------------------------------------------------------------------
// MyDS: insert/delete/search/getRandom in Theta(1) (no duplicates).
// ---------------------------------------------------------------------------

type MyDS struct {
	arr  []int
	hash map[int]int // value -> index in arr
}

func newMyDS() *MyDS {
	return &MyDS{hash: make(map[int]int)}
}

func (m *MyDS) add(x int) {
	if _, ok := m.hash[x]; ok {
		return
	}
	s := len(m.arr)
	m.arr = append(m.arr, x)
	m.hash[x] = s
}

func (m *MyDS) remove(x int) {
	index, ok := m.hash[x]
	if !ok {
		return
	}
	delete(m.hash, x)
	size := len(m.arr)
	last := m.arr[size-1]
	// Swap with last so removal from arr is O(1).
	m.arr[index], m.arr[size-1] = m.arr[size-1], m.arr[index]
	m.arr = m.arr[:size-1]
	m.hash[last] = index
}

func (m *MyDS) getRandom() int {
	return m.arr[rand.Intn(len(m.arr))]
}

func (m *MyDS) search(x int) (int, bool) {
	v, ok := m.hash[x]
	return v, ok
}

// ---------------------------------------------------------------------------
// RandomizedCollection: insert/remove/getRandom O(1) with duplicates allowed.
// ---------------------------------------------------------------------------

type RandomizedCollection struct {
	list []int
	mp   map[int]map[int]struct{} // value -> set of indices
}

func newRandomizedCollection() *RandomizedCollection {
	return &RandomizedCollection{mp: make(map[int]map[int]struct{})}
}

// insert returns true if the collection did not already contain the element.
func (r *RandomizedCollection) insert(val int) bool {
	ans := true
	loc := len(r.list)
	r.list = append(r.list, val)
	indices, ok := r.mp[val]
	if ok {
		ans = false
	} else {
		indices = make(map[int]struct{})
	}
	indices[loc] = struct{}{}
	r.mp[val] = indices
	return ans
}

// remove returns true if the collection contained the element.
func (r *RandomizedCollection) remove(val int) bool {
	if indices, ok := r.mp[val]; !ok || len(indices) == 0 {
		return false
	}
	// Get a location of the value to be removed.
	var locToRemove int
	for k := range r.mp[val] {
		locToRemove = k
		break
	}
	delete(r.mp[val], locToRemove)
	if locToRemove < len(r.list)-1 {
		// Move the tail number into the removed location.
		numToSwap := r.list[len(r.list)-1]
		r.list[locToRemove] = numToSwap
		delete(r.mp[numToSwap], len(r.list)-1)
		r.mp[numToSwap][locToRemove] = struct{}{}
	}
	r.list = r.list[:len(r.list)-1]
	return true
}

func (r *RandomizedCollection) getRandom() int {
	if len(r.list) == 0 {
		return 0
	}
	return r.list[rand.Intn(len(r.list))]
}

// ---------------------------------------------------------------------------
// TimeHashMap: 3-dimensional map keyed by (key, time). get(key, t) returns the
// value at the greatest time t' <= t (TreeMap.floorKey behaviour).
// ---------------------------------------------------------------------------

type timeEntry struct {
	time  float64
	value int
}

type TimeHashMap struct {
	mp map[string][]timeEntry // entries kept sorted by time
}

func newTimeHashMap() *TimeHashMap {
	return &TimeHashMap{mp: make(map[string][]timeEntry)}
}

func (t *TimeHashMap) get(key string, time float64) (int, bool) {
	entries, ok := t.mp[key]
	if !ok {
		return 0, false
	}
	idx := -1
	for i := 0; i < len(entries); i++ {
		if entries[i].time <= time {
			idx = i
		} else {
			break
		}
	}
	if idx == -1 {
		return 0, false
	}
	return entries[idx].value, true
}

func (t *TimeHashMap) put(key string, time float64, value int) {
	entries := t.mp[key]
	pos := sort.Search(len(entries), func(i int) bool { return entries[i].time >= time })
	if pos < len(entries) && entries[pos].time == time {
		entries[pos].value = value
	} else {
		entries = append(entries, timeEntry{})
		copy(entries[pos+1:], entries[pos:])
		entries[pos] = timeEntry{time: time, value: value}
	}
	t.mp[key] = entries
}

// ---------------------------------------------------------------------------
// HitCounter: count hits in the past 60 seconds.
// ---------------------------------------------------------------------------

type HitCounter struct {
	time [60]int
	hits [60]int
}

func newHitCounter() *HitCounter {
	return &HitCounter{}
}

func (h *HitCounter) hit(timestamp int) {
	index := timestamp % 60
	if h.time[index] != timestamp {
		h.time[index] = timestamp
		h.hits[index] = 1
	} else {
		h.hits[index]++ // add one
	}
}

func (h *HitCounter) getHits(timestamp int) int {
	total := 0
	for i := 0; i < 60; i++ {
		if timestamp-h.time[i] < 60 {
			total += h.hits[i]
		}
	}
	return total
}
