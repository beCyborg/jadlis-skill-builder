# skill-creator-plugin — конвенции репо

Два плагина в одном маркетплейсе `skill-creator-plugin`: `skill-creator` лежит в корне (root-as-plugin, скиллы в `skills/`), `plugin-creator` — в `plugins/plugin-creator/`. Плагины раздаются и через хаб `jadlis`. Эти правила читает агент, который правит и коммитит репозиторий.

## Коммиты

- Тема — Conventional Commits на английском: `type(scope): subject`, ≤72 символа. `scope` = `skill-creator`, `plugin-creator`, `docs`, `ci` или `repo`.
- Тело двухслойное: `Что изменилось:` — 1–3 предложения по-русски для человека; `Details (for agents):` — буллеты `Added / Changed / Removed / Migration / Refs` с путями.
- Без строк атрибуции (`Co-Authored-By` и подобных).

## Релизы

- Версия живёт только в `plugin.json` (`.claude-plugin/plugin.json` для skill-creator, `plugins/plugin-creator/.claude-plugin/plugin.json` для plugin-creator); в записи маркетплейса версии нет.
- Бамп — в том же коммите, что и изменение: версия = ключ кеша обновлений. Правка README внутри папки плагина тоже считается изменением плагина; docs-only → patch.
- Тег `{plugin}--v{X.Y.Z}`: `claude plugin tag --push .` для skill-creator, `claude plugin tag --push plugins/plugin-creator` для второго.
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

Своих `tools/` в репозитории нет — скрипты берутся из соседнего клона хаба `jadlis-plugins`:

```bash
python3 ~/jadlis-plugins/tools/readme-parity.py .        # H2-паритет, mermaid, ссылки
python3 ~/jadlis-plugins/tools/privacy-grep.py .         # ключи, почты, личные пути
python3 ~/jadlis-plugins/tools/release-notes.py . --title
claude plugin validate .
claude plugin validate plugins/plugin-creator
claude plugin validate .claude-plugin/marketplace.json
```

## Приватность

- В файлах нет ключей, почт, телефонов, путей владельца (`/Users/<имя>` → писать `~`) и упоминаний приватного бэкапа.
- Перед пушем локально: `gitleaks git .` и `privacy-grep.py`. В CI (`.github/workflows/plugin-validate.yml`) гоняются валидация плагинов, preflight и gitleaks.

## Разработка

- Правки только в рабочем клоне `~/skill-creator-plugin`, никогда в `~/.claude/plugins/marketplaces/` — фоновый рефреш стирает их вместе с локальными ветками.
- Роли не смешивать: содержание скиллов — зона `skill-creator`, упаковка и релизы — `plugin-creator`.
- Язык доков — русский (RU-файл первичен), код и идентификаторы — английский.
