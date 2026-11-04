# Medical Records: Fetch Pages, Filter by Conditions and Historical-Average Weight

Code: [medical_records_filter.py](medical_records_filter.py). Tests: `python3 tests/test_medical_records_filter.py` (needs `requests`).

## 1. Problem Understanding

Fetch every page (10 records each), then keep records that satisfy all conditions. Most conditions compare a field with a constant. The weight condition compares a record's weight with the average of the same patient's earlier weights.

**Assumptions** (state them; the interviewer can overrule):

| Question | Default |
|---|---|
| Endpoint | `GET url?page=N`, pages start at 1, JSON `{"records": [...]}` |
| Last page | An **empty page**, plus a page cap to avoid an endless loop |
| Order | Records can be out of time order, so sort per patient by timestamp (ISO strings sort as text) |
| Weight history | Same patient's **earlier** records. The record being tested isn't included. History is all of the patient's records, not only those passing other conditions. |
| Comparison | `weight > 1.1 * average` (`ratio` parameter) |
| First record | No history, so it doesn't pass |
| Missing/bad values | A missing or unusable value never matches. A record with no usable weight is skipped and adds nothing to the history. |
| Page failure | Retry 3 times with backoff, then **raise**. Partial results would corrupt the averages. |

## 2. Approach & Intuition

1. `fetch_all` loops over pages until one is empty, retrying each page. The HTTP call is a `get` parameter, so tests can pass a fake, and the network stays separate from the filtering.
2. `filter_records` pass 1 (weight): group by patient, sort by time, and walk once with a running `total` and `count`. Test the weight against `total / count` **before** adding it. This is one pass per patient, with no rescanning.
3. Pass 2 (conditions): conditions are data, `(field, operator, constant)` tuples. For a numeric constant the value goes through `float()`, so `"55"` works. A missing field, `None`, `"abc"` or a list raises inside `try`, and the record doesn't match.
4. Return the original record dicts in fetch order, so unused fields are kept.

## 3. Data Structures

- `list` of records, in arrival order.
- `defaultdict(list)`: patient to that patient's records.
- Running `total` and `count` per patient instead of recomputing averages.
- `dict` of `operator` functions: the conditions as data.
- `set` of `id(record)` for the records passing the weight rule, for an O(1) check in the final filter.

## 4. Python Implementation

See [medical_records_filter.py](medical_records_filter.py): two functions, about 70 lines. Usage:

```python
records = fetch_all("https://host/records")
result = filter_records(records, [("age", ">=", 18), ("status", "==", "active")], ratio=1.1)
```

## 5. Complexity Analysis

N records, P ≈ N/10 + 1 pages, C conditions.

- **Fetch:** P requests, which dominate the runtime.
- **Conditions:** O(N·C).
- **Weight:** O(N log N) for the per-patient sort (O(N) if already ordered). No history rescanning.
- **Space:** O(N).

## 6. Dry Run

Patient A has weights 70 (Jan 1), 80 (Mar 1) and 72 (Feb 1), but the Mar 1 record (id 2) arrives before the Feb 1 record (id 3).

| Sorted by time | Weight | History avg | Threshold (×1.1) | Passes? |
|---|---|---|---|---|
| id 1 (Jan 1) | 70 | none | none | no (first record) |
| id 3 (Feb 1) | 72 | 70 | 77 | no |
| id 2 (Mar 1) | `"80"` → 80 | 71 | 78.1 | **yes** |

## 7. Test Cases & Edge Cases

| Case | Expected |
|---|---|
| 23, 20 or 0 records | all records returned, then an empty page stops the loop |
| Endpoint never returns an empty page | `RuntimeError` after `max_pages` |
| Page fails once, then succeeds | retried, all records returned |
| Page keeps failing | exception raised after 3 attempts |
| Age `"34"` (string) | converted, matches |
| Age missing, `None`, `"n/a"` or `[40]` | no match |
| Weight `"80"` (string) | converted to 80.0 |
| Weight missing or `"heavy"` | skipped, not part of the history |
| First record of a patient | never passes |
| Test dataset: weight rule plus `age >= 18`, `status == "active"` | ids `[2, 13]` |
| Test dataset: weight rule only | ids `[2, 8, 11, 13]` |
| Empty input | `[]` |

Ids 8 and 11 pass the weight rule but fail `status` and `age`, which shows the conditions are combined with AND. Ties on the same timestamp keep arrival order (confirm with the interviewer).

## 8. Alternative Approaches

- **Recompute the average per record:** O(N²) for a heavy patient. Avoid.
- **Prefix sums per patient (chosen):** one pass after sorting.
- **Pandas `groupby().expanding().mean().shift()`:** short, but it adds a dependency and hides the missing-value rules.
- **Concurrent fetching:** faster, but needs a bounded worker pool when rate-limited.

## Follow-up Answers

- **Doesn't fit in memory:** keep only `(total, count)` per patient (O(patients) memory). Stream the records in time order via an external sort or a database.
- **Slow and rate-limited:** a small thread pool with a shared token bucket, honoring `Retry-After`. Fetch in windows of N pages and stop at the first empty one.
- **Inserts during paging:** page offsets shift, so records can be skipped or repeated. Dedupe on a record id, or better, use cursor-based paging on an increasing key.
- **Testing without the real endpoint:** `fetch_all` takes the `get` function, so tests pass a fake that returns saved pages. `filter_records` takes plain lists.
