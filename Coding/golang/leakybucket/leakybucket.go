package main

import (
	"fmt"
	"math"
	"sync"
	"time"
)

// LeakyBucket is a leaky-bucket meter with lazy refill of the bucket level.
// It is safe for concurrent use.
type LeakyBucket struct {
	mu sync.Mutex
	// currentBudget is the level of the bucket as of lastUpdate.
	currentBudget int
	// capacity is the maximum level of the bucket.
	capacity int
	// rate is the number of tokens the bucket leaks (refills) per second.
	rate int
	// lastUpdate is the time (ms) when the level was last updated.
	lastUpdate int64
}

// newLeakyBucket creates a bucket that starts full at the given capacity.
func newLeakyBucket(capacity, rate int) *LeakyBucket {
	return &LeakyBucket{
		currentBudget: capacity,
		capacity:      capacity,
		rate:          rate,
		lastUpdate:    time.Now().UnixMilli(),
	}
}

// consume attempts to take nbTokens from the bucket. Before checking it lazily
// refills the budget based on the seconds elapsed since the last update. It
// returns whether the tokens were granted, and an error if nbTokens < 0.
func (b *LeakyBucket) consume(nbTokens int) (bool, error) {
	b.mu.Lock()
	defer b.mu.Unlock()
	if nbTokens < 0 {
		return false, fmt.Errorf("cannot add negative number of tokens: %d", nbTokens)
	}
	now := time.Now().UnixMilli()
	seconds := int(math.Floor(float64(now-b.lastUpdate) / 1000))
	b.currentBudget = minInt(b.capacity, b.currentBudget+b.rate*seconds)
	b.lastUpdate = now
	if b.currentBudget >= nbTokens {
		b.currentBudget -= nbTokens
		return true, nil
	}
	return false, nil
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	bucket := newLeakyBucket(10, 2)
	// Fast successive calls (≈0s elapsed) so no refill happens between them,
	// making the demo deterministic.
	for i := 1; i <= 6; i++ {
		ok, err := bucket.consume(3)
		if err != nil {
			fmt.Println("error:", err)
			continue
		}
		fmt.Printf("consume(3) #%d -> %v (budget=%d)\n", i, ok, bucket.currentBudget)
	}
	if _, err := bucket.consume(-1); err != nil {
		fmt.Println("error:", err)
	}
}
