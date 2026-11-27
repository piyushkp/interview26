"""Tests for Optimizer. Outlines for optional tests, maybe useful after Optimizer is functioning."""

import unittest

from optimizer import Optimizer
from scheduler import Scheduler
from task import get_test_tasks, get_large_tasks, get_critical_path_tasks


class OptimizerTest(unittest.TestCase):

    def test_execution_order_basic(self) -> None:
        scheduler = Scheduler(get_test_tasks())
        optimizer = Optimizer(scheduler)
        order = optimizer.compute_execution_order()
        # self.assertGreater(len(order), 0, "compute_execution_order returned empty list")

    # def test_execution_order_all_present(self) -> None:
    #     scheduler = Scheduler(get_test_tasks())
    #     optimizer = Optimizer(scheduler)
    #     order = optimizer.compute_execution_order()
    #     self.assertEqual(len(order), 5, f"expected 5 tasks, got {len(order)}")
    #     self.assertEqual(
    #         sorted(order),
    #         ["compile", "deploy", "lint", "package", "test"],
    #     )

    # def test_execution_order_dependencies_respected(self) -> None:
    #     scheduler = Scheduler(get_test_tasks())
    #     optimizer = Optimizer(scheduler)
    #     order = optimizer.compute_execution_order()
    #     deploy_idx = order.index("deploy")
    #     test_idx = order.index("test")
    #     compile_idx = order.index("compile")
    #     lint_idx = order.index("lint")
    #     package_idx = order.index("package")
    #     self.assertGreater(deploy_idx, test_idx, "deploy must come after test")
    #     self.assertGreater(deploy_idx, package_idx, "deploy must come after package")
    #     self.assertGreater(test_idx, compile_idx, "test must come after compile")
    #     self.assertGreater(package_idx, compile_idx, "package must come after compile")
    #     self.assertGreater(package_idx, lint_idx, "package must come after lint")

    # def test_parallel_schedule_basic(self) -> None:
    #     scheduler = Scheduler(get_test_tasks())
    #     optimizer = Optimizer(scheduler)
    #     optimizer.compute_execution_order()
    #     total_time, timeline = optimizer.parallel_schedule(num_workers=2)
    #     self.assertEqual(total_time, 8)
    #     for name, (start, end) in timeline.items():
    #         task = scheduler.get_task(name)
    #         self.assertEqual(end - start, task.duration)

    # def test_parallel_schedule_large(self) -> None:
    #     scheduler = Scheduler(get_large_tasks())
    #     optimizer = Optimizer(scheduler)
    #     optimizer.compute_execution_order()
    #     total_time, _ = optimizer.parallel_schedule(num_workers=3)
    #     self.assertEqual(total_time, 26)

    # def test_parallel_schedule_critical_path(self) -> None:
    #     scheduler = Scheduler(get_critical_path_tasks())
    #     optimizer = Optimizer(scheduler)
    #     optimizer.compute_execution_order()
    #     total_time, _ = optimizer.parallel_schedule(num_workers=2)
    #     self.assertEqual(total_time, 26)


if __name__ == "__main__":
    unittest.main()
