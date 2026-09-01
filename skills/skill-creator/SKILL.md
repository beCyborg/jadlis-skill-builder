---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Runs a guided interview to scope new skills and helps choose an orchestration architecture (inline, forked subagent, dynamic workflow, or agent team). Use when users want to create a skill from scratch, update or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Evaluate the results
  - which can be through automated evals, but also it's totally fine and good for them to be evaluated by the human by hand and that's often the only way
- Rewrite the skill based on feedback from the evaluation
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Cool? Cool.

## Building Blocks

See references/building-blocks.md for details on Eval Run, Grade Expectations, Blind Compare, and Post-hoc Analysis building blocks.

---

## Environment Capabilities

Check whether you can spawn subagents — independent agents that execute tasks
in parallel. If you can, you'll delegate work to executor, grader, comparator,
and analyzer agents. If not, you'll do all work inline, sequentially.

This affects which modes are available and how they execute. The core
workflows are the same — only the execution strategy changes. Environment-specific
mechanics (Claude.ai inline runs, Cowork static viewer/feedback) are in
`references/environments.md` — read it when running outside Claude Code.

---

## Mode Workflows

Building blocks combine into higher-level workflows for each mode:

| Mode | Purpose | Workflow |
|------|---------|----------|
| **Eval** | Test skill performance | Executor → Grader → Results |
| **Improve** | Iteratively optimize skill | Executor → Grader → Comparator → Analyzer → Apply |
| **Create** | Interactive skill development | Triage → Interview → Research → (Orchestration fork) → Draft → Run → Refine |
| **Benchmark** | Standardized performance measurement (requires subagents) | 3x runs per configuration → Aggregate → Analyze |

See `references/mode-diagrams.md` for detailed visual workflow diagrams.

---

## Task Tracking

Use tasks to track progress when the task tools are available (they are off by default on Opus 4.8 / Sonnet 5 / Fable 5 / Mythos 5 and newer — see the availability section in references/task-tracking.md). See references/task-tracking.md for lifecycle, creation, and stage progression details.

---

## Architecture

The **coordinator** (this skill):

1. Asks the user what they want to do and which skill to work on
2. Determines workspace location (ask if not obvious)
3. Creates workspace and tasks for tracking progress
4. Delegates work to subagents when available, otherwise executes inline
5. Tracks the **best version** (not necessarily the latest)
6. Reports results with evidence and metrics

### Agent Types

| Agent | Role | Reference |
|-------|------|-----------|
| **Executor** | Run skill on a task, produce transcript + outputs + metrics | `agents/executor.md` |
| **Grader** | Evaluate expectations against transcript and outputs | `agents/grader.md` |
| **Comparator** | Blind A/B comparison between two outputs | `agents/comparator.md` |
| **Analyzer** | Post-hoc analysis of comparison results | `agents/analyzer.md` |

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. If you haven't heard (and how could you, it's only very recently that it started), there's a trend now where the power of Claude is inspiring plumbers to open up their terminals, parents and grandparents to google "how to install npm". On the other hand, the bulk of users are probably fairly computer-literate.

So please pay attention to context cues to understand how to phrase your communication! In the default case, just to give you some idea:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

It's OK to briefly explain terms if you're in doubt, and feel free to clarify terms with a short definition if you're unsure if the user will get it.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact.

**Triage first — is this actually a skill?** A skill is on-demand, gated by a decision point Claude can skip, so it fits *discrete, invocable workflows* ("do X, then Y, then verify" — the "would I write a function for it?" test). It is a poor fit for *always-on passive knowledge* (framework/API surface, ever-present conventions, code-style rules) — that belongs in CLAUDE.md/AGENTS.md, which loads every turn with no trigger risk. Practitioner evals repeatedly find description-only skills failing to fire on a large fraction of relevant prompts. So: if the user needs something to apply *every time*, steer it to CLAUDE.md or a hook; reserve the skill format for workflows they (or Claude) explicitly trigger. The two can coexist — a rule can live in CLAUDE.md *and* a review skill can reference it.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview, Research & House Style

The interview is adaptive: a silent triage gate routes simple skills (advise/format/summarize, one pass) to a single AskUserQuestion screen, and complex ones (fan-out, MCP/API, cron, multi-file mutation, mid-run interaction) to a staged flow — intent, research, architecture, guardrails, evals. Follow `references/creation-interview.md`; it also defines the "just vibe" degradation for users who don't want process.

Research runs on two tiers (`references/research-protocol.md`): always verify frontmatter fields and orchestration features against the local Claude Code docs mirror before drafting; offer web/library research (library-docs MCP, web search) as an interview option — never launch it unasked.

If `references/house-style.md` exists, read it in full at the start of every Create run — it carries machine-local conventions (trigger format, allowed-tools form, heavy-skill patterns) that override the generic defaults in this file.

### Initialize

Run the initialization script:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

This creates:
- SKILL.md template with frontmatter
- scripts/, references/, assets/ directories
- Example files to customize or delete

### Fill SKILL.md Frontmatter

Based on interview, fill in the required fields and relevant optional fields:

- **name**: Display label (kebab-case, max 64 chars). The command you type comes from the **directory name**, not this field — so keep `name` == directory basename. (Exceptions: in a plugin skill, `name` replaces the command's *last segment*, the plugin prefix stays, v2.1.216+; in a plugin-root `SKILL.md`, `name` supplies the final segment.) Every skill is also a slash command (`/<name>`, or `/<plugin>:<name>`) and appears in the `/` menu unless `user-invocable: false`. Check `/skills` for collisions and avoid reserved and built-in command names — the canonical list lives in `references/description-optimization.md` §"Naming the skill".
- **description**: What the skill does — this is the primary triggering mechanism. Front-load key use cases: the combined `description` + `when_to_use` text is truncated at **1,536 characters** in the skill listing. Include both what the skill does AND specific contexts for when to use it. Claude tends to "undertrigger" skills — make descriptions a little "pushy" (e.g., "Build dashboards for internal data. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'")
- **when_to_use** *(optional)*: Additional trigger context — phrases, example requests. Appended to `description` in the skill listing and counts toward the 1,536-char cap. Use `description` for WHAT it does and `when_to_use` for WHEN to invoke it.

**Optional fields**: invocation control (`when_to_use`, `arguments`, `argument-hint`, `disable-model-invocation`, `user-invocable`), execution (`allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`/`agent`/`background`, `paths`, `shell`), session hooks (`hooks` — registered on invocation and kept for the rest of the session, not dropped when the skill finishes), portability metadata (`license`, `metadata`, `compatibility`). Full field table, semantics, and version notes: `references/frontmatter-reference.md` §1; quick schema: `references/schemas.md`.

**Portability check**: only six fields — `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` — survive outside Claude Code (claude.ai uploads, the Skills API, `.skill` packaging, enabling a personal skill for Cowork/cloud sessions). Anything else fails those paths with a hard `Unexpected key(s)` error. If the skill must travel, restrict the frontmatter to those six; `scripts/quick_validate.py` warns and `scripts/package_skill.py` refuses. Details: `references/frontmatter-reference.md` §1.1.

**Invocation control**: By default, both user and Claude can invoke a skill. Set `disable-model-invocation: true` for user-only skills (e.g., dangerous operations; also blocks preload into subagents and scheduled-task runs). Set `user-invocable: false` for Claude-only background knowledge skills that shouldn't appear in the `/` menu. Matrix and takeaways: `references/frontmatter-reference.md` §2.

Skills are discovered from `.claude/skills/` in the starting directory and every parent directory up to the repo root. Directories added via `--add-dir` also have their `.claude/skills/` loaded automatically. Useful for monorepo setups.

### skillOverrides (settings-based visibility)

Control skill visibility from `settings.json` without editing SKILL.md — values `"on"`/`"name-only"`/`"user-invocable-only"`/`"off"`; the `/skills` menu writes it for you. Caveats (managed-settings-only propagation, Remote Control/SDK hiding, plugin skills excluded) and permission rules (`Skill(name)` / `Skill(name *)`): `references/frontmatter-reference.md` §8.

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Writing the body

Read `references/skill-writing-craft.md` when drafting or rewriting SKILL.md content. It carries: what NOT to include (no README/CHANGELOG — skills are for agents), progressive disclosure (three-level loading, the <500-line rule, domain organization by variant), the Principle of Lack of Surprise (no malware/misleading skills), and body-writing craft — imperative form, output-format and example patterns, affirmative directives, placing rules where they fire, trimming what the model already knows, and reaching for a hook instead of prose for must-happen steps.

### Immediate Feedback Loop

**Always have something cooking.** Every time user adds an example or input:

1. **Immediately start running it** - don't wait for full specification
2. **Show outputs in workspace** - tell user: "The output is at X, take a look"
3. **First runs in main agent loop** - not subagent, so user sees the transcript
4. **Seeing what Claude does** helps user understand and refine requirements

Claude Code watches skill directories — file edits are detected without restarting. However, already-loaded skill content in the current conversation is NOT updated — re-invoke the skill to pick up changes. The iteration loop is: edit SKILL.md → re-invoke (or run `/reload-skills`, v2.1.152+, to re-scan all skill directories without restarting) → re-test. Only a *brand-new top-level* skills directory that didn't exist at session start needs `/reload-skills` or a restart to be picked up.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: [you don't have to use this exact language] "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

If the user wants evals, create `evals/evals.json` with this structure:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": [],
      "expectations": [
        "The output includes X",
        "The skill correctly handles Y"
      ]
    }
  ]
}
```

You can initialize with `scripts/init_json.py evals evals/evals.json` and validate with `scripts/validate_json.py evals/evals.json`. See `references/schemas.md` for the full schema.

### Transition to Automated Iteration

Once gradable criteria are defined (expectations, success metrics), Claude can:

- More aggressively suggest improvements
- Run tests automatically (via subagents in the background if available, otherwise sequentially)
- Present results: "I tried X, it improved pass rate by Y%"

**Baseline gate.** A skill earns its place only if it beats the no-skill baseline. Many shared skills make output *worse* or never fire. So when evals exist, run the same prompts **with and without** the skill and require a demonstrable improvement before calling it done — a skill that matches vanilla is pure context cost. Keep the grader/judge independent from whatever produced the output (don't let the same context grade itself), and treat small score deltas as noise rather than signal.

### Choosing an Orchestration Architecture

When the skill being created involves more than single-pass inline work — fan-out over many items, background or scheduled runs, parallel file mutation — pick the execution architecture during the interview, before drafting. Seven options: plain inline, forked subagent (`context: fork` — runs in the **background by default** since v2.1.218, with a narrower tool set and no `/rewind` coverage; `background: false` restores foreground semantics), direct subagents (hub-and-spoke), thin skill + saved workflow, agent teams (experimental, env-gated), hooks as a cross-cutting enforcement layer, and scheduled/cron. The constraint that eliminates options fastest: workflows and cron runs accept **no mid-run user input** — anything interactive must happen before the fan-out launches or after it returns.

See `references/orchestration-guide.md` for frontmatter signatures, the decision matrix, resolution order, and worked examples.

### Package and Present

After creating or improving a skill, package it:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

Direct the user to the resulting `.skill` file path so they can install it. This is the quick, single-recipient path. For skills that need to be **shared, versioned, or published**, wrap them in a plugin + marketplace instead — see `references/plugin-packaging.md` (layout, `plugin.json`/`marketplace.json`, version-bump rules, `claude plugin validate --strict`).

---

## Advanced Skill Features

These features extend what skills can do. See `references/frontmatter-reference.md` for full documentation and examples.

### String Substitutions

Variables replaced at load time: `$ARGUMENTS` / `$N` / `$name` (arguments), `${CLAUDE_SKILL_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_PROJECT_DIR}`. Full table, examples, and edge cases (auto-append when `$ARGUMENTS` is absent, unmatched `$N` preserved verbatim): `references/frontmatter-reference.md` §3.

### Dynamic Context Injection

Skills can embed shell command output directly into their content at load time. Commands execute before content reaches Claude — Claude only sees the substituted output. Useful for injecting git diffs, file listings, API responses, etc. See `references/frontmatter-reference.md` section 4 for syntax and examples.

**Note:** If `disableSkillShellExecution: true` is set in settings, `` !`command` `` placeholders in user/project/plugin/additional-directory skills are replaced with `[shell command execution disabled by policy]`. Bundled and managed skills are exempt. Warn users if their skill relies on dynamic context.

### Extended Thinking (ultrathink)

Include the word "ultrathink" anywhere in skill content to enable extended thinking mode. See `references/frontmatter-reference.md` for details.

### Skills as Subagents

To create or manage custom agents, ask Claude or edit `.claude/agents/*.md` directly (the `/agents` wizard was removed in v2.1.198).

Set `context: fork` and `agent` to run the skill in an independent subagent:

```yaml
---
name: security-scan
context: fork
agent: general-purpose
---
```

### Preloading Skills into Subagents

Custom agents can preload skills via the `skills` field in their frontmatter:

```yaml
---
name: api-developer
skills:
  - api-conventions
  - error-handling
---
```

### Skill Content Lifecycle

When invoked, skill content stays in the conversation for the session. On compaction, each skill retains its first 5,000 tokens (25,000 combined budget, MRU-first). Re-invoke after compaction to restore full content. See `references/skill-lifecycle.md` for details.

### Context Budget

The skill listing is budgeted at a fraction of the model's context window (default 1%); combined `description` + `when_to_use` is truncated at 1,536 characters per skill — front-load key use cases. Keep SKILL.md under 500 lines. Budget overrides (`skillListingBudgetFraction`, `skillListingMaxDescChars`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`) and diagnostics (`/context`, `/doctor`): `references/frontmatter-reference.md` §7.

### Validation

Run `claude plugin validate` as the primary validator for frontmatter and plugin structure — it is the canon. `python -m scripts.quick_validate` is a lightweight authoring guardrail: it *fails* only on hard errors (missing `description`, malformed YAML, over-limit lengths) and *warns* on everything else, including unknown keys — a warning is a prompt to double-check the docs, not a blocker.

---

## Improving a skill

Iteratively optimize an existing skill using the building blocks (run, grade, compare, analyze).

**IMPORTANT**: Before running improvement iterations, read the full documentation:
```
Read references/improve-mode.md   # Complete Improve workflow
Read references/schemas.md        # JSON output structures
```

Key questions to ask: Which skill? How much time? What's the goal?

Without subagents, use single runs per iteration and inline grading. See `references/improve-mode.md` for details.

---

## Eval Mode

Run individual evals to test skill performance and grade expectations.

**IMPORTANT**: Before running evals, read the full documentation:
```
Read references/eval-mode.md      # Complete Eval workflow
Read references/schemas.md        # JSON output structures
```

Use Eval mode when:
- Testing a specific eval case
- Comparing with/without skill on a single task
- Quick validation during development

The workflow: Setup → Check Dependencies → Prepare → Execute → Grade → Display Results

Without subagents, execute and grade sequentially in the main loop. Read the agent reference files (`agents/executor.md`, `agents/grader.md`) and follow the procedures directly.

---

## Benchmark Mode

Run standardized performance measurement with variance analysis.

**Requires subagents.** Benchmark mode relies on parallel execution of many runs to produce statistically meaningful results. Without subagents, use Eval mode for individual eval testing instead.

**IMPORTANT**: Before running benchmarks, read the full documentation:
```
Read references/benchmark-mode.md # Complete Benchmark workflow
Read references/schemas.md        # JSON output structures
```

Use Benchmark mode when:
- "How does my skill perform?" - Understanding overall performance
- "Compare Sonnet vs Haiku" - Cross-model comparison
- "Has performance regressed?" - Tracking changes over time
- "Does the skill add value?" - Validating skill impact

Key differences from Eval:
- Runs **all evals** (not just one)
- Runs each **3 times per configuration** for variance
- Always includes **no-skill baseline**
- Uses **most capable model** for analysis

---

## Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

See `references/description-optimization.md` for the full 4-step optimization workflow (generate queries, review with user, run optimization loop, apply result).

---

## Workspace Structure

Workspaces are created as sibling directories to the skill being worked on (e.g., `skill-name-workspace/`).

See `references/workspace-structure.md` for detailed directory layouts for each mode (Eval, Improve, Benchmark).

---

## Coordinator Responsibilities

See references/coordinator.md for the full coordinator responsibility list.

---

## Delegating Work

See references/delegating-work.md for delegation patterns with and without subagents.

---

## Reference files

The agents/ directory contains instructions for specialized subagents:
- `agents/executor.md` — How to execute an eval run and produce transcript + outputs
- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs
- `agents/analyzer.md` — How to analyze why one version beat another

The eval-viewer/ directory contains the browsable review UI:
- `eval-viewer/generate_review.py` — generate/serve the review page (Outputs + Benchmark tabs, per-eval feedback); `--static` for headless environments

The references/ directory has additional documentation:
- `references/schemas.md` — JSON structures for evals.json, grading.json, benchmark.json, etc. + frontmatter schema
- `references/frontmatter-reference.md` — Complete frontmatter field documentation, invocation control, string substitutions, hooks
- `references/orchestration-guide.md` — Seven execution architectures, decision matrix, subagents vs agent teams, worked examples
- `references/creation-interview.md` — Adaptive Create interview: triage gate, simple/staged paths, orchestration fork, "just vibe" degradation
- `references/research-protocol.md` — Two-tier research: local docs mirror always, web/library research on request
- `references/house-style.md` — Machine-local conventions; read in full at the start of every Create run when present
- `references/skill-writing-craft.md` — What not to include, progressive disclosure, lack-of-surprise principle, body-writing patterns and style craft
- `references/sandboxing.md` — Sandbox settings that affect skills running bash (network allowlist, credential masking, filesystem isolation)
- `references/AUDIT.md` — Audit registry: per-file audit dates, SYNC registry of facts duplicated across files, release checklist
- `references/integration-testing.md` — TESTS.md capability matrix + gate for skills with live external dependencies
- `references/plugin-packaging.md` — Distributing a skill as a plugin: layout, plugin.json/marketplace.json, version semantics, validation
- `references/skill-lifecycle.md` — Skill content lifecycle, compaction behavior, re-invocation
- `references/agent-authoring.md` — When skills create companion agents, skill vs agent frontmatter
- `references/building-blocks.md` — Eval Run, Grade Expectations, Blind Compare, Post-hoc Analysis
- `references/task-tracking.md` — Task lifecycle, creation, stage progression
- `references/coordinator.md` — Coordinator responsibility checklist
- `references/delegating-work.md` — Delegation patterns with/without subagents
- `references/improve-mode.md` — Complete Improve workflow (setup, iteration loop, final report)
- `references/description-optimization.md` — Description optimization 4-step workflow
- `references/eval-mode.md` — Complete Eval workflow
- `references/benchmark-mode.md` — Complete Benchmark workflow
- `references/environments.md` — Claude.ai / Cowork adaptations (inline runs, static viewer, feedback.json)
- `references/mode-diagrams.md` — Visual workflow diagrams
- `references/workspace-structure.md` — Directory layouts for each mode

---

# Conclusion

The loop, one more time: scope it (triage → interview → architecture) → draft → run realistic test prompts → evaluate (by hand or with evals) → rewrite → repeat, expanding the test set as the skill stabilizes. Good luck!
