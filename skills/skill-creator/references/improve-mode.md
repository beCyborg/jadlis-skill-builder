## Improving a skill

When user asks to improve a skill, ask:
1. **Which skill?** - Identify the skill to improve
2. **How much time?** - How long can Claude spend iterating?
3. **What's the goal?** - Target quality level, specific issues to fix, or general improvement

Claude should then autonomously iterate using the building blocks (run, grade, compare, analyze) to drive the skill toward the goal within the time budget.

Some advice on writing style when improving a skill:

1. Try to generalize from the feedback, rather than fixing specific examples one by one. The big picture thing that's happening here is that we're trying to create "skills" that can be used a million times (maybe literally, maybe even more who knows) across many different prompts. Here you and the user are iterating on only a few examples over and over again because it helps move faster. The user knows these examples in and out and it's quick for them to assess new outputs. But if the skill you and the user are codeveloping works only for those examples, it's useless. Rather than put in fiddley overfitty changes, or oppressively constrictive MUSTs, if there's some stubborn issue, you might try branching out and using different metaphors, or recommending different patterns of working. It's relatively cheap to try and maybe you'll land on something great.

2. Keep the prompt lean; remove things that aren't pulling their weight. Make sure to read the transcripts, not just the final outputs -- if it looks like the skill is making the model waste a bunch of time doing things that are unproductive, you can try getting rid of the parts of the skill that are making it do that and seeing what happens.

3. Last but not least, try hard to explain the **why** behind everything you're asking the model to do. Today's LLMs are *smart*. They have good theory of mind and when given a good harness and go beyond rote instructions and really make things happen. Even if the feedback from the user is terse or frustrated, try to actually understand the task and why the user is writing what they wrote, and what they actually wrote, and then try to transmit this understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag - try to reframe and explain the reasoning so that the model understands why the thing you're asking for is important. That's a more humane, powerful, and effective approach.

This task is pretty important (we are trying to create billions a year in economic value here!) and your thinking time is not the blocker; take your time and really mull things over. I'd suggest writing a draft skill and then looking at it anew and making improvements. Really try to get into the head of the user and understand what they want and need. Best of luck.

### Setup Phase

0. **Read output schemas**:

   ```bash
   Read references/schemas.md  # JSON structures for grading, history, comparison, analysis
   ```

   This ensures you understand the structure of outputs you'll produce and validate.

1. **Choose workspace location**:

   **Ask the user** where to put the workspace. Suggest `<skill-name>-workspace/` as a sibling to the skill directory, but let the user choose. If the workspace ends up inside a git repo, suggest adding it to `.gitignore`.

2. **Copy skill to v0**:
   ```bash
   scripts/copy_skill.py <skill-path> <skill-name>-workspace/v0 --iteration 0
   ```

3. **Verify or create evals**:
   - Check for existing `evals/evals.json`
   - If missing, ask user for 2-3 example tasks and create evals
   - Use `scripts/init_json.py evals` to create with correct structure

4. **Create tasks** for baseline:

   ```python
   for run in range(3):
       TaskCreate(
           subject=f"Eval baseline, run {run+1}"
       )
   ```

5. **Initialize history.json**:

   ```bash
   scripts/init_json.py history <workspace>/history.json
   ```

   Then edit to fill in skill_name. See `references/schemas.md` for full structure.

### Iteration Loop

For each iteration (0, 1, 2, ...):

#### Step 1: Execute (3 Parallel Runs)

Spawn 3 executor subagents in parallel (or run sequentially without subagents — see "Without subagents" below). Update task to `implementing` stage.

Spawn a subagent for each run with these instructions:

```
Read agents/executor.md at: <skill-creator-path>/agents/executor.md

Execute this task:
- Skill path: workspace/v<N>/skill/
- Task: <eval prompt from evals.json>
- Test files: <eval files if any>
- Save transcript to: workspace/v<N>/runs/run-<R>/transcript.md
- Save outputs to: workspace/v<N>/runs/run-<R>/outputs/
```

#### Step 2: Grade Assertions

Spawn grader subagents (or grade inline — see "Without subagents" below). Update task to `reviewing` stage.

**Purpose**: Grading produces structured pass/fail results for tracking pass rates over iterations. The grader also extracts claims and reads user_notes to surface issues that expectations might miss.

**Set the grader up for success**: The grader needs to actually inspect the outputs, not just read the transcript. If the outputs aren't plain text, tell the grader how to read them — check the skill for inspection tools it already uses and pass those as hints in the grader prompt.

Spawn a subagent with these instructions:

```
Read agents/grader.md at: <skill-creator-path>/agents/grader.md

Grade these expectations:
- Assertions: <list from evals.json>
- Transcript: workspace/v<N>/runs/run-<R>/transcript.md
- Outputs: workspace/v<N>/runs/run-<R>/outputs/
- Save grading to: workspace/v<N>/runs/run-<R>/grading.json

To inspect output files:
<include inspection hints from the skill, e.g.:>
<"Use python -m markitdown <file> to extract text content">
```

**Review grading.json**: Check `user_notes_summary` for uncertainties and workarounds flagged by the executor. Also check `eval_feedback` — if the grader flagged lax assertions or missing coverage, update `evals.json` before continuing. Improving evals mid-loop is fine and often necessary; you can't meaningfully improve a skill if the evals don't measure anything real.

**Eval quality loop**: If `eval_feedback` has suggestions, tighten the assertions and rerun the evals. Keep iterating as long as the grader keeps finding issues. Once `eval_feedback` says the evals look solid (or has no suggestions), move on to skill improvement. Consult the user about what you're doing, but don't block on approval for each round — just keep making progress.

When picking which eval to use for the quality loop, prefer one where the skill partially succeeds — some expectations pass, some fail. An eval where everything fails gives the grader nothing to critique (there are no false positives to catch). The feedback is most useful when some expectations pass and the grader can assess whether those passes reflect genuine quality or surface-level compliance.

#### Step 3: Blind Compare (If N > 0)

For iterations after baseline, use blind comparison:

**Purpose**: While grading tracks expectation pass rates, the comparator judges **holistic output quality** using a rubric. Two outputs might both pass all expectations, but one could still be clearly better. The comparator uses expectations as secondary evidence, not the primary decision factor.

**Blind A/B Protocol:**
1. Randomly assign: 50% chance v<N> is A, 50% chance v<N> is B
2. Record the assignment in `workspace/grading/v<N>-vs-best/assignment.json`
3. Comparator sees only "Output A" and "Output B" - never version names

Spawn a subagent with these instructions:

```
Read agents/comparator.md at: <skill-creator-path>/agents/comparator.md

Blind comparison:
- Eval prompt: <the task that was executed>
- Output A: <path to one version's output>
- Output B: <path to other version's output>
- Assertions: <list from evals.json>

You do NOT know which is old vs new. Judge purely on quality.
```

**Determine winner by majority vote:**
- If 2+ comparators prefer A: A wins
- If 2+ comparators prefer B: B wins
- Otherwise: TIE

#### Step 4: Post-hoc Analysis

After blind comparison, analyze results. Spawn a subagent with these instructions:

```
Read agents/analyzer.md at: <skill-creator-path>/agents/analyzer.md

Analyze:
- Winner: <A or B>
- Winner skill: workspace/<winner-version>/skill/
- Winner transcript: workspace/<winner-version>/runs/run-1/transcript.md
- Loser skill: workspace/<loser-version>/skill/
- Loser transcript: workspace/<loser-version>/runs/run-1/transcript.md
- Comparison result: <from comparator>
```

#### Step 4.5: Launch Eval Viewer for Human Review

After grading and analysis, launch the eval viewer so the user can review outputs qualitatively:

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
  <workspace>/v<N>/runs \
  --skill-name "my-skill" \
  --benchmark <benchmark.json path if available> \
  > /dev/null 2>&1 &
```

For iteration 2+, pass `--previous-workspace` pointing at the previous version's runs. Tell the user: "I've opened the results in your browser. The 'Outputs' tab shows each test case with feedback fields, 'Benchmark' shows quantitative stats. Come back when you're done."

Read `feedback.json` when the user is done. Empty feedback means the output was fine.

#### Step 5: Update State

Update task to `completed` stage. Record results:

```python
if new_version wins majority:
    current_best = new_version
    # Update history.json

history.iterations.append({
    "version": "v<N>",
    "parent": "<previous best>",
    "expectation_pass_rate": 0.85,
    "grading_result": "won" | "lost" | "tie",
    "is_current_best": bool
})
```

#### Step 6: Create New Version (If Continuing)

1. Copy current best to new version:
   ```bash
   scripts/copy_skill.py workspace/<current_best>/skill workspace/v<N+1> \
       --parent <current_best> \
       --iteration <N+1>
   ```

2. Apply improvements from analyzer suggestions

3. Create new tasks for next iteration

4. Continue loop or stop if:
   - **Time budget exhausted**: Track elapsed time, stop when approaching limit
   - **Goal achieved**: Target quality level or pass rate reached
   - **Diminishing returns**: No significant improvement in last 2 iterations
   - **User requests stop**: Check for user input between iterations

### Final Report

When iterations complete:

1. **Best Version**: Which version performed best (not necessarily the last)
2. **Score Progression**: Assertion pass rates across iterations
3. **Key Improvements**: What changes had the most impact
4. **Recommendation**: Whether to adopt the improved skill

Copy best skill back to main location:
```bash
cp -r workspace/<best_version>/skill/* ./
```

Package and present the improved skill:
```bash
scripts/package_skill.py <path/to/skill-folder>
```
Direct the user to the resulting `.skill` file path.

### Without Subagents

Without subagents, Improve mode still works but with reduced rigor:

- **Single run per iteration** (not 3) — variance analysis isn't possible with one run
- **Inline execution**: Read `agents/executor.md` and follow the procedure directly in your main loop. Then read `agents/grader.md` and follow it directly to grade the results.
- **No blind comparison**: You can't meaningfully blind yourself since you have full context. Instead, compare outputs by re-reading both versions' results and analyzing the differences directly.
- **No separate analyzer**: Do the analysis inline after comparing — identify what improved, what regressed, and what to try next.
- **Keep everything else**: Version tracking, copy-iterate-grade loop, history.json, stopping criteria all work the same.
- **Acknowledge reduced rigor**: Without independent agents, grading is less rigorous — the same context that executed the task also grades it. Results are directional, not definitive.
