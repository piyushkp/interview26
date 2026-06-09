package main

import (
	"fmt"
	"strconv"
	"time"
)

// AllOne is meant to support inc/dec/getMaxKey/getMinKey in O(1).
// The reference implementation is unimplemented; the stubs are preserved.
//
// Inc(Key)      - inserts a new key with value 1, or increments an existing key by 1.
// Dec(Key)      - decrements an existing key by 1; removes it when the value reaches 0.
// GetMaxKey()   - returns one of the keys with the maximal value (or "").
// GetMinKey()   - returns one of the keys with the minimal value (or "").
type AllOne struct{}

func NewAllOne() *AllOne { return &AllOne{} }

func (a *AllOne) inc(key string) {}

func (a *AllOne) dec(key string) {}

func (a *AllOne) getMaxKey() string { return "" }

func (a *AllOne) getMinKey() string { return "" }

// SparseSet is a dynamically sized integer store supporting get/set/setAll in O(1).
// Java used Integer (nullable); *int models the "null" entries here.
type SparseSet struct {
	data          []*int
	indexer       []*int
	setAllValue   *int
	indexPointer  int
	setAllPointer int
}

func NewSparseSet(capacity int) *SparseSet {
	return &SparseSet{
		data:          make([]*int, capacity),
		indexer:       make([]*int, capacity),
		indexPointer:  0,
		setAllPointer: 0,
		setAllValue:   nil,
	}
}

func (s *SparseSet) set(index, value int) {
	v := value
	s.data[index] = &v
	ip := s.indexPointer
	s.indexer[index] = &ip
	s.indexPointer++
}

func (s *SparseSet) get(index int) *int {
	if s.data[index] != nil {
		if *s.indexer[index] >= s.setAllPointer {
			return s.data[index]
		}
		return s.setAllValue
	}
	return nil
}

func (s *SparseSet) setAll(value int) {
	v := value
	s.setAllValue = &v
	s.setAllPointer = s.indexPointer
	s.indexPointer++
}

// Combo pairs a value with the timestamp at which it was written.
type Combo struct {
	timeStamp time.Time
	value     *int
}

func NewCombo(t time.Time, value *int) *Combo {
	return &Combo{timeStamp: t, value: value}
}

// SetAll is an alternative get/set/setAll store that resolves the most recent write
// per index against a global "set all" default using timestamps.
type SetAll struct {
	defaultValue *Combo
	m            map[int]*Combo
}

func NewSetAll() *SetAll {
	return &SetAll{
		defaultValue: NewCombo(time.Now(), nil),
		m:            make(map[int]*Combo),
	}
}

func (s *SetAll) setAll(val int) {
	s.defaultValue.timeStamp = time.Now()
	v := val
	s.defaultValue.value = &v
}

func (s *SetAll) set(index, val int) {
	v := val
	s.m[index] = NewCombo(time.Now(), &v)
}

func (s *SetAll) get(index int) *int {
	c, ok := s.m[index]
	if !ok {
		return nil
	}
	if c.timeStamp.After(s.defaultValue.timeStamp) {
		return c.value
	}
	return s.defaultValue.value
}

func fmtInt(p *int) string {
	if p == nil {
		return "null"
	}
	return strconv.Itoa(*p)
}

func main() {
	ds := NewSparseSet(20)
	ds.set(1, 5)
	ds.set(2, 6)

	ds.setAll(7)

	ds.set(2, 8)
	ds.setAll(7)
	ds.set(1, 9)
	ds.set(3, 6)
	ds.set(4, 8)
	ds.setAll(10)
	ds.set(4, 88)
	ds.set(5, 80)

	ds.set(1, 7)
	ds.setAll(99)
	ds.set(6, 9)

	fmt.Println(fmtInt(ds.get(1)))
	fmt.Println(fmtInt(ds.get(2)))
	fmt.Println(fmtInt(ds.get(3)))
	fmt.Println(fmtInt(ds.get(4)))
	fmt.Println(fmtInt(ds.get(5)))
	fmt.Println(fmtInt(ds.get(6)))
}
