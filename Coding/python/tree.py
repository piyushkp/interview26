"""Idiomatic Python 3 port of java/Tree.java (original package code.ds).

Interview / DSA reference implementation covering binary trees and BSTs:
traversals, views, LCA, diameter, path sums, serialization, balancing,
successors, and assorted tree puzzles.

Java overloaded methods were renamed (Python has no overloading) and Java
collections were mapped to Python equivalents:
  Stack        -> list (append / pop)
  Queue/Deque  -> collections.deque (append / popleft)
  PriorityQueue/heap helpers -> plain lists
  javafx.util.Pair -> tuple

Some methods in the original are intentionally buggy (e.g. ``Queue q = null``
followed by ``q.add(...)``). These are ported faithfully and would raise at
runtime if invoked; they are not exercised by the ``__main__`` demo.
"""

from collections import deque

INT_MIN = -2147483648
INT_MAX = 2147483647


# ---------------------------------------------------------------------------
# Node / helper classes (Java nested classes -> module-level classes)
# ---------------------------------------------------------------------------
class Node:
    def __init__(self, data=0):
        self.data = data
        self.left = None
        self.right = None
        self.parent = None
        self.isVisited = False


class Node1:
    """Node variant used by the iterative diameter algorithm."""

    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.maxDistance = 0
        self.rHeight = 0
        self.lHeight = 0


class BNode:
    """Node wrapper carrying the valid (left, right) value boundaries."""

    def __init__(self, n, left, right):
        self.n = n
        self.left = left
        self.right = right


class DLL:
    """Doubly linked list node used for vertical-sum computation."""

    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class NodeT:
    """BST node that also tracks the size of its left subtree (lCount)."""

    def __init__(self):
        self.data = 0
        self.lCount = 0
        self.left = None
        self.right = None


class RankNode:
    """Supports stream rank queries (track + getRank)."""

    def __init__(self, d):
        self.left_size = 0
        self.left = None
        self.right = None
        self.data = d

    def insert(self, d):
        if d <= self.data:
            if self.left is not None:
                self.left.insert(d)
            else:
                self.left = RankNode(d)
            self.left_size += 1
        else:
            if self.right is not None:
                self.right.insert(d)
            else:
                self.right = RankNode(d)

    def getRank(self, d):
        if d == self.data:
            return self.left_size
        elif d < self.data:
            if self.left is None:
                return -1
            return self.left.getRank(d)
        else:
            right_rank = -1 if self.right is None else self.right.getRank(d)
            if right_rank == -1:
                return -1
            return self.left_size + 1 + right_rank


class Relation:
    """child -> parent relationship used to rebuild a binary tree."""

    def __init__(self, parent=None, child=None, isLeft=False):
        self.parent = parent
        self.child = child
        self.isLeft = isLeft


class NTree:
    """Minimal N-ary tree node (stand-in for N_Tree.NTree)."""

    def __init__(self, data):
        self.data = data
        self.children = []

    def addChild(self, child):
        self.children.append(child)


class BSTIterator:
    """Iterator returning the next smallest BST value in O(h) memory."""

    def __init__(self, root):
        self.stack = []
        self._push_all(root)

    def hasNext(self):
        return len(self.stack) > 0

    def next(self):
        tmp_node = self.stack.pop()
        self._push_all(tmp_node.right)
        return tmp_node.data

    def _push_all(self, node):
        while node is not None:
            self.stack.append(node)
            node = node.left


class BSTIteratorUsingMorris:
    """O(1) next()/hasNext() Morris-based iterator.

    Faithful to the Java bug ``root = root;`` which never assigns the field, so
    ``self.root`` stays None and only ``self.cur`` is used.
    """

    def __init__(self, root):
        root = root  # Java: `root = root;` (assigns the parameter to itself)
        self.root = None
        self.cur = root

    def hasNext(self):
        return self.cur is not None

    def next(self):
        r = 0
        while self.cur is not None:
            if self.cur.left is None:
                r = self.cur.data
                self.cur = self.cur.right
                break
            else:
                node = self.cur.left
                while node.right is not None and node.right != self.cur:
                    node = node.right
                if node.right is None:
                    node.right = self.cur
                    self.cur = self.cur.left
                else:
                    node.right = None
                    r = self.cur.data
                    self.cur = self.cur.right
                    break
        return r


class Tree:
    # ----- static (class-level) state -------------------------------------
    countN = 0
    preIndex = 0
    diameter = 0
    path = None          # Stack<Node> for printDiameterOfBinaryTree
    maxSoFar = 0
    _path = [0, 0]
    maxSize = 1
    currentIndex = 0

    def __init__(self):
        self.root = None
        self.HD_OFFSET = 16
        self.prev = None
        self.head = None
        self.splitter = ","
        self.deepestlevel = 0
        self.value = 0
        self.count = 0

    # ----- insertion / search ---------------------------------------------
    def insert(self, root, value):
        """Insert a node in a BST (recursive; mirrors the original)."""
        if root is None:
            newNode = Node()
            newNode.data = value
            root = newNode
        if value < root.data:
            self.insert(root.left, value)
        elif value > root.data:
            self.insert(root.right, value)

    def insertItr(self, root, data):
        """Insert a node iteratively into a BST."""
        newNode = Node()
        newNode.data = data
        if root is None:
            root.data = data
        else:
            current = root
            while True:
                if data < current.data:
                    current = current.left
                    if current is None:
                        current.left = newNode
                        return
                else:
                    current = current.right
                    if current is None:
                        current.right = newNode
                        return

    def search(self, root, data):
        """Recursive search in a BST."""
        if root is None:
            return None
        if root.data == data:
            return root
        if data < root.data:
            self.search(root.left, data)
        elif data > root.data:
            self.search(root.right, data)
        return None

    # ----- DFS / BFS ------------------------------------------------------
    def DFS(self, root, target):
        """Depth first search, recursive."""
        if root is None:
            return False
        if root.data == target:
            return True
        return self.DFS(root.left, target) or self.DFS(root.right, target)

    def DFSIterative(self, root, target):
        """Depth first search, iterative."""
        if root is None:
            return False
        _stack = []
        _stack.append(root)
        while len(_stack) > 0:
            temp = _stack.pop()
            if temp.data == target:
                return True
            if temp.right is not None:
                _stack.append(temp.right)
            if temp.left is not None:
                _stack.append(temp.left)
        return False

    def BFS(self, root, target):
        """Breadth first / level order search."""
        if root is None:
            return False
        _queue = deque()
        _queue.append(root)
        while len(_queue) > 0:
            tmp = _queue.popleft()
            if tmp.data == target:
                return True
            if tmp.left is not None:
                _queue.append(tmp.left)
            if tmp.right is not None:
                _queue.append(tmp.right)
        return False

    # ----- level / vertical order printing --------------------------------
    @staticmethod
    def printLevels(root):
        """Print a binary tree level by level, one level per line."""
        if root is None:
            return
        q = deque()
        q.append(root)
        while len(q) > 0:
            nodeCount = len(q)
            while nodeCount > 0:
                node = q.popleft()
                print(node.data, end="")
                if node.left is not None:
                    q.append(node.left)
                if node.right is not None:
                    q.append(node.right)
                nodeCount -= 1
            print()

    @staticmethod
    def printVerticalOrder(root):
        """Vertical order traversal, left to right. Time O(n), space O(n)."""
        if root is None:
            return
        m = {}
        hd = 0
        que = deque()
        que.append((root, hd))
        mx, mn = 0, 0
        while que:
            node, hd = que.popleft()
            m.setdefault(hd, []).append(node.data)
            if node.left is not None:
                que.append((node.left, hd - 1))
                mn = min(mn, hd - 1)
            if node.right is not None:
                que.append((node.right, hd + 1))
                mx = max(mx, hd + 1)
        for i in range(mn, mx + 1):
            print(m.get(i))

    def reverseLevelOrder(self, root):
        """Reverse level order. Faithful to Java's null-queue bug."""
        S = []
        Q = None  # Java: `Queue<Node> Q = null;`
        Q.append(root)
        while len(Q) > 0:
            root = Q[0]
            Q.popleft()
            S.append(root)
            if root.right is not None:
                Q.append(root.right)  # right enqueued before left
            if root.left is not None:
                Q.append(root.left)
        while len(S) > 0:
            root = S[-1]
            print(root.data, end="")
            S.pop()

    def spiralLevelOrderTraversal(self, root):
        """Print nodes in spiral (zig-zag) order."""
        if root is None:
            return
        _stack1 = []
        _stack2 = []
        _stack1.append(root)
        while _stack1 or _stack2:
            while _stack1:
                node = _stack1.pop()
                print(node.data, end="")
                if node.right is not None:
                    _stack2.append(node.right)
                if node.left is not None:
                    _stack2.append(node.left)
            while _stack2:
                node = _stack2.pop()
                print(node.data, end="")
                if node.left is not None:
                    _stack1.append(node.left)
                if node.right is not None:
                    _stack1.append(node.right)

    # ----- traversals -----------------------------------------------------
    def inOrder(self, root):
        if root is not None:
            self.inOrder(root.left)
            print(root.data, end="")
            self.inOrder(root.right)

    def preOrder(self, root):
        if root is not None:
            print(root.data, end="")
            self.preOrder(root.left)
            self.preOrder(root.right)

    def MorrisTraversal(self, root):
        """In-order traversal using Morris (threaded) traversal, O(1) space."""
        if root is None:
            return
        current = root
        while current is not None:
            if current.left is None:
                print(str(current.data) + " ", end="")
                current = current.right
            else:
                pre = current.left
                while pre.right is not None and pre.right != current:
                    pre = pre.right
                if pre.right is None:
                    pre.right = current
                    current = current.left
                else:
                    pre.right = None
                    print(str(current.data) + " ", end="")
                    current = current.right

    def inorder(self, root):
        """Iterative in-order traversal."""
        node = root
        stack = []
        while stack or node is not None:
            if node is not None:
                stack.append(node)
                node = node.left
            else:
                node = stack.pop()
                print(str(node.data) + " ", end="")
                node = node.right

    def iterativePreorder(self, root):
        """Iterative pre-order traversal."""
        if root is None:
            return
        nodeStack = []
        nodeStack.append(root)
        while len(nodeStack) > 0:
            node = nodeStack[-1]
            print(node.data, end="")
            nodeStack.pop()
            if node.right is not None:
                nodeStack.append(node.right)
            if node.left is not None:
                nodeStack.append(node.left)

    def postOrder(self, root):
        if root is not None:
            self.postOrder(root.left)
            self.postOrder(root.right)
            print(root.data, end="")

    def postOrderIterative(self, node):
        """Iterative post-order traversal using a single stack."""
        S = []
        if node is None:
            return
        S.append(node)
        prev = None
        while S:
            current = S[-1]
            if prev is None or prev.left == current or prev.right == current:
                if current.left is not None:
                    S.append(current.left)
                elif current.right is not None:
                    S.append(current.right)
                else:
                    S.pop()
                    print(current.data, end="")
            elif current.left == prev:
                if current.right is not None:
                    S.append(current.right)
                else:
                    S.pop()
                    print(current.data, end="")
            elif current.right == prev:
                S.pop()
                print(current.data, end="")
            prev = current

    # ----- construct from traversals --------------------------------------
    def build_tree_from_in_pre(self, in_arr, pre, inStrt, inEnd):
        """Construct a tree from inorder + preorder traversals.

        (Java: buildTree(char in[], char pre[], int inStrt, int inEnd))
        """
        if inStrt > inEnd:
            return None
        tNode = Node(pre[Tree.preIndex])
        Tree.preIndex += 1
        if inStrt == inEnd:
            return tNode
        inIndex = self.search_index(in_arr, inStrt, inEnd, tNode.data)
        tNode.left = self.build_tree_from_in_pre(in_arr, pre, inStrt, inIndex - 1)
        tNode.right = self.build_tree_from_in_pre(in_arr, pre, inIndex + 1, inEnd)
        return tNode

    def search_index(self, arr, start, end, value):
        """Index of value in arr[start..end] (assumes value present)."""
        i = start
        for i in range(start, end + 1):
            if arr[i] == value:
                return i
        return i

    # ----- deletion -------------------------------------------------------
    def delete(self, key):
        """Delete a node from a binary tree (faithful port)."""
        parent = None
        nodetoDelete = None
        if self.root.data == key:
            nodetoDelete = self.root
        else:
            parent = self.getParent(self.root, key, nodetoDelete)
        if nodetoDelete.left is None and nodetoDelete.right is None:
            if parent is not None:
                if parent.left == nodetoDelete:
                    parent.left = None
                else:
                    parent.right = None
            else:
                self.root = None
        elif nodetoDelete.left is None:
            if parent is not None:
                if parent.left == nodetoDelete:
                    parent.left = nodetoDelete.right
                else:
                    parent.right = nodetoDelete.right
            else:
                self.root = nodetoDelete.right
        elif nodetoDelete.right is None:
            if parent is not None:
                if parent.left == nodetoDelete:
                    parent.left = nodetoDelete.left
                else:
                    parent.right = nodetoDelete.left
            else:
                self.root = nodetoDelete.left
        else:
            successor = self.FinMinValue(nodetoDelete.right)
            if parent is not None:
                if parent.right == nodetoDelete:
                    parent.right = successor
                else:
                    parent.left = successor
            else:
                self.root = successor

    def getParent(self, root, target, NodetoDelete):
        if root is not None:
            if root.left is not None:
                if root.left.data == target:
                    NodetoDelete = root.left
                    return root
            if root.right is not None:
                if root.right.data == target:
                    NodetoDelete = root.right
                    return root
            self.getParent(root.left, target, NodetoDelete)
            self.getParent(root.right, target, NodetoDelete)
        return root

    def FinMinValue(self, startNode):
        parent = None
        while startNode.left is not None:
            parent = startNode
            startNode = startNode.left
        if parent is not None:
            parent.left = None
        return startNode

    def deleteRec(self, root, key):
        """Delete key from a BST and return the new root."""
        if root is None:
            return root
        if key < root.data:
            root.left = self.deleteRec(root.left, key)
        elif key > root.data:
            root.right = self.deleteRec(root.right, key)
        else:
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            root.data = self.minValuedata(root.right)
            root.right = self.deleteRec(root.right, root.data)
        return root

    def minValuedata(self, root):
        minv = root.data
        while root.left is not None:
            minv = root.left.data
            root = root.left
        return minv

    # ----- lowest common ancestor -----------------------------------------
    def FindLCA(self, root, one, two):
        """LCA in a BST."""
        while root is not None:
            if root.data < one.data and root.data < two.data:
                return root.right
            elif root.data > one.data and root.data > two.data:
                return root.left
            else:
                return root
        return None

    def FindLCA_BTree(self, root, one, two):
        """LCA of a binary tree using parent pointers and a hash set."""
        hash_set = set()
        while one is not None or two is not None:
            if one is not None:
                if one in hash_set:
                    return one
                else:
                    hash_set.add(one)
                one = one.parent
            if two is not None:
                if two in hash_set:
                    return two
                else:
                    hash_set.add(two)
                two = two.parent
        return None

    def FindLCA_Best(self, root, one, two):
        """LCA via height alignment, no extra space."""
        h1 = self.getHeight(one)
        h2 = self.getHeight(two)
        if h1 > h2:
            h1 ^= h2
            h2 ^= h1
            h1 ^= h2
            self.swap(one.data, two.data)
        dh = h2 - h1
        for _ in range(dh):
            two = two.parent
        while one is not None and two is not None:
            if one.data == two.data:
                return one
            one = one.parent
            two = two.parent
        return None

    def getHeight(self, node):
        height = 0
        while node is not None:
            height += 1
            node = node.parent
        return height

    @staticmethod
    def FindLowestCommonAncestor(n, n1, n2):
        """LCA without parent pointers."""
        if n is None:
            return None
        if n.data == n1 or n.data == n2:
            return n
        left = Tree.FindLowestCommonAncestor(n.left, n1, n2)
        right = Tree.FindLowestCommonAncestor(n.right, n1, n2)
        if left is None and right is None:
            return None
        if left is not None and right is not None:
            return n
        if left is not None:
            return left
        if right is not None:
            return right
        return None

    @staticmethod
    def findFirstCommonAncestor(root, n1, n2):
        if root is None:
            return None
        if not Tree.contains(root, n1) or not Tree.contains(root, n2):
            return None
        if root == n1 or root == n2:
            return root
        n1OnLeft = Tree.contains(root.left, n1)
        n2OnLeft = Tree.contains(root.left, n2)
        if n1OnLeft != n2OnLeft:
            return root
        elif n1OnLeft and n2OnLeft:
            return Tree.findFirstCommonAncestor(root.left, n1, n2)
        elif not n1OnLeft and not n2OnLeft:
            return Tree.findFirstCommonAncestor(root.right, n1, n2)
        return None

    @staticmethod
    def contains(root, n):
        if root is None:
            return False
        if root == n:
            return True
        return Tree.contains(root.left, n) or Tree.contains(root.right, n)

    # ----- diameter -------------------------------------------------------
    @staticmethod
    def iterativeDiameter(root):
        """Iterative diameter using two stacks (operates on Node1)."""
        if root is None:
            return 0
        S = []
        O = []
        maxDistance = 0
        S.append(root)
        while S:
            node = S.pop()
            O.append(node)
            if node.left is not None:
                S.append(node.left)
            if node.right is not None:
                S.append(node.right)
        while O:
            node = O.pop()
            if node.left is None:
                node.lHeight = 1
                node.maxDistance = 0
            else:
                node.lHeight = max(node.left.lHeight, node.left.rHeight) + 1
            if node.right is None:
                node.rHeight = 1
                node.maxDistance = 0
            else:
                node.rHeight = max(node.right.rHeight, node.right.lHeight) + 1
            if node.left is not None and node.right is not None:
                temp = node.lHeight + node.rHeight - 1
                node.maxDistance = temp
                if maxDistance < temp:
                    maxDistance = temp
        return maxDistance

    @staticmethod
    def diameterOfBinaryTree(root):
        Tree.maxDepth(root)
        return Tree.diameter

    @staticmethod
    def maxDepth(root):
        if root is None:
            return 0
        left = Tree.maxDepth(root.left)
        right = Tree.maxDepth(root.right)
        Tree.diameter = max(Tree.diameter, left + right + 1)
        return max(left, right) + 1

    @staticmethod
    def printDiameterOfBinaryTree(root):
        """Print the longest path of a binary tree (directed)."""
        Tree.longestPath(root)
        s = ""
        while Tree.path:
            s += str(Tree.path.pop().data) + " "
        return s

    @staticmethod
    def longestPath(root):
        if root is None:
            return []
        l = Tree.longestPath(root.left)
        r = Tree.longestPath(root.right)
        if len(l) + len(r) + 1 > Tree.diameter:
            Tree.diameter = len(l) + len(r) + 1
            tmp = list(l)
            tmp.append(root)
            tmp.extend(r)
            Tree.path = tmp
        l.append(root)
        r.append(root)
        return l if len(l) > len(r) else r

    @staticmethod
    def longestPathNaryTree(root):
        """Longest path (between any two nodes) in an undirected N-ary tree."""
        Tree.longestPathNaryTreeUtil(root, set())
        print("start: - " + str(Tree._path[0]) + " End: - " + str(Tree._path[1]))
        return Tree.maxSoFar

    @staticmethod
    def longestPathNaryTreeUtil(root, visited):
        large = 0
        small = 0
        visited.add(root)
        for nxt in root.children:
            if nxt not in visited:
                val = Tree.longestPathNaryTreeUtil(nxt, visited)
                if val > large:
                    small = large
                    large = val
                    Tree._path[1] = Tree._path[0]
                    Tree._path[0] = nxt.data
                elif val > small and val != large:
                    small = val
                    Tree._path[1] = nxt.data
        Tree.maxSoFar = max(Tree.maxSoFar, small + large)
        return large + 1

    # ----- BST validation -------------------------------------------------
    @staticmethod
    def isValidBST(root):
        """Validate a BST via Morris traversal. O(n) time, O(1) space."""
        pre = None
        cur = root
        while cur is not None:
            if cur.left is None:
                if pre is not None and pre.data >= cur.data:
                    return False
                pre = cur
                cur = cur.right
            else:
                tmp = cur.left
                while tmp.right is not None and tmp.right != cur:
                    tmp = tmp.right
                if tmp.right is None:
                    tmp.right = cur
                    cur = cur.left
                else:
                    tmp.right = None
                    if pre is not None and pre.data >= cur.data:
                        return False
                    pre = cur
                    cur = cur.right
        return True

    @staticmethod
    def validateBST(root, min_val, max_val):
        if root is None:
            return True
        if root.data <= min_val or root.data >= max_val:
            return False
        return (Tree.validateBST(root.left, min_val, root.data)
                and Tree.validateBST(root.right, root.data, max_val))

    @staticmethod
    def isValidBST1(root):
        """Iterative BST validation using value boundaries."""
        if root is None:
            return True
        queue = deque()
        queue.append(BNode(root, float("-inf"), float("inf")))
        while queue:
            b = queue.popleft()
            if b.n.data <= b.left or b.n.data >= b.right:
                return False
            if b.n.left is not None:
                queue.append(BNode(b.n.left, b.left, b.n.data))
            if b.n.right is not None:
                queue.append(BNode(b.n.right, b.n.data, b.right))
        return True

    # ----- second largest / kth smallest ----------------------------------
    @staticmethod
    def findSecondLargestValueInBST(root):
        """Second largest element in a BST. O(h)."""
        pre = root
        cur = root
        while cur.right is not None:
            pre = cur
            cur = cur.right
        if cur.left is not None:
            cur = cur.left
            while cur.right is not None:
                cur = cur.right
            secondMax = cur.data
        else:
            if cur == root and pre == root:
                secondMax = INT_MIN
            else:
                secondMax = pre.data
        return secondMax

    def secondLargestUtil(self, root, c):
        """Recursive 2nd largest via reverse in-order."""
        if root is None or c >= 2:
            return
        self.secondLargestUtil(root.right, c)
        c += 1
        if c == 2:
            print("2nd largest element is " + str(root.data), end="")
            return
        self.secondLargestUtil(root.left, c)

    def KSmallestUsingMorris(self, root, k):
        """K-th smallest in a BST using Morris traversal, O(1) space."""
        count = 0
        ksmall = INT_MIN
        curr = root
        while curr is not None:
            if curr.left is None:
                count += 1
                if count == k:
                    ksmall = curr.data
                curr = curr.right
            else:
                pre = curr.left
                while pre.right is not None and pre.right != curr:
                    pre = pre.right
                if pre.right is None:
                    pre.right = curr
                    curr = curr.left
                else:
                    pre.right = None
                    count += 1
                    if count == k:
                        ksmall = curr.data
                    curr = curr.right
        return ksmall

    def findKthNode_SMALLEST(self, root, k):
        """K-th smallest using left subtree sizes."""
        if root is None:
            return None
        leftSize = self.findLeftTreeSize(root.left)
        if leftSize == k - 1:
            return root
        elif leftSize < k - 1:
            self.findKthNode_SMALLEST(root.left, k)
        else:
            self.findKthNode_SMALLEST(root.right, k - leftSize - 1)
        return None

    def findLeftTreeSize(self, root):
        if root is None:
            return 0
        return 1 + self.findLeftTreeSize(root.left) + self.findLeftTreeSize(root.right)

    def insert_node(self, root, node):
        """Insert into a NodeT tree maintaining left subtree counts."""
        pTraverse = root
        currentParent = root
        while pTraverse is not None:
            currentParent = pTraverse
            if node.data < pTraverse.data:
                pTraverse.lCount += 1
                pTraverse = pTraverse.left
            else:
                pTraverse = pTraverse.right
        if root is None:
            root = node
        elif node.data < currentParent.data:
            currentParent.left = node
        else:
            currentParent.right = node
        return root

    def k_smallest_element(self, root, k):
        ret = -1
        if root is not None:
            pTraverse = root
            while pTraverse is not None:
                if (pTraverse.lCount + 1) == k:
                    ret = pTraverse.data
                    break
                elif k > pTraverse.lCount:
                    k = k - (pTraverse.lCount + 1)
                    pTraverse = pTraverse.right
                else:
                    pTraverse = pTraverse.left
        return ret

    # ----- construct BST --------------------------------------------------
    @staticmethod
    def sortedArraytoBST(arr, start, end):
        """Construct a balanced BST from a sorted array."""
        if end < start:
            return None
        mid = start + (end - start) // 2
        tree = Node()
        tree.data = arr[mid]
        tree.left = Tree.sortedArraytoBST(arr, start, mid - 1)
        tree.right = Tree.sortedArraytoBST(arr, mid + 1, end)
        return tree

    def constructBST(self, pre):
        """O(n) construction of a BST from its preorder traversal."""
        root = Node(pre[0])
        s = []
        s.append(root)
        for i in range(1, len(pre)):
            temp = None
            while s and pre[i] > s[-1].data:
                temp = s.pop()
            if temp is not None:
                temp.right = Node(pre[i])
                s.append(temp.right)
            else:
                temp = s[-1]
                temp.left = Node(pre[i])
                s.append(temp.left)
        return root

    @staticmethod
    def inOrderFromPreOrderBST(pre):
        """Print the inorder traversal given a BST preorder traversal."""
        if pre is None:
            return
        if len(pre) < 2:
            print(pre[0])
        s = []
        s.append(pre[0])
        for i in range(1, len(pre)):
            while s and pre[i] > s[-1]:
                print(s.pop())
            s.append(pre[i])
        print(s.pop())

    # ----- correct a swapped BST ------------------------------------------
    def CorrectBST(self, root):
        first = None
        middle = None
        last = None
        prev = None
        self.CorrectBSTUtil(root, first, middle, last, prev)
        if first is not None and last is not None:
            self.swap(first.data, last.data)
        elif first is not None and middle is not None:
            self.swap(first.data, middle.data)

    def CorrectBSTUtil(self, root, first, middle, last, prev):
        if root is not None:
            self.CorrectBSTUtil(root.left, first, middle, last, prev)
            if prev is not None and root.data < prev.data:
                if first is None:
                    first = prev
                    middle = root
                else:
                    last = root
            prev = root
            self.CorrectBSTUtil(root.right, first, middle, last, prev)

    def swap(self, a, b):
        """No-op swap (Java pass-by-value semantics preserved)."""
        t = a
        a = b
        b = t

    # ----- path sums ------------------------------------------------------
    @staticmethod
    def countPathsWithSum(node, targetSum, runningSum, pathCount):
        """Count downward paths summing to targetSum. O(n) time."""
        if node is None:
            return 0
        runningSum += node.data
        s = runningSum - targetSum
        totalPaths = pathCount.get(s, 0)
        if runningSum == targetSum:
            totalPaths += 1
        Tree.incrementHashTable(pathCount, runningSum, 1)
        totalPaths += Tree.countPathsWithSum(node.left, targetSum, runningSum, pathCount)
        totalPaths += Tree.countPathsWithSum(node.right, targetSum, runningSum, pathCount)
        Tree.incrementHashTable(pathCount, runningSum, -1)
        return totalPaths

    @staticmethod
    def incrementHashTable(hashTable, key, delta):
        newCount = hashTable.get(key, 0) + delta
        if newCount == 0:
            hashTable.pop(key, None)
        else:
            hashTable[key] = newCount

    def findSumUtil(self, node, sum_, path, level):
        """Print all downward paths summing to sum_. O(n log n)."""
        if node is None:
            return
        path[level] = node.data
        t = 0
        for i in range(level, -1, -1):
            t += path[i]
            if t == sum_:
                Tree.print_path(path, i, level)
        self.findSumUtil(node.left, sum_, path, level + 1)
        self.findSumUtil(node.right, sum_, path, level + 1)
        path[level] = INT_MIN

    def findSum(self, node, sum_):
        d = self.depth(node)
        path = [0] * d
        self.findSumUtil(node, sum_, path, 0)

    @staticmethod
    def print_path(path, start, end):
        for i in range(start, end + 1):
            print(str(path[i]) + " ", end="")
        print()

    def depth(self, node):
        if node is None:
            return 0
        return 1 + max(self.depth(node.left), self.depth(node.right))

    def maxPathSum(self, root):
        """Binary tree maximum path sum (mutates node values like the original)."""
        if root is None:
            return 0
        maxLeft = self.maxPathSum(root.left)
        maxRight = self.maxPathSum(root.right)
        leftLen = 0
        rightLen = 0
        if root.left is not None:
            leftLen = max(root.left.data, 0)
        if root.right is not None:
            rightLen = max(root.right.data, 0)
        maxLength = root.data
        if leftLen > 0:
            maxLength += leftLen
        if rightLen > 0:
            maxLength += rightLen
        if root.left is not None:
            maxLength = max(maxLeft, maxLength)
        if root.right is not None:
            maxLength = max(maxRight, maxLength)
        root.data = max(leftLen, rightLen) + root.data
        return maxLength

    def maxSumSubtree(self, root):
        """Return the root of the subtree with the largest sum (faithful)."""
        if root is None:
            return None
        maxsum = 0
        res = None
        self.max_sum_helper(root, res, maxsum)
        return res

    def max_sum_helper(self, p, res, maxsum):
        if p is None:
            return 0
        lsum = self.max_sum_helper(p.left, res, maxsum)
        rsum = self.max_sum_helper(p.right, res, maxsum)
        total = lsum + rsum + p.data
        if total > maxsum:
            maxsum = total
            res = p
        return total

    def FindMaxSumSubtree(self, root):
        max_sum = 0
        max_sum = self.MaxSumSubtree(root, max_sum)
        return max_sum

    def MaxSumSubtree(self, root, max_sum):
        lsum = 0
        rsum = 0
        if root is None:
            return 0
        if root.left is not None:
            lsum = self.MaxSumSubtree(root.left, max_sum)
        if root.right is not None:
            rsum = self.MaxSumSubtree(root.right, max_sum)
        sum_ = root.data + lsum + rsum
        if max_sum < sum_:
            max_sum = sum_
        return max_sum

    # ----- views / mirror -------------------------------------------------
    def rightView(self):
        max_level = 0
        self.rightViewUtil(self.root, 1, max_level)

    def rightViewUtil(self, root, level, max_level):
        if root is None:
            return
        if max_level < level:
            print(root.data, end="")
            max_level = level
        self.rightViewUtil(root.right, level + 1, max_level)
        self.rightViewUtil(root.left, level + 1, max_level)

    def mirrorTreeIterative(self, root):
        """Mirror a tree iteratively (faithful; swap is commented out as in Java)."""
        newNode = Node()
        if root is None:
            return None
        _q = deque()
        _q.append(root)
        while _q:
            newNode = _q.popleft()
            # SWAP(newNode.left, newNode.right)
            if newNode.left is not None:
                _q.append(newNode.left)
            if newNode.right is not None:
                _q.append(newNode.right)
        return newNode

    def mirrorTree(self, root):
        """Mirror a tree into a brand new tree."""
        newNode = Node()
        if root is None:
            return None
        newNode.data = root.data
        newNode.left = self.mirrorTree(root.right)
        newNode.right = self.mirrorTree(root.left)
        return newNode

    def isMirror(self, node1, node2):
        if node1 is None and node2 is None:
            return True
        if node1 is not None and node2 is not None and node1.data == node2.data:
            return (self.isMirror(node1.left, node2.right)
                    and self.isMirror(node1.right, node2.left))
        return False

    def trimBST(self, root, minValue, maxValue):
        """Trim a BST so all values stay in [minValue, maxValue]."""
        if root is None:
            return None
        root.left = self.trimBST(root.left, minValue, maxValue)
        root.right = self.trimBST(root.right, minValue, maxValue)
        if minValue <= root.data <= maxValue:
            return root
        if root.data < minValue:
            return root.right
        if root.data > maxValue:
            return root.left
        return None

    # ----- closest value --------------------------------------------------
    def min_diff(self, a, b, key):
        if abs(a - key) <= abs(b - key):
            return a
        return b

    def searchClosest(self, root, key):
        close = INT_MAX
        if root is None:
            return 0
        if key == root.data:
            return key
        close = self.min_diff(close, root.data, key)
        if key > root.data and root.right is not None:
            close = self.min_diff(close, self.searchClosest(root.right, key), key)
        if key < root.data and root.left is not None:
            close = self.min_diff(close, self.searchClosest(root.left, key), key)
        return close

    # ----- vertical sum ---------------------------------------------------
    def verticalSUM(self, root, sum_, hd, min_val, max_val):
        index = hd + self.HD_OFFSET // 2
        if index < min_val:
            min_val = index
        if index > max_val:
            max_val = index
        sum_[index] += root.data
        self.verticalSUM(root.left, sum_, hd - 1, min_val, max_val)
        self.verticalSUM(root.right, sum_, hd + 1, min_val, max_val)

    @staticmethod
    def verticalSumDLL(root):
        """Print vertical sum using a doubly linked list."""
        _dllNode = DLL(0)
        Tree.verticalSumDLLUtil(root, _dllNode)
        while _dllNode.prev is not None:
            _dllNode = _dllNode.prev
        while _dllNode is not None:
            print(str(_dllNode.data) + " ", end="")
            _dllNode = _dllNode.next

    @staticmethod
    def verticalSumDLLUtil(tnode, _dllNode):
        _dllNode.data = _dllNode.data + tnode.data
        if tnode.left is not None:
            if _dllNode.prev is None:
                _dllNode.prev = DLL(0)
                _dllNode.prev.next = _dllNode
            Tree.verticalSumDLLUtil(tnode.left, _dllNode.prev)
        if tnode.right is not None:
            if _dllNode.next is None:
                _dllNode.next = DLL(0)
                _dllNode.next.prev = _dllNode
            Tree.verticalSumDLLUtil(tnode.right, _dllNode.next)

    def FlipTree(self, root):
        """Flip a tree (right nodes are leaves) upside down."""
        if root is None:
            return None
        if root.left is None and root.right is None:
            return root.left
        newRoot = self.FlipTree(root.left)
        root.left.left = root.right
        root.left.right = root
        root.left = None
        root.right = None
        return newRoot

    # ----- heap helpers ---------------------------------------------------
    @staticmethod
    def BuildMaxHeap(arr):
        for i in range(len(arr) - 1, -1, -1):
            Tree.MaxHeapify(arr, i)

    @staticmethod
    def MaxHeapify(arr, i):
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < len(arr) and arr[left] > arr[largest]:
            largest = left
        if right < len(arr) and arr[right] > arr[largest]:
            largest = right
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            Tree.MaxHeapify(arr, largest)

    # ----- balance checks -------------------------------------------------
    @staticmethod
    def isBalanced3(n):
        """O(N) time, O(H) space balance check."""
        return Tree.getHeightBalanced(n) != -1

    @staticmethod
    def getHeightBalanced(n):
        if n is None:
            return 0
        leftHeight = Tree.getHeightBalanced(n.left)
        if leftHeight == -1:
            return -1
        rightHeight = Tree.getHeightBalanced(n.right)
        if rightHeight == -1:
            return -1
        if abs(leftHeight - rightHeight) > 1:
            return -1
        return 1 + max(leftHeight, rightHeight)

    @staticmethod
    def isSuperBalanced(root):
        """A tree is superbalanced if all leaf depths differ by <= 1."""
        if root is None:
            return True
        stack = []
        stack.append((root, 0))
        depths = []
        while stack:
            node, depth = stack.pop()
            if node.left is None and node.right is None:
                if depth not in depths:
                    depths.append(depth)
                if len(depths) > 2 or (len(depths) == 2 and abs(depths[0] - depths[1]) > 1):
                    return False
            else:
                if node.left is not None:
                    stack.append((node.left, depth + 1))
                if node.right is not None:
                    stack.append((node.right, depth + 1))
        return True

    # ----- successors -----------------------------------------------------
    def inorderSuccessor(self, root, p):
        """Inorder successor in a BST (no parent pointers)."""
        if root is None or p is None:
            return None
        successor = None
        while root is not None:
            if p.data < root.data:
                successor = root
                root = root.left
            else:
                root = root.right
        return successor

    @staticmethod
    def inorder_successor_with_parent(n):
        """Inorder successor using parent pointers (Java: inorderSuccessor(Node n))."""
        if n is None:
            return None
        if n.right is not None:
            return Tree.leftmostChild(n.right)
        while n.parent is not None and n.parent.right == n:
            n = n.parent
        return n.parent

    @staticmethod
    def leftmostChild(n):
        if n.left is None:
            return n
        return Tree.leftmostChild(n.left)

    @staticmethod
    def preorderSuccessor(n):
        if n is None:
            return None
        if n.left is not None:
            return n.left
        elif n.right is not None:
            return n.right
        while n.parent is not None and (n.parent.right is None or n.parent.right == n):
            n = n.parent
        if n.parent is None:
            return None
        return n.parent.right

    @staticmethod
    def postorderSuccessor(n):
        if n is None or n.parent is None:
            return None
        if n.parent.right == n or n.parent.right is None:
            return n.parent
        return Tree.leftmostBottomChild(n.parent.right)

    @staticmethod
    def leftmostBottomChild(n):
        if n.left is None and n.right is None:
            return n
        if n.left is not None:
            return Tree.leftmostBottomChild(n.left)
        return Tree.leftmostBottomChild(n.right)

    # ----- levels / relations ---------------------------------------------
    def getLevel(self, node, data, level):
        if node is None:
            return 0
        if node.data == data:
            return level
        downlevel = self.getLevel(node.left, data, level + 1)
        if downlevel != 0:
            return downlevel
        downlevel = self.getLevel(node.right, data, level + 1)
        return downlevel

    def isSibling(self, root, a, b):
        if root is None:
            return False
        return ((root.left == a and root.right == b)
                or (root.left == b and root.right == a)
                or self.isSibling(root.left, a, b)
                or self.isSibling(root.right, a, b))

    def isCousin(self, root, a, b):
        if (self.getLevel(root, a.data, 1) == self.getLevel(root, b.data, 1)
                and not self.isSibling(root, a, b)):
            return True
        return False

    def morrisTraverse(self, root):
        """Morris in-order traversal (prints values)."""
        while root is not None:
            if root.left is None:
                print(root.data)
                root = root.right
            else:
                ptr = root.left
                while ptr.right is not None and ptr.right != root:
                    ptr = ptr.right
                if ptr.right is None:
                    ptr.right = root
                    root = root.left
                else:
                    ptr.right = None
                    print(root.data)
                    root = root.right

    def find_sum(self, search, root):
        """Find two BST nodes that add up to `search`. O(n) time, O(log n) space."""
        s1 = []
        s2 = []
        curr1 = root
        curr2 = root
        done1 = done2 = False
        val1 = 0
        val2 = 0
        result = []
        while True:
            while not done1:
                if curr1 is not None:
                    s1.append(curr1)
                    curr1 = curr1.left
                elif not s1:
                    done1 = True
                else:
                    curr1 = s1.pop()
                    val1 = curr1.data
                    curr1 = curr1.right
                    done1 = True
            while not done2:
                if curr2 is not None:
                    s2.append(curr2)
                    curr2 = curr2.right
                else:
                    if not s2:
                        done2 = True
                    else:
                        curr2 = s2.pop()
                        val2 = curr2.data
                        curr2 = curr2.left
                        done2 = True
            if val1 + val2 == search:
                result.append(val1)
                result.append(val2)
                return result
            elif val1 + val2 > search:
                done2 = False
            else:
                done1 = False

    def printSpecificLevelOrder(self, root):
        """Perfect binary tree specific level order traversal (faithful; null-queue bug)."""
        if root is None:
            return
        print(root.data, end="")
        if root.left is not None:
            print(str(root.left.data) + " " + str(root.right.data), end="")
        if root.left.left is None:
            return
        q = None  # Java: `Queue<Node> q = null;`
        q.append(root.left)
        q.append(root.right)
        while q:
            first = q[0]
            q.popleft()
            second = q[0]
            q.popleft()
            print(str(first.left.data) + " " + str(second.right.data), end="")
            print(str(first.right.data) + " " + str(second.left.data), end="")
            if first.left.left is not None:
                q.append(first.left)
                q.append(second.right)
                q.append(first.right)
                q.append(second.left)

    def leftLeavesSum(self, root):
        """Sum of all left leaves. O(n)."""
        res = 0
        if root is not None:
            if self.isLeaf(root.left):
                res += root.left.data
            else:
                res += self.leftLeavesSum(root.left)
            res += self.leftLeavesSum(root.right)
        return res

    def isLeaf(self, node):
        if node is None:
            return False
        if node.left is None and node.right is None:
            return True
        return False

    # ----- tree to doubly linked list -------------------------------------
    def BTtoDLLmorris(self, root, head, prev):
        """Convert a binary tree to a DLL via Morris traversal."""
        if root is None:
            return
        curr = root
        while curr is not None:
            if curr.left is None:
                if head is None:
                    head = curr
                    prev = curr
                else:
                    prev.right = curr
                    curr.left = prev
                    prev = curr
                curr = curr.right
            else:
                pre = curr.left
                while pre.right is not None and pre.right != curr:
                    pre = pre.right
                if pre.right is None:
                    pre.right = curr
                    curr = curr.left
                else:
                    if head is None:
                        head = curr
                        prev = curr
                    else:
                        prev.right = curr
                        curr.left = prev
                        prev = curr
                    pre.right = None
                    curr = curr.right

    def treeToDoublyList(self, root, prev, head):
        """Convert a binary tree to a circular DLL (faithful port)."""
        if root is None:
            return
        self.treeToDoublyList(root.left, prev, head)
        root.left = prev
        if prev is not None:
            prev.right = root
        else:
            head = root
        right = root.right
        head.left = root
        root.right = head
        prev = root
        self.treeToDoublyList(right, prev, head)

    # ----- serialize / deserialize ----------------------------------------
    @staticmethod
    def Serialize(root):
        """Serialize a binary tree. "'" marks internal, "/" marks NULL."""
        if root is None:
            return ""
        nodeStack = []
        nodeStack.append(root)
        sb = []
        while len(nodeStack) > 0:
            node = nodeStack[-1]
            nodeStack.pop()
            if node is not None:
                if node.left is not None and node.right is not None:
                    sb.append(str(node.data) + "'")
                    nodeStack.append(node.right)
                    nodeStack.append(node.left)
                elif node.left is None and node.right is None:
                    sb.append(str(node.data))
                else:
                    sb.append(str(node.data) + "'")
                    nodeStack.append(node.right)
                    nodeStack.append(node.left)
            else:
                sb.append("/")
        return "".join(sb)

    @staticmethod
    def Deserialize(s):
        root = None
        if Tree.currentIndex > len(s):
            return None
        elif s[Tree.currentIndex] == '/':
            return None
        elif s[Tree.currentIndex + 1] == "'":
            root = Node(s[Tree.currentIndex])
            Tree.currentIndex += 2
            root.left = Tree.Deserialize(s)
            root.right = Tree.Deserialize(s)
        else:
            root = Node(s[Tree.currentIndex])
            root.left = None
            root.right = None
            Tree.currentIndex += 1
            return root
        return root

    def serialize(self, root):
        """Encode a BST to a single comma-separated string (preorder)."""
        sb = []
        self.buildString(root, sb)
        return "".join(sb)

    def buildString(self, root, sb):
        if root is None:
            return
        sb.append(str(root.data) + self.splitter)
        self.buildString(root.left, sb)
        self.buildString(root.right, sb)

    def deserialize(self, data):
        """Decode the string produced by serialize() back into a BST."""
        if len(data) == 0:
            return None
        # Java's String.split drops trailing empty tokens; emulate by filtering.
        nodes = [n for n in data.split(self.splitter) if n != ""]
        pos = [0]
        return self.build_tree_from_nodes(nodes, pos, INT_MIN, INT_MAX)

    def build_tree_from_nodes(self, nodes, pos, min_val, max_val):
        if pos[0] == len(nodes):
            return None
        val = int(nodes[pos[0]])
        if val < min_val or val > max_val:
            return None
        cur = Node(val)
        pos[0] += 1
        cur.left = self.build_tree_from_nodes(nodes, pos, min_val, val)
        cur.right = self.build_tree_from_nodes(nodes, pos, val, max_val)
        return cur

    def createBST(self, a, start, end):
        """Create a minimal-height BST from a sorted, unique array."""
        if start > end:
            return None
        mid = start + (end - start) // 2
        n = Node(a[mid])
        n.left = self.createBST(a, start, mid - 1)
        n.right = self.createBST(a, mid + 1, end)
        return n

    # ----- depth / deepest nodes ------------------------------------------
    def maxDepthIter(self, root):
        """Maximum depth of a binary tree (iterative BFS)."""
        if root is None:
            return 0
        queue = deque()
        queue.append(root)
        count = 0
        while queue:
            size = len(queue)
            while size > 0:
                node = queue.popleft()
                if node.left is not None:
                    queue.append(node.left)
                if node.right is not None:
                    queue.append(node.right)
                size -= 1
            count += 1
        return count

    def deepestLeftLeaf(self, root):
        """Deepest left leaf via BFS traversing right to left."""
        queue = deque()
        queue.append(root)
        while queue:
            root = queue.popleft()
            if root.right is not None:
                queue.append(root.right)
            if root.left is not None:
                queue.append(root.left)
        return root

    def deepestNode(self, root):
        """Deepest node in a binary tree (faithful; null-queue bug)."""
        if root is None:
            return None
        _queue = None  # Java: `Queue<Node> _queue = null;`
        tmp = None
        _queue.append(root)
        while len(_queue) > 0:
            tmp = _queue.popleft()
            if tmp.left is not None:
                _queue.append(tmp.left)
            if tmp.right is not None:
                _queue.append(tmp.right)
        return tmp

    def find(self, root, level):
        """Record the value of the deepest node (uses instance state)."""
        if root is not None:
            self.find(root.left, level + 1)
            if level > self.deepestlevel:
                self.value = root.data
                self.deepestlevel = level
            self.find(root.right, level + 1)

    @staticmethod
    def createLevelLinkedList(root):
        """Create a list of linked lists of nodes at each depth. O(N)."""
        result = []
        current = []
        if root is not None:
            current.append(root)
        while current:
            result.append(current)
            parents = current
            current = []
            for parent in parents:
                if parent.left is not None:
                    current.append(parent.left)
                if parent.right is not None:
                    current.append(parent.right)
        return result

    # ----- subtree containment --------------------------------------------
    def containsTree(self, tl, t2):
        if t2 is None:
            return True
        return self.subTree(tl, t2)

    def subTree(self, rl, r2):
        if rl is None:
            return False
        if rl.data == r2.data:
            if self.matchTree(rl, r2):
                return True
        return self.subTree(rl.left, r2) or self.subTree(rl.right, r2)

    def matchTree(self, rl, r2):
        if r2 is None and rl is None:
            return True
        if rl is None or r2 is None:
            return False
        if rl.data != r2.data:
            return False
        return self.matchTree(rl.left, r2.left) and self.matchTree(rl.right, r2.right)

    # ----- root to leaf paths ---------------------------------------------
    @staticmethod
    def RootToLeafPathPrint(root):
        """Print all root-to-leaf paths, one per line. O(n)."""
        stack = []
        if root is None:
            return
        stack.append(str(root.data) + "")
        stack.append(root)
        while stack:
            temp = stack.pop()
            path = stack.pop()
            if temp.right is not None:
                stack.append(path + str(temp.right.data))
                stack.append(temp.right)
            if temp.left is not None:
                stack.append(path + str(temp.left.data))
                stack.append(temp.left)
            if temp.left is None and temp.right is None:
                print(path)

    def printPaths(self, root):
        if root is None:
            return
        s = []
        s.append(root)
        temp = root.left
        while len(s) != 0:
            while temp is not None:
                s.append(temp)
                temp = temp.left
            top = s[-1]
            if not top.isVisited:
                top.isVisited = True
                temp = top.right
                if temp is None:
                    self.printThePath(s)
                    s.pop()
            else:
                s.pop()

    def printThePath(self, s):
        # get an iterator and print the stack
        pass

    def binaryTreePaths(self, root):
        """Root-to-leaf paths as "a->b->c" strings."""
        res = []
        self.paths_helper(res, root, "")
        return res

    def paths_helper(self, res, root, s):
        if root is None:
            return
        s = s + str(root.data)
        if root.left is None and root.right is None:
            res.append(s)
        else:
            s = s + "->"
            self.paths_helper(res, root.left, s)
            self.paths_helper(res, root.right, s)

    @staticmethod
    def printAllPossiblePath(node, nodelist):
        if node is not None:
            nodelist.append(node)
            if node.left is not None:
                Tree.printAllPossiblePath(node.left, nodelist)
            if node.right is not None:
                Tree.printAllPossiblePath(node.right, nodelist)
            elif node.left is None and node.right is None:
                for i in range(len(nodelist)):
                    print(nodelist[i].data, end="")
                print()
            nodelist.remove(node)

    def printLongestPath(self, root):
        """Longest root-to-leaf path via BFS + parent map (faithful; null-queue bug)."""
        _queue = None  # Java: `Queue<Node> _queue = null;`
        m = {root: None}
        tmp = None
        _queue.append(root)
        while len(_queue) > 0:
            tmp = _queue.popleft()
            if tmp.left is not None:
                m[tmp.left] = tmp
                _queue.append(tmp.left)
            if tmp.right is not None:
                _queue.append(tmp.right)
                m[tmp.right] = tmp
        # printTopToBottomPath(tmp, map)

    # ----- unival trees ---------------------------------------------------
    @staticmethod
    def isTreeUnivalRoot(root):
        if root is None:
            return True
        return Tree.isTreeUnival(root.left, root.data) and Tree.isTreeUnival(root.right, root.data)

    @staticmethod
    def isTreeUnival(n, val):
        if n is None:
            return True
        if n.data != val:
            return False
        return Tree.isTreeUnival(n.left, val) and Tree.isTreeUnival(n.right, val)

    def countSingleRec(self, node):
        """Count unival subtrees (updates self.count)."""
        if node is None:
            return True
        left = self.countSingleRec(node.left)
        right = self.countSingleRec(node.right)
        if left is False or right is False:
            return False
        if node.left is not None and node.data != node.left.data:
            return False
        if node.right is not None and node.data != node.right.data:
            return False
        self.count += 1
        return True

    @staticmethod
    def findNodesCountBelowLevel(root, curr, level):
        """Count nodes beneath a specified level."""
        if root is None:
            return 0
        if curr > level:
            Tree.countN += 1
        Tree.findNodesCountBelowLevel(root.left, curr + 1, level)
        Tree.findNodesCountBelowLevel(root.right, curr + 1, level)
        return Tree.countN

    @staticmethod
    def findLevelWithMaxNodes(root):
        """Level (0-based) of an N-ary tree that has the most nodes."""
        if root is None:
            return 0
        q = deque()
        q.append(root)
        max_Nodes = 1
        level = 0
        max_level = 0
        while True:
            nodeCount = len(q)
            if nodeCount > max_Nodes:
                max_Nodes = nodeCount
                max_level = level
            if nodeCount == 0:
                break
            while nodeCount > 0:
                _node = q.popleft()
                for t in _node.children:
                    q.append(t)
                nodeCount -= 1
            level += 1
        return max_level

    # ----- ternary expression <-> tree ------------------------------------
    @staticmethod
    def convertTtoBT(values):
        """Convert a ternary expression (a?b:c) to a binary tree."""
        n = Node(values[0])
        i = 1
        while i < len(values):
            if values[i] == '?':
                n.left = Node(values[i + 1])
                n.left.parent = n
                n = n.left
            elif values[i] == ':':
                n = n.parent
                while n.right is not None and n.parent is not None:
                    n = n.parent
                n.right = Node(values[i + 1])
                n.right.parent = n
                n = n.right
            i += 2
        return n

    @staticmethod
    def convert(expr):
        """Convert a ternary expression to a binary tree using a stack."""
        if len(expr) == 0:
            return None
        root = Node(expr[0])
        stack = []
        stack.append(root)
        i = 1
        while i < len(expr):
            node = Node(expr[i + 1])
            if expr[i] == '?':
                stack[-1].left = node
            elif expr[i] == ':':
                stack.pop()
                while stack[-1].right is not None:
                    stack.pop()
                stack[-1].right = node
            stack.append(node)
            i += 2
        stack.clear()
        return root

    @staticmethod
    def convertBack(root):
        """Convert a binary tree back to a ternary expression string."""
        stack = []
        sb = []
        stack.append(root)
        while stack:
            node = stack.pop()
            if node.left is not None and node.right is not None:
                stack.append(node.right)
                stack.append(node.left)
                sb.append(str(node.data) + "?")
            elif node.left is None and node.right is None:
                sb.append(str(node.data) + ":")
        result = "".join(sb)
        return result[:-1]

    # ----- has path sum ---------------------------------------------------
    def hasPathSum(self, root, sum_):
        if root is None:
            return False
        if root.data == sum_ and root.left is None and root.right is None:
            return True
        return self.hasPathSum(root.left, sum_ - root.data) or self.hasPathSum(root.right, sum_ - root.data)

    @staticmethod
    def printAllPathSum(root, sum_, path):
        """Print all root-to-leaf-ish paths that add up to sum_."""
        if root is not None:
            if root.data > sum_:
                return
            else:
                path += " " + str(root.data)
                if root.data == sum_ and root.left is None and root.right is None:
                    print(path)
                Tree.printAllPathSum(root.left, sum_ - root.data, path)
                Tree.printAllPathSum(root.right, sum_ - root.data, path)

    # ----- upside down ----------------------------------------------------
    def upsideDownBinaryTree(self, root):
        curr = root
        next_ = None
        temp = None
        prev = None
        while curr is not None:
            next_ = curr.left
            curr.left = temp
            temp = curr.right
            curr.right = prev
            prev = curr
            curr = next_
        return prev

    # ----- perfect subtree size -------------------------------------------
    @staticmethod
    def getLargestSizeOfPerfactTree(root):
        if root.left is None and root.right is None:
            return 1
        if root.left is None or root.right is None:
            return 0
        left = Tree.getLargestSizeOfPerfactTree(root.left)
        right = Tree.getLargestSizeOfPerfactTree(root.right)
        if left < 1 or right < 1:
            return 1
        if left == right:
            Tree.maxSize = left + right + 1
        else:
            Tree.maxSize = max(left, right)
        return Tree.maxSize

    def countSubtrees(self, root):
        """Count subtrees with an odd count of even numbers (updates self.count)."""
        if root is None:
            return 0
        c = self.countSubtrees(root.left)
        c += self.countSubtrees(root.right)
        if root.data % 2 == 0:
            c += 1
        if c % 2 != 0:
            self.count += 1
        return c

    # ----- leaf similar ---------------------------------------------------
    @staticmethod
    def leafSimilar(root1, root2):
        s1 = []
        s2 = []
        s1.append(root1)
        s2.append(root2)
        while s1 and s2:
            if Tree.dfs(s1) != Tree.dfs(s2):
                return False
        return (not s1) and (not s2)

    @staticmethod
    def dfs(s):
        while True:
            node = s.pop()
            if node.right is not None:
                s.append(node.right)
            if node.left is not None:
                s.append(node.left)
            if node.left is None and node.right is None:
                return node.data

    # ----- prune ----------------------------------------------------------
    @staticmethod
    def pruneTree(root):
        """Remove every subtree that does not contain a 1."""
        if root is None:
            return None
        root.left = Tree.pruneTree(root.left)
        root.right = Tree.pruneTree(root.right)
        if root.left is None and root.right is None and root.data == 0:
            return None
        return root

    # ----- build from child->parent relations -----------------------------
    @staticmethod
    def build_tree_from_relations(data):
        """Build a binary tree from a list of Relation(child, parent, isLeft)."""
        m = {}
        root = None
        for r in data:
            child = m.get(r.child)
            if child is None:
                child = Node()
                child.data = r.child
                m[r.child] = child
            if r.parent is None:
                root = child
                continue
            parent = m.get(r.parent)
            if parent is None:
                parent = Node()
                parent.data = r.parent
                m[r.parent] = parent
            if r.isLeft:
                parent.left = child
            else:
                parent.right = child
        return root

    # ----- graph valid tree -----------------------------------------------
    def validTree(self, n, edges):
        """Whether undirected edges form a valid tree (union-find)."""
        nums = [-1] * n
        for i in range(len(edges)):
            x = self.find_uf(nums, edges[i][0])
            y = self.find_uf(nums, edges[i][1])
            if x == y:
                return False
            nums[x] = y
        return len(edges) == n - 1

    def find_uf(self, nums, i):
        if nums[i] == -1:
            return i
        return self.find_uf(nums, nums[i])


if __name__ == "__main__":
    t = Tree()

    # --- Original main: build a small tree and prune zero-only subtrees ---
    tree = Node(1)
    tree.right = Node(0)
    tree.right.left = Node(0)
    tree.right.right = Node(1)
    pruned = Tree.pruneTree(tree)
    print("Pruned root data:", pruned.data if pruned else None)

    # --- Build a minimal-height BST from a sorted array and traverse ------
    bst = t.createBST([1, 2, 3, 4, 5, 6, 7], 0, 6)
    print("Inorder:", end=" ")
    t.inOrder(bst)
    print()
    print("Preorder:", end=" ")
    t.preOrder(bst)
    print()

    # --- Diameter (reset the static accumulator first) --------------------
    Tree.diameter = 0
    print("Diameter:", Tree.diameterOfBinaryTree(bst))

    # --- Validate BST -----------------------------------------------------
    print("isValidBST:", Tree.isValidBST(bst))
    print("validateBST:", Tree.validateBST(bst, INT_MIN, INT_MAX))

    # --- Serialize / deserialize round-trip -------------------------------
    s = t.serialize(bst)
    print("Serialized:", s)
    print("Round-trip inorder:", end=" ")
    t.inOrder(t.deserialize(s))
    print()

    # --- A few more read-only queries -------------------------------------
    print("maxDepthIter:", t.maxDepthIter(bst))
    print("isBalanced3:", Tree.isBalanced3(bst))
    print("binaryTreePaths:", t.binaryTreePaths(bst))
    print("findSecondLargestValueInBST:", Tree.findSecondLargestValueInBST(bst))
    print("hasPathSum(1->2->4 == 7):", t.hasPathSum(bst, 7))
