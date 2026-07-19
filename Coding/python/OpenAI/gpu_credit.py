"""GPU credit calculator whose grants expire over an INCLUSIVE window.
addCredit registers a grant usable during [timestamp, timestamp +
expiration] - BOTH ends included.

Overview:
  Credit is granted in dated chunks that each expire. Spending draws
  from the grants valid at that instant, taking the soonest-to-expire
  first so credit is used before it lapses; a balance never goes below
  zero.

Interface (class GPUCredit, camelCase API):
  - addCredit(credit_id, amount, timestamp, expiration) -> None
        Register a grant of amount usable in
        [timestamp, timestamp + expiration] (inclusive). credit_id is
        only a label (grants may share one) and is not stored.
  - useCredit(timestamp, amount) -> None
        Spend amount at timestamp from soonest-to-expire grants first.
        Partial spends are allowed: it takes what the usable grants
        hold and silently ignores any shortfall (no error, never
        negative). Returns nothing.
  - getBalance(timestamp) -> int
        Total credit still usable at timestamp (0 if none).

Semantics and rules:
  - Both ends of a grant's window count, so a grant added at t with
    expiration e is usable at t and at t + e.
  - Spending order is soonest expiry first; grants that expire at the
    same time break ties by the order they were added.
  - The credit_id does not affect the math; two grants may carry the
    same id.

Constraints/assumptions:
  - Each call carries its own timestamp, so requests may arrive out of
    order without changing an already-returned result.

Example:
  addCredit("microsoft", 10, 10, 30) -> usable in [10, 40];
  getBalance(10) -> 10; getBalance(40) -> 10; getBalance(41) -> 0.
"""


class _Grant:
    """One credit grant: a remaining balance and its inclusive window."""

    def __init__(self, start, end, remaining, order):
        # Time: O(1), Space: O(1) - stores four fields.
        self.start = start
        self.end = end            # inclusive: usable in [start, end]
        self.remaining = remaining
        self.order = order        # insertion index, for stable tie-breaks

    def usable_at(self, t):
        # Time: O(1), Space: O(1) - two range comparisons.
        return self.start <= t <= self.end


def _grant_sort_key(grant):
    """Sort key: soonest-expiring grant first, ties by insertion order."""
    # Time: O(1), Space: O(1) - returns a two-field tuple.
    return (grant.end, grant.order)


# Approach (in plain terms):
#   Think of each credit grant like a prepaid gift card that only works
#   during a fixed time window and still has some money left on it. We keep a
#   list of every card plus a counter remembering the order they were added.
#     - getBalance(t): add up the money left on every card whose window
#       covers time t (both ends count, since the window is inclusive).
#     - useCredit(t, amount): look at the cards valid at time t, then spend
#       starting from the one that expires soonest so credits get used before
#       they lapse. Take as much as each card allows until the request is
#       filled; if the cards together fall short, spend what is there and let
#       the leftover request go unfilled (a balance never goes negative).
#   Because every request states its own time, out-of-order requests simply
#   ask which cards are valid at that instant.
#   Data structures used:
#     - a list of grant objects (start, end, remaining, order) - append-only;
#       each spend filters the currently-usable grants from it.
#     - an integer insertion counter + a named sort key - orders spending by
#       soonest expiry, breaking ties by insertion order.
class GPUCredit:

    def __init__(self):
        # Time: O(1), Space: O(1) - empty grant list and a zero counter.
        self._grants = []
        self._counter = 0

    def addCredit(self, credit_id, amount, timestamp, expiration):
        """Register a grant of amount usable in
        [timestamp, timestamp + expiration] (inclusive)."""
        # Time: O(1) amortized (list append), Space: O(1) per call.
        # credit_id is a label only and is intentionally not stored.
        end = timestamp + expiration
        self._grants.append(_Grant(timestamp, end, amount, self._counter))
        self._counter += 1

    def useCredit(self, timestamp, amount):
        """Spend amount at timestamp, taking from soonest-expiring grants
        first; spends what it can and ignores any unaffordable remainder."""
        # n = total grants, k = grants usable at this timestamp (k <= n).
        # Time:  O(n + k log k) - scan all n grants, then sort the k usable.
        # Space: O(k) - the list of usable grants.
        usable = []
        for grant in self._grants:
            if grant.usable_at(timestamp) and grant.remaining > 0:
                usable.append(grant)

        usable.sort(key=_grant_sort_key)
        need = amount
        for grant in usable:
            if need <= 0:
                break
            take = min(grant.remaining, need)
            grant.remaining -= take
            need -= take

    def getBalance(self, timestamp):
        """Total credit still usable at the given timestamp (0 if none)."""
        # Time: O(n) - scans all n grants once. Space: O(1).
        total = 0
        for grant in self._grants:
            if grant.usable_at(timestamp):
                total += grant.remaining
        return total


if __name__ == "__main__":
    # Example 1: a single grant usable in [10, 40] inclusive.
    g = GPUCredit()
    g.addCredit("microsoft", 10, 10, 30)
    print(g.getBalance(0))     # 0
    print(g.getBalance(10))    # 10
    print(g.getBalance(40))    # 10
    print(g.getBalance(41))    # 0

    # Example 2: spend across time, then add a second grant.
    g = GPUCredit()
    g.addCredit("amazon", 40, 10, 50)
    g.useCredit(30, 30)
    print(g.getBalance(40))    # 10
    g.addCredit("google", 20, 60, 10)
    print(g.getBalance(60))    # 30
    print(g.getBalance(61))    # 20
    print(g.getBalance(70))    # 20
    print(g.getBalance(71))    # 0

    # Example 3: overspending takes all it can and ignores the excess.
    g = GPUCredit()
    g.addCredit("a", 5, 0, 100)        # usable in [0, 100]
    g.useCredit(10, 12)                # only 5 available -> drains to 0
    print(g.getBalance(10))            # 0

    # Example 4: a spend drains the soonest-expiring grant first.
    g = GPUCredit()
    g.addCredit("early", 5, 0, 10)     # usable in [0, 10]
    g.addCredit("late", 5, 0, 30)      # usable in [0, 30]
    g.useCredit(5, 5)                  # both usable; drain 'early' first
    print(g.getBalance(5))             # 5
    print(g.getBalance(20))            # 5

    # Example 5: the same credit_id can label two separate grants.
    g = GPUCredit()
    g.addCredit("dup", 3, 0, 10)       # grant #0, usable [0, 10]
    g.addCredit("dup", 4, 0, 10)       # grant #1, usable [0, 10]
    print(g.getBalance(5))             # 7
    g.useCredit(5, 10)                 # 7 available -> drains both
    print(g.getBalance(5))             # 0

    # Example 6: spending when nothing is usable is a harmless no-op.
    g = GPUCredit()
    g.addCredit("x", 5, 100, 10)       # usable in [100, 110]
    g.useCredit(0, 5)                  # nothing usable at t=0
    print(g.getBalance(105))           # 5
