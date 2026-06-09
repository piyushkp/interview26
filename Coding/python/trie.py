"""Trie (prefix tree).

Port of java/Trie.java (original package code.ds).

Provides:
  - A Node-based Trie that records, for each word, the positions where it occurs
    (contains / get_item / print_trie / output).
  - A shortest-unique-prefix finder (find_prefixes).

NOTE: The Java `trieNode` section is buggy as written -- it allocates a child
array of size Integer.MAX_VALUE and has an inverted null check in insert(). It is
re-expressed here with dict-based children so the intended logic is runnable.
This part is not exercised by the (faithful) main, which simply prints "Trie".
"""

from __future__ import annotations

from typing import Dict, List, Optional


class Node:
    """A node in the word-position Trie."""

    def __init__(self, letter: str = ""):
        # Java default char is '\u0000'; "" is used so the root contributes
        # nothing when words are reconstructed in output().
        self.letter = letter
        self.is_terminal = False
        # Java TreeMap -> dict here; iterated in sorted key order in output().
        self.children: Dict[str, "Node"] = {}
        self.positions: List[int] = []


class Trie:
    """Trie mapping each stored word to the list of positions it occurs at."""

    def __init__(self):
        self.root = Node()

    def contains(self, word: str) -> bool:
        current = self.root
        for c in word:
            nxt = current.children.get(c)
            if nxt is None:
                return False
            current = nxt
        return current.is_terminal

    def get_item(self, word: str) -> List[int]:
        """Return the (mutable) positions list for word, creating nodes as needed."""
        current = self.root
        for c in word:
            nxt = current.children.get(c)
            if nxt is None:
                nxt = Node(c)
                current.children[c] = nxt
            current = nxt
        current.is_terminal = True
        return current.positions

    def print_trie(self) -> None:
        self.output([self.root], "")

    def output(self, current_path: List[Node], indent: str) -> None:
        """Depth-first print of every stored word and its positions."""
        current = current_path[-1]
        if current.is_terminal:
            word = "".join(n.letter for n in current_path)
            print(f"{indent}{word} {current.positions}")
        for c in sorted(current.children.keys()):
            node = current.children[c]
            new_list = list(current_path)
            new_list.append(node)
            self.output(new_list, indent)


# --- Shortest unique prefixes -------------------------------------------------
# Input  = ["zebra", "dog", "duck", "dove"]   Output: dog, dov, du, z
# Time complexity O(N), where N is the total number of characters in all words.


class TrieNode:
    """Node for the unique-prefix finder (dict children; see the module note)."""

    def __init__(self):
        self.child: Dict[str, "TrieNode"] = {}
        self.freq = 0  # how many words share the prefix ending at this node


def new_trie_node() -> TrieNode:
    node = TrieNode()
    node.freq = 1
    return node


def insert(root: TrieNode, s: str) -> None:
    """Insert s, incrementing freq along the shared-prefix path."""
    p_crawl = root
    for ch in s:
        if ch not in p_crawl.child:
            p_crawl.child[ch] = new_trie_node()
        else:
            p_crawl.child[ch].freq += 1
        p_crawl = p_crawl.child[ch]


def find_prefixes_util(root: Optional[TrieNode], prefix: List[str], ind: int) -> None:
    """Print the unique prefix for each word; recurses until freq == 1."""
    if root is None:
        return
    if root.freq == 1:
        print("".join(prefix[:ind]))
        return
    for ch in sorted(root.child.keys()):
        prefix_copy = list(prefix)
        if ind < len(prefix_copy):
            prefix_copy[ind] = ch
        else:
            prefix_copy.append(ch)
        find_prefixes_util(root.child[ch], prefix_copy, ind + 1)


def find_prefixes(arr: List[str]) -> None:
    """Print the shortest prefix that uniquely identifies each word in arr."""
    root = new_trie_node()
    root.freq = 0
    for w in arr:
        insert(root, w)
    # Maximum length of an input word is assumed to be 500.
    prefix: List[str] = [""] * 500
    find_prefixes_util(root, prefix, 0)


if __name__ == "__main__":
    # Faithful to the Java main, which prints "Trie".
    print("Trie")

    # Small demonstration of the (runnable) Trie and unique-prefix finder.
    trie = Trie()
    for i, w in enumerate(["dog", "dove", "duck", "zebra"]):
        positions = trie.get_item(w)
        positions.append(i)
    print("contains('duck'):", trie.contains("duck"))
    print("contains('cat'):", trie.contains("cat"))
    print("trie contents:")
    trie.print_trie()

    print("shortest unique prefixes for [zebra, dog, duck, dove]:")
    find_prefixes(["zebra", "dog", "duck", "dove"])
