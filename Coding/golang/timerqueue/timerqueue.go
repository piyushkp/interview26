package main

import (
	"container/heap"
	"fmt"
	"sync"
	"time"
)

// TimerTask states.
const (
	taskNew       = 1
	taskScheduled = 2
	taskExecuted  = 3
	taskCancelled = 4
)

func nowMillis() int64 { return time.Now().UnixMilli() }

// TimerTask is the Go analogue of Java's abstract TimerTask. The abstract
// execute() is modelled by the exec func field (supplied by the caller).
type TimerTask struct {
	mu                sync.Mutex
	state             int
	period            int64
	nextExecutionTime int64
	exec              func()
	name              string
}

func newTimerTask(name string, exec func()) *TimerTask {
	return &TimerTask{state: taskNew, period: 0, exec: exec, name: name}
}

func newPeriodicTimerTask(name string, period int64, exec func()) *TimerTask {
	if period < 0 {
		panic("Period can't be negative")
	}
	return &TimerTask{state: taskNew, period: period, exec: exec, name: name}
}

func (t *TimerTask) cancel() bool {
	t.mu.Lock()
	defer t.mu.Unlock()
	ret := t.state == taskScheduled
	t.state = taskCancelled
	return ret
}

func (t *TimerTask) execute() {
	if t.exec != nil {
		t.exec()
	}
}

// compareTo: a task is "less" if it is scheduled earlier.
func (t *TimerTask) compareTo(other *TimerTask) int {
	if other == t {
		return 0
	}
	return int(t.getNextExecutionTime() - other.getNextExecutionTime())
}

func (t *TimerTask) setState(state int) {
	t.mu.Lock()
	t.state = state
	t.mu.Unlock()
}

func (t *TimerTask) getState() int {
	t.mu.Lock()
	defer t.mu.Unlock()
	return t.state
}

func (t *TimerTask) isPeriodic() bool { return t.period > 0 }

func (t *TimerTask) getNextExecutionTime() int64 {
	t.mu.Lock()
	defer t.mu.Unlock()
	return t.nextExecutionTime
}

func (t *TimerTask) setNextExecutionTime(v int64) {
	t.mu.Lock()
	t.nextExecutionTime = v
	t.mu.Unlock()
}

func (t *TimerTask) getPeriod() int64 { return t.period }

// taskHeap is a min-heap of *TimerTask ordered by next execution time.
type taskHeap []*TimerTask

func (h taskHeap) Len() int           { return len(h) }
func (h taskHeap) Less(i, j int) bool { return h[i].getNextExecutionTime() < h[j].getNextExecutionTime() }
func (h taskHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *taskHeap) Push(x any)        { *h = append(*h, x.(*TimerTask)) }
func (h *taskHeap) Pop() any {
	old := *h
	n := len(old)
	x := old[n-1]
	old[n-1] = nil
	*h = old[:n-1]
	return x
}

// TimerQueue holds multiple timers in a priority queue and executes them on
// schedule. Java's wait/notify monitor is modelled with sync.Cond; the worker
// thread/Runnable is a goroutine.
type TimerQueue struct {
	mu     sync.Mutex
	cond   *sync.Cond
	heap   taskHeap
	stop   bool
	stopCh chan struct{}
}

func NewTimerQueue() *TimerQueue {
	tq := &TimerQueue{stopCh: make(chan struct{})}
	tq.cond = sync.NewCond(&tq.mu)
	return tq
}

// schedule runs the task immediately.
func (tq *TimerQueue) schedule(t *TimerTask) { tq.scheduleDelay(t, 0) }

// scheduleDelay runs the task after delay ms (renamed Java overload schedule(t,delay)).
func (tq *TimerQueue) scheduleDelay(t *TimerTask, delay int64) {
	if t == nil {
		panic("Can't schedule a null TimerTask")
	}
	if delay < 0 {
		delay = 0
	}
	t.setNextExecutionTime(nowMillis() + delay)
	tq.putJob(t)
}

func (tq *TimerQueue) putJob(task *TimerTask) {
	tq.mu.Lock()
	heap.Push(&tq.heap, task)
	task.setState(taskScheduled)
	tq.cond.Broadcast()
	tq.mu.Unlock()
}

// getJob blocks until a live task is available, or returns nil if stopped.
func (tq *TimerQueue) getJob() *TimerTask {
	tq.mu.Lock()
	defer tq.mu.Unlock()
	for {
		for len(tq.heap) == 0 && !tq.stop {
			tq.cond.Wait()
		}
		if tq.stop {
			return nil
		}
		task := heap.Pop(&tq.heap).(*TimerTask)
		switch task.getState() {
		case taskCancelled, taskExecuted:
			continue // skip dead task and fetch the next one
		case taskNew, taskScheduled:
			return task
		default:
			panic("TimerTask has an illegal state")
		}
	}
}

func (tq *TimerQueue) executeTask() func() { return tq.timerTaskLoop }

func (tq *TimerQueue) clear() {
	tq.mu.Lock()
	tq.heap = tq.heap[:0]
	tq.mu.Unlock()
}

// Stop terminates the worker loop and wakes any waiters.
func (tq *TimerQueue) Stop() {
	tq.mu.Lock()
	if !tq.stop {
		tq.stop = true
		close(tq.stopCh)
		tq.cond.Broadcast()
	}
	tq.mu.Unlock()
}

func (tq *TimerQueue) isStopped() bool {
	tq.mu.Lock()
	defer tq.mu.Unlock()
	return tq.stop
}

// sleepOrStop waits up to d, returning true if the queue was stopped meanwhile.
func (tq *TimerQueue) sleepOrStop(d time.Duration) bool {
	if d <= 0 {
		d = time.Millisecond
	}
	timer := time.NewTimer(d)
	defer timer.Stop()
	select {
	case <-timer.C:
		return tq.isStopped()
	case <-tq.stopCh:
		return true
	}
}

// timerTaskLoop is the worker: get next job, wait until due, then execute.
func (tq *TimerQueue) timerTaskLoop() {
	defer tq.clear()
	for {
		task := tq.getJob()
		if task == nil {
			return // stopped
		}
		now := nowMillis()
		executionTime := task.getNextExecutionTime()
		timeToWait := executionTime - now
		if timeToWait > 0 {
			// Not yet time to run the first one: put it back and wait.
			tq.putJob(task)
			if tq.sleepOrStop(time.Duration(timeToWait) * time.Millisecond) {
				return
			}
		} else {
			if task.isPeriodic() {
				// Reschedule with the new time.
				task.setNextExecutionTime(executionTime + task.getPeriod())
				tq.putJob(task)
			} else {
				// One-shot task already removed from the heap; mark executed.
				task.setState(taskExecuted)
			}
			task.execute()
		}
	}
}

func main() {
	fmt.Println("TimerQueue demo")

	tq := NewTimerQueue()
	var wg sync.WaitGroup
	var mu sync.Mutex
	var order []string

	scheduleOne := func(name string, delay int64) {
		wg.Add(1)
		t := newTimerTask(name, func() {
			mu.Lock()
			order = append(order, name)
			mu.Unlock()
			fmt.Printf("Executed %s\n", name)
			wg.Done()
		})
		tq.scheduleDelay(t, delay)
	}

	loop := tq.executeTask()
	go loop()

	scheduleOne("task-30ms", 30)
	scheduleOne("task-10ms", 10)
	scheduleOne("task-20ms", 20)

	wg.Wait()
	tq.Stop()

	fmt.Println("Execution order:", order)
}
