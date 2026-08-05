# Sandboxing Notes for Skill Authors

> Last audited against Claude Code docs: 2026-08-05 (v2.1.222)

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
- **`sandbox.filesystem.disabled`** (v2.1.216+): skips filesystem isolation
  while keeping network egress control. The inverse also holds — filesystem
  isolation may be ON, so a skill's script must not assume it can write outside
  the working directory.

## Authoring rules

1. Network-dependent steps: name the host(s) the skill needs in SKILL.md so the
   user can allowlist them; handle the denied case with a clear message.
2. Never bake in reads of `~/.aws`, `~/.config/gh`, or similar credential paths
   — masked or denied under sandboxing, and a red flag in review either way.
3. Test the skill once with sandboxing enabled before shipping if its scripts
   touch the network or write outside the skill's own workspace.
