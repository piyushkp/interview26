"""Generate labeling schedules. An assignment is [task_id, model_id, human_id];
tasks are t1..t{total_task}, models m1..m{total_model}, humans h1..h{total_human}.
Every human must appear in at least k assignments, the same human never
annotates the same task twice, and every ID must be valid. Returns an empty
list if no valid schedule exists.
  - any_schedule             Part 1: any valid schedule.
  - prefix_balanced_schedule Part 2: additionally prefix-balanced.
"""


def any_schedule(total_task, total_model, total_human, k):
    """Part 1: any valid schedule. Each human gets k distinct tasks; the
    reference rotates each human's starting task by the human index (human i
    takes tasks (i+0)..(i+k-1) mod total_task). Model is always m1."""
    result = []
    if k == 0:
        return result  # no assignments required -> empty schedule is valid
    if k > total_task:
        return result  # cannot give a human k distinct tasks -> impossible
    for i in range(total_human):          # human index (human-major order)
        for j in range(k):                # j-th distinct task for this human
            task_index = (i + j) % total_task
            result.append([f"t{task_index + 1}", "m1", f"h{i + 1}"])
    return result


def prefix_balanced_schedule(total_task, total_model, total_human, k):
    """Part 2: a prefix-balanced schedule. Emitted in k rounds; round r assigns
    task t{r+1} to every human, with human i using model
    m{((i + r) % total_model) + 1}. Every prefix satisfies both balance rules."""
    result = []
    if k == 0:
        return result
    if k > total_task:
        return result
    for r in range(k):                    # round r -> task t{r+1}
        for i in range(total_human):      # human index
            model_index = (i + r) % total_model
            result.append([f"t{r + 1}", f"m{model_index + 1}", f"h{i + 1}"])
    return result


if __name__ == "__main__":
    print(any_schedule(3, 1, 2, 2))
    # [['t1', 'm1', 'h1'], ['t2', 'm1', 'h1'], ['t2', 'm1', 'h2'], ['t3', 'm1', 'h2']]
    print(prefix_balanced_schedule(3, 2, 4, 2))
    # [['t1','m1','h1'], ['t1','m2','h2'], ..., ['t2','m1','h4']]
