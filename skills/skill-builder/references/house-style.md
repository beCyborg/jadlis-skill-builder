# House Style (beCyborg fork)

User-specific conventions for skills created on this machine. **Read this whole
file at the start of every Create run.** Everything here overrides generic
defaults; nothing here is upstream material — keep it out of SKILL.md and the
generic references.

## Thin skill + workflow core + pinned agents

The house pattern for heavy skills (architecture 4 in
`references/orchestration-guide.md`), as implemented by the `jadlis-research`
plugin (repo `~/jadlis-research`; since 2026-09-10 the research stack ships as
plugins, there are no local `~/.claude/skills/full-research` or
`~/.claude/workflows/` copies any more):

- **Thin skill** (`skills/research/SKILL.md`, invoked as
  `/jadlis-research:research`): Phase A interview + recon, Phase B
  `Workflow({scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/full-research-core.js", args: {...}})`,
  Phase C vault write. All interaction in Phase A; the always-asked first
  interview question is "what decision will you make based on this?"
- **Workflow core** (`workflows/full-research-core.js`, shipped in the plugin):
  deterministic fan-out. Results are **file-mediated**: workers write into a
  `workDir`, the script returns a small contract object like
  `{workDir, status, channelsAnswered, reportPath, ...}` — paths and status, never
  payloads. Args may arrive as a JSON string — normalize with a try/parse guard.
- **Pinned agents** (`agents/researcher-opus.md` and the other agents in the same
  plugin, referenced as `agentType: 'jadlis-research:researcher-opus'`): heavy
  stages pin `model:`/`effort:` via a custom agent, not via the skill's `model:`
  field. Effort is no longer part of agent names — it changes more often than the
  model. Worker agents state "never invoke manually — the whole prompt comes from
  the orchestrator" in their description and must not spawn nested subagents or
  invoke skills.

New heavy skills follow this trio: `<skill>/SKILL.md` + `<skill>-core.js` + a
pinned worker agent (reuse an existing pinned worker agent when the role fits).
Which model and effort to pin per role: `references/model-routing.md`, then the
personal overlay it points to.

## Bilingual triggers

Skill prose for this user is written in Russian (deliverables are Russian; skill
*text* for skill-builder's own output stays English per fork policy, but
user-facing skills here are Russian). Descriptions use the house trigger format —
both languages, explicit boundaries:

```
TRIGGER when: user says "полный ресерч", "full research", "deep research", ...
DO NOT TRIGGER when: only web search (use search), library docs (use Context7).
```

Always include both RU and EN trigger phrases, and always include the DO NOT
TRIGGER line routing near-miss intents to the right neighboring skill.

## Canonical `allowed-tools` form

The canonical form is a **comma-separated string with `Bash(cmd:*)` scoping** (the
`verif` skill is the reference):

```yaml
allowed-tools: Read, Glob, Write, Edit, AskUserQuestion, Agent, Bash(codex:*), Bash(jq:*), Bash(mktemp:*)
```

Scope every Bash pre-approval to a command (`Bash(git:*)`), never bare `Bash`.
YAML-list `allowed-tools` in existing skills is legacy — do not migrate old skills,
but write all new ones in the comma-string form.

## Directory conventions

- `references/` = knowledge loaded on demand (facts, schemas, guides).
- `protocols/` = step-by-step playbooks a worker agent executes for one phase
  (e.g. `full-research/protocols/web-protocol.md`). If a workflow worker reads it
  as its instructions, it is a protocol, not a reference.
- `~/.claude/skills/_shared/*.md` = cross-skill contracts referenced by absolute
  path (e.g. `obsidian-write-contract.md`, `metric-status-formula.md`). Check
  `_shared/` before duplicating a contract into a new skill.

## Invocation defaults

- Worker/internal skills that only an orchestrator should run:
  `disable-model-invocation: true` (and remember this also blocks scheduled-task
  invocation as of v2.1.196 — cron skills must not set it).
- Batch interview UX: `AskUserQuestion` with up to 4 questions per screen,
  recommended option first with "(Recommended)" — the `verif` findings interview
  is the reference implementation.

## Run contract

- Every new skill includes the `## Run contract` block (Done when, keep going vs.
  stop, subagent checks, progress file, final report) — see the `init_skill.py`
  template.

## Integration testing

Skills with live external dependencies (MCP servers, CLIs, browser) get a
`TESTS.md` capability matrix — see `references/integration-testing.md`.
