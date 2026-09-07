English · [Русский](README.md)

# You paste the same instructions into the chat again, and the result comes back in a different shape every time

The procedure gets written down once, as a skill folder: an interview scopes the job, the skill's
architecture is chosen, a draft is written, test prompts are run against it, and the description is
reworked until the skill starts firing on its own.

```
claude plugin marketplace add https://github.com/beCyborg/jadlis-start.git
claude plugin install skill-builder@jadlis
```

No keys needed: the plugin runs on your Claude Code subscription. It is a fork of Anthropic's
official `skill-creator` plugin, renamed — a plugin of the same name ships in Anthropic's
marketplace, and two plugins with one name share a single namespace.

![An instruction folder: steps on top, references on the side, a script below — and a test-prompt run beside it](docs/img/hero-jadlis-skill-builder.webp)

In words: on the left, the repeated job in plain language; on the right, the skill folder — steps,
references, script — and a test-prompt loop that feeds fixes back into the steps.

This is my workbench published as it is, not a product: whatever I stopped using, I removed.

## Before → after

| By hand | With an AI chat | With this plugin |
|---|---|---|
| **Where the procedure lives.** The instructions sit in a chat thread and get pasted again on every run. | It does what you pasted, and by the next time it no longer has it. | It writes the procedure down as a folder: `SKILL.md` with the steps, `references/` for details loaded on demand, `scripts/` for the deterministic part. |
| **When the instructions fire.** Remembering they exist at all is on you. | It fires on your phrasing, and a miss only shows up in the result. | A separate mode reworks the description: it runs queries, watches whether the skill fired, and rewrites the description for triggering. |
| **How you know the skill works.** You judge by the last run you happen to remember. | It rates its own output in the same window that produced it. | It runs test prompts, grades them with a separate role, and puts the result next to a no-skill run: no improvement, no pass. |
| **How a heavy skill is built.** You pick the shape by eye and rebuild it after the first fan-out. | It writes one long prompt: fan-out, background work and schedules do not fit in there. | It walks you through seven architectures with a decision matrix — inline, fork, subagents, thin skill plus workflow, agent team, hooks, schedule. |
| **What survives leaving Claude Code.** The package is built, then the upload fails on an unfamiliar field. | It never warns you about the format limits. | It keeps the list of six fields that live outside Claude Code: the validator warns, and the packager refuses to build something unportable. |

## How it works

![Triage, interview, docs check, draft, test-prompt run, analysis, fixes — and packaging](docs/img/how-jadlis-skill-builder.webp)

Going in — the work you keep repeating by hand, and the result described in plain words.
Inside — triage cuts off what should not be a skill at all, the interview fills the gaps, the draft
is checked against the local docs mirror, and the test-prompt run is placed next to a run without
the skill.
Coming out — a skill folder, the test prompts for it, and an analysis of where it failed.

In words: the job → triage → interview → architecture choice → draft → test-prompt run → grading →
fixes to the description and the steps → packaging.

Inside it holds four roles: the executor runs the skill on a task and hands back a transcript, the
grader checks the result against expectations, the comparator compares two versions blind, the
analyzer explains why one of them won. There are four modes — create, improve, eval and benchmark;
benchmark runs each test three times per configuration and always adds a no-skill run. Triage also
works as a refusal: anything that must apply every time is sent to `CLAUDE.md` or to a hook rather
than into a skill you can skip. The details sit in twenty-four reference files loaded on demand; a
separate `house-style.md` overrides the generic defaults with house conventions, and `AUDIT.md`
keeps the registry of facts duplicated across files together with the date of the last docs check.

## Installing and the first run

**a) Text to paste to an agent.** Copy the whole thing into a Claude Code chat:

```
You are the installer. Install the plugin skill-builder from the jadlis marketplace on this Mac.
Run exactly these commands, verbatim, shortening nothing:
1. claude plugin marketplace add https://github.com/beCyborg/jadlis-start.git
2. claude plugin install skill-builder@jadlis
3. claude plugin list — show me the line about skill-builder and its version.
This plugin needs no keys: it runs on the Claude Code subscription, nothing has to be entered.
Before each command show it to me in full and wait for "yes". If I say "no", do not run it,
tell me what you skipped, and move on.
If a command returns an error, stop, show me the output, and do not move to the next one.
```

**b) Commands by hand.**

```
claude plugin marketplace add https://github.com/beCyborg/jadlis-start.git
claude plugin install skill-builder@jadlis
claude plugin list
```

The first command installs nothing — it adds the marketplace. Only the second one installs, and one
line removes it: `claude plugin uninstall skill-builder@jadlis --keep-data`.

**c) The short command.** Open Claude Code in the folder you work in and type:

```
/skill-builder
```

If it is not found, check the name with `claude plugin list`. After that just state the job: "make a
skill for <the work you keep repeating>" or "run an eval for ~/skills/<name>" — the plugin picks the
mode itself.

## Limits, cost, updating

**What it does not do.** It does not release plugins: the standard repository layout, validation,
version, tag and release belong to its neighbour `plugin-creator`, which lives in its own repository.
It does not turn into a skill what should not be one: a rule that must always apply is routed by
triage into `CLAUDE.md` or a hook. It does not promise triggering — the description is reworked from
runs, and the result is measured again each time. It does not judge matters of taste: where the
output is subjective, test cases are not forced on you and the run is reviewed by hand. Benchmark is
unavailable without subagents — there you are left with eval, one test at a time. And it does not
replace the Claude Code documentation: the draft is checked against the local docs mirror, and where
they disagree, the mirror wins.

**What you need.** No keys and no paid services: everything goes through your Claude Code
subscription. Externally you need `claude` itself — the scripts call it as a subprocess for runs and
description rewriting — and `python3` (the scripts stay on the standard library, there is nothing to
install). A local docs mirror in `~/.claude-code-docs/` is optional: without it the skill falls back
to the official docs, but feature versions are then checked less rigorously. The plugin sets up no
API keys of its own and creates no third-party invoices.

**How tokens get spent.** Creating a skill is a conversation plus file edits, so the spend is light.
It grows with the first run: every test prompt is a separate launch, and a no-skill run always goes
alongside. Benchmark is a heavy run — dozens of subagents out of your quota, because every test is
repeated three times per configuration. Improving takes as many iterations as you allow — you set
that bound up front, not after the fact.

**Upstream.** This is a fork of Anthropic's official `skill-creator` plugin: the original author is
Anthropic, not me. The fork diverged by adding the interview with a triage gate, the guide to seven
architectures, the docs-verification protocol, the portability check, the audit registry and the
house conventions; upstream itself, by the notes in this repository, has been frozen since
2026-04-23.

[уточнить] — this repository carries no direct link to the original's repository.

**Verified where I work:** my Mac, my subscription. Where else this works — [уточнить].

**Terms of use.** A fork of an official Anthropic plugin, licensed Apache-2.0 — the text is in the
[LICENSE](LICENSE) file.

**Updating.** With a third-party marketplace, auto-update is off on your side: until you run the
first command you keep the version you installed.

```
claude plugin marketplace update jadlis
claude plugin update skill-builder@jadlis
claude plugin list
```

Reinstall, if something ended up crooked:

```
claude plugin uninstall skill-builder@jadlis --keep-data && claude plugin install skill-builder@jadlis
```

Installs made under the old name `skill-creator` migrate on their own: the rename is recorded in the
marketplace manifest and picked up on update.
