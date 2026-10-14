# Model and Effort Routing

> Last audited against Claude Code docs: 2026-10-14 (v2.1.300, mirror 305bb5ef)

Read this before writing `model:` or `effort:` anywhere — skill frontmatter, an
agent definition, a Workflow script. This file is the **general layer**: mechanics
that hold for any account. It carries no quota numbers and no per-role defaults for
a particular user; those live in an optional personal overlay (see the last line).

Doc references below are to pages of the Claude Code docs (`skills.md`,
`sub-agents.md`, `model-config.md`, `prompt-caching.md`, `workflows.md`,
`advisor.md`), with line numbers from the audited mirror.

## 1. Where a model and an effort level come from

| Unit | Model | Effort | Notes |
|---|---|---|---|
| **Inline skill** (main conversation) | Frontmatter `model:` applies **for the rest of the current turn** and isn't saved; the session model resumes on the next prompt. Ignored if excluded by an org `availableModels` allowlist, or (in auto mode / plan mode with the classifier) if auto mode doesn't support it. (`skills.md:380`) | Frontmatter `effort:` overrides the session level while the skill is active; default = session level (`skills.md:381`). It does **not** override `CLAUDE_CODE_EFFORT_LEVEL`; `maxEffortLevel` or an org cap still limits it (`model-config.md:664`). | A skill can't turn on the advisor: there is no frontmatter field for it. |
| **Forked skill** (`context: fork`) | `model:` sets the **forked subagent's** model, not the session's; then the subagent rules below apply (`skills.md:380`; `prompt-caching.md:93`) | `effort:` as for a subagent; `/tasks` shows it on the row when the skill sets it (`sub-agents.md:385`) | The fork loses `AskUserQuestion` and `Workflow` (`orchestration-guide.md`, architecture 2). |
| **Subagent** (Agent tool, custom definition) | First of: model passed at spawn → definition `model:` (`inherit` = main model) → `CLAUDE_CODE_SUBAGENT_MODEL` → main model (`sub-agents.md:358-363`). A family alias such as `opus` resolves to the **main conversation's exact model** when the main model is in that family (`sub-agents.md:365-367`). | First of: `CLAUDE_CODE_EFFORT_LEVEL` → `effort` parameter Claude passes to the Agent tool for that launch (v2.1.292+, non-fork subagents; stays in effect when the subagent is resumed) → definition `effort:` → session level (`sub-agents.md:316,421`; changelog 2.1.292) | `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) ignores every definition's `model` and any spawn-time model (`sub-agents.md:391-416`). |
| **Workflow `agent()`** | Same order as subagents; a model the script names for a stage counts as the per-invocation model (`workflows.md:453`). `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` (v2.1.296+) runs every workflow agent on one model while other subagents keep theirs (changelog 2.1.296; not yet on the workflows page, so its rank against a model the script names is undocumented — check `/tasks`) | The `agentType` definition's `effort:` applies. Whether a per-call effort option exists in your runtime is not in the workflows page — check the bundled `/workflow-authoring` skill before relying on one. | Agents share prompt cache only with the same model, effort, agent type, tools, output schema and working directory (`workflows.md:350`) — keep one effort per fan-out wave. |
| **Agent-teams teammate** | Spawn prompt names it → definition `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → lead's model (`orchestration-guide.md`, architecture 5) | Inherits the lead's level (`agent-teams.md:161`) | — |

Rule of thumb that falls out of the table: **pin a stage's model in an agent
definition, not in the skill.** An inline skill's `model:` hits every step of that
turn, cheap ones included, and costs a cache rebuild (next section).

## 2. What busts the prompt cache

- **A model switch always does.** Each model has its own cache; switching recomputes
  the whole request (`prompt-caching.md:37`). A skill or command whose frontmatter
  `model:` differs from the session's current model makes that turn a model switch:
  the next request rereads the entire history with no cache hits
  (`prompt-caching.md:93`). A `context: fork` skill's `model:` switches only the
  forked subagent.
- **An effort change depends on the model.** On most models each effort level has its
  own cache. On **Opus 5.5, Sonnet 5.5 and Fable 5.1 with an API key or a Claude
  subscription**, changing effort keeps the cache — except on Amazon Bedrock, Google
  Cloud's Agent Platform, a Claude apps gateway, with
  `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`, or under a HIPAA configuration
  (`prompt-caching.md:38,97-99`). The docs state this for changing the level with
  `/effort`. **A skill's `effort:` frontmatter does NOT behave the same** — measured
  2026-10-02 (CC 2.1.287, Opus 5.5, subscription, `claude -p --resume`, one run per
  arm): on the skill turn a `effort: low` skill in a `high` session read 11.8K cached
  tokens and rewrote ~43K, while the same skill without `effort:` read 51.3K and wrote
  2.5K. So: no `effort:` on inline (main-thread) skills; put a different effort on a
  `context: fork` skill or an agent, which has its own cache anyway.
- **Skill loading itself doesn't.** Skills and plan mode append their instructions as
  conversation messages, so the cached prefix stays intact (`prompt-caching.md:33`).
- **Toggling the advisor doesn't** touch the main model's cache (`advisor.md:168`).

Consequence: on an inline skill, prefer `effort:` over `model:` when you only need
more or less depth; put a different model on a subagent or workflow stage.

## 3. The advisor tool

A server-side tool: Claude calls a second model at decision points; it reads the
full transcript and returns guidance (`advisor.md:15`).

- **When it pays:** long multi-step tasks where most turns are routine but plan
  quality decides the outcome — big refactors, a recurring error, a check before
  "done". Little value on short tasks or where every turn needs the strongest model;
  switch the main model instead (`advisor.md:19-23`).
- **Valid pairs** — the advisor must be at least as capable as the main model
  (`advisor.md:88-100`). Examples: Opus 5.5 / Opus 5 accept Fable or Opus 5+ (Sonnet
  and Opus 4.6 rejected, Opus 4.7/4.8 refused by the API); Sonnet 5.5 accepts Fable,
  Opus 5+ or Sonnet 5.5; Fable 5.1 accepts only Fable 5.1; Haiku can call an advisor
  but never be one. A pair the API refuses is dropped silently for the rest of the
  conversation (`advisor.md:111`) — check `/advisor` output after changing it.
- **Typical pairings** (`advisor.md:124-133`): cheaper main + stronger advisor saves
  money; "Opus main + Opus advisor" buys an independent check where that matters more
  than cost.
- **Inheritance:** subagents inherit the configured advisor and apply the pairing
  check against their own model (`advisor.md:106`) — in a wide fan-out the advisor
  is multiplied by the number of workers.
- **Cost:** advisor tokens bill at the advisor model's rate (on a subscription they
  count toward plan limits; a Fable advisor bills to usage credits on plans where
  Fable does). The advisor's own read of the transcript is **not cached** — every call
  processes the whole transcript anew (`advisor.md:155-170`).
- **Turning it on:** `/advisor <model>`, the `advisorModel` setting, or `--advisor` for
  one session; off with `/advisor off` or `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`
  (`advisor.md:27-31,180-188`). Needs the Anthropic API and feature-flag fetching.
- **For skill authors:** you can't enable it from a skill. If a stage is a long
  autonomous run, recommend the user start that session with `--advisor`; warn that
  in fan-out workers it is inherited and multiplies cost.

## 4. Full model IDs vs aliases

- Aliases (`opus`, `sonnet`, `haiku`, `fable`, `best`) move: they resolve per
  provider and advance with Claude Code releases (`model-config.md:26-59`), and
  `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU,FABLE}_MODEL` can redirect each one to any
  model (`model-config.md:326`). On a machine that redirects `haiku` or `sonnet` to
  an Opus model, an alias-based comparison silently compares a model with itself.
- To pin a version, use the full model ID, e.g. `claude-opus-5-5`
  (`model-config.md:61`). Write full IDs in: benchmark/eval configurations
  (`--model` of `run_loop.py`, `claude plugin eval --model`), agent definitions that
  must not drift with a release, and anything shipped to other people — their
  aliases may point elsewhere.
- Use an alias (or `inherit`) when "whatever the user's current family default is"
  is the intent. A family alias in a subagent definition already follows the main
  model's exact version when the families match (§1).
- A shipped skill or agent that names a full ID should say which Claude Code version
  and model access it needs; a recipient may not have that model, and an org
  `availableModels` allowlist substitutes another one (`sub-agents.md:378-383`).

## 5. Calibrating effort on your own tasks

- **Defaults:** without any setting, Opus 5.5 and Sonnet 5.5 start at `medium`; most
  other models at `high`; Opus 4.7 at `xhigh` (`model-config.md:583`). A skill or
  agent without `effort:` inherits whatever the session runs at — which differs per
  user.
- **What the levels trade:** a higher level tests more edge cases, verifies more and
  decides more on its own; a lower one returns a starting point sooner, which suits
  work you review step by step. `max` shows diminishing returns and can overthink
  (`model-config.md:635-642`). Level names are calibrated per model — the same name
  is not the same budget across models (`model-config.md:644`).
- **Moving models:** going from Opus 5 to Opus 5.5, start at `medium` rather than
  carrying over the old level (`model-config.md:646`).
- **Procedure:**
  1. Pick 3–5 representative tasks per role (a fan-out worker, a verifier, the final
     synthesis) with a checkable outcome.
  2. Run each at two adjacent levels with the model pinned by full ID — the eval
     loops in this skill do it (`references/benchmark-mode.md`; `claude plugin eval
     --model <id> --runs 3` for plugin skills).
  3. Compare pass rate, tokens and wall time; keep the lower level unless the higher
     one fixes failures that matter.
  4. Write the chosen level into the agent definition (or the skill's `effort:`), with
     the date and the evidence, and re-check when a new model ships.
  Anthropic's own guide: "Calibrate effort" in the Opus 5.5 prompting guide, linked
  from `model-config.md:646`.
- **Keep effort out of names.** Name agents by role (`researcher`), not by level
  (`researcher-xhigh`): the level changes more often than the role.

If `~/.claude/skills/_shared/model-routing.md` exists, read it in full — it overrides the examples here.
