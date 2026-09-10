# jadlis-skill-builder — конвенции репо

Один плагин `jadlis-skill-builder` в корне (root-as-plugin, скиллы в `skills/`); раздаётся через хаб `jadlis`, легаси-`marketplace.json` со `skill-creator-plugin` оставлен ради режима `mode: marketplace` в CI, `renames` пуст — совместимости со старыми именами нет. `plugin-creator` с 1.1.0 живёт в отдельном репозитории `jadlis-plugin-creator`. Эти правила читает агент, который правит и коммитит репозиторий.

## Коммиты

- Тема — Conventional Commits на английском: `type(scope): subject`, ≤72 символа. `scope` = `skill-builder`, `docs`, `ci` или `repo`.
- Тело двухслойное: `Что изменилось:` — 1–3 предложения по-русски для человека; `Details (for agents):` — буллеты `Added / Changed / Removed / Migration / Refs` с путями.
- Без строк атрибуции (`Co-Authored-By` и подобных).

## Релизы

- Версия живёт только в `.claude-plugin/plugin.json`; в записи маркетплейса версии нет.
- Бамп — в том же коммите, что и изменение: версия = ключ кеша обновлений. Правка README внутри папки плагина тоже считается изменением плагина; docs-only → patch.
- Тег `{plugin}--v{X.Y.Z}`: `claude plugin tag --push .`.
- GitHub Release поверх тега: заголовок и тело — из `CHANGELOG.md` соответствующего плагина.
- `CHANGELOG.md`: `## [X.Y.Z] — YYYY-MM-DD — <кратко по-русски> / <short EN>`, затем `### Для человека` (≤3 буллета) и `### For agents` (`Added / Changed / Removed / Migration / Breaking`, с путями).
- Только patch-forward: никаких force-push, переписывания тегов и релизов.

## README и доки

- Пара `README.md` (RU) + `README.en.md` (EN) в каждой папке с документом. Первая строка RU: `Русский · [English](README.en.md)`; EN: `[Русский](README.md) · English`. Одинаковое число и порядок H2.
- Документ инструмента — 5 секций: **Зачем / Как выглядит / Как поставить / Как пользоваться / Границы и стоимость**; дополнительные H2 (Плагины, Обновление, Лицензия) — после пятой и одинаково в обеих версиях. Списки ≤5 пунктов, первая строка секции — действие, оценок времени не давать.
- Статьи (`docs/employee.md`) 5 секций не держат, но переключатель языка первой строкой обязателен.
- Иллюстрации — `docs/img/*.webp`, примеры вывода синтетические. Каждая картинка просматривается глазами перед коммитом.
- Числа и механика сверяются с кодом плагина; рядом с числом указывается тег.

## Скрипты проверки

Своих `tools/` в репозитории нет — скрипты берутся из соседнего клона хаба `jadlis-hub`:

```bash
python3 ~/jadlis-hub/tools/readme-parity.py .        # H2-паритет, mermaid, ссылки
python3 ~/jadlis-hub/tools/privacy-grep.py .         # ключи, почты, личные пути
python3 ~/jadlis-hub/tools/release-notes.py . --title
claude plugin validate .
claude plugin validate .claude-plugin/marketplace.json
```

## Приватность

- В файлах нет ключей, почт, телефонов, путей владельца (`/Users/<имя>` → писать `~`) и упоминаний приватного бэкапа.
- Перед пушем локально: `gitleaks git .` и `privacy-grep.py`. В CI (`.github/workflows/ci.yml`, переиспользуемый `beCyborg/jadlis-hub/.github/workflows/plugin-ci.yml@main`) гоняются валидация плагинов, gitleaks, privacy-grep и README-паритет.

## Разработка

- Правки только в рабочем клоне, никогда в `~/.claude/plugins/marketplaces/` — фоновый рефреш стирает их вместе с локальными ветками.
- Роли не смешивать: содержание скиллов — зона `skill-builder`, упаковка и релизы — `plugin-creator` (свой репозиторий).
- Язык доков — русский (RU-файл первичен), код и идентификаторы — английский.
