# Sandboxing Notes for Skill Authors

> Last audited against Claude Code docs: 2026-11-09 (v2.1.321, mirror 39e6937e)

Why this matters: **a skill that runs bash must not assume it has network access
or an unrestricted filesystem.** The user's sandbox settings decide, not the
skill. Design bash steps to fail loudly and explain what to allow, rather than
hanging or silently producing empty output.

## Settings that change what a skill's bash can do

- **`sandbox.network.strictAllowlist`** (v2.1.219+): when `true`, sandboxed
  commands are *denied* access to hosts outside the allowlist (`allowedDomains`
  + `WebFetch(domain:...)` allow rules) instead of prompting. A skill's `curl`
  to an unlisted host fails with no prompt shown. Only honored from user,
  managed, or CLI `--settings` sources — a skill cannot ship it in project
  settings. In-process tools (WebFetch) are not gated by it.
- **Credential masking, `"mode": "mask"`**: env vars (v2.1.199+) and credential
  files on Linux/WSL (v2.1.221+) can be masked — the sandboxed command sees a
  sentinel value while the proxy substitutes the real one on egress. On macOS,
  *file* masking falls back to `deny`: a skill reading a masked credential file
  there gets nothing. Don't design a skill around reading credentials from disk.
- **`--restricted` / `CLAUDE_CODE_RESTRICTED=1`** (v2.1.248+): a stricter mode than
  sandboxing — it *removes* the built-in tools that run commands or code, plus
  `WebFetch` unless named in `--tools`, keeps file tools inside the working
  directory, refuses `bypassPermissions`, and ignores user, project, and local
  settings files. A skill whose steps shell out has no Bash at all there, not a
  denied Bash. Detect and say so instead of assuming the command silently failed.
- **`sandbox.filesystem.disabled`** (v2.1.216+): skips filesystem isolation
  while keeping network egress control. The inverse also holds — filesystem
  isolation may be ON, so a skill's script must not assume it can write outside
  the working directory.
- **`sandbox.excludedCommands` matches the whole call** (v2.1.314 corrected the
  setting's description): a Bash or Monitor call leaves the sandbox only when an
  entry covers **every** command in it — `npm ci && docker compose build` stays
  sandboxed under a lone `docker compose *` entry (`sandboxing.md:327-331`;
  `changelog.md:527`). A skill step that chains a setup command in front of an
  excluded tool runs sandboxed; split the call. Since v2.1.309 an excluded command
  asks before writing to the sandbox's write-list paths while the sandbox is enabled
  but can't run, and the unsandboxed fallback is refused there (`changelog.md:804`).
- **Shell startup files (v2.1.309+):** on macOS and Linux a sandboxed Bash command's
  shell startup files now run inside the sandbox too, not outside it before each
  command (`changelog.md:821`). A skill that relied on a profile reaching outside
  the sandbox loses that.
- **`sandbox.allowNestedUserNamespaces`** (v2.1.305+, Linux/WSL2, user or managed
  settings only): lets sandboxed commands create user namespaces, which Chromium and
  rootless podman need — and lets them get around the sandbox's file protections
  (`sandboxing.md:563`; `changelog.md:962`). A skill that drives headless Chromium on
  Linux may need it; say so rather than ask for the sandbox off.
- **`permissions.blockWritesOutsideWorkingDirectories`** (v2.1.314+): `Write`,
  `Edit` and `NotebookEdit` refuse paths outside the working directories in every
  permission mode, `bypassPermissions` included; shell commands, MCP tools and hook
  programs are not limited by it (`settings-reference.md:1099-1101`;
  `changelog.md:455`). A skill that writes its report to `~/` or `/tmp` with the
  file tools fails there — write inside the project, or `/add-dir` the target.
- **Nested skills under the sandbox (v2.1.319+):** with the Bash sandbox on, a skill in
  a `.claude/skills` folder below the starting folder loads only if Claude Code starts
  there or the user `/cd`s there (`changelog.md:49`; docs not yet updated). A monorepo package skill can be absent
  for a sandboxed user; say where to start the session.

## Authoring rules

1. Network-dependent steps: name the host(s) the skill needs in SKILL.md so the
   user can allowlist them; handle the denied case with a clear message.
2. Never bake in reads of `~/.aws`, `~/.config/gh`, or similar credential paths
   — masked or denied under sandboxing, and a red flag in review either way.
3. Test the skill once with sandboxing enabled before shipping if its scripts
   touch the network or write outside the skill's own workspace.
