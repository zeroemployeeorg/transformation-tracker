# CLAUDE.md

This repo is a minimal starter for the 12-week transformation-tracker program taught at
profrod.ai. It exists so a student can `git clone` it into their own project (or copy the
`.claude/skills/transformation-tracker/` directory into a project they already have) and start
logging weeks immediately.

## What's here

- `.claude/skills/transformation-tracker/` — the skill Claude Code loads automatically. See its
  `SKILL.md` for the full contract.
- `example-transformation-log.jsonl` — four real weeks of output from the scripts in this repo,
  kept as a worked example, not fabricated data. Delete it before logging your own Week 1; it is
  not the log the skill will read from and write to (that's `transformation-log.jsonl`, created
  fresh the first time you log a week).

## Project conventions

- The log is `transformation-log.jsonl` at the repo root, one JSON object per line, append-only.
  Never hand-edit a past week's numbers to make a trend look better; if a week's numbers were
  wrong, say so in that week's bottleneck field rather than rewriting history.
- The two scripts under `.claude/skills/transformation-tracker/scripts/` are stdlib-only Python.
  Do not add a dependency to make them work — that defeats the point of a starter any project can
  drop into its own stack without a new install.
- If this repo is cloned into a project that already has its own linter, formatter, or CI, run
  those against any changes made here. This repo does not ship its own linting configuration on
  purpose, so the student's own tooling is what applies.
