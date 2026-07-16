# Agent Authoring Guide

When a skill creates or works with companion subagents.

## Skill vs Agent frontmatter

Skills and subagents have separate `.md` files with **different** frontmatter fields:

### SKILL.md frontmatter
Fields like `name`, `description`, `when_to_use`, `arguments`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`, `disable-model-invocation`, `user-invocable`. (Skill uses the hyphenated `disallowed-tools`; agents use camelCase `disallowedTools` — see below.)

### Agent `.md` frontmatter (`.claude/agents/`)
Fields: `name`, `description`, `prompt`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`. (See the canonical [sub-agents docs](https://code.claude.com/docs/en/sub-agents) for the complete table.) For agents the `model` field defaults to `inherit`. `prompt` sets the system prompt and is equivalent to the markdown body — it exists mainly for the JSON `--agents` flag; in `.md` files write the body instead.

Two model-inheritance facts worth knowing when pinning workers:
- The built-in **Explore** agent inherits the main session's model, capped at opus (it no longer runs on haiku) — v2.1.198+.
- `isolation: worktree` is git-hardened: worktree subagents are prevented from running shell/git-mutating commands against the main checkout instead of their own worktree (fixes landed in v2.1.203 and v2.1.210). Still treat worktree isolation as protection against *accidents*, not a security boundary.

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

Built-in agent types: `Explore`, `Plan`, `general-purpose`.

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
