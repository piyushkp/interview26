"""An in-memory key-value store (string keys and values) that saves and loads
itself as JSON.

KVStore supports get/set/delete, plus serialize() to a JSON string and
deserialize() to replace the contents from a JSON string, and keys() which
returns every key in sorted order. get() returns None for a missing key, and
delete() reports whether the key was actually there.
"""

import json


# Approach (in plain terms):
#   A key-value store is exactly what a Python dict is for, so the whole store
#   is just one dict. get/set/delete are direct dict operations; delete also
#   reports whether the key was actually present. Saving and loading reuse the
#   json module: serialize turns the dict into a JSON string, and deserialize
#   parses a JSON string back into a fresh dict, replacing what we had. keys()
#   hands back the dict's keys run through sorted() so they come out in order.
#   Data structures used:
#     - dict - the store itself; O(1) average get/set/delete by key.
#     - sorted list (built on demand) - keys() returns keys in order.
class KVStore:

    def __init__(self):
        """Start with an empty store."""
        # Time: O(1), Space: O(1) - one empty dict.
        self._store = {}

    def get(self, key):
        """Value for key, or None if the key is absent."""
        # Time: O(1) average - one dict lookup. Space: O(1).
        return self._store.get(key)

    def set(self, key, value):
        """Insert or overwrite the value for key."""
        # Time: O(1) average - one dict insert. Space: O(1).
        self._store[key] = value

    def delete(self, key):
        """Remove key; return True if it existed, False if it was missing."""
        # Time: O(1) average. Space: O(1).
        if key in self._store:
            del self._store[key]
            return True
        return False

    def keys(self):
        """All keys in ascending sorted order."""
        # n = number of keys. Time: O(n log n) - sorts the keys.
        # Space: O(n) - the returned list.
        return sorted(self._store.keys())

    def serialize(self):
        """The whole store as a JSON string (keys sorted, stable form)."""
        # n = number of pairs, m = total characters.
        # Time: O(n log n + m). Space: O(m) - the JSON string.
        return json.dumps(self._store, sort_keys=True)

    def deserialize(self, data):
        """Replace the store's contents with the pairs from a JSON string."""
        # m = length of data. Time: O(m) - parse the JSON. Space: O(m).
        self._store = json.loads(data)


if __name__ == "__main__":
    store = KVStore()
    store.set("theme", "dark")
    store.set("region", "eu")
    print(store.get("theme"))        # dark
    print(store.get("missing"))      # None
    print(store.keys())              # ['region', 'theme']

    snapshot = store.serialize()
    print(snapshot)                  # {"region": "eu", "theme": "dark"}

    print(store.delete("theme"))     # True   (was present)
    print(store.delete("theme"))     # False  (already gone)
    print(store.keys())              # ['region']

    # Restore from the earlier snapshot -> both pairs come back.
    store.deserialize(snapshot)
    print(store.keys())              # ['region', 'theme']
    print(store.get("theme"))        # dark
