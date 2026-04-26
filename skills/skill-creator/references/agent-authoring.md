# Agent Authoring Guide

When a skill creates or works with companion subagents.

## Skill vs Agent frontmatter

Skills and subagents have separate `.md` files with **different** frontmatter fields:

### SKILL.md frontmatter
Fields like `name`, `description`, `when_to_use`, `arguments`, `allowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`, `disable-model-invocation`, `user-invocable`.

### Agent `.md` frontmatter (`.claude/agents/`)
Fields like `name`, `description`, `model`, `memory`, `isolation`, `mcpServers`, `color`, `background`, `maxTurns`, `disallowedTools`, `skills`.

**Do not mix these.** Agent-specific fields (`memory`, `isolation`, `mcpServers`, etc.) belong in agent `.md` files, not in SKILL.md.

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

The full content of each listed skill is injected at agent startup.
