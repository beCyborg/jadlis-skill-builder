# Creation Interview

Procedure for scoping a new skill before drafting. Uses `AskUserQuestion` for every
fork: up to 4 questions per screen, up to 4 options per question, put the
recommended option first with "(Recommended)" appended, synthesize the options from
the user's actual request — never present generic boilerplate choices. Conduct the
interview in the language the user is speaking; option labels stay short.

The interview is adaptive: a triage gate routes simple requests to a single screen
and complex ones to a staged flow. Do not run the staged flow for a formatting
skill, and do not squeeze an orchestrated pipeline into one screen.

## Triage gate

Classify silently from the request and conversation history — do not ask the user
to self-classify. One COMPLEX signal is enough (OR-gate).

**SIMPLE signals:** the skill advises, formats, summarizes, or serves reference
knowledge; one pass in the main context; no external systems; output is text the
user reads.

**COMPLEX signals:**
- "for each …", "in parallel", "across all …" — fan-out over many items
- "every day / every week / when X happens" — scheduled or autonomous runs
- talks to MCP servers, external APIs, CLIs, or live services
- mutates many files or runs multi-stage pipelines
- the skill itself must ask its users questions mid-run
- long-running background work, or output another program consumes

Borderline (e.g. "summarize my open PRs" — is it one pass or a fan-out?): ask one
tie-breaker question about scale, then route.

If the current conversation already contains the workflow being captured ("turn
this into a skill"), extract answers from history first and only ask about the
gaps — in both paths.

## Simple path

One `AskUserQuestion` screen, up to 4 questions. Skip any question the request
already answers.

1. **Trigger** — when should this fire? Options built from the request: the obvious
   trigger phrasing (Recommended), a broader variant, a narrower variant.
2. **Invoke** — who calls it? "Both user and Claude (Recommended)" / "User only
   via /name" (→ `disable-model-invocation: true`) / "Claude only, hidden from
   menu" (→ `user-invocable: false`).
3. **Output** — what does done look like? Options from the request: format,
   destination, length.
4. **Tests** — set up eval cases? Recommend "Yes" when the output is objectively
   checkable (transforms, extraction, fixed steps), "No, iterate by hand" when it
   is subjective (style, taste). Let the user decide.

Then go straight to Initialize → Draft → Run.

## Staged path

Up to 5 screens; conditional screens collapse when their answers are already known,
so a typical run is 3–4 screens. Announce the plan in one line ("A few short rounds
of questions — intent first, then architecture and guardrails") so the user knows
what's coming.

### Stage 0 — silent recon (no questions)

Before the first screen: grep the local Claude Code docs mirror for any feature the
request touches (see `references/research-protocol.md`); detect whether agent teams
are enabled (`$CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` = "1"); check `/skills` for
name collisions; note which MCP servers the skill would need. Recon feeds the
options you present — it is not a report to the user.

### Stage 1 — Intent

The first question is always the outcome question:

1. **Outcome** — "What will you (or the skill's user) be able to do or decide once
   this skill has run?" Options are concrete hypotheses synthesized from the
   request. This anchors every later trade-off.
2. **Trigger** — as in the simple path.
3. **Scale** — how many units of work per run? "One" / "A handful (2–8)" /
   "Dozens or more" / "Unbounded, depends on input".
4. **Timing** — the key architecture question: "Once running, will the skill need
   to ask you anything mid-run, or does it get everything up front?" "Everything up
   front (Recommended for automation)" / "May need to ask mid-run" / "It runs
   unattended (cron) — nobody can answer".

### Stage 2 — Research (conditional)

Skip when Stage 0 recon left no open questions. Otherwise ask how deep to research
before drafting:

- "Local docs mirror only (Recommended — instant, free)"
- "Also library/web research (Context7, web search) — for external APIs or fast-moving
  tools"
- "Skip research, I know the domain"

Run the chosen research **before** fixing the architecture: do not present Stage 3
options while an uncertainty flag (unknown API shape, unverified feature, ambiguous
scale) is still open. Protocol details: `references/research-protocol.md`.

### Stage 3 — Architecture

Score the answers against the decision matrix in
`references/orchestration-guide.md` and present the top 2–4 architectures as one
question. Each option's description states its main trade-off in one sentence; the
matrix winner goes first with "(Recommended)". Example shape:

- "Thin skill + workflow core (Recommended) — deterministic fan-out over N items;
  no questions possible mid-run"
- "Direct subagents — stays interactive between stages; practical up to ~8 workers"
- "Single forked subagent — simplest isolation; no parallelism"

Only include agent teams when the matrix ranks it AND the env gate is on (when
off, mention it needs `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and recommend
subagents as fallback). Conditional follow-ups on the same screen when relevant:

- **Isolation** — workers mutate files in parallel? → worktree per worker.
- **Coordination** — workers only report back, or must they debate? (report-back →
  subagents; debate → teams)

### Stage 4 — Guardrails

1. **Invoke** — as in the simple path; for cron skills, note that
   `disable-model-invocation: true` must NOT be set (v2.1.196 blocks scheduled
   runs) — gate with a narrow description and `disallowed-tools` instead.
2. **Tools** — pre-approve tools (`allowed-tools`) and/or remove tools
   (`disallowed-tools` — e.g. `AskUserQuestion` for anything unattended)?
3. **Enforce** — any must-happen/must-not-happen step? Recommend a skill-declared
   hook over prose for hard constraints, but warn that it outlives the invocation
   and stays armed for the whole session: `once: true` for a one-shot gate, an
   exact `matcher`/`if` for a narrow one (`references/frontmatter-reference.md` §6).
4. **Paths** — should the skill only activate for certain file globs (`paths`)?

### Stage 5 — Evals

1. **Success criterion** — one measurable statement of "it worked", derived from
   the Stage 1 outcome.
2. **Evals** — create `evals/evals.json` + run the no-skill baseline gate?
   Recommend "Yes" for objectively checkable output; the skill must beat the
   baseline to earn its place.
3. **Failure modes** — what should the skill do on empty/missing input? For
   unattended skills, always design the anti-stub guard: exit without output rather
   than fabricate a placeholder.

## Orchestration fork

The Stage 3 fork deserves its own rule because it is where interviews most often go
wrong: **architecture is chosen by the matrix, presented as a question, and decided
by the user** — not silently assumed. If the user's Stage 1 Timing answer was "may
need to ask mid-run", workflows (and cron) are off the table no matter how large
the fan-out is; offer direct subagents, or a Phase A/B/C split where every question
is asked before the workflow launches. State this constraint inside the option
description so the user is choosing with the trade-off visible.

## Research options

Local docs mirror checks are always-on (free, instant — see
`references/research-protocol.md`). Web and library research is opt-in via Stage 2
because it costs time and API credits; never launch it unasked. Whatever was
researched, come to the next screen with the findings folded into the options
rather than dumping them as prose.

## "Just vibe" degradation

At any point, if the user signals they don't want process ("just make it", "vibe
with me", "skip the questions"):

1. Stop interviewing immediately — this is a mode toggle, not a failed screen.
2. Fix the two things a skill cannot exist without, in prose: what it does, when it
   triggers. Confirm in one sentence, don't re-ask.
3. Take the decision-matrix default for architecture and state the assumption in
   one line ("Going with a plain inline skill — say the word if it should fan
   out").
4. Draft immediately; iterate on the artifact instead of the spec.
5. Evals become opt-in: offer once after the first successful run, drop it if
   declined.
