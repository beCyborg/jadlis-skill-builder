# Choosing an Orchestration Architecture

> Last audited against Claude Code docs: 2026-08-05 (v2.1.222)

When a new skill involves more than a single pass of inline work — fan-out over many
items, background execution, scheduled runs, enforcement — the most consequential
design decision is which execution architecture the skill is built on. Make this
decision **during the interview, before drafting**, because it shapes the frontmatter,
the file layout, and what the skill body even says.

## The seven architectures

### 1. Plain inline skill

The default. SKILL.md loads into the main conversation; Claude follows it in the
current context. No frontmatter signature beyond `name`/`description`.

Right when: single-pass work, advice/formatting/reference tasks, anything where the
user should see the transcript as it happens.

### 2. Forked skill (`context: fork`)

```yaml
context: fork
agent: general-purpose   # or Explore, Plan, or a custom agent name
```

The whole skill runs in one isolated subagent; only the result returns to the main
conversation. One unit of work, no orchestration.

As of v2.1.218 the fork runs in the **background by default**: the user keeps
working and the result arrives when it completes. A backgrounded fork gets the
narrower background-subagent tool set, and its edits land outside session
checkpoints (`/rewind` can't undo them — git only). Set `background: false` when
the skill needs the full tool set or checkpointed edits. Details:
`references/frontmatter-reference.md` §5.

Right when: a single heavy, self-contained task whose intermediate output would
pollute the main context (a big scan, a long report). Not for fan-out — it is one
fork, not many.

**Disambiguation — three unrelated "forks":** `context: fork` (this architecture)
runs a *skill* in a subagent. The `/fork` command starts a separate background
*session* with its own worktree (v2.1.221+; it doesn't share the original
checkout) and its own subagent budget. The in-session conversation fork is
`/subtask` (named `/fork` before v2.1.212). Don't design a skill around one
expecting the semantics of another.

### 3. Direct subagents (hub-and-spoke)

The skill body instructs Claude to spawn subagents with the Agent tool — either
built-in types or custom definitions in `.claude/agents/*.md`. The main session is
the hub: it delegates, waits, and integrates. Custom agent files can pin `model:`
and `effort:` per worker and preload `skills:`.

Right when: roughly 2–8 parallel units, especially when the flow needs **user input
between stages** (interview → fan-out → review) — the main session stays interactive
between spawns. See `references/agent-authoring.md` for writing the agent files.

Since v2.1.198 subagents run **in the background by default**: the hub keeps working
while they run and receives each result via a `<task-notification>` when it finishes.
Design hub skills to process notifications as they arrive (and to persist anything
the notification carries that isn't stored elsewhere, e.g. token/duration metrics)
rather than assuming synchronous returns.

**Agent-tool limits** (these govern architecture 3; the Workflow tool in
architecture 4 has its own, different caps):
- **20 concurrent** subagents per session (v2.1.217+; ultracode sessions exempt) —
  `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`. Excess spawns fail with an error telling
  Claude not to retry; size fan-out waves accordingly.
- **200 per session** total (v2.1.212+) — `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`.
  Nested subagents, forks, and background subagents all count; agents a workflow
  script spawns with `agent()` do not.
- **Depth 3** of nesting below the main conversation (default since v2.1.219; in
  v2.1.217–218 the default was 1) — `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`.

All three variables accept a positive whole number; the limits can be raised but
not turned off. A skill that fans out near these numbers should batch its spawns
and degrade gracefully when a spawn is refused.

### 4. Thin skill + saved Workflow

The heavyweight fan-out pattern. The skill is a thin interactive shell; the
deterministic orchestration lives in a saved workflow script (`.claude/workflows/`
or `~/.claude/workflows/`, project wins on a name clash), conventionally named
`<skill>-core.js`:

- **Phase A (skill, main session):** interview the user, do recon, compute
  parameters — everything requiring judgment or input.
- **Phase B (workflow):** `Workflow({name: "<skill>-core", args: {...}})` runs the
  deterministic fan-out — up to 16 concurrent agents, 1,000 per run (Workflow-tool
  limits, separate from the Agent-tool limits in architecture 3), loops and
  conditionals in plain JavaScript, `agent(prompt, {schema})` for validated
  structured output. Workflows run in the background; the skill waits for the
  `<task-notification>` and reads the script's return value. Big intermediate
  results should be **file-mediated**: workers write to a work directory, the
  return value carries paths and status, not payloads.
- **Phase C (skill, main session):** synthesize, present, write outputs.

Right when: large or unbounded fan-out, work that must be repeatable and
deterministic in structure, budget-scaled loops. The hard constraint: **a workflow
accepts no mid-run user input** — only permission prompts can pause it. Anything
interactive must happen in Phase A or C.

Environment knobs to be aware of when authoring workflow-backed skills:
- **Size guideline** (v2.1.202+): `workflowSizeGuideline` is sent to Claude as
  *advice* on agent count — a prompt calling for a different scale still overrides
  it. Values map to targets: `small` <5, `medium` <15, `large` <50, `unrestricted`
  no guideline. Default is `medium` since v2.1.219 (earlier: `unrestricted`). Set
  it via `/config`, or as a settings-file key (v2.1.219+) — the settings key takes
  precedence and hides the `/config` row.
- **Large-workflow warning** (v2.1.203+): a run that schedules >25 agents or whose
  projected token total passes 1.5M gets a `Large workflow` warning in the task
  panel, pointing to `/workflows` where the user can stop it. The size guideline's
  agent count replaces the default threshold.
- **Kill switch**: `"disableWorkflows": true` in settings (or
  `CLAUDE_CODE_DISABLE_WORKFLOWS=1`) disables dynamic workflows entirely — a
  workflow-backed skill should degrade to architecture 3 or fail with a clear
  message, not assume the Workflow tool exists.
- **MCP tools**: workflow agents reach session-connected MCP tools via `ToolSearch`
  (deferred tool schemas load on demand) — but interactively-authenticated servers
  may be absent in headless/cron runs.

### 5. Agent teams (experimental)

Peer-to-peer parallelism: teammates share a task list, claim work, and message each
other directly instead of reporting to a hub. Requires
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Since v2.1.178 every session has one
implicit team — spawn teammates with the Agent tool's `name` parameter; there is no
setup step (the old `TeamCreate`/`TeamDelete` tools are gone). Practical size: 3–5
teammates. Note: a subagent definition's `skills:` and `mcpServers:` fields are
**not** applied when it runs as a teammate — teammates load skills and MCP servers
from project/user settings like a regular session, so a team-mode skill cannot rely
on per-agent preloading.

Right when: workers must debate, challenge each other, or self-coordinate — 
competing debugging hypotheses, cross-layer features, adversarial review. Highest
token cost of all options.

### 6. Hooks (cross-cutting enforcement)

Not an execution architecture but a layer over any of the others. A skill-scoped
`PreToolUse` command hook that exits with code 2 blocks the action and feeds its
message back — deterministic where prose is only a hint. Use for must-happen /
must-not-happen steps in any architecture. See `references/frontmatter-reference.md` §6.

### 7. Scheduled / cron skill

The skill is the prompt of a scheduled task and runs unattended. Signature:

```yaml
disallowed-tools: AskUserQuestion   # nobody is there to answer
```

**Footgun (v2.1.196):** do NOT set `disable-model-invocation: true` on a scheduled
skill — it now also blocks the scheduled task from running the skill. Constrain
triggering with a narrow `description` and `disallowed-tools` instead.

Design in an **anti-stub guard**: an unattended run that finds no fresh input must
exit without writing placeholder output, not fabricate a result. Composes with 3 or
4 for the actual work (cron fires → skill orchestrates).

## Decision matrix

Score the skill-to-be on each axis, then resolve top-down (first match wins —
signals higher in the list dominate):

| Axis | Question |
|---|---|
| Units of work | 1 / 2–8 / dozens-to-hundreds? |
| Determinism | Must the orchestration structure be repeatable run-to-run? |
| Mid-run input | Does the user need to answer questions after work starts? |
| Budget | Should depth scale with a token budget? |
| Hub vs peer | Do workers only report back, or must they talk to each other? |
| Autonomy | Does it run with nobody watching (cron, background)? |
| Isolation | Do workers mutate files in parallel (worktree needed)? |

Resolution order:

1. Runs unattended on a schedule → **7**, composed with **3** or **4** for the work.
2. Needs mid-run user input AND fan-out → **3** (or **5** if peers must talk); never 4.
3. Large deterministic fan-out (≳8 units, repeatable) → **4**.
4. Workers must communicate peer-to-peer → **5** if the env flag is on, else **3**.
5. Small fan-out (2–8, hub-and-spoke) → **3**.
6. One heavy isolated task → **2**.
7. Otherwise → **1**.
8. Any must-happen/must-not-happen step, in any of the above → add **6**.

### The mid-run-input teaching point

The single most common architecture mistake: a skill that needs to **interview its
users mid-run** cannot be a workflow (4) or a cron skill (7) — full stop. A workflow
accepts no mid-run input; a cron run has nobody to ask. If the task otherwise wants
a big deterministic fan-out, the resolution is the Phase A/B/C split of architecture
4: pull *all* interaction into Phase A before the workflow launches, and accept that
nothing can be asked until Phase C. If questions genuinely arise from intermediate
results, that is architecture 3 — the hub stays interactive between spawns.

## Subagents vs agent teams

Ported from the Claude Code docs comparison:

|  | Subagents (3) | Agent teams (5) |
|---|---|---|
| Context | Own window; results return to caller | Own window; fully independent |
| Communication | Report back to main agent only | Teammates message each other directly |
| Coordination | Main agent manages all work | Shared task list, self-coordination |
| Best for | Focused tasks where only the result matters | Work requiring discussion and collaboration |
| Token cost | Lower — results summarized back | Higher — each teammate is a full instance |

**Detecting the env gate at runtime** (portable — don't hardcode the machine):

```bash
[ "$CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" = "1" ] && echo "teams: on" || echo "teams: off"
```

Offer architecture 5 in an interview only when the matrix actually ranks it AND the
gate is on; when it's off, present it as "possible after enabling
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings" with 3 as the recommended
fallback.

## Pinning models per stage

Pin heavy stages through **custom agent definitions** (`model:`/`effort:` in
`.claude/agents/<worker>.md`, referenced via `agentType`/`agent`), not through the
skill's own `model:` field — the skill-level override is turn-scoped and hits every
stage including cheap ones. Mechanics: `references/agent-authoring.md`.

## Worked examples

- **"A skill that recommends books in my taste"** — single pass, no fan-out,
  conversational → **1**.
- **"Research a topic across web + 4 social platforms, verify claims, write a
  report"** — 5+ channel workers, per-claim verifiers, deterministic structure, but
  needs an upfront interview → **4** with the Phase A/B/C split; workers write to a
  work dir, the workflow returns `{workDir, status, reportPath}`.
- **"Every morning digest the news that affects my projects"** — unattended → **7**
  (no `disable-model-invocation`, `disallowed-tools: AskUserQuestion`, anti-stub
  guard) composed with **3** for parallel per-source analysts.
- **"Rename this API across ~200 files"** — large mechanical fan-out, workers mutate
  files in parallel → **4** with `isolation: 'worktree'` per worker; a verify stage
  gates the merge. (If a batch-runner skill is available in your setup, it may cover
  the small end of this; the general path is the workflow.)
