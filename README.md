Русский · [English](README.en.md)

# skill-creator + plugin-creator

Два плагина Claude Code для одной работы: превратить повторяющуюся задачу в скилл — должностную инструкцию для агента — и упаковать готовое в плагин, который ставится одной командой.

## Зачем

Ответ можно скопировать, работу — нет. Пока инструкция живёт в переписке, каждый заход изобретается заново: два одинаковых запроса дают разный формат результата, а адрес, куда класть итог, приходится диктовать каждый раз.

- `skill-creator` пишет скилл: интервью о задаче, выбор архитектуры (инлайн, субагент, workflow, команда агентов), черновик, тесты, правка описания под срабатывание.
- `plugin-creator` упаковывает готовое: репозиторий по домашнему стандарту, валидация, релиз с тегом, миграция старых репозиториев в общий маркетплейс.

Разбор идеи целиком — [«Claude Code как сотрудник»](docs/employee.md).

## Как выглядит

![Рабочее место со спины: человек за столом, перед ним пять панелей, у каждой работает механическая рука, справа стопка готовых листов](docs/img/08-employee-01.webp)

Скилл — это папка с инструкцией: когда включаться, что делать по шагам, чего не делать, куда класть результат.

<details>
<summary>Синтетический пример: создание скилла</summary>

```
> /skill-creator:skill-creator сделай скилл для еженедельного дайджеста отчётов

Триаж: процедура с шагами и явным запуском → скилл подходит.
Вопрос 1/3: откуда берутся отчёты — папка, почта, трекер?
Вопрос 2/3: что должно лежать на выходе — файл, строка в трекере, оба?
Вопрос 3/3: делать тест-кейсы? (выход проверяемый — рекомендую да)

Создано  ~/skills/weekly-digest/
  SKILL.md              frontmatter + 6 шагов
  references/format.md  формат итоговой таблицы
  scripts/collect.py    сбор файлов за неделю
  evals/                3 тест-промпта

Дальше: прогнать eval и посмотреть, где скилл не сработал.
```

</details>

## Как поставить

Основной путь — через хаб `jadlis`. Вставь этот блок агенту:

> Ты — установщик. Выполни ровно эти шаги и ничего сверх них:
> 1. Bash: `claude plugin marketplace add https://github.com/beCyborg/jadlis-plugins.git`
> 2. Bash: `claude plugin install skill-creator@jadlis`
> 3. Bash: `claude plugin install plugin-creator@jadlis`
> 4. Bash: `claude plugin list`
> 5. Скажи мне: какие два плагина появились в списке и с какими версиями.

Руками — те же команды:

```bash
claude plugin marketplace add https://github.com/beCyborg/jadlis-plugins.git
claude plugin install skill-creator@jadlis
claude plugin install plugin-creator@jadlis
```

Альтернатива — маркетплейс этого репозитория, без хаба:

```bash
claude plugin marketplace add https://github.com/beCyborg/skill-creator-plugin.git
claude plugin install skill-creator@skill-creator-plugin
claude plugin install plugin-creator@skill-creator-plugin
```

## Как пользоваться

Три сценария, командами:

1. Новый скилл из повторяющейся работы: `/skill-creator:skill-creator сделай скилл для <задача>` — интервью, черновик, тест-промпты.
2. Замер и правка готового скилла: `/skill-creator:skill-creator прогони eval для ~/skills/<имя>` — прогон, оценка, разбор провалов, применение правки.
3. Упаковка и релиз: `/plugin-creator:plugin-creator упакуй ~/skills/<имя> в плагин`, затем `/plugin-creator:plugin-creator зарелизь плагин` — бамп версии, CHANGELOG, тег, GitHub Release.

Подробности по режимам plugin-creator — [plugins/plugin-creator/README.md](plugins/plugin-creator/README.md).

## Границы и стоимость

- Своих API-ключей и платных сервисов плагины не требуют: работают на подписке Claude Code.
- Benchmark-режим гоняет каждый тест 3 раза на конфигурацию и всегда добавляет прогон без скилла — расход квоты кратный числу конфигураций (тег `skill-creator--v1.8.1`).
- Benchmark требует субагентов; там, где их нет, доступен только режим Eval — по одному тесту.
- Разделение ролей жёсткое: skill-creator не публикует плагины, plugin-creator не пишет содержание скиллов.
- plugin-creator вызывает `git`, `gh` и `claude plugin` — нужен установленный GitHub CLI с авторизацией.

## Плагины

| Плагин | Что делает | Версия | Документ |
|---|---|---|---|
| `skill-creator` | Создание, улучшение, eval и benchmark скиллов; оптимизация описания под срабатывание | 1.8.1 | этот файл, [CHANGELOG](CHANGELOG.md) |
| `plugin-creator` | Сборка, валидация, релиз и миграция плагинов и маркетплейсов | 1.0.2 | [README](plugins/plugin-creator/README.md), [CHANGELOG](plugins/plugin-creator/CHANGELOG.md) |

## Обновление

У сторонних маркетплейсов автообновление выключено по умолчанию — обновлять руками:

```bash
claude plugin update skill-creator@jadlis
claude plugin update plugin-creator@jadlis
```

Из своего маркетплейса — те же команды с суффиксом `@skill-creator-plugin`.

## Лицензия

Apache-2.0, [LICENSE](LICENSE). `skill-creator` основан на одноимённом скилле Anthropic и доработан под домашний стандарт.
