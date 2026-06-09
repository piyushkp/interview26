package main

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

// RateLimiter allows a fixed number of occurrences per unit of time. This is an
// idiomatic Go port of a semaphore-based rate gate: a buffered channel acts as
// the semaphore and a timer returns each permit one time unit after it is taken.
type RateLimiter struct {
	occurrences int
	timeUnit    time.Duration
	permits     chan struct{}
	wg          sync.WaitGroup
}

// NewRateLimiter builds a limiter of `occurrences` per `timeSeconds` seconds.
func NewRateLimiter(occurrences, timeSeconds int) (*RateLimiter, error) {
	if occurrences <= 0 {
		return nil, errors.New("number of occurrences must be a positive integer")
	}
	rl := &RateLimiter{
		occurrences: occurrences,
		timeUnit:    time.Duration(timeSeconds) * time.Second,
		permits:     make(chan struct{}, occurrences),
	}
	for i := 0; i < occurrences; i++ {
		rl.permits <- struct{}{}
	}
	return rl, nil
}

// WaitToProceed blocks until a permit is available. The permit is automatically
// returned after one time unit, which enforces the configured rate.
func (rl *RateLimiter) WaitToProceed() {
	<-rl.permits
	rl.wg.Add(1)
	time.AfterFunc(rl.timeUnit, func() {
		rl.permits <- struct{}{}
		rl.wg.Done()
	})
}

func main() {
	rl, err := NewRateLimiter(3, 1) // 3 occurrences per second
	if err != nil {
		fmt.Println(err)
		return
	}
	start := time.Now()
	for i := 1; i <= 6; i++ {
		rl.WaitToProceed()
		fmt.Printf("request %d allowed at ~%v\n", i, time.Since(start).Round(100*time.Millisecond))
	}
	// Let the outstanding permits be returned so the program exits cleanly.
	rl.wg.Wait()
	fmt.Println("done")
}
