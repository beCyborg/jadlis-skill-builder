# Skill Writing Craft

Patterns and style for the skill body itself. Read when drafting or rewriting
SKILL.md content.

## What NOT to include

README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, or any auxiliary documentation.
Skills are for AI agents, not human onboarding.

## Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited, scripts can execute without loading)

These word counts are approximate and you can feel free to go longer if needed.

**Key patterns:**
- Keep SKILL.md under 500 lines; if you're approaching this limit, move detail into reference files linked directly from SKILL.md, with clear pointers about when to read each one.
- Keep references one level deep: a file reached only through another reference may be previewed instead of read in full.
- Reference files clearly from SKILL.md with guidance on when to read them
- For reference files longer than 100 lines, include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant:
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```
Claude reads only the relevant reference file.

## Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

## Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:
```markdown
## Report structure
Use this exact template:
# [Title]
## Result
## Не удалось подтвердить — what, and where it was looked for
**От тебя:** — only when the user must do or decide something
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

Five more points come from Anthropic's "Prompting Claude Fable 5.2"
(platform.claude.com, read 2026-11-09). Anthropic measured them on its own tasks —
confirm each on the skill's evals:

- **Keep reasoning out of the output.** Ask for the result and a short
  justification, not for the model's reasoning: "think step by step in
  `<thinking>` tags" or "show your reasoning" can be declined (refusal category
  `reasoning_extraction`, no automatic fallback). Depth comes from `effort:`, not
  from prompt lines — "answer directly without deliberating" no longer lowers
  thinking at `medium` and above (`references/model-routing.md` §5).
- **Give a rule its scope, its reason and its exception.** The model applies a
  rule as written: a bare "never", or a category such as "anything external",
  makes it hold back routine work, and a separate "approved steps may proceed"
  line barely helps. Name the exact actions that need a go-ahead, put the
  exception inside the rule ("ask first, then …"), and name the routine steps
  that need none (retrying a call that is safe to repeat, re-running a script).
- **Describe the reader instead of capping the style.** A hard limit ("20 words
  per sentence at most") is followed literally and makes prose choppy. Say who
  reads the output and what they have not seen; keep a numeric limit only where
  an eval shows it is needed.
- **Price delegation where you ask for it.** A standing "use subagents" line is
  followed readily, and every subagent pays for a context of its own. Say when
  delegation pays, when to stay inline, and how to brief a worker
  (`references/orchestration-guide.md`, "Cost first").
- **Say who owns the code when the skill edits code.** Unstated, the model adds
  to the existing structure and reports nearby problems instead of fixing them.
  To have it restructure, say the codebase is its own to shape; for minimal
  diffs say so and leave that sentence out — a scope rule elsewhere does not
  cancel it.
