"""Manage GPU credit batches that expire. A batch added as
(id, amount, timestamp, expiration) is usable during the half-open interval
[timestamp, timestamp + expiration).

  - add(amount, timestamp, expiration): register a credit batch.
  - charge(amount, timestamp): consume amount from batches active at that
    timestamp, soonest-to-expire first; all-or-nothing (no partial charge).
  - balance(timestamp): total remaining credits active at that timestamp.

Operations are applied in input order; a later op may reference an earlier
timestamp but never retroactively changes an already-returned result.
expiration == 0 yields an empty interval (never active).
"""


class _Batch:
    """A credit batch with a mutable remaining amount and its active window."""

    def __init__(self, start, end, remaining):
        # Time: O(1), Space: O(1) - just stores three fields.
        self.start = start
        self.end = end          # exclusive: active in [start, end)
        self.remaining = remaining

    def active_at(self, t):
        # Time: O(1), Space: O(1) - two range comparisons.
        return self.start <= t < self.end and self.remaining > 0


def _batch_end(batch):
    """Sort key: a batch's expiration time (used to take
    soonest-expiring first)."""
    # Time: O(1), Space: O(1) - returns a single field.
    return batch.end


# Approach (in plain terms):
#   Think of each credit grant like a gift card that only works during a
#   certain time window and has some money left on it. We just keep a list
#   of all the gift cards.
#     - balance(t): add up the money left on every card that is still valid at
#       time t.
#     - charge(amount, t): look at all the cards valid at time t. If together
#       they don't have enough, don't charge anything (all-or-nothing). If they
#       do, spend from the card that expires soonest first, so credits get used
#       before they expire and go to waste.
#   Every request tells us its own time, so even if requests arrive out of
#   order, we simply check which cards are valid at that moment.
class GpuCreditManager:

    def __init__(self):
        # Time: O(1), Space: O(1) - starts with an empty batch list.
        self._batches = []

    def add(self, amount, timestamp, expiration):
        """Register a new credit batch active in
        [timestamp, timestamp + expiration)."""
        # Time: O(1) amortized (list append), Space: O(1) per call.
        self._batches.append(_Batch(timestamp, timestamp + expiration, amount))

    def charge(self, amount, timestamp):
        """Consume amount from batches active at timestamp, soonest-expiring
        first. Returns True and applies the deduction only if the active
        balance covers the full amount; otherwise returns False and changes
        nothing."""
        # n = total batches, k = batches active at this timestamp (k <= n).
        # Time:  O(n + k log k) - scan all n batches, then sort the k
        #        active ones.
        # Space: O(k) - the list of active batches.
        # Collect the batches that are active at this timestamp.
        active = []
        total = 0
        for batch in self._batches:
            if batch.active_at(timestamp):
                active.append(batch)
                total += batch.remaining

        if total < amount:
            return False  # insufficient active balance -> no change

        # Consume from the soonest-to-expire batches first.
        active.sort(key=_batch_end)
        need = amount
        for batch in active:
            if need <= 0:
                break
            take = min(batch.remaining, need)
            batch.remaining -= take
            need -= take
        return True

    def balance(self, timestamp):
        """Total remaining credits usable at the given timestamp."""
        # Time: O(n) - scans all n batches once. Space: O(1).
        total = 0
        for batch in self._batches:
            if batch.active_at(timestamp):
                total += batch.remaining
        return total

    @staticmethod
    def simulate(operations):
        """Simulate the manager, returning the result of every non-add op."""
        # m = number of operations, n = batches accumulated so far.
        # Time:  O(m * n log n) worst case (each charge sorts the active
        #        batches).
        # Space: O(m + n) - the results list plus the stored batches.
        mgr = GpuCreditManager()
        results = []
        for op in operations:
            kind = op[0]
            if kind == "add":
                # op[1] = id (unique metadata, unused by the logic)
                mgr.add(op[2], op[3], op[4])
            elif kind == "charge":
                results.append(mgr.charge(op[1], op[2]))
            elif kind == "balance":
                results.append(mgr.balance(op[1]))
            else:
                raise ValueError(f"Unknown op: {kind}")
        return results


if __name__ == "__main__":
    # Test 1: partial charge, then balances before and after expiry.
    gpu1 = [
        ["balance", 5], ["add", "a", 10, 5, 5], ["balance", 7],
        ["charge", 4, 8], ["balance", 8], ["balance", 10],
    ]
    print(GpuCreditManager.simulate(gpu1))  # [0, 10, True, 6, 0]

    # Test 2: two batches, soonest-to-expire consumed first.
    gpu2 = [
        ["add", "a", 5, 10, 10], ["add", "b", 7, 5, 10], ["charge", 5, 12],
        ["balance", 12], ["balance", 17], ["charge", 6, 9], ["balance", 17],
    ]
    print(GpuCreditManager.simulate(gpu2))  # [True, 7, 5, False, 5]

    # Test 3: no batches at all -> nothing to read or charge.
    gpu3 = [
        ["balance", 0], ["charge", 1, 0],
    ]
    print(GpuCreditManager.simulate(gpu3))  # [0, False]

    # Test 4: expiration == 0 -> empty interval, batch is never active.
    gpu4 = [
        ["add", "z", 100, 5, 0], ["balance", 5], ["charge", 1, 5],
    ]
    print(GpuCreditManager.simulate(gpu4))  # [0, False]

    # Test 5: window boundaries - start is inclusive, end is exclusive.
    gpu5 = [
        ["add", "a", 10, 5, 5], ["balance", 5], ["balance", 10],
        ["balance", 4], ["balance", 9],
    ]
    print(GpuCreditManager.simulate(gpu5))  # [10, 0, 0, 10]

    # Test 6: soonest-to-expire batch is drained before the later one.
    gpu6 = [
        ["add", "early", 5, 0, 10], ["add", "late", 5, 0, 20],
        ["charge", 5, 5], ["balance", 12], ["balance", 8],
    ]
    print(GpuCreditManager.simulate(gpu6))  # [True, 5, 5]

    # Test 7: all-or-nothing - an unaffordable charge changes nothing.
    gpu7 = [
        ["add", "a", 3, 0, 100], ["charge", 5, 10], ["balance", 10],
        ["charge", 3, 10], ["balance", 10],
    ]
    print(GpuCreditManager.simulate(gpu7))  # [False, 3, True, 0]

    # Test 8: several charges, including an out-of-order (earlier) timestamp.
    gpu8 = [
        ["add", "a", 10, 100, 50], ["charge", 4, 120], ["charge", 3, 110],
        ["balance", 130], ["charge", 5, 130], ["balance", 200],
    ]
    print(GpuCreditManager.simulate(gpu8))  # [True, True, 3, False, 0]
