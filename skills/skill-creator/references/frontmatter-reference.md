# SKILL.md Frontmatter Reference

Complete reference for all frontmatter fields available in Claude Code SKILL.md files.

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard, which works across multiple AI tools. Claude Code extends the standard with additional features like invocation control, subagent execution, and dynamic context injection.

---

## 1. Complete Frontmatter Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | No (defaults to directory name) | Skill identifier. Must be kebab-case, max 64 characters. |
| `description` | string | Recommended | What the skill does and when to use it. Max 1024 chars, no angle brackets (`<>`). **Front-load key use cases in the first 250 chars** — descriptions are truncated at this length in the skill listing. If omitted, uses the first paragraph of markdown content. This is the primary triggering mechanism -- Claude reads descriptions to decide when to invoke a skill. |
| `argument-hint` | string | No | Hint shown during autocomplete in the `/` menu, e.g. `[issue-number]`, `[file-path]`. |
| `allowed-tools` | string or list | No | Tools Claude can use without asking permission while this skill is active. Accepts a space-separated string (`Read Grep Glob`) or YAML list (`["Bash", "Read"]`). Supports patterns: `Bash(gh *)`. |
| `model` | string | No | Model override for this skill. Forces a specific model when the skill is invoked. |
| `effort` | enum | No | Effort level override. Values: `low`, `medium`, `high`, `max`. Opus 4.6 only. |
| `paths` | string or list | No | Glob patterns limiting when the skill is activated. Accepts a comma-separated string or a YAML list. When set, skill auto-loads only when working with files matching the patterns. |
| `shell` | enum | No | Shell for dynamic context injection commands. Values: `bash` (default), `powershell`. Requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` for PowerShell. |
| `context` | enum | No | Execution context. Set to `fork` to run the skill in a forked subagent context instead of the main conversation. |
| `agent` | string | No | Which subagent type to use when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or a custom agent name. |
| `hooks` | object | No | Hooks scoped to this skill's lifecycle. Only active while the skill runs. See section 6. |
| `disable-model-invocation` | boolean | No (default: `false`) | When `true`, prevents Claude from auto-loading this skill. It will not appear in Claude's context and can only be invoked manually by the user via `/skill-name`. |
| `user-invocable` | boolean | No (default: `true`) | When `false`, hides the skill from the `/` menu. Only Claude can invoke it programmatically. |
| `license` | string | No | License identifier (e.g. `MIT`, `Apache-2.0`). From Agent Skills standard; not in Claude Code docs. |
| `metadata` | object | No | Custom key-value pairs for your own use. From Agent Skills standard; not in Claude Code docs. |

---

## 2. Invocation Control Matrix

How `disable-model-invocation` and `user-invocable` interact to control skill visibility:

| Frontmatter | User can invoke | Claude can invoke | When loaded into context |
|---|---|---|---|
| *(defaults)* | Yes | Yes | Description is always in context. Full skill content loads when invoked. |
| `disable-model-invocation: true` | Yes | No | Description is NOT in context. Full skill content loads only when user invokes via `/`. |
| `user-invocable: false` | No | Yes | Description is always in context. Full skill content loads when Claude invokes it. |

Key takeaways:
- Use `disable-model-invocation: true` for rarely-used skills to save context budget.
- Use `user-invocable: false` for internal/helper skills that Claude should call autonomously but users should not see in the menu.

---

## 3. String Substitutions

Available variables inside SKILL.md content (below the frontmatter):

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking the skill, as a single string. |
| `$ARGUMENTS[N]` | Specific argument by 0-based index. |
| `$N` | Shorthand for `$ARGUMENTS[N]`. E.g. `$0` is the first argument, `$1` is the second. |
| `${CLAUDE_SESSION_ID}` | Current Claude Code session ID. |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the directory containing this skill's SKILL.md file. |

If `$ARGUMENTS` is **not** referenced anywhere in the skill content, arguments are automatically appended as `ARGUMENTS: <value>` at the end.

### Example

```yaml
---
name: deploy
argument-hint: [environment]
---
Deploy to $ARGUMENTS environment.
Config path: ${CLAUDE_SKILL_DIR}/configs/$0.yaml
```

When invoked as `/deploy staging`:
- `$ARGUMENTS` resolves to `staging`
- `$0` resolves to `staging`
- `${CLAUDE_SKILL_DIR}` resolves to the skill's directory path

---

## 4. Dynamic Context Injection

The `` !`command` `` syntax runs shell commands **before** the skill content is sent to Claude. The command output replaces the placeholder inline.

This is preprocessing -- Claude only sees the final result with actual data already substituted.

### Example

```yaml
---
name: pr-summary
context: fork
agent: Explore
---
- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`

Summarize the changes in this PR.
```

When invoked, Claude receives the skill content with real diff output already embedded -- it never sees the backtick commands.

### Notes
- Commands run in the project's working directory.
- If a command fails, the error output is included in place of the placeholder.
- Use this for injecting dynamic context like git status, file listings, API responses, etc.

### Extended Thinking (ultrathink)

Include the word **"ultrathink"** anywhere in your skill content to enable extended thinking mode. This gives Claude a larger thinking budget for complex reasoning tasks. Use for skills that require deep analysis, multi-step planning, or complex code review.

---

## 5. Skills + Subagents Integration

### Skill as subagent (`context: fork`)

Run a skill in an isolated subagent context. The skill executes in a fork and returns results to the main conversation.

```yaml
---
name: security-scan
context: fork
agent: general-purpose
---
Scan the codebase for security vulnerabilities.
Report findings grouped by severity.
```

### Preloading skills into subagents

In a custom agent definition, use the `skills` field to inject full skill content into the subagent's context at startup:

```yaml
---
name: api-developer
description: Implement API endpoints
skills:
  - api-conventions
  - error-handling-patterns
---
Implement the requested API endpoint following the preloaded conventions.
```

The full content of each listed skill is injected into the subagent's context when it starts, so the agent has immediate access to all referenced patterns and conventions.

---

## 6. Hooks in Skills

Hooks can be defined directly in skill frontmatter. They are **scoped to the skill's lifecycle** -- they are only active while the skill is running, and are removed when the skill completes.

### Supported hook events

All standard Claude Code hook events are supported: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, etc.

### Hook types

| Type | Description |
|---|---|
| `command` | Run a shell command. Non-zero exit blocks the action. |
| `http` | Send an HTTP request. |
| `prompt` | Inject a prompt for Claude to process. |
| `agent` | Spawn a subagent to evaluate. |

### Example

```yaml
---
name: secure-operations
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: prompt
          prompt: "Verify no secrets were written to the file"
---
Perform the requested operations with security checks enabled.
```

### The `once` field

Setting `once: true` on a hook causes it to run only once per session, then be automatically removed. This is a **skills-only feature** -- it is not available in global or project hooks.

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      once: true
      hooks:
        - type: prompt
          prompt: "Confirm this is the first Bash command of the session"
```

---

## 7. Context Budget

Skill descriptions consume approximately **~1% of the context window** (fallback: 8,000 characters). Each description is **truncated at 250 characters** in the skill listing, so front-load key trigger words. Full skill content only loads when the skill is actually invoked.

### Best practices

- Skills with `disable-model-invocation: true` have **zero context cost** until manually invoked by the user.
- Keep SKILL.md under **500 lines**. Move reference material, examples, and large prompts to supporting files and reference them with `Read` or dynamic context injection.
- If too many skills exceed the character budget, some may be excluded from context. Run `/context` to check which skills are loaded.
- Override the budget with the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable.

---

## 8. Skill Locations and Priority

| Location | Path | Applies to |
|---|---|---|
| Enterprise | Managed settings | All users in the organization |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where the plugin is enabled |

**Priority order:** Enterprise > Personal > Project.

Plugin skills use the `plugin-name:skill-name` namespace to avoid naming conflicts. For example, a skill `deploy` in plugin `my-tools` is invoked as `/my-tools:deploy`.

Skills in nested `.claude/skills/` directories are automatically discovered (useful for monorepo setups).

### Permission rules

Control which skills Claude can invoke using permission rules:

```text
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

Syntax: `Skill(name)` for exact match, `Skill(name *)` for prefix match with any arguments.

---

## 9. Validation

Use the CLI validation command to check skill frontmatter for YAML parse errors and schema violations before deploying:

```bash
claude plugin validate
```

This validates:
- YAML syntax in frontmatter
- Field types match the expected schema
- Required constraints (max lengths, allowed values) are met
- Skill file structure is correct
