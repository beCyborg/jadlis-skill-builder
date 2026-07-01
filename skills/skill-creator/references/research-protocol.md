# Research Protocol for Skill Creation

Two tiers: local docs are always checked; external research is opt-in.

## Always: local Claude Code docs mirror

Before writing frontmatter or choosing an orchestration architecture, verify
against the local docs mirror at `~/.claude-code-docs/docs/` (if present —
otherwise use the official docs at https://code.claude.com/docs):

```bash
grep -rn "<feature keyword>" ~/.claude-code-docs/docs/skills.md \
  ~/.claude-code-docs/docs/sub-agents.md ~/.claude-code-docs/docs/workflows.md \
  ~/.claude-code-docs/docs/agent-teams.md ~/.claude-code-docs/docs/hooks.md
```

Key files: `skills.md` (frontmatter, substitutions, lifecycle), `sub-agents.md`,
`agent-teams.md`, `workflows.md`, `hooks.md`, `plugins-reference.md`,
`changelog.md` (feature version gates). This costs nothing and catches the most
common failure: a skill built on a stale or misremembered feature. When the mirror
and this skill's reference files disagree, the mirror wins — and note the
discrepancy so the reference can be fixed.

## On request: web and library research

Offered as an interview option (see `references/creation-interview.md`, Stage 2),
never launched unasked — it costs time and API credits:

- **Library/SDK surface** (the skill wraps an external API, SDK, CLI): library
  docs tooling such as Context7 MCP (`resolve-library-id` → `query-docs`), or the
  vendor's docs via web search.
- **Freshness/domain questions** (best practices, ecosystem state, comparable
  skills): web search (e.g. Brave Search MCP or the built-in search available in
  the session).

Fold findings into the interview options and the draft; cite sources in the
skill's references/ files when a design decision rests on them.

## Exit criterion

Research is done when no architecture-relevant uncertainty remains: every
frontmatter field used is confirmed by the docs, external API shapes are known,
and version-gated features have their minimum version noted. Do not fix the
architecture (interview Stage 3) before this point.
