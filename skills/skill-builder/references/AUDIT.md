# Audit Registry

Central ledger for keeping this skill's references aligned with Claude Code.
Update this file on every release that touches doc-derived content.

## Audit markers

Nine version-dense files carry a `> Last audited against Claude Code docs:` line;
the other references change rarely and are covered by release-time grep instead.
(`schemas.md` joined the list in v1.8.0: 7 versioned claims and a mirror in 8 of
the SYNC facts below — the one file that could drift silently.)

| File | Last audited | CC version |
|---|---|---|
| `references/frontmatter-reference.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/orchestration-guide.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/agent-authoring.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/plugin-packaging.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/skill-lifecycle.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/environments.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/sandboxing.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/schemas.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |
| `references/model-routing.md` | 2026-11-09 | v2.1.321 (mirror 39e6937e) |

Note: the 2026-10-02 audit read the mirror's changelog 2.1.257–2.1.287 in full and
checked the name semantics by hand on an installed 2.1.287 (a project skill in folder
`probe-dir` with `name: probe-name` answers to both `/probe-name` and `/probe-dir`).
The 2026-10-14 audit read the mirror's changelog 2.1.288–2.1.299 in full (the mirror
has no 2.1.297, 2.1.298 or 2.1.300 entry; the installed CLI is 2.1.300). Facts the docs
pages don't carry yet — agent `autoCompactWindow` bounds, the eval case field
`disallowed_tools` — were read from `claude plugin eval --help` and the 2.1.300 CLI.
The 2026-10-17 audit read the mirror's changelog 2.1.301–2.1.302 in full and the
diff 305bb5ef..da8a6ce9 of `skills.md`, `sub-agents.md`, `hooks.md` and
`plugins__components.md` (installed CLI 2.1.302). It re-dated only the four marked
files it touched; the rest keep their 2026-10-14 marker. Two facts still live only
in the changelog: the 64-name / 64-char argument limit (2.1.301) and `updatedInput`
validation (2.1.300).
The 2026-11-04 audit read the mirror's changelog 2.1.303–2.1.318 in full (mirror
8f02c497, `changelog.md:175-1107`) and re-derived every `page.md:line` citation in
the references by grepping the quoted text at that head — the docs moved from MDX
to plain markdown, which shifted most line numbers. All nine marked files were
re-dated. Fork mode: `sub-agents.md:1278` and `env-vars.md:306` now say "on by
default", so the 2.1.302 docs-lag caveat is gone. Docs and changelog disagree on
four facts, and the references keep both statements with their sources:
`prompt`/`agent` hook concurrency (`hooks.md:407` — 12 per event — vs changelog
2.1.312 — 24 per session plus 12 past their timeout); a subagent's
`autoCompactWindow` under `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (`sub-agents.md:1197` —
no effect — vs 2.1.312 — lowers it); a flagged request in a subagent under "Ask each
time" (`model-config.md:569` at 8f02c497 — re-runs on the fallback model — vs 2.1.318 —
stops); the effort of a subagent on a different model (`model-config.md:727` —
only "the session level doesn't apply" — vs 2.1.317 — that model's saved level or
its default). Changelog-only facts, marked "docs not yet updated":
`CLAUDE_CODE_SUBAGENT_EFFORT` and `CLAUDE_CODE_DISABLE_ULTRATHINK` (2.1.316),
`onFailure: "block"` for SDK hook callbacks (2.1.317), Monitor commands and hooks
(2.1.314), the skill-list resend after compaction and `/reload-skills` delta
(2.1.304), workflow resume after a usage limit and 3-minute shell backgrounding in
background subagents (2.1.318). The Agent tool's alias-only `model` parameter
(`sub-agents.md:355`) carries no version in docs or changelog.
The 2026-11-09 audit (installed CLI 2.1.321; there is no 2.1.320) read the mirror's
changelog 2.1.319 in full (mirror 39e6937e, `changelog.md:12-173`) and the GitHub
CHANGELOG entry for 2.1.321, which the docs changelog page doesn't carry yet — those
facts are cited as `changelog 2.1.321`, without a line. A script moved every unchanged
`page.md:line` citation from 8f02c497 to 39e6937e; the 15 whose cited text had changed
were re-read by hand. `model-config.md`, `advisor.md` and `prompt-caching.md` were
read live, because the mirror didn't describe Fable 5.2 yet, and their citations use
the live line numbers. Docs diffs read: `skills.md`, `hooks.md`, `hooks-guide.md`,
`model-config.md`, `agent-teams.md`, `sandboxing.md`, `permissions.md`, `headless.md`,
`best-practices.md`, `prompt-caching.md`, `env-vars.md`, `settings-reference.md`,
`agent-sdk__hooks.md`, `plugins__cli-reference.md`, `plugins__marketplace-reference.md`;
`sub-agents.md`, `workflows.md`, `plugins__components.md`, `plugin-evals.md` and the
mirror's `advisor.md` did not change. The effort guidance in `model-routing.md` §5
comes from Anthropic's "Prompting Claude Fable 5.2" and the Fable 5.2 migration guide
(platform.claude.com, read 2026-11-09), cited by title and section. All nine marked
files were re-dated. Resolved: the flagged-request conflict — `model-config.md:585-592`
now documents that a subagent fails under "Ask each time" (v2.1.318+); Monitor
commands and hooks (`hooks.md:388-396`) and `PreCompact` stdout (`hooks.md:3367-3369`)
reached the docs; SDK `onFailure: "block"` was already in `agent-sdk__hooks.md:291` at
8f02c497, so that caveat was stale. Still in conflict, both statements kept: hook
concurrency (`hooks.md:407`), a subagent's `autoCompactWindow` under the variable
(`sub-agents.md:1197`), the effort of a subagent on a different model
(`model-config.md:727`). Changelog-only, marked "docs not yet updated": nested-skill
loading under the Bash sandbox and `permissions.denyInsteadOfPrompting` (2.1.319), plus
the earlier `CLAUDE_CODE_SUBAGENT_EFFORT`, `CLAUDE_CODE_DISABLE_ULTRATHINK`, skill-list
resend and `/reload-skills` delta, workflow resume after a usage limit and 3-minute
shell backgrounding. Every 2.1.321 fact (Bamum-letter names, nested skills inside
`~/.claude/plugins`, the `git stash` fix, the workflow stop/pause notice) is
changelog-only until the docs changelog page catches up. Upstream `skill-creator` is
still frozen (last change 2026-04-23).

## SYNC registry — facts duplicated across files

Each fact has one canonical location; the mirrors repeat it where it is applied.
When the fact changes, update the canon first, then every mirror.

| Fact | Canon | Mirrors |
|---|---|---|
| 1,536-char cap on combined `description` + `when_to_use` (`skillListingMaxDescChars`) | `frontmatter-reference.md` §1 `description` row | `frontmatter-reference.md` §7; `SKILL.md` (Frontmatter, Context Budget); `schemas.md` (frontmatter block); `description-optimization.md` (checklist); `quick_validate.py` (limit + error text); `init_skill.py` (template comment); `improve_description.py` (budget math + prompt text) |
| Scheduled-task footgun: `disable-model-invocation: true` blocks runs by a session-scoped scheduled task (v2.1.196; `skills.md:402`) | `orchestration-guide.md` §7 (architecture 7 footgun) | `frontmatter-reference.md` §1 + §2; `SKILL.md` (Invocation control); `schemas.md`; `house-style.md`; `creation-interview.md` |
| Reserved / built-in command names to avoid (incl. `design` v2.1.234+, `workflow-authoring` v2.1.248+, aliases `checkup`/`proactive`); names that don't load (`anthropic-skills[:*]`, folder `synced`); `verify` runs before every commit (v2.1.286) | `description-optimization.md` §"Naming the skill" | `SKILL.md` (Frontmatter `name` bullet — pointer only, no list); `environments.md` (synced skills); `quick_validate.py` (reserved-name checks) |
| Fork background default + narrower tool set + `/rewind` gap (v2.1.218; since mirror da8a6ce9 rewind restores only files Claude had already edited; `sed -i` and other Bash edits are not restored, v2.1.309) | `frontmatter-reference.md` §5 | `frontmatter-reference.md` §1 (`context`/`background` rows); `orchestration-guide.md` (architectures 2, 3); `SKILL.md` (Orchestration); `schemas.md`; `init_skill.py` |
| Agent-tool limits: 20 concurrent / depth 3; no per-session total (the 200 cap was removed in v2.1.224, `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` is a no-op) | `orchestration-guide.md` (architecture 3) | — (Workflow-tool 16/1,000 caps are a *different* fact, same file, architecture 4) |
| Skill-declared hooks live to the END of the session (registered on invocation; only `once: true` removes one early, after its first *successful* run) | `frontmatter-reference.md` §6 | `frontmatter-reference.md` §1 (`hooks` row); `SKILL.md` (optional-field list); `schemas.md`; `orchestration-guide.md` (architecture 6 caveat); `creation-interview.md` (Stage 4 guardrails); `init_skill.py` (template comment) |
| Skill-hook limits (v2.1.304): per source (project, personal folder, each plugin) and session at most 1,024 hooks and 16,384 matcher chars, else the skill registers none (`registers none of its hooks` in the debug log); under a plugin-only `hooks` policy a personal/project skill with `hooks` also loses its `allowed-tools` pre-approval | `frontmatter-reference.md` §6 ("Limits on skill hooks") | `frontmatter-reference.md` §1 (`hooks` + `allowed-tools` rows); `schemas.md` (frontmatter block, `hooks` line) |
| `prompt`/`agent` hook concurrency: docs 12 per event at once (`hooks.md:407`) vs changelog 2.1.312 24 per session incl. subagents + 12 past their timeout, `timeout` < 1 s counts as 1 s — keep both | `frontmatter-reference.md` §6 (Runtime limits) | `orchestration-guide.md` (architecture 6) |
| Portability allowlist: outside Claude Code only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`; any other field = hard error on upload/packaging; on that path `description` is capped at 1,024 characters (`quick_validate.py --portable`, `DESCRIPTION_MAX`) | `frontmatter-reference.md` §1.1 | `schemas.md` (`[portable]` tags); `environments.md` (Cowork/cloud); `quick_validate.py` (CC-mode warning / `--portable` hard error); `package_skill.py` (packaging gate); `init_skill.py` (template comment); `SKILL.md` (portability paragraph) |
| `name` sets the command: personal/project skill → `/<name>` **and** `/<dir>` both work; plugin skill → `name` replaces the last command segment (`skills/review/` + `name: fancy` → `/my-plugin:fancy`, v2.1.216+; prefix not doubled v2.1.246+); portable packaging still requires name = dirname, kebab-case (agentskills.io spec); an `--add-dir` skill whose name clashes runs as `/<folder>:<name>` (v2.1.309+) | `frontmatter-reference.md` §1 `name` row | `schemas.md`; `SKILL.md` (Frontmatter `name` bullet; `--add-dir` line); `quick_validate.py` (mode-dependent name checks); `description-optimization.md` (64-cap attribution) |
| Task tools are not always present (v2.1.268+: on by default only on the allowlist Claude 3.x / Opus 4–4.7 / Sonnet 4–4.6 / Haiku 4.5; off on newer or unrecognized models) — every task instruction must be gated on availability | `task-tracking.md` (availability section) | `SKILL.md`:65; `coordinator.md` (responsibility 4); `eval-mode.md`; `improve-mode.md` (benchmark-mode.md carries no task instructions — keep it that way) |
| `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}`: plugin skills only, substituted in the body and in `allowed-tools` | `frontmatter-reference.md` §3 (variable table) | `schemas.md` (variable table); `plugin-packaging.md` |
| Cache cost: frontmatter `model:` ≠ session model = model switch, no cache hits that turn; effort change keeps the cache on Fable 5.1 and later / Opus 5.5 / Sonnet 5.5 / Haiku 5.5 with API key or subscription (per docs for `/effort`) | `model-routing.md` | `frontmatter-reference.md` §1 `model` row + §4; `SKILL.md` (Reasoning depth); `orchestration-guide.md` (Pinning models) |
| `compatibility` is a current portable field, max 500 chars (Agent Skills spec) | `frontmatter-reference.md` §1 `compatibility` row | `schemas.md` (frontmatter block); `quick_validate.py` (500-char check) |

## Release checklist

1. `git -C ~/.claude-code-docs log -1 --format=%cs` — confirm the docs mirror is fresh; skim `changelog.md` releases since the version in the markers above.
2. Apply content changes; update the audit markers + the table above.
3. `python3 -m scripts.quick_validate --self-test` and `python3 -m scripts.quick_validate .` — both green. Optionally run `/doctor prompt-audit` (v2.1.283+) over the skill and its agents — a cheap lint for prompting patterns written for older models and stale paths.
4. `claude plugin validate <marketplace-root> --strict` — zero errors. That run only reads `marketplace.json` plus the `plugin.json` of each entry; it never opens the skill files. Add `claude plugin validate <plugin-dir>` and `claude plugin validate skills/` for frontmatter coverage.
5. Grep the SYNC registry facts — every mirror consistent with its canon. If the plugin carries `evals/` cases, run them with `claude plugin eval .` (recipe: `eval-mode.md` §"Native plugin eval") — triggering regressions show up here, not in `validate`.
6. Bump the version in `.claude-plugin/plugin.json` — the single source of truth. Do **NOT** duplicate it in the `.claude-plugin/marketplace.json` entry: when both set `version`, `plugin.json` wins silently and the marketplace copy only masks drift.
7. Commit, push, then tag with `claude plugin tag --push` (convention `{plugin-name}--v{version}`, i.e. `jadlis-skill-builder--v2.0.0` — the form plugin dependency resolution understands; the old `vX.Y.Z` tags stay as history). Then `claude plugin update jadlis-skill-builder@jadlis`. Never run `/plugin` operations before the push — marketplace autoUpdate can wipe uncommitted edits.
8. Do ALL editing in a dev clone (`~/jadlis-skill-builder`), never in `~/.claude/plugins/marketplaces/<marketplace>/` — the background marketplace refresh resets that clone to origin (it deleted a local *branch* on 2026-09-01; any `claude` start, including headless `claude -p`, can trigger it). Push the working branch early.

## Rejected decisions (do not re-propose without new evidence)

- **Per-category `/usage` metrics in eval/benchmark modes** (planned v1.5.0, dropped v1.7.0): `/usage` attribution was still being fixed as of 2.1.222 — surface too unstable to build on.
- **Physical dedup of shared facts** (each number lives in exactly one file): rejected — the 1,536 cap is needed at the point of use; an extra Read per number is a bad trade. The SYNC registry above is the compromise.
- **Audit markers in all 22 references**: rejected — drifts apart in practice; markers only in the version-dense files listed above.
- **Strict validator mirroring Claude Code's schema**: rejected (v1.5.0 precedent) — `quick_validate` is an authoring guardrail; `claude plugin validate` is the canon. *Not* the same as `--portable` (v1.8.0): portable mode does not mirror Claude Code's schema — it mirrors the **upload path** (claude.ai / Skills API / packaging), where a non-allowlisted field is a hard error by definition. The default Claude Code mode stays guardrail-soft.
- **Reverting to the official upstream `skill-creator`** (Anthropic's marketplace plugin this one is forked from): upstream frozen since 2026-04-23 and behind this fork.
