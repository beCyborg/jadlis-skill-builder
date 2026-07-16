# Environment Notes: Claude.ai and Cowork

The core loop (draft → test → review → improve) is the same everywhere; only the mechanics change.

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
