# Audit Registry

Central ledger for keeping this skill's references aligned with Claude Code.
Update this file on every release that touches doc-derived content.

## Audit markers

Eight version-dense files carry a `> Last audited against Claude Code docs:` line;
the other references change rarely and are covered by release-time grep instead.
(`schemas.md` joined the list in v1.8.0: 7 versioned claims and a mirror in 8 of
the SYNC facts below — the one file that could drift silently.)

| File | Last audited | CC version |
|---|---|---|
| `references/frontmatter-reference.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |
| `references/orchestration-guide.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |
| `references/agent-authoring.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |
| `references/plugin-packaging.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |
| `references/skill-lifecycle.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |
| `references/environments.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |
| `references/sandboxing.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |
| `references/schemas.md` | 2026-09-01 | ~v2.1.251 (mirror b290425) |

Note: installed CLI at audit time was 2.1.252; the docs mirror's changelog stops
at 2.1.251, so ~v2.1.251 is the honest upper bound of what was verified.

## SYNC registry — facts duplicated across files

Each fact has one canonical location; the mirrors repeat it where it is applied.
When the fact changes, update the canon first, then every mirror.

| Fact | Canon | Mirrors |
|---|---|---|
| 1,536-char cap on combined `description` + `when_to_use` (`skillListingMaxDescChars`) | `frontmatter-reference.md` §1 `description` row | `frontmatter-reference.md` §7; `SKILL.md` (Frontmatter, Context Budget); `schemas.md` (frontmatter block); `description-optimization.md` (checklist); `quick_validate.py` (limit + error text); `init_skill.py` (template comment); `improve_description.py` (budget math + prompt text) |
| Scheduled-task footgun: `disable-model-invocation: true` blocks cron runs (v2.1.196) | `orchestration-guide.md` §7 (architecture 7 footgun) | `frontmatter-reference.md` §1 + §2; `SKILL.md` (Invocation control); `schemas.md`; `house-style.md`; `creation-interview.md` |
| Reserved / built-in command names to avoid (incl. `design` v2.1.234+, `workflow-authoring` v2.1.248+, aliases `checkup`/`proactive`) | `description-optimization.md` §"Naming the skill" | `SKILL.md` (Frontmatter `name` bullet — pointer only, no list) |
| Fork background default + narrower tool set + `/rewind` gap (v2.1.218) | `frontmatter-reference.md` §5 | `frontmatter-reference.md` §1 (`context`/`background` rows); `orchestration-guide.md` (architectures 2, 3); `SKILL.md` (Orchestration); `schemas.md`; `init_skill.py` |
| Agent-tool limits: 20 concurrent / depth 3; no per-session total (the 200 cap was removed in v2.1.224, `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` is a no-op) | `orchestration-guide.md` (architecture 3) | — (Workflow-tool 16/1,000 caps are a *different* fact, same file, architecture 4) |
| Skill-declared hooks live to the END of the session (registered on invocation; only `once: true` removes one early, after its first *successful* run) | `frontmatter-reference.md` §6 | `frontmatter-reference.md` §1 (`hooks` row); `SKILL.md` (optional-field list); `schemas.md`; `orchestration-guide.md` (architecture 6 caveat); `creation-interview.md` (Stage 4 guardrails); `init_skill.py` (template comment) |
| Portability allowlist: outside Claude Code only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`; any other field = hard error on upload/packaging | `frontmatter-reference.md` §1.1 | `schemas.md` (`[portable]` tags); `environments.md` (Cowork/cloud); `quick_validate.py` (CC-mode warning / `--portable` hard error); `package_skill.py` (packaging gate); `init_skill.py` (template comment); `SKILL.md` (portability paragraph) |
| Plugin-skill `name` replaces the last command segment (`skills/review/` + `name: fancy` → `/my-plugin:fancy`, v2.1.216+; prefix not doubled v2.1.246+); portable packaging still requires name = dirname, kebab-case (agentskills.io spec) | `frontmatter-reference.md` §1 `name` row | `schemas.md`; `SKILL.md` (Frontmatter `name` bullet); `quick_validate.py` (mode-dependent name checks); `description-optimization.md` (64-cap attribution) |
| Task tools are not always present (off by default on Opus 4.8 / Sonnet 5 / Fable 5 / Mythos 5 and newer) — every task instruction must be gated on availability | `task-tracking.md` (availability section) | `SKILL.md`:65; `coordinator.md` (responsibility 4); `eval-mode.md`; `improve-mode.md` (benchmark-mode.md carries no task instructions — keep it that way) |
| `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}`: plugin skills only, substituted in the body and in `allowed-tools` | `frontmatter-reference.md` §3 (variable table) | `schemas.md` (variable table); `plugin-packaging.md` |
| `compatibility` is a current portable field, max 500 chars (Agent Skills spec) | `frontmatter-reference.md` §1 `compatibility` row | `schemas.md` (frontmatter block); `quick_validate.py` (500-char check) |

## Release checklist

1. `git -C ~/.claude-code-docs log -1 --format=%cs` — confirm the docs mirror is fresh; skim `changelog.md` releases since the version in the markers above.
2. Apply content changes; update the audit markers + the table above.
3. `python3 -m scripts.quick_validate --self-test` and `python3 -m scripts.quick_validate .` — both green.
4. `claude plugin validate <marketplace-root> --strict` — zero errors. That run only reads `marketplace.json` plus the `plugin.json` of each entry; it never opens the skill files. Add `claude plugin validate <plugin-dir>` and `claude plugin validate skills/` for frontmatter coverage.
5. Grep the SYNC registry facts — every mirror consistent with its canon.
6. Bump the version in `.claude-plugin/plugin.json` — the single source of truth. Do **NOT** duplicate it in the `.claude-plugin/marketplace.json` entry: when both set `version`, `plugin.json` wins silently and the marketplace copy only masks drift.
7. Commit, push, then tag with `claude plugin tag --push` (convention `{plugin-name}--v{version}`, i.e. `jadlis-skill-builder--v2.0.0` — the form plugin dependency resolution understands; the old `vX.Y.Z` tags stay as history). Then `claude plugin update jadlis-skill-builder@jadlis`. Never run `/plugin` operations before the push — marketplace autoUpdate can wipe uncommitted edits.
8. Do ALL editing in a dev clone (`~/jadlis-skill-builder`), never in `~/.claude/plugins/marketplaces/<marketplace>/` — the background marketplace refresh resets that clone to origin (it deleted a local *branch* on 2026-09-01; any `claude` start, including headless `claude -p`, can trigger it). Push the working branch early.

## Rejected decisions (do not re-propose without new evidence)

- **Per-category `/usage` metrics in eval/benchmark modes** (planned v1.5.0, dropped v1.7.0): `/usage` attribution was still being fixed as of 2.1.222 — surface too unstable to build on.
- **Physical dedup of shared facts** (each number lives in exactly one file): rejected — the 1,536 cap is needed at the point of use; an extra Read per number is a bad trade. The SYNC registry above is the compromise.
- **Audit markers in all 22 references**: rejected — drifts apart in practice; markers only in the version-dense files listed above.
- **Strict validator mirroring Claude Code's schema**: rejected (v1.5.0 precedent) — `quick_validate` is an authoring guardrail; `claude plugin validate` is the canon. *Not* the same as `--portable` (v1.8.0): portable mode does not mirror Claude Code's schema — it mirrors the **upload path** (claude.ai / Skills API / packaging), where a non-allowlisted field is a hard error by definition. The default Claude Code mode stays guardrail-soft.
- **Reverting to the official upstream `skill-creator`** (Anthropic's marketplace plugin this one is forked from): upstream frozen since 2026-04-23 and behind this fork.
