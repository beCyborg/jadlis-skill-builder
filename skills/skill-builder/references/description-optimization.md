## Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

### Writing the description (checklist)

Before optimizing, get the basics right — these prevent most "my skill never fires" and "my skill fires on everything" problems:

- **Lead with the trigger condition, not the topic.** Sentence one should state *when* to fire ("Use when the user edits a `.svelte` file or asks to redact a PDF"), not just *what* it covers ("A skill for improving writing"). Crowded sessions truncate descriptions and you can't predict where the cut lands, so the firing condition must come first (within the first ~100 characters).
- **Write in the third person.** "Processes Excel files…", never "I can help…" or "You can use this…". Mixed point-of-view is injected into the system prompt and hurts discovery.
- **State both what AND when.** All "when to use" information lives in the `description`/`when_to_use`, never only in the body — the body loads *after* Claude has already decided to trigger.
- **Scope over-broad triggers.** A vague description ("checks content quality") fires on everything (package.json, README, JSON). Add file-type + directory + action scope ("checks markdown files in `drafts/` when writing or editing article content") so it fires only when relevant. Test descriptions for false positives, not just the happy path.
- **Add use-when / don't-use-when examples** to the `description`/`when_to_use` for skills that overlap with others — positive *and* near-miss negative examples sharpen routing, especially for cheaper models.
- **Keep it one line.** A multi-line YAML description can be mis-parsed so the skill silently disappears from the listing. Avoid angle brackets — Claude Code escapes `<>` in the text that reaches Claude rather than rejecting them, but escaped markup only burns trigger budget. Front-load regardless of the 1,536-char combined cap.

### Naming the skill

In a personal or project skill both the frontmatter `name` and the directory name invoke the skill (in a plugin skill, `name` replaces the last command segment), so name both well: prefer the **gerund form** (`processing-pdfs`, `analyzing-spreadsheets`) or a clear noun/action phrase. Avoid vague names (`helper`, `utils`, `tools`), reserved words (`anthropic`, `claude`), and the bundled-skill and built-in command names (`run`, `verify`, `run-skill-generator`, `loop`, `batch`, `simplify`, `code-review`, `debug`, `doctor`, `dataviz`, `design`, `design-sync`, `workflow-authoring`, `claude-api`, `fewer-permission-prompts`, `update-config`, `deep-research`, `init`, `review`, `security-review`, `schedule`) — a collision shadows the built-in. Aliases work the other way round: a local skill shadows a bundled skill's own name but **not** its aliases, so typing `/review` still runs the bundled `/code-review`, never yours, and `checkup` (→ `/doctor`) and `proactive` (→ `/loop`) stay pointed at the built-ins. Naming a skill after an alias therefore buys a name nobody can reach by that alias — avoid those too. Lowercase letters, digits, and hyphens only. Claude Code accepts `name` ≠ directory basename, but keep them equal by default: the 64-character cap and the `name` == folder-name rule come from the [Agent Skills spec](https://agentskills.io), not from the Claude Code docs, and both bind when the skill is packaged or uploaded — see `references/frontmatter-reference.md` §1.1.

**Names that silently don't work:**

- `anthropic-skills`, or any name starting with `anthropic-skills:` — reserved for skills synced from claude.ai. Outside a plugin, a skill folder, a frontmatter `name`, a command file or a saved workflow with that name **doesn't load** (a startup notice names it). A *plugin* named `anthropic-skills` still loads.
- A skill folder named `synced`, in any capitalization — `~/.claude/skills/synced/` is where claude.ai skills are downloaded, so a skill you author under that name is skipped in the enterprise, personal and project locations.
- A folder or file name with hidden, direction-changing or blank-like characters (zero-width, bidi marks), `<` or `>` — the skill is not offered until renamed, and a frontmatter `name` with them is ignored (v2.1.299+, changelog 2.1.299). A `name` longer than 256 characters is ignored too (v2.1.292+).

**A name with side effects:** when the project or user skills include one named `verify`, Claude is told to run it right before every commit (except docs-only and tests-only commits; v2.1.286+). Name a skill `verify` only if that is exactly what you want.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic — concrete, specific, with file paths, personal context, abbreviations, typos, casual speech. Focus on edge cases rather than clear-cut ones.

For **should-trigger** queries (8-10): different phrasings of the same intent, some formal, some casual. Include cases where the user doesn't explicitly name the skill but clearly needs it.

For **should-not-trigger** queries (8-10): near-misses that share keywords but need something different. Don't make them obviously irrelevant.

### Step 2: Review with user

Present the eval set using the HTML template:

1. Read `assets/eval_review.html`
2. Replace placeholders: `__EVAL_DATA_PLACEHOLDER__` → JSON array, `__SKILL_NAME_PLACEHOLDER__` → name, `__SKILL_DESCRIPTION_PLACEHOLDER__` → description
3. Write to temp file and open: `open /tmp/eval_review_<skill-name>.html`
4. User edits queries, toggles should-trigger, exports to `~/Downloads/eval_set.json`

### Step 3: Run the optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

This splits evals 60/40 train/test, evaluates trigger rates (3 runs each), calls Claude with extended thinking to propose improvements, and iterates up to 5 times. Best description is selected by test score to avoid overfitting.

**Measurement caveats.** `run_eval.py` checks whether Claude invokes a *synthetic* copy of the skill it registers in a temp directory. The `claude -p` subprocess also sees the installed copy of the same skill and any skills synced from the claude.ai account (v2.1.275+), which compete with the synthetic one — an invocation of the installed copy is not counted, so the trigger rate can read low. For a skill that ships in a plugin, measure triggering with the native eval instead (`references/eval-mode.md` §"Native plugin eval"): a case per natural phrasing with a `tool_used: Skill` grader, `--ablation none`, `max_turns: 2`. Re-run the same suite after each description change.

### Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's frontmatter. Show before/after and report scores.

### How skill triggering works

Skills appear in Claude's available skills list with name + description. Claude only consults skills for tasks it can't easily handle alone — simple one-step queries may not trigger. Eval queries should be substantive enough that Claude would benefit from consulting a skill.
