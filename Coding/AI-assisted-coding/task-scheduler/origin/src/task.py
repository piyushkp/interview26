"""
Provides task definitions and sample build configurations.
get_test_tasks() is useful when developing your Optimizer.
"""

from typing import List, NamedTuple


class Task(NamedTuple):
    name: str
    duration: int
    depends_on: List[str]


def get_test_tasks() -> List[Task]:
    return [
        Task("compile", 3, []),
        Task("lint", 1, []),
        Task("test", 4, ["compile"]),
        Task("package", 2, ["compile", "lint"]),
        Task("deploy", 1, ["test", "package"]),
    ]


def get_large_tasks() -> List[Task]:
    return [
        Task("fetch-deps", 5, []),
        Task("generate-proto", 3, []),
        Task("compile-core", 6, ["fetch-deps", "generate-proto"]),
        Task("compile-ui", 4, ["fetch-deps"]),
        Task("lint", 2, []),
        Task("test-core", 5, ["compile-core"]),
        Task("test-ui", 3, ["compile-ui"]),
        Task("test-integration", 7, ["compile-core", "compile-ui"]),
        Task("bundle", 2, ["test-core", "test-ui"]),
        Task("deploy-staging", 3, ["bundle", "lint"]),
        Task("smoke-test", 4, ["deploy-staging"]),
        Task("deploy-prod", 1, ["smoke-test", "test-integration"]),
    ]


def get_critical_path_tasks() -> List[Task]:
    return [
        Task("scan-a", 6, []),
        Task("scan-b", 6, []),
        Task("scan-c", 6, []),
        Task("scan-d", 6, []),
        Task("setup", 1, []),
        Task("build-1", 8, ["setup"]),
        Task("build-2", 8, ["build-1"]),
        Task("build-3", 8, ["build-2"]),
        Task("finalize", 1, ["build-3"]),
    ]
