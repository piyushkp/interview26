import operator
import time
from collections import defaultdict

import requests

OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt,
       "<=": operator.le, "==": operator.eq, "!=": operator.ne}


def fetch_all(url, get=requests.get, max_pages=10_000, retries=3):
    records = []
    for page in range(1, max_pages + 1):
        for attempt in range(retries):
            try:
                response = get(url, params={"page": page}, timeout=5)
                response.raise_for_status()
                batch = response.json()["records"]
                break
            except requests.RequestException:
                if attempt == retries - 1:
                    raise  # fail loudly: missing pages would corrupt the averages
                time.sleep(2 ** attempt)
        if not batch:  # empty page = end
            return records
        records += batch
    raise RuntimeError("no empty page found; stopping to avoid an endless loop")


def get_timestamp(record):
    return record["timestamp"]


def filter_records(records, conditions, ratio=1.1):
    # Pass 1: records whose weight is above ratio * average of the patient's earlier weights.
    by_patient = defaultdict(list)
    for record in records:
        by_patient[record["patient_id"]].append(record)

    heavy = set()
    for visits in by_patient.values():
        visits.sort(key=get_timestamp)  # ISO timestamps sort as text
        total = count = 0
        for record in visits:
            try:
                weight = float(record["weight"])
            except (KeyError, TypeError, ValueError):
                continue  # no usable weight: skip, and keep it out of the history
            if count and weight > ratio * total / count:  # first record has no history
                heavy.add(id(record))
            total += weight  # added after the test, so a record is not its own history
            count += 1

    # Pass 2: keep heavy records that also satisfy every condition.
    result = []
    for record in records:
        if id(record) not in heavy:
            continue
        for field, op, expected in conditions:
            try:
                value = float(record[field]) if isinstance(expected, (int, float)) else record[field]
                if not OPS[op](value, expected):
                    break
            except (KeyError, TypeError, ValueError):
                break  # missing or bad value never matches
        else:
            result.append(record)
    return result


if __name__ == "__main__":
    records = [
        {"id": 1, "patient_id": "A", "timestamp": "2024-01-01", "weight": 70, "age": 40},
        {"id": 2, "patient_id": "A", "timestamp": "2024-03-01", "weight": "80", "age": 40},
        {"id": 3, "patient_id": "A", "timestamp": "2024-02-01", "weight": 72, "age": 40},
    ]
    print([r["id"] for r in filter_records(records, [("age", ">=", 18)])])  # [2]
