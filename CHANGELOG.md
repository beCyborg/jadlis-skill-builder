# Changelog — jadlis-skill-builder

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
