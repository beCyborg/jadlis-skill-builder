# Changelog — jadlis-skill-builder

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
