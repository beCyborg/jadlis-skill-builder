# Delegating Work

There are two patterns for delegating work to building blocks:

**With subagents**: Spawn an independent agent with the reference file instructions. Include the reference file path in the prompt so the subagent knows its role. When tasks are independent (like 3 runs of the same version), spawn all subagents in the same turn for parallelism.

Since v2.1.198 subagents run **in the background by default**: the coordinator keeps working while they run, and each result arrives as a `<task-notification>` when it finishes. Process notifications as they arrive — in particular, persist metrics the notification carries (`total_tokens`, `duration_ms`) immediately, because they aren't reported anywhere else.

**Without subagents**: Read the agent reference file (e.g., `agents/executor.md`) and follow the procedure directly in your main loop. Execute each step sequentially -- the procedures are designed to work both as subagent instructions and as inline procedures.
