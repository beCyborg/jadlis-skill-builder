# Coordinator Responsibilities

The coordinator must:

1. **Delegate to subagents when available; otherwise execute inline** - In Improve, Eval, and Benchmark modes, use subagents for executor/grader work when possible. Without subagents, read the agent reference files and follow the procedures directly.
2. **Create mode exception** - Run examples in main loop so user sees the transcript (interactive feedback matters more than consistency)
3. **Use independent grading when possible** - Spawn separate grader/comparator agents for unbiased evaluation. Without subagents, grade inline but acknowledge the limitation.
4. **Track progress with tasks when the task tools are available** - Create tasks, update stages, mark complete. The task tools are off by default on Opus 4.8 / Sonnet 5 / Fable 5 / Mythos 5 and newer (`references/task-tracking.md`); without them, skip the task calls silently and report stage transitions in the response text instead.
5. **Track best version** - The best performer, not the latest iteration
6. **Run multiple times for variance** - 3 runs per configuration when subagents are available; 1 run otherwise
7. **Parallelize independent work** - When subagents are available, spawn independent work in parallel
8. **Report results clearly** - Display pass/fail with evidence and metrics
9. **Review user_notes** - Check executor's user_notes.md for issues that passed expectations might miss
10. **Capture execution metrics** - In Benchmark mode, record tokens/time/tool_calls from each execution
11. **Use most capable model for analysis** - Benchmark analyzer should use the smartest available model
