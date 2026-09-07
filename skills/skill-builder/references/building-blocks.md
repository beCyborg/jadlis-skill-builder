# Building Blocks

The skill-builder operates on composable building blocks. Each has well-defined inputs and outputs.

| Building Block | Input | Output | Agent |
|-----------|-------|--------|-------|
| **Eval Run** | skill + eval prompt + files | transcript, outputs, metrics | `agents/executor.md` |
| **Grade Expectations** | outputs + expectations | pass/fail per expectation | `agents/grader.md` |
| **Blind Compare** | output A, output B, eval prompt | winner + reasoning | `agents/comparator.md` |
| **Post-hoc Analysis** | winner + skills + transcripts | improvement suggestions | `agents/analyzer.md` |

### Eval Run

Executes a skill on an eval prompt and produces measurable outputs.

- **Input**: Skill path, eval prompt, input files
- **Output**: `transcript.md`, `outputs/`, `metrics.json`
- **Metrics captured**: Tool calls, execution steps, output size, errors

### Grade Expectations

Evaluates whether outputs meet defined expectations.

- **Input**: Expectations list, transcript, outputs directory
- **Output**: `grading.json` with pass/fail per expectation plus evidence
- **Purpose**: Objective measurement of skill performance

### Blind Compare

Compares two outputs without knowing which skill produced them.

- **Input**: Output A path, Output B path, eval prompt, expectations (optional)
- **Output**: Winner (A/B/TIE), reasoning, quality scores
- **Purpose**: Unbiased comparison between skill versions

### Post-hoc Analysis

After blind comparison, analyzes WHY the winner won.

- **Input**: Winner identity, both skills, both transcripts, comparison result
- **Output**: Winner strengths, loser weaknesses, improvement suggestions
- **Purpose**: Generate actionable improvements for next iteration
