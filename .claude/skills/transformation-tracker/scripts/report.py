#!/usr/bin/env python3
"""
transformation-tracker: read transformation-log.jsonl and print a progress
table plus a graduation-readiness report. Stdlib only.

Usage:
    python3 report.py            # progress table + full report
    python3 report.py --table    # just the table
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LOG_PATH = Path("transformation-log.jsonl")

# Graduation targets. The original repo's dashboard text and its graduation
# checklist disagreed with each other (dashboard target lines drawn at 80%
# automation / 50% recurring revenue, but the graduation gate itself checked
# automation_index >= 70). This port picks ONE number per metric and uses it
# everywhere, rather than reproducing that inconsistency: 70% automation and
# 50% recurring revenue are the two gating numbers; 80% is kept as the
# aspirational target line shown in prose, clearly labeled as a stretch
# beyond the graduation bar, not the bar itself.
GRADUATION_AUTOMATION_TARGET = 70.0
STRETCH_AUTOMATION_TARGET = 80.0
GRADUATION_RECURRING_TARGET = 50.0
GRADUATION_TIME_REDUCTION_TARGET = 50.0
GRADUATION_WEEKS = 12


def read_log() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    rows = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    rows.sort(key=lambda r: r["week_number"])
    return rows


def print_table(rows: list[dict]) -> None:
    if not rows:
        print("No weeks logged yet. Run log_week.py for Week 1 first.")
        return
    header = f"{'Week':<6}{'Automation %':<14}{'Hours Saved':<13}{'Rev Efficiency':<16}{'Client Capacity':<17}{'Recurring %':<12}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['week_number']:<6}"
            f"{r['automation_index']:<14.1f}"
            f"{r['time_saved_vs_baseline']:<13.1f}"
            f"{r['revenue_efficiency_multiple']:<16.2f}"
            f"{r['client_capacity_score']:<17.2f}"
            f"{r['recurring_revenue_pct']:<12.1f}"
        )


def print_report(rows: list[dict]) -> None:
    if not rows:
        print("No weeks logged yet. Run log_week.py for Week 1 first.")
        return

    first = rows[0]
    latest = rows[-1]
    week_num = latest["week_number"]

    print(f"\nWeek {week_num} of {GRADUATION_WEEKS}")
    print(f"Started: {first['submission_date']}  Latest: {latest['submission_date']}\n")

    ai_current = latest["automation_index"]
    ai_start = first["automation_index"]
    print("Automation Index")
    print(f"  Week 1: {ai_start:.1f}%   Week {week_num}: {ai_current:.1f}%   Change: {ai_current - ai_start:+.1f}%")
    if ai_current >= STRETCH_AUTOMATION_TARGET:
        print(f"  Stretch target ({STRETCH_AUTOMATION_TARGET:.0f}%): reached")
    else:
        print(f"  Graduation target ({GRADUATION_AUTOMATION_TARGET:.0f}%): {'reached' if ai_current >= GRADUATION_AUTOMATION_TARGET else f'{GRADUATION_AUTOMATION_TARGET - ai_current:.1f}% to go'}")

    time_saved = latest["time_saved_vs_baseline"]
    baseline_hours = first["total_hours"]
    time_reduction_pct = (time_saved / baseline_hours * 100) if baseline_hours > 0 else 0
    print("\nTime Liberation Score")
    print(f"  Hours saved per week vs Week 1: {time_saved:.1f}")
    print(f"  Time reduction: {time_reduction_pct:.1f}%  (target: {GRADUATION_TIME_REDUCTION_TARGET:.0f}%)")

    rem = latest["revenue_efficiency_multiple"]
    print(f"\nRevenue Efficiency Multiple: {rem:.2f}x baseline")

    ccs = latest["client_capacity_score"]
    print(f"Client Capacity Score: {ccs:.2f}x baseline")

    recurring = latest["recurring_revenue_pct"]
    print(f"\nRecurring revenue: {recurring:.1f}%  (target: {GRADUATION_RECURRING_TARGET:.0f}%)")

    print("\nGraduation readiness")
    requirements = [
        (f"Automation Index >= {GRADUATION_AUTOMATION_TARGET:.0f}%", ai_current >= GRADUATION_AUTOMATION_TARGET),
        (f"Time reduction >= {GRADUATION_TIME_REDUCTION_TARGET:.0f}%", time_reduction_pct >= GRADUATION_TIME_REDUCTION_TARGET),
        (f"Recurring revenue >= {GRADUATION_RECURRING_TARGET:.0f}%", recurring >= GRADUATION_RECURRING_TARGET),
        (f"{GRADUATION_WEEKS} weeks logged", week_num >= GRADUATION_WEEKS),
    ]
    for label, met in requirements:
        print(f"  [{'x' if met else ' '}] {label}")

    remaining = sum(1 for _, met in requirements if not met)
    if remaining == 0:
        print("\nAll graduation requirements met.")
    else:
        print(f"\n{remaining} requirement(s) remaining.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", action="store_true", help="print only the table, skip the full report")
    args = parser.parse_args()

    rows = read_log()
    print_table(rows)
    if not args.table:
        print_report(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
