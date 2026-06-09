package main

import (
	"fmt"
	"sort"
	"strings"
	"time"
)

// Event represents a scheduled calendar event with an id and a [start, end) window.
type Event struct {
	id        int
	startDate time.Time
	endDate   time.Time
}

func (e Event) String() string {
	return fmt.Sprintf("Event{id=%d, startDate=%s, endDate=%s}",
		e.id, fmtDate(e.startDate), fmtDate(e.endDate))
}

// scheEvent is a flattened ((date, id), isStart) tuple used internally.
// Replaces the Java nested Pair<Pair<Date, Integer>, Boolean>.
type scheEvent struct {
	date    time.Time
	id      int
	isStart bool
}

// ConflictedTimeWindow describes a window of time in which more than one event overlaps.
type ConflictedTimeWindow struct {
	startDate          time.Time
	endDate            time.Time
	conflictedEventIds map[int]bool
}

func (c ConflictedTimeWindow) String() string {
	ids := make([]int, 0, len(c.conflictedEventIds))
	for id := range c.conflictedEventIds {
		ids = append(ids, id)
	}
	sort.Ints(ids)
	return fmt.Sprintf("ConflictedTimeWindow{startDate=%s, endDate=%s, conflictedEventIds=%v}",
		fmtDate(c.startDate), fmtDate(c.endDate), ids)
}

// Calendar allows multiple events to be scheduled over the same time window.
type Calendar struct {
	scheEvents []scheEvent
}

// schedule records the start and end markers for an event.
func (cal *Calendar) schedule(event *Event) {
	if event != nil {
		cal.scheEvents = append(cal.scheEvents, scheEvent{event.startDate, event.id, true})
		cal.scheEvents = append(cal.scheEvents, scheEvent{event.endDate, event.id, false})
	}
}

// findConflictedTimeWindow returns all windows where more than one event is ongoing.
func (cal *Calendar) findConflictedTimeWindow() []ConflictedTimeWindow {
	// Sort by date; tie-break by id (stable, like Java Collections.sort).
	sort.SliceStable(cal.scheEvents, func(i, j int) bool {
		a, b := cal.scheEvents[i], cal.scheEvents[j]
		if a.date.Equal(b.date) {
			return a.id < b.id
		}
		return a.date.Before(b.date)
	})

	var output []ConflictedTimeWindow
	if len(cal.scheEvents) == 0 {
		return output
	}
	ongoing := map[int]bool{}
	ongoing[cal.scheEvents[0].id] = true
	start := cal.scheEvents[0].date
	for i := 1; i < len(cal.scheEvents); i++ {
		if cal.scheEvents[i].isStart {
			ongoing[cal.scheEvents[i].id] = true
			start = cal.scheEvents[i].date
			// Guard against i+1 out-of-range (the reference assumes the last
			// marker is always an "end" event).
			if len(ongoing) > 1 && i+1 < len(cal.scheEvents) && !start.Equal(cal.scheEvents[i+1].date) {
				temp := copySet(ongoing)
				output = append(output, ConflictedTimeWindow{start, cal.scheEvents[i+1].date, temp})
				start = cal.scheEvents[i+1].date
			}
		} else {
			if len(ongoing) > 1 && !start.Equal(cal.scheEvents[i].date) {
				temp := copySet(ongoing)
				output = append(output, ConflictedTimeWindow{start, cal.scheEvents[i].date, temp})
				start = cal.scheEvents[i].date
			}
			delete(ongoing, cal.scheEvents[i].id)
		}
	}
	return output
}

func copySet(m map[int]bool) map[int]bool {
	out := make(map[int]bool, len(m))
	for k := range m {
		out[k] = true
	}
	return out
}

func fmtDate(t time.Time) string {
	return t.Format("Mon Jan 02 15:04:05 2006")
}

// mkDate builds a UTC time (month is 1-based, unlike java.util.Date).
func mkDate(year, month, day, hour, min int) time.Time {
	return time.Date(year, time.Month(month), day, hour, min, 0, 0, time.UTC)
}

func main() {
	calendar := &Calendar{}

	calendar.schedule(&Event{1, mkDate(2014, 1, 1, 10, 0), mkDate(2014, 1, 1, 11, 0)})  // 2014-01-01 10:00 - 11:00
	calendar.schedule(&Event{2, mkDate(2014, 1, 1, 11, 0), mkDate(2014, 1, 1, 12, 0)})  // 2014-01-01 11:00 - 12:00
	calendar.schedule(&Event{3, mkDate(2014, 1, 1, 12, 0), mkDate(2014, 1, 1, 13, 0)})  // 2014-01-01 12:00 - 13:00

	calendar.schedule(&Event{4, mkDate(2014, 1, 2, 10, 0), mkDate(2014, 1, 2, 11, 0)})  // 2014-01-02 10:00 - 11:00
	calendar.schedule(&Event{5, mkDate(2014, 1, 2, 9, 30), mkDate(2014, 1, 2, 11, 30)}) // 2014-01-02 09:30 - 11:30
	calendar.schedule(&Event{6, mkDate(2014, 1, 2, 8, 30), mkDate(2014, 1, 2, 12, 30)}) // 2014-01-02 08:30 - 12:30

	calendar.schedule(&Event{7, mkDate(2014, 1, 3, 10, 0), mkDate(2014, 1, 3, 11, 0)})  // 2014-01-03 10:00 - 11:00
	calendar.schedule(&Event{8, mkDate(2014, 1, 3, 9, 30), mkDate(2014, 1, 3, 10, 30)}) // 2014-01-03 09:30 - 10:30
	calendar.schedule(&Event{9, mkDate(2014, 1, 3, 9, 45), mkDate(2014, 1, 3, 10, 45)}) // 2014-01-03 09:45 - 10:45

	conflicted := calendar.findConflictedTimeWindow()

	var sb strings.Builder
	sb.WriteString("[")
	for i, c := range conflicted {
		if i > 0 {
			sb.WriteString(", ")
		}
		sb.WriteString(c.String())
	}
	sb.WriteString("]")
	fmt.Println(sb.String())
}
