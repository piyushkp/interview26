package main

import (
	"fmt"
	"sync"
)

// Ported from Coding/java/Threading.java (package code.ds).
// Java threads / synchronized / wait / notify / Executors -> idiomatic Go
// using goroutines, channels, sync.Mutex / sync.WaitGroup / sync.Cond.

func main() {
	threeThreadsDemo()
}

// Multi Threading implementation. Each instance has its own lock (faithful to
// the reference, where the synchronized block guards a per-instance object).
type MultiThreading struct {
	tLock     sync.Mutex
	parameter int
}

func (m *MultiThreading) run(wg *sync.WaitGroup) {
	defer wg.Done()
	m.tLock.Lock()
	// do work
	m.tLock.Unlock()
}

func (m *MultiThreading) threadExe() {
	var wg sync.WaitGroup
	tr := make([]*MultiThreading, 5)
	for i := 0; i < 5; i++ {
		tr[i] = &MultiThreading{parameter: i}
	}
	// Start each "thread".
	for _, x := range tr {
		wg.Add(1)
		go x.run(&wg)
	}
	wg.Wait()
}

// Merge Sort using multiple goroutines.
func parallelMergeSort(a []int, numThreads int) {
	if numThreads <= 1 {
		mergeSort(a)
		return
	}
	mid := len(a) / 2
	left := make([]int, mid)
	copy(left, a[:mid])
	right := make([]int, len(a)-mid)
	copy(right, a[mid:])

	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		defer wg.Done()
		parallelMergeSort(left, numThreads/2)
	}()
	go func() {
		defer wg.Done()
		parallelMergeSort(right, numThreads/2)
	}()
	wg.Wait()

	merge(left, right, a)
}

func mergeSort(a []int) {
	if len(a) <= 1 {
		return
	}
	mid := len(a) / 2
	left := make([]int, mid)
	copy(left, a[:mid])
	right := make([]int, len(a)-mid)
	copy(right, a[mid:])
	mergeSort(left)
	mergeSort(right)

	merge(left, right, a)
}

func merge(a, b, r []int) {
	i, j, k := 0, 0, 0
	for i < len(a) && j < len(b) {
		if a[i] < b[j] {
			r[k] = a[i]
			k++
			i++
		} else {
			r[k] = b[j]
			k++
			j++
		}
	}
	for i < len(a) {
		r[k] = a[i]
		k++
		i++
	}
	for j < len(b) {
		r[k] = b[j]
		k++
		j++
	}
}

// Deadlock example. It is intentionally NOT invoked from main() because
// acquiring the two mutexes in opposite orders can deadlock. To avoid
// deadlock, all locks should be acquired in the same order.
func deadLock() {
	var resource1, resource2 sync.Mutex
	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		defer wg.Done()
		resource1.Lock()
		fmt.Println("Thread 1: locked resource 1")
		resource2.Lock()
		fmt.Println("Thread 1: locked resource 2")
		resource2.Unlock()
		resource1.Unlock()
	}()
	go func() {
		defer wg.Done()
		resource2.Lock()
		fmt.Println("Thread 2: locked resource 2")
		resource1.Lock()
		fmt.Println("Thread 2: locked resource 1")
		resource1.Unlock()
		resource2.Unlock()
	}()
	wg.Wait()
}

// Three goroutines print 1 2 3 1 2 3 ... in order. Made deterministic and
// bounded (3 rounds) using a shared mutex + condition variable, with a
// WaitGroup so main() does not exit early.
func threeThreadsDemo() {
	var mu sync.Mutex
	cond := sync.NewCond(&mu)
	threadID := 1
	var wg sync.WaitGroup

	run := func(currentThreadID, nextThreadID int) {
		defer wg.Done()
		for i := 0; i < 3; i++ {
			mu.Lock()
			for threadID != currentThreadID {
				cond.Wait()
			}
			fmt.Println(currentThreadID)
			threadID = nextThreadID
			cond.Broadcast()
			mu.Unlock()
		}
	}

	wg.Add(3)
	go run(1, 2)
	go run(2, 3)
	go run(3, 1)
	wg.Wait()
}
