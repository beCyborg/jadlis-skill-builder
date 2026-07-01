# Skill Writing Craft

Patterns and style for the skill body itself. Read when drafting or rewriting
SKILL.md content.

## Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** - It's useful to include examples. You can format them like this (but if "Input" and "Output" are in the examples you might want to deviate a little):
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

## Writing Style

Try to explain to the model why things are important in lieu of heavy-handed musty
MUSTs. Use theory of mind and try to make the skill general and not super-narrow to
specific examples. Start by writing a draft and then look at it with fresh eyes and
improve it.

For the final skill body: state what to do rather than narrating how or why. Every
line in a loaded skill is a recurring token cost across turns — optimize for signal
density in the artifact, while using explanatory context during the iterative
development process.

A few craft points that consistently help:

- **Prefer affirmative directives over negative-only ones.** "Write in flowing
  prose with no headers" beats "Don't use bullet points" — models follow positive
  instructions more reliably.
- **Put a rule where it fires, not in a wall of rules at the top.** Constraints
  loaded before Claude knows the task tend to fade out by the time the relevant
  step runs; inline the constraint at the step it governs. A long top-of-file
  "Rules" block is an anti-pattern.
- **Trim what the model already knows.** Don't restate general knowledge — it
  dilutes context until the skill's actual signal disappears. For style/voice
  skills, 3–5 real labeled examples teach more than any list of rules.
- **For must-happen steps, reach for a hook, not prose.** Skill instructions are
  strong hints the model can rationalize around; a `PreToolUse` hook (exit code 2
  blocks + feeds back) enforces deterministically. See
  `references/frontmatter-reference.md` §6.
