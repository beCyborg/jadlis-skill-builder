# Task Tracking

Use tasks to track progress on multi-step workflows.

> **Read this first — the task tools are not always there.** Since v2.1.233
> `TodoWrite`, `TaskCreate`, `TaskGet`, `TaskUpdate`, and `TaskList` are **not
> available** on Opus 4.8, Sonnet 5, Fable 5, Mythos 5, or later versions of those
> families unless the user opts in. Those models track multi-step work without a
> written checklist, and the tool definitions plus reminders cost context, so
> Claude Code leaves them out — nothing is added to the task list while Claude
> works. **Never write a skill that requires these tools to function.** Treat the
> task list as optional progress *reporting* and keep the skill's real state
> somewhere the skill controls (a workspace file, the run directory, the
> orchestrator's return value).

### Availability and how to turn the tools on

On the listed models, any one of these brings the tools back:

- `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` exported **before** Claude Code starts, e.g.
  `CLAUDE_CODE_ENABLE_TODO_TOOLS=1 claude`. This provides the same tools on every
  model and every provider.
- Naming one of the tools in `--allowedTools`, e.g. `claude --allowedTools TaskCreate`.
- Listing them in `--tools`, which restricts the session's built-in tools to the
  ones it names — include the other built-ins the skill needs alongside them.
- In the Agent SDK, the `allowedTools` and `tools` options work like the two flags.

Two contexts always have them, on every model, listed or not: **background
sessions** and **Claude Code on the web**.

On any other model (Opus 4.7, for example) Claude Code provides the four Task
tools by default, and `TodoWrite` only when `CLAUDE_CODE_ENABLE_TASKS=0` is set —
`CLAUDE_CODE_ENABLE_TASKS` selects *which* family a session that has them gets,
while `CLAUDE_CODE_ENABLE_TODO_TOOLS` decides whether it has them at all.

Inheritance: a **subagent** gets the tools only when the parent session has them,
even when the subagent runs a different model. An in-process **agent-team**
teammate follows the session the same way; a teammate in its own split pane is a
separate Claude Code process, so its own model decides. Without the task tools, a
teammate coordinates through messages instead of the shared task list.

### Degrading gracefully

Write skill steps so the task calls are additive, never load-bearing:

- Phrase instructions as "if the task tools are available, create a task for each
  eval; otherwise report stage transitions in the response text."
- Don't derive control flow from a task id or a task's status — keep the id in a
  local variable and the authoritative status in the skill's own files.
- Don't treat a missing tool as an error state to retry; it is the default on the
  current model generation.

The snippets below show the lifecycle **when the tools are present**.

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
