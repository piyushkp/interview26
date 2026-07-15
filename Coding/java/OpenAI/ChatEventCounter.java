import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * In-memory counter for chat activity per exact (userId, chatId) pair.
 *
 * processEvent records one event; getCount returns how many events for that
 * pair fall in the inclusive 15-minute (900 s) window ending at the pair's
 * most recent timestamp T, i.e. timestamps in [T - 900, T]. Returns 0 if the
 * pair has no events.
 *
 * Because, for a given pair, processEvent timestamps arrive non-decreasing,
 * each pair's list is already sorted, so getCount is a binary search for the
 * window start (no per-call sorting).
 *   - processEvent: O(1) amortized append.
 *   - getCount:     O(log m) over that pair's m events.
 */
public class ChatEventCounter {

    // (userId, chatId) -> ascending list of event timestamps.
    private final Map<String, List<Long>> events = new HashMap<>();

    private static String key(String userId, String chatId) {
        // Length-prefix the userId so distinct pairs can never collide
        // (e.g. ("a", "bc") vs ("ab", "c")).
        return userId.length() + ":" + userId + chatId;
    }

    /** Record one event for (userId, chatId) at the given timestamp. */
    public void processEvent(String userId, String chatId, long timestamp) {
        events.computeIfAbsent(key(userId, chatId), x -> new ArrayList<>()).add(timestamp);
    }

    /** Events for (userId, chatId) within [T - 900, T], where T is the pair's latest timestamp. */
    public int getCount(String userId, String chatId) {
        List<Long> ts = events.get(key(userId, chatId));
        if (ts == null || ts.isEmpty()) {
            return 0;
        }
        long latest = ts.get(ts.size() - 1); // list is sorted -> last is the max
        long windowStart = latest - 900;
        // First index whose timestamp is >= windowStart; everything from there
        // to the end is inside the inclusive window.
        int lo = lowerBound(ts, windowStart);
        return ts.size() - lo;
    }

    /** Smallest index i in a sorted list with a.get(i) >= target (a.size() if none). */
    private static int lowerBound(List<Long> a, long target) {
        int lo = 0, hi = a.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a.get(mid) < target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }

    /**
     * Simulate the counter from a list of operations, returning the result of
     * every getCount in order. Each op is {"processEvent", userId, chatId, timestamp}
     * or {"getCount", userId, chatId}.
     */
    public static List<Integer> simulate(Object[][] operations) {
        ChatEventCounter counter = new ChatEventCounter();
        List<Integer> results = new ArrayList<>();
        for (Object[] op : operations) {
            String type = (String) op[0];
            if ("processEvent".equals(type)) {
                counter.processEvent((String) op[1], (String) op[2], ((Number) op[3]).longValue());
            } else if ("getCount".equals(type)) {
                results.add(counter.getCount((String) op[1], (String) op[2]));
            } else {
                throw new IllegalArgumentException("Unknown op: " + type);
            }
        }
        return results;
    }
}
