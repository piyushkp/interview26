"""Tests for Optimizer. Outlines for optional tests, maybe useful after Optimizer is functioning."""

import os
import sys

# NEW: lets this file run directly (python3 test_x.py); run.sh's PYTHONPATH still takes priority.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "solution", "src"))
import unittest

from optimizer import Optimizer
from scheduler import Scheduler
from task import get_test_tasks, get_large_tasks, get_critical_path_tasks


# NEW: a schedule is valid if every task runs once for its full duration, starts only after all its
# dependencies finish, and at most `workers` tasks run at any moment.
def assert_valid_schedule(test, scheduler, workers, total, timeline) -> None:
    names = {t.name for t in scheduler.get_all_tasks()}
    test.assertEqual(set(timeline), names)
    completion = {name: end for name, (_, end) in timeline.items()}
    for name, (start, end) in timeline.items():
        test.assertEqual(end - start, scheduler.get_task(name).duration, name)
        test.assertGreaterEqual(start, scheduler.earliest_start(name, completion), name)
    for moment in {start for start, _ in timeline.values()}:
        busy = sum(1 for start, end in timeline.values() if start <= moment < end)
        test.assertLessEqual(busy, workers, moment)
    test.assertEqual(total, max((end for _, end in timeline.values()), default=0))


class OptimizerTest(unittest.TestCase):

    def test_execution_order_basic(self) -> None:
        scheduler = Scheduler(get_test_tasks())
        optimizer = Optimizer(scheduler)
        order = optimizer.compute_execution_order()
        # UNCOMMENTED (original test_optimizer.py line 16).
        self.assertGreater(len(order), 0, "compute_execution_order returned empty list")

    # UNCOMMENTED (original test_optimizer.py lines 18-26).
    def test_execution_order_all_present(self) -> None:
        scheduler = Scheduler(get_test_tasks())
        optimizer = Optimizer(scheduler)
        order = optimizer.compute_execution_order()
        self.assertEqual(len(order), 5, f"expected 5 tasks, got {len(order)}")
        self.assertEqual(
            sorted(order),
            ["compile", "deploy", "lint", "package", "test"],
        )

    # UNCOMMENTED (original test_optimizer.py lines 28-41).
    def test_execution_order_dependencies_respected(self) -> None:
        scheduler = Scheduler(get_test_tasks())
        optimizer = Optimizer(scheduler)
        order = optimizer.compute_execution_order()
        deploy_idx = order.index("deploy")
        test_idx = order.index("test")
        compile_idx = order.index("compile")
        lint_idx = order.index("lint")
        package_idx = order.index("package")
        self.assertGreater(deploy_idx, test_idx, "deploy must come after test")
        self.assertGreater(deploy_idx, package_idx, "deploy must come after package")
        self.assertGreater(test_idx, compile_idx, "test must come after compile")
        self.assertGreater(package_idx, compile_idx, "package must come after compile")
        self.assertGreater(package_idx, lint_idx, "package must come after lint")

    # UNCOMMENTED (original test_optimizer.py lines 43-51).
    def test_parallel_schedule_basic(self) -> None:
        scheduler = Scheduler(get_test_tasks())
        optimizer = Optimizer(scheduler)
        optimizer.compute_execution_order()
        total_time, timeline = optimizer.parallel_schedule(num_workers=2)
        self.assertEqual(total_time, 8)
        for name, (start, end) in timeline.items():
            task = scheduler.get_task(name)
            self.assertEqual(end - start, task.duration)

    # UNCOMMENTED (original test_optimizer.py lines 53-58).
    def test_parallel_schedule_large(self) -> None:
        scheduler = Scheduler(get_large_tasks())
        optimizer = Optimizer(scheduler)
        optimizer.compute_execution_order()
        total_time, _ = optimizer.parallel_schedule(num_workers=3)
        self.assertEqual(total_time, 26)

    # UNCOMMENTED (original test_optimizer.py lines 60-65).
    def test_parallel_schedule_critical_path(self) -> None:
        scheduler = Scheduler(get_critical_path_tasks())
        optimizer = Optimizer(scheduler)
        optimizer.compute_execution_order()
        total_time, _ = optimizer.parallel_schedule(num_workers=2)
        self.assertEqual(total_time, 26)


    # NEW: edge cases O7-O9 (not in the original tests).
    def test_schedules_are_valid_for_any_worker_count(self) -> None:  # O7
        for tasks in (get_test_tasks(), get_large_tasks(), get_critical_path_tasks()):
            scheduler = Scheduler(tasks)
            for workers in (1, 2, 3, 4, 20):
                total, timeline = Optimizer(scheduler).parallel_schedule(workers)
                assert_valid_schedule(self, scheduler, workers, total, timeline)
            self.assertEqual(Optimizer(scheduler).parallel_schedule(1)[0], sum(t.duration for t in tasks))

    def test_order_on_large_build_is_valid(self) -> None:  # O8
        scheduler = Scheduler(get_large_tasks())
        optimizer = Optimizer(scheduler)
        order = optimizer.compute_execution_order()
        self.assertEqual(sorted(order), sorted(t.name for t in get_large_tasks()))
        for task in get_large_tasks():
            for dep in task.depends_on:
                self.assertLess(order.index(dep), order.index(task.name), (dep, task.name))
        self.assertEqual(optimizer.get_execution_order(), order)

    def test_empty_build_and_bad_worker_count(self) -> None:  # O9
        optimizer = Optimizer(Scheduler([]))
        self.assertEqual(optimizer.compute_execution_order(), [])
        self.assertEqual(optimizer.parallel_schedule(3), (0, {}))
        with self.assertRaises(ValueError):
            Optimizer(Scheduler(get_test_tasks())).parallel_schedule(0)

if __name__ == "__main__":
    unittest.main()
