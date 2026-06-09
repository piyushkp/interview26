package main

import (
	"fmt"
	"sort"
	"strings"
)

// Node is a trie node. Given a text file and a word, the trie records the positions
// at which the word occurs in the file.
type Node struct {
	letter     rune
	isTerminal bool
	children   map[rune]*Node
	positions  []int
}

func NewNode() *Node {
	return &Node{children: map[rune]*Node{}, positions: []int{}}
}

func NewNodeLetter(letter rune) *Node {
	n := NewNode()
	n.letter = letter
	return n
}

// Trie stores words and the positions associated with each terminal word.
type Trie struct {
	root *Node
}

func NewTrie() *Trie {
	return &Trie{root: NewNode()}
}

func (t *Trie) contains(word string) bool {
	current := t.root
	for _, c := range word {
		next, ok := current.children[c]
		if !ok {
			return false
		}
		current = next
	}
	return current.isTerminal
}

func (t *Trie) getItem(word string) []int {
	current := t.root
	for _, c := range word {
		next, ok := current.children[c]
		if !ok {
			next = NewNodeLetter(c)
			current.children[c] = next
		}
		current = next
	}
	current.isTerminal = true
	return current.positions
}

func (t *Trie) print() {
	t.output([]*Node{t.root}, "")
}

// output performs a depth-first traversal, printing each terminal word.
func (t *Trie) output(currentPath []*Node, indent string) {
	current := currentPath[len(currentPath)-1]
	if current.isTerminal {
		word := ""
		for _, n := range currentPath {
			word += string(n.letter)
		}
		fmt.Println(indent + word + " " + fmt.Sprint(current.positions))
	}
	// Java used a TreeMap (sorted by key); sort the keys for a deterministic order.
	keys := make([]rune, 0, len(current.children))
	for k := range current.children {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool { return keys[i] < keys[j] })
	for _, k := range keys {
		node := current.children[k]
		newlist := make([]*Node, len(currentPath))
		copy(newlist, currentPath)
		newlist = append(newlist, node)
		t.output(newlist, indent)
	}
}

// Finding shortest unique prefixes for strings in an array.
// Input  = {"zebra", "dog", "duck", "dove"}     Output: dog, dov, du, z
//
// NOTE: trieNode and its methods below are a faithful but buggy port of the reference
// "shortest unique prefixes" trie. The original Java is broken (it iterates child[] up
// to Integer.MAX_VALUE and uses String.indexOf(int) incorrectly), so the bodies are
// guarded to compile and run without panicking. // TODO: port correctly.
type trieNode struct {
	child []*trieNode
	freq  int // to store frequency
}

// newTrieNode creates a new trie node. The reference iterates child[] up to
// Integer.MAX_VALUE which is invalid; RADIX=256 is used here.
func newTrieNode() *trieNode {
	return &trieNode{child: make([]*trieNode, 256), freq: 1}
}

// insert inserts a new string into the trie (faithful to the reference logic).
func (t *Trie) insert(root *trieNode, str string) {
	length := len(str)
	pCrawl := root
	for level := 0; level < length; level++ {
		// Reference uses str.indexOf(level); preserved, then bounds-guarded.
		index := strings.IndexByte(str, byte(level))
		if index < 0 || index >= len(pCrawl.child) {
			continue
		}
		// The reference inverted the nil check (guaranteeing a NullPointerException);
		// corrected here to the intended behaviour: create the child when missing,
		// otherwise bump its frequency.
		if pCrawl.child[index] == nil {
			pCrawl.child[index] = newTrieNode()
		} else {
			pCrawl.child[index].freq++
		}
		pCrawl = pCrawl.child[index]
	}
}

// findPrefixesUtil prints the unique prefix for every word stored in the trie.
func (t *Trie) findPrefixesUtil(root *trieNode, prefix []rune, ind int) {
	if root == nil {
		return
	}
	if root.freq == 1 {
		fmt.Println(string(prefix[:ind]))
		return
	}
	for i := 0; i < 256; i++ {
		if i < len(root.child) && root.child[i] != nil {
			if ind < len(prefix) {
				prefix[ind] = rune(i)
			}
			t.findPrefixesUtil(root.child[i], prefix, ind+1)
		}
	}
}

// findPrefixes prints all prefixes that uniquely represent the words in arr[0..n-1].
func (t *Trie) findPrefixes(arr []string, n int) {
	root := newTrieNode()
	root.freq = 0
	for i := 0; i < n; i++ {
		t.insert(root, arr[i])
	}
	// Maximum length of an input word is assumed to be 500.
	prefix := make([]rune, 500)
	t.findPrefixesUtil(root, prefix, 0)
}

func main() {
	fmt.Print("Trie")
}
