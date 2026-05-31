# Task Tracking

Use tasks to track progress on multi-step workflows.

### Task Lifecycle

The Task tools support exactly these statuses: `pending` → `in_progress` → `completed` (plus `deleted` to remove a task). There is no separate "planning"/"reviewing"/"verifying" status — a task is created `pending`, set to `in_progress` while any of its work runs, and `completed` when done. Narrate the current stage with `activeForm`, not with invented statuses.

```
pending ──▶ in_progress ──▶ completed
            (activeForm names the current stage: preparing → executing → grading → done)
```

### Creating Tasks

`TaskCreate` requires both `subject` and `description`. It returns a task id and the task starts `pending`. Capture the id so you can update it later:

```python
task_id = TaskCreate(
    subject="Eval 0, run 1 (with_skill)",
    description="Execute skill eval 0 with the skill loaded and grade expectations",
    activeForm="Preparing eval 0"
)
```

### Updating Stages

Move the single task through the real statuses, and update `activeForm` to reflect the current stage. Pass the captured `taskId` (not the task object):

```python
TaskUpdate(taskId=task_id, status="in_progress", activeForm="Preparing inputs")
TaskUpdate(taskId=task_id, activeForm="Running executor")   # status stays in_progress
TaskUpdate(taskId=task_id, activeForm="Grading expectations")
TaskUpdate(taskId=task_id, status="completed")
```

### Comparison Tasks

For blind comparisons (after all runs complete), create the task with a description and walk it through the same three statuses:

```python
cmp_id = TaskCreate(
    subject="Compare skill-v1 vs skill-v2",
    description="Blind A/B comparison of v1 and v2 outputs; tally votes and declare a winner",
    activeForm="Gathering outputs"
)
TaskUpdate(taskId=cmp_id, status="in_progress", activeForm="Spawning blind comparators")
TaskUpdate(taskId=cmp_id, activeForm="Tallying votes / handling ties")
TaskUpdate(taskId=cmp_id, status="completed")   # winner declared
```
