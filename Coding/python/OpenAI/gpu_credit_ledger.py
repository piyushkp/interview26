"""In-memory credit ledger for a shared GPU pool with idempotent events.

Event schema (event_id, tenant_id, delta): a signed delta changes one tenant's
balance. Rules:
  - A balance may never go below 0; an event that would make it negative is
    rejected (no change).
  - Idempotency: a repeated event_id does not change state again and returns
    the SAME accept/reject result produced the first time.
  - Unknown tenants have balance 0.

Average O(1) per get/apply: a dict of balances plus a dict remembering each
processed event_id's first result.
"""


class GpuCreditLedger:

    def __init__(self):
        self._balances = {}
        self._processed = {}  # event_id -> first result

    def init(self, events):
        """Apply the initial events in order, using the same rules."""
        for e in events:
            self.apply(e[0], e[1], e[2])

    def get_balance(self, tenant_id):
        """Current balance for a tenant; 0 if unknown."""
        return self._balances.get(tenant_id, 0)

    def apply(self, event_id, tenant_id, delta):
        """Apply an event idempotently. Returns True if accepted, False if
        rejected (would go negative). A duplicate event_id returns its original
        result without changing state."""
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
    init1 = [["e1", "tenantA", 10], ["e2", "tenantA", -3], ["e3", "tenantB", 5]]
    ops1 = [
        ["get", "tenantA"], ["get", "tenantB"], ["apply", ["e4", "tenantA", 2]],
        ["apply", ["e5", "tenantB", -6]], ["get", "tenantB"],
        ["apply", ["e6", "tenantA", -4]], ["get", "tenantB"],
    ]
    print(GpuCreditLedger.solution(init1, ops1))  # [7, 5, True, False, 5, True, 5]
    ops2 = [
        ["get", "ghost"], ["apply", ["x1", "ghost", -3]], ["get", "ghost"],
        ["apply", ["x1", "ghost", -3]], ["apply", ["x2", "ghost", 4]], ["get", "ghost"],
    ]
    print(GpuCreditLedger.solution([], ops2))  # [0, False, 0, False, True, 4]
