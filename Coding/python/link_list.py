"""
link_list.py

Idiomatic Python 3 port of java/LinkList.java (original package code.ds).
A collection of singly / doubly / circular / multi-level linked-list
interview problems.

Notes
-----
* The Java ``LinkList`` class becomes the Python ``LinkList`` class. Instance
  methods keep ``self`` and use ``self.head``; ``static`` methods become
  ``@staticmethod`` (they call one another via ``LinkList.<name>``).
* Java method overloads / name clashes were renamed:
    - ``merge(Node, Node)``      -> ``merge``            (static)
    - ``merge(LinkList)``        -> ``merge_alternate``  (instance)
    - ``remove_duplicates()``    -> ``remove_duplicates_unsorted``
    - ``removeDuplicates()``     -> ``remove_duplicates_sorted``
    - ``remove(Node, int)``      -> ``remove_dll``
    - ``Reverse``/``reverse``/``reverselist``/``reverseUtil``/``reverseKGroup``
      -> ``reverse`` / ``reverse_between`` / ``reverse_list`` /
         ``reverse_util`` / ``reverse_k_group``
* Several reference implementations in the original are intentionally buggy
  (e.g. ``find_middle`` on odd-length lists, ``copy_list``) or are never called
  from ``main``.  They are ported faithfully and flagged with comments.
"""

import math
import random


class Node:
    """Linked-list node with next, random and prev pointers."""

    def __init__(self, data=0):
        self.data = data
        self.next = None
        self.random = None
        self.prev = None


class FlatList:
    """Node for a multi-level (flatten) linked list: next + down pointers."""

    def __init__(self, data=0):
        self.data = data
        self.next = None
        self.down = None


class LinkList:

    def __init__(self):
        self.head = None

    # Traverse Linked List
    def print_linked_list(self, start):
        print("\nHEAD .", end="")
        while start is not None:
            print(start.data, end="")
            start = start.next
        print("null\n")

    # insert a node at the beginning of the list
    def insert_node_in_linked_list_at_front(self, data):
        temp = Node(data)
        temp.data = data
        temp.next = self.head
        self.head = temp

    # insert a node at the end of the list
    def insert_node_in_linked_list_at_end(self, data):
        temp = Node(data)
        temp.data = data
        temp.next = None
        if self.head is None:
            self.head = temp
            return
        else:
            traveller = self.head
            while traveller.next is not None:
                traveller = traveller.next
            traveller.next = temp

    # insert a node in a given location in a list
    def insert_node_in_linked_list(self, data, position):
        temp = Node(data)
        temp.data = data
        temp.next = None
        if position == 1 or self.head is None:
            temp.next = self.head
            self.head = temp
            return
        else:
            t = self.head
            curr_pos = 2
            while curr_pos < position and t.next is not None:
                t = t.next
                curr_pos += 1
            temp.next = t.next
            t.next = temp

    # delete a node at a specific location
    def delete_node_from_linked_list(self, position):
        if self.head is None:
            return 0
        if position == 1:
            self.head = self.head.next
        else:
            t = self.head
            curr_pos = 2
            while curr_pos < position and t.next is not None:
                t = t.next
                curr_pos += 1
            if t.next is not None:
                t.next = t.next.next  # NOTE THIS
            else:
                return 0  # could not find the correct node
        return 1

    # Delete a node in the middle given only access to that node.
    # Copy the data from the next node into this node and delete the next node.
    @staticmethod
    def delete_node(n):
        if n is None or n.next is None:
            return False  # Failure
        nxt = n.next
        n.data = nxt.data
        n.next = nxt.next
        return True

    # Sort Link List (selection-style swap of data)
    def sort(self):
        lst = self.head
        while lst.next is not None:
            pass_node = lst.next
            while pass_node is not None:
                if lst.data > pass_node.data:
                    lst.data, pass_node.data = pass_node.data, lst.data
                pass_node = pass_node.next
            lst = lst.next

    # Merge Sort LinkList -- Time Complexity O(n log n)
    @staticmethod
    def merge_sort(head):
        if head is None or head.next is None:
            return head
        first = head
        middle = LinkList.find_middle(head)
        second = middle.next
        middle.next = None
        return LinkList.merge(LinkList.merge_sort(first), LinkList.merge_sort(second))

    @staticmethod
    def merge(first, second):
        result = None
        # Base cases
        if first is None:
            return second
        elif second is None:
            return first
        # Pick either a or b, and recur
        if first.data <= second.data:
            result = first
            result.next = LinkList.merge(first.next, second)
        else:
            result = second
            result.next = LinkList.merge(first, second.next)
        return result

    @staticmethod
    def find_middle(head):
        # NOTE: faithful port -- this raises on odd-length lists (mirrors the
        # Java NullPointerException bug); only safe for even-length lists.
        slow = head
        fast = head
        while slow.next is not None and fast.next.next is not None:
            slow = slow.next
            fast = fast.next.next
        return slow

    # Search an element in linked list
    def find(self, value):
        current_node = self.head
        while current_node is not None:
            if current_node.data == value:
                return current_node
            else:
                current_node = current_node.next
        return None

    # Find maximum and minimum in a linked list
    def max_min_in_list(self, max_val, min_val):
        current_node = self.head
        if current_node is None:
            return 0  # list is empty
        max_val = min_val = current_node.data
        while current_node.next is not None:
            current_node = current_node.next
            if current_node.data > max_val:
                max_val = current_node.data
            elif current_node.data < min_val:
                min_val = current_node.data
        return 1

    # Print reverse in O(N) time and O(sqrt(N)) space. Do not manipulate list.
    @staticmethod
    def print_reverse1(head):
        node = head
        n = 0
        while node is not None:
            node = node.next
            n += 1
        node = head
        k = int(math.sqrt(n))
        stack = []
        stack.append(node)
        temp = 0
        for _i in range(n):
            if temp == k:
                stack.append(node)
                temp = 0
            node = node.next
            temp += 1
        stack2 = []
        while len(stack) > 0:
            t = stack.pop()
            stack2.append(t)
            for _i in range(1, k):
                stack2.append(t.next)
                t = t.next
            while stack2:
                print(stack2.pop().data, end="")

    # Print reverse of linked list. Time = O(N) space = O(N)
    @staticmethod
    def print_reverse(head):
        if head is None:
            return
        LinkList.print_reverse(head.next)
        print(str(head.data) + " ", end="")

    # Reverse Linked List. Time = O(N) space = O(1)
    @staticmethod
    def reverse(head):
        current_node = head
        prev_node = None
        next_node = None
        while current_node is not None:
            next_node = current_node.next
            current_node.next = prev_node
            prev_node = current_node
            current_node = next_node
        head = prev_node  # local rebinding only (mirrors Java semantics)

    # reverse single linklist recursively
    def reverse_util(self, curr, prev):
        # If last node, mark it head
        if curr.next is None:
            self.head = curr
            curr.next = prev
            return None
        next1 = curr.next
        curr.next = prev
        self.reverse_util(next1, curr)
        return self.head

    # Reverse a Linked List in groups of given size.
    # 1->2->3->4->5->6->7->8 and k=3  =>  3->2->1->6->5->4->8->7
    @staticmethod
    def reverse_k_group(head, k):
        if head is None or head.next is None or k == 1:
            return head
        dummyhead = Node(-1)
        dummyhead.next = head
        begin = dummyhead
        i = 0
        while head is not None:
            i += 1
            if i % k == 0:
                begin = LinkList.reverse_between(begin, head.next)
                head = begin.next
            else:
                head = head.next
        return dummyhead.next

    # reverse(begin, end) helper used by reverse_k_group
    @staticmethod
    def reverse_between(begin, end):
        curr = begin.next
        prev = begin
        first = curr
        while curr is not end:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        begin.next = prev
        first.next = curr
        return first

    # Detect cycle. Time O(n) space O(1)
    def find_circular(self, head):
        slower = head
        faster = head
        while slower is not None and faster is not None and faster.next is not None:
            slower = slower.next
            faster = faster.next.next
            if faster is slower:
                return True
        return False

    # Detect loop and remove it from linkList
    def detect_and_remove_loop(self, node):
        slow = self.head
        fast = self.head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                slow = self.head
                while slow is not fast.next:
                    slow = slow.next
                    fast = fast.next
                fast.next = None

    # Return the kth element from the tail of a singly linked list
    def print_nth_from_last(self, head, k):
        main_ptr = head
        ref_ptr = head
        count = 0
        if head is not None:
            while count < k:
                if ref_ptr is None:
                    print("n is greater than the no. of nodes in list", end="")
                    return
                ref_ptr = ref_ptr.next
                count += 1
            while ref_ptr is not None:
                main_ptr = main_ptr.next
                ref_ptr = ref_ptr.next
            print("Node no. n from last is " + str(main_ptr.data), end="")

    # Copy a linked list with next and random pointer.
    # NOTE: faithful port of a buggy reference (self-referential next); would
    # loop forever if invoked. Not used by the demo.
    def copy_list(self, head):
        copy = None
        temp = None
        ptr = head
        while ptr is not None:
            temp = ptr
            ptr.next = temp
            ptr = ptr.next.next
        ptr = head
        while ptr is not None and ptr.next is not None:
            ptr.next.random = ptr.random.next
            ptr = ptr.next.next
        ptr = head
        prev = None
        while ptr is not None:
            if copy is None:
                copy = ptr.next
            else:
                prev.next = ptr.next
            prev = ptr.next
            ptr = ptr.next.next
        return copy

    # Check if a linked list is a palindrome (like 0->1->2->1->0)
    def is_palindrome(self, head):
        if head is None:
            return False
        p1 = head
        p2 = head
        s = []  # stack of ints
        while p2 is not None and p2.next is not None:
            s.append(p1.data)
            p1 = p1.next
            p2 = p2.next.next
        # handle odd nodes
        if p2 is not None:
            p1 = p1.next
        while p1 is not None:
            if p1.data != s.pop():
                return False
            p1 = p1.next
        return True

    # Group all odd nodes together followed by even nodes.
    # 1->2->3->4->5 => 1->3->5->2->4
    @staticmethod
    def odd_even_list(head):
        if head is None or head.next is None:
            return head
        odd = head
        even = head.next
        even_head = even
        while even is not None and even.next is not None:
            odd.next = even.next
            odd = odd.next
            even.next = odd.next
            even = even.next
        odd.next = even_head
        return head

    # Reverse alternate nodes and append them to end of list. O(1) extra space.
    # 1->2->3->4->5->6 => 1->3->5->6->4->2
    def rearrange(self, odd):
        if odd is None or odd.next is None or odd.next.next is None:
            return
        even = odd.next
        odd.next = odd.next.next
        odd = odd.next
        even.next = None
        while odd is not None and odd.next is not None:
            temp = odd.next.next
            odd.next.next = even
            even = odd.next
            odd.next = temp
            if temp is not None:
                odd = temp
        odd.next = even

    # Rearrange L0->L1->...->Ln into L0->Ln->L1->Ln-1->...
    # 1->2->3->4 => 1->4->2->3
    def rearrange1(self, node):
        # 1) Find the middle point using tortoise and hare
        slow = node
        fast = slow.next
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
        # 2) Split the list into two halves
        node1 = node
        node2 = slow.next
        slow.next = None
        # 3) Reverse the second half
        node2 = LinkList.reverse_list(node2)
        # 4) Merge alternate nodes
        node = Node(0)  # dummy
        curr = node
        while node1 is not None or node2 is not None:
            if node1 is not None:
                curr.next = node1
                curr = curr.next
                node1 = node1.next
            if node2 is not None:
                curr.next = node2
                curr = curr.next
                node2 = node2.next
        node = node.next  # local rebinding only (mirrors Java semantics)

    @staticmethod
    def reverse_list(node):
        prev = None
        curr = node
        while curr is not None:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        node = prev
        return node

    # Retain M nodes then delete next N nodes, repeat till end.
    # M=2, N=2  1->2->3->4->5->6->7->8 => 1->2->5->6
    def skip_m_delete_n(self, head, m, n):
        curr = head
        while curr is not None:
            # Skip M nodes
            count = 1
            while count < m and curr is not None:
                curr = curr.next
                count += 1
            if curr is None:
                return
            # Start from next node and delete N nodes
            t = curr.next
            count = 1
            while count <= n and t is not None:
                t = t.next
                count += 1
            curr.next = t
            curr = t

    # Swap nodes in a linked list without swapping data
    # 10->15->12->13->20->14, x=12, y=20 => 10->15->20->13->12->14
    def swap_node(self, head, x, y):
        if x == y:
            return
        prev_x = None
        curr_x = head
        while curr_x is not None and curr_x.data != x:
            prev_x = curr_x
            curr_x = curr_x.next
        prev_y = None
        curr_y = head
        while curr_y is not None and curr_y.data != y:
            prev_y = curr_y
            curr_y = curr_y.next
        if prev_x is not None:
            prev_x.next = curr_y
        else:
            head = curr_y
        if prev_y is not None:
            prev_y.next = curr_x
        else:
            head = curr_x
        temp = curr_y.next
        curr_y.next = curr_x.next
        curr_x.next = temp

    # Compare two strings represented as linked lists
    def compare(self, node1, node2):
        if node1 is None and node2 is None:
            return 1
        while node1 is not None and node2 is not None and node1.data == node2.data:
            node1 = node1.next
            node2 = node2.next
        # if the lists differ in value
        if node1 is not None and node2 is not None:
            return 1 if node1.data > node2.data else -1
        # if either of the lists has reached its end
        if node1 is not None and node2 is None:
            return -1
        if node1 is None and node2 is not None:
            return -1
        return 0

    # Merge a linked list q into self at alternate positions. (was merge(LinkList))
    def merge_alternate(self, q):
        p_curr = self.head
        q_curr = q.head
        while p_curr is not None and q_curr is not None:
            p_next = p_curr.next
            q_next = q_curr.next
            q_curr.next = p_next
            p_curr.next = q_curr
            p_curr = p_next
            q_curr = q_next
        q.head = q_curr

    # Reservoir-sampling based pick of a random node.
    def printrandom(self, node):
        if node is None:
            return
        # (Java seeded its RNG via UUID here; the result was discarded.)
        result = node.data
        current = node
        n = 2
        while current is not None:
            # faithful port: with floats in [0,1) this is almost never true.
            if random.random() % n == 0:
                result = current.data
            current = current.next
            n += 1
        print("Randomly selected key is " + str(result))

    # Remove duplicates from an UNSORTED list. Time O(n^2) space O(1).
    def remove_duplicates_unsorted(self):
        ptr1 = self.head
        while ptr1 is not None and ptr1.next is not None:
            ptr2 = ptr1
            while ptr2.next is not None:
                if ptr1.data == ptr2.next.data:
                    ptr2.next = ptr2.next.next
                else:
                    ptr2 = ptr2.next
            ptr1 = ptr1.next

    # Remove duplicates from a SORTED list.
    def remove_duplicates_sorted(self):
        current = self.head
        if self.head is None:
            return
        while current.next is not None:
            if current.data == current.next.data:
                next_next = current.next.next
                current.next = None
                current.next = next_next
            else:
                current = current.next

    # Add two numbers represented by linked lists (digits in reverse order).
    # (3-1-5),(5-9-2) => 9-0-7
    # NOTE: Java used pass-by-reference for ``result``; faithful port keeps the
    # same (ineffective) reassignments. Not used by the demo.
    def add_list(self, head1, head2, result):
        if head1 is None:
            result = head2
            return
        elif head2 is None:
            result = head1
            return
        size1 = self.get_size(head1)
        size2 = self.get_size(head2)
        carry = 0
        if size1 == size2:
            result = self.add_same_size(head1, head2, carry)
        else:
            diff = abs(size1 - size2)
            if size1 < size2:
                self.swap_pointer(head1, head2)
            cur = head1
            while diff > 0:
                cur = cur.next
                diff -= 1
            result = self.add_same_size(cur, head2, carry)
            self.add_carry_to_remaining(head1, cur, carry, result)

    # A utility function to swap two pointers (no-op: swaps locals only)
    def swap_pointer(self, a, b):
        t = a
        a = b
        b = t

    # Get size of linked list
    def get_size(self, node):
        size = 0
        while node is not None:
            node = node.next
            size += 1
        return size

    # Add two same-size lists; carry propagated while returning from recursion.
    def add_same_size(self, head1, head2, carry):
        if head1 is None:
            return None
        result = Node()
        result.next = self.add_same_size(head1.next, head2.next, carry)
        s = head1.data + head2.data + carry
        carry = s // 10
        s = s % 10
        result.data = s
        return result

    # Add carry to the left portion of the larger list.
    def add_carry_to_remaining(self, head1, cur, carry, result):
        if head1 is not cur:
            self.add_carry_to_remaining(head1.next, cur, carry, result)
            s = head1.data + carry
            carry = s // 10
            s %= 10
            # result.addAtFront(s)  # (left as in original)

    # Insert into a sorted circular linked list.
    def sorted_insert(self, new_node):
        current = self.head
        # Case 1: empty list
        if current is None:
            new_node.next = new_node
            self.head = new_node
        # Case 2: insert just before the head
        elif current.data >= new_node.data:
            while current.next is not self.head:
                current = current.next
            current.next = new_node
            new_node.next = self.head
            self.head = new_node
        # Case 3: insert somewhere after the head
        else:
            while current.next is not self.head and current.next.data < new_node.data:
                current = current.next
            new_node.next = current.next
            current.next = new_node

    # Insert a value into a sorted cyclic list given any node in the list.
    def insert(self, node, x):
        if node is None:
            node = Node(x)
            node.next = node
            return
        curr = node
        prev = None
        while True:
            prev = curr
            curr = curr.next
            if x <= curr.data and x >= prev.data:
                break  # case 1
            if prev.data > curr.data and (x < curr.data or x > prev.data):
                break  # case 2
            if curr is node:
                break  # case 3: back to start
        new_node = Node(x)
        new_node.next = curr
        prev.next = new_node

    # Remove a single occurrence of a value from a doubly linked list.
    # (was remove(Node, int))
    def remove_dll(self, head, value):
        cur = head
        if head is None:
            return
        if head.data == value:
            head = cur.next
        while cur is not None:
            if cur.data == value:
                if cur.prev is not None:
                    cur.prev.next = cur.next
                if cur.next is not None:
                    cur.next.prev = cur.prev
                break
            cur = cur.next

    # Intersection point (by value) of two linked lists.
    def get_inter_section_node(self, head1, head2):
        c1 = self.get_count(head1)
        c2 = self.get_count(head2)
        if c1 > c2:
            d = c1 - c2
            return self._get_intersection_node(d, head1, head2)
        else:
            d = c2 - c1
            return self._get_intersection_node(d, head2, head1)

    def _get_intersection_node(self, d, node1, node2):
        current1 = node1
        current2 = node2
        for _i in range(d):
            current1 = current1.next
        while current1 is not None and current2 is not None:
            if current1.data == current2.data:
                return current1.data
            current1 = current1.next
            current2 = current2.next
        return -1

    # Count of nodes in the list
    def get_count(self, node):
        current = node
        count = 0
        while current is not None:
            current = current.next
            count += 1
        return count

    # Add '1' to a number represented as a linked list. O(n), no extra space.
    def add_one(self, head):
        head = LinkList.reverse_list(head)
        head = self.add_one_to_list(head)
        return LinkList.reverse_list(head)

    def add_one_to_list(self, head):
        res = head
        temp = None
        carry = 1
        while head is not None:
            s = carry + head.data
            carry = 1 if s >= 10 else 0
            s = s % 10
            head.data = s
            temp = head
            head = head.next
        if carry > 0:
            node = Node()
            node.data = carry
            temp.next = node
        return res

    def add_one_to_list1(self, head):
        carry = LinkList.add_with_carry(head)
        if carry > 0:
            new_node = Node()
            new_node.data = carry
            new_node.next = head
            return new_node  # New node becomes head now
        return head

    @staticmethod
    def add_with_carry(head):
        if head is None:
            return 1
        s = head.data + LinkList.add_with_carry(head.next)
        head.data = s % 10
        return s // 10

    # Find an entry in less than n probes (skip-by-2 search).
    @staticmethod
    def search_list_fast(head, target):
        prev = None
        ptr = head
        if head is None:
            return False
        while ptr is not None:
            if ptr.data == target:
                return True
            elif ptr.data > target:
                return LinkList.search(prev, ptr, target)
            prev = ptr
            if ptr.next is not None and ptr.next.next is not None:
                ptr = ptr.next.next
            elif ptr.next is not None and ptr.next.data == target:
                return True
            else:
                return False
        return False

    @staticmethod
    def search(start, end, target):
        if start is None:
            return False
        while start is not end:
            if start.data == target:
                return True
            start = start.next
        return False

    # Remove odd numbers from the linked list.
    @staticmethod
    def remove_odd(head):
        if head is None:
            return None
        curr = head
        while curr.data % 2 != 0:
            head = curr.next
            curr = curr.next
        curr = curr.next
        prev = head
        while curr is not None:
            if curr.data % 2 != 0:
                prev.next = curr.next
            else:
                prev = curr
            curr = curr.next
        return head

    # Deck-of-cards style interleave shuffle.
    @staticmethod
    def interleave(first, second):
        tail = None
        while second is not None:
            if tail is None:
                tail = second
            else:
                tail.next = second
                tail = second
            nxt = second.next
            second.next = None
            second = nxt
            # swap the two lists
            temp = first
            first = second
            second = temp

    # Merge two sorted linked lists.
    def merge_lists(self, list1, list2):
        if list1 is None:
            return list2
        if list2 is None:
            return list1
        if list1.data < list2.data:
            head = list1
        else:
            head = list2
            list2 = list1
            list1 = head
        while list1.next is not None and list2 is not None:
            if list1.next.data <= list2.data:
                list1 = list1.next
            else:
                tmp = list1.next
                list1.next = list2
                list2 = tmp
        if list1.next is None:
            list1.next = list2
        return head

    # Sorted linked list to BST (uses self.head as the running cursor).
    def sorted_list_to_bst_recur(self, n):
        if n <= 0:
            return None
        left = self.sorted_list_to_bst_recur(n // 2)
        root = self.head
        root.prev = left
        self.head = self.head.next
        root.next = self.sorted_list_to_bst_recur(n - n // 2 - 1)
        return root

    # Flatten a multi-level linked list (next + down pointers).
    # NOTE: the final ``else`` peeks an empty stack in the original; faithful
    # port may raise IndexError if invoked. Not used by the demo.
    def flatten_linked_list(self, head):
        stack = []
        stack.append(head)
        while stack:
            node = stack.pop()
            if node.down is not None and node.next is not None:
                stack.append(node.next)
                stack.append(node.down)
                node.next = node.down
                node.down = None
            elif node.next is not None:
                stack.append(node.next)
            elif node.down is not None:
                stack.append(node.down)
                node.next = node.down
                node.down = None
            else:
                node.next = stack[-1]
        return head


if __name__ == "__main__":
    head = Node(1)
    head.next = Node(2)
    head.next.next = Node(3)
    head.next.next.next = Node(4)
    LinkList.print_reverse1(head)  # prints 4321 (reverse of 1 2 3 4)
    print()
