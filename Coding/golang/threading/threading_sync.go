package main

import (
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
)

// Lock-free range, odd/even alternation, and a reentrant read/write lock.

// IntPair is an immutable (lower, upper) pair swapped atomically.
type IntPair struct {
	lower, upper int
}

// CasNumberRange lets multiple goroutines change the value with the invariant
// lower <= upper, using an atomic compare-and-set loop.
type CasNumberRange struct {
	values atomic.Pointer[IntPair]
}

func newCasNumberRange() *CasNumberRange {
	c := &CasNumberRange{}
	c.values.Store(&IntPair{lower: 0, upper: 0})
	return c
}

func (c *CasNumberRange) getLower() int { return c.values.Load().lower }

func (c *CasNumberRange) setLower(i int) error {
	for {
		oldv := c.values.Load()
		if i > oldv.upper {
			return errors.New("illegal argument: lower cannot exceed upper")
		}
		newv := &IntPair{lower: i, upper: oldv.upper}
		if c.values.CompareAndSwap(oldv, newv) {
			return nil
		}
	}
}

func (c *CasNumberRange) getUpper() int { return c.values.Load().upper }

func (c *CasNumberRange) setUpper(i int) error {
	for {
		oldv := c.values.Load()
		if i < oldv.lower {
			return errors.New("illegal argument: upper cannot be below lower")
		}
		newv := &IntPair{lower: oldv.lower, upper: i}
		if c.values.CompareAndSwap(oldv, newv) {
			return nil
		}
	}
}

// OddEvenMonitor coordinates two goroutines so they alternate turns.
const (
	oddTurn  = true
	evenTurn = false
)

type OddEvenMonitor struct {
	mu   sync.Mutex
	cond *sync.Cond
	turn bool
}

func newOddEvenMonitor() *OddEvenMonitor {
	m := &OddEvenMonitor{turn: oddTurn}
	m.cond = sync.NewCond(&m.mu)
	return m
}

func (m *OddEvenMonitor) waitTurn(oldTurn bool) {
	m.mu.Lock()
	for m.turn != oldTurn {
		m.cond.Wait()
	}
	m.mu.Unlock()
	// Move on, it's our turn.
}

func (m *OddEvenMonitor) toggleTurn() {
	m.mu.Lock()
	m.turn = !m.turn
	m.cond.Signal()
	m.mu.Unlock()
}

// oddEvenDemo runs two goroutines that, running concurrently, print the
// numbers from 1 to 100 in order (odd thread prints odds, even prints evens).
func oddEvenDemo() {
	monitor := newOddEvenMonitor()
	var wg sync.WaitGroup
	wg.Add(2)
	go func() {
		defer wg.Done()
		for i := 1; i <= 100; i += 2 {
			monitor.waitTurn(oddTurn)
			fmt.Println("i =", i)
			monitor.toggleTurn()
		}
	}()
	go func() {
		defer wg.Done()
		for i := 2; i <= 100; i += 2 {
			monitor.waitTurn(evenTurn)
			fmt.Println("i =", i)
			monitor.toggleTurn()
		}
	}()
	wg.Wait()
}

// threadToken models a "calling thread" identity (Go goroutines have no public
// IDs, so callers pass a token).
type threadToken struct{ id int }

// ReadWriteLock is a reentrant read/write lock implemented with a mutex and a
// condition variable, mirroring the classic Java implementation.
type ReadWriteLock struct {
	mu            sync.Mutex
	cond          *sync.Cond
	writeRequests int
	writeAccess   int
	writingThread *threadToken
	readers       map[*threadToken]int
}

func newReadWriteLock() *ReadWriteLock {
	rw := &ReadWriteLock{readers: make(map[*threadToken]int)}
	rw.cond = sync.NewCond(&rw.mu)
	return rw
}

func (rw *ReadWriteLock) lockRead(callingThread *threadToken) {
	rw.mu.Lock()
	defer rw.mu.Unlock()
	for !rw.canGrantReadAccess(callingThread) {
		rw.cond.Wait()
	}
	rw.readers[callingThread] = rw.readers[callingThread] + 1
}

func (rw *ReadWriteLock) canGrantReadAccess(callingThread *threadToken) bool {
	if rw.writingThread == callingThread {
		return true
	}
	if rw.writingThread != nil {
		return false
	}
	if _, ok := rw.readers[callingThread]; ok {
		return true
	}
	if rw.writeRequests > 0 {
		return false
	}
	return true
}

func (rw *ReadWriteLock) unlockRead(callingThread *threadToken) {
	rw.mu.Lock()
	defer rw.mu.Unlock()
	if rw.readers[callingThread] == 1 {
		delete(rw.readers, callingThread)
	} else {
		rw.readers[callingThread] = rw.readers[callingThread] - 1
	}
	rw.cond.Broadcast()
}

func (rw *ReadWriteLock) lockWrite(callingThread *threadToken) {
	rw.mu.Lock()
	defer rw.mu.Unlock()
	rw.writeRequests++
	for !rw.canGrantWriteAccess(callingThread) {
		rw.cond.Wait()
	}
	rw.writeRequests--
	rw.writeAccess++
	rw.writingThread = callingThread
}

func (rw *ReadWriteLock) canGrantWriteAccess(callingThread *threadToken) bool {
	if len(rw.readers) == 1 {
		if _, ok := rw.readers[callingThread]; ok {
			return true
		}
	}
	if len(rw.readers) > 0 {
		return false
	}
	if rw.writingThread == nil {
		return true
	}
	if rw.writingThread != callingThread {
		return false
	}
	return true
}

func (rw *ReadWriteLock) unlockWrite() {
	rw.mu.Lock()
	defer rw.mu.Unlock()
	rw.writeAccess--
	if rw.writeAccess == 0 {
		rw.writingThread = nil
	}
	rw.cond.Broadcast()
}
