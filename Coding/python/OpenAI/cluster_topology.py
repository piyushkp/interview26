"""Answer topology queries on a cluster of machines shaped as a rooted tree.

The tree is given as a parent array: parents[i] is the parent of node i, and
the single node with parent -1 is the root. Node IDs are 0..n-1.

ClusterTopologyQueries(parents) builds the tree; query(command) returns a
string:
  - "count":    the number of nodes.
  - "topology": a nested string of the tree. A leaf is written as its id
                ("4"); a node with children is "id(c1,c2,...)" with children
                in ascending id order, e.g. "0(1(3(5),4),2)".
"""


# Approach (in plain terms):
#   From the parent array we build, for each node, the list of its children.
#   Scanning ids 0..n-1 in order and appending each to its parent's list means
#   every children list is already in ascending id order for free. "count" is
#   simply how many nodes there are. "topology" walks the tree from the root:
#   a node with no children is written as its id; otherwise it is written as
#   "id(...)" with its rendered children joined by commas - the recursion
#   mirrors the nested shape of the output.
#   Data structures used:
#     - list of lists (children) - children[i] holds node i's children in
#       ascending id order (dense ids 0..n-1 make a list ideal).
#     - the call stack (recursion) - renders each subtree, matching the
#       nested "id(...)" structure.
class ClusterTopologyQueries:

    def __init__(self, parents):
        """Build the tree (each node's children) from the parent array."""
        # n = number of nodes.
        # Time: O(n) - one pass to bucket children. Space: O(n) - the lists.
        self._count = len(parents)
        self._children = []
        for _ in range(self._count):
            self._children.append([])
        self._root = -1
        for node in range(self._count):
            parent = parents[node]
            if parent == -1:
                self._root = node
            else:
                # scanning nodes in order keeps each list ascending for free
                self._children[parent].append(node)

    def query(self, command):
        """Run one command ("count" or "topology") and return a string."""
        # Time: O(1) dispatch (plus the command's own cost). Space: O(1).
        if command == "count":
            return self._count_query()
        if command == "topology":
            return self._topology_query()
        raise ValueError(f"Unknown command: {command}")

    def _count_query(self):
        """Total number of nodes, as a string."""
        # Time: O(1), Space: O(1).
        return str(self._count)

    def _topology_query(self):
        """Nested string of the whole tree, starting at the root."""
        # n = number of nodes.
        # Time: O(n) - renders each node once. Space: O(n) - output + stack.
        if self._root == -1:
            return ""            # empty tree (no root) -> nothing to render
        return self._render(self._root)

    def _render(self, node):
        """Render one subtree: 'id' for a leaf, else 'id(child,child,...)'."""
        # Time: O(size of subtree). Space: O(depth) - the recursion.
        kids = self._children[node]
        if not kids:
            return str(node)
        parts = []
        for kid in kids:
            parts.append(self._render(kid))
        return f"{node}({','.join(parts)})"


if __name__ == "__main__":
    # ----- Example from the problem statement -----
    cluster = ClusterTopologyQueries([-1, 0, 0, 1, 1, 3])
    print(cluster.query("count"))      # 6
    print(cluster.query("topology"))   # 0(1(3(5),4),2)

    # ----- A single node (root only) -----
    solo = ClusterTopologyQueries([-1])
    print(solo.query("count"))         # 1
    print(solo.query("topology"))      # 0

    # ----- A straight chain 0 -> 1 -> 2 -> 3 -----
    chain = ClusterTopologyQueries([-1, 0, 1, 2])
    print(chain.query("topology"))     # 0(1(2(3)))

    # ----- Root is not id 0; a wide root with several leaves -----
    star = ClusterTopologyQueries([2, 2, -1, 2, 2])
    print(star.query("count"))         # 5
    print(star.query("topology"))      # 2(0,1,3,4)
