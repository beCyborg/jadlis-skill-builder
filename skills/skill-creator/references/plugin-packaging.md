# Distributing a Skill as a Plugin

`scripts/package_skill.py` produces a `.skill` file — the quick path for handing one skill to one person. For anything that needs to be **shared with teammates, versioned, updated over time, or published**, wrap the skill in a **plugin** inside a **marketplace**. (This skill-creator ships exactly that way.)

## Standalone vs plugin — which to use

| Use standalone `.claude/skills/<name>/` when… | Wrap in a plugin when… |
|---|---|
| One skill, one project or one machine | Multiple skills/agents/commands/hooks shipped together |
| Quick personal helper | You want versioned updates users pull via a marketplace |
| No distribution needed | Sharing publicly or org-wide, or namespacing to avoid collisions |

## Plugin layout

Component directories live at the **plugin root** — never inside `.claude-plugin/`. Only the manifests go in `.claude-plugin/`.

```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json          # required manifest
│   └── marketplace.json     # if this repo is also the marketplace
├── skills/
│   └── my-skill/SKILL.md    # → invoked as /my-plugin:my-skill
├── agents/                  # optional
├── commands/                # optional
└── hooks/                   # optional
```

A plugin with a **root-level `SKILL.md`** and no `skills/` subdir is auto-loaded as a single-skill plugin (v2.1.142+); there, the frontmatter `name` sets the command. Plugin skills are namespaced `plugin-name:skill-name`, so `/my-plugin:my-skill` cannot collide with other levels.

> **Don't set component keys in `plugin.json` unless you mean to override defaults.** Declaring `"skills": [...]` *shadows* the default `skills/` directory; if you must list it, point at a **directory**, not a file (`claude plugin validate` flags file paths). Omit `commands`/`agents`/`skills`/`hooks` to use the default folders.

## plugin.json (minimal)

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin provides.",
  "author": { "name": "you" }
}
```

- A top-level `$schema` is accepted (v2.1.120+) if you want editor autocomplete; check the current docs for the canonical URL before adding one.
- `themes` and `monitors` must be nested under `"experimental": { ... }` (top-level still works but warns).
- `defaultEnabled: false` (v2.1.154+) ships the plugin disabled; users enable it with `/plugin` or `claude plugin enable`. Dependencies of enabled plugins stay enabled automatically.

## marketplace.json

Lives in `.claude-plugin/marketplace.json`. For a single-repo plugin, point `source` at `./`:

```json
{
  "name": "my-marketplace",
  "owner": { "name": "you" },
  "plugins": [
    { "name": "my-plugin", "version": "1.0.0", "source": "./", "description": "…" }
  ]
}
```

`$schema`, `version`, and `description` are also accepted at the top level of `marketplace.json` (v2.1.120+).

## Version semantics (this is the one people get wrong)

- Setting `version` in `plugin.json` **pins** the plugin: users get **no updates** until you bump it. Omit `version` and Claude Code falls back to the git commit SHA (so every push ships).
- When both `plugin.json` and the marketplace entry set `version`, **`plugin.json` wins**.
- **Bump the version on every release.** Editing a SKILL.md but forgetting to bump `plugin.json` means nobody receives the change.

## Validate before publishing

```bash
claude plugin validate <path>     # primary validator
```

- Pointed at a **marketplace directory**, it checks `marketplace.json` only.
- Pointed at a **plugin directory**, it checks `plugin.json` plus the skill/agent/command/hook frontmatter and `hooks/hooks.json`.
- Add `--strict` in CI to turn unrecognized-field warnings into errors before you publish.

Use `scripts/quick_validate.py <skill-dir>` for a fast local SKILL.md smoke check during authoring.

## Distribution notes

- Test a local plugin with `--plugin-dir <path>` (accepts a `.zip`), or fetch one for a session with `--plugin-url <url>`.
- `skipLfs` on `github`/`git` marketplace sources skips Git LFS during clone/update; `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` helps environments without SSH keys.
- `claude plugin prune` (and `uninstall --prune`) removes orphaned auto-installed dependencies.
