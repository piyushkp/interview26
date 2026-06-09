"""Port of java/AutoComplete.java -> ternary search tree (TST) autocomplete.

Original Java package: code.ds

Java's inner (non-static) classes Node/TernaryTree become module-level classes.
The Java source had NO main(); a small demonstrative __main__ is added.

Faithful detail: the Java Node constructor's `wordEnd = wordEnd` self-assignment
is a no-op bug (the field keeps its default False). It is preserved here; word
ends are flagged explicitly inside add(), so lookups still work.
"""

from typing import List, Optional


class Node:
    def __init__(self, ch: str, word_end: bool):
        self.m_char = ch
        self.left: Optional["Node"] = None
        self.center: Optional["Node"] = None
        self.right: Optional["Node"] = None
        # Java bug (faithful): `wordEnd = wordEnd` shadows the parameter, so the
        # field stays at its default; ends get set later inside add().
        word_end = word_end  # noqa: F841
        self.word_end = False


class TernaryTree:
    def __init__(self):
        self.root: Optional[Node] = None

    # private recursive insert (Java overloaded Add(s, pos, node))
    def _add(self, s: str, pos: int, node: Optional[Node]) -> Node:
        if node is None:
            node = Node(s[pos], False)
        if s[pos] < node.m_char:
            node.left = self._add(s, pos, node.left)
        elif s[pos] > node.m_char:
            node.right = self._add(s, pos, node.right)
        else:
            if pos + 1 == len(s):
                node.word_end = True
            else:
                node.center = self._add(s, pos + 1, node.center)
        return node

    # public insert (Java overloaded Add(s))
    def add(self, s: str) -> None:
        if s is None or s == "":
            raise ValueError()
        self.root = self._add(s, 0, self.root)

    def auto_complete(self, s: str) -> List[str]:
        if s is None or s == "":
            raise ValueError()
        suggestions: List[str] = []
        pos = 0
        node = self.root
        while node is not None:
            if s[pos] > node.m_char:
                node = node.right
            elif s[pos] < node.m_char:
                node = node.left
            else:
                pos += 1
                if pos == len(s):
                    if node.word_end:
                        suggestions.append(s)
                    self._find_suggestions(s, suggestions, node.center)
                    return suggestions
                node = node.center
        return suggestions

    def _find_suggestions(self, s: str, suggestions: List[str], node: Optional[Node]) -> None:
        if node is None:
            return
        if node.word_end:
            suggestions.append(s + node.m_char)
        self._find_suggestions(s, suggestions, node.left)
        self._find_suggestions(s + node.m_char, suggestions, node.center)
        self._find_suggestions(s, suggestions, node.right)

    def contains(self, s: str) -> bool:
        if s is None or s == "":
            raise ValueError()
        pos = 0
        node = self.root
        while node is not None:
            if s[pos] < node.m_char:
                node = node.left
            elif s[pos] > node.m_char:
                node = node.right
            else:
                pos += 1
                if pos == len(s):
                    return node.word_end
                node = node.center
        return False


if __name__ == "__main__":
    tree = TernaryTree()
    for word in ["cat", "car", "can", "dog", "do"]:
        tree.add(word)

    print('auto_complete("ca") ->', tree.auto_complete("ca"))
    print('auto_complete("do") ->', tree.auto_complete("do"))
    print('contains("cat")     ->', tree.contains("cat"))
    print('contains("ca")      ->', tree.contains("ca"))
    print('contains("dog")     ->', tree.contains("dog"))
