# transformation-tracker

A minimal, dependency-free starter for tracking a 12-week automation transformation, built as a
Claude Code skill instead of a standalone notebook. Five things get measured every week:
Automation Index, Time Liberation Score, Revenue Efficiency Multiple, Client Capacity Score, and
recurring-revenue percentage. Revenue is never stored as an absolute number, only as a ratio to
your own Week 1 baseline.

This is a re-platform of the original [Billion Transformation
Tracker](https://github.com/zeroemployeeorg/business-transformation-tracker) (Polars + DuckDB +
Jupyter), keeping the same five metrics and the same privacy design, on a stack that doesn't
require installing a data-analysis toolchain: two stdlib-only Python scripts, a plain JSONL log,
and a Claude Code skill that asks the right questions before writing anything.

## Use it

Clone this repo, or copy `.claude/skills/transformation-tracker/` into a project you already
have. Open Claude Code in that project and say "log week 1" — it will ask for the six numbers it
needs (see `.claude/skills/transformation-tracker/SKILL.md`) and run the logging script for you.

Prefer the command line directly:

```bash
python3 .claude/skills/transformation-tracker/scripts/log_week.py \
  --week 1 --total-hours 55 --automated-hours 8 --active-clients 3 \
  --revenue-ratio 1.0 --recurring-pct 10.0 \
  --automated-this-week "Email filtering, automated meeting notes" \
  --bottleneck "Manual client onboarding"

python3 .claude/skills/transformation-tracker/scripts/report.py
```

No install step. Both scripts are Python standard library only.

## What changed from the original, and what didn't

The five metrics and their formulas are unchanged, ported directly from the original
`billion_tracker.py`. What changed is the storage (a plain JSONL file instead of a DuckDB
database) and the interface (a Claude Code skill that asks for the week's numbers conversationally
instead of a Python function call in a notebook cell).

One real inconsistency in the original was not carried over silently: its dashboard text and
target lines were drawn at 80% automation, but its actual graduation gate checked for 70%. This
port picks one number for the graduation bar (70%) and names 80% separately as a stretch target,
documented in `report.py`.

## License

MIT.
