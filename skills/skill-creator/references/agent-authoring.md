# Agent Authoring Guide

> Last audited against Claude Code docs: 2026-09-01 (~v2.1.251, mirror b290425)

When a skill creates or works with companion subagents.

## Skill vs Agent frontmatter

Skills and subagents have separate `.md` files with **different** frontmatter fields:

### SKILL.md frontmatter
Fields like `name`, `description`, `when_to_use`, `arguments`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`, `disable-model-invocation`, `user-invocable`. (Skill uses the hyphenated `disallowed-tools`; agents use camelCase `disallowedTools` — see below.)

### Agent `.md` frontmatter (`.claude/agents/`)
Fields: `name`, `description`, `prompt`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental`. (See the canonical [sub-agents docs](https://code.claude.com/docs/en/sub-agents) for the complete table.) For agents the `model` field defaults to `inherit`. `prompt` sets the system prompt and is equivalent to the markdown body — it exists mainly for the JSON `--agents` flag; in `.md` files write the body instead. Since v2.1.243 `--agents` no longer silently ignores invalid JSON or invalid agent definitions — it exits with a clear error, like `--mcp-config`, so a malformed inline definition fails loudly rather than yielding a session without the agent.

Two field semantics worth spelling out:

- **`maxTurns`** — since v2.1.246 a subagent that stops at its `maxTurns` limit returns its output **marked as partial**, with a hint to continue it via `SendMessage`, instead of looking finished. A skill that caps worker turns must therefore check for the partial marker and either continue the worker or treat the result as incomplete; don't read a returned payload as a completed run.
- **`experimental.cacheTtl`** (v2.1.248+) — per-agent prompt cache lifetime, `"5m"` or `"1h"`. Write it **inside the `experimental` map**, not at the top level; any other value is ignored, `1h` is ignored while the Claude subscription is using usage credits, and the field is read only from subagent files. It applies below the `promptCacheTtl`/`subagentPromptCacheTtl` settings (v2.1.243+, which keep a 1-hour cache for the main conversation while subagents stay at 5 minutes) and below `FORCE_PROMPT_CACHING_5M`/the bucket env var. Useful for a long-lived worker that re-reads a big prompt prefix:

```yaml
---
name: repo-auditor
description: Audits a large repository and reports what it finds
experimental:
  cacheTtl: 1h
---
```

**Naming (v2.1.218+):** agent names use lowercase letters and hyphens and **cannot contain `:`** — the colon is reserved for plugin-scoped identifiers (`my-plugin:reviewer`). Claude Code doesn't load a file whose agent name contains one and logs the error only to the debug log, so a bad name fails silently from the user's point of view. Also note the Task tool's `mode` parameter is deprecated and ignored as of v2.1.212 — subagents inherit the parent session's permission mode by default; use `permissionMode` in the agent definition instead.

Model-inheritance facts worth knowing when pinning workers:
- `CLAUDE_CODE_SUBAGENT_MODEL` sets the **default** subagent model since v2.1.251 — it no longer overrides everything. The order is: a model named at spawn time → the definition's `model` field (including `inherit`) → `CLAUDE_CODE_SUBAGENT_MODEL` → the session/lead model. So `model:` in `.claude/agents/<worker>.md` is the reliable place to pin a worker; before v2.1.251 an exported variable silently beat it. Setting the variable to `inherit` is the same as leaving it unset.
- The built-in **Explore** agent inherits the main session's model (v2.1.198+; it no longer runs on Haiku), capped at Opus on the Claude API — with today's default session model that means Explore runs on the session's Opus/Sonnet tier, never above it. On other providers (Bedrock, Vertex, Foundry) it inherits directly with no cap. A user/project agent named `Explore` overrides the built-in and keeps its own `model` field — define one with `model: haiku` to pin exploration to a cheaper model.
- `isolation: worktree` is git-hardened: worktree subagents are prevented from running shell/git-mutating commands against the main checkout instead of their own worktree (fixes landed in v2.1.203, v2.1.210, and v2.1.222 — the latter extends isolation of file edits and Bash to every session type). Still treat worktree isolation as protection against *accidents*, not a security boundary.

The `memory` field enables persistent memory for agents. Scopes:
- `user` — stored in `~/.claude/agent-memory/<agent-name>/`, available across all projects
- `project` (recommended default) — stored in `.claude/agent-memory/<agent-name>/`, shareable via git
- `local` — stored in `.claude/agent-memory-local/<agent-name>/`, gitignored

Set in frontmatter: `memory: project`. (The `/agents` wizard was removed in v2.1.198 — ask Claude to create/manage subagents or edit `.claude/agents/` directly.)

**Do not mix these.** Agent-specific fields (`memory`, `isolation`, `mcpServers`, etc.) belong in agent `.md` files, not in SKILL.md.

> **Plugin-distributed agents are restricted.** For security, agents loaded from a plugin silently ignore the `hooks`, `mcpServers`, and `permissionMode` frontmatter fields. If a companion agent needs those, ship it in `.claude/agents/` or `~/.claude/agents/` rather than inside the plugin.

## Skill with `context: fork`

A skill with `context: fork` runs in a subagent. The `agent` field selects the agent type:

```yaml
---
name: security-scan
description: Scan for security vulnerabilities
context: fork
agent: general-purpose
---
Scan the codebase for security vulnerabilities.
```

Built-in agent types: `Explore`, `Plan`, `general-purpose`. Since v2.1.235 the Agent tool no longer advertises `general-purpose` by default where that agent isn't available — omitting `subagent_type` returns a clear error listing the types the session actually has, so don't assume `general-purpose` exists in every environment.

For a custom agent, use the agent name from `.claude/agents/<name>.md`:

```yaml
---
name: deep-review
context: fork
agent: my-custom-reviewer
---
```

## Decision guide: `context: fork` vs standard skill

| Use `context: fork` when... | Use standard skill when... |
|---|---|
| Task is self-contained | Task needs conversation context |
| Heavy or parallel work | Quick, interactive response needed |
| Side effects should be isolated | User should see the transcript |
| Custom agent with special tools/model | Default tools are sufficient |

## Preloading skills into agents

Custom agents can preload skills via the `skills` field in their `.md` frontmatter:

```yaml
---
name: api-developer
description: Implement API endpoints
skills:
  - api-conventions
  - error-handling-patterns
---
```

The **full content** of each listed skill is injected at agent startup — not just the description — so budget the agent's context accordingly. Caveats:

- A skill with `disable-model-invocation: true` **cannot** be preloaded this way — Claude Code skips it and logs a warning, so don't rely on it here.
- Built-in agents (Explore, Plan, general-purpose) don't preload skills — `skills` only works on custom agent definitions.
- When the definition runs as an agent-teams **teammate**, `skills` (and `mcpServers`) are not applied — see `references/orchestration-guide.md` §5.

## Managing agents

The `/agents` wizard was removed in v2.1.198. Ask Claude to create or manage subagents, or edit `.claude/agents/*.md` directly — Claude Code watches those directories and picks up changes within seconds, no restart needed.
