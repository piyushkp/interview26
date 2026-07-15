import java.util.ArrayList;
import java.util.List;

/**
 * Five self-contained IP exercises that share IPv4 parse/format helpers:
 *   - {@link #parseIPv4(String)}              validate + parse a dotted IPv4 into octets
 *   - {@link #adjacentIPv4(String, String)}   the IPv4 one above/below
 *   - {@link #cidrRange(String)}              first + last address of a CIDR block
 *   - {@link #ipInCidr(String, String)}       membership test for a CIDR block
 *   - {@link #adjacentIPv6(String, String)}   the IPv6 one above/below (period-separated)
 * No networking libraries are used - only manual parsing and arithmetic.
 */
public class IpAddressing {

    // ---------- Part 1: validate & parse IPv4 ----------
    /** Parse a dotted-decimal IPv4 into 4 octets, or an empty list if invalid. */
    public static List<Integer> parseIPv4(String ip) {
        List<Integer> result = new ArrayList<>();
        int[] octets = toOctets(ip);
        if (octets == null) {
            return result; // invalid -> empty list
        }
        for (int o : octets) {
            result.add(o);
        }
        return result;
    }

    // ---------- Part 2: adjacent IPv4 ----------
    /** The IPv4 address one above ('up') or below ('down'); "" on invalid input or over/underflow. */
    public static String adjacentIPv4(String ip, String direction) {
        int[] o = toOctets(ip);
        if (o == null) {
            return "";
        }
        long v = octetsToLong(o);
        if ("up".equals(direction)) {
            if (v == 0xFFFFFFFFL) {
                return ""; // would overflow above 255.255.255.255
            }
            v++;
        } else if ("down".equals(direction)) {
            if (v == 0L) {
                return ""; // would underflow below 0.0.0.0
            }
            v--;
        } else {
            return ""; // invalid direction
        }
        return longToIPv4(v);
    }

    // ---------- Part 3: first & last address of a CIDR block ----------
    /** Inclusive [first, last] addresses of A.B.C.D/P (host bits ignored); empty list if invalid. */
    public static List<String> cidrRange(String cidr) {
        List<String> result = new ArrayList<>();
        long[] firstLast = cidrFirstLast(cidr);
        if (firstLast == null) {
            return result;
        }
        result.add(longToIPv4(firstLast[0]));
        result.add(longToIPv4(firstLast[1]));
        return result;
    }

    // ---------- Part 4: membership in a CIDR block ----------
    /** 1 if ip is inside cidr (inclusive), 0 if not, -1 if either input is invalid. */
    public static int ipInCidr(String ip, String cidr) {
        int[] o = toOctets(ip);
        long[] firstLast = cidrFirstLast(cidr);
        if (o == null || firstLast == null) {
            return -1;
        }
        long v = octetsToLong(o);
        return (v >= firstLast[0] && v <= firstLast[1]) ? 1 : 0;
    }

    // ---------- Part 5: adjacent IPv6 (8 period-separated hex groups) ----------
    /**
     * The IPv6 address one above ('up') or below ('down'), normalized to eight
     * lowercase 4-digit hex groups separated by '.'; "" on invalid input,
     * invalid direction, or 128-bit over/underflow. Compressed '::' is NOT allowed.
     */
    public static String adjacentIPv6(String ip, String direction) {
        int[] groups = toGroups(ip);
        if (groups == null) {
            return "";
        }
        boolean up;
        if ("up".equals(direction)) {
            up = true;
        } else if ("down".equals(direction)) {
            up = false;
        } else {
            return ""; // invalid direction
        }

        int i = 7;
        if (up) {
            // propagate carry from the least-significant group
            while (i >= 0 && groups[i] == 0xFFFF) {
                groups[i] = 0;
                i--;
            }
            if (i < 0) {
                return ""; // overflow above ffff.ffff...ffff
            }
            groups[i]++;
        } else {
            // propagate borrow from the least-significant group
            while (i >= 0 && groups[i] == 0) {
                groups[i] = 0xFFFF;
                i--;
            }
            if (i < 0) {
                return ""; // underflow below 0000.0000...0000
            }
            groups[i]--;
        }

        StringBuilder sb = new StringBuilder();
        for (int g = 0; g < 8; g++) {
            if (g > 0) {
                sb.append('.');
            }
            sb.append(toHex4(groups[g]));
        }
        return sb.toString();
    }

    // ---------- shared helpers ----------

    /** Validate and split a dotted-decimal IPv4 into 4 octets, or null if invalid. */
    private static int[] toOctets(String ip) {
        String[] parts = splitExact(ip, '.', 4);
        if (parts == null) {
            return null;
        }
        int[] octets = new int[4];
        for (int i = 0; i < 4; i++) {
            int v = parseOctet(parts[i]);
            if (v < 0) {
                return null;
            }
            octets[i] = v;
        }
        return octets;
    }

    /** Parse a decimal octet (digits only, leading zeros allowed, 0..255); -1 if invalid. */
    private static int parseOctet(String s) {
        if (s == null || s.isEmpty()) {
            return -1;
        }
        int value = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < '0' || c > '9') {
                return -1;
            }
            value = value * 10 + (c - '0');
            if (value > 255) {
                return -1; // also guards against overflow on long inputs
            }
        }
        return value;
    }

    /** {first, last} of a CIDR block, or null if invalid. */
    private static long[] cidrFirstLast(String cidr) {
        String[] parts = splitExact(cidr, '/', 2);
        if (parts == null) {
            return null;
        }
        int[] o = toOctets(parts[0]);
        if (o == null) {
            return null;
        }
        int prefix = parsePrefix(parts[1]);
        if (prefix < 0) {
            return null; // prefix must be 0..32
        }
        long base = octetsToLong(o);
        long mask = (prefix == 0) ? 0L : ((0xFFFFFFFFL << (32 - prefix)) & 0xFFFFFFFFL);
        long first = base & mask;
        long last = first | (~mask & 0xFFFFFFFFL);
        return new long[] {first, last};
    }

    /** Parse a CIDR prefix length (digits only); -1 if not an integer in [0, 32]. */
    private static int parsePrefix(String s) {
        if (s == null || s.isEmpty()) {
            return -1;
        }
        int value = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c < '0' || c > '9') {
                return -1;
            }
            value = value * 10 + (c - '0');
            if (value > 32) {
                return -1;
            }
        }
        return value;
    }

    /** Parse the 8 period-separated hex groups (1..4 hex digits each); null if invalid. */
    private static int[] toGroups(String ip) {
        String[] parts = splitExact(ip, '.', 8);
        if (parts == null) {
            return null;
        }
        int[] groups = new int[8];
        for (int i = 0; i < 8; i++) {
            int v = parseHexGroup(parts[i]);
            if (v < 0) {
                return null;
            }
            groups[i] = v;
        }
        return groups;
    }

    /** Parse a 1..4 digit hex group into 0..0xFFFF; -1 if invalid. */
    private static int parseHexGroup(String s) {
        if (s == null || s.isEmpty() || s.length() > 4) {
            return -1;
        }
        int value = 0;
        for (int i = 0; i < s.length(); i++) {
            int d = hexVal(s.charAt(i));
            if (d < 0) {
                return -1;
            }
            value = value * 16 + d;
        }
        return value;
    }

    private static int hexVal(char c) {
        if (c >= '0' && c <= '9') {
            return c - '0';
        }
        if (c >= 'a' && c <= 'f') {
            return c - 'a' + 10;
        }
        if (c >= 'A' && c <= 'F') {
            return c - 'A' + 10;
        }
        return -1;
    }

    /** Format a 16-bit value as exactly 4 lowercase hex digits. */
    private static String toHex4(int v) {
        char[] hex = "0123456789abcdef".toCharArray();
        char[] out = new char[4];
        out[0] = hex[(v >> 12) & 0xF];
        out[1] = hex[(v >> 8) & 0xF];
        out[2] = hex[(v >> 4) & 0xF];
        out[3] = hex[v & 0xF];
        return new String(out);
    }

    /**
     * Split s on delim with no merging (trailing empties kept); returns the parts
     * only if there are exactly 'expected' of them, else null.
     */
    private static String[] splitExact(String s, char delim, int expected) {
        if (s == null) {
            return null;
        }
        List<String> parts = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == delim) {
                parts.add(cur.toString());
                cur.setLength(0);
            } else {
                cur.append(c);
            }
        }
        parts.add(cur.toString());
        if (parts.size() != expected) {
            return null;
        }
        return parts.toArray(new String[0]);
    }

    private static long octetsToLong(int[] o) {
        return ((long) o[0] << 24) | ((long) o[1] << 16) | ((long) o[2] << 8) | o[3];
    }

    private static String longToIPv4(long v) {
        long a = (v >> 24) & 0xFF, b = (v >> 16) & 0xFF, c = (v >> 8) & 0xFF, d = v & 0xFF;
        return a + "." + b + "." + c + "." + d;
    }
}
