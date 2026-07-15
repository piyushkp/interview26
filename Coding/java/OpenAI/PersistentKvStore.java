import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * A persistent key-value store with a binary-safe serialization format.
 * Keys and values are typed blobs ({@link PyVal}: a "str" or "bytes" payload).
 *
 * Persistence uses LENGTH-PREFIXED encoding (no delimiters), so keys/values
 * may contain any byte (including '|', ':', newlines):
 *   field = [type:1][len:4 big-endian][raw bytes]
 *   map   = [count:4][field key][field value] x count
 *
 *   - Part 1 {@link #simulatePart1}: serialize/deserialize a snapshot to a label.
 *   - Part 2 {@link #simulatePart2}: split a snapshot into size-bounded, order-
 *     independent segments (each segment = [total:4][index:4][chunk]).
 *   - Part 3 {@link #simulatePart3}: snapshot + append-only log with replay on
 *     restart and threshold-based compaction.
 */
public class PersistentKvStore {

    /** A Python-like value: either a str (UTF-8) or a raw bytes blob. */
    public static final class PyVal {
        final boolean isStr;
        final byte[] data;
        PyVal(boolean isStr, byte[] data) {
            this.isStr = isStr;
            this.data = data;
        }
        @Override public boolean equals(Object o) {
            if (!(o instanceof PyVal)) return false;
            PyVal p = (PyVal) o;
            return isStr == p.isStr && Arrays.equals(data, p.data);
        }
        @Override public int hashCode() {
            return (isStr ? 1 : 0) * 31 + Arrays.hashCode(data);
        }
        @Override public String toString() {
            // Python-style repr so demo output matches 'x' (str) vs b'x' (bytes).
            String s = new String(data, isStr ? StandardCharsets.UTF_8 : StandardCharsets.ISO_8859_1);
            return isStr ? "'" + s + "'" : "b'" + s + "'";
        }
    }

    /** Build a PyVal from a demo argument: String -> str, byte[] -> bytes. */
    private static PyVal toPyVal(Object o) {
        if (o instanceof byte[]) {
            return new PyVal(false, (byte[]) o);
        }
        return new PyVal(true, ((String) o).getBytes(StandardCharsets.UTF_8));
    }

    /** Demo helper: represent Python bytes literally (ISO-8859-1, 1 char == 1 byte). */
    static byte[] by(String s) {
        return s.getBytes(StandardCharsets.ISO_8859_1);
    }

    // ---------- binary-safe codec ----------

    private static void writeInt(ByteArrayOutputStream out, int v) {
        out.write((v >>> 24) & 0xFF);
        out.write((v >>> 16) & 0xFF);
        out.write((v >>> 8) & 0xFF);
        out.write(v & 0xFF);
    }

    private static void writeField(ByteArrayOutputStream out, PyVal f) {
        out.write(f.isStr ? 1 : 0);
        writeInt(out, f.data.length);
        out.write(f.data, 0, f.data.length);
    }

    /** Serialize a map to a binary-safe blob. */
    private static byte[] encodeMap(Map<PyVal, PyVal> map) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        writeInt(out, map.size());
        for (Map.Entry<PyVal, PyVal> e : map.entrySet()) {
            writeField(out, e.getKey());
            writeField(out, e.getValue());
        }
        return out.toByteArray();
    }

    private static PyVal readField(ByteBuffer bb) {
        int tag = bb.get() & 0xFF;
        int len = bb.getInt();
        byte[] d = new byte[len];
        bb.get(d);
        return new PyVal(tag == 1, d);
    }

    /** Rebuild a map from a blob produced by {@link #encodeMap}. */
    private static Map<PyVal, PyVal> decodeMap(byte[] blob) {
        Map<PyVal, PyVal> map = new LinkedHashMap<>();
        ByteBuffer bb = ByteBuffer.wrap(blob); // big-endian by default
        int count = bb.getInt();
        for (int i = 0; i < count; i++) {
            PyVal k = readField(bb);
            PyVal v = readField(bb);
            map.put(k, v);
        }
        return map;
    }

    private static int readInt(byte[] b, int off) {
        return ((b[off] & 0xFF) << 24) | ((b[off + 1] & 0xFF) << 16)
             | ((b[off + 2] & 0xFF) << 8) | (b[off + 3] & 0xFF);
    }

    // ---------- Part 1: serialize / deserialize a single snapshot ----------
    public static List<Object> simulatePart1(Object[][] operations) {
        Map<PyVal, PyVal> store = new LinkedHashMap<>();
        Map<String, byte[]> disk = new HashMap<>(); // fake disk: label -> blob
        List<Object> results = new ArrayList<>();
        for (Object[] op : operations) {
            String type = (String) op[0];
            switch (type) {
                case "put":
                    store.put(toPyVal(op[1]), toPyVal(op[2]));
                    break;
                case "delete":
                    store.remove(toPyVal(op[1]));
                    break;
                case "get":
                    results.add(store.get(toPyVal(op[1]))); // PyVal or null (None)
                    break;
                case "serialize":
                    disk.put((String) op[1], encodeMap(store));
                    break;
                case "deserialize":
                    store = decodeMap(disk.get((String) op[1]));
                    break;
                default:
                    throw new IllegalArgumentException("Unknown op: " + type);
            }
        }
        return results;
    }

    // ---------- Part 2: snapshot split across size-bounded segments ----------
    private static final int SEG_HEADER = 8; // [total:4][index:4]

    private static List<byte[]> splitIntoSegments(byte[] snap, int maxSegmentSize) {
        int chunk = maxSegmentSize - SEG_HEADER;      // >= 1 since maxSegmentSize >= 9
        int total = Math.max(1, (snap.length + chunk - 1) / chunk);
        List<byte[]> segs = new ArrayList<>();
        for (int idx = 0, off = 0; idx < total; idx++, off += chunk) {
            int len = Math.min(chunk, snap.length - off);
            ByteArrayOutputStream seg = new ByteArrayOutputStream();
            writeInt(seg, total);
            writeInt(seg, idx);
            if (len > 0) {
                seg.write(snap, off, len);
            }
            segs.add(seg.toByteArray());
        }
        return segs;
    }

    private static byte[] joinSegments(List<byte[]> segments) {
        // Segments may be in any order; sort by their stored index header.
        List<byte[]> ordered = new ArrayList<>(segments);
        ordered.sort((x, y) -> Integer.compare(readInt(x, 4), readInt(y, 4)));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        for (byte[] seg : ordered) {
            out.write(seg, SEG_HEADER, seg.length - SEG_HEADER);
        }
        return out.toByteArray();
    }

    public static List<Object> simulatePart2(int maxSegmentSize, Object[][] operations) {
        Map<PyVal, PyVal> store = new LinkedHashMap<>();
        Map<String, List<byte[]>> disk = new HashMap<>(); // prefix -> segment blobs
        List<Object> results = new ArrayList<>();
        for (Object[] op : operations) {
            String type = (String) op[0];
            switch (type) {
                case "put":
                    store.put(toPyVal(op[1]), toPyVal(op[2]));
                    break;
                case "delete":
                    store.remove(toPyVal(op[1]));
                    break;
                case "get":
                    results.add(store.get(toPyVal(op[1])));
                    break;
                case "serialize":
                    disk.put((String) op[1], splitIntoSegments(encodeMap(store), maxSegmentSize));
                    break;
                case "segment_count":
                    results.add(disk.get((String) op[1]).size());
                    break;
                case "reorder": {
                    List<byte[]> cur = disk.get((String) op[1]);
                    int[] order = (int[]) op[2];
                    List<byte[]> next = new ArrayList<>(order.length);
                    for (int idx : order) {
                        next.add(cur.get(idx)); // physical shuffle; index header preserves truth
                    }
                    disk.put((String) op[1], next);
                    break;
                }
                case "deserialize":
                    store = decodeMap(joinSegments(disk.get((String) op[1])));
                    break;
                default:
                    throw new IllegalArgumentException("Unknown op: " + type);
            }
        }
        return results;
    }

    // ---------- Part 3: snapshot + append-only log with replay & compaction ----------
    private static final class LogRecord {
        final boolean isPut;
        final PyVal key;
        final PyVal val; // null for delete
        LogRecord(boolean isPut, PyVal key, PyVal val) {
            this.isPut = isPut;
            this.key = key;
            this.val = val;
        }
    }

    public static List<Object> simulatePart3(int compactThreshold, Object[][] operations) {
        Map<PyVal, PyVal> store = new LinkedHashMap<>();
        // Persisted artifacts (survive a restart): a snapshot blob + a pending log.
        byte[][] snapshot = { encodeMap(store) };
        List<LogRecord> log = new ArrayList<>();
        int[] compactions = {0};
        List<Object> results = new ArrayList<>();

        for (Object[] op : operations) {
            String type = (String) op[0];
            switch (type) {
                case "put": {
                    PyVal k = toPyVal(op[1]), v = toPyVal(op[2]);
                    store.put(k, v);
                    log.add(new LogRecord(true, k, v));
                    maybeCompact(store, snapshot, log, compactions, compactThreshold);
                    break;
                }
                case "delete": {
                    PyVal k = toPyVal(op[1]);
                    store.remove(k);
                    log.add(new LogRecord(false, k, null));
                    maybeCompact(store, snapshot, log, compactions, compactThreshold);
                    break;
                }
                case "get":
                    results.add(store.get(toPyVal(op[1])));
                    break;
                case "restart":
                    // Throw away memory; reload the snapshot, then replay the log in order.
                    store = decodeMap(snapshot[0]);
                    for (LogRecord rec : log) {
                        if (rec.isPut) {
                            store.put(rec.key, rec.val);
                        } else {
                            store.remove(rec.key);
                        }
                    }
                    break;
                case "status":
                    // (live keys, pending log records, snapshots written)
                    results.add(new int[] {store.size(), log.size(), compactions[0]});
                    break;
                default:
                    throw new IllegalArgumentException("Unknown op: " + type);
            }
        }
        return results;
    }

    private static void maybeCompact(Map<PyVal, PyVal> store, byte[][] snapshot,
                                     List<LogRecord> log, int[] compactions, int threshold) {
        if (log.size() >= threshold) {
            snapshot[0] = encodeMap(store); // fresh full snapshot
            log.clear();                    // clear the pending log
            compactions[0]++;
        }
    }

    /** Render a results list Python-style: PyVal -> repr, null -> None, int[] -> tuple. */
    public static String pyRepr(List<Object> results) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < results.size(); i++) {
            if (i > 0) {
                sb.append(", ");
            }
            Object o = results.get(i);
            if (o == null) {
                sb.append("None");
            } else if (o instanceof int[]) {
                int[] t = (int[]) o;
                sb.append('(');
                for (int j = 0; j < t.length; j++) {
                    if (j > 0) {
                        sb.append(", ");
                    }
                    sb.append(t[j]);
                }
                sb.append(')');
            } else {
                sb.append(o);
            }
        }
        return sb.append(']').toString();
    }
}
