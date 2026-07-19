"""Generate labeling schedules. An assignment is [task_id, model_id, human_id];
tasks are t1..t{total_task}, models m1..m{total_model}, humans
h1..h{total_human}.
Every human must appear in at least k assignments, the same human never
annotates the same task twice, and every ID must be valid. Returns an empty
list if no valid schedule exists.
  - any_schedule             Part 1: any valid schedule.
  - prefix_balanced_schedule Part 2: additionally prefix-balanced.
"""


# Approach (in plain terms):
#   Picture running a workshop where every helper (human) must finish k
#   different tasks, and you want to hand out the work in a tidy, repeatable
#   way.
#     - any_schedule: give each helper k tasks in a row, but start each helper
#       on a different task by rotating the starting point by the helper's
#       number - like dealing cards - so nobody repeats a task and the work
#       spreads out. Model is always m1 because Part 1 only cares about a valid
#       assignment.
#     - prefix_balanced_schedule: instead of finishing one helper at a time, go
#       round by round. In round r every helper does the same task t{r+1} at
#       once, and we rotate which model each helper uses. Because a whole round
#       finishes before the next starts, if you stop reading the list at ANY
#       point everyone has done nearly the same amount - that is what
#       "prefix-balanced" means.
#   No schedule is possible when k distinct tasks cannot fit (k > total_task);
#   when k is 0 there is simply nothing to schedule, so an empty list is the
#   answer.
#   Data structures used:
#     - a plain list that accumulates the [task, model, human] triples,
#       filled by modulo (rotation) index arithmetic - no auxiliary
#       structure needed since the schedule is produced directly in order.
def any_schedule(total_task, total_model, total_human, k):
    """Part 1: any valid schedule. Each human gets k distinct tasks; the
    reference rotates each human's starting task by the human index (human i
    takes tasks (i+0)..(i+k-1) mod total_task). Model is always m1."""
    # h = number of humans, k = required assignments per human.
    # Time:  O(h * k) - emits exactly k rows for each of the h humans.
    # Space: O(h * k) - the returned schedule holds one row per assignment.
    result = []
    if k == 0:
        return result  # no assignments required -> empty schedule is valid
    if k > total_task:
        return result  # cannot give a human k distinct tasks -> impossible
    for human_index in range(total_human):  # human-major order
        for task_offset in range(k):  # the k distinct tasks for this human
            task_index = (human_index + task_offset) % total_task
            result.append([f"t{task_index + 1}", "m1", f"h{human_index + 1}"])
    return result


def prefix_balanced_schedule(total_task, total_model, total_human, k):
    """Part 2: a prefix-balanced schedule. Emitted in k rounds; round r assigns
    task t{r+1} to every human, with human i using model
    m{((i + r) % total_model) + 1}. Every prefix satisfies both balance
    rules."""
    # h = number of humans, k = number of rounds (assignments per human).
    # Time:  O(h * k) - emits one row per human across k rounds.
    # Space: O(h * k) - the returned schedule holds one row per assignment.
    result = []
    if k == 0:
        return result
    if k > total_task:
        return result
    for round_index in range(k):  # round r -> task t{r+1}
        for human_index in range(total_human):  # human index within the round
            model_index = (human_index + round_index) % total_model
            result.append(
                [f"t{round_index + 1}", f"m{model_index + 1}",
                 f"h{human_index + 1}"])
    return result


if __name__ == "__main__":
    # ----- any_schedule -----
    print(any_schedule(3, 1, 2, 2))
    # [['t1', 'm1', 'h1'], ['t2', 'm1', 'h1'], ['t2', 'm1', 'h2'],
    #  ['t3', 'm1', 'h2']]
    print(any_schedule(3, 1, 1, 1))          # [['t1', 'm1', 'h1']]
    print(any_schedule(2, 1, 3, 2))  # rotation wraps around the 2 tasks
    # [['t1', 'm1', 'h1'], ['t2', 'm1', 'h1'], ['t2', 'm1', 'h2'],
    #  ['t1', 'm1', 'h2'], ['t1', 'm1', 'h3'], ['t2', 'm1', 'h3']]
    print(any_schedule(3, 1, 2, 0))  # []  (k == 0 -> nothing to schedule)
    print(any_schedule(2, 1, 2, 3))  # []  (k > total_task -> impossible)
    print(any_schedule(5, 1, 0, 2))          # []  (no humans)

    # ----- prefix_balanced_schedule -----
    print(prefix_balanced_schedule(3, 2, 4, 2))
    # [['t1', 'm1', 'h1'], ['t1', 'm2', 'h2'], ['t1', 'm1', 'h3'],
    #  ['t1', 'm2', 'h4'], ['t2', 'm2', 'h1'], ['t2', 'm1', 'h2'],
    #  ['t2', 'm2', 'h3'], ['t2', 'm1', 'h4']]
    print(prefix_balanced_schedule(3, 2, 2, 1))   # single round, models m1/m2
    # [['t1', 'm1', 'h1'], ['t1', 'm2', 'h2']]
    # model index rotates each round
    print(prefix_balanced_schedule(2, 3, 2, 2))
    # [['t1', 'm1', 'h1'], ['t1', 'm2', 'h2'], ['t2', 'm2', 'h1'],
    #  ['t2', 'm3', 'h2']]
    print(prefix_balanced_schedule(3, 2, 4, 0))   # []  (k == 0)
    print(prefix_balanced_schedule(2, 2, 2, 3))   # []  (k > total_task)
