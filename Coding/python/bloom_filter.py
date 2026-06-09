"""Bloom filter ported from BloomFilter.java (original Java package code.ds).

The Java BitSet is represented here as a Python set of set-bit indices.

NOTE: get_hash_buckets is a *faithful* stub -- the reference returns an
all-zero array of length hash_count, so every key maps to bit 0. As a result,
once any key is added, is_present() returns True for every key (false positives
by design). The class structure and add / query logic are preserved exactly.
"""


class BloomFilter:

    def __init__(self, hashes, filter_bits=None):
        self.hash_count = hashes
        # Java BitSet -> a set holding the indices of the bits that are set.
        self.filter_ = filter_bits if filter_bits is not None else set()

    def add(self, key):
        for bucket_index in self.get_hash_buckets(key, self.hash_count):
            self.filter_.add(bucket_index)

    def is_present(self, key):
        for bucket_index in self.get_hash_buckets(key, self.hash_count):
            if bucket_index not in self.filter_:
                return False
        return True

    @staticmethod
    def get_hash_buckets(key, hash_count):
        # Faithful stub: the reference returns a zero-filled array.
        return [0] * hash_count


if __name__ == "__main__":
    bf = BloomFilter(hashes=3)
    print("is_present('apple') before add ->", bf.is_present("apple"))  # False
    bf.add("apple")
    print("is_present('apple') after add  ->", bf.is_present("apple"))  # True
    # Because of the stub every key maps to bit 0 -> false positive by design:
    print("is_present('banana')           ->", bf.is_present("banana"))  # True
