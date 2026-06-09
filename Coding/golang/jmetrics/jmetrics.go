package main

import (
	"fmt"
	"sync"
	"time"
)

// Jmetric holds a single metric. The Java version used AtomicLong counters;
// here the counters are guarded by the registry's mutex instead.
type Jmetric struct {
	productID    string
	tenantID     string
	docType      string
	source       string
	metricID     string
	metricValue  int64
	metricUnit   string
	intervalTime int64
}

// JmetricsRegistry replaces the Java static ConcurrentHashMap plus the
// ScheduledExecutorService. A timer flushes each metric after its interval and a
// WaitGroup lets the demo wait for all flushes to complete before exiting.
type JmetricsRegistry struct {
	mu sync.Mutex
	m  map[string]*Jmetric
	wg sync.WaitGroup
}

var registry = &JmetricsRegistry{m: make(map[string]*Jmetric)}

// schedule prints and removes the metric after delay. For the demo we treat the
// delay as milliseconds instead of seconds so the program terminates quickly.
func (r *JmetricsRegistry) schedule(key string, delay int) {
	r.wg.Add(1)
	time.AfterFunc(time.Duration(delay)*time.Millisecond, func() {
		defer r.wg.Done()
		r.mu.Lock()
		defer r.mu.Unlock()
		if metric, ok := r.m[key]; ok {
			fmt.Printf("Doing a task during : %s - Time - %s\n", key, time.Now().Format(time.RFC1123))
			fmt.Printf("%s metric_value: %d\n", key, metric.metricValue)
			delete(r.m, key)
		}
	})
}

// Jmetrics is the API surface used to record metric occurrences.
type Jmetrics struct{}

func (j *Jmetrics) OnboardProduct() {
	key := "Onboard" + "onboard_products"
	fmt.Println(key + " request time: " + time.Now().Format(time.RFC1123))
	registry.mu.Lock()
	metric, ok := registry.m[key]
	if !ok {
		metric = &Jmetric{
			source:       "onboard",
			metricID:     "onboard_products",
			metricUnit:   "value",
			metricValue:  1,
			intervalTime: 60,
		}
		registry.m[key] = metric
		registry.mu.Unlock()
		registry.schedule(key, 60)
	} else {
		metric.metricValue++
		registry.mu.Unlock()
	}
}

func (j *Jmetrics) OnboardTenant() {
	key := "Onboard" + "onboard_tenant"
	fmt.Println(key + " request time: " + time.Now().Format(time.RFC1123))
	registry.mu.Lock()
	metric, ok := registry.m[key]
	if !ok {
		metric = &Jmetric{
			source:       "onboard",
			productID:    "axa",
			metricID:     "onboard_tenant",
			metricUnit:   "value",
			metricValue:  1,
			intervalTime: 20,
		}
		registry.m[key] = metric
		registry.mu.Unlock()
		registry.schedule(key, 20)
	} else {
		metric.metricValue++
		registry.mu.Unlock()
	}
}

func (j *Jmetrics) OnboardDoctype() {}

func main() {
	obj := &Jmetrics{}
	obj.OnboardProduct()
	obj.OnboardProduct()
	obj.OnboardProduct()
	obj.OnboardTenant()
	// Wait for the scheduled flush tasks so the demo ends deterministically.
	registry.wg.Wait()
}
