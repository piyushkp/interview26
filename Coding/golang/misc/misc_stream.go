package main

import (
	"fmt"
	"sort"
)

// ---------------------------------------------------------------------------
// Bot detection: an id that visits the site m times in the last n seconds.
// ---------------------------------------------------------------------------

type Log struct {
	id   string
	time int
}

type LogCount struct {
	time  int
	count int
}

func newLogCount(time, count int) *LogCount {
	return &LogCount{time: time, count: count}
}

func getBots1(logs []*Log, m, n int) map[string]struct{} {
	mp := make(map[string]*LogCount)
	out := make(map[string]struct{})
	for _, log := range logs {
		if lc, ok := mp[log.id]; ok && (log.time-lc.time <= n) {
			lc.time = log.time
			lc.count++
			mp[log.id] = lc
			if mp[log.id].count == m {
				fmt.Println(log.id)
				out[log.id] = struct{}{}
			}
		} else {
			mp[log.id] = newLogCount(log.time, 1)
		}
	}
	return out
}

func getBots(logs []*Log, m, n int) map[string]struct{} {
	timeSlots := make([]int, n)
	data := make([]map[string]int, n)
	output := make(map[string]struct{})
	count := 0
	for _, log := range logs {
		index := log.time % n
		if timeSlots[index] != log.time {
			temp := data[index]
			if temp != nil {
				if _, ok := temp[log.id]; ok {
					temp[log.id] = temp[log.id] + 1
				} else {
					timeSlots[index] = log.time
					temp = make(map[string]int)
					temp[log.id] = 1
					data[index] = temp
				}
			} else {
				timeSlots[index] = log.time
				temp = make(map[string]int)
				temp[log.id] = 1
				data[index] = temp
			}
		} else {
			temp := data[index]
			if _, ok := temp[log.id]; !ok {
				temp[log.id] = 1
			} else {
				temp[log.id] = temp[log.id] + 1
			}
		}
		if count > n {
			for i := 0; i < n; i++ {
				if log.time-timeSlots[i] < n {
					m2 := data[i]
					for key := range m2 {
						if m2[key] >= m {
							fmt.Println(key)
							output[key] = struct{}{}
						}
					}
				}
			}
		}
		count++
	}
	return output
}

// ---------------------------------------------------------------------------
// Stream deduplication: print last 1 minute of unique data.
// ---------------------------------------------------------------------------

type Streamdedu struct {
	time [60]int
	data [60]map[string]struct{}
}

func newStreamdedu() *Streamdedu {
	return &Streamdedu{}
}

func (s *Streamdedu) onDataReceived(input string, timestamp int) {
	index := timestamp % 60
	if s.time[index] != timestamp {
		s.time[index] = timestamp
		temp := make(map[string]struct{})
		temp[input] = struct{}{}
		s.data[index] = temp
	} else {
		temp := s.data[index]
		if _, ok := temp[input]; !ok {
			temp[input] = struct{}{}
		}
	}
}

func (s *Streamdedu) printData(timestamp int) map[string]struct{} {
	output := make(map[string]struct{})
	for i := 0; i < 60; i++ {
		if timestamp-s.time[i] < 60 {
			for k := range s.data[i] {
				output[k] = struct{}{}
			}
		}
	}
	return output
}

// ---------------------------------------------------------------------------
// Logger rate limiter: a message prints only if not printed in last 10 seconds.
// ---------------------------------------------------------------------------

type Logger struct {
	mp map[string]int
}

func newLogger() *Logger {
	return &Logger{mp: make(map[string]int)}
}

func (l *Logger) shouldPrintMessage(timestamp int, message string) bool {
	if v, ok := l.mp[message]; ok && (timestamp-v < 10) {
		return false
	}
	l.mp[message] = timestamp
	return true
}

// ---------------------------------------------------------------------------
// Number of logged-in users at each event time.
// ---------------------------------------------------------------------------

type Input struct {
	name   string
	login  float64
	logout float64
}

type loginType struct {
	loggedin bool
	time     float64
}

func newLoginType(time float64, loggedIn bool) *loginType {
	return &loginType{time: time, loggedin: loggedIn}
}

type Output struct {
	time        float64
	numLoggedIn int
}

func newOutput(t float64, num int) *Output {
	return &Output{time: t, numLoggedIn: num}
}

func findLoggedIn(list []*Input) []*Output {
	var loggedIn []*loginType
	var retValue []*Output
	loggedInNow := 0
	for _, iv := range list {
		loggedIn = append(loggedIn, newLoginType(iv.login, true))
		loggedIn = append(loggedIn, newLoginType(iv.logout, false))
	}
	sort.Slice(loggedIn, func(i, j int) bool { return loggedIn[i].time < loggedIn[j].time })
	for _, t := range loggedIn {
		if t.loggedin {
			loggedInNow++
		} else {
			loggedInNow--
		}
		retValue = append(retValue, newOutput(t.time, loggedInNow))
	}
	return retValue
}
