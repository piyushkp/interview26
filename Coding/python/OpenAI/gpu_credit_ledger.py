"""Idempotent in-memory credit ledger for a shared GPU pool, where each
event is identified by a unique event_id.

Overview:
  Tenants hold a credit balance changed by signed events. A balance is
  never allowed to drop below zero, and replaying the same event_id is
  a no-op that returns its original result - safe against duplicate
  deliveries.

Interface (class GpuCreditLedger):
  - init(events) -> None
        Apply a list of initial events in order. Each event is
        [event_id, tenant_id, delta] and follows the same rules as
        apply().
  - get_balance(tenant_id) -> int
        Current balance for a tenant; 0 for an unknown tenant.
  - apply(event_id, tenant_id, delta) -> bool
        Add delta to the tenant's balance. Returns True if accepted,
        False if it would make the balance negative (then nothing
        changes). A repeated event_id returns the SAME result it gave
        the first time and changes no state.
  - solution(init_events, operations) -> list (staticmethod)
        Run init_events, then each op, collecting one result per op.
        Ops:
          ["get", tenant_id] -> int balance
          ["apply", [event_id, tenant, delta]] -> bool accepted
        Any other op kind raises ValueError.

Semantics and rules:
  - Rejection is all-or-nothing: an event that would overdraw is
    dropped entirely (balance unchanged) and reports False.
  - A delta of 0 is accepted and may leave the balance exactly at 0.
  - Idempotency is keyed by event_id GLOBALLY, even across tenants: the
    first tenant to use an id wins; a later reuse just replays the
    stored result.

Constraints/assumptions:
  - event_id values are the identity for idempotency; callers reuse an
    id only when they intend the same logical event.
  - Average O(1) per get/apply via a balances dict and a dict of each
    processed event_id's first result.

Example:
  apply("d", "t", 5) -> True (balance 5); apply("d", "t", 5) again ->
  True, but the balance stays 5 (no double apply).
"""


# Approach (in plain terms):
#   Think of one prepaid wallet per tenant. Each event is a receipt with a
#   unique ID saying "add or subtract this much for this tenant".
#     - Unknown tenants start at 0, and a wallet is never allowed to go
#       negative: if a charge is too big we reject it and leave the wallet
#       untouched.
#     - To stay idempotent we keep a notebook of every receipt ID we've already
#       handled and the yes/no answer we gave. If the same ID shows up again we
#       simply repeat that answer and change nothing - like ignoring a
#       duplicate payment-confirmation email.
#   Data structures used:
#     - two dicts: balances (tenant -> balance) and processed
#       (event_id -> first result) - O(1) balance reads and O(1)
#       idempotency lookups.
class GpuCreditLedger:

    def __init__(self):
        # Time: O(1), Space: O(1) - two empty dictionaries.
        self._balances = {}
        self._processed = {}  # event_id -> first result

    def init(self, events):
        """Apply the initial events in order, using the same rules."""
        # n = number of initial events.
        # Time:  O(n) average - one O(1)-average apply per event.
        # Space: O(n) - balances plus one remembered result per event_id.
        for event in events:
            self.apply(event[0], event[1], event[2])

    def get_balance(self, tenant_id):
        """Current balance for a tenant; 0 if unknown."""
        # Time: O(1) average - a single dict lookup. Space: O(1).
        return self._balances.get(tenant_id, 0)

    def apply(self, event_id, tenant_id, delta):
        """Apply an event idempotently. Returns True if accepted, False if
        rejected (would go negative). A duplicate event_id returns its original
        result without changing state."""
        # Time:  O(1) average - a few dict lookups/inserts.
        # Space: O(1) amortized - may remember one balance and one result.
        prior = self._processed.get(event_id)
        if prior is not None:
            return prior  # idempotent replay -> same result, no state change
        current = self._balances.get(tenant_id, 0)
        nxt = current + delta
        accepted = nxt >= 0
        if accepted:
            self._balances[tenant_id] = nxt
        self._processed[event_id] = accepted  # remember the first-seen result
        return accepted

    @staticmethod
    def solution(init_events, operations):
        """Apply init_events first, then run each op ("get" or "apply")."""
        # n = number of init events, m = number of operations.
        # Time:  O(n + m) average - each event/op is O(1) average.
        # Space: O(n + m) - stored balances and remembered event results.
        ledger = GpuCreditLedger()
        ledger.init(init_events)
        results = []
        for op in operations:
            kind = op[0]
            if kind == "get":
                results.append(ledger.get_balance(op[1]))
            elif kind == "apply":
                event = op[1]
                results.append(ledger.apply(event[0], event[1], event[2]))
            else:
                raise ValueError(f"Unknown op: {kind}")
        return results


if __name__ == "__main__":
    # Test 1: init then mixed get/apply, including a rejected overdraft.
    init1 = [
        ["e1", "tenantA", 10], ["e2", "tenantA", -3], ["e3", "tenantB", 5],
    ]
    ops1 = [
        ["get", "tenantA"], ["get", "tenantB"],
        ["apply", ["e4", "tenantA", 2]],
        ["apply", ["e5", "tenantB", -6]], ["get", "tenantB"],
        ["apply", ["e6", "tenantA", -4]], ["get", "tenantB"],
    ]
    # -> [7, 5, True, False, 5, True, 5]
    print(GpuCreditLedger.solution(init1, ops1))

    # Test 2: unknown tenant starts at 0; duplicate event_id repeats first
    # result.
    ops2 = [
        ["get", "ghost"], ["apply", ["x1", "ghost", -3]], ["get", "ghost"],
        ["apply", ["x1", "ghost", -3]], ["apply", ["x2", "ghost", 4]],
        ["get", "ghost"],
    ]
    print(GpuCreditLedger.solution([], ops2))  # [0, False, 0, False, True, 4]

    # Test 3: no init events and no ops -> empty result.
    print(GpuCreditLedger.solution([], []))  # []

    # Test 4: a duplicate accepted event_id must NOT apply the delta twice.
    init4 = [["g1", "t", 5]]
    ops4 = [
        ["apply", ["g2", "t", 3]], ["get", "t"],
        ["apply", ["g2", "t", 3]], ["get", "t"],
    ]
    print(GpuCreditLedger.solution(init4, ops4))  # [True, 8, True, 8]

    # Test 5: reject an overdraft, then a smaller charge succeeds.
    init5 = [["a", "t", 10]]
    ops5 = [
        ["apply", ["b", "t", -15]], ["get", "t"],
        ["apply", ["c", "t", -4]], ["get", "t"],
    ]
    print(GpuCreditLedger.solution(init5, ops5))  # [False, 10, True, 6]

    # Test 6: zero delta is accepted; balance may land exactly on 0.
    ops6 = [
        ["apply", ["z", "t", 0]], ["get", "t"], ["apply", ["p", "t", 5]],
        ["apply", ["m", "t", -5]], ["get", "t"],
    ]
    print(GpuCreditLedger.solution([], ops6))  # [True, 0, True, True, 0]

    # Test 7: a rejecting event inside init leaves the balance untouched.
    init7 = [["i1", "t", -5], ["i2", "t", 8]]
    print(GpuCreditLedger.solution(init7, [["get", "t"]]))  # [8]

    # Test 8: idempotency is keyed by event_id globally, across tenants.
    ops8 = [
        ["apply", ["dup", "tA", 5]], ["apply", ["dup", "tB", 5]],
        ["get", "tA"], ["get", "tB"],
    ]
    print(GpuCreditLedger.solution([], ops8))  # [True, True, 5, 0]
