[Русский](employee.md) · English

# Claude Code as an employee

An assistant finishes on text. An employee finishes on a record at a known address: a file on disk, a row in a tracker, a field in a note's properties. The difference is not how clever the model is — it is that it has hands, credentials, and a place decided in advance for the result to go.

Below are the four parts of the setup and what each one is for: skill, hooks, memory, MCP. All examples are synthetic.

![Workplace seen from behind: a person at a wide desk facing five panels, a mechanical arm working at each one, a stack of finished sheets on the right](img/08-employee-01.webp)

## Where the chain breaks

The answer is usually fine. What comes next is opening the file, finding the line, pasting, fixing the format, ticking the task — and that part is on you, every time. The break is always at the same point: between “worded” and “filed where it belongs”.

A chat thread holds none of your data. It holds what you managed to paste and what the model remembers. It cannot see which tasks closed today or which line in a note went stale a week ago — which is why its answer is confident and about yesterday.

![A glass partition: outside, a person reaching towards it with a speech bubble; inside, a working room with a desk, drawers, and a second person moving a sheet of paper](img/08-employee-02.webp)

## The skill — a job description

A skill is a folder of instructions for one type of task: when to fire, what to do step by step, what not to do, where to put the result. You do not name the tool or dictate the order of operations — you name the result; working out what does the job is the agent's part.

```
weekly-digest/
  SKILL.md              trigger conditions, 6 steps, where to write
  references/format.md  layout of the final table (loaded on demand)
  scripts/collect.py    the deterministic part — collects the week's files
```

What the instructions buy you:

- Repeatability: two identical runs produce one output format instead of two.
- The destination is fixed up front — with no address, the agent asks instead of deciding.
- Fixes made after mistakes accumulate in one file rather than in your head.
- Heavy tasks follow fixed phases (collect → verify → synthesise → write): if verification returned nothing, synthesis never starts, and the gap shows up as a stop.

One instruction, one type of task. Once there are many skills, they sort themselves onto shelves: advisors, market intel, research, bridges to apps, personal operations.

![A six-shelf rack filled with rows of identical blocks, and a separate box beside it carrying three round tags of a different shape](img/08-employee-03.webp)

## Hooks — standing orders

A skill is what the agent reads. A hook is what fires without the agent: an interceptor script that sees a tool call before it runs and can refuse it.

The refusal comes from the system, not from the model's reasoning — it cannot be talked out of it. The gap between “the instructions say don't” and “this cannot be done” shows up exactly when the model gets something wrong.

A good standing order does not merely forbid — it names the replacement:

```
> read this document at the link

[hook: pre-tool-use] refused: the paid parser bills documents per page.
Replacement: local utility fetch-doc.sh <url> — same text, no charges.

Taking the local path.
```

Worth handing to hooks: expensive calls that have a free alternative, irreversible operations, writes to places that must stay untouched. Not worth it: everything at once — only what is named is blocked, the rest passes, and a long list turns into a false sense of protection.

## Memory — a log of findings

A mistake can repeat forever while it lives only in your head. Each post-mortem becomes its own file: what looked true, what turned out to be the case, how to check next time.

```
memory/
  MEMORY.md                      index: one line per finding
  quota-counts-failed-calls.md   the service bills quota for validation errors too
  green-tests-miss-live-run.md   green tests ≠ a real run on live data
```

Rules that keep the log usable:

- One finding, one file; the index stays an index, not a dump.
- It is read before work starts, not after the next mistake.
- It holds only what actually broke once and got written down — nothing beyond that.
- Your own documentation is just another source: it gets checked against what is observed, not treated as truth.

## MCP — credentials

MCP is the adapter between a service and the workplace: a bridge program through which the agent reads and writes live data under your accounts. That is the state at launch time, not a copy exported a week ago.

Access is granted by name: one adapter per service, keys in the system keychain rather than in repository files. The permissions are real, which is why they come with limiters attached.

![A closed padlock, a ring of three keys, and a round dial with a needle and no markings; a thin line connects them and stops at the dial](img/08-employee-04.webp)

Four rules that make this comfortable to live with:

1. Dangerous calls named in advance are blocked before the service is contacted.
2. No fresh data means “no data” in the result, not a plausible-looking value.
3. Writes only to an explicit address; the agent starts no files “at its own discretion”.
4. Every report carries a “what failed” section: an unreachable source or a skipped step goes there instead of being filled in by guesswork.

The padlock and keys are real. The dial with no markings is the honest part of the picture: exactly one class of overspend is intercepted, the rest of the spend shows up in the status line, and you are the one watching it.

## What follows from this

Build your first skill out of the work you are doing by hand for the third time in a row. The rest arrives as needed: a hook after the first expensive miss, a memory file after the first repeated mistake, an adapter once copying data by hand stops being enough.

This stack covers two of those steps: [skill-builder](../README.en.md) writes the instructions, [plugin-creator](https://github.com/beCyborg/jadlis-plugin-creator) packages them into a plugin that installs with one command.
