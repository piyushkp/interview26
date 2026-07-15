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
    __slots__ = ("start", "end", "remaining")

    def __init__(self, start, end, remaining):
        self.start = start
        self.end = end          # exclusive: active in [start, end)
        self.remaining = remaining

    def active_at(self, t):
        return self.start <= t < self.end and self.remaining > 0


class GpuCreditManager:

    def __init__(self):
        self._batches = []

    def add(self, amount, timestamp, expiration):
        """Register a new credit batch active in [timestamp, timestamp + expiration)."""
        self._batches.append(_Batch(timestamp, timestamp + expiration, amount))

    def charge(self, amount, timestamp):
        """Consume amount from batches active at timestamp, soonest-expiring
        first. Returns True and applies the deduction only if the active balance
        covers the full amount; otherwise returns False and changes nothing."""
        active = [b for b in self._batches if b.active_at(timestamp)]
        total = sum(b.remaining for b in active)
        if total < amount:
            return False  # insufficient active balance -> no change
        # Consume from the soonest-to-expire batches first.
        active.sort(key=lambda b: b.end)
        need = amount
        for b in active:
            if need <= 0:
                break
            take = min(b.remaining, need)
            b.remaining -= take
            need -= take
        return True

    def balance(self, timestamp):
        """Total remaining credits usable at the given timestamp."""
        return sum(b.remaining for b in self._batches if b.active_at(timestamp))

    @staticmethod
    def simulate(operations):
        """Simulate the manager, returning the result of every non-add op."""
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
    gpu1 = [
        ["balance", 5], ["add", "a", 10, 5, 5], ["balance", 7],
        ["charge", 4, 8], ["balance", 8], ["balance", 10],
    ]
    print(GpuCreditManager.simulate(gpu1))  # [0, 10, True, 6, 0]
    gpu2 = [
        ["add", "a", 5, 10, 10], ["add", "b", 7, 5, 10], ["charge", 5, 12],
        ["balance", 12], ["balance", 17], ["charge", 6, 9], ["balance", 17],
    ]
    print(GpuCreditManager.simulate(gpu2))  # [True, 7, 5, False, 5]
