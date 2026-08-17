#!/usr/bin/env python3
"""
transformation-tracker: append one week's metrics to the local log and print
the calculated values. No external dependencies — stdlib only, so it runs
inside any project's existing Python without adding a new dependency to
the student's stack.

Formulas ported directly from the original billion_tracker.py
(automation_index, time_saved_vs_baseline, revenue_efficiency_multiple,
client_capacity_score), Week 1 is always the baseline.

Usage:
    python3 log_week.py \
        --week 1 \
        --total-hours 55 \
        --automated-hours 8 \
        --active-clients 3 \
        --revenue-ratio 1.0 \
        --recurring-pct 10.0 \
        --automated-this-week "Email filtering, automated meeting notes" \
        --bottleneck "Manual client onboarding"

Writes one line to transformation-log.jsonl in the current directory
(append-only, never rewrites a prior week) and prints the calculated
metrics for that week.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

LOG_PATH = Path("transformation-log.jsonl")


def read_log() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    rows = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_week(rows: list[dict], week_number: int) -> dict | None:
    for row in rows:
        if row["week_number"] == week_number:
            return row
    return None


def calculate(
    week_number: int,
    total_hours: float,
    automated_hours: float,
    active_clients: int,
    revenue_ratio: float,
    recurring_pct: float,
    baseline: dict | None,
) -> dict:
    if total_hours <= 0:
        raise ValueError("total-hours must be greater than 0")
    if automated_hours < 0 or automated_hours > total_hours:
        raise ValueError("automated-hours must be between 0 and total-hours")

    manual_hours = total_hours - automated_hours
    automation_index = (automated_hours / total_hours) * 100

    if baseline is not None and week_number > 1:
        baseline_hours = baseline["total_hours"]
        baseline_clients = baseline["active_clients"]
        baseline_revenue_ratio = baseline["revenue_ratio"]
        time_saved = baseline_hours - total_hours
        # Ported exactly from the original: revenue-per-hour this week,
        # divided by revenue-per-hour at baseline (always 1.0 at baseline
        # since Week 1's own revenue_ratio is 1.0 by definition).
        revenue_efficiency_multiple = (revenue_ratio / total_hours) / (
            baseline_revenue_ratio / baseline_hours
        )
        client_capacity_score = (active_clients / total_hours) / (
            baseline_clients / baseline_hours
        )
    else:
        time_saved = 0.0
        revenue_efficiency_multiple = 1.0
        client_capacity_score = 1.0

    return {
        "week_number": week_number,
        "submission_date": date.today().isoformat(),
        "total_hours": total_hours,
        "automated_hours": automated_hours,
        "manual_hours": manual_hours,
        "active_clients": active_clients,
        "revenue_ratio": revenue_ratio,
        "recurring_revenue_pct": recurring_pct,
        "automation_index": round(automation_index, 2),
        "time_saved_vs_baseline": round(time_saved, 2),
        "revenue_efficiency_multiple": round(revenue_efficiency_multiple, 4),
        "client_capacity_score": round(client_capacity_score, 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Log one week's transformation metrics.")
    parser.add_argument("--week", type=int, required=True, dest="week_number")
    parser.add_argument("--total-hours", type=float, required=True)
    parser.add_argument("--automated-hours", type=float, required=True)
    parser.add_argument("--active-clients", type=int, required=True)
    parser.add_argument("--revenue-ratio", type=float, required=True)
    parser.add_argument("--recurring-pct", type=float, required=True)
    parser.add_argument("--automated-this-week", type=str, default="")
    parser.add_argument("--bottleneck", type=str, default="")
    args = parser.parse_args()

    rows = read_log()

    if find_week(rows, args.week_number) is not None:
        print(
            f"week {args.week_number} is already logged. "
            "This script only appends; it will not overwrite a prior week.",
            file=sys.stderr,
        )
        return 1

    baseline = find_week(rows, 1)
    if args.week_number == 1 and baseline is not None:
        print("Week 1 is already logged and is the baseline for every later week.", file=sys.stderr)
        return 1
    if args.week_number > 1 and baseline is None:
        print("No Week 1 entry found. Log Week 1 first; every later week is measured against it.", file=sys.stderr)
        return 1

    try:
        result = calculate(
            week_number=args.week_number,
            total_hours=args.total_hours,
            automated_hours=args.automated_hours,
            active_clients=args.active_clients,
            revenue_ratio=args.revenue_ratio,
            recurring_pct=args.recurring_pct,
            baseline=baseline,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result["automated_this_week"] = args.automated_this_week
    result["biggest_bottleneck"] = args.bottleneck
    result["logged_at_utc"] = datetime.now(timezone.utc).isoformat()

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")

    print(f"week {args.week_number} logged.")
    print(f"automation_index: {result['automation_index']}%")
    print(f"time_saved_vs_baseline: {result['time_saved_vs_baseline']} hours/week")
    print(f"revenue_efficiency_multiple: {result['revenue_efficiency_multiple']}x")
    print(f"client_capacity_score: {result['client_capacity_score']}x")
    print(f"recurring_revenue_pct: {result['recurring_revenue_pct']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
