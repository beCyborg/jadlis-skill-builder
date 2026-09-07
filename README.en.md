[Русский](README.md) · English

# skill-builder

A Claude Code plugin that turns recurring work into a skill — a job description for the agent.

The plugin used to be called `skill-creator`; it was renamed to `skill-builder` because a plugin of the same name ships in Anthropic's official marketplace, and two plugins with one name share a single namespace.

## Why

An answer is easy to copy; the work is not. While the instructions live in a chat thread, every run is reinvented: two identical requests produce different output formats, and you have to dictate the destination for the result every single time.

- `skill-builder` writes the skill: an interview about the task, a choice of architecture (inline, subagent, workflow, agent team), a draft, tests, and a description tuned for reliable triggering.
- `plugin-creator` packages the result: a repo built to the house standard, validation, a tagged release, and migration of legacy repos into a shared marketplace. Since 1.1.0 it lives in its own repository — [jadlis-plugin-creator](https://github.com/beCyborg/jadlis-plugin-creator).

The full idea is spelled out in [“Claude Code as an employee”](docs/employee.en.md).

## What it looks like

![Workplace seen from behind: a person at a wide desk facing five panels, a mechanical arm working at each one, a stack of finished sheets on the right](docs/img/08-employee-01.webp)

A skill is a folder with instructions: when to fire, what to do step by step, what not to do, where to put the result.

<details>
<summary>Synthetic example: creating a skill</summary>

```
> /skill-builder build a skill for a weekly report digest

Triage: a multi-step procedure with an explicit trigger → a skill fits.
Question 1/3: where do the reports come from — folder, mail, tracker?
Question 2/3: what should the output be — a file, a tracker row, both?
Question 3/3: add test cases? (verifiable output — recommended yes)

Created  ~/skills/weekly-digest/
  SKILL.md              frontmatter + 6 steps
  references/format.md  layout of the final table
  scripts/collect.py    collects the week's files
  evals/                3 test prompts

Next: run the evals and see where the skill missed.
```

</details>

## Install

The main path goes through the `jadlis` hub. Paste this block to your agent:

> You are an installer. Do exactly these steps and nothing more:
> 1. Bash: `claude plugin marketplace add https://github.com/beCyborg/jadlis-start.git`
> 2. Bash: `claude plugin install skill-builder@jadlis`
> 3. Bash: `claude plugin install plugin-creator@jadlis`
> 4. Bash: `claude plugin list`
> 5. Tell me: which two plugins appeared in the list and at which versions.

By hand — the same commands:

```bash
claude plugin marketplace add https://github.com/beCyborg/jadlis-start.git
claude plugin install skill-builder@jadlis
claude plugin install plugin-creator@jadlis
```

Alternative — this repository's own marketplace, no hub (it carries `skill-builder` only):

```bash
claude plugin marketplace add https://github.com/beCyborg/jadlis-skill-builder.git
claude plugin install skill-builder@skill-creator-plugin
```

## Usage

Three scenarios, as commands:

1. A new skill out of recurring work: `/skill-builder build a skill for <task>` — interview, draft, test prompts.
2. Measuring and fixing an existing skill: `/skill-builder run evals for ~/skills/<name>` — run, grade, analyse failures, apply the fix.
3. Packaging and shipping (a separate plugin): `/plugin-creator package ~/skills/<name> as a plugin`, then `/plugin-creator release the plugin` — version bump, changelog, tag, GitHub Release.

Mode-by-mode detail for plugin-creator lives in its own repository: [jadlis-plugin-creator](https://github.com/beCyborg/jadlis-plugin-creator).

## Limits and cost

- No API keys and no paid services: the plugin runs on the Claude Code subscription.
- Benchmark mode runs every eval 3 times per configuration and always adds a no-skill baseline — quota use scales with the number of configurations (tag `skill-creator--v1.8.1`).
- Benchmark needs subagents; where they are unavailable only Eval mode works, one eval at a time.
- The split of roles is strict: `skill-builder` does not publish plugins, `plugin-creator` does not write skill content.
- plugin-creator shells out to `git`, `gh` and `claude plugin` — an authenticated GitHub CLI is required.

## Plugins

| Plugin | What it does | Version | Docs |
|---|---|---|---|
| `skill-builder` | Creating, improving, evaluating and benchmarking skills; description optimization for triggering | 1.9.0 | this file, [CHANGELOG](CHANGELOG.md) |
| `plugin-creator` | Assembling, validating, releasing and migrating plugins and marketplaces (separate repository) | 1.1.0 | [jadlis-plugin-creator](https://github.com/beCyborg/jadlis-plugin-creator) |

## Update

Third-party marketplaces have auto-update off by default — update by hand:

```bash
claude plugin update skill-builder@jadlis
claude plugin update plugin-creator@jadlis
```

From this repo's own marketplace — `claude plugin update skill-builder@skill-creator-plugin`. Existing `skill-creator@skill-creator-plugin` installs migrate on their own: `marketplace.json` carries a `renames` entry.

## License

Apache-2.0, [LICENSE](LICENSE). `skill-builder` is a fork of Anthropic's official `skill-creator` skill, extended to the house standard.
