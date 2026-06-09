package main

import "errors"

// ---------------------------------------------------------------------------
// Singleton
// ---------------------------------------------------------------------------

// Singleton demonstrates lazy single-instance creation.
type Singleton struct {
	uniqInstance *Singleton
}

func (s *Singleton) getInstance() *Singleton {
	if s.uniqInstance == nil {
		s.uniqInstance = &Singleton{}
	}
	return s.uniqInstance
}

// ---------------------------------------------------------------------------
// Iterable that reads a file (byte stream)
// ---------------------------------------------------------------------------

// Line holds a line number and its raw data.
type Line struct {
	lineNumber int
	lineData   []byte
}

type fileReaderIterable struct {
	data []byte
}

func (f *fileReaderIterable) iterator() *fileReaderIterator {
	return newFileReaderIterator(f.data)
}

type fileReaderIterator struct {
	data   []byte
	buffer []byte
}

func newFileReaderIterator(dat []byte) *fileReaderIterator {
	return &fileReaderIterator{data: dat}
}

func (f *fileReaderIterator) tryGetNext() {
	if len(f.buffer) == 0 {
		for _, item := range f.data {
			f.buffer = append(f.buffer, item)
		}
	}
}

func (f *fileReaderIterator) hasNext() bool {
	f.tryGetNext()
	return len(f.buffer) > 0
}

func (f *fileReaderIterator) next() (byte, error) {
	if !f.hasNext() {
		return 0, errors.New("Nothing left")
	}
	b := f.buffer[0]
	f.buffer = f.buffer[1:]
	return b, nil
}

func (f *fileReaderIterator) remove() {
	panic("It is read-only")
}

// ---------------------------------------------------------------------------
// 2D Iterator with remove() (Airbnb)
// Traverse a 2-D int array from left to right and top to bottom.
// ---------------------------------------------------------------------------

type twoDArrayIterator struct {
	array   [][]int
	rowID   int
	colID   int
	numRows int
}

func newTwoDArrayIterator(array [][]int) *twoDArrayIterator {
	return &twoDArrayIterator{array: array, numRows: len(array)}
}

func (t *twoDArrayIterator) hasNext() bool {
	if len(t.array) == 0 {
		return false
	}
	for t.rowID < t.numRows && len(t.array[t.rowID]) == 0 {
		t.rowID++
	}
	return t.rowID < t.numRows
}

func (t *twoDArrayIterator) next() int {
	ret := t.array[t.rowID][t.colID]
	t.colID++
	if t.colID == len(t.array[t.rowID]) {
		t.rowID++
		t.colID = 0
	}
	return ret
}

func (t *twoDArrayIterator) remove() {
	var listToRemove []int
	var rowToRemove, colToRemove int
	// Case 1: the element to remove is the last element of the row.
	if t.colID == 0 {
		rowToRemove = t.rowID - 1
		listToRemove = t.array[rowToRemove]
		colToRemove = len(listToRemove) - 1
		t.array[rowToRemove] = append(listToRemove[:colToRemove], listToRemove[colToRemove+1:]...)
	} else { // Case 2: the element to remove is not the last element.
		rowToRemove = t.rowID
		listToRemove = t.array[rowToRemove]
		colToRemove = t.colID - 1
		t.array[rowToRemove] = append(listToRemove[:colToRemove], listToRemove[colToRemove+1:]...)
	}
	// If the list to remove became empty, drop the row.
	if len(t.array[rowToRemove]) == 0 {
		t.array = append(t.array[:rowToRemove], t.array[rowToRemove+1:]...)
		t.rowID--
	}
	if t.colID != 0 {
		t.colID--
	}
}

// ---------------------------------------------------------------------------
// Robot circular path check
// G - Go one unit, L - Turn left, R - Turn right.
// ---------------------------------------------------------------------------

// isCircular returns true if the given path returns the robot to the origin.
func isCircular(path []byte) bool {
	const N, E, S, W = 0, 1, 2, 3
	// Start at (0, 0) facing North.
	x, y := 0, 0
	dir := N
	for i := 0; i < len(path); i++ {
		move := path[i]
		if move == 'R' {
			dir = (dir + 1) % 4
		} else if move == 'L' {
			dir = (4 + dir - 1) % 4
		} else { // move == 'G'
			if dir == N {
				y++
			} else if dir == E {
				x++
			} else if dir == S {
				y--
			} else { // dir == W
				x--
			}
		}
	}
	return x == 0 && y == 0
}
