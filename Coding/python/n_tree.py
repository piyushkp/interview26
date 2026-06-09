"""Port of java/N_Tree.java -> n-ary tree (de)serialization + longest path.

Original Java package: code.ds

An n-ary (non-binary) tree is serialized in pre-order where ')' marks the end
of a node's children list. Includes a stack-based variant (serialize1 /
simple_deserialize) and a faithfully ported (intentionally quirky) longest-path
DFS that walks an undirected tree.
"""

from typing import List, Optional, Set


class NTree:
    """A node in an n-ary tree."""

    def __init__(self, c: str):
        self.data: str = c
        self.children: List["NTree"] = []

    def add_child(self, node: "NTree") -> None:
        self.children.append(node)


class NTreeCodec:
    """Serialize / deserialize an n-ary tree (was the Java class N_Tree)."""

    def __init__(self):
        self._sb: List[str] = []
        self._current_index = 0

    # --- instance serialize using a string buffer ---
    def serialize(self, root: Optional[NTree]) -> str:
        self._sb = []
        self._serialize_recursive(root)
        return "".join(self._sb)

    def _serialize_recursive(self, root: Optional[NTree]) -> None:
        if root is None:
            return
        self._sb.append(root.data)
        for node in root.children:
            self._serialize_recursive(node)
        self._sb.append(")")

    # --- instance deserialize using a running index ---
    def deserialize(self, s: str) -> Optional[NTree]:
        self._current_index = 0
        return self._deserialize_recursive(s)

    def _deserialize_recursive(self, s: str) -> Optional[NTree]:
        if self._current_index >= len(s):
            return None
        elif s[self._current_index] == ")":
            return None
        root = NTree(s[self._current_index])
        while self._current_index < len(s):
            self._current_index += 1
            child = self._deserialize_recursive(s)
            if child is None:
                break
            root.add_child(child)
        return root


# --- static helpers (stack based) ---

def serialize1(root: Optional[NTree]) -> str:
    sb: List[str] = []
    if root is not None:
        sb.append(root.data)
        sb.append(",")
        for child in root.children:
            sb.append(serialize1(child))
        sb.append(")")
    return "".join(sb)


def simple_deserialize(s: str) -> Optional[NTree]:
    root: Optional[NTree] = None
    stack: List[NTree] = []
    data: List[str] = []
    for ch in s:
        if ch == ",":
            child = NTree(data[0])
            if stack:
                stack[-1].add_child(child)
            else:
                root = child
            stack.append(child)
            data = []
        elif ch == ")":
            stack.pop()
        else:
            data.append(ch)
    return root


# --- longest path of an undirected tree (faithful port of a quirky reference) ---
_max_so_far = 0


def find_longest_path(node: NTree) -> int:
    global _max_so_far
    _max_so_far = 0
    seen: Set[int] = set()
    _dfs(node, 0, seen)
    print(_max_so_far)
    return _max_so_far


def _dfs(node: NTree, idx: int, seen: Set[int]) -> int:
    global _max_so_far
    max_first = 0
    max_second = 0
    seen.add(idx)
    for nxt in node.children:
        if ord(nxt.data) in seen:
            continue
        val = _dfs(node, ord(nxt.data), seen)
        if val > max_first:
            max_second = max_first
            max_first = val
        elif val > max_second:
            max_second = val
    _max_so_far = max(_max_so_far, max_second + max_first)
    max_first += 1  # Java: return ++maxFirst
    return max_first


if __name__ == "__main__":
    codec = NTreeCodec()
    serialized = "ABE)FK)))C)DG)H)I)J)))"
    root = codec.deserialize(serialized)
    print("input string:      ", serialized)
    print("deserialized root: ", root.data)
    print("re-serialized:     ", codec.serialize(root))
    print("serialize1:        ", serialize1(root))

    root2 = simple_deserialize(serialize1(root))
    print("simple_deserialize:", root2.data if root2 else None)

    print("longest path (quirky reference):", end=" ")
    find_longest_path(root)
