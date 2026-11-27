"""You'll implement this."""

from typing import Dict, List, Tuple

from scheduler import Scheduler

# NEW: a min-heap for ready and running tasks, a queue for Kahn's algorithm, and type hints.
import heapq
from collections import deque
from typing import Callable, Optional

# V = tasks, E = dependency links, W = workers, O = valid task orders (up to V!).
Timeline = Dict[str, Tuple[int, int]]


class Optimizer:
    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler
        self.execution_order: List[str] = []

    # Kahn's algorithm: start with tasks that have no dependencies, and add a task once its last
    # dependency is placed. Ties keep the input order. Time O(V + E), Space O(V + E)
    def compute_execution_order(self) -> List[str]:
        # CHANGED (original optimizer.py lines 14-15): implemented. Old code:
        #     pass
        #     return self.execution_order
        tasks = self.scheduler.get_all_tasks()
        waiting = {t.name: len(t.depends_on) for t in tasks}
        dependents = self._dependents()
        queue = deque(t.name for t in tasks if waiting[t.name] == 0)
        order: List[str] = []
        while queue:  # each task is queued once
            name = queue.popleft()
            order.append(name)
            for child in dependents[name]:  # each link is used once
                waiting[child] -= 1
                if waiting[child] == 0:
                    queue.append(child)
        self.execution_order = order
        return self.execution_order

    # AI prompt: "Step 1: get the execution order with Kahn's algorithm, then give each task a weight, its
    #   duration plus the largest weight among the tasks that depend on it. Build the dependents map from
    #   depends_on, then fill weights by walking that order backward, so no recursion is needed.
    #   Step 2: implement parallel_schedule with greedy list scheduling, tracking readiness like Kahn's
    #   algorithm (a task is ready when its unfinished-dependency count hits zero): a max-heap of ready tasks
    #   by weight, and a min-heap of running tasks by finish time. Start tasks at the current time, and free
    #   every task finishing at the same moment before refilling workers. Raise ValueError for fewer than one
    #   worker, and return 0 and an empty timeline when there are no tasks; expect 8, 26 and 26 on the given
    #   tests."
    # Optimized: critical-path list scheduling. Time O(V log V + E), Space O(V + E)
    def parallel_schedule(self, num_workers: int) -> Tuple[int, Timeline]:
        # CHANGED (original optimizer.py lines 18-19): implemented. Old code:
        #     pass
        #     return 0, {}
        chain = self._longest_chain_to_end()
        position = {t.name: i for i, t in enumerate(self.scheduler.get_all_tasks())}
        return self._list_schedule(num_workers, lambda name: (-chain[name], position[name]))

    def get_execution_order(self) -> List[str]:
        return self.execution_order

    # NEW: brute force kept so tests can compare it with the optimized parallel_schedule.
    # AI prompt: "Solve this with backtracking over every valid task order, adding a task only once all its
    #   dependencies are placed and undoing it after exploring. Schedule each order greedily on the workers
    #   and keep the shortest total time; with no tasks, return zero and an empty timeline."
    # Brute force: best list schedule over every valid task order. Time O(O·(V log V + E)), Space O(V + E)
    def parallel_schedule_brute_force(self, num_workers: int) -> Tuple[int, Timeline]:
        tasks = self.scheduler.get_all_tasks()
        waiting = {t.name: len(t.depends_on) for t in tasks}
        dependents = self._dependents()
        order: List[str] = []
        placed: set = set()
        best: Optional[Tuple[int, Timeline]] = None

        def explore() -> None:
            nonlocal best
            if len(order) == len(tasks):
                rank = {name: i for i, name in enumerate(order)}
                result = self._list_schedule(num_workers, lambda name: rank[name])
                if best is None or result[0] < best[0]:  # the first best order wins a tie
                    best = result
                return
            for t in tasks:  # every ready task can go next: O orders in total
                if waiting[t.name] == 0 and t.name not in placed:
                    placed.add(t.name)
                    order.append(t.name)
                    for child in dependents[t.name]:
                        waiting[child] -= 1
                    explore()
                    for child in dependents[t.name]:  # undo, so other orders can place this task later
                        waiting[child] += 1
                    order.pop()
                    placed.discard(t.name)

        explore()
        assert best is not None  # a cycle-free task list always has at least one valid order
        return best

    # NEW: event-driven simulation. Whenever workers are free, start the ready tasks with the smallest
    # priority key; a task is ready once all its dependencies have finished. Time O(V log V + E), Space O(V)
    def _list_schedule(self, num_workers: int, priority: Callable[[str], object]) -> Tuple[int, Timeline]:
        if num_workers < 1:
            raise ValueError(f"num_workers must be at least 1, got {num_workers}")
        tasks = self.scheduler.get_all_tasks()
        waiting = {t.name: len(t.depends_on) for t in tasks}
        dependents = self._dependents()
        ready = [(priority(t.name), t.name) for t in tasks if waiting[t.name] == 0]
        heapq.heapify(ready)  # min-heap: the most urgent ready task first
        running: List[Tuple[int, str]] = []  # min-heap of (finish time, task)
        timeline: Timeline = {}
        completion: Dict[str, int] = {}
        now, free = 0, num_workers
        while ready or running:
            while free and ready:  # fill every free worker
                _, name = heapq.heappop(ready)
                start = max(now, self.scheduler.earliest_start(name, completion))  # deps finished by now
                end = start + self.scheduler.get_task(name).duration
                timeline[name] = (start, end)
                heapq.heappush(running, (end, name))
                free -= 1
            now = running[0][0]
            while running and running[0][0] == now:  # free every worker that finishes at this moment
                _, done = heapq.heappop(running)
                completion[done] = now
                free += 1
                for child in dependents[done]:
                    waiting[child] -= 1
                    if waiting[child] == 0:
                        heapq.heappush(ready, (priority(child), child))
        return max((end for _, end in timeline.values()), default=0), timeline

    # NEW: each task's longest chain of durations from its start to the end of the build, itself included.
    # Filled in reverse execution order so every dependent is done first. Time O(V + E), Space O(V)
    def _longest_chain_to_end(self) -> Dict[str, int]:
        dependents = self._dependents()
        chain: Dict[str, int] = {}
        for name in reversed(self.compute_execution_order()):
            longest_after = max((chain[child] for child in dependents[name]), default=0)
            chain[name] = self.scheduler.get_task(name).duration + longest_after
        return chain

    # NEW: task -> the tasks that depend on it, in input order. Time O(V + E), Space O(V + E)
    def _dependents(self) -> Dict[str, List[str]]:
        dependents: Dict[str, List[str]] = {t.name: [] for t in self.scheduler.get_all_tasks()}
        for t in self.scheduler.get_all_tasks():
            for dep in t.depends_on:
                dependents[dep].append(t.name)
        return dependents
