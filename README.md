# Feynman Technique

Turn resolved bugs, implementation lessons, reviews, and debugging sessions into evidence-grounded engineering learning notes.

This repo contains a single skill and the helper files around it. The point is simple: when you finish a bug fix or work through a debugging session, capture the lesson in a form you can actually reuse later.

> Not a diary. More like a small workflow for turning evidence into a lesson: evidence -> root cause -> Feynman explanation -> prediction check -> guardrail -> review.

---

## Contents

- [What This Repository Does](#what-this-repository-does)
- [Quickstart](#quickstart)
- [Commands](#commands)
- [How the Skill Works](#how-the-skill-works)
- [Journal Storage](#journal-storage)
- [Repository Structure](#repository-structure)
- [Helper Script](#helper-script)
- [Contributing](#contributing)
- [License](#license)

## What This Repository Does

`feynman-technique` is a single-skill repo for engineering learning capture. It is meant for the part after the work is done, when the better question is not "what changed?" but "what should I remember so I do not make this mistake again?"

The skill is built around a few straightforward ideas:

- Capture only fixes worth learning from.
- Rewrite evidence into generic, transferable lessons.
- Explain the underlying mechanism in plain English.
- End every lesson with a guardrail and a review prompt.

Common use cases:

- Turn a resolved bug into a reusable engineering lesson.
- Generate a same-day learning digest from logged entries.
- Run a 7-day retrospective across recurring blind spots.
- Build active-recall quizzes from recent notes.
- Track repeated mental-model gaps over time.

## Quickstart

This repository is a local skill folder.

- It is not an npm package.
- It is not a Claude plugin.
- Do not install it with `npm install`.
- Do not run it with `claude --plugin-dir ...`.

### 1. Install the skill

For Claude Code, copy or symlink the whole folder into your local skills directory:

```bash
mkdir -p ~/.config/claude-code/skills
cp -R /path/to/feynman-technique ~/.config/claude-code/skills/feynman-technique
```

If you want to keep the repo where it is while you work on it, symlink it instead:

```bash
mkdir -p ~/.config/claude-code/skills
ln -s /absolute/path/to/feynman-technique ~/.config/claude-code/skills/feynman-technique
```

If you use Codex or another runtime, put this folder wherever that runtime looks for local `SKILL.md`-based skills.

### 2. Choose where journal files should live

You can let the helper pick a default location, or set one yourself:

```bash
export FEYNMAN_TECHNIQUE_DIR="$HOME/Documents/feynman-technique"
```

On the first write, the helper confirms the storage directory before it creates any journal files.

### 3. Start your agent runtime

For Claude Code, restart or launch the CLI after installing the skill:

```bash
claude
```

If you use another runtime, restart it so it can pick up the new `SKILL.md`.

### 4. Start logging learnings

Use the skill after a meaningful fix, debugging session, or review:

```text
/feynman-technique
/feynman-technique review
/feynman-technique retro
/feynman-technique quiz
```

### 5. Review generated files

Daily entries are stored as dated Markdown files such as `YYYY-MM-DD.md`. Weekly retrospectives are written as `retro-YYYY-MM-DD.md`.

### 6. Verify local prerequisites

The bundled helper script uses only the Python standard library, but it does require Python 3.10+.

## Commands

| Command | Purpose |
|---|---|
| `/feynman-technique` | Log all resolved fixes and lessons from the current session |
| `/feynman-technique <description>` | Anchor the run on one issue while still capturing other fixes |
| `/feynman-technique review` | Generate today's daily digest |
| `/feynman-technique review YYYY-MM-DD` | Generate a digest for a specific date |
| `/feynman-technique retro` | Create a retrospective for the last 7 days |
| `/feynman-technique retro <N>` | Create a retrospective over the last `N` days |
| `/feynman-technique quiz` | Build active-recall questions from recent entries |
| `/feynman-technique explain <entry-title>` | Re-explain one entry using the full Feynman loop |
| `/feynman-technique gaps` | Summarize repeated categories and blind spots |

## How the Skill Works

The flow is simple:

1. Scan the full session for fixes worth keeping.
2. Classify each fix using a single primary category.
3. Rewrite the lesson so it is generic, transferable, and testable.
4. Explain the misunderstood mechanism in plain English.
5. Add a prediction check and a concrete recurrence guardrail.
6. Save the result to the daily journal without duplicating titles.

The quality bar is strict on purpose:

- No project-specific file paths, identifiers, or internal names in the saved notes.
- Titles should describe principles, not one-off bugs.
- Every entry should capture the gap, the principle, and the guardrail.
- External references are optional. Use them only when they actually help and you can state them safely.

## Journal Storage

The helper script resolves the journal directory in this order:

1. `FEYNMAN_TECHNIQUE_DIR`
2. `FEYNMAN_TECHNIQUE_BASE_DIR/feynman-technique`
3. `~/Documents/feynman-technique`

If you do not set anything explicitly, journal files go here:

```text
~/Documents/feynman-technique
```

If none of those locations is writable, set `FEYNMAN_TECHNIQUE_DIR` yourself.

## Repository Structure

```text
feynman-technique/
|-- SKILL.md
|-- README.md
|-- CONTRIBUTING.md
|-- scripts/
|   `-- journal.py
`-- resources/
    |-- categories.md
    |-- evidence-bank.md
    |-- feynman-method.md
    `-- templates.md
```

## Helper Script

`scripts/journal.py` handles the local file work: appending entries, avoiding duplicates, generating digests, building retros, and pulling quiz or gap reports.

Examples:

```bash
python3 scripts/journal.py list --date 2026-04-24
python3 scripts/journal.py digest --date 2026-04-24
python3 scripts/journal.py retro --limit 7
python3 scripts/journal.py quiz --limit 7
python3 scripts/journal.py explain --title "Verify contracts before coding"
python3 scripts/journal.py gaps --limit 7
```

Use `append` when another tool or agent is generating note bodies and piping them into the journal:

```bash
printf '### Verify contracts before coding\n**The principle:** Validate interfaces before coding against them.\n' | python3 scripts/journal.py append --title "Verify contracts before coding"
```

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](./CONTRIBUTING.md).

In practice, the most useful contributions do one of these:

- Improve the skill instructions without widening scope unnecessarily.
- Strengthen the bundled templates, categories, or evidence guidance.
- Keep the helper script aligned with the documented behavior in `SKILL.md`.

## License

This repository does not currently include a top-level license file. Add one before publishing broadly or accepting external reuse under specific terms.
