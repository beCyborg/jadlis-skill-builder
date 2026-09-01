# JSON Schemas

> Last audited against Claude Code docs: 2026-09-01 (~v2.1.251, mirror b290425)

This document defines the JSON schemas used by skill-creator.

## Working with JSON Files

### Initialize a new file with correct structure

```bash
scripts/init_json.py <type> <output-path>

# Examples:
scripts/init_json.py evals evals/evals.json
scripts/init_json.py grading run-1/grading.json
scripts/init_json.py benchmark benchmarks/2026-01-15/benchmark.json
scripts/init_json.py metrics run-1/outputs/metrics.json
```

### Validate an existing file

```bash
scripts/validate_json.py <file-path> [--type <type>]

# Examples:
scripts/validate_json.py evals/evals.json
scripts/validate_json.py run-1/grading.json --type grading
```

The validator infers the type from the filename when possible.

---

## SKILL.md Frontmatter

Defines the frontmatter structure for skill files. Numeric limits and version
gates here mirror `references/frontmatter-reference.md` §1 (the canon) — update
both together.

Fields marked **[portable]** are the only six allowed outside Claude Code (claude.ai
uploads, the Skills API, `package_skill.py`, Cowork/cloud enablement). Anything else
is a hard `Unexpected key(s)` error there — see `frontmatter-reference.md` §1.1.
Frontmatter is read only when the opening `---` is the file's first line.

```yaml
---
# Recommended
description: string       # [portable] combined with when_to_use, truncated at 1,536 chars. Primary trigger mechanism. Angle brackets are escaped by Claude Code, not rejected — but avoid them.

# Optional - Identity
name: string              # [portable] display label; defaults to the directory name. In a personal/project skill the COMMAND comes from the directory name and a mismatch is harmless. In a plugin skill under skills/, name replaces the command's LAST SEGMENT and the plugin prefix stays (name: fancy -> /my-plugin:fancy; not doubled if it already carries the prefix, v2.1.246+); in a plugin-root SKILL.md it supplies the whole final segment. Kebab-case + 64-char cap come from the Agent Skills spec (agentskills.io), not skills.md — they bind on the portable path.
when_to_use: string       # additional trigger context; appended to description (counts toward the 1,536-char cap)

# Optional - Invocation Control
argument-hint: string     # autocomplete hint (e.g., "[file-path]")
arguments: string|list   # named positional arguments for $name substitution
disable-model-invocation: boolean  # default false; true = user-only. Also blocks preloading into a subagent's skills: field AND scheduled-task invocation (v2.1.196+).
user-invocable: boolean   # default true; false = Claude-only (hidden from / menu)

# Optional - Execution
allowed-tools: string|list  # [portable] pre-approve tools (no permission prompt) for the INVOKING TURN; the grant clears on the next user message. e.g. "Bash Read" or ["Bash", "Read"]. Supports patterns: "Bash(gh *)". Does NOT restrict the tool pool. Workspace trust does NOT gate this field.
disallowed-tools: string|list  # remove tools from the model while active, e.g. "AskUserQuestion". Clears on the next user message. (v2.1.152+)
model: string             # model override; accepts /model values or "inherit"; turn-scoped (not saved — session model resumes next prompt)
effort: enum              # low | medium | high | xhigh | max (available levels depend on the model)
context: enum             # fork (runs in subagent context)
agent: string             # subagent type when context: fork (Explore, Plan, general-purpose, or a custom agent)
background: boolean       # only with context: fork; default true (fork runs in background). false = wait for the result in the invoking turn. (v2.1.218+)
paths: string | list      # glob patterns limiting activation (e.g., "*.py, src/**")
shell: enum               # bash (default) | powershell
# boolean fields accept yes/no/on/off/1/0 in any case, besides true/false (v2.1.218+)

# Optional - Lifecycle
hooks: object             # registered on invocation, KEPT FOR THE REST OF THE SESSION (any of the 33 events). `once: true` removes a hook after its first SUCCESSFUL run.

# Optional - Metadata
license: string           # [portable] license covering the skill; Claude Code accepts but doesn't act on it
metadata: object          # [portable] free-form YAML MAP; a non-map value is dropped. Don't reuse frontmatter field names (e.g. `paths`) as keys.
compatibility: string     # [portable] environment requirements, max 500 chars (Agent Skills spec). Current field, NOT deprecated.
display-name: string      # Claude Code-only (v2.1.186+); not in the Agent Skills spec — not portable
default-enabled: boolean  # Claude Code-only (v2.1.186+); not in the Agent Skills spec — not portable
fallback: string          # Claude Code-only (v2.1.186+); not in the Agent Skills spec — not portable
# display-name/default-enabled/fallback/metadata.* accept kebab/snake/camelCase keys (v2.1.186+)
---
```

`description` is the one field to treat as required — `quick_validate` fails without it (a deliberate authoring guardrail; the docs call it merely recommended). Everything else (including `name`) is optional: a missing `name` only warns (the skill falls back to the directory name).

See `references/frontmatter-reference.md` for detailed field documentation, invocation control matrix, and examples.

---

## String Substitutions

Variables available in SKILL.md content, replaced at load time:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Specific argument by 0-based index |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing the skill's SKILL.md file (for plugin skills: the skill's subdirectory, not the plugin root) |
| `${CLAUDE_EFFORT}` | Current effort level: low/medium/high/xhigh/max (v2.1.120+). Ultracode is not a distinct level — it reports as `xhigh`. |
| `${CLAUDE_PROJECT_DIR}` | Project root directory — same path hooks receive as `CLAUDE_PROJECT_DIR`. Works in the skill body and in `allowed-tools` rules. (v2.1.196+) |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin install directory. Plugin skills only; substituted in the body and in `allowed-tools` rules |
| `${CLAUDE_PLUGIN_DATA}` | Plugin persistent data directory, survives plugin updates. Plugin skills only; same two substitution sites |
| `$name` | Named argument from `arguments` frontmatter list |

If **no placeholder receives an argument**, arguments are appended as `ARGUMENTS: <value>` at the end of the skill content. An indexed placeholder with no argument at its position stays literal and does *not* count as receiving one; a named placeholder always counts, because it expands to an empty string. Details: `references/frontmatter-reference.md` §3.

Dynamic context injection: `` !`command` `` runs shell commands before content is sent to Claude. Output replaces the placeholder inline. A non-zero exit **aborts the whole skill invocation** (exit 1 from search/compare commands excepted); injected commands never prompt for permission — an ask or deny rule aborts too. Details: `references/frontmatter-reference.md` §4.

---

## evals.json

Defines the evals for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable statements

---

## history.json

Tracks version progression in Improve mode. Located at workspace root.

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**Fields:**
- `started_at`: ISO timestamp of when improvement started
- `skill_name`: Name of the skill being improved
- `current_best`: Version identifier of the best performer
- `iterations[].version`: Version identifier (v0, v1, ...)
- `iterations[].parent`: Parent version this was derived from
- `iterations[].expectation_pass_rate`: Pass rate from grading
- `iterations[].grading_result`: "baseline", "won", "lost", or "tie"
- `iterations[].is_current_best`: Whether this is the current best version

---

## grading.json
<!-- SYNC: agents/grader.md inlines this schema — update both together -->

Output from the grader agent. Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Bash": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

> **Exact field names matter.** The eval viewer and `aggregate_benchmark.py` require `expectations[]` entries to use exactly `text`, `passed`, `evidence` — variants like `name`/`met`/`details` silently render as zeros in the viewer.

**Fields:**
- `expectations[]`: Graded expectations with evidence
- `summary`: Aggregate pass/fail counts
- `execution_metrics`: Tool usage and output size (from executor's metrics.json)
- `timing`: Wall clock timing (from timing.json)
- `claims`: Extracted and verified claims from the output
- `user_notes_summary`: Issues flagged by the executor
- `eval_feedback`: (optional) Improvement suggestions for the evals, only present when the grader identifies issues worth raising

---

## metrics.json
<!-- SYNC: agents/executor.md inlines this schema — update both together -->

Output from the executor agent. Located at `<run-dir>/outputs/metrics.json`.

```json
{
  "tool_calls": {
    "Read": 5,
    "Write": 2,
    "Bash": 8,
    "Edit": 1,
    "Glob": 2,
    "Grep": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

**Fields:**
- `tool_calls`: Count per tool type
- `total_tool_calls`: Sum of all tool calls
- `total_steps`: Number of major execution steps
- `files_created`: List of output files created
- `errors_encountered`: Number of errors during execution
- `output_chars`: Total character count of output files
- `transcript_chars`: Character count of transcript

---

## timing.json

Wall clock timing for a run. Located at `<run-dir>/timing.json`.

```json
{
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0,
  "total_duration_seconds": 191.0
}
```

**Capturing tokens from background subagents:** when an executor runs as a background subagent, the task-completion notification is the *only* place `total_tokens` and `duration_ms` are reported — they aren't persisted anywhere else. Write them into `timing.json` immediately as each notification arrives:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

`aggregate_benchmark.py` falls back to `timing.json` for time/tokens when `grading.json` lacks them.

---

## eval_metadata.json

Written by `prepare_eval.py` into each run directory; can also be authored manually for ad-hoc runs. Minimal manual form:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

`eval_name` is optional — a short descriptive slug of what the eval tests (shown in the viewer instead of a bare "eval-0"). `prepare_eval.py` additionally records staged paths (`input_files`, `skill_path`, `outputs_dir`, ...).

---

## benchmark.json

Output from Benchmark mode. Located at `benchmarks/<timestamp>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "<model-name>",
    "analyzer_model": "<most-capable-model-name>",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },

  "runs": [
    {
      "eval_id": 1,
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": [
        "Used 2023 data, may be stale",
        "Fell back to text overlay for non-fillable fields"
      ]
    }
  ],

  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },

  "notes": [
    "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
    "Eval 3 shows high variance (50% ± 40%) - may be flaky or model-dependent",
    "Without-skill runs consistently fail on table extraction expectations",
    "Skill adds 13s average execution time but improves pass rate by 50%"
  ]
}
```

**Fields:**
- `metadata`: Information about the benchmark run
- `runs[]`: Individual run results with expectations and notes
- `run_summary`: Statistical aggregates per configuration
- `notes`: Freeform observations from the analyzer

> **Exact field names matter.** If you generate `benchmark.json` by hand instead of via `aggregate_benchmark.py`, the viewer requires exactly `configuration` (not `config`) and nested `result.pass_rate` (not a top-level `pass_rate`) — mismatches show as empty/zero benchmark tabs. Configuration names other than `with_skill`/`without_skill` (e.g. `new_skill`/`old_skill`) are fine: the aggregator discovers them dynamically.

---

## comparison.json
<!-- SYNC: agents/comparator.md inlines this schema — update both together -->

Output from blind comparator. Located at `<grading-dir>/comparison-N.json`.

```json
{
  "winner": "A",
  "reasoning": "Output A provides a complete solution with proper formatting and all required fields. Output B is missing the date field and has formatting inconsistencies.",
  "rubric": {
    "A": {
      "content": {
        "correctness": 5,
        "completeness": 5,
        "accuracy": 4
      },
      "structure": {
        "organization": 4,
        "formatting": 5,
        "usability": 4
      },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {
        "correctness": 3,
        "completeness": 2,
        "accuracy": 3
      },
      "structure": {
        "organization": 3,
        "formatting": 2,
        "usability": 3
      },
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Complete solution", "Well-formatted", "All fields present"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable output", "Correct basic structure"],
      "weaknesses": ["Missing date field", "Formatting inconsistencies", "Partial data extraction"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    }
  }
}
```

---

## analysis.json
<!-- SYNC: agents/analyzer.md inlines this schema — update both together -->

Output from post-hoc analyzer. Located at `<grading-dir>/analysis.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary of why comparator chose winner"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for handling multi-page documents",
    "Included validation script that caught formatting errors"
  ],
  "loser_weaknesses": [
    "Vague instruction 'process the document appropriately' led to inconsistent behavior",
    "No script for validation, agent had to improvise"
  ],
  "instruction_following": {
    "winner": {
      "score": 9,
      "issues": ["Minor: skipped optional logging step"]
    },
    "loser": {
      "score": 6,
      "issues": [
        "Did not use the skill's formatting template",
        "Invented own approach instead of following step 3"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process the document appropriately' with explicit steps",
      "expected_impact": "Would eliminate ambiguity that caused inconsistent behavior"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5-step process -> Used validation script",
    "loser_execution_pattern": "Read skill -> Unclear on approach -> Tried 3 different methods"
  }
}
```
