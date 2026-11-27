"""Read this first."""

from typing import Dict, List, Set

from task import Task


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

    def _check_cycles(self) -> None:
        for task in self._tasks.values():
            for dep_name in task.depends_on:
                dep = self._tasks[dep_name]
                if task.name in dep.depends_on:
                    raise CycleError(f"cycle detected: {task.name} <-> {dep_name}")

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

    def earliest_start(self, name: str, completion_times: Dict[str, int]) -> int:
        task = self._tasks[name]
        if not task.depends_on:
            return 0
        return min(completion_times[dep] for dep in task.depends_on)
