"""You'll implement this."""

from typing import Dict, List, Tuple

from scheduler import Scheduler


class Optimizer:
    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler
        self.execution_order: List[str] = []

    def compute_execution_order(self) -> List[str]:
        pass
        return self.execution_order

    def parallel_schedule(self, num_workers: int) -> Tuple[int, Dict[str, Tuple[int, int]]]:
        pass
        return 0, {}

    def get_execution_order(self) -> List[str]:
        return self.execution_order
