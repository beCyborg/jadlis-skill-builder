# Choosing an Orchestration Architecture

> Last audited against Claude Code docs: 2026-11-04 (v2.1.318, mirror 8f02c497)

When a new skill involves more than a single pass of inline work — fan-out over many
items, background execution, scheduled runs, enforcement — the most consequential
design decision is which execution architecture the skill is built on. Make this
decision **during the interview, before drafting**, because it shapes the frontmatter,
the file layout, and what the skill body even says.

## Which form? (decide this before the architecture)

Not every recurring need is a skill. Pick the form by what must happen, then — only
if the answer is "skill" (or a skill plus something) — pick an architecture below.

| The need | Form | Why / limits | Docs |
|---|---|---|---|
| A procedure you keep pasting into chat; Claude or the user triggers it | **Skill** (rule in a skill) | On demand; Claude may skip it — a description is a hint, not a guarantee | mods overview "Compare…" table (`plugins__mods__overview.md:205-215`); `features-overview.md:42` |
| Must apply on *every* turn: conventions, facts, "always do X" | **CLAUDE.md** / rules | Loaded every session, no trigger risk | `features-overview.md:40` |
| A voice, length or format for every reply, or Claude in a non-engineering role | **Output style** | Session-wide, not invoked | `features-overview.md:41` |
| Block, allow or log an event with a script; must-happen / must-not-happen steps | **Classic (settings) hook** — or `hooks:` in skill frontmatter | Deterministic; stable API; exit 2 blocks on gate events. A hook that crashes, can't start or times out lets the action through unless a `command`/`http` hook sets `"onFailure": "block"` (v2.1.295+) — use it on policy gates | `plugins__mods__overview.md:205-215`; `hooks.md:902-904`; architecture 6 below |
| A pane or band in the UI, a `/command` that runs code with no Claude turn, rewriting a tool call, prompt or request | **Mod** (plugin of in-process handlers) | See mod limits below | `plugins__mods__overview.md:15-23,205-215` |
| Claude needs to reach an external system (API, DB, browser) | **MCP server** | Gives Claude tools; a skill can then teach *how* to use them | `plugins__mods__overview.md:205-215`; `features-overview.md:47` |
| Keep working until a verifiable condition holds | **`/goal`** (this session) or a **Stop hook** (every session in scope; script or prompt check) | Both fire after every turn; `/goal` adds a fresh evaluator model | `goal.md:18-28` |
| Isolated heavy work that returns a summary | **Subagent** (architectures 2–3) | Own context; loses `AskUserQuestion` and `Workflow` | `features-overview.md:43`; `sub-agents.md:429-438` |
| Dozens–hundreds of agents, repeatable orchestration | **Workflow** (architecture 4) | The script holds the plan; no mid-run input | `workflows.md:17-28` |

A plugin can carry a skill, hooks, an MCP server and a mod together, so these
compose: an MCP server for access, a skill for the procedure, a hook for the hard
rule.

**Mod limits** — say them when you propose one:

- Requires Claude Code **v2.1.287+** (changelog 2.1.287, "Added Claude Mods").
- **Fails open.** A handler that throws, times out (10 s of its own running time per
  event) or returns the wrong shape is skipped and the event proceeds, unless the mod
  wrote a `.catch` handler (`plugins__mods__events.md:430-435`,
  `plugins__mods__reference.md:378`). A mod guard is a seatbelt, not a lock — for a
  hard rule prefer a classic `PreToolUse` hook with `exit 2`.
- **Not sandboxed.** A mod runs with the permissions of the user who installed it,
  with the user's access to files, processes and network (`plugins__mods__admin.md:9,88`).
  Never install a third-party mod unread.
- **Can't patch skills yet.** The `skill.prompt` event is not delivered as of
  v2.1.287 (anthropics/claude-code#96831, open) — rewriting a third-party skill's
  text through a mod doesn't work.
- Authoring: the bundled `plugin-authoring` skill (`/plugin-authoring`).

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
checkpoints (`/rewind` restores only files Claude had already edited in the
conversation; the fork's other edits stay — git only). Set `background: false` when
the skill needs the full tool set or checkpointed edits. Details:
`references/frontmatter-reference.md` §5.

Right when: a single heavy, self-contained task whose intermediate output would
pollute the main context (a big scan, a long report). Not for fan-out — it is one
fork, not many.

**What a fork can't do.** Every subagent — a `context: fork` skill included — loses
`AskUserQuestion` and `Workflow` (plus `EnterPlanMode`, `ScheduleWakeup`, and
`Agent` at the depth limit), even when listed in `tools`. So a forked skill can't
ask the user anything mid-run and can't launch a saved workflow (architecture 4)
from inside the fork. Interview first in the main session, or use architecture 3/4
instead.

**Disambiguation — four unrelated "forks":** `context: fork` (this architecture)
runs a *skill* in a subagent. The `/fork` command starts a separate background
*session* with its own worktree (v2.1.221+; it doesn't share the original
checkout) and its own subagent budget. The in-session conversation fork is
`/subtask` (named `/fork` before v2.1.212). And the Agent tool's
`subagent_type: "fork"` spawns a *subagent that inherits the full conversation
and prompt cache* — this "fork mode" is on by default in interactive terminal
sessions since v2.1.232 and everywhere else since v2.1.302 (`claude -p`, the Agent
SDK, the desktop app, VS Code); `CLAUDE_CODE_FORK_SUBAGENT=0` turns it off, a
`permissions.deny` entry `"Agent(fork)"` stops forks only, and `claude mcp serve`
never offers it (`sub-agents.md:1271-1278`; `env-vars.md:303`; changelog 2.1.302).
Since v2.1.307 forks launched together are each told which launch is their own, so
they are much less likely to start each other's work (`changelog.md:752`) — on
older versions give parallel forks explicitly disjoint briefs. Don't design a skill
around one expecting the semantics of another.

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
rather than assuming synchronous returns. Since v2.1.302 the desktop app and VS Code
always run the main conversation's subagents in the background, as the terminal
does — Claude no longer chooses there. A subagent's **own** Agent calls (nested
workers) in `claude -p`, the Agent SDK, the desktop app and VS Code run in the
**foreground** by default, so a worker that spawns helpers waits for them
(changelog 2.1.302).

**Agent-tool limits** (these govern architecture 3; the Workflow tool in
architecture 4 has its own, different caps):
- **20 concurrent** subagents per session (v2.1.217+; ultracode sessions exempt) —
  `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`. Excess spawns fail with an error telling
  Claude not to retry; size fan-out waves accordingly.
- **Depth 3** of nesting below the main conversation (default since v2.1.219; in
  v2.1.217–218 the default was 1) — `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`.
  Setting it to `1` leaves subagents spawnable from the main conversation but
  stops them spawning their own, which is as close to "nesting off" as it gets.
- **No per-session total.** The old 200-subagent-per-session spawn cap was
  **removed in v2.1.224**; `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` is now a
  no-op. A long-running session no longer refuses new agents once it has spawned
  many — don't design a skill (or a budget) around exhausting a session quota.

Both variables accept a positive whole number in plain digits; anything else is
ignored, so the limits can be raised or lowered but never removed (there is no
"unlimited" value). A skill that fans out
wide should still batch its spawns against the concurrency cap and degrade
gracefully when a spawn is refused.

### 4. Thin skill + saved Workflow

The heavyweight fan-out pattern. The skill is a thin interactive shell; the
deterministic orchestration lives in a saved workflow script (`.claude/workflows/`
or `~/.claude/workflows/`, project wins on a name clash), conventionally named
`<skill>-core.js`:

- **Phase A (skill, main session):** interview the user, do recon, compute
  parameters — everything requiring judgment or input.
- **Phase B (workflow):** `Workflow({name: "<skill>-core", args: {...}})` runs the
  deterministic fan-out — up to 16 concurrent agents by default (fewer when Claude
  Code has fewer CPUs, e.g. in a CPU-limited container; `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`
  1–256, v2.1.269+), 1,000 per run (Workflow-tool limits, separate from the
  Agent-tool limits in architecture 3), loops and
  conditionals in plain JavaScript, `agent(prompt, {schema})` for validated
  structured output. Workflows run in the background; the skill waits for the
  `<task-notification>` and reads the script's return value. Big intermediate
  results should be **file-mediated**: workers write to a work directory, the
  return value carries paths and status, not payloads.
- **Phase C (skill, main session):** synthesize, present, write outputs.

Right when: large or unbounded fan-out, work that must be repeatable and
deterministic in structure, budget-scaled loops. The hard constraint: **a workflow
accepts no mid-run user input** — only permission prompts can pause it. Anything
interactive must happen in Phase A or C. Unlike a subagent fan-out, an interrupted
run is **resumable in the same session** — the runtime tracks each agent's result.
On a relaunch Claude Code replays the run in start order: a completed agent returns
its saved result unless its prompt changed or an earlier agent's result did, and a
failed agent reruns together with every agent started after it, completed or not
(`workflows.md:366-380`). Two resume bugs are fixed: before v2.1.305 completed
`pipeline()` and `parallel()` agents could rerun on a relaunch of an unedited script
(`workflows.md:376`; `changelog.md:833`), and before v2.1.318 a run resumed after a
usage limit could rerun finished agents (`changelog.md:93`; docs not yet updated).
On older versions keep stage outputs on disk so a rerun can skip work.

**Ultracode changes the picture for inline skills.** With ultracode on (`/effort
ultracode`, the `ultracode` setting, `--effort ultracode`), Claude plans a workflow
for each substantive task on its own — an inline skill's work may get wrapped in a
workflow without the skill asking for one, and the `Large workflow` warning and the
Agent-tool concurrency cap are off for that session.

**Before writing or hand-editing the script, load the bundled `workflow-authoring`
skill** (`/workflow-authoring`, v2.1.248+). In v2.1.248 the Workflow tool's own
description was cut from ~5.7k to ~1k tokens and the script-writing reference —
script API, resume behaviour, quality patterns, worked examples — moved into that
skill. Claude normally loads it on its own before writing a script; run it yourself
before editing a saved `.js` by hand. Don't rely on the Workflow tool description
to still carry the API.

Environment knobs to be aware of when authoring workflow-backed skills:
- **Size guideline** (v2.1.202+): `workflowSizeGuideline` is sent to Claude as
  *advice* on agent count — a prompt calling for a different scale still overrides
  it. Values map to targets: `small` <5, `medium` <10, `large` <50, `unrestricted`
  no guideline. Default is `medium` since v2.1.219 (earlier: `unrestricted`), or
  `small` on a Pro plan from v2.1.271. Set
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
- **Prefix stagger** (v2.1.229+): a fan-out staggers same-prefix sibling agents so
  later ones read the cached prompt prefix instead of re-paying it.
  `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS=0` disables the stagger — leave it on
  unless a stage genuinely needs every sibling to start at once.

### 5. Agent teams (experimental)

Peer-to-peer parallelism: teammates share a task list, claim work, and message each
other directly instead of reporting to a hub. Requires
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Since v2.1.178 every session has one
implicit team — spawn teammates with the Agent tool's `name` parameter; there is no
setup step (the old `TeamCreate`/`TeamDelete` tools are gone). Practical size: 3–5
teammates. Note: a subagent definition's `skills:` field is **never** applied to a
teammate, and `mcpServers:` only to a split-pane teammate — an in-process teammate
loads MCP servers from project/user settings like a regular session. A team-mode
skill cannot rely on per-agent skill preloading.

**Trap for hub-and-spoke skills:** while agent teams are enabled, a subagent that
Claude *names* when it spawns it launches as a **teammate**, not a subagent — and
Claude can name subagents on its own. An architecture-3 skill run in a session with
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` may therefore get teammates (higher cost,
different `skills`/MCP rules) without asking for them. Setting the variable to `0`
turns it back; Claude Code rereads it at each spawn.

**Teammate models:** the `teammateDefaultModel` setting was **removed in v2.1.234**
and a leftover value is ignored. Each teammate's model is the first of: the model
the spawn prompt names for that teammate → the `model` field of the subagent
definition it was spawned from (`inherit` = the lead's model) →
`CLAUDE_CODE_SUBAGENT_MODEL` when set to anything but `inherit` → the lead's
current model. So a team-mode skill that wants a specific teammate model must name
it in the spawn prompt (or in the definition), not in settings.

Right when: workers must debate, challenge each other, or self-coordinate — 
competing debugging hypotheses, cross-layer features, adversarial review. Highest
token cost of all options.

### 6. Hooks (cross-cutting enforcement)

Not an execution architecture but a layer over any of the others. A skill-declared
`PreToolUse` command hook that exits with code 2 blocks the action and feeds its
message back — deterministic where prose is only a hint; add `"onFailure": "block"`
(v2.1.295+, `command`/`http` only) so a broken hook blocks instead of failing open
(`hooks.md:902-904`). Agent SDK hook callbacks take `onFailure: "block"` too since
v2.1.317, so a callback that fails blocks the action instead of letting it run
(`changelog.md:121`; docs not yet updated). Use for must-happen /
must-not-happen steps in any architecture. Three runtime limits to design around:
`updatedInput` a `PreToolUse`/`PermissionRequest` hook returns is validated like
Claude's own input — unknown keys are dropped, and input the tool rejects denies
the call (v2.1.300); `prompt`/`agent` hooks run with a concurrency cap — per the
docs 12 of one event at once, the rest waiting their turn (`hooks.md:398`), per
changelog 2.1.312 at most 24 at a time per session, subagents included, plus 12 that
waited past their timeout, with a `timeout` under 1 s counted as 1 s
(`changelog.md:439`; docs not yet updated); a hook that starts a background process
must print its decision first and redirect that process's stdout/stderr, or the
call is blocked with `refusing to honor the suspect capture` (`hooks.md:881-885`).
Caveat: a skill's hook is **not**
scoped to the invocation — it stays registered for the rest of the session. For a
one-shot gate set `once: true`; for a standing one keep the `matcher`/`if` as
narrow as the rule actually needs. See `references/frontmatter-reference.md` §6.

### 7. Scheduled / cron skill

The skill is the prompt of a scheduled task and runs unattended. Signature:

```yaml
disallowed-tools: AskUserQuestion   # nobody is there to answer
```

**Footgun (v2.1.196):** do NOT set `disable-model-invocation: true` on a scheduled
skill — it now also blocks a session-scoped scheduled task from running the skill
(`skills.md:402`). Constrain
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
2. Needs mid-run user input AND fan-out → **3** (or **5** if peers must talk); never 4, never 2 (a fork has no `AskUserQuestion`).
3. Large deterministic fan-out (≳8 units, repeatable) → **4**.
4. Workers must communicate peer-to-peer → **5** if the env flag is on, else **3**.
5. Small fan-out (2–8, hub-and-spoke) → **3**.
6. One heavy isolated task → **2** — unless it must ask the user mid-run or launch a workflow from inside (a fork can do neither) → keep it in the main session (**1**, or **4** started from the main session).
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
| Communication | Return a result to the caller; subagents Claude named at spawn can also message each other | Teammates message each other directly |
| Coordination | Main agent manages all work | Self-coordination through messages, plus a shared task list for agents that have the Task tools (see `references/task-tracking.md`) |
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
skill's own `model:` field — the skill-level override is turn-scoped, hits every
stage including cheap ones, and on an inline skill rebuilds the prompt cache.
Mechanics: `references/agent-authoring.md`. Which model and effort per stage, cache
cost, advisor, full IDs vs aliases: **read `references/model-routing.md`**.

**`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) overrides every pin:** Claude Code
then ignores the `model` field of every subagent definition (built-in Explore/Plan
included), Claude can't pass a model at spawn, and subagents, teammates and workflow
agents all run on `CLAUDE_CODE_SUBAGENT_MODEL` (or the main model if only FORCE is
set). A fork and a `context: fork` skill with `model: inherit` still run on the main
model. Check what a worker actually runs on with `/tasks`.

`CLAUDE_CODE_SUBAGENT_MODEL` sets only the **default** model for subagents,
teammates, and workflow agents that aren't assigned one another way (since
v2.1.251; before that it overrode everything). A definition's `model:` field
— `inherit` included — and a model Claude names at spawn time both take
precedence, so a pinned worker keeps its pin even in a session that exports the
variable. Setting it to `inherit` is the same as leaving it unset.

Note also that since v2.1.223 Claude Code **warns** when the subagent model
requested by a workflow agent, forked skill, slash command, or resumed background
agent is restricted and the parent model runs instead — treat that warning as a
signal that the pin didn't take, not as noise.

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
