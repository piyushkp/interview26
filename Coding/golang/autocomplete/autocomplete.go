package main

import "fmt"

// node is a node in a ternary search tree.
type node struct {
	mChar               byte
	left, center, right *node
	wordEnd             bool
}

// newNode mirrors the Java constructor, including its bug: the original assigned
// the parameter to itself (wordEnd = wordEnd), so the field is always left false.
func newNode(ch byte, wordEnd bool) *node {
	return &node{mChar: ch}
}

// ternaryTree is a ternary search tree used for prefix autocomplete.
type ternaryTree struct {
	root *node
}

// addNode inserts s starting at pos into the subtree rooted at n. O(len(s)).
func (t *ternaryTree) addNode(s string, pos int, n *node) *node {
	if n == nil {
		n = newNode(s[pos], false)
	}
	if s[pos] < n.mChar {
		n.left = t.addNode(s, pos, n.left)
	} else if s[pos] > n.mChar {
		n.right = t.addNode(s, pos, n.right)
	} else {
		if pos+1 == len(s) {
			n.wordEnd = true
		} else {
			n.center = t.addNode(s, pos+1, n.center)
		}
	}
	return n
}

// Add inserts a word into the tree.
func (t *ternaryTree) Add(s string) {
	if s == "" {
		panic("illegal argument")
	}
	t.root = t.addNode(s, 0, t.root)
}

// autoComplete returns every stored word that begins with prefix s.
func (t *ternaryTree) autoComplete(s string) []string {
	if s == "" {
		panic("illegal argument")
	}
	var suggestions []string
	pos := 0
	n := t.root
	for n != nil {
		if s[pos] > n.mChar {
			n = n.right
		} else if s[pos] < n.mChar {
			n = n.left
		} else {
			pos++
			if pos == len(s) {
				if n.wordEnd {
					suggestions = append(suggestions, s)
				}
				t.findSuggestions(s, &suggestions, n.center)
				return suggestions
			}
			n = n.center
		}
	}
	return suggestions
}

func (t *ternaryTree) findSuggestions(s string, suggestions *[]string, n *node) {
	if n == nil {
		return
	}
	if n.wordEnd {
		*suggestions = append(*suggestions, s+string(n.mChar))
	}
	t.findSuggestions(s, suggestions, n.left)
	t.findSuggestions(s+string(n.mChar), suggestions, n.center)
	t.findSuggestions(s, suggestions, n.right)
}

// contains reports whether s is stored as a complete word in the tree.
func (t *ternaryTree) contains(s string) bool {
	if s == "" {
		panic("illegal argument")
	}
	pos := 0
	n := t.root
	for n != nil {
		if s[pos] < n.mChar {
			n = n.left
		} else if s[pos] > n.mChar {
			n = n.right
		} else {
			pos++
			if pos == len(s) {
				return n.wordEnd
			}
			n = n.center
		}
	}
	return false
}

func main() {
	t := &ternaryTree{}
	for _, w := range []string{"cat", "car", "card", "dog", "care", "can"} {
		t.Add(w)
	}
	fmt.Println("autocomplete 'ca':", t.autoComplete("ca"))
	fmt.Println("contains 'car':", t.contains("car"))
	fmt.Println("contains 'cab':", t.contains("cab"))
}
