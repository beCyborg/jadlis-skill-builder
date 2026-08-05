# SKILL.md Frontmatter Reference

> Last audited against Claude Code docs: 2026-08-05 (v2.1.222)

Complete reference for all frontmatter fields available in Claude Code SKILL.md files.

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard, which works across multiple AI tools. Claude Code extends the standard with additional features like invocation control, subagent execution, and dynamic context injection.

---

## 1. Complete Frontmatter Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | No (defaults to directory name) | Display label shown in skill listings. Kebab-case, max 64 characters. **It does not set the command you type** — the command comes from the skill's directory name (`.claude/skills/<dir>/` → `/<dir>`). The one exception is a plugin-root `SKILL.md` with no `skills/` subdir, where `name` *does* set the command. Keep `name` equal to the directory basename; a mismatch can suppress argument-hint/autocomplete. |
| `description` | string | Recommended | What the skill does and when to use it. No angle brackets (`<>`). Front-load the key use case: the combined `description` and `when_to_use` text is truncated at **1,536 characters** in the skill listing. If omitted, uses the first paragraph of markdown content. This is the primary triggering mechanism. |
| `when_to_use` | string | No | Additional context for when Claude should invoke the skill — trigger phrases, example requests. Appended to `description` in the skill listing and counts toward the 1,536-character cap. |
| `argument-hint` | string | No | Hint shown during autocomplete in the `/` menu, e.g. `[issue-number]`, `[file-path]`. |
| `arguments` | string or list | No | Named positional arguments for `$name` substitution in the skill content. Accepts a space-separated string or a YAML list. Names map to argument positions in order. |
| `allowed-tools` | string or list | No | Pre-approves the listed tools (no permission prompt) while this skill is active. Accepts a space-separated string (`Read Grep Glob`) or YAML list (`["Bash", "Read"]`). Supports patterns: `Bash(gh *)`. **It does not restrict the tool pool** — every tool remains callable; to remove tools use `disallowed-tools`. For project skills, this takes effect only after you accept the workspace-trust dialog, so review project skills before trusting a repo. Context: the default permission mode is named **Manual** as of v2.1.200 (`manual` is accepted alongside `default`), so unlisted tools prompt unless the user switched modes. |
| `disallowed-tools` | string or list | No | Removes the listed tools from the model's available pool while this skill is active — the inverse of `allowed-tools`. Useful for autonomous/background-loop skills that should never call a tool (e.g. `AskUserQuestion`). Accepts a space/comma string or YAML list. The restriction clears when you send your next message. Works for slash commands too. (v2.1.152+) |
| `model` | string | No | Model override for this skill. Accepts the same values as `/model`, or `inherit` to keep the active model. The override is **turn-scoped**: it applies for the rest of the current turn and is not saved — the session model resumes on your next prompt. A value excluded by an org `availableModels` allowlist is ignored. The session default is the recommended model for the account type (an org default set by an admin overrides it) — don't hardcode assumptions about which model that resolves to. |
| `effort` | enum | No | Effort level override. Values: `low`, `medium`, `high`, `xhigh`, `max`. Available levels depend on the model. |
| `paths` | string or list | No | Glob patterns limiting when the skill is activated. Accepts a comma-separated string or a YAML list. When set, skill auto-loads only when working with files matching the patterns. Uses the same format as path-specific rules. Skills in nested `.claude/skills/` directories and `--add-dir` directories are automatically discovered. |
| `shell` | enum | No | Shell for dynamic context injection commands. Values: `bash` (default), `powershell`. `powershell` runs inline commands via the PowerShell tool — on by default on Windows without Git Bash; elsewhere it requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`. |
| `context` | enum | No | Execution context. Set to `fork` to run the skill in a forked subagent context instead of the main conversation. As of v2.1.218 the fork runs in the **background by default** — see the `background` field and the consequences listed in §5. |
| `agent` | string | No | Which subagent type to use when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or a custom agent name. |
| `background` | boolean | No (default: `true`) | Only applies with `context: fork`. Set to `false` to wait for the forked subagent's result in the turn that invoked the skill, instead of running it in the background. (v2.1.218+; before that, forked skills always ran in the foreground.) |
| `hooks` | object | No | Hooks scoped to this skill's lifecycle. Only active while the skill runs. See section 6. |
| `disable-model-invocation` | boolean | No (default: `false`) | When `true`, prevents Claude from auto-loading this skill. It will not appear in Claude's context and can only be invoked manually by the user via `/skill-name`. It also cannot be preloaded into a subagent via the agent's `skills:` field (Claude Code skips it with a warning). As of v2.1.196 it **also blocks the skill from running when a scheduled task fires** with the skill as its prompt — do not set it on skills meant to run from cron/scheduled tasks. As of v2.1.222, when Claude tries to invoke such a skill, the refusal tells it to ask the user to run the skill instead of replicating its workflow. |
| `user-invocable` | boolean | No (default: `true`) | When `false`, hides the skill from the `/` menu. Only Claude can invoke it programmatically. |
| `license` | string | No | License identifier (e.g. `MIT`, `Apache-2.0`). From Agent Skills standard; not in Claude Code docs. |
| `metadata` | object | No | Custom key-value pairs for your own use. From Agent Skills standard; not in Claude Code docs. |
| `display-name` | string | No | Human-friendly display name. From Agent Skills standard; not in Claude Code docs. |
| `default-enabled` | boolean | No | Whether the skill starts enabled. From Agent Skills standard; not in Claude Code docs. |
| `fallback` | string | No | Fallback behavior hint. From Agent Skills standard; not in Claude Code docs. |

**Key casing (v2.1.186+):** the `display-name`, `default-enabled`, `fallback`, and `metadata.*` keys are accepted in kebab-case, snake_case, or camelCase (`display-name` / `display_name` / `displayName`). Prefer kebab-case for consistency with the rest of the frontmatter. Malformed YAML frontmatter no longer fails silently — Claude Code loads the skill body with empty metadata instead (v2.1.186+).

**Boolean literals (v2.1.218+):** boolean fields accept `yes`, `no`, `on`, `off`, `1`, and `0` in any letter case, in addition to `true` and `false`. Before v2.1.218 only `true`/`false` were recognized.

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
- `disable-model-invocation: true` also blocks scheduled-task invocation (v2.1.196+) — a cron/scheduled skill must leave it unset and rely on a narrow `description` plus `disallowed-tools` instead.
- **Stacked invocation (v2.1.199+):** `/skill-a /skill-b do XYZ` loads the first skill plus up to five more stacked after it (six total), passing the trailing text as `$ARGUMENTS` to each. Expansion stops at the first token that isn't an inline user-invocable skill — a `context: fork` skill or one whose arguments may themselves start with a slash (e.g. `/loop`) ends the run there. Note: `/code-review` runs as a forked subagent from v2.1.218, so it too ends the run (before that it ran inline and stacked). Before v2.1.199 only the first skill loaded.

---

## 3. String Substitutions

Available variables inside SKILL.md content (below the frontmatter):

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking the skill, as a single string. |
| `\$` | Escapes a literal `$` before a digit, `ARGUMENTS`, or a declared argument name (e.g. `\$1.00` in prose). A backslash before any other `$` is left unchanged; a doubled backslash (`\\$1`) keeps both backslashes and `$1` still expands. |
| `$ARGUMENTS[N]` | Specific argument by 0-based index. |
| `$N` | Shorthand for `$ARGUMENTS[N]`. E.g. `$0` is the first argument, `$1` is the second. |
| `$name` | Named argument declared in the `arguments` frontmatter list. Names map to positions in order, so with `arguments: [issue, branch]` the placeholder `$issue` expands to the first argument and `$branch` to the second. |
| `${CLAUDE_SESSION_ID}` | Current Claude Code session ID. |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the directory containing this skill's SKILL.md file. For plugin skills, this is the skill's subdirectory within the plugin, not the plugin root. |
| `${CLAUDE_EFFORT}` | Current effort level: `low`, `medium`, `high`, `xhigh`, or `max`. Adapt skill instructions by effort. Ultracode is **not** a distinct level — it reports as `xhigh`. (v2.1.120+) |
| `${CLAUDE_PROJECT_DIR}` | The project root directory — the same path hooks and MCP servers receive as `CLAUDE_PROJECT_DIR`. Applies to both the skill body and `allowed-tools` (e.g. `Bash(${CLAUDE_PROJECT_DIR}/scripts/lint.sh *)`). Use it to reference project-local scripts independent of where the skill is installed. (v2.1.196+) |

If `$ARGUMENTS` is **not** referenced anywhere in the skill content, arguments are automatically appended as `ARGUMENTS: <value>` at the end.

Unmatched positional placeholders (`$1`/`$2` with no corresponding argument) are preserved verbatim in the content as of v2.1.210 — before that they were silently stripped. Don't rely on stripping to hide optional-argument scaffolding; guard optional arguments in prose instead.

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

### Multi-line Dynamic Context

For multi-line commands, use a fenced code block opened with ` ```! ` instead of the inline form:

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

### disableSkillShellExecution

To disable shell execution in skills from user, project, plugin, or additional-directory sources, set `"disableSkillShellExecution": true` in settings. Each command is replaced with `[shell command execution disabled by policy]`. Bundled and managed skills are not affected. Most useful in managed settings where users cannot override it.

### Extended Thinking (ultrathink)

Include the word **"ultrathink"** anywhere in your skill content to enable extended thinking mode. This gives Claude a larger thinking budget for complex reasoning tasks. Use for skills that require deep analysis, multi-step planning, or complex code review.

---

## 5. Skills + Subagents Integration

### Skill as subagent (`context: fork`)

Run a skill in an isolated subagent context. The skill executes in a fork and returns results to the main conversation. It has no access to the conversation history.

**Background by default (v2.1.218+).** The forked subagent runs in the background: the user keeps working and the result arrives when it completes. Consequences to design for:

- A backgrounded fork runs with the **narrower tool set that applies to background subagents** — the skill's subagent is a regular agent type, so the exemption for subagents that fork the conversation doesn't cover it. If the skill's steps depend on a tool outside that set, set `background: false` to keep the full tool set.
- Edits a background fork applies land **outside the session's checkpoints** — `/rewind` doesn't undo them; use git to revert. A foreground fork (`background: false`) edits the working tree during the invoking turn, so rewind restores its edits as usual.
- Claude Code waits for the result anyway (as if `background: false`) in non-interactive mode (`-p` / Agent SDK), when `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, when an earlier invocation of the same skill is still running, and when a scheduled task fires with the skill as its prompt.

Before v2.1.218, forked skills always blocked the turn until they finished.

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

All standard Claude Code hook events are supported. This list is not exhaustive — see the [hooks docs](https://code.claude.com/docs/en/hooks) for the full set. Commonly used: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `SubagentStart`, `SubagentStop`, `SessionStart`, `MessageDisplay` (transform/hide assistant message text as it's displayed, v2.1.152+), `DirectoryAdded` (fires when a working directory is added mid-session via `/add-dir` or the SDK, v2.1.219+; non-blocking), plus the agent-teams events `TaskCreated`, `TaskCompleted`, and `TeammateIdle` (used to gate quality — a hook exiting with code 2 blocks the action and feeds its message back). `SessionStart`/`Setup`/`SubagentStart` hooks must be **command-type** (prompt/agent hooks are rejected), and a `SessionStart` hook can return `reloadSkills: true` to make skills it installed available in the same session.

**Workspace trust (v2.1.218+):** frontmatter hooks in a *project subagent* run only after the user accepts the workspace-trust dialog for the folder the agent file came from. Before v2.1.218 these hooks could run from untrusted folders. Relevant when a skill ships companion agents with hooks.

### Hook types

| Type | Description |
|---|---|
| `command` | Run a shell command. Non-zero exit blocks the action. |
| `http` | Send an HTTP request. |
| `mcp_tool` | Call a tool on a connected MCP server. |
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

### Best practices for hooks in skills

- Use `once: true` for one-time checks (e.g., environment verification at skill start)
- Keep hook commands fast — they block the tool call
- Use `prompt` type hooks for soft guidance, `command` type for hard enforcement
- Test hooks in isolation before adding them to skill frontmatter

---

## 7. Context Budget

The skill listing Claude sees each turn is budgeted at a **fraction of the model's context window** (default 1%). The combined `description` + `when_to_use` text is **truncated at 1,536 characters** per skill in the listing (canon: §1 `description` row), so front-load key trigger words. Full skill content only loads when the skill is actually invoked.

### Best practices

- Skills with `disable-model-invocation: true` have **zero context cost** until manually invoked by the user.
- Keep SKILL.md under **500 lines**. Move reference material, examples, and large prompts to supporting files and reference them with `Read` or dynamic context injection.
- When the listing exceeds the budget, descriptions for the least-used skills are dropped and only their names are listed — Claude can still invoke them but can't see what they do. Run `/context` to check which skills are loaded.
### Override the budget

- `skillListingBudgetFraction` in settings.json (v2.1.105+, default `0.01` = 1% of the model's context window). Raise to keep more descriptions visible at the cost of more context per turn.
- `skillListingMaxDescChars` — per-skill character cap on combined `description` + `when_to_use` (default 1536).
- `SLASH_COMMAND_TOOL_CHAR_BUDGET` — env var, fixed character count.
- Run `/doctor` to diagnose overflow and see which skills are affected.

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

Skills load from `.claude/skills/` in the starting directory AND every parent directory up to the repo root. Nested `.claude/skills/` directories discovered on demand. `--add-dir` directories have their `.claude/skills/` loaded automatically.

**Directory-qualified names (nested skills):** when a nested skill's name clashes with a project-root one, the nested skill appears under a directory-qualified name (`apps/web:deploy`) and both stay available; type the qualified name to run the nested variant explicitly. As of v2.1.203, invoking the *unqualified* name loads the project-root skill and appends a list of the directory-qualified variants, instructing Claude to also invoke any variant whose directory holds the files being worked on — so a nested skill still applies to work in its directory.

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

### skillOverrides (settings-based visibility)

Control skill visibility from settings without editing SKILL.md (v2.1.129+). The `/skills` menu writes the overrides to `.claude/settings.local.json` for you (highlight a skill, press Space to cycle states). Values: `"on"`, `"name-only"`, `"user-invocable-only"`, `"off"`.

```json
{
  "skillOverrides": {
    "my-skill": "off",
    "another-skill": "name-only"
  }
}
```

As of v2.1.199, `"off"` also hides the skill from the command lists advertised to **Remote Control** clients and **Agent SDK** callers, not only the terminal `/` menu; invoking a hidden skill by full name returns the skillOverrides error instead of running it.

Plugin skills are not affected; manage those through `/plugin`.

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
