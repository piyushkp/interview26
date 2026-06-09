"""Port of java/Jmetrics.java -> simple metric counters with a scheduled flush.

Original Java package: code.ds

Java concurrency mapping:
  AtomicLong                                 -> _AtomicLong (threading.Lock backed)
  ConcurrentHashMap                          -> dict guarded by a threading.Lock
  ScheduledExecutorService.schedule(t, d, S) -> threading.Timer

The scheduled flush delay is scaled down (SECONDS / 1000) so the demo finishes
in tens of milliseconds instead of waiting 20-60 real seconds. The demo is
deterministic & terminating: every scheduled timer is tracked and joined.
"""

import threading
from datetime import datetime
from typing import Dict, List, Optional


class _AtomicLong:
    def __init__(self, value: int = 0):
        self._value = value
        self._lock = threading.Lock()

    def set(self, value: int) -> None:
        with self._lock:
            self._value = value

    def get(self) -> int:
        with self._lock:
            return self._value

    def increment_and_get(self) -> int:
        with self._lock:
            self._value += 1
            return self._value


class Jmetric:
    def __init__(self):
        self.product_id: Optional[str] = None
        self.tenant_id: Optional[str] = None
        self.doc_type: Optional[str] = None
        self.source: Optional[str] = None
        self.metric_id: Optional[str] = None
        self.metric_value = _AtomicLong()
        self.metric_unit: Optional[str] = None
        self.interval_time = _AtomicLong()


class JmetricsUtil:
    # static ConcurrentHashMap<String, Jmetric>
    map: Dict[str, Jmetric] = {}
    _map_lock = threading.Lock()
    # all scheduled timers so the demo can wait for completion
    _timers: List[threading.Timer] = []
    # scale SECONDS -> seconds/1000 so 60s/20s demos finish quickly
    _SCALE = 1.0 / 1000.0

    def __init__(self, key: str, delay: int):
        timer = threading.Timer(delay * JmetricsUtil._SCALE, self._run, args=(key,))
        timer.daemon = True
        JmetricsUtil._timers.append(timer)
        timer.start()

    def _run(self, key: str) -> None:
        try:
            with JmetricsUtil._map_lock:
                metric = JmetricsUtil.map.get(key)
            if metric is not None:
                print("Doing a task during : " + key + " - Time - " + str(datetime.now()))
                print(key + " metric_value: " + str(metric.metric_value.get()))
                with JmetricsUtil._map_lock:
                    JmetricsUtil.map.pop(key, None)
        except Exception as e:  # pragma: no cover
            print(e)

    @staticmethod
    def wait_all() -> None:
        for t in list(JmetricsUtil._timers):
            t.join()
        JmetricsUtil._timers.clear()


class Jmetrics:
    def onboard_product(self) -> None:
        key = "Onboard" + "onboard_products"
        print(key + " request time: " + str(datetime.now()))
        with JmetricsUtil._map_lock:
            present = key in JmetricsUtil.map
        if not present:
            metric = Jmetric()
            metric.source = "onboard"
            metric.metric_id = "onboard_products"
            metric.metric_unit = "value"
            metric.metric_value.set(1)
            metric.interval_time.set(60)
            with JmetricsUtil._map_lock:
                JmetricsUtil.map[key] = metric
            JmetricsUtil(key, 60)
        else:
            with JmetricsUtil._map_lock:
                metric = JmetricsUtil.map[key]
            metric.metric_value.increment_and_get()

    def onboard_tenant(self) -> None:
        key = "Onboard" + "onboard_tenant"
        print(key + " request time: " + str(datetime.now()))
        with JmetricsUtil._map_lock:
            present = key in JmetricsUtil.map
        if not present:
            metric = Jmetric()
            metric.source = "onboard"
            metric.product_id = "axa"
            metric.metric_id = "onboard_tenant"
            metric.metric_unit = "value"
            metric.metric_value.set(1)
            metric.interval_time.set(20)
            with JmetricsUtil._map_lock:
                JmetricsUtil.map[key] = metric
            JmetricsUtil(key, 20)
        else:
            with JmetricsUtil._map_lock:
                metric = JmetricsUtil.map[key]
            metric.metric_value.increment_and_get()

    def onboard_doctype(self) -> None:
        pass


if __name__ == "__main__":
    obj = Jmetrics()
    obj.onboard_product()
    obj.onboard_product()
    obj.onboard_product()
    obj.onboard_tenant()
    # Wait for the scheduled flush tasks so the program terminates cleanly.
    JmetricsUtil.wait_all()
