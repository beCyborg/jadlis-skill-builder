## Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

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

### Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's frontmatter. Show before/after and report scores.

### How skill triggering works

Skills appear in Claude's available skills list with name + description. Claude only consults skills for tasks it can't easily handle alone — simple one-step queries may not trigger. Eval queries should be substantive enough that Claude would benefit from consulting a skill.
