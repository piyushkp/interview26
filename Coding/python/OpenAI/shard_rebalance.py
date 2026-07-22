import unittest
"""
You have a collection of database shards, each covering a numeric range of
keys. The system currently allows shards to have:
  - Overlapping key ranges (multiple shards might cover the same keys).
  - Missing ranges where no shards cover certain keys ("holes").

rebalance_shards() adjusts shard ranges so that every key is covered by at
most `overlap_threshold` shards, closes gaps, and minimizes data migration.
"""


def _shard_sort_key(shard):
    """Sort key: order shards by (start, end)."""
    return (shard.start, shard.end)


class Shard:
    def __init__(self, shard_id: str, start: int, end: int):
        """Represents a database shard covering keys in the range [start, end]."""
        self.id = shard_id
        self.start = start
        self.end = end

    def covers(self, key: int) -> bool:
        return self.start <= key <= self.end

    def __repr__(self):
        return f"Shard({self.id}, {self.start}, {self.end})"


class Gateway:
    def __init__(self, overlap_threshold: int = 1):
        self.shards: list[Shard] = []
        self.overlap_threshold = overlap_threshold

    def add_shards(self, shard: Shard):
        self.shards.append(shard)

    def remove_shard(self, shard_id: str):
        self.shards = [s for s in self.shards if s.id != shard_id]

    def get_shards_for_key(self, key: int) -> list[Shard]:
        return [s for s in self.shards if s.covers(key)]

    def rebalance_shards(self):
        """Adjust shard ranges so coverage stays within [1, overlap_threshold].

        Algorithm:
          1. Sweep the current layout. If coverage is already between 1 and
             overlap_threshold across the whole [global_start, global_end]
             span (no over-overlap, no holes), do nothing -> zero migration.
          2. Otherwise flatten the shards into a disjoint, gap-free partition:
             sort by start, and give each shard the range starting right after
             the previous shard ends. Pushing a start forward removes overlap;
             pulling it back to prev_end + 1 closes a gap by extending the
             shard leftward. A shard already fully covered is dropped. Each key
             ends up owned by exactly one shard, which trivially respects any
             overlap_threshold >= 1 and leaves no holes.

        Complexity: O(n log n) time (sort + boundary sweep), O(n) space, for
        n shards. Only boundaries move, so unaffected shards never migrate.
        """
        if not self.shards:
            return

        threshold = max(1, self.overlap_threshold)
        shards = sorted(self.shards, key=_shard_sort_key)
        global_start = shards[0].start
        global_end = max(s.end for s in shards)

        if self._is_valid(shards, global_start, global_end, threshold):
            return  # already within [1, threshold] everywhere -> no migration

        result = []
        prev_end = None
        for shard in shards:
            if prev_end is None:
                result.append(shard)          # first shard anchors global_start
                prev_end = shard.end
                continue
            new_start = prev_end + 1
            if new_start > shard.end:
                continue                       # fully covered already -> drop
            shard.start = new_start            # close gap / remove overlap
            result.append(shard)
            prev_end = shard.end
        self.shards = result

    @staticmethod
    def _is_valid(shards, global_start, global_end, threshold):
        """True iff coverage stays within [1, threshold] over the whole span."""
        delta = {}
        for s in shards:
            delta[s.start] = delta.get(s.start, 0) + 1
            delta[s.end + 1] = delta.get(s.end + 1, 0) - 1
        xs = sorted(delta)
        cur = 0
        for i, x in enumerate(xs):
            if i > 0:                          # segment [xs[i-1], x-1] has cov=cur
                if global_start <= xs[i - 1] and x - 1 <= global_end:
                    if cur < 1 or cur > threshold:
                        return False
            cur += delta[x]
        return True


class TestGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = Gateway(overlap_threshold=1)
        self.s1 = Shard("A", 0, 100)
        self.s2 = Shard("B", 80, 180)
        self.s3 = Shard("C", 170, 250)
        self.gateway.add_shards(self.s1)
        self.gateway.add_shards(self.s2)
        self.gateway.add_shards(self.s3)

    def test_overlapping_before_rebalance(self):
        overlapping_before = self.gateway.get_shards_for_key(85)
        self.assertGreaterEqual(len(overlapping_before), 2)

    def test_after_rebalance_no_excessive_overlap(self):
        self.gateway.rebalance_shards()
        for key in [85, 175, 95]:
            shards = self.gateway.get_shards_for_key(key)
            self.assertLessEqual(
                len(shards), self.gateway.overlap_threshold,
                f"Key {key} is covered by too many shards: {shards}")

    def test_overlap_threshold_respected(self):
        gw = Gateway(overlap_threshold=3)
        for s in [Shard("A", 0, 60), Shard("B", 20, 40), Shard("C", 30, 35)]:
            gw.add_shards(s)
        self.assertEqual(len(gw.get_shards_for_key(32)), 3)   # before
        gw.rebalance_shards()
        self.assertLessEqual(len(gw.get_shards_for_key(32)), 3)  # after

    def test_closes_gaps(self):
        gw = Gateway(overlap_threshold=1)
        gw.add_shards(Shard("A", 0, 50))
        gw.add_shards(Shard("B", 100, 150))   # hole in [51, 99]
        gw.rebalance_shards()
        for key in [0, 50, 51, 75, 99, 100, 150]:
            self.assertEqual(len(gw.get_shards_for_key(key)), 1)

    def test_dynamic_add_remove(self):
        gw = Gateway(overlap_threshold=1)
        gw.add_shards(Shard("A", 0, 100))
        gw.add_shards(Shard("B", 50, 200))
        gw.add_shards(Shard("C", 190, 300))
        gw.remove_shard("B")                  # leaves a hole in [101, 189]
        gw.rebalance_shards()
        for key in [0, 100, 101, 150, 189, 190, 300]:
            self.assertEqual(len(gw.get_shards_for_key(key)), 1)


if __name__ == "__main__":
    unittest.main()
