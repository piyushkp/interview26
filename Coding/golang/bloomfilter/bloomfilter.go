package main

import "fmt"

// bitSet is a minimal, growable bit set used as the filter backing store
// (a port of java.util.BitSet, which also grows on demand).
type bitSet struct {
	words []uint64
}

// set turns on bit i, growing the backing store as needed.
func (b *bitSet) set(i int) {
	w := i >> 6
	for w >= len(b.words) {
		b.words = append(b.words, 0)
	}
	b.words[w] |= 1 << uint(i&63)
}

// get reports whether bit i is set.
func (b *bitSet) get(i int) bool {
	w := i >> 6
	if w >= len(b.words) {
		return false
	}
	return b.words[w]&(1<<uint(i&63)) != 0
}

// BloomFilter is a probabilistic set-membership structure with no false
// negatives (but possible false positives).
type BloomFilter struct {
	filter    *bitSet
	hashCount int
}

// newBloomFilter builds a filter using the given number of hash functions and
// an existing bit set.
func newBloomFilter(hashes int, filter *bitSet) *BloomFilter {
	return &BloomFilter{filter: filter, hashCount: hashes}
}

// add inserts key by setting each of its hash-bucket bits. O(hashCount).
func (bf *BloomFilter) add(key string) {
	for _, bucketIndex := range getHashBuckets(key, bf.hashCount) {
		bf.filter.set(bucketIndex)
	}
}

// isPresent reports whether key may be present. A false result is definitive;
// a true result may be a false positive. O(hashCount).
func (bf *BloomFilter) isPresent(key string) bool {
	for _, bucketIndex := range getHashBuckets(key, bf.hashCount) {
		if !bf.filter.get(bucketIndex) {
			return false
		}
	}
	return true
}

// getHashBuckets is a faithful port of the original Java method, which is a
// stub that returns hashCount zero-valued buckets (real hashing was never
// implemented there). Consequently every key maps to bucket 0.
func getHashBuckets(key string, hashCount int) []int {
	result := make([]int, hashCount)
	return result
}

func main() {
	bf := newBloomFilter(3, &bitSet{})
	bf.add("hello")
	// Note: because getHashBuckets is the original stub (all-zero buckets),
	// any key reports present once any key has been added.
	fmt.Println("isPresent(hello):", bf.isPresent("hello"))
	fmt.Println("isPresent(world):", bf.isPresent("world"))
}
