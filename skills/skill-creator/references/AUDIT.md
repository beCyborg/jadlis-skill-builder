# Audit Registry

Central ledger for keeping this skill's references aligned with Claude Code.
Update this file on every release that touches doc-derived content.

## Audit markers

Six version-dense files carry a `> Last audited against Claude Code docs:` line;
the other references change rarely and are covered by release-time grep instead.

| File | Last audited | CC version |
|---|---|---|
| `references/frontmatter-reference.md` | 2026-08-05 | v2.1.222 |
| `references/orchestration-guide.md` | 2026-08-05 | v2.1.222 |
| `references/agent-authoring.md` | 2026-08-05 | v2.1.222 |
| `references/plugin-packaging.md` | 2026-08-05 | v2.1.222 |
| `references/skill-lifecycle.md` | 2026-08-05 | v2.1.222 |
| `references/environments.md` | 2026-08-05 | v2.1.222 |
| `references/sandboxing.md` | 2026-08-05 | v2.1.222 |

## SYNC registry — facts duplicated across files

Each fact has one canonical location; the mirrors repeat it where it is applied.
When the fact changes, update the canon first, then every mirror.

| Fact | Canon | Mirrors |
|---|---|---|
| 1,536-char cap on combined `description` + `when_to_use` (`skillListingMaxDescChars`) | `frontmatter-reference.md` §1 `description` row | `frontmatter-reference.md` §7; `SKILL.md` (Frontmatter, Context Budget); `schemas.md` (frontmatter block); `description-optimization.md` (checklist); `quick_validate.py` (limit + error text); `init_skill.py` (template comment) |
| Scheduled-task footgun: `disable-model-invocation: true` blocks cron runs (v2.1.196) | `orchestration-guide.md` §7 (architecture 7 footgun) | `frontmatter-reference.md` §1 + §2; `SKILL.md` (Invocation control); `schemas.md` |
| Reserved / built-in command names to avoid | `description-optimization.md` §"Naming the skill" | `SKILL.md` (Frontmatter `name` bullet — pointer only, no list) |
| Fork background default + narrower tool set + `/rewind` gap (v2.1.218) | `frontmatter-reference.md` §5 | `frontmatter-reference.md` §1 (`context`/`background` rows); `orchestration-guide.md` (architectures 2, 3); `SKILL.md` (Orchestration); `schemas.md`; `init_skill.py` |
| Agent-tool limits: 20 concurrent / 200 per session / depth 3 | `orchestration-guide.md` (architecture 3) | — (Workflow-tool 16/1,000 caps are a *different* fact, same file, architecture 4) |

## Release checklist

1. `git -C ~/.claude-code-docs log -1 --format=%cs` — confirm the docs mirror is fresh; skim `changelog.md` releases since the version in the markers above.
2. Apply content changes; update the audit markers + the table above.
3. `python3 -m scripts.quick_validate --self-test` and `python3 -m scripts.quick_validate .` — both green.
4. `claude plugin validate <marketplace-root> --strict` — zero errors.
5. Grep the SYNC registry facts — every mirror consistent with its canon.
6. Bump the version in **both** manifests: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
7. Commit, tag `vX.Y.Z`, push; then `claude plugin update skill-creator@skill-creator-plugin`. Never run `/plugin` operations before the push — marketplace autoUpdate can wipe uncommitted edits.

## Rejected decisions (do not re-propose without new evidence)

- **Per-category `/usage` metrics in eval/benchmark modes** (planned v1.5.0, dropped v1.7.0): `/usage` attribution was still being fixed as of 2.1.222 — surface too unstable to build on.
- **Physical dedup of shared facts** (each number lives in exactly one file): rejected — the 1,536 cap is needed at the point of use; an extra Read per number is a bad trade. The SYNC registry above is the compromise.
- **Audit markers in all 22 references**: rejected — drifts apart in practice; markers only in the version-dense files listed above.
- **Strict validator mirroring Claude Code's schema**: rejected (v1.5.0 precedent) — `quick_validate` is an authoring guardrail; `claude plugin validate` is the canon.
- **Reverting to the official upstream skill-creator**: upstream frozen since 2026-04-23 and behind this fork.
