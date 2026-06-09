"""Idiomatic Python 3 port of java/Hasher.java (original package code.ds).

Three data structures:
  * Hasher        - generic hash table with separate chaining (doubly-linked
                    nodes per bucket)
  * MiniCassandra - two-level key/value store with ordered column ranges
  * ConsistentHash - consistent-hashing ring (with the source's stub hash that
                     always returns 0)

Java generics ``<K, V>`` become plain Python. ``TreeMap`` (a sorted map) is
emulated with a regular ``dict`` whose keys are sorted on demand. The
``HashFunction.hash`` method in the source always returns 0; that behaviour is
preserved, so every node maps to the same ring slot.
"""


# ---------------------------------------------------------------------------
# Hasher: separate-chaining hash table
# ---------------------------------------------------------------------------
class LinkedListNode:
    def __init__(self, k, v):
        self.next = None
        self.prev = None
        self.key = k
        self.value = v

    def print_forward(self):
        data = "({},{})".format(self.key, self.value)
        if self.next is not None:
            return data + "->" + self.next.print_forward()
        return data


class Hasher:
    def __init__(self, capacity):
        # List of bucket heads (each a linked list), all initially empty.
        self.arr = [None] * capacity

    def put(self, key, value):
        node = self._get_node_for_key(key)
        if node is not None:
            old_value = node.value
            node.value = value  # just update the value
            return old_value

        node = LinkedListNode(key, value)
        index = self.get_index_for_key(key)
        if self.arr[index] is not None:
            node.next = self.arr[index]
            node.next.prev = node
        self.arr[index] = node
        return None

    def remove(self, key):
        node = self._get_node_for_key(key)
        if node is None:
            return None

        if node.prev is not None:
            node.prev.next = node.next
        else:
            # Removing head - update bucket.
            hash_key = self.get_index_for_key(key)
            self.arr[hash_key] = node.next

        if node.next is not None:
            node.next.prev = node.prev
        return node.value

    def get(self, key):
        if key is None:
            return None
        node = self._get_node_for_key(key)
        return None if node is None else node.value

    def _get_node_for_key(self, key):
        index = self.get_index_for_key(key)
        current = self.arr[index]
        while current is not None:
            if current.key == key:
                return current
            current = current.next
        return None

    def get_index_for_key(self, key):
        # "Really stupid function to map a key to an index."
        return abs(hash(key) % len(self.arr))

    def print_table(self):
        for i in range(len(self.arr)):
            s = "" if self.arr[i] is None else self.arr[i].print_forward()
            print("{}: {}".format(i, s))


# ---------------------------------------------------------------------------
# MiniCassandra: two-level keyed store (raw_key -> column_key -> value)
# ---------------------------------------------------------------------------
class Column:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return "Column({},{})".format(self.key, self.value)


class MiniCassandra:
    def __init__(self):
        self.map = {}

    def insert(self, raw_key, column_key, column_value):
        tm = self.map.get(raw_key)
        if tm is None:
            tm = {}
            self.map[raw_key] = tm
        tm[column_key] = column_value

    def query(self, raw_key, column_start, column_end):
        results = []
        tm = self.map.get(raw_key)
        if tm is None:
            return results
        # TreeMap.subMap(start, true, end, true): inclusive on both ends,
        # returned in ascending key order.
        for key in sorted(tm.keys()):
            if column_start <= key <= column_end:
                results.append(Column(key, tm[key]))
        return results


# ---------------------------------------------------------------------------
# ConsistentHash: hashing ring
# ---------------------------------------------------------------------------
class HashFunction:
    def hash(self, key):
        return 0  # faithful stub from the source


class ConsistentHash:
    def __init__(self, hash_function, number_of_replicas, nodes):
        self.hash_function = hash_function
        self.number_of_replicas = number_of_replicas
        self.circle = {}  # emulated SortedMap<Integer, T>
        for node in nodes:
            self.add(node)

    def add(self, node):
        for i in range(self.number_of_replicas):
            self.circle[self.hash_function.hash(str(node) + str(i))] = node

    def remove(self, node):
        for i in range(self.number_of_replicas):
            self.circle.pop(self.hash_function.hash(str(node) + str(i)), None)

    def get(self, key):
        if not self.circle:
            return None
        h = self.hash_function.hash(key)
        if h not in self.circle:
            keys = sorted(self.circle.keys())
            tail = [k for k in keys if k >= h]  # circle.tailMap(hash)
            h = tail[0] if tail else keys[0]
        return self.circle[h]


if __name__ == "__main__":
    print("Hasher")
    print()

    h = Hasher(10)
    h.put(1, "one")
    h.put(11, "eleven")  # collides with key 1 (both index 1) -> chained
    h.put(2, "two")
    print("get(1):", h.get(1), " get(11):", h.get(11), " get(2):", h.get(2))
    print("remove(1):", h.remove(1), " get(1) after remove:", h.get(1))

    mc = MiniCassandra()
    mc.insert("user1", 3, "c")
    mc.insert("user1", 1, "a")
    mc.insert("user1", 2, "b")
    print("MiniCassandra query user1 [1,2]:", mc.query("user1", 1, 2))

    ch = ConsistentHash(HashFunction(), 3, ["nodeA", "nodeB"])
    print("ConsistentHash get('x'):", ch.get("x"))
