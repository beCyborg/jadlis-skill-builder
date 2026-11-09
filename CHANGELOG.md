# Changelog — jadlis-skill-builder

## [2.5.0] — 2026-11-09 — скиллы под Fable 5.2 и сверка с Claude Code 2.1.321 / skills for Fable 5.2, references aligned with Claude Code 2.1.321

### Для человека

- Плагин учит писать скиллы под Fable 5.2 по гайду Anthropic. Новый скилл получает правило «доведи до конца» и список точных действий, перед которыми надо спросить. В режиме улучшения появился чек-лист, как перенести скилл на новую модель.
- Справочники знают Claude Code 2.1.319–2.1.321. Fable 5.2 стартует на effort `medium`, alias `best` теперь ведёт на Opus, вложенные скиллы под песочницей грузятся иначе, у хуков новые правила.
- Проверка переносимого скилла отклоняет описание длиннее 1 024 символов. Тесты скилла запускают исполнителя на том effort, с которым скилл выходит.

### For agents

- Added: `references/skill-writing-craft.md` — five craft points from Anthropic's "Prompting Claude Fable 5.2" (read 2026-11-09): keep reasoning out of the output (`reasoning_extraction` refusal; "think less" lines don't work at `medium`+), give a rule its scope, reason and exception, describe the reader instead of capping the style, price delegation, say who owns the code. Also: references one level deep, table of contents from 100 lines (was 300) — Skill authoring best practices.
- Added: `references/improve-mode.md` — "Carrying a skill to a new model" checklist before Setup Phase; the improve step may merge and delete lines, not only append; a go-ahead is required before the best version overwrites the user's original skill.
- Changed: `scripts/init_skill.py` template — Run contract names the exact actions that need a go-ahead (a TODO the author fills) and the steps that need none; new **Obstacles** line (ordinary obstacle vs deliberate blocker); final report written for a reader who saw no tool calls; `effort:` comment says when to set it and where. `references/house-style.md` lists the new parts.
- Added: `SKILL.md` — own `## Run contract` (keep going inside a mode, obstacles, the three stop points); a no-skill baseline run before drafting (Capture Intent); `description` guidance: complete trigger contexts instead of louder wording; `ultrathink` list adds Fable 5.2; the cache note on inline `effort:` now matches `model-routing.md` §2.
- Changed: `agents/executor.md` — nobody can answer during an eval run: take the recommended option, record it, never send/post/pay/delete outside `output_dir`, finish in one turn. `agents/analyzer.md` — suggestion category `removal`. `references/coordinator.md` #11 and `references/delegating-work.md` — analysis and subagents run on the session's model and effort unless pinned; executors don't get the skill's frontmatter.
- Added: `references/eval-mode.md`, `references/benchmark-mode.md` — pass the skill's shipped level as the executors' Agent-call `effort`; re-run the effort sweep after a model change (one benchmark per level). `references/orchestration-guide.md` — "Cost first" paragraph before the decision matrix. `references/creation-interview.md` — Stage 4 item 5 "Approvals".
- Added: `scripts/quick_validate.py` — `DESCRIPTION_MAX = 1024` on the portable path (`--portable` fails a longer `description`; Claude Code mode unchanged), two fixtures (50 total on Python 3.10+). Mirrors: `references/frontmatter-reference.md` §1.1, `SKILL.md` (Portability check), `references/AUDIT.md` SYNC row.
- Changed: `scripts/improve_description.py` — the optimizer prompt asks for a third-person description ("Processes X. Use when ..."), as `description-optimization.md` and the template already did; `references/description-optimization.md` no longer says "extended thinking".
- Changed: `references/model-routing.md` — Fable 5.2 throughout: Claude Code default `medium` for Fable 5.2 / Opus 5.5 / Sonnet 5.5 / Haiku 5.5 (`model-config.md:636`) kept apart from the Claude API default `high`; cache kept on an effort change on "Fable 5.1 and later" (`prompt-caching.md:36,95-97`); advisor pairs (`advisor.md:101-105`); `fable` → Fable 5.2, `best` = `opus` since v2.1.321, saved `claude-fable-5-1` moves to `fable` in user settings (`model-config.md:33,51,74-79,1118-1119`); "Flagged requests in subagents" rewritten from the new docs section (`model-config.md:582,585-592`) plus the 2.1.319 retry-narrower note (`changelog.md:52`); §5 gains "which level for which work", behaviour at a level and the re-run-the-sweep rule (Prompting Claude Fable 5.2 §Calibrate effort).
- Changed: `references/frontmatter-reference.md` — `name` row: Bamum-letter names refused (changelog 2.1.321); `allowed-tools` row: path patterns on `Write`/`NotebookEdit`/`Glob`/`Grep` never match (`permissions.md:356-363`); `effort` row and §4 `ultrathink` list (`model-config.md:630-636,703-707`); §6: `AskUserQuestion`/`ExitPlanMode` need `updatedInput` with `allow` (`hooks.md:2028-2038,2169`), Monitor matcher and `PreCompact` output now cited from docs (`hooks.md:388-396,3367-3369`), `PostToolUse` after an interrupt (v2.1.319, `hooks.md:2233-2243`), no hooks under `--bare` (`headless.md:61`); §8 nested skill loading (`skills.md:181`, `changelog.md:49`, changelog 2.1.321).
- Changed: `references/orchestration-guide.md` (lost background reports and `/tasks` "Earlier in this session" — `changelog.md:32,159`; workflow stop/pause notice — changelog 2.1.321; SDK `onFailure` cites `agent-sdk__hooks.md:291`; `permissions.denyInsteadOfPrompting` — `changelog.md:21`), `references/agent-authoring.md`, `references/skill-lifecycle.md` (project skills/agents reappear after `git stash` — changelog 2.1.321), `references/sandboxing.md` (nested skills under the Bash sandbox), `references/plugin-packaging.md` (update installs new dependencies — `changelog.md:117,157`; "Validate a manifest file" — `plugins__cli-reference.md:634-642`), `references/description-optimization.md` (Bamum-letter names).
- Changed: every `page.md:line` citation re-derived at mirror 39e6937e by script and verified by line text (222 unchanged targets, 61 re-read by hand); `model-config.md`, `advisor.md`, `prompt-caching.md` cite the live pages read 2026-11-09 (the mirror has no Fable 5.2 text yet). Audit markers of all nine files and the `references/AUDIT.md` table → 2026-11-09 / v2.1.321 / mirror 39e6937e; audit note added; cache-cost SYNC row reads "Fable 5.1 and later".
- Changed: `.claude-plugin/plugin.json` version 2.4.2 → 2.5.0.

## [2.4.2] — 2026-11-09 — тесты скилла снова получают критерии / eval runs receive their expectations again

### Для человека

- Исправлена ошибка подготовки тестов. Если критерии записаны так, как их создаёт сам плагин (`expectations`), проверяющие раньше получали пустой список и ставили «0 из 0». Теперь критерии доходят до них.
- Если у теста нет критериев, скрипт подготовки предупреждает об этом прямо.

### For agents

- Fixed: `skills/skill-builder/scripts/prepare_eval.py` — `normalize_eval` now reads the canonical `expectations` key (what `init_json.py` writes and `validate_json.py` checks); `assertions` and gym `expected_behavior` stay as legacy fallbacks. Before, an `expectations`-only eval produced `"assertions": []` in `eval_metadata.json` silently, so graders had nothing to grade.
- Added: stderr warning `this eval has no expectations` when the list is empty.
- Added: `eval_metadata.json` carries `eval_number` (the eval's own `id`) and `eval_name` next to `eval_id` (still the 0-based CLI index), so graders stop mixing up eval 0 and eval 1.
- Changed: `.claude-plugin/plugin.json` version 2.4.1 → 2.4.2.

## [2.4.1] — 2026-11-06 — репозиторий снова на GitHub beCyborg / repository back on GitHub beCyborg

### Для человека

- Плагин снова живёт на GitHub: https://github.com/beCyborg/jadlis-skill-builder. Каталог ставится командой `claude plugin marketplace add https://github.com/beCyborg/jadlis-hub.git`.
- Работа плагина не изменилась, поменялись только адреса.

### For agents

- Changed: README pair, `docs/employee*.md`, `.claude/CLAUDE.md`, `.claude-plugin/plugin.json` and legacy `marketplace.json` owner — GitLab/becyb-org → `github.com/beCyborg`.
- Changed: `skills/skill-builder/references/plugin-packaging.md` — house marketplace URL is `https://github.com/beCyborg/jadlis-hub.git`.
- Changed: CI `.gitlab-ci.yml` → `.github/workflows/ci.yml` (reusable `beCyborg/jadlis-hub` plugin-ci).
- Changed: `.claude-plugin/plugin.json` version 2.4.0 → 2.4.1.

## [2.4.0] — 2026-11-04 — справочники сверены с Claude Code 2.1.318, основной дом — GitHub becyb-org / references aligned with Claude Code 2.1.318, primary home moved to GitHub becyb-org

### Для человека

- Справочники знают о правилах Claude Code 2.1.303–2.1.318. `ultrathink` в терминале теперь может поднять ход до `xhigh`. У хуков скилла есть лимит на источник. Субагент на другой модели берёт effort этой модели.
- Где документация и журнал изменений расходятся, справочник приводит оба утверждения с источниками. Так сделано для лимита хуков, `autoCompactWindow` и смены модели у субагента.
- Плагин теперь живёт на GitHub: https://github.com/becyb-org/jadlis-skill-builder. Команда установки не изменилась и берёт каталог из хаба на GitLab.

### For agents

- Changed: `references/frontmatter-reference.md` — `ultrathink` (§4): in-context instruction always; since v2.1.311 the word typed at the interactive terminal can raise the turn's API effort to `xhigh` on Opus 5.5 / Sonnet 5.5 / Haiku 5.5 / Fable 5.1 via Anthropic's API, not on Bedrock, never above `CLAUDE_CODE_EFFORT_LEVEL` / `maxEffortLevel` / org cap, not inside quotes/paths/commands or `/` prompts, mid-turn raises the rest of the turn, VS Code v2.1.316, `CLAUDE_CODE_DISABLE_ULTRATHINK` (`model-config.md:679-685`; `changelog.md:491,238,222`). §1 rows: `name` — `--add-dir` clash → `/<folder>:<name>` (v2.1.309, `skills.md:196-203,447`); `description` — `&lt;`/`&gt;` display (`skills.md:1232-1234`); `allowed-tools` — plugin-only `hooks` policy drops the pre-approval (v2.1.304, `skills.md:634-640`, `settings-reference.md:4168`); `effort` — rest of the current turn, fork's run with `context: fork`, five-step session order (`skills.md:407`, `model-config.md:608-614,699-701`); `paths` — relative to cwd, outside never matches (`skills.md:412`), `cd` fix v2.1.312; `hooks` — per-source limits; `disable-model-invocation` — session-scoped scheduled task (`skills.md:402`). §5: `sed -i` not restored by `/rewind` (v2.1.309), Bash edits after a file-tool edit are (`checkpointing.md:76`). §6: hook concurrency docs (12 per event, `hooks.md:398`) vs changelog 2.1.312 (24 per session + 12 past timeout) — both kept; Monitor commands and `if` (v2.1.314); output cap and PreCompact cut (`hooks.md:1050-1054`, v2.1.314); new "Limits on skill hooks" block (1,024 hooks / 16,384 matcher chars per source, `registers none of its hooks`, `hooks.md:684-695`); `once` cross-skill fix (v2.1.304).
- Changed: `references/model-routing.md` §1 — skill `effort:` turn-scoped with the session order; Agent-call `model` parameter takes aliases only (`sub-agents.md:355`, no version); subagents/teammates on a different model use that model's saved effort or default (v2.1.317, docs only say the session level doesn't apply); `CLAUDE_CODE_SUBAGENT_EFFORT` (v2.1.316); flagged requests in subagents stop under "Ask each time" (v2.1.318) vs `model-config.md:569` (re-runs on fallback) — both kept. §2 Haiku 5.5 keeps the cache on an effort change; §3 advisor pairs re-read (Haiku 5.5 can be an advisor, a refused pair takes effect after `/clear`/`/compact`).
- Changed: `references/agent-authoring.md` — effort for a different model and `CLAUDE_CODE_SUBAGENT_EFFORT`; `autoCompactWindow` vs `CLAUDE_CODE_AUTO_COMPACT_WINDOW` docs (`sub-agents.md:1197`) vs changelog 2.1.312 — both kept, env var `k`/`M` suffixes (v2.1.304); `SendMessage` by ID, subagent `name` only with agent teams (`sub-agents.md:968,1132`); background subagents background a shell command after 3 min (v2.1.318); plan-mode main conversation keeps subagents in plan mode (`sub-agents.md:590-595`); alias-only spawn `model`; `blockWritesOutsideWorkingDirectories` refuses worktree-subagent edits outside working dirs (v2.1.314, `settings-reference.md:1129-1132`).
- Changed: `references/orchestration-guide.md` — fork mode on by default everywhere, docs-lag caveat dropped (`sub-agents.md:1271-1278`, `env-vars.md:303`); parallel forks told which launch is theirs (v2.1.307); architecture 4 resume rules (`workflows.md:366-380`), v2.1.305 and v2.1.318 resume fixes; architecture 6 SDK callback `onFailure: "block"` (v2.1.317), hook concurrency both statements; architecture 7 session-scoped footgun.
- Changed: `references/skill-lifecycle.md` (skill list resent after compaction, `/reload-skills` sends only new/changed — v2.1.304), `references/sandboxing.md` (`excludedCommands` whole-call match, excluded-command writes, startup files, `allowNestedUserNamespaces`, `blockWritesOutsideWorkingDirectories`), `references/plugin-packaging.md` (monitors on Bedrock/Vertex/Foundry v2.1.310, `@skills-dir` plugins blocked by managed settings `plugins__loading.md:95-102`, plugin agents list `autoCompactWindow`), `references/schemas.md`, `references/description-optimization.md`, `references/environments.md`, `SKILL.md` (`--add-dir` prefix, ultrathink).
- Changed: every `page.md:line` citation in `references/` re-derived at mirror 8f02c497 (docs moved from MDX to markdown); audit markers of all nine files and the `references/AUDIT.md` table → 2026-11-04 / v2.1.318 / mirror 8f02c497; audit note for changelog 2.1.303–2.1.318; SYNC rows for skill-hook limits and hook concurrency, `--add-dir` naming, Haiku 5.5 cache, session-scoped scheduled tasks.
- Changed: hosting → GitHub `becyb-org`: `.claude-plugin/plugin.json` `homepage`/`repository`, `.claude-plugin/marketplace.json` `owner.url`/`homepage`, `docs/employee*.md`, `references/plugin-packaging.md`, `.claude/CLAUDE.md`; README pair gains a source link (no new H2). Install commands keep the hub URL `https://gitlab.com/beCyborg/jadlis-hub.git`.
- Changed: `.claude-plugin/plugin.json` version 2.3.1 → 2.4.0.

## [2.3.1] — 2026-10-17 — справочники сверены с Claude Code 2.1.302, plugin-creator стал plugin-builder / references aligned with Claude Code 2.1.302, plugin-creator renamed plugin-builder

### Для человека

- Соседний плагин `plugin-creator` теперь называется `plugin-builder`, команда — `/plugin-builder`. Я обновил ссылки в README, статье и справочниках.
- Справочники знают о новых правилах Claude Code 2.1.300–2.1.302: Claude Code запускает форк-агентов и в `claude -p`, связка скиллов работает только в терминале, `/rewind` откатывает правки фонового форка лишь частично.
- Раздел про хуки предупреждает о трёх ловушках: проверку `updatedInput`, лимит в 12 хуков одного события и фоновый процесс внутри хука.

### For agents

- Changed: `references/orchestration-guide.md` — architecture 2 disambiguation: fork mode (`subagent_type: "fork"`) on by default in `claude -p`, Agent SDK, desktop, VS Code since v2.1.302, `CLAUDE_CODE_FORK_SUBAGENT=0` turns it off, `claude mcp serve` never offers it (changelog 2.1.302; `sub-agents.md:1247` still says off); `/rewind` restores only files Claude had already edited. Architecture 3: desktop/VS Code always background the main conversation's subagents, a subagent's own Agent calls run in the foreground in `-p`/SDK/desktop/VS Code (v2.1.302). Architecture 6: `updatedInput` validation (v2.1.300), 12 concurrent `prompt`/`agent` hooks per event (v2.1.302), background process in a hook (`hooks.md:889-893`). Citations `hooks.md:904` → `910`, `sub-agents.md:422-433` → `426-437`.
- Changed: `references/frontmatter-reference.md` — §2 stacked invocation only at the terminal prompt, `-p`/SDK load the first skill only (`skills.md:693-695`); §3 only the first 64 argument names, each up to 64 chars, are filled in (v2.1.301); §5 `/rewind` after a background fork restores only files Claude had already edited (`skills.md:810`, `checkpointing.md:87`); §6 runtime limits block (`updatedInput`, 12-hook cap, suspect-capture), `hooks.md:904` → `910`.
- Changed: `references/agent-authoring.md` — `--debug` string `does not recognize or apply` (`sub-agents.md:301`); `autoCompactWindow` now documented (`sub-agents.md:313,1170-1187`: env var wins, `200k` reads as 200, `invalid autoCompactWindow` in the debug log), listed among plugin-agent fields (`plugins__components.md:739`); MCP whole-server entries per `sub-agents.md:480-486`; shifted line citations.
- Changed: `references/plugin-packaging.md`, `.claude/CLAUDE.md`, `README.md`, `README.en.md`, `docs/employee.md`, `docs/employee.en.md` — `plugin-creator` → `plugin-builder` (`/plugin-builder`, `gitlab.com/beCyborg/jadlis-plugin-builder`); `SKILL.md` Orchestration — partial `/rewind` coverage.
- Changed: audit markers of the four touched references and the `references/AUDIT.md` table → 2026-10-17 / v2.1.302 / mirror da8a6ce9; audit note for changelog 2.1.301–2.1.302; SYNC row of the fork `/rewind` gap.
- Changed: `.claude-plugin/plugin.json` version 2.3.0 → 2.3.1.

## [2.3.0] — 2026-10-14 — справочники сверены с Claude Code 2.1.300 / references aligned with Claude Code 2.1.300

### Для человека

- Плагин теперь ставится одной командой: `claude plugin install jadlis-skill-builder --marketplace https://gitlab.com/beCyborg/jadlis-hub.git`. Нужен Claude Code 2.1.292 или новее; старая пара команд осталась в README для старых версий.
- Справочники знают о новых правилах Claude Code 2.1.288–2.1.300: effort при запуске агента, ранняя компакция агента, лимиты имён и предзагрузки скиллов, хуки, которые блокируют при сбое.
- Нативный eval умеет убирать встроенные инструменты из прогона, например `Agent`. Скилл подсказывает, когда это нужно.

### For agents

- Added: `references/agent-authoring.md` — `effort` semantics (Agent-tool `effort` parameter per launch beats the definition, persists on resume, `CLAUDE_CODE_EFFORT_LEVEL` beats both; v2.1.292, `sub-agents.md:316,421`); `autoCompactWindow` field (v2.1.296; integer 100000–1000000, only lowers the inherited window, read from the 2.1.300 CLI); 256-char agent-name cap (v2.1.292); MCP entries in `tools:`/`disallowedTools:` reach only the named server, `mcp__<whole name>__*` for names with `__` (v2.1.299); `skills:` preloads at most 32 (v2.1.295); `--debug` names unknown agent fields (v2.1.296).
- Added: `references/frontmatter-reference.md` — `name` row: 256-char cap (v2.1.292), hidden/bidi/blank-like chars and `<` `>` in `name:` or the folder/file name (v2.1.299); §4: `!` commands with raw control chars refused (v2.1.290), `UserPromptSubmit` runs before skill expansion (v2.1.299); §6: a skill's own `UserPromptSubmit` hook first runs on the next prompt (v2.1.299), `onFailure: "block"` after the exit-code rule (v2.1.295).
- Added: `references/model-routing.md` §1 — subagent effort order with the Agent-tool `effort` parameter; Workflow row: `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` (v2.1.296), `workflows.md` citation 423 → 453.
- Added: `references/orchestration-guide.md` — hook row of "Which form?" and architecture 6: `onFailure: "block"` for `command`/`http` hooks (v2.1.295, `hooks.md:904`).
- Added: `references/eval-mode.md` + `SKILL.md` (Eval Mode) — `claude plugin eval --disallow-tools` and case field `disallowed_tools` (`prompt.md` frontmatter or `execution.disallowed_tools` in `case.yaml`, merged; v2.1.299); API-error runs score 0 and exit 1 (v2.1.299).
- Added: `references/plugin-packaging.md` — one-command `claude plugin install <p> --marketplace <source>` (v2.1.292) with the two-command fallback; `validate` README install-line advice (v2.1.295).
- Added: `references/description-optimization.md` §"Names that silently don't work" — hidden/bidi chars and `<` `>` (v2.1.299), >256-char `name` (v2.1.292).
- Changed: `README.md` / `README.en.md` — install via `--marketplace`, two-command pair kept as fallback for CC < 2.1.292.
- Changed: audit markers of the nine version-dense references and the `references/AUDIT.md` table → 2026-10-14 / v2.1.300 / mirror 305bb5ef; audit note for changelog 2.1.288–2.1.299.
- Changed: `.claude-plugin/plugin.json` version 2.2.3 → 2.3.0.
- Changed: repo conventions moved `CLAUDE.md` → `.claude/CLAUDE.md` — since CC 2.1.289 `claude plugin validate .` also checks the root plugin, and a root `CLAUDE.md` failed `--strict` ("not loaded as project context"). Claude Code still loads it as project context from `.claude/`.

## [2.2.3] — 2026-10-08 — репозиторий переехал на GitLab / repository moved to GitLab

### Для человека

- Плагин теперь живёт на GitLab: https://gitlab.com/beCyborg/jadlis-skill-builder. Аккаунт GitHub beCyborg заблокирован, поэтому старые ссылки открывают 404.
- Каталог ставится новой командой: `claude plugin marketplace add https://gitlab.com/beCyborg/jadlis-hub.git`. Если ты уже ставил его со старой ссылки GitHub, удали каталог командой `claude plugin marketplace remove jadlis` и поставь всё заново по README. Плагины этого каталога при удалении тоже снимутся.
- Работа плагина не изменилась.

### For agents

- Changed: every `github.com/beCyborg/*` link in README pairs, `docs/employee` pair, the legacy root `marketplace.json`, `references/plugin-packaging.md` and `CLAUDE.md` now points to `gitlab.com/beCyborg/*`; `marketplace add` uses the full `https://…/jadlis-hub.git` URL (non-GitHub hosts have no `owner/repo` shorthand).
- Changed: `.claude-plugin/plugin.json` `homepage`/`repository` → GitLab; version 2.2.2 → 2.2.3.
- Changed: CI moved from `.github/workflows/ci.yml` (reusable workflow in `beCyborg/jadlis-hub`) to `.gitlab-ci.yml` including `/ci/plugin-ci.yml` from `beCyborg/jadlis-hub` on GitLab — same checks: `claude plugin validate --strict`, gitleaks full history, README parity, privacy grep.

## [2.2.2] — 2026-10-02 — effort во frontmatter скилла сбрасывает кэш (замер) / skill `effort:` busts the cache (measured)

### Для человека
- Проверили на деле: если у обычного (не вынесенного в субагента) скилла стоит свой `effort:`, на этом ходу почти весь кэш разговора считается заново. Документация обещает обратное только для команды `/effort`. Совет теперь прямой: свой effort — только у скиллов с `context: fork` и у агентов.

### For agents
- Changed: `skills/skill-builder/references/model-routing.md` — «not separately verified» replaced by the measurement (CC 2.1.287, Opus 5.5, subscription, `claude -p --resume`, n=1 per arm: `effort: low` skill turn cache_read 11.8K / write ~43K vs control 51.3K / 2.5K) and the rule «no `effort:` on inline skills».
- Changed: `references/frontmatter-reference.md` — `effort` row points to the measurement.
- Changed: `.claude-plugin/plugin.json` version 2.2.1 → 2.2.2.

## [2.2.1] — 2026-10-02 — исправлена ссылка на документацию / fixed a docs reference

### Для человека
- Протокол сверки с документацией ссылался на страницу, которой больше нет; теперь — на актуальные страницы про плагины.

### For agents
- Fixed: `skills/skill-builder/references/research-protocol.md` — `plugins-reference.md` (gone from the docs mirror) → `plugins__manifest-reference.md` and `plugins__components.md`.
- Changed: `.claude-plugin/plugin.json` version 2.2.0 → 2.2.1.

## [2.2.0] — 2026-10-02 — сверка с Claude Code 2.1.287: имя скилла, нативные эвалы, выбор формы, роутинг моделей / alignment with Claude Code 2.1.287: skill naming, native evals, choosing the form, model routing
### Для человека
- Правило «имя скилла = имя папки» снято: в 2.1.287 личный или проектный скилл вызывается и по полю `name`, и по имени папки; валидатор предупреждает про запрещённые имена (`anthropic-skills`, папка `synced`) и про скилл `verify`, который запускается перед каждым коммитом.
- Скилл из плагина теперь проверяется нативным `claude plugin eval` (рецепт триггер-кейсов, в самом плагине — два таких кейса); новое руководство «что выбрать»: скилл, хук, мод, MCP, output style, `/goal`, субагент или Workflow — с ограничениями модов.
- Новый справочник `model-routing.md`: откуда берутся модель и effort, что сбрасывает кэш, советник и допустимые пары, полные ID вместо алиасов, как подобрать effort; личные настройки читаются из `~/.claude/skills/_shared/model-routing.md`, если он есть.
### For agents
- Added: `skills/skill-builder/references/model-routing.md` — general layer only (source priority for inline skill / `context: fork` / subagent / Workflow `agent()` / teammate; cache cost of `model:` vs `effort:`; advisor pairs; full IDs vs aliases; effort calibration); ends with the gate line to `~/.claude/skills/_shared/model-routing.md`. Linked from `SKILL.md` (Orchestration, Reasoning depth, Benchmark, reference list), `orchestration-guide.md` (Pinning models), `agent-authoring.md`, `frontmatter-reference.md`, `benchmark-mode.md`, `house-style.md`.
- Added: `references/orchestration-guide.md` §"Which form?" — skill / CLAUDE.md / output style / classic hook / mod / MCP / `/goal` + Stop hook / subagent / Workflow, with doc citations; mod limits (v2.1.287+, fail-open, not sandboxed, `skill.prompt` not delivered — anthropics/claude-code#96831). Fork limits (no `AskUserQuestion`/`Workflow`) in architecture 2 and the matrix; teams trap (named subagents become teammates); `skills`/`mcpServers` on teammates; re-ported subagents-vs-teams table; workflow resumable + ultracode note; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`.
- Added: `references/eval-mode.md` §"Native plugin eval" (routing rule plugin → `claude plugin eval`, personal/project → `evals/evals.json`; trigger recipe with `--ablation none`, `max_turns: 2`); `plugin-packaging.md` eval + mods sections; `description-optimization.md` measurement caveats for `run_eval.py`; `evals/ru-trigger-create-skill`, `evals/no-trigger-offtopic` (not run); `.gitignore` `evals/results/`.
- Changed: `name` semantics in `SKILL.md`, `frontmatter-reference.md` §1, `schemas.md`, `description-optimization.md` §"Naming the skill" (+ reserved `anthropic-skills[:*]`, folder `synced`, `verify` before commits), `environments.md` (synced skills lose the short name instead of being skipped); `scripts/quick_validate.py` — comments/warning text, new reserved-name warnings + 4 self-test fixtures (46/46). Behaviour for name ≠ folder unchanged: CC mode passes, `--portable` still fails.
- Changed: `frontmatter-reference.md` — auto mode is the starting mode since v2.1.283 (`allowed-tools` row, `!` injection in auto mode), `model` row (auto/plan-classifier, cache), `effort` row, description fallback = first non-empty line, `shell: powershell` conditions, `${CLAUDE_EFFORT}` + `--effort ultracode` still sets `xhigh` (also `schemas.md`), `/skill-doctor`, `/name` mid-message, `agent` hook not on `PermissionRequest`.
- Changed: task tools as the v2.1.268 allowlist in `task-tracking.md`, `SKILL.md`, `eval-mode.md`, `improve-mode.md`, `coordinator.md`, `AUDIT.md`; Workflow `medium` <10, `small` on Pro, `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`; agent fields `omitClaudeMd`, plugin-agent field list, omitted `model` ≠ `inherit`, `--agents <file>` in `agent-authoring.md` / `plugin-packaging.md`; `validate` MCP checks and `--json`.
- Changed: `house-style.md` heavy-skill pattern points at the `jadlis-research` plugin (no `*-opus-xhigh` agents, no `~/.claude/workflows` copies); benchmark compares models by full ID; audit markers and `AUDIT.md` table → 2026-10-02 / v2.1.287 / mirror 934d35c9, new SYNC row (cache cost), release checklist (+ `/doctor prompt-audit`, `claude plugin eval`).
- Changed: `.claude-plugin/plugin.json` version 2.1.0 → 2.2.0.
- Removed: untracked `skills/skill-builder/scripts/__pycache__/` (already ignored).

## [2.1.0] — 2026-09-23 — скиллы под гайд Opus 5.5: effort вместо ultrathink, блок Run contract / Opus 5.5 guide alignment: effort over ultrathink, Run contract block
### Для человека
- Глубину размышлений скилла теперь задают полем `effort:` во frontmatter, а не словами «ultrathink»/«think hard» в тексте скилла.
- Каждый новый скилл из шаблона получает блок «Run contract»: когда работа считается сделанной, когда продолжать без вопросов и как выглядит финальный отчёт.
- Агенты-оценщики больше не просят «объяснить рассуждения» — только коротко обосновать победителя на конкретных примерах.
### For agents
- Changed: `skills/skill-builder/SKILL.md`, `skills/skill-builder/references/frontmatter-reference.md` — section «Extended Thinking (ultrathink)» → «Reasoning depth (effort, not ultrathink)»: `ultrathink` is a per-turn user-prompt keyword, thinking is always on for Opus 5.5/Fable, skills set depth via `effort:` (per `docs/model-config.md`).
- Changed: `skills/skill-builder/references/improve-mode.md` — dropped «take your time and really mull things over».
- Changed: `skills/skill-builder/agents/comparator.md`, `agents/analyzer.md`, `references/schemas.md`, `scripts/init_json.py` — «Explain your reasoning» → «Justify the winner in 1–3 sentences with specific examples»; JSON keys (`reasoning`, `comparator_reasoning`) unchanged.
- Added: `skills/skill-builder/scripts/init_skill.py` — `## Run contract` section in `SKILL_TEMPLATE` (Done-when as TODO; `{{WORK_DIR}}` escaped for `.format()`).
- Added: `skills/skill-builder/references/house-style.md` — «Run contract» rule for every new skill.
- Changed: `skills/skill-builder/references/skill-writing-craft.md` — report-structure example reordered to Result → «Не удалось подтвердить» → «От тебя:».
- Changed: `.claude-plugin/plugin.json` version 2.0.0 → 2.1.0.

## [2.0.0] — 2026-09-10 — плагин переименован в `jadlis-skill-builder` / plugin renamed to `jadlis-skill-builder`
### Для человека
- Плагин называется `jadlis-skill-builder`: ставится строкой `claude plugin install jadlis-skill-builder@jadlis`, маркетплейс добавляется из хаба `https://github.com/beCyborg/jadlis-hub`.
- Короткая команда `/skill-builder` не изменилась; полная форма стала `/jadlis-skill-builder:skill-builder`.
- Совместимости со старыми именами нет: `renames` в манифесте маркетплейса очищен, установки под прежним именем надо переставить.
### For agents
- Changed: `.claude-plugin/plugin.json` — `name` `skill-builder` → `jadlis-skill-builder`, version 1.9.0 → 2.0.0 (`homepage`/`repository` уже указывали на свой репозиторий).
- Changed: `.claude-plugin/marketplace.json` — запись плагина `skill-builder` → `jadlis-skill-builder`; `renames` → `{}` (было `{"skill-creator": "skill-builder", "plugin-creator": null}`).
- Changed: `.github/workflows/ci.yml` — reusable workflow `beCyborg/jadlis-start/...` → `beCyborg/jadlis-hub/.github/workflows/plugin-ci.yml@main`.
- Changed: `README.md` / `README.en.md` — `marketplace add https://github.com/beCyborg/jadlis-start.git` → `.../jadlis-hub`, все `skill-builder@jadlis` → `jadlis-skill-builder@jadlis`, имя плагина в промпте-установщике.
- Removed: `README.md` / `README.en.md` — финальный абзац про автоматический переезд установок со `skill-creator` (шимов совместимости больше нет).
- Changed: `CLAUDE.md` — имя плагина, клон хаба и пути скриптов `~/jadlis-plugins/tools/` → `~/jadlis-hub/tools/`, ссылка на reusable workflow, описание пустого `renames`.
- Changed: `skills/skill-builder/references/AUDIT.md` — пример тега `jadlis-skill-builder--v2.0.0`, `claude plugin update jadlis-skill-builder@jadlis`.
- Breaking: имя плагина изменилось, старые теги `skill-builder--vX.Y.Z` не подхватываются; папки скиллов и `name: skill-builder` в `SKILL.md` не менялись.

## [1.9.0] — 2026-09-07 — переименование в `skill-builder`, репо `jadlis-skill-builder` / rename to `skill-builder`, repo `jadlis-skill-builder`
### Для человека
- Плагин переименован в `skill-builder`: одноимённый плагин есть в официальном маркетплейсе Anthropic, а два плагина с одним именем делят один неймспейс — команда стала `/skill-builder`.
- Репозиторий переименован в `jadlis-skill-builder`, плагин раздаётся через маркетплейс `jadlis`; `plugin-creator` уехал в собственный репозиторий `jadlis-plugin-creator`.
- Уже сделанные установки продолжают работать: в легаси-`marketplace.json` прописан `renames`.
### For agents
- Changed: `.claude-plugin/plugin.json` — `name` skill-creator → skill-builder, version 1.8.1 → 1.9.0, `displayName` added, `homepage`/`repository` → `https://github.com/beCyborg/jadlis-skill-builder`.
- Changed: `skills/skill-creator/` → `skills/skill-builder/`; entry skill frontmatter `name: skill-builder`. Command `/skill-creator:skill-creator` → `/skill-builder`.
- Changed: `.claude-plugin/marketplace.json` — marketplace `name` stays `skill-creator-plugin` (legacy installs), single entry `skill-builder` → `./`, `"renames": {"skill-creator": "skill-builder", "plugin-creator": null}`.
- Removed: `plugins/plugin-creator/` — the plugin now lives in `beCyborg/jadlis-plugin-creator` at 1.1.0 (no diverging copies).
- Changed: CI — `.github/workflows/plugin-validate.yml` replaced by `.github/workflows/ci.yml` calling `beCyborg/jadlis-start/.github/workflows/plugin-ci.yml@main` with `mode: marketplace`, `forbid-mermaid: false`.
- Changed: `README.md` / `README.en.md` / `docs/employee*.md` / `CLAUDE.md` — install via `claude plugin install skill-builder@jadlis` from `https://github.com/beCyborg/jadlis-start.git`, plugin-creator links point at its own repo.
- Migration: `claude plugin marketplace update` picks up the rename automatically; a fresh install is `claude plugin install skill-builder@jadlis`.

## [1.8.1] — 2026-09-06 — README RU/EN, docs/employee, формат CHANGELOG, gitleaks в CI / bilingual READMEs, docs/employee, changelog format, gitleaks in CI
### Для человека
- Появились README на русском и английском: зачем, как выглядит, как поставить, как пользоваться, границы.
- Добавлен разбор «Claude Code как сотрудник» — скилл, хуки, память, доступы простым языком.
- Репозиторий приведён к домашнему стандарту: CHANGELOG в общем формате, конвенции в CLAUDE.md, проверка на утечку ключей в CI.
### For agents
- Added: `README.md` + `README.en.md` (5 sections + Плагины/Обновление/Лицензия), `docs/employee.md` + `docs/employee.en.md`, `docs/img/08-employee-01..04.webp`, `CHANGELOG.md`, `CLAUDE.md`.
- Added: `gitleaks` job in `.github/workflows/plugin-validate.yml` (`gitleaks/gitleaks-action@v2`, `fetch-depth: 0`).
- Changed: `.claude-plugin/plugin.json` version 1.8.0 → 1.8.1, `homepage` added, author email dropped; `.claude-plugin/marketplace.json` owner email replaced with `url`.
- Migration: none — docs and metadata only, skill behaviour unchanged.

## [1.8.0] — 2026-09-01 — сверка с Claude Code 2.1.252 и переносимость скиллов / alignment with 2.1.252 and skill portability
### Для человека
- Скилл понимает, какие поля переживают выгрузку наружу, и не даёт собрать непереносимый пакет.
- Обновлены разделы про хуки, оркестрацию и учёт задач под свежую версию Claude Code.
### For agents
- Added: six-field portability allowlist (`references/frontmatter-reference.md` §1.1), `--portable` mode in `scripts/quick_validate.py`, refusal in `scripts/package_skill.py`, `references/schemas.md` portability tags.
- Changed: hooks lifetime (session-scoped), 33-event table, exit-2 semantics; orchestration notes (200-cap removal, `subagent_type: fork`, `CLAUDE_CODE_SUBAGENT_MODEL`); task-tracking availability gates for Opus 4.8 / Sonnet 5 / Fable 5 / Mythos 5+.
- Changed: `references/plugin-packaging.md` — `skills` adds rather than shadows, validate scope, command-source versioning; `references/AUDIT.md` markers moved to 2026-09-01.
- Changed: scripts read BOM-tolerantly, self-test grew 14 → 31 fixtures.

## [1.7.0] — 2026-08-05 — сверка с Claude Code 2.1.222, мягкий валидатор / alignment with 2.1.222, softer validator
### Для человека
- Валидатор перестал ронять проверку из-за незнакомых полей — теперь это предупреждение.
- Руководство по написанию скиллов вынесено в отдельный файл, SKILL.md стал короче.
### For agents
- Fixed: `scripts/package_skill.py` works both as `python -m scripts.package_skill` and by direct path.
- Changed: `scripts/quick_validate.py` — unknown keys warn instead of fail, spec-key normalization, `_as_bool`, `--self-test` (14 fixtures).
- Added: `references/AUDIT.md` (audit + SYNC registry), `references/sandboxing.md`, `references/skill-writing-craft.md` (offloaded from SKILL.md).
- Changed: `references/frontmatter-reference.md` (background field, boolean literals, `skillListingMaxDescChars`), `references/orchestration-guide.md` (Agent-tool limits 20/200/depth 3).

## [1.6.0] — 2026-07-16 — сверка с Claude Code 2.1.211, eval-конвейер / alignment with 2.1.211, eval workflow
### Для человека
- Прогон тестов скилла и разбор результатов собраны в один рабочий цикл.
### For agents
- Changed: eval workflow ported from upstream (`references/eval-mode.md`, `agents/executor.md`, `agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md`).
- Changed: references aligned with Claude Code 2.1.211.

## Более ранние версии

История 1.1.0 → 1.5.0 велась только в git: `git log --oneline` в этом репозитории.
