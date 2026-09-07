# Integration Testing for Skills with Live External Dependencies

> Adapted from upstream proposal anthropics/skills#1265 (closed unmerged; reworked
> for this fork). Optional — reach for it only when a skill depends on live
> external systems: MCP connectors, CLIs, browser DOM, host filesystems, remote
> APIs. File-based evals alone miss integration-seam failures (auth expiry, schema
> drift, rate limits, DOM changes).

## TESTS.md capability matrix

Keep a `TESTS.md` state file next to SKILL.md listing each externally-dependent
capability as a row with one of four states:

| State | Meaning |
|---|---|
| `PASS` | Exercised against the live dependency; behaved as specified |
| `FAIL` | Exercised; broken — the row links to the failure note |
| `CODED-NOT-VERIFIED` | Written but never run against the live system |
| `NOT-TESTED` | Known capability, no test exists yet |

Example:

```markdown
# TESTS.md — <skill-name>
| Capability | State | Last run | Notes |
|---|---|---|---|
| Search via connector X | PASS | 2026-06-30 | 3 queries, schema stable |
| Pagination past page 2 | CODED-NOT-VERIFIED | — | needs a >50-item corpus |
| Auth refresh on 401 | NOT-TESTED | — | |
```

`CODED-NOT-VERIFIED` is the state that earns the matrix its keep: it makes the
difference between "written" and "verified" visible instead of letting untested
code pass as done.

## Gate

`TESTS.md` ends with a **Gate** section naming which rows must be `PASS` before
the skill is reinstalled, published, or version-bumped. Rows outside the gate are
allowed to lag; rows inside it block release. Re-run gate rows after any change to
the skill's external-facing steps, not just after changes to the tested capability.

## Offline regression fixtures

For each gated capability, check in **one captured live response** as a fixture
(`tests/fixtures/<capability>.json`, secrets stripped). The offline check replays
the skill's parsing/handling against the fixture without touching the live
system — it catches regressions in your handling and, when a later live run
diverges from the fixture, flags upstream schema drift. Refresh a fixture only
deliberately (the diff is signal), never automatically.

## Cadence

- Live gate rows: before install/publish/bump, and after auth or dependency
  changes.
- Offline fixture replay: every improvement iteration — it is cheap enough to run
  alongside regular evals.
