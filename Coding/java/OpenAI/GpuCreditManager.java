import java.util.ArrayList;
import java.util.List;

/**
 * Manage GPU credit batches that expire. A batch added as
 * (id, amount, timestamp, expiration) is usable during the half-open
 * interval [timestamp, timestamp + expiration).
 *
 *   - add(id, amount, timestamp, expiration): register a credit batch.
 *   - charge(amount, timestamp): consume amount from batches active at that
 *     timestamp, soonest-to-expire first; all-or-nothing (no partial charge).
 *   - balance(timestamp): total remaining credits active at that timestamp.
 *
 * Operations are applied in input order; a later op may reference an earlier
 * timestamp but never retroactively changes an already-returned result.
 * All amounts/timestamps use long arithmetic (timestamp + expiration can
 * exceed int range). expiration == 0 yields an empty interval (never active).
 */
public class GpuCreditManager {

    /** A credit batch with a mutable remaining amount and its active window. */
    private static final class Batch {
        final long start;
        final long end;       // exclusive: active in [start, end)
        long remaining;
        Batch(long start, long end, long remaining) {
            this.start = start;
            this.end = end;
            this.remaining = remaining;
        }
        boolean activeAt(long t) {
            return t >= start && t < end && remaining > 0;
        }
    }

    private final List<Batch> batches = new ArrayList<>();

    /** Register a new credit batch active in [timestamp, timestamp + expiration). */
    public void add(long amount, long timestamp, long expiration) {
        batches.add(new Batch(timestamp, timestamp + expiration, amount));
    }

    /**
     * Consume amount from batches active at timestamp, soonest-expiring first.
     * Returns true and applies the deduction only if the active balance covers
     * the full amount; otherwise returns false and changes nothing.
     */
    public boolean charge(long amount, long timestamp) {
        // Collect batches active at this timestamp.
        List<Batch> active = new ArrayList<>();
        long total = 0;
        for (Batch b : batches) {
            if (b.activeAt(timestamp)) {
                active.add(b);
                total += b.remaining;
            }
        }
        if (total < amount) {
            return false; // insufficient active balance -> no change
        }
        // Consume from the soonest-to-expire batches first.
        active.sort((x, y) -> Long.compare(x.end, y.end));
        long need = amount;
        for (Batch b : active) {
            if (need <= 0) {
                break;
            }
            long take = Math.min(b.remaining, need);
            b.remaining -= take;
            need -= take;
        }
        return true;
    }

    /** Total remaining credits usable at the given timestamp. */
    public long balance(long timestamp) {
        long total = 0;
        for (Batch b : batches) {
            if (b.activeAt(timestamp)) {
                total += b.remaining;
            }
        }
        return total;
    }

    /**
     * Simulate the manager from a list of operations, returning the result of
     * every non-add op in order (Boolean for charge, Long for balance). Each op
     * is {"add", id, amount, timestamp, expiration}, {"charge", amount, timestamp},
     * or {"balance", timestamp}.
     */
    public static List<Object> simulate(Object[][] operations) {
        GpuCreditManager mgr = new GpuCreditManager();
        List<Object> results = new ArrayList<>();
        for (Object[] op : operations) {
            String type = (String) op[0];
            switch (type) {
                case "add":
                    // op[1] = id (unique metadata, unused by the logic)
                    mgr.add(((Number) op[2]).longValue(), ((Number) op[3]).longValue(),
                            ((Number) op[4]).longValue());
                    break;
                case "charge":
                    results.add(mgr.charge(((Number) op[1]).longValue(),
                                           ((Number) op[2]).longValue()));
                    break;
                case "balance":
                    results.add(mgr.balance(((Number) op[1]).longValue()));
                    break;
                default:
                    throw new IllegalArgumentException("Unknown op: " + type);
            }
        }
        return results;
    }
}
