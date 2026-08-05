# Eval Mode Reference

Eval mode runs skill evals and grades expectations. Enables measuring skill performance, comparing with/without skill, and validating that skills add value.

## Purpose

Evals serve to:
1. **Set a floor** - Prove the skill helps Claude do something it couldn't by default
2. **Raise the ceiling** - Enable iterating on skills to improve performance
3. **Measure holistically** - Capture metrics beyond pass/fail (time, tokens)
4. **Understand cross-model behavior** - Test skills across different models

## Eval Workflow

```
0. Choose Workspace Location
   → Ask user where to put workspace, suggest sensible default

1. Check Dependencies
   → Scan skill for dependencies, confirm availability with user

2. Prepare (scripts/prepare_eval.py)
   → Create task, copies skill, stages files (both configs)

3. Execute (agents/executor.md)
   → Set task in_progress (activeForm: "Running executor")
   → Spawn with_skill AND without_skill executors in the SAME turn
   → Executor reads skill, runs prompt, saves transcript
   → Capture total_tokens/duration_ms from each task notification → timing.json

4. Grade (agents/grader.md)
   → Update activeForm to "Grading", spawn grader sub-agent per run
   → Grader reads transcript + outputs, evaluates expectations

5. Complete task, display results
   → Pass/fail per expectation, overall pass rate, metrics
   → Offer the eval viewer (eval-viewer/generate_review.py)
```

## Step 0: Setup

**Before running any evals, read the output schemas:**

```bash
# Read to understand the JSON structures you'll produce
Read references/schemas.md
```

This ensures you know the expected structure for:
- `grading.json` - What the grader produces
- `metrics.json` - What the executor produces
- `timing.json` - Wall clock timing format

**Choose workspace location:**

1. **Suggest default**: `<skill-name>-workspace/` as a sibling to the skill directory
2. **Ask the user** using AskUserQuestion — if the workspace is inside a git repo, suggest adding it to `.gitignore`
3. **Create the workspace directory** once confirmed

## Step 1: Check Dependencies

Before running evals, scan the skill for dependencies:

1. Read SKILL.md and scan its body for dependency hints (tools, MCPs, external services it relies on)
2. Check referenced scripts for required tools
3. Present to user and confirm availability

**Do NOT use `/skill-test` or any other testing skill to run the evals.** Follow this skill's own procedure (executor → grader) directly. An external testing harness bypasses the executor/grader separation this workflow depends on — the same context ends up producing and judging the output, which contaminates the results.

## Step 2: Prepare and Create Task

Run the prepare script for each configuration and create a task. Run directories follow the nested layout from `references/workspace-structure.md` (`eval-<id>/<config>/`) — the same layout `aggregate_benchmark.py` reads:

```bash
scripts/prepare_eval.py <skill-path> <eval-id> --output-dir <workspace>/eval-<id>/with_skill/
scripts/prepare_eval.py <skill-path> <eval-id> --output-dir <workspace>/eval-<id>/without_skill/ --no-skill
```

Each run directory gets an `eval_metadata.json` (prompt, assertions, staged paths). Give evals descriptive `eval_name`s where possible — they read better in the viewer than bare eval numbers (see `references/schemas.md`).

```python
task_id = TaskCreate(
    subject=f"Eval {eval_id}",
    description=f"Prepare, execute, and grade eval {eval_id}",
    activeForm=f"Preparing eval {eval_id}",
)
TaskUpdate(taskId=task_id, status="in_progress")
```

## Step 3: Execute

Update `activeForm` to "Running executor" (status stays `in_progress`) and run the executors:

```bash
echo "{\"executor_start\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > <run-dir>/timing.json
```

**With subagents**: Spawn the `with_skill` AND `without_skill` executors **in the same turn** — don't run with-skill first and come back for the baseline later; launching everything at once means it all finishes around the same time. One executor per configuration, with these instructions:

```
Read agents/executor.md at: <skill-creator-path>/agents/executor.md

Execute this eval:
- Skill path: <workspace>/eval-<id>/<config>/skill/   (omit for without_skill)
- Prompt: <eval prompt from eval_metadata.json>
- Input files: <workspace>/eval-<id>/<config>/inputs/
- Save transcript to: <workspace>/eval-<id>/<config>/outputs/transcript.md
- Save outputs to: <workspace>/eval-<id>/<config>/outputs/
```

**Capture timing as notifications arrive:** each background executor's completion notification carries `total_tokens` and `duration_ms` — this is the *only* place they're reported. Write them into that run's `timing.json` immediately, notification by notification, rather than batching (format in `references/schemas.md`).

**Without subagents**: Read `agents/executor.md` and follow the procedure directly — execute the eval, save the transcript, and produce outputs inline.

After execution completes, update timing.json with executor_end and duration.

## Step 4: Grade

Update `activeForm` to "Grading" (status stays `in_progress`) and run the grader:

**With subagents**: Spawn a grader subagent with these instructions:

```
Read agents/grader.md at: <skill-creator-path>/agents/grader.md

Grade these expectations:
- Assertions: <list from eval_metadata.json>
- Transcript: <workspace>/eval-<id>/<config>/outputs/transcript.md
- Outputs: <workspace>/eval-<id>/<config>/outputs/
- Save grading to: <workspace>/eval-<id>/<config>/grading.json
```

The `expectations[]` entries in grading.json must use exactly the fields `text`/`passed`/`evidence` — the eval viewer shows zeros otherwise (see `references/schemas.md`).

**Without subagents**: Read `agents/grader.md` and follow the procedure directly — evaluate expectations against the transcript and outputs, then save grading.json.

After grading completes, finalize timing.json.

## Step 5: Display Results

Update the task to `completed` (`TaskUpdate(taskId=task_id, status="completed")`). Display:

- Pass/fail status for each expectation with evidence
- Overall pass rate
- Execution metrics from grading.json
- Wall clock time from timing.json
- **User notes summary**: Uncertainties, workarounds, and suggestions from the executor (may reveal issues even when expectations pass)

**Offer the eval viewer.** For anything beyond a single quick run, offer to open the browsable review UI instead of (or in addition to) the text summary — it renders outputs inline and collects per-eval feedback:

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py <workspace> \
  --skill-name "<name>" > /dev/null 2>&1 &
```

Pass `--benchmark <workspace>/benchmark.json` if one exists. In headless environments (no display/browser), use `--static <output_path>` to write a standalone HTML file instead of starting a server — see `references/environments.md`.

## Comparison Workflow

To compare skill-enabled vs no-skill performance:

```
1. Prepare both runs (with --no-skill flag for baseline)
2. Execute both (parallel executors)
3. Grade both (parallel graders)
4. Blind Compare outputs
5. Report winner with analysis
```
