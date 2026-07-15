import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

/**
 * Invertible, binary-safe encoding for a Map&lt;String,String&gt;.
 *
 * Because keys/values may contain any character (including '#', ':', '|', '=',
 * spaces), a delimiter-only format is unsafe. Instead each field is
 * LENGTH-PREFIXED as {@code <len>#<content>}, and after reading a length we
 * consume exactly that many characters — so the content may contain anything.
 *
 * Format: {@code <pair_count>#<key_len>#<key><value_len>#<value>...} with pairs
 * written in lexicographically sorted key order, so the output is deterministic.
 * Example: {@code {"a":"hi","b":""}} -&gt; {@code "2#1#a2#hi1#b0#"};
 * the empty map -&gt; {@code "0#"}.
 */
public class MapSerializer {

    /** Serialize a map to the length-prefixed format (keys sorted lexicographically). */
    public static String serialize(Map<String, String> map) {
        TreeMap<String, String> sorted = new TreeMap<>(map); // deterministic key order
        StringBuilder sb = new StringBuilder();
        sb.append(sorted.size()).append('#');
        for (Map.Entry<String, String> e : sorted.entrySet()) {
            String k = e.getKey(), v = e.getValue();
            sb.append(k.length()).append('#').append(k);
            sb.append(v.length()).append('#').append(v);
        }
        return sb.toString();
    }

    /** Reconstruct the original map from a serialized string. */
    public static Map<String, String> deserialize(String data) {
        Map<String, String> map = new LinkedHashMap<>();
        int[] pos = {0};
        int count = readLength(data, pos);
        for (int i = 0; i < count; i++) {
            String key = readField(data, pos);
            String value = readField(data, pos);
            map.put(key, value);
        }
        return map;
    }

    /** Read a run of digits terminated by '#', returning the integer; advances past '#'. */
    private static int readLength(String s, int[] pos) {
        int start = pos[0];
        while (pos[0] < s.length() && s.charAt(pos[0]) != '#') {
            char c = s.charAt(pos[0]);
            if (c < '0' || c > '9') {
                throw new IllegalArgumentException("Malformed: expected digit at index " + pos[0]);
            }
            pos[0]++;
        }
        if (pos[0] >= s.length() || start == pos[0]) {
            throw new IllegalArgumentException("Malformed: missing length or '#'");
        }
        int len = Integer.parseInt(s.substring(start, pos[0]));
        pos[0]++; // skip the '#'
        return len;
    }

    /** Read a length-prefixed field: {@code <len>#<exactly len chars>}. */
    private static String readField(String s, int[] pos) {
        int len = readLength(s, pos);
        if (pos[0] + len > s.length()) {
            throw new IllegalArgumentException("Malformed: field length exceeds input");
        }
        String field = s.substring(pos[0], pos[0] + len);
        pos[0] += len;
        return field;
    }

    /**
     * Single judge-style entry point. If operation == "serialize", data is a
     * Map&lt;String,String&gt; and the result is the serialized String. If
     * operation == "deserialize", data is a serialized String and the result is
     * the reconstructed Map&lt;String,String&gt;.
     */
    @SuppressWarnings("unchecked")
    public static Object solution(String operation, Object data) {
        if ("serialize".equals(operation)) {
            return serialize((Map<String, String>) data);
        } else if ("deserialize".equals(operation)) {
            return deserialize((String) data);
        }
        throw new IllegalArgumentException("Unknown operation: " + operation);
    }
}
