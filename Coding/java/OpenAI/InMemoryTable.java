import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * A simple in-memory SQL-like database for a single table of string cells.
 *
 * A row is identified by a string rowKey; each row maps colKey -> value.
 * Commands (whitespace-separated tokens):
 *   - SET rowKey colKey value     set/overwrite table[rowKey][colKey].
 *   - GET rowKey colKey           the value, or "NULL" if the cell is absent.
 *   - SELECT whereCol whereValue orderByCol
 *         rowKeys where table[row][whereCol] == whereValue, sorted by the
 *         value of orderByCol ascending (missing -> ""), ties broken by rowKey
 *         ascending, joined by single spaces ("" if none match).
 *
 * processCommands returns one output string per GET and SELECT, in order.
 */
public class InMemoryTable {

    // rowKey -> (colKey -> value). LinkedHashMap keeps iteration deterministic.
    private final Map<String, Map<String, String>> table = new LinkedHashMap<>();

    /** SET: set or overwrite a cell. */
    public void set(String rowKey, String colKey, String value) {
        table.computeIfAbsent(rowKey, x -> new LinkedHashMap<>()).put(colKey, value);
    }

    /** GET: the cell value, or "NULL" if the row or column is absent. */
    public String get(String rowKey, String colKey) {
        Map<String, String> row = table.get(rowKey);
        if (row == null) {
            return "NULL";
        }
        String value = row.get(colKey);
        return value == null ? "NULL" : value;
    }

    /**
     * SELECT: rowKeys where whereCol == whereValue, sorted by orderByCol value
     * (missing column -> ""), ties broken by rowKey, joined by single spaces.
     */
    public String select(String whereCol, String whereValue, String orderByCol) {
        List<String> matches = new ArrayList<>();
        for (Map.Entry<String, Map<String, String>> e : table.entrySet()) {
            String cell = e.getValue().get(whereCol);
            if (whereValue.equals(cell)) {
                matches.add(e.getKey());
            }
        }
        matches.sort((r1, r2) -> {
            String s1 = sortValue(r1, orderByCol);
            String s2 = sortValue(r2, orderByCol);
            int byOrder = s1.compareTo(s2);          // lexicographic on orderByCol value
            return byOrder != 0 ? byOrder : r1.compareTo(r2); // tie-break by rowKey
        });
        return String.join(" ", matches);
    }

    /** The orderByCol value for a row, or "" if the row lacks that column. */
    private String sortValue(String rowKey, String orderByCol) {
        String v = table.get(rowKey).get(orderByCol);
        return v == null ? "" : v;
    }

    /**
     * Process whitespace-separated commands, returning one output per GET/SELECT
     * in order. SET produces no output.
     */
    public static List<String> processCommands(List<String> commands) {
        InMemoryTable db = new InMemoryTable();
        List<String> outputs = new ArrayList<>();
        for (String command : commands) {
            String[] t = command.split(" ");
            switch (t[0]) {
                case "SET":
                    db.set(t[1], t[2], t[3]);
                    break;
                case "GET":
                    outputs.add(db.get(t[1], t[2]));
                    break;
                case "SELECT":
                    outputs.add(db.select(t[1], t[2], t[3]));
                    break;
                default:
                    throw new IllegalArgumentException("Unknown command: " + t[0]);
            }
        }
        return outputs;
    }
}
