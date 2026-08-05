# Environment Notes: Claude.ai and Cowork

> Last audited against Claude Code docs: 2026-08-05 (v2.1.222)

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
