"""Group a workflow's jobs into execution stages by dependency level.

Overview:
  A workflow is a set of named jobs, some of which must wait for others to
  finish. Partition the jobs into ordered stages such that every job's
  prerequisites all live in earlier stages; jobs sharing a stage have no
  dependency between them and can run in parallel. This is a level-by-level
  topological sort (Kahn's algorithm).

Interface:
  workflow_stages(jobs) -> list[list[str]]
      jobs is a dict mapping job name -> config dict. A config may hold a
      "needs" key whose value is a list of job names that must finish first
      (a missing or empty "needs" means no prerequisites). Returns a list of
      stages, each a list of job names sorted alphabetically for
      deterministic output.

Semantics / rules:
  - Stage 0 holds every job with no prerequisites; each later stage holds
    the jobs whose prerequisites all completed in earlier stages.
  - An empty workflow returns an empty list.
  - The input is assumed to be a valid DAG (every name in a "needs" list is
    a real job and there are no cycles); cycles are not detected.

Example:
  workflow_stages({
      "compile": {}, "lint": {},
      "test": {"needs": ["compile", "lint"]},
      "package": {"needs": ["test"]}, "publish": {"needs": ["test"]},
  }) -> [['compile', 'lint'], ['test'], ['package', 'publish']]
"""


# Approach (in plain terms):
#   This is a "who can go next" scheduling problem. For each job we count how
#   many prerequisites it still waits on (its in-degree) and remember which
#   jobs are waiting on it (its dependents). Any job waiting on nobody can run
#   now - those form the first stage. We then finish that whole stage at once:
#   for every job we just ran, tick down its dependents' counters; any that
#   reach zero become the next stage. Repeat until no jobs remain. Each stage
#   is sorted so the output is deterministic. (This is a level-by-level
#   topological sort, i.e. Kahn's algorithm.)
#   Data structures used:
#     - dict in-degree (job -> unmet prerequisite count) - decremented as
#       earlier stages finish; hitting 0 means a job is ready.
#     - dict of lists dependents (job -> jobs that need it) - a reverse
#       adjacency list used to release the next stage.
#     - list of stages (each a sorted list) - the result, one per level.
def workflow_stages(jobs):
    """Return jobs grouped into parallel-executable stages (sorted per stage).
    Jobs in later stages depend on jobs from earlier ones."""
    # j = number of jobs, e = number of dependency edges.
    # Time: O(j log j + e) - each stage sorts its jobs; each edge relaxed once.
    # Space: O(j + e) - the in-degree map and dependents lists.
    indegree = {}
    dependents = {}
    for job in jobs:
        indegree[job] = 0
        dependents[job] = []
    for job in jobs:
        for need in jobs[job].get("needs", []):
            indegree[job] += 1            # one more prerequisite for job
            dependents[need].append(job)  # 'need' must finish before 'job'

    # First stage: every job with no unmet prerequisites.
    current = []
    for job in jobs:
        if indegree[job] == 0:
            current.append(job)
    current.sort()

    stages = []
    while current:
        stages.append(current)
        next_stage = []
        for job in current:
            for dependent in dependents[job]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    next_stage.append(dependent)
        next_stage.sort()
        current = next_stage
    return stages


if __name__ == "__main__":
    # ----- Example from the problem statement -----
    jobs = {
        "compile": {},
        "lint": {},
        "test": {"needs": ["compile", "lint"]},
        "package": {"needs": ["test"]},
        "publish": {"needs": ["test"]},
    }
    print(workflow_stages(jobs))
    # [['compile', 'lint'], ['test'], ['package', 'publish']]

    # ----- No dependencies -> one stage with everything (sorted) -----
    print(workflow_stages({"a": {}, "c": {}, "b": {}}))
    # [['a', 'b', 'c']]

    # ----- A straight chain a -> b -> c -> d -----
    chain = {
        "a": {},
        "b": {"needs": ["a"]},
        "c": {"needs": ["b"]},
        "d": {"needs": ["c"]},
    }
    print(workflow_stages(chain))
    # [['a'], ['b'], ['c'], ['d']]

    # ----- Empty workflow -> no stages -----
    print(workflow_stages({}))
    # []
