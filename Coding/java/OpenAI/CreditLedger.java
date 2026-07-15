import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * A GPU credit ledger fed by a stream of requests whose timestamps are NOT
 * necessarily increasing. Each GET reflects only the requests that have arrived
 * so far, evaluated at the query timestamp; a later-arriving request with an
 * earlier timestamp affects future GETs but never retroactively changes a GET
 * that was already returned.
 *
 * Request forms:
 *   ["GRANT",  user, amount, timestamp]  add amount at timestamp
 *   ["CHARGE", user, amount, timestamp]  subtract amount IF the running balance
 *                                        at that moment is >= amount, else ignore
 *   ["GET",    user, timestamp]          balance considering only arrived events
 *                                        with timestamp <= the query timestamp
 *
 * Within a user, events are applied in (timestamp, arrival-order) order — a
 * stable tie-breaker for equal timestamps. Each GET replays that user's
 * eligible events from scratch so charge successes reflect the correct ordering.
 */
public class CreditLedger {

    /** One ledger event for a user. */
    private static final class Event {
        final boolean isGrant;
        final long amount;
        final long timestamp;
        final int arrival;   // index in the input stream -> stable tie-breaker
        Event(boolean isGrant, long amount, long timestamp, int arrival) {
            this.isGrant = isGrant;
            this.amount = amount;
            this.timestamp = timestamp;
            this.arrival = arrival;
        }
    }

    // user -> events that have arrived so far (in arrival order).
    private final Map<String, List<Event>> ledger = new HashMap<>();

    /** Record a GRANT for user. */
    public void grant(String user, long amount, long timestamp, int arrival) {
        ledger.computeIfAbsent(user, x -> new ArrayList<>())
              .add(new Event(true, amount, timestamp, arrival));
    }

    /** Record a CHARGE for user (success is decided later, at replay time). */
    public void charge(String user, long amount, long timestamp, int arrival) {
        ledger.computeIfAbsent(user, x -> new ArrayList<>())
              .add(new Event(false, amount, timestamp, arrival));
    }

    /**
     * Balance for user at the given timestamp, considering only events arrived
     * so far with timestamp <= the query timestamp. Replays those events in
     * (timestamp, arrival) order, applying each charge only if affordable.
     */
    public long get(String user, long timestamp) {
        List<Event> events = ledger.get(user);
        if (events == null) {
            return 0L;
        }
        // Eligible events: timestamp <= query time.
        List<Event> eligible = new ArrayList<>();
        for (Event e : events) {
            if (e.timestamp <= timestamp) {
                eligible.add(e);
            }
        }
        // Apply in (timestamp, arrival) order — stable tie-break by arrival.
        eligible.sort((a, b) -> {
            int byTime = Long.compare(a.timestamp, b.timestamp);
            return byTime != 0 ? byTime : Integer.compare(a.arrival, b.arrival);
        });
        long balance = 0L;
        for (Event e : eligible) {
            if (e.isGrant) {
                balance += e.amount;
            } else if (balance >= e.amount) {
                balance -= e.amount; // charge applied only when affordable
            }
        }
        return balance;
    }

    /**
     * Process the request stream in arrival order, returning the balance for
     * every GET in order. Each request is {"GRANT"/"CHARGE", user, amount, timestamp}
     * or {"GET", user, timestamp}.
     */
    public static List<Long> simulate(Object[][] requests) {
        CreditLedger ledger = new CreditLedger();
        List<Long> results = new ArrayList<>();
        for (int i = 0; i < requests.length; i++) {
            Object[] req = requests[i];
            String type = (String) req[0];
            String user = (String) req[1];
            switch (type) {
                case "GRANT":
                    ledger.grant(user, ((Number) req[2]).longValue(),
                                 ((Number) req[3]).longValue(), i);
                    break;
                case "CHARGE":
                    ledger.charge(user, ((Number) req[2]).longValue(),
                                  ((Number) req[3]).longValue(), i);
                    break;
                case "GET":
                    results.add(ledger.get(user, ((Number) req[2]).longValue()));
                    break;
                default:
                    throw new IllegalArgumentException("Unknown request: " + type);
            }
        }
        return results;
    }
}
