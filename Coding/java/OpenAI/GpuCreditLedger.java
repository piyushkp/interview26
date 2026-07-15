import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * In-memory credit ledger for a shared GPU pool with idempotent events.
 *
 * Event schema (eventId, tenantId, delta): a signed delta changes one tenant's
 * balance. Rules:
 *   - A balance may never go below 0; an event that would make it negative is
 *     rejected (no change).
 *   - Idempotency: a repeated eventId does not change state again and returns
 *     the SAME accept/reject result produced the first time.
 *   - Unknown tenants have balance 0.
 *
 * Average O(1) per get/apply: a HashMap of balances plus a HashMap remembering
 * each processed eventId's first result.
 */
public class GpuCreditLedger {

    private final Map<String, Long> balances = new HashMap<>();
    private final Map<String, Boolean> processed = new HashMap<>(); // eventId -> first result

    /** Apply the initial events in order, using the same rules. */
    public void init(Object[][] events) {
        for (Object[] e : events) {
            apply((String) e[0], (String) e[1], ((Number) e[2]).longValue());
        }
    }

    /** Current balance for a tenant; 0 if unknown. */
    public long getBalance(String tenantId) {
        return balances.getOrDefault(tenantId, 0L);
    }

    /**
     * Apply an event idempotently. Returns true if accepted, false if rejected
     * (would go negative). A duplicate eventId returns its original result
     * without changing state.
     */
    public boolean apply(String eventId, String tenantId, long delta) {
        Boolean prior = processed.get(eventId);
        if (prior != null) {
            return prior; // idempotent replay -> same result, no state change
        }
        long current = balances.getOrDefault(tenantId, 0L);
        long next = current + delta;
        boolean accepted = next >= 0;
        if (accepted) {
            balances.put(tenantId, next);
        }
        processed.put(eventId, accepted); // remember the first-seen result
        return accepted;
    }

    /**
     * Judge entry point. init_events is applied first (in order); then each op is
     * {"get", tenantId} -> append the balance, or {"apply", {eventId, tenantId,
     * delta}} -> append true/false (or the duplicate's original result).
     */
    public static List<Object> solution(Object[][] initEvents, Object[][] operations) {
        GpuCreditLedger ledger = new GpuCreditLedger();
        ledger.init(initEvents);
        List<Object> results = new ArrayList<>();
        for (Object[] op : operations) {
            String type = (String) op[0];
            if ("get".equals(type)) {
                results.add(ledger.getBalance((String) op[1]));
            } else if ("apply".equals(type)) {
                Object[] event = (Object[]) op[1];
                results.add(ledger.apply((String) event[0], (String) event[1],
                                         ((Number) event[2]).longValue()));
            } else {
                throw new IllegalArgumentException("Unknown op: " + type);
            }
        }
        return results;
    }
}
