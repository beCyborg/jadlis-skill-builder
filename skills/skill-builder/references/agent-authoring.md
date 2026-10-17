# Agent Authoring Guide

> Last audited against Claude Code docs: 2026-10-17 (v2.1.302, mirror da8a6ce9)

When a skill creates or works with companion subagents.

## Skill vs Agent frontmatter

Skills and subagents have separate `.md` files with **different** frontmatter fields:

### SKILL.md frontmatter
Fields like `name`, `description`, `when_to_use`, `arguments`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`, `disable-model-invocation`, `user-invocable`. (Skill uses the hyphenated `disallowed-tools`; agents use camelCase `disallowedTools` — see below.)

### Agent `.md` frontmatter (`.claude/agents/`)
Fields: `name`, `description`, `prompt`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `autoCompactWindow`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental`. (See the canonical [sub-agents docs](https://code.claude.com/docs/en/sub-agents) for the complete table.) Claude Code ignores an unrecognized field without an error; since v2.1.296 `claude --debug` writes up to five unrecognized top-level fields of a loaded agent file to `~/.claude/debug/<session-id>.txt`, with the likely intended name — search the log for `does not recognize or apply` (`sub-agents.md:301`). Run it once on a new agent file. `omitClaudeMd: true` (v2.1.271+) launches the subagent without the user, project and local CLAUDE.md files (managed policy files still load) — for workers that get everything from the delegation prompt. **An omitted `model` is not the same as `model: inherit`:** without the field Claude Code walks the order below (spawn-time model → definition → `CLAUDE_CODE_SUBAGENT_MODEL` → main model), so an exported variable decides; an explicit `inherit` is the definition's value and beats the variable. `prompt` sets the system prompt and is equivalent to the markdown body — it exists mainly for the JSON `--agents` flag; in `.md` files write the body instead. Since v2.1.243 `--agents` no longer silently ignores invalid JSON or invalid agent definitions — it exits with a clear error, like `--mcp-config`, so a malformed inline definition fails loudly rather than yielding a session without the agent. Since v2.1.281 `--agents` also accepts a path to a JSON file (with `-p`), and an empty `prompt` is allowed.

Field semantics worth spelling out:

- **`effort`** — the definition's level is a default, not a pin. Since v2.1.292 Claude can pass an `effort` parameter to the Agent tool for one launch of a non-fork subagent; it beats the definition's `effort` and stays in effect when that subagent is resumed. `CLAUDE_CODE_EFFORT_LEVEL` beats both (`sub-agents.md:320,425`; changelog 2.1.292). A skill that needs a worker at a set level can say so in the delegation step ("launch `<agent>` with effort `high`") instead of shipping a second agent file per level.
- **`autoCompactWindow`** (v2.1.296+, also in `--agents` JSON and in plugin agents) — an integer token count from 100000 to 1000000 at which the subagent auto-compacts its own conversation. It can only **lower** the window the subagent would otherwise inherit and has no effect when the agent runs as the main session agent (`--agent` or the `agent` setting). An exported `CLAUDE_CODE_AUTO_COMPACT_WINDOW` beats the field. Write a plain integer: `200k` reads as 200, out of range, and the agent then compacts as if the field were absent — `claude --debug` logs `invalid autoCompactWindow` (`sub-agents.md:313,1170-1187`). Useful for a long-running worker that should compact before its context gets large.
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

  Plugin-shipped agents support `name`, `description`, `model`, `effort`, `maxTurns`, `autoCompactWindow`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` (`"worktree"` only), `color`, and the `cacheTtl` key of `experimental` — so `cacheTtl` works inside a plugin too. They ignore `permissionMode`, `hooks`, `mcpServers`, and `initialPrompt` (`plugins__components.md:739-740`).

**Naming (v2.1.218+):** agent names use lowercase letters and hyphens and **cannot contain `:`** — the colon is reserved for plugin-scoped identifiers (`my-plugin:reviewer`). Since v2.1.292 a name is also capped at **256 characters**, and one that starts with `-` is refused too. Claude Code doesn't load a file whose agent name breaks these rules and logs the error only to the debug log, so a bad name fails silently from the user's point of view (`sub-agents.md:306,343`; changelog 2.1.292).

**MCP tools in `tools:` / `disallowedTools:`** — write a server-level entry with the server's whole normalized name: `mcp__<server>__*` in `tools` grants every tool of that server; `mcp__<server>` or `mcp__<server>__*` in `disallowedTools` withholds them; `mcp__*` in `disallowedTools` withholds every MCP tool (`sub-agents.md:480-486`). Since v2.1.299 such an entry reaches only that server: `mcp__a` no longer also grants a server named `a__b`, so a server whose name contains `__` must be listed as `mcp__<whole name>__*` (changelog 2.1.299). Permission allow rules changed the same way. Also note the Task tool's `mode` parameter is deprecated and ignored as of v2.1.212 — subagents inherit the parent session's permission mode by default; use `permissionMode` in the agent definition instead.

Model-inheritance facts worth knowing when pinning workers:
- `CLAUDE_CODE_SUBAGENT_MODEL` sets the **default** subagent model since v2.1.251 — it no longer overrides everything. The order is: a model named at spawn time → the definition's `model` field (including `inherit`) → `CLAUDE_CODE_SUBAGENT_MODEL` → the session/lead model. So `model:` in `.claude/agents/<worker>.md` is the reliable place to pin a worker — **unless `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` is set** (v2.1.257+): then every definition's `model` is ignored and Claude can't pass one at spawn; only forks and `context: fork` skills with `model: inherit` stay on the main model. Before v2.1.251 an exported variable silently beat the pin as well. Setting the variable to `inherit` is the same as leaving it unset. Verify the model a worker actually got with `/tasks`. Choosing the model and effort per role: `references/model-routing.md`.
- The built-in **Explore** agent inherits the main session's model (v2.1.198+; it no longer runs on Haiku), capped at Opus on the Claude API — with today's default session model that means Explore runs on the session's Opus/Sonnet tier, never above it. On other providers (Bedrock, Vertex, Foundry) it inherits directly with no cap. A user/project agent named `Explore` overrides the built-in and keeps its own `model` field — define one with `model: haiku` to pin exploration to a cheaper model.
- `isolation: worktree` is git-hardened: worktree subagents are prevented from running shell/git-mutating commands against the main checkout instead of their own worktree (fixes landed in v2.1.203, v2.1.210, and v2.1.222 — the latter extends isolation of file edits and Bash to every session type). Still treat worktree isolation as protection against *accidents*, not a security boundary.

The `memory` field enables persistent memory for agents. Scopes:
- `user` — stored in `~/.claude/agent-memory/<agent-name>/`, available across all projects
- `project` (recommended default) — stored in `.claude/agent-memory/<agent-name>/`, shareable via git
- `local` — stored in `.claude/agent-memory-local/<agent-name>/`, gitignored

Set in frontmatter: `memory: project`. (The `/agents` wizard was removed in v2.1.198 — ask Claude to create/manage subagents or edit `.claude/agents/` directly.)

**Do not mix these.** Agent-specific fields (`memory`, `isolation`, `mcpServers`, etc.) belong in agent `.md` files, not in SKILL.md.

> **Plugin-distributed agents are restricted.** For security, agents loaded from a plugin silently ignore the `hooks`, `mcpServers`, `permissionMode`, and `initialPrompt` frontmatter fields. If a companion agent needs those, ship it in `.claude/agents/` or `~/.claude/agents/` rather than inside the plugin.

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

- **At most 32 skills** are preloaded, each once (v2.1.295+); a subagent that has the Skill tool can still invoke the rest on demand (changelog 2.1.295). Past 32, list only the skills the agent needs on every run.
- A skill with `disable-model-invocation: true` **cannot** be preloaded this way — Claude Code skips it and logs a warning, so don't rely on it here.
- Built-in agents (Explore, Plan, general-purpose) don't preload skills — `skills` only works on custom agent definitions.
- When the definition runs as an agent-teams **teammate**, `skills` is never applied and `mcpServers` only in a split-pane teammate — see `references/orchestration-guide.md` §5.

## Managing agents

The `/agents` wizard was removed in v2.1.198. Ask Claude to create or manage subagents, or edit `.claude/agents/*.md` directly — Claude Code watches those directories and picks up changes within seconds, no restart needed.
