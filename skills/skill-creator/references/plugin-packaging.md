# Distributing a Skill as a Plugin

> Last audited against Claude Code docs: 2026-09-01 (~v2.1.251, mirror b290425)

`python -m scripts.package_skill` produces a `.skill` file — the quick path for handing one skill to one person. For anything that needs to be **shared with teammates, versioned, updated over time, or published**, wrap the skill in a **plugin** inside a **marketplace**. (This skill-creator ships exactly that way.)

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
│   ├── plugin.json          # optional manifest (name defaults to dir name)
│   └── marketplace.json     # if this repo is also the marketplace
├── skills/
│   └── my-skill/SKILL.md    # → invoked as /my-plugin:my-skill
├── agents/                  # optional
├── commands/                # optional
└── hooks/                   # optional
```

Other default folders exist (`workflows/`, `output-styles/`, `themes/`, `monitors/`, `bin/`, plus `.mcp.json` / `.lsp.json` / `settings.json` at the root) — see the official plugins-reference for the full table. A root `CLAUDE.md` is **not** loaded as context; ship instructions as skills.

A plugin with a **root-level `SKILL.md`**, no `skills/` subdir **and no `skills` manifest field** is auto-loaded as a single-skill plugin (v2.1.142+). Set the frontmatter `name`: without it Claude Code falls back to the **install directory name**, which for a marketplace install is a version string that changes on every update — so in practice `name` is required here. For skills in the `skills/` subdir, `name` replaces only the **last segment** of the command — the plugin prefix stays (v2.1.216+). Plugin skills are namespaced `plugin-name:skill-name`, so `/my-plugin:my-skill` cannot collide with other levels.

> **Don't set component keys in `plugin.json` unless you mean to override defaults.** The fields behave differently:
>
> - **Replace the default folder**: `commands`, `agents`, `workflows`, `outputStyles`, `experimental.themes`, `experimental.monitors`. To keep the default and add more, list it explicitly: `"commands": ["./commands/", "./extras/"]`.
> - **Adds to the default**: `skills` — `skills/` is **always** scanned, and listed dirs load alongside it. (Sole exception: a marketplace entry whose `source` resolves to the marketplace root, where listing specific subdirs *does* replace the scan.)
> - **Own merge rules**: `hooks`, `mcpServers`, `lspServers`.
>
> All paths are relative and start with `./`; `skills` additionally accepts `"."` (the plugin root) as of v2.1.221 — use `"./"` for older versions. A path resolving outside the plugin root is rejected with `path escapes plugin directory` and the plugin loads without that component (extended to marketplace-entry command paths in v2.1.251). A skill path may point straight at a directory containing `SKILL.md`.

## plugin.json (minimal)

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin provides.",
  "author": { "name": "you" }
}
```

- `$schema` is `https://json.schemastore.org/claude-code-plugin-manifest.json` (v2.1.120+). Claude Code **ignores it at load time** — it is for editor autocomplete only, not a CI gate (the published schemas lag the CLI).
- `themes` and `monitors` must be nested under `"experimental": { ... }` (top-level still works but warns).
- `defaultEnabled: false` (v2.1.154+) ships the plugin disabled; users enable it with `/plugin` or `claude plugin enable`. Dependencies of enabled plugins stay enabled automatically. A `defaultEnabled` in the marketplace entry overrides the manifest value.
- `userConfig` declares values Claude Code prompts for at enable time, substituted as `${user_config.KEY}` and exported to hooks as `CLAUDE_PLUGIN_OPTION_<KEY>`. Shell-executed fields reject the substitution. Full canon: plugin-creator reference (in this repo, upcoming).
- `dependencies` declares plugin→plugin requirements, optionally with semver ranges resolved against git tags named `{plugin-name}--v{version}` — without those tags a constraint can't resolve.
- Plugin **agents** support only `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation` (`"worktree"`). `hooks`, `mcpServers`, and `permissionMode` are **not supported** in plugin-shipped agents, for security reasons.

## Path variables

`${CLAUDE_PLUGIN_ROOT}` (install directory — **changes on every update**, never write state there), `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/{id}/`, **survives** updates — put `node_modules`, venvs, caches here), and `${CLAUDE_PROJECT_DIR}`. In shell-form hook and monitor commands, wrap them in double quotes; prefer exec form with `args`.

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

- `$schema`, `version`, and `description` are also accepted at the top level (v2.1.120+), as are `metadata.pluginRoot` (v2.1.239+, resolves bare plugin source names) and `renames` (v2.1.193+, maps a former plugin `name` to its current name or `null`).
- 16 marketplace names are **reserved** for Anthropic (`claude-plugins-official`, `agent-skills`, `healthcare`, …), along with impersonating variants; the check runs on every load, not only on add.
- Seven `source` types: relative path, `github`, `url` (any git host, incl. GitLab/Bitbucket/self-hosted), `git-subdir`, `npm`, `archive` (v2.1.224+), `command` (v2.1.229+). `sha` overrides `ref`.
- `strict` defaults to `true` (`plugin.json` is the authority, the entry supplements it). With `strict: false` the entry is the *entire* definition, and components declared in `plugin.json` become a load-blocking conflict.

## Version semantics (this is the one people get wrong)

- Setting `version` in `plugin.json` **pins** the plugin for every source type **except `command`**, whose version always includes a 12-char hash of what the command produced. Users get **no updates** until you bump it. Omit `version` and Claude Code falls back to the resolved commit SHA (so every push ships) or, for archives, the digest.
- When both `plugin.json` and the marketplace entry set `version`, **`plugin.json` wins silently** — a stale manifest version masks the one in `marketplace.json`. Set it in `plugin.json` only and leave `version` out of the marketplace entry.
- **Bump the version on every release.** Editing a SKILL.md but forgetting to bump `plugin.json` means nobody receives the change.
- Tag releases with `claude plugin tag --push` (convention `{plugin-name}--v{version}`) if anything depends on this plugin.

## Validate before publishing

```bash
claude plugin validate <path>     # primary validator
```

- Pointed at a **marketplace directory**: schema errors, **duplicate plugin names**, **source path traversal**, and — for every entry whose `source` is a local path — that plugin's own `plugin.json`, with a warning when the entry's `version` disagrees with it (findings prefixed `plugins[2] plugin.json →`). It does **not** open the plugins' skill/agent/command/hook files.
- Pointed at a **plugin directory**: `plugin.json`, `hooks/hooks.json`, and the `skills`, `agents`, and `commands` directories **at the plugin root** only. A root-level `SKILL.md` is **not** checked here — to check it, run again naming the containing directory, which must literally be called `skills`. For paths set through component path fields, only *existence* is checked; the files are not read. Symlinks are **not** followed (linked dirs and entries are skipped with a warning; naming a symlinked dir is an error).
- Pointed at a **bare skills/agents/commands directory** (`claude plugin validate .claude/skills`, `~/.claude`, `./my-plugin/agents`) it checks every file there — the way to catch unparseable frontmatter in a plugin that has no manifest yet. Requires v2.1.233+.
- Add `--strict` in CI to turn **all** warnings into errors before you publish. A clean run prints `Validation passed`.
- As of v2.1.221, validation also warns when a marketplace or plugin name would be rejected by Claude Desktop's managed marketplace sync — heed these if the plugin may ever be distributed through managed settings.
- `claude plugin details <name>` shows the component inventory plus projected always-on / on-invoke token cost — useful before shipping a large plugin.

Use `python -m scripts.quick_validate <skill-dir>` for a fast local SKILL.md smoke check during authoring.

## Distribution notes

- `claude plugin init <name>` scaffolds a plugin into `~/.claude/skills/<name>/`; it loads next session as `<name>@skills-dir` with no marketplace and no install step — the cheapest development loop.
- Test a local plugin with `--plugin-dir <path>` (accepts a `.zip`), or fetch one for a session with `--plugin-url <url>`.
- `skipLfs` on `github`/`git` marketplace sources skips Git LFS during clone/update; `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` helps environments without SSH keys.
- `claude plugin prune` (and `uninstall --prune`) removes orphaned auto-installed dependencies.

---

> Deep marketplace operations (sources, headersHelper, renames, release channels, org distribution) are covered by the plugin-creator plugin in this repo; this file stays a minimal packaging guide.
