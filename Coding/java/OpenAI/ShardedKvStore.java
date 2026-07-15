import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Simulation of a persistent sharded key-value store. Each "shard file" is just
 * a String of appended records; every write is immediately persisted to a shard.
 *
 * Record encoding (keys/values are ASCII letters/digits, never '|' or ';'):
 *   put record:    {@code P|key|value;}
 *   delete record: {@code D|key;}
 *
 * Sharding: append a record to the last shard unless that would make it longer
 * than shard_size; if it would exceed, start a new shard. (A single record is
 * guaranteed to fit in a fresh shard.)
 *
 * Operations: put, get, delete, shutdown (no-op — already persisted), and
 * restore (discard the in-memory map and rebuild by replaying shards in
 * creation order, ignoring any incomplete trailing fragment not ending in ';').
 */
public class ShardedKvStore {

    private final int shardSize;
    private final Map<String, String> store = new LinkedHashMap<>();
    private final List<StringBuilder> shards = new ArrayList<>();

    public ShardedKvStore(int shardSize) {
        this.shardSize = shardSize;
    }

    /** put: persist a put record and set the current value. */
    public void put(String key, String value) {
        appendRecord("P|" + key + "|" + value + ";");
        store.put(key, value);
    }

    /** get: the current value, or null (None) if absent. */
    public String get(String key) {
        return store.get(key);
    }

    /** delete: if the key exists, persist a tombstone and remove it; else do nothing. */
    public void delete(String key) {
        if (store.containsKey(key)) {
            appendRecord("D|" + key + ";");
            store.remove(key);
        }
    }

    /** shutdown: no-op in this simulation (every write is already persisted). */
    public void shutdown() {
        // intentionally empty
    }

    /** restore: discard the in-memory map and rebuild it by replaying the shards. */
    public void restore() {
        store.clear();
        for (StringBuilder shard : shards) {
            replayShard(shard.toString());
        }
    }

    /** Append a record to the last shard, or start a new shard if it would overflow. */
    private void appendRecord(String record) {
        if (shards.isEmpty()
                || shards.get(shards.size() - 1).length() + record.length() > shardSize) {
            shards.add(new StringBuilder(record)); // record always fits a fresh shard
        } else {
            shards.get(shards.size() - 1).append(record);
        }
    }

    /** Replay every complete ';'-terminated record in one shard; ignore a trailing fragment. */
    private void replayShard(String shard) {
        int i = 0;
        while (i < shard.length()) {
            int end = shard.indexOf(';', i);
            if (end < 0) {
                break; // incomplete trailing fragment -> ignore
            }
            applyRecord(shard.substring(i, end)); // record body without the ';'
            i = end + 1;
        }
    }

    /** Apply one decoded record body ("P|key|value" or "D|key") to the map. */
    private void applyRecord(String rec) {
        if (rec.startsWith("P|")) {
            int p1 = rec.indexOf('|');            // after 'P'
            int p2 = rec.indexOf('|', p1 + 1);    // between key and value
            String key = rec.substring(p1 + 1, p2);
            String value = rec.substring(p2 + 1);
            store.put(key, value);
        } else if (rec.startsWith("D|")) {
            store.remove(rec.substring(2));
        }
        // any other (malformed) fragment is ignored
    }

    /** Final shard contents as plain strings. */
    private List<String> shardStrings() {
        List<String> out = new ArrayList<>(shards.size());
        for (StringBuilder s : shards) {
            out.add(s.toString());
        }
        return out;
    }

    /** Result of a run: the get outputs (in order) and the final shard list. */
    public static final class Result {
        public final List<String> getResults; // entries may be null (None)
        public final List<String> shards;
        Result(List<String> getResults, List<String> shards) {
            this.getResults = getResults;
            this.shards = shards;
        }
    }

    /**
     * Run a sequence of operations and return (getResults, shards). Each op is
     * {"put", key, value}, {"get", key}, {"delete", key}, {"shutdown"}, or
     * {"restore"}.
     */
    public static Result simulate(int shardSize, Object[][] operations) {
        ShardedKvStore db = new ShardedKvStore(shardSize);
        List<String> getResults = new ArrayList<>();
        for (Object[] op : operations) {
            String type = (String) op[0];
            switch (type) {
                case "put":
                    db.put((String) op[1], (String) op[2]);
                    break;
                case "get":
                    getResults.add(db.get((String) op[1]));
                    break;
                case "delete":
                    db.delete((String) op[1]);
                    break;
                case "shutdown":
                    db.shutdown();
                    break;
                case "restore":
                    db.restore();
                    break;
                default:
                    throw new IllegalArgumentException("Unknown op: " + type);
            }
        }
        return new Result(getResults, db.shardStrings());
    }

    /** Render a Result Python-tuple style: (['1', '333'], ['P|a|1;']), null -> None. */
    public static String pyRepr(Result r) {
        return "(" + pyList(r.getResults) + ", " + pyList(r.shards) + ")";
    }

    private static String pyList(List<String> items) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < items.size(); i++) {
            if (i > 0) {
                sb.append(", ");
            }
            String s = items.get(i);
            sb.append(s == null ? "None" : "'" + s + "'");
        }
        return sb.append(']').toString();
    }
}
