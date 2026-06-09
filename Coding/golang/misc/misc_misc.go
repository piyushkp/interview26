package main

import (
	"container/heap"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// ---------------------------------------------------------------------------
// Knight tour on a phone keypad.
// ---------------------------------------------------------------------------

func knightTour() {
	keypad := make([][]int, 4)
	for i := range keypad {
		keypad[i] = make([]int, 4)
	}
	values := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 0, -1}
	count := 0
	for i := 0; i < 4; i++ {
		for j := 0; j < 3; j++ {
			keypad[i][j] = values[count]
		}
	}
	count++
	mtable := make([][]int, 11)
	for i := range mtable {
		mtable[i] = make([]int, 10)
	}
}

func knightUtil(table, mem [][]int, digits, start int) int {
	if digits == 1 {
		return 1
	}
	if mem[digits][start] == 0 {
		for _, next := range nextKnightMove(start, table) {
			mem[digits][start] += knightUtil(table, mem, digits-1, next)
		}
	}
	return mem[digits][start]
}

func nextKnightMove(start int, table [][]int) []int {
	return make([]int, 2)
}

// ---------------------------------------------------------------------------
// Travel buddies: people who share more than half of your locations.
// ---------------------------------------------------------------------------

// Pair is a small generic key/value tuple (replaces javafx.util.Pair).
type Pair[K any, V any] struct {
	key   K
	value V
}

func preProcess(input []Pair[string, []int], user Pair[string, []int]) {
	mp := make(map[int][]string) // location -> list of users
	for _, p := range input {
		var users []string
		for _, location := range p.value {
			if mp[location] == nil {
				users = []string{}
			} else {
				users = mp[location]
			}
			mp[location] = users
		}
	}
	findTravelBuddy(user, mp)
}

func findTravelBuddy(user Pair[string, []int], mp map[int][]string) []string {
	var output []string
	var temp []string
	N := len(user.value)
	commonUsers := make(map[string]int)
	for _, loc := range user.value {
		if v, ok := mp[loc]; ok {
			temp = append(temp, v...)
		}
	}
	// Find the majority element from the temp slice.
	for _, u := range temp {
		if _, ok := commonUsers[u]; ok {
			commonUsers[u] = commonUsers[u] + 1
		} else {
			commonUsers[u] = 1
		}
	}
	for u := range commonUsers {
		if commonUsers[u] > N/2 {
			output = append(output, u)
		}
	}
	return output
}

// ---------------------------------------------------------------------------
// Browser history: prev, forward, add.
// ---------------------------------------------------------------------------

type BrowserNode struct {
	next *BrowserNode
	prev *BrowserNode
	url  string
	time time.Time
	curr *BrowserNode
}

func newBrowserNode(url string) *BrowserNode {
	return &BrowserNode{url: url}
}

type Browser struct {
	head *BrowserNode
	end  *BrowserNode
	curr *BrowserNode
	size int
}

func newBrowser(size int) *Browser {
	return &Browser{size: size}
}

func (b *Browser) add(url string) {
	node := newBrowserNode(url)
	if b.head == nil {
		b.head = node
		b.end = b.head
	} else {
		node.prev = b.end
		b.end.next = node
		b.end = node
	}
	b.curr = node
	b.size++
}

func (b *Browser) forward() string {
	if b.curr != nil && b.curr.next != nil {
		b.curr.next = b.curr.next.next
		b.curr.prev = b.curr
		b.curr = b.curr.next
		return b.curr.next.url
	}
	return ""
}

func (b *Browser) backward() string {
	if b.curr != nil && b.curr.prev != nil {
		b.curr.next = b.curr
		b.curr.prev = b.curr.prev.prev
		b.curr = b.curr.prev
		return b.curr.prev.url
	}
	return ""
}

// ---------------------------------------------------------------------------
// Read all files from a directory recursively.
// ---------------------------------------------------------------------------

var miscFiles []os.DirEntry

func listFilesForFolder(folder string) {
	entries, err := os.ReadDir(folder)
	if err != nil {
		return
	}
	for _, fileEntry := range entries {
		if fileEntry.IsDir() {
			listFilesForFolder(filepath.Join(folder, fileEntry.Name()))
		} else {
			fmt.Println(fileEntry.Name())
			miscFiles = append(miscFiles, fileEntry)
		}
	}
}

// ---------------------------------------------------------------------------
// Moving average of the last N numbers in a stream.
// Time O(1), space O(window size).
// ---------------------------------------------------------------------------

type MovingAverage struct {
	window []int
	n      int
	insert int
	sum    int64
}

func newMovingAverage(size int) *MovingAverage {
	return &MovingAverage{window: make([]int, size)}
}

func (m *MovingAverage) next(val int) float64 {
	if m.n < len(m.window) {
		m.n++
	}
	m.sum -= int64(m.window[m.insert]) // subtract num when window is full
	m.sum += int64(val)
	m.window[m.insert] = val // insert num
	m.insert = (m.insert + 1) % len(m.window)
	return float64(m.sum) / float64(m.n)
}

// ---------------------------------------------------------------------------
// Find duplicate files in a file system (group by size, then by content hash).
// ---------------------------------------------------------------------------

func findDuplicateFiles(paths []string) [][]string {
	var output [][]string
	mapSize := make(map[int64][]string)
	mp := make(map[string][]string)
	for _, path := range paths {
		var length int64
		if info, err := os.Stat(path); err == nil {
			length = info.Size()
		}
		mapSize[length] = append(mapSize[length], path)
	}
	for _, files := range mapSize {
		if len(files) > 1 {
			for _, file := range files {
				hashCode := "" // Utils.getMD5(file)
				mp[hashCode] = append(mp[hashCode], file)
			}
		}
	}
	for _, file := range mp {
		if len(file) > 1 {
			output = append(output, file)
		}
	}
	return output
}

// ---------------------------------------------------------------------------
// Iterator over k sorted lists: each next() returns the next integer in the
// overall sorted order. Time O(log k), space O(k).
// ---------------------------------------------------------------------------

type Element struct {
	value    int
	position int
	kIndex   int
}

type kElementHeap []*Element

func (h kElementHeap) Len() int           { return len(h) }
func (h kElementHeap) Less(i, j int) bool { return h[i].value < h[j].value }
func (h kElementHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *kElementHeap) Push(x any)        { *h = append(*h, x.(*Element)) }
func (h *kElementHeap) Pop() any {
	old := *h
	n := len(old)
	item := old[n-1]
	*h = old[:n-1]
	return item
}

type KSortedIterator struct {
	minHeap *kElementHeap
	data    [][]int
}

func newKSortedIterator() *KSortedIterator {
	h := &kElementHeap{}
	heap.Init(h)
	return &KSortedIterator{minHeap: h}
}

func (k *KSortedIterator) next() (int, bool) {
	if k.minHeap.Len() > 0 {
		output := heap.Pop(k.minHeap).(*Element)
		result := output.value
		if output.position+1 < len(k.data[output.kIndex]) {
			output.value = k.data[output.kIndex][output.position+1]
			output.position++
			heap.Push(k.minHeap, output)
		}
		return result, true
	}
	return 0, false
}

func (k *KSortedIterator) process(data [][]int) {
	k.data = data
	for i := 0; i < len(data); i++ {
		e := &Element{position: 0, value: data[i][0], kIndex: i}
		heap.Push(k.minHeap, e)
	}
}
