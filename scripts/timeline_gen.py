#!/usr/bin/env python3
"""
Timeline Generator — Generate project timelines for IB transactions.

Generates phase start/end dates, milestone lists, critical path, and
intermediary deliverables schedule for IPO, Refinancing, and M&A projects.

Usage:
    python timeline_gen.py --product IPO --board 科创板 --start 2026-06-01

    python timeline_gen.py --product M&A --type 发行股份购买资产 --start 2026-06-01 -o timeline.csv
"""

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Duration data (months, typical)
# ---------------------------------------------------------------------------

IPO_PHASES: Dict[str, Dict[str, float]] = {
    "主板": {"改制": 2.5, "辅导": 4.0, "申报": 2.5, "审核": 9.0, "注册": 1.5, "发行": 1.5},
    "科创板": {"改制": 1.5, "辅导": 3.5, "申报": 1.5, "审核": 5.0, "注册": 1.0, "发行": 1.5},
    "创业板": {"改制": 2.0, "辅导": 4.0, "申报": 2.0, "审核": 7.0, "注册": 1.0, "发行": 1.5},
    "北交所": {"改制": 1.5, "辅导": 2.5, "申报": 1.0, "审核": 3.5, "注册": 0.75, "发行": 1.0},
}

REFINANCING_PHASES: Dict[str, Dict[str, float]] = {
    "定向增发": {"准备": 1.0, "申报": 1.0, "审核": 2.0, "注册": 0.75, "发行": 0.5},
    "公开增发": {"准备": 1.5, "申报": 1.0, "审核": 3.5, "注册": 1.0, "发行": 1.0},
    "配股": {"准备": 1.0, "申报": 1.0, "审核": 3.0, "注册": 1.0, "发行": 1.0},
    "可转债": {"准备": 1.5, "申报": 1.0, "审核": 3.0, "注册": 1.0, "发行": 1.0},
    "优先股": {"准备": 1.0, "申报": 1.0, "审核": 2.0, "注册": 0.75, "发行": 0.75},
}

MA_PHASES: Dict[str, Dict[str, float]] = {
    "现金收购": {"尽调": 0.5, "谈判签约": 1.0, "审批披露": 1.0, "交割": 0.5},
    "发行股份购买资产": {"尽调": 1.0, "谈判签约": 1.5, "申报": 1.0, "审核": 3.0, "注册": 1.0, "交割": 0.5},
    "借壳上市": {"尽调": 1.5, "重组方案": 2.0, "申报": 1.5, "审核": 6.0, "注册": 2.0, "交割": 1.0},
    "吸收合并": {"尽调": 1.0, "谈判签约": 1.5, "申报": 1.0, "审核": 4.0, "注册": 1.0, "交割": 0.5},
}

# IPO Milestones (standard)
IPO_MILESTONES = [
    ("项目启动", "开工会议召开", "Sponsor"),
    ("改制完成", "法律主体改制完毕", "Lawyer"),
    ("审计报告出具", "三年一期审计报告完成", "Accountant"),
    ("辅导备案", "辅导备案登记", "Sponsor"),
    ("辅导验收", "辅导验收通过", "Sponsor"),
    ("董事会决议", "董事会审议通过IPO方案", "Company"),
    ("申报受理", "申报材料获受理", "Sponsor"),
    ("首轮问询", "收到首轮审核问询函", "Exchange"),
    ("问询回复", "提交问询回复", "All"),
    ("上市委审议", "上市委会议审议通过", "Committee"),
    ("注册生效", "获得注册批文", "CSRC"),
    ("发行完成", "完成发行并上市", "Sponsor"),
]

# Intermediary deliverables by phase
DELIVERABLES: Dict[str, List[Tuple[str, str]]] = {
    "改制": [
        ("审计报告（改制基准日）", "Accountant"),
        ("法律尽职调查报告", "Lawyer"),
        ("改制方案", "Lawyer + Sponsor"),
        ("创立大会文件", "Lawyer"),
    ],
    "辅导": [
        ("辅导备案报告", "Sponsor"),
        ("辅导工作底稿", "Sponsor"),
        ("辅导验收申请", "Sponsor"),
    ],
    "申报": [
        ("招股说明书（申报稿）", "All"),
        ("法律意见书", "Lawyer"),
        ("审计报告", "Accountant"),
        ("内控鉴证报告", "Accountant"),
        ("保荐工作报告", "Sponsor"),
        ("发行保荐书", "Sponsor"),
    ],
    "审核": [
        ("问询回复（各轮）", "All"),
        ("招股说明书（上会稿）", "All"),
        ("会计师专项说明", "Accountant"),
        ("律师补充法律意见", "Lawyer"),
    ],
    "注册": [
        ("招股说明书（注册稿）", "All"),
        ("会后事项专项说明", "All"),
    ],
    "发行": [
        ("发行方案", "Sponsor"),
        ("投资价值研究报告", "Sponsor"),
        ("发行公告", "Sponsor"),
        ("上市公告书", "All"),
    ],
}


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def months_to_days(months: float) -> int:
    """Convert months to approximate days."""
    return round(months * 30.44)


@dataclass
class Phase:
    name: str
    start_date: date
    end_date: date
    duration_months: float
    deliverables: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class Milestone:
    name: str
    description: str
    owner: str
    date: date


@dataclass
class Timeline:
    product: str
    board_or_type: str
    start_date: date
    phases: List[Phase] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    total_months: float = 0.0
    end_date: Optional[date] = None


def generate_ipo_timeline(board: str, start: date) -> Timeline:
    """Generate IPO timeline."""
    phases_data = IPO_PHASES.get(board)
    if not phases_data:
        raise ValueError(f"Unknown board: {board}. Must be one of: {list(IPO_PHASES.keys())}")

    timeline = Timeline(product="IPO", board_or_type=board, start_date=start)
    current_date = start

    for phase_name, duration in phases_data.items():
        phase_days = months_to_days(duration)
        phase_end = current_date + timedelta(days=phase_days)

        deliverables = DELIVERABLES.get(phase_name, [])

        timeline.phases.append(Phase(
            name=phase_name,
            start_date=current_date,
            end_date=phase_end,
            duration_months=duration,
            deliverables=deliverables,
        ))

        timeline.total_months += duration
        current_date = phase_end

    timeline.end_date = current_date

    # Generate milestones based on phase transitions
    milestone_idx = 0
    for phase in timeline.phases:
        if milestone_idx < len(IPO_MILESTONES):
            m_name, m_desc, m_owner = IPO_MILESTONES[milestone_idx]
            timeline.milestones.append(Milestone(
                name=m_name,
                description=m_desc,
                owner=m_owner,
                date=phase.start_date,
            ))
            milestone_idx += 1

    # Add final milestone
    if milestone_idx < len(IPO_MILESTONES):
        m_name, m_desc, m_owner = IPO_MILESTONES[-1]
        timeline.milestones.append(Milestone(
            name=m_name,
            description=m_desc,
            owner=m_owner,
            date=timeline.end_date,
        ))

    return timeline


def generate_refinancing_timeline(instrument: str, start: date) -> Timeline:
    """Generate refinancing timeline."""
    phases_data = REFINANCING_PHASES.get(instrument)
    if not phases_data:
        raise ValueError(f"Unknown instrument: {instrument}. Must be one of: {list(REFINANCING_PHASES.keys())}")

    timeline = Timeline(product="Refinancing", board_or_type=instrument, start_date=start)
    current_date = start

    for phase_name, duration in phases_data.items():
        phase_days = months_to_days(duration)
        phase_end = current_date + timedelta(days=phase_days)

        timeline.phases.append(Phase(
            name=phase_name,
            start_date=current_date,
            end_date=phase_end,
            duration_months=duration,
        ))

        timeline.total_months += duration
        current_date = phase_end

    timeline.end_date = current_date
    return timeline


def generate_ma_timeline(deal_type: str, start: date) -> Timeline:
    """Generate M&A timeline."""
    phases_data = MA_PHASES.get(deal_type)
    if not phases_data:
        raise ValueError(f"Unknown deal type: {deal_type}. Must be one of: {list(MA_PHASES.keys())}")

    timeline = Timeline(product="M&A", board_or_type=deal_type, start_date=start)
    current_date = start

    for phase_name, duration in phases_data.items():
        phase_days = months_to_days(duration)
        phase_end = current_date + timedelta(days=phase_days)

        timeline.phases.append(Phase(
            name=phase_name,
            start_date=current_date,
            end_date=phase_end,
            duration_months=duration,
        ))

        timeline.total_months += duration
        current_date = phase_end

    timeline.end_date = current_date
    return timeline


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_timeline_report(timeline: Timeline) -> str:
    """Format timeline as readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"  PROJECT TIMELINE: {timeline.product} — {timeline.board_or_type}")
    lines.append("=" * 70)
    lines.append(f"  Start Date:    {timeline.start_date}")
    lines.append(f"  End Date:      {timeline.end_date}")
    lines.append(f"  Total Duration: {timeline.total_months:.1f} months")
    lines.append("")
    lines.append("─" * 70)
    lines.append("  PHASES")
    lines.append("─" * 70)
    lines.append("")

    for i, phase in enumerate(timeline.phases, 1):
        days = (phase.end_date - phase.start_date).days
        lines.append(f"  Phase {i}: {phase.name}")
        lines.append(f"    Period: {phase.start_date} → {phase.end_date} ({days} days / {phase.duration_months:.1f} months)")
        if phase.deliverables:
            lines.append(f"    Deliverables:")
            for doc, owner in phase.deliverables:
                lines.append(f"      • {doc} ({owner})")
        lines.append("")

    if timeline.milestones:
        lines.append("─" * 70)
        lines.append("  KEY MILESTONES")
        lines.append("─" * 70)
        lines.append("")
        for m in timeline.milestones:
            lines.append(f"  • {m.date}: {m.name} — {m.description} [{m.owner}]")
        lines.append("")

    lines.append("─" * 70)
    lines.append("  CRITICAL PATH NOTE")
    lines.append("─" * 70)
    lines.append("  All phases are sequential. Any delay propagates downstream.")
    lines.append("  The most common delay points are: 审核 (inquiry rounds) and 申报 (document prep).")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_csv(timeline: Timeline) -> List[Dict[str, str]]:
    """Generate CSV rows for the timeline."""
    rows = []

    # Phase rows
    for phase in timeline.phases:
        rows.append({
            "Type": "Phase",
            "Name": phase.name,
            "Start": str(phase.start_date),
            "End": str(phase.end_date),
            "Duration (months)": f"{phase.duration_months:.1f}",
            "Duration (days)": str((phase.end_date - phase.start_date).days),
            "Owner": "—",
            "Notes": "",
        })

        # Deliverable sub-rows
        for doc, owner in phase.deliverables:
            rows.append({
                "Type": "  Deliverable",
                "Name": f"  {doc}",
                "Start": str(phase.start_date),
                "End": str(phase.end_date),
                "Duration (months)": "—",
                "Duration (days)": "—",
                "Owner": owner,
                "Notes": f"Due by {phase.end_date}",
            })

    # Milestone rows
    for m in timeline.milestones:
        rows.append({
            "Type": "Milestone",
            "Name": m.name,
            "Start": str(m.date),
            "End": str(m.date),
            "Duration (months)": "—",
            "Duration (days)": "—",
            "Owner": m.owner,
            "Notes": m.description,
        })

    return rows


def write_csv(timeline: Timeline, path: str) -> None:
    """Write timeline as CSV file."""
    rows = generate_csv(timeline)
    fieldnames = ["Type", "Name", "Start", "End", "Duration (months)", "Duration (days)", "Owner", "Notes"]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(timeline: Timeline) -> str:
    """Serialize timeline as JSON."""
    data = {
        "product": timeline.product,
        "board_or_type": timeline.board_or_type,
        "start_date": str(timeline.start_date),
        "end_date": str(timeline.end_date),
        "total_months": round(timeline.total_months, 1),
        "phases": [
            {
                "name": p.name,
                "start": str(p.start_date),
                "end": str(p.end_date),
                "duration_months": round(p.duration_months, 1),
                "duration_days": (p.end_date - p.start_date).days,
                "deliverables": [{"document": d, "owner": o} for d, o in p.deliverables],
            }
            for p in timeline.phases
        ],
        "milestones": [
            {
                "name": m.name,
                "description": m.description,
                "owner": m.owner,
                "date": str(m.date),
            }
            for m in timeline.milestones
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate project timelines for IB transactions (IPO, Refinancing, M&A).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --product IPO --board 科创板 --start 2026-06-01
  %(prog)s --product IPO --board 主板 --start 2026-06-01 -o timeline.csv
  %(prog)s --product M&A --type 发行股份购买资产 --start 2026-08-01 --json
  %(prog)s --product Refinancing --type 定向增发 --start 2026-07-15
        """,
    )

    parser.add_argument("--product", required=True,
                        choices=["IPO", "Refinancing", "M&A"],
                        help="Product type")
    parser.add_argument("--board", default=None,
                        choices=["主板", "科创板", "创业板", "北交所"],
                        help="Target board (for IPO)")
    parser.add_argument("--type", default=None, dest="instrument_type",
                        help="Refinancing instrument or M&A deal type")
    parser.add_argument("--start", required=True,
                        help="Project start date (YYYY-MM-DD)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output CSV file path")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--report", action="store_true",
                        help="Output as formatted text report (default)")

    args = parser.parse_args()

    # Parse start date
    try:
        start_date = date.fromisoformat(args.start)
    except ValueError:
        print(f"ERROR: Invalid date format: {args.start}. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    # Generate timeline
    try:
        if args.product == "IPO":
            if not args.board:
                print("ERROR: --board is required for IPO product.", file=sys.stderr)
                sys.exit(1)
            timeline = generate_ipo_timeline(args.board, start_date)

        elif args.product == "Refinancing":
            if not args.instrument_type:
                print("ERROR: --type is required for Refinancing product.", file=sys.stderr)
                sys.exit(1)
            timeline = generate_refinancing_timeline(args.instrument_type, start_date)

        elif args.product == "M&A":
            if not args.instrument_type:
                print("ERROR: --type is required for M&A product.", file=sys.stderr)
                sys.exit(1)
            timeline = generate_ma_timeline(args.instrument_type, start_date)

        else:
            print(f"ERROR: Unknown product: {args.product}", file=sys.stderr)
            sys.exit(1)

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        json_str = write_json(timeline)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"JSON timeline written to {args.output}")
        else:
            print(json_str)

    elif args.output and args.output.endswith(".csv"):
        write_csv(timeline, args.output)
        print(f"CSV timeline written to {args.output}")
        # Also print summary
        print(f"\nTimeline: {timeline.product} — {timeline.board_or_type}")
        print(f"  Start: {timeline.start_date}")
        print(f"  End:   {timeline.end_date}")
        print(f"  Total: {timeline.total_months:.1f} months")

    else:
        report = format_timeline_report(timeline)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Timeline report written to {args.output}")
        else:
            print(report)


if __name__ == "__main__":
    main()