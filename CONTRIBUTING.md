# Contributing

Thanks for improving `feynman-technique`.

This repo is small on purpose: one skill, one helper script, and a few reference docs. Please keep changes focused on the core job of turning engineering work into reusable learning notes.

## What To Contribute

- Improvements to `SKILL.md`
- Better templates or categorization guidance in `resources/`
- Deterministic helper behavior in `scripts/journal.py`
- Documentation updates in `README.md`

## Quality Bar

Changes should preserve the shape of the skill:

- Keep entries generic and transferable.
- Do not introduce project-specific identifiers into saved examples.
- Prefer concrete instructions over motivational copy.
- Keep command behavior, docs, and helper script behavior aligned.
- Do not turn this into a general note-taking system.

## Working Guidelines

1. Update docs when command behavior or storage behavior changes.
2. Keep resource files consistent with the expectations described in `SKILL.md`.
3. Prefer deterministic helper logic over agent-only heuristics when file I/O is involved.
4. Preserve portability: do not hardcode machine-specific paths.

## Manual Checks

Before opening a pull request, run the checks that cover the part you changed:

```bash
python3 scripts/journal.py list --date 2026-04-24
python3 scripts/journal.py quiz --limit 7
python3 scripts/journal.py gaps --limit 7
```

If you changed journal storage behavior, also make sure environment variable precedence still matches `SKILL.md`.

## Pull Requests

Open focused pull requests with:

- A short summary of the problem
- The reasoning behind the change
- Any doc updates needed alongside the change
- A note on how you verified the result

Smaller patches are easier to review here than broad cleanups.
