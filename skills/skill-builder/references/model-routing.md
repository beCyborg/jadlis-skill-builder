# Model and Effort Routing

> Last audited against Claude Code docs: 2026-11-09 (v2.1.321, mirror 39e6937e)

Read this before writing `model:` or `effort:` anywhere — skill frontmatter, an
agent definition, a Workflow script. This file is the **general layer**: mechanics
that hold for any account. It carries no quota numbers and no per-role defaults for
a particular user; those live in an optional personal overlay (see the last line).

Doc references below are to pages of the Claude Code docs (`skills.md`,
`sub-agents.md`, `model-config.md`, `prompt-caching.md`, `workflows.md`,
`advisor.md`), with line numbers from the audited mirror; for `model-config.md`,
`advisor.md` and `prompt-caching.md`, from the live pages read 2026-11-09 (they
describe Fable 5.2 and run ahead of the mirror).

## 1. Where a model and an effort level come from

| Unit | Model | Effort | Notes |
|---|---|---|---|
| **Inline skill** (main conversation) | Frontmatter `model:` applies **for the rest of the current turn** and isn't saved; the session model resumes on the next prompt. Ignored if excluded by an org `availableModels` allowlist, or (in auto mode / plan mode with the classifier) if auto mode doesn't support it. (`skills.md:406`) | Frontmatter `effort:` applies **for the rest of the current turn** and overrides the session level (`skills.md:407`; `model-config.md:721`). It does **not** override `CLAUDE_CODE_EFFORT_LEVEL`; `maxEffortLevel` or an org cap still limits it (`model-config.md:721-723`). Without it the turn runs at the session level, resolved first-match: `CLAUDE_CODE_EFFORT_LEVEL` → a level picked in the session (`/effort`, the `/model` picker, `applyFlagSettings()`) → `--effort` → settings (the level saved per model in `modelSettings`, or `effortLevel`) → the model's default (`model-config.md:630-636`). | A skill can't turn on the advisor: there is no frontmatter field for it. |
| **Forked skill** (`context: fork`) | `model:` sets the **forked subagent's** model, not the session's; then the subagent rules below apply (`skills.md:406`; `prompt-caching.md:91`) | `effort:` sets the forked subagent's level for the fork's run (`skills.md:407`; `model-config.md:721`). A fork on a model other than the session's gets no session level without it (`skills.md:407` → `model-config.md:727`). `/tasks` shows the skill's level on the row when it sets one (`sub-agents.md:382`) | The fork loses `AskUserQuestion` and `Workflow` (`orchestration-guide.md`, architecture 2). |
| **Subagent** (Agent tool, custom definition) | First of: `model` parameter Claude passes on the Agent call → definition `model:` (`inherit` = main model) → `CLAUDE_CODE_SUBAGENT_MODEL` → main model (`sub-agents.md:357-360`). The Agent-call parameter takes **only the aliases** `sonnet`, `opus`, `haiku`, `fable` — never a full model ID or `inherit` (`sub-agents.md:355`; the docs name no version), so a worker that must run on an exact version needs it in its definition. A family alias such as `opus` resolves to the **main conversation's exact model** when the main model is in that family (`sub-agents.md:364-367`). | First of: `CLAUDE_CODE_EFFORT_LEVEL` → `effort` parameter Claude passes to the Agent tool for that launch (v2.1.292+, non-fork subagents; stays in effect when the subagent is resumed) → definition `effort:` (`sub-agents.md:312,417`; changelog 2.1.292). With none of these: on the main conversation's model the subagent runs at the session level; on a **different model** it runs at that model's saved level or that model's default, not the session's (v2.1.317, `changelog.md:295`; the docs say only that the session level doesn't apply there, `sub-agents.md:421`, `model-config.md:727`). `CLAUDE_CODE_SUBAGENT_EFFORT` (v2.1.316+) sets the level subagents run at when nothing else names one (`changelog.md:387`; docs not yet updated, so its rank against a different model's saved level is undocumented — check `/tasks`). | `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) ignores every definition's `model` and any spawn-time model (`sub-agents.md:390-411`). |
| **Workflow `agent()`** | Same order as subagents; a model the script names for a stage counts as the per-invocation model (`workflows.md:446`). `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` (v2.1.296+) runs every workflow agent on one model while other subagents keep theirs (changelog 2.1.296; not yet on the workflows page, so its rank against a model the script names is undocumented — check `/tasks`) | The `agentType` definition's `effort:` applies. Whether a per-call effort option exists in your runtime is not in the workflows page — check the bundled `/workflow-authoring` skill before relying on one. | Agents share prompt cache only with the same model, effort, agent type, tools, output schema and working directory (`workflows.md:340`) — keep one effort per fan-out wave. |
| **Agent-teams teammate** | Spawn prompt names it → definition `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → lead's model (`orchestration-guide.md`, architecture 5) | On the lead's model, inherits the lead's level (`agent-teams.md:161`); on another model, as for a subagent on a different model (v2.1.317, `changelog.md:295`; `model-config.md:727`). An in-process teammate applies its definition's `effort` (`agent-teams.md:279`). | — |

**Flagged requests in subagents.** A subagent Claude starts with the Agent tool never
pauses to ask at a flagged request. With "Switch models when a message is flagged" on
"Switch automatically" (or never chosen) the request re-runs on the fallback model and
the session model stays; on "Ask each time" (`switchModelsOnFlag: false`, v2.1.318+)
the subagent **fails** with `Agent terminated early due to an API error` plus the
refusal; with no fallback model it fails under either choice (`model-config.md:582,585-592`).
Since v2.1.319 Claude is then told to retry with a narrower prompt or tell the user,
not to do the work itself (`changelog.md:52`). A fan-out worker can therefore end on a
refusal; the hub should check each result for one instead of reading it as a finished run.

Rule of thumb that falls out of the table: **pin a stage's model in an agent
definition, not in the skill.** An inline skill's `model:` hits every step of that
turn, cheap ones included, and costs a cache rebuild (next section).

## 2. What busts the prompt cache

- **A model switch always does.** Each model has its own cache; switching recomputes
  the whole request (`prompt-caching.md:35`). A skill or command whose frontmatter
  `model:` differs from the session's current model makes that turn a model switch:
  the next request rereads the entire history with no cache hits
  (`prompt-caching.md:91`). A `context: fork` skill's `model:` switches only the
  forked subagent.
- **An effort change depends on the model.** On most models each effort level has its
  own cache. On **Fable 5.1 and later, Opus 5.5, Sonnet 5.5 and Haiku 5.5 with an API key
  or a Claude subscription**, changing effort keeps the cache — except on Amazon Bedrock, Google
  Cloud's Agent Platform, a Claude apps gateway, with
  `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`, or under a HIPAA configuration
  (`prompt-caching.md:36,95-97`). The docs state this for changing the level with
  `/effort`. **A skill's `effort:` frontmatter does NOT behave the same** — measured
  2026-10-02 (CC 2.1.287, Opus 5.5, subscription, `claude -p --resume`, one run per
  arm): on the skill turn a `effort: low` skill in a `high` session read 11.8K cached
  tokens and rewrote ~43K, while the same skill without `effort:` read 51.3K and wrote
  2.5K. So: no `effort:` on inline (main-thread) skills; put a different effort on a
  `context: fork` skill or an agent, which has its own cache anyway.
- **Skill loading itself doesn't.** Skills and plan mode append their instructions as
  conversation messages, so the cached prefix stays intact (`prompt-caching.md:31`).
- **Toggling the advisor doesn't** touch the main model's cache (`advisor.md:169-171`).

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
  (`advisor.md:88-103`). Examples: Opus 5.5 / Opus 5 accept Fable or Opus 5+ (Sonnet
  and Opus 4.6–4.8 rank below and are not attached); Sonnet 5.5 accepts Fable,
  Opus 5+ or Sonnet 5.5; Fable 5 accepts Fable 5.2, 5.1 or 5, Fable 5.1 accepts
  Fable 5.2 or 5.1, Fable 5.2 accepts only Fable 5.2 (Fable 5.2 needs v2.1.321+,
  `advisor.md:101-105`); Haiku 4.5 can call an
  advisor but never be one, while Haiku 5.5 can be one for Haiku 4.5, Haiku 5.5,
  Sonnet 4.6, Sonnet 5 and Opus 4.6 (v2.1.293+, `advisor.md:94-97,105`). A pair the API refuses is dropped
  silently — the conversation continues without an advisor, and a new pick takes
  effect only after `/clear` or `/compact` (`advisor.md:114`) — check `/advisor`
  output after changing it.
- **Typical pairings** (`advisor.md:125-134`): cheaper main + stronger advisor saves
  money; "Opus main + Opus advisor" buys an independent check where that matters more
  than cost.
- **Inheritance:** subagents inherit the configured advisor and apply the pairing
  check against their own model (`advisor.md:109`) — in a wide fan-out the advisor
  is multiplied by the number of workers.
- **Cost:** advisor tokens bill at the advisor model's rate (on a subscription they
  count toward plan limits; a Fable advisor bills to usage credits on plans where
  Fable does). The advisor's own read of the transcript is **not cached** — every call
  processes the whole transcript anew (`advisor.md:156-173`).
- **Turning it on:** `/advisor <model>`, the `advisorModel` setting, or `--advisor` for
  one session; off with `/advisor off` or `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`
  (`advisor.md:27-31,181-191`). Needs the Anthropic API and feature-flag fetching.
- **For skill authors:** you can't enable it from a skill. If a stage is a long
  autonomous run, recommend the user start that session with `--advisor`; warn that
  in fan-out workers it is inherited and multiplies cost.

## 4. Full model IDs vs aliases

- Aliases (`opus`, `sonnet`, `haiku`, `fable`, `best`) move: they resolve per
  provider and advance with Claude Code releases (`model-config.md:26-57`), and
  `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU,FABLE}_MODEL` can redirect each one to any
  model (`model-config.md:336`). On a machine that redirects `haiku` or `sonnet` to
  an Opus model, an alias-based comparison silently compares a model with itself.
- Since v2.1.321 `fable` resolves to Fable 5.2 (Fable 5 in Claude apps gateway
  sessions) and `best` to the same model as `opus` — before, `best` was the model
  `fable` resolved to (`model-config.md:33,51,1118-1119`). A `claude-fable-5-1`
  saved in **user** settings moves to `fable` (Pro/Max at the first v2.1.321 run,
  Team/Enterprise once the organization allows it) and then starts at Fable 5.2's
  default effort; project, local and managed settings keep `claude-fable-5-1`
  (`model-config.md:74-79`; changelog 2.1.321).
- To pin a version, use the full model ID, e.g. `claude-opus-5-5`
  (`model-config.md:59`). Write full IDs in: benchmark/eval configurations
  (`--model` of `run_loop.py`, `claude plugin eval --model`), agent definitions that
  must not drift with a release, and anything shipped to other people — their
  aliases may point elsewhere.
- Use an alias (or `inherit`) when "whatever the user's current family default is"
  is the intent. A family alias in a subagent definition already follows the main
  model's exact version when the families match (§1).
- A shipped skill or agent that names a full ID should say which Claude Code version
  and model access it needs; a recipient may not have that model, and an org
  `availableModels` allowlist substitutes another one (`sub-agents.md:375-378`).

## 5. Calibrating effort on your own tasks

- **Defaults in Claude Code:** without any setting, Fable 5.2, Opus 5.5, Sonnet 5.5
  and Haiku 5.5 start at `medium`, Opus 4.7 at `xhigh`, the other models with effort
  at `high` (`model-config.md:636`). **On the Claude API Fable 5.2 defaults to
  `high`** (Prompting Claude Fable 5.2 §Calibrate effort) — API-side guidance that
  says "start at `high`" starts one level above a Claude Code session. A skill or agent
  without `effort:` inherits whatever the session runs at — which differs per user.
- **What the levels trade:** a higher level tests more edge cases, verifies more and
  decides more on its own; a lower one returns a starting point sooner, which suits
  work you review step by step. `max` shows diminishing returns and can overthink
  (`model-config.md:690,693`).
- **Which level for which work** (Prompting Claude Fable 5.2 §Calibrate effort):
  `low` — fast subagents, well-specified and high-volume tasks; `medium` — interactive
  coding, chat, everyday knowledge work; `high` — hard coding, research, agentic work,
  long unattended runs (most of the capability gain is already there); `xhigh` — only
  where you measured a gain (slightly higher scores, many more tokens); `max` — ceiling
  measurements, or the rare task where time and tokens don't matter.
- **Behaviour at a level** (same section): the model stops early more often at `low`
  and `medium`, so an agentic worker there needs an explicit "finish the whole task"
  instruction. At `medium` and above a prompt line such as "answer directly without
  deliberating" doesn't stop Fable 5.2 thinking — lower the effort instead, and drop
  such lines from skills and agents. Effort barely changes reply length; set length
  in the prompt.
- **Moving models:** level names are calibrated per model — the same name is not the
  same budget across models (`model-config.md:695`), so re-run the sweep below after a
  model change instead of carrying a level over (Prompting Claude Fable 5.2 §Calibrate
  effort, for Fable 5.1 / Opus 5.5 → Fable 5.2). Going from Opus 5 to Opus 5.5, start
  at `medium` (`model-config.md:697`).
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
  Anthropic's own guides: "Calibrate effort" in the Opus 5.5 prompting guide (linked
  from `model-config.md:697`) and in Prompting Claude Fable 5.2.
- **Keep effort out of names.** Name agents by role (`researcher`), not by level
  (`researcher-xhigh`): the level changes more often than the role.

If `~/.claude/skills/_shared/model-routing.md` exists, read it in full — it overrides the examples here.
