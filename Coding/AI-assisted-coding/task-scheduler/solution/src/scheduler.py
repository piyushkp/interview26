"""Read this first."""

from typing import Dict, List, Set

from task import Task

# V = tasks, E = dependency links, d = dependencies of one task.


class CycleError(Exception):
    pass


class Scheduler:
    def __init__(self, tasks: List[Task]):
        self._tasks: Dict[str, Task] = {t.name: t for t in tasks}
        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        for task in self._tasks.values():
            for dep in task.depends_on:
                if dep not in self._tasks:
                    raise ValueError(f"unknown dependency '{dep}' in task '{task.name}'")
        self._check_cycles()

    # Kahn's algorithm: peel off tasks with no unfinished dependencies; any task left over is on a cycle.
    # Time O(V + E), Space O(V)
    def _check_cycles(self) -> None:
        # BUG FIX 1 (original scheduler.py lines 24-29): it only compared each task with its direct
        # dependencies, so it caught a <-> b but missed longer cycles like a -> c -> b -> a.
        # Old code:
        #     for task in self._tasks.values():
        #         for dep_name in task.depends_on:
        #             dep = self._tasks[dep_name]
        #             if task.name in dep.depends_on:
        #                 raise CycleError(f"cycle detected: {task.name} <-> {dep_name}")
        waiting = {name: len(task.depends_on) for name, task in self._tasks.items()}
        dependents: Dict[str, List[str]] = {name: [] for name in self._tasks}
        for task in self._tasks.values():
            for dep_name in task.depends_on:
                dependents[dep_name].append(task.name)
        free = [name for name, count in waiting.items() if count == 0]
        while free:  # each task is freed once: O(V + E)
            for child in dependents[free.pop()]:
                waiting[child] -= 1
                if waiting[child] == 0:
                    free.append(child)
        stuck = sorted(name for name, count in waiting.items() if count > 0)
        if stuck:
            raise CycleError(f"cycle detected among: {', '.join(stuck)}")

    def get_task(self, name: str) -> Task:
        return self._tasks[name]

    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def get_ready_tasks(self, completed: Set[str]) -> List[Task]:
        ready: List[Task] = []
        for task in self._tasks.values():
            if task.name in completed:
                continue
            if all(dep in completed for dep in task.depends_on):
                ready.append(task)
        return ready

    # A task can start once its last dependency finishes. Time O(d), Space O(1)
    def earliest_start(self, name: str, completion_times: Dict[str, int]) -> int:
        task = self._tasks[name]
        if not task.depends_on:
            return 0
        # BUG FIX 2 (original scheduler.py line 50): a task needs all its dependencies done, so it waits for
        # the latest one, not the earliest. Old code:
        #     return min(completion_times[dep] for dep in task.depends_on)
        return max(completion_times[dep] for dep in task.depends_on)
