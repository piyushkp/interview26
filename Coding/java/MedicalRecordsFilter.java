package code.ds;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MedicalRecordsFilter {

    // Returns one page of records; an empty list means end of data.
    interface PageFetcher {
        List<Map<String, Object>> fetch(int page) throws IOException;
    }

    static class Condition {
        String field;
        String op;
        Object expected;

        Condition(String field, String op, Object expected) {
            this.field = field;
            this.op = op;
            this.expected = expected;
        }
    }

    static class ByTimestamp implements Comparator<Integer> {
        List<Map<String, Object>> records;

        ByTimestamp(List<Map<String, Object>> records) {
            this.records = records;
        }

        public int compare(Integer a, Integer b) {
            String ta = String.valueOf(records.get(a).get("timestamp"));
            String tb = String.valueOf(records.get(b).get("timestamp"));
            return ta.compareTo(tb); // ISO timestamps sort as text
        }
    }

    static List<Map<String, Object>> fetchAll(PageFetcher fetcher, int maxPages, int retries)
            throws IOException, InterruptedException {
        List<Map<String, Object>> records = new ArrayList<>();
        for (int page = 1; page <= maxPages; page++) {
            List<Map<String, Object>> batch = null;
            for (int attempt = 0; attempt < retries; attempt++) {
                try {
                    batch = fetcher.fetch(page);
                    break;
                } catch (IOException e) {
                    if (attempt == retries - 1) {
                        throw e; // fail loudly: missing pages would corrupt the averages
                    }
                    Thread.sleep(1000L << attempt);
                }
            }
            if (batch == null || batch.isEmpty()) {
                return records;
            }
            records.addAll(batch);
        }
        throw new IllegalStateException("no empty page found; stopping to avoid an endless loop");
    }

    // Returns null when the value is missing or not numeric.
    static Double toDouble(Object value) {
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        if (value instanceof String) {
            try {
                return Double.parseDouble(((String) value).trim());
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }

    static boolean matches(Object value, String op, Object expected) {
        int cmp;
        if (expected instanceof Number) {
            Double number = toDouble(value);
            if (number == null) {
                return false;
            }
            cmp = Double.compare(number, ((Number) expected).doubleValue());
        } else {
            if (value == null) {
                return false;
            }
            cmp = value.toString().compareTo(expected.toString());
        }

        if (op.equals(">")) {
            return cmp > 0;
        } else if (op.equals(">=")) {
            return cmp >= 0;
        } else if (op.equals("<")) {
            return cmp < 0;
        } else if (op.equals("<=")) {
            return cmp <= 0;
        } else if (op.equals("==")) {
            return cmp == 0;
        } else if (op.equals("!=")) {
            return cmp != 0;
        }
        throw new IllegalArgumentException("unknown op: " + op);
    }

    static List<Map<String, Object>> filterRecords(
            List<Map<String, Object>> records, List<Condition> conditions, double ratio) {
        // Pass 1: group record positions by patient.
        Map<Object, List<Integer>> byPatient = new HashMap<>();
        for (int i = 0; i < records.size(); i++) {
            Object patient = records.get(i).get("patient_id");
            if (!byPatient.containsKey(patient)) {
                byPatient.put(patient, new ArrayList<Integer>());
            }
            byPatient.get(patient).add(i);
        }

        // Mark records whose weight is above ratio * average of the patient's earlier weights.
        boolean[] heavy = new boolean[records.size()];
        for (List<Integer> visits : byPatient.values()) {
            Collections.sort(visits, new ByTimestamp(records));
            double total = 0;
            int count = 0;
            for (int index : visits) {
                Double weight = toDouble(records.get(index).get("weight"));
                if (weight == null) {
                    continue; // no usable weight: skip, and keep it out of the history
                }
                if (count > 0 && weight > ratio * total / count) { // first record has no history
                    heavy[index] = true;
                }
                total += weight; // added after the test, so a record is not its own history
                count++;
            }
        }

        // Pass 2: keep heavy records that also satisfy every condition.
        List<Map<String, Object>> result = new ArrayList<>();
        for (int i = 0; i < records.size(); i++) {
            if (!heavy[i]) {
                continue;
            }
            Map<String, Object> record = records.get(i);
            boolean ok = true;
            for (Condition c : conditions) {
                if (!record.containsKey(c.field) || !matches(record.get(c.field), c.op, c.expected)) {
                    ok = false; // missing or bad value never matches
                    break;
                }
            }
            if (ok) {
                result.add(record);
            }
        }
        return result;
    }

    static Map<String, Object> record(int id, String timestamp, Object weight) {
        Map<String, Object> r = new HashMap<>();
        r.put("id", id);
        r.put("patient_id", "A");
        r.put("timestamp", timestamp);
        r.put("weight", weight);
        r.put("age", 40);
        return r;
    }

    public static void main(String[] args) {
        List<Map<String, Object>> records = new ArrayList<>();
        records.add(record(1, "2024-01-01", 70));
        records.add(record(2, "2024-03-01", "80"));
        records.add(record(3, "2024-02-01", 72));

        List<Condition> conditions = new ArrayList<>();
        conditions.add(new Condition("age", ">=", 18));

        List<Integer> ids = new ArrayList<>();
        for (Map<String, Object> r : filterRecords(records, conditions, 1.1)) {
            ids.add((Integer) r.get("id"));
        }
        System.out.println(ids); // [2]
    }
}
