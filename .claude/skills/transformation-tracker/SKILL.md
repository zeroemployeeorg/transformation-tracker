---
name: transformation-tracker
description: "Log one week's automation metrics (hours automated, active clients, revenue ratio to your Week 1 baseline, recurring-revenue percentage) and generate a progress table plus graduation report for the 12-week transformation program. Use this at the end of each week of the program, or when asked to log a week, show progress, or check graduation readiness. Never invents numbers — always asks the operator for the real ones before writing to the log."
---

# transformation-tracker

Ports the metrics from the original Billion Transformation Tracker (Automation Index, Time
Liberation Score, Revenue Efficiency Multiple, Client Capacity Score, and recurring-revenue
tracking) onto a plain, dependency-free log any project can carry, instead of a separate
Polars/DuckDB notebook. The formulas are unchanged from the original; only the storage and the
interface changed.

## Privacy contract — read this before logging anything

Revenue is **never** stored as an absolute number. Every week after Week 1 asks for a
**revenue ratio to your own Week 1 baseline** (e.g. `1.15` means 15% more revenue than Week 1,
whatever that week's real number was). Only the operator knows what Week 1's baseline actually
represents. The log file (`transformation-log.jsonl`) is safe to commit, share, or show on a call
without exposing real financials, because it never contains one.

## When to use this skill

- The operator says something like "log this week," "week N is done," or gives you the week's
  numbers directly.
- The operator asks to see progress, the dashboard, or "how am I doing."
- The operator asks whether they're ready to graduate, or how close they are.

## Logging a week

**Ask for these six numbers before running anything** — never estimate or infer them from
conversation history, and never carry a number over from a prior week:

1. Total hours worked this week
2. Hours of that work which were automated (an agent did it, not the operator)
3. Number of active clients
4. Revenue ratio to Week 1 (Week 1 itself is always `1.0`; every later week states its revenue
   as a multiple of Week 1's, e.g. `1.2` for 20% more)
5. Percentage of revenue that is recurring/subscription rather than one-off project work
6. One sentence on what got automated this week, and one sentence on the current bottleneck

Then run:

```bash
python3 .claude/skills/transformation-tracker/scripts/log_week.py \
  --week <N> \
  --total-hours <hours> \
  --automated-hours <hours> \
  --active-clients <count> \
  --revenue-ratio <ratio> \
  --recurring-pct <percentage> \
  --automated-this-week "<one sentence>" \
  --bottleneck "<one sentence>"
```

The script refuses to run if: `--week` is already logged (it never overwrites a prior week — fix
a mistake by editing the JSONL line directly, not by re-running), `--automated-hours` is negative
or exceeds `--total-hours`, or `--week` is greater than 1 and no Week 1 entry exists yet.

Report the script's own printed numbers back to the operator. Do not recompute them yourself —
the script is the source of truth for the arithmetic; your job is asking the right questions and
relaying what it prints, not re-deriving the formulas from memory.

## Showing progress

```bash
python3 .claude/skills/transformation-tracker/scripts/report.py
```

Prints the week-by-week table and a graduation-readiness report. Pass `--table` for just the
table. If the operator's project already has a charting tool in its own stack (matplotlib, a
notebook, a dashboard framework, anything), offer to read `transformation-log.jsonl` and feed it
into that tool instead of just printing the table — the log is plain JSONL specifically so it is
not tied to this skill's own scripts. If they have nothing, the table above is the whole
deliverable; do not install a charting library on their behalf.

## Graduation targets

Two numbers gate graduation, kept deliberately distinct from an aspirational stretch line:

| Requirement | Graduation bar |
|---|---|
| Automation Index | 70% (80% is named separately as a stretch target, not the bar) |
| Time reduction vs. Week 1 | 50% |
| Recurring revenue | 50% |
| Weeks logged | 12 |

## What this skill will not do

It will not guess a number you have not given it, carry a number over from a prior week without
asking, or edit a week that is already logged. If the operator is unsure of a number, ask them to
estimate deliberately and say so in the automated-this-week or bottleneck field — an honest
estimate beats a number invented to look tidy.
