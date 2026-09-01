# Environment Notes: Claude.ai and Cowork

> Last audited against Claude Code docs: 2026-09-01 (~v2.1.251, mirror b290425)

The core loop (draft → test → review → improve) is the same everywhere; only the mechanics change.

**File delivery gate (both environments):** before pointing the user at a file path, check whether a file-presentation tool is available in the session (e.g. `present_files` / a send-file tool). In Claude.ai and Cowork the user cannot browse the local filesystem — a bare path like `/tmp/my-skill.skill` is unreachable for them. If the tool exists, deliver outputs (packaged `.skill` files, eval viewer HTML, reports) through it; if not, fall back to showing the content inline or telling the user where to download it.

## Claude.ai (no subagents)

- **Run test cases inline, one at a time**: read the skill's SKILL.md and follow it yourself. Less rigorous than independent executors (you wrote the skill and you're running it), but a useful sanity check — human review compensates. Skip baseline runs and quantitative benchmarking.
- **No browser/display**: skip the viewer; present prompt + output per test case directly in conversation, save file outputs to disk for the user to download, ask for feedback inline.
- **Description optimization requires `claude -p`** (Claude Code only) — skip it.
- **Updating an existing skill**: the installed path may be read-only — copy to `/tmp/<skill-name>/`, edit there, package from the copy. Preserve the original directory name and `name` frontmatter (output `research-helper.skill`, not `research-helper-v2`). If packaging manually, stage in `/tmp/` first, then copy out.

## Cowork (subagents, no display)

- Subagents work — the full parallel workflow applies (fall back to serial runs if timeouts bite).
- **Generate the eval viewer BEFORE evaluating outputs yourself** — get results in front of the human ASAP, using `generate_review.py`, not hand-written HTML. Use `--static <output_path>` to write a standalone HTML file instead of starting a server, then give the user a clickable link.
- Feedback: with no running server, "Submit All Reviews" downloads `feedback.json` — read it from Downloads (may need access) and copy it into the workspace for the next iteration.
- Packaging and description optimization (`claude -p` subprocess) both work; save optimization until the skill is in good shape.
- Updating an existing skill: same read-only caveats as Claude.ai above.

## Frontmatter budget outside Claude Code

Enabling a personal skill for Cowork or cloud sessions (routines included) **uploads it to claude.ai**, so only the six portable fields — `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` — are allowed. Anything else fails the upload with a hard `Unexpected key(s) in SKILL.md frontmatter` error. Same rule for the Skills API and for `.skill` packages. Full table and consequences: `references/frontmatter-reference.md` §1.1.

## Skills synced from claude.ai are hardened (v2.1.228+)

A skill that Claude Code syncs down from a claude.ai account is treated as untrusted content, so a skill authored *for* that path must not depend on Claude Code-only body behavior:

- **No shell execution on the user's machine.** Claude Code never runs a synced skill's `` !`command` `` lines locally, regardless of `disableSkillShellExecution`. Behavior by session: in a **cloud** session the body behaves like a local skill (isolated container); in **Cowork on the desktop** every `!` line is replaced with the `disableSkillShellExecution` placeholder; in **any other local session** the `!` line reaches Claude as literal text, `@` file references are not attached, and `${CLAUDE_PROJECT_DIR}` / `${CLAUDE_SESSION_ID}` are not substituted — all arrive verbatim.
- **Descriptions are sanitized and labeled**: control characters stripped, angle brackets escaped in the text that reaches Claude, so a description can't imitate Claude Code's internal formatting. Frontmatter is still honored in every session — an `allowed-tools` grant goes through the normal permission flow.
- **No shadowing**: synced skills no longer shadow local commands or MCP prompts, and a synced skill whose name matches any built-in command is skipped.

Design rule: a skill meant to be synced must carry its logic in prose and bundled files, never in injected command output.

## `--restricted` sessions (v2.1.248+)

`claude --restricted` (or `CLAUDE_CODE_RESTRICTED=1`) removes the built-in tools that run commands or code and `WebFetch` (unless named in `--tools`), keeps file tools inside the working directory, refuses `bypassPermissions`, and ignores user, project, and local settings files. A skill that shells out or fetches URLs is inert there — state the requirement in SKILL.md and fail loudly rather than hanging.
