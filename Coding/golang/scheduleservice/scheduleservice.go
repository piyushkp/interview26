package main

import (
	"fmt"
	"sync"
	"time"
)

// scheduleService mirrors the Java Runnable whose run() prints its delay field.
// The mutex makes concurrent reads/writes of delay safe (the Java original was
// unsynchronized but relied on a single shared object).
type scheduleService struct {
	mu    sync.Mutex
	delay int
}

func (s *scheduleService) setDelay(d int) {
	s.mu.Lock()
	s.delay = d
	s.mu.Unlock()
}

// run is the scheduled task body: print the current delay value.
func (s *scheduleService) run() {
	s.mu.Lock()
	d := s.delay
	s.mu.Unlock()
	fmt.Println(d)
}

func main() {
	obj := &scheduleService{}
	var wg sync.WaitGroup

	// schedule runs obj.run() once after the given delay, mirroring
	// ScheduledExecutorService.schedule. A WaitGroup replaces shutdown()+await
	// so the program terminates once queued tasks finish.
	schedule := func(after time.Duration) {
		wg.Add(1)
		time.AfterFunc(after, func() {
			defer wg.Done()
			obj.run()
		})
	}

	// Java scheduled the SAME object twice after mutating delay, so both runs
	// observe the final value (15). Durations are scaled to ms to keep the
	// demo fast and terminating.
	obj.setDelay(10)
	schedule(10 * time.Millisecond)
	obj.setDelay(15)
	schedule(15 * time.Millisecond)

	wg.Wait()
}
