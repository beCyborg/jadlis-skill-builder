# Skill Content Lifecycle

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

## Live change detection

Claude Code watches skill directories — file creation and modification are detected without restarting. However:
- Already-loaded skill content in the current conversation is not updated — re-invoke needed
- Creating a new **top-level** skills directory (e.g., a new `.claude/skills/` path) requires a restart

## Best practices for long skills

- Keep SKILL.md under **500 lines** — move reference material to supporting files
- Front-load critical instructions in the first 5,000 tokens (they survive compaction)
- Check which skills are loaded with `/context`
