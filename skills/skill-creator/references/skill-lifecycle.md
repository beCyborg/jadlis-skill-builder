# Skill Content Lifecycle

> Last audited against Claude Code docs: 2026-09-01 (~v2.1.251, mirror b290425)

How skill content behaves across a Claude Code session.

## Loading

When you or Claude invoke a skill, the rendered SKILL.md content enters the conversation as a single message and stays there for the rest of the session. Claude Code does not re-read the skill file on later turns, so write guidance that should apply throughout a task as standing instructions rather than one-time steps.

## Compaction behavior

Auto-compaction carries invoked skills forward within a token budget:

- Each skill retains the **first 5,000 tokens** after compaction
- Combined budget across all invoked skills: **25,000 tokens**
- Budget is filled starting from the **most recently invoked** skill (MRU-first)
- Older skills can be dropped entirely after compaction if many were invoked in one session

## Re-invocation

If a skill seems to stop influencing behavior after the first response, the content is usually still present and the model is choosing other tools or approaches. To restore influence:

1. **Strengthen** the skill's `description` and instructions so the model keeps preferring it
2. **Use hooks** to enforce behavior deterministically
3. **Re-invoke** the skill after compaction to restore the full content

Editing a skill file on disk does not update the already-loaded content in the current session — you must re-invoke the skill to pick up changes.

Re-invoking is cheap when nothing changed: as of v2.1.202, re-invoking a skill whose **rendered content is identical** to the copy already in context adds only a short "already loaded" note instead of a second copy. The dedup is content-based, not name-based — when the rendered content differs, because arguments changed or a dynamic-context command produced new output, Claude Code appends the **full content again**. A skill with a `!` injection therefore re-appends on every invocation whose command output moved.

Note that the `allowed-tools` grant does *not* persist with the content: it covers only the turn that invoked the skill and clears on the next user message, so re-invoking is also how you re-apply the grant.

## Live change detection

Claude Code watches the already-active skill directories — `~/.claude/skills/`, the project `.claude/skills/`, and `.claude/skills/` inside an `--add-dir` directory. Edits, additions, and removals within those are picked up live. However:
- Already-loaded skill content in the current conversation is not updated — re-invoke needed (see Re-invocation above)
- Creating a **top-level** skills directory that did not exist when the session started is the one case the watcher can't pick up — run `/reload-skills` to re-scan without restarting, or restart if needed
- `/reload-skills` (v2.1.152+) re-scans all skill directories on demand; a `SessionStart` hook can return `reloadSkills: true` to surface skills it just installed in the same session
- Skills and commands changed during a session appear in the `/` slash menu without a restart as of v2.1.216 (before that, the menu showed the stale list until restart)

## Best practices for long skills

- Keep SKILL.md under **500 lines** — move reference material to supporting files
- Front-load critical instructions in the first 5,000 tokens (they survive compaction)
- Check which skills are loaded with `/context`
