#!/usr/bin/env python3
"""
Filing Tracker — Track regulatory filing progress for IB projects.

Tracks filing lifecycle: acceptance, inquiry dates/deadlines/actuals, hearing date,
registration approval, approval expiry, offering, listing. Provides dashboard
view, overdue alerts, and historical comparison statistics.

Usage:
    python filing_tracker.py init --project "Project Alpha" --filing-date 2026-01-15
    python filing_tracker.py update --project "Project Alpha" --event hearing --date 2026-06-10
    python filing_tracker.py status --project "Project Alpha"
    python filing_tracker.py dashboard
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = os.path.expanduser("~/.qclaw/skills/ib-execution/data/filing_tracker.json")


def ensure_db_dir() -> None:
    """Ensure the data directory exists."""
    db_dir = os.path.dirname(DEFAULT_DB_PATH)
    os.makedirs(db_dir, exist_ok=True)


def load_db() -> dict:
    """Load the filing tracker database."""
    ensure_db_dir()
    if os.path.exists(DEFAULT_DB_PATH):
        with open(DEFAULT_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": {}}


def save_db(db: dict) -> None:
    """Save the filing tracker database."""
    ensure_db_dir()
    with open(DEFAULT_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Event types and their rules
# ---------------------------------------------------------------------------

EVENT_TYPES = {
    "filing": {
        "label": "申报受理",
        "description": "Application accepted",
    },
    "inquiry_r1": {
        "label": "首轮问询",
        "description": "First round inquiry received",
        "response_deadline_days": 90,
    },
    "inquiry_r1_response": {
        "label": "首轮问询回复",
        "description": "Response to first inquiry",
    },
    "inquiry_r2": {
        "label": "二轮问询",
        "description": "Second round inquiry (if any)",
        "response_deadline_days": 60,
    },
    "inquiry_r2_response": {
        "label": "二轮问询回复",
        "description": "Response to second inquiry",
    },
    "inquiry_r3": {
        "label": "三轮问询",
        "description": "Third round inquiry (if any)",
        "response_deadline_days": 30,
    },
    "hearing": {
        "label": "上市委审议",
        "description": "Listing committee hearing",
    },
    "registration": {
        "label": "注册生效",
        "description": "Registration approved by CSRC",
        "expiry_months": 12,
    },
    "offering": {
        "label": "发行",
        "description": "Offering launched",
    },
    "listing": {
        "label": "上市",
        "description": "Shares listed on exchange",
    },
}

# Phase order
PHASE_ORDER = [
    "filing", "inquiry_r1", "inquiry_r1_response",
    "inquiry_r2", "inquiry_r2_response",
    "inquiry_r3", "inquiry_r3_response",
    "hearing", "registration", "offering", "listing",
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Project:
    name: str
    filing_date: date
    events: Dict[str, date] = field(default_factory=dict)
    notes: str = ""

    @property
    def current_phase(self) -> str:
        """Determine the current phase based on completed events."""
        for phase in reversed(PHASE_ORDER):
            if phase in self.events:
                idx = PHASE_ORDER.index(phase)
                next_idx = idx + 1
                if next_idx < len(PHASE_ORDER):
                    return PHASE_ORDER[next_idx]
                return "listing"
        return "filing"

    @property
    def overdue_alerts(self) -> List[str]:
        """Check for overdue items."""
        alerts = []
        today = date.today()

        # Check inquiry response deadlines
        for inquiry_event, response_event, deadline_days in [
            ("inquiry_r2", "inquiry_r2_response", 60),
            ("inquiry_r3", "inquiry_r3_response", 30),
        ]:
            if inquiry_event in self.events and response_event not in self.events:
                inquiry_date_obj = self.events[inquiry_event]
                if isinstance(inquiry_date_obj, str):
                    inquiry_date_obj = date.fromisoformat(inquiry_date_obj)
                deadline = inquiry_date_obj + timedelta(days=deadline_days)
                if today > deadline:
                    days_overdue = (today - deadline).days
                    alerts.append(
                        f"⚠️ OVERDUE: {EVENT_TYPES[inquiry_event]['label']} response was due "
                        f"{deadline} ({days_overdue} days overdue)"
                    )
                elif (deadline - today).days <= 14:
                    days_left = (deadline - today).days
                    alerts.append(
                        f"⏰ DUE SOON: {EVENT_TYPES[inquiry_event]['label']} response due "
                        f"{deadline} ({days_left} days remaining)"
                    )

        # Check registration expiry
        if "registration" in self.events and "offering" not in self.events:
            reg_date = self.events["registration"]
            if isinstance(reg_date, str):
                reg_date = date.fromisoformat(reg_date)
            expiry = reg_date.replace(year=reg_date.year + 1)
            if today > expiry:
                alerts.append(f"🚨 EXPIRED: Registration approval expired {expiry}!")
            elif (expiry - today).days <= 60:
                alerts.append(
                    f"⏰ EXPIRING SOON: Registration approval expires {expiry} "
                    f"({(expiry - today).days} days remaining)"
                )

        return alerts

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "filing_date": str(self.filing_date),
            "events": {k: str(v) for k, v in self.events.items()},
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            name=data["name"],
            filing_date=date.fromisoformat(data["filing_date"]),
            events={k: date.fromisoformat(v) if isinstance(v, str) else v
                    for k, v in data.get("events", {}).items()},
            notes=data.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args):
    """Initialize a new project in the tracker."""
    db = load_db()

    project_name = args.project
    if project_name in db["projects"]:
        print(f"Project '{project_name}' already exists. Use 'update' to modify.", file=sys.stderr)
        sys.exit(1)

    try:
        filing_date = date.fromisoformat(args.filing_date)
    except ValueError:
        print(f"ERROR: Invalid date: {args.filing_date}", file=sys.stderr)
        sys.exit(1)

    project = Project(
        name=project_name,
        filing_date=filing_date,
    )

    db["projects"][project_name] = project.to_dict()
    save_db(db)

    print(f"✅ Project '{project_name}' initialized.")
    print(f"   Filing date (申报): {filing_date}")


def cmd_update(args):
    """Record an event for a project."""
    db = load_db()

    project_name = args.project
    if project_name not in db["projects"]:
        print(f"Project '{project_name}' not found. Use 'init' first.", file=sys.stderr)
        sys.exit(1)

    event = args.event
    if event not in EVENT_TYPES:
        print(f"Unknown event '{event}'. Available: {list(EVENT_TYPES.keys())}",
              file=sys.stderr)
        sys.exit(1)

    try:
        event_date = date.fromisoformat(args.date)
    except ValueError:
        print(f"ERROR: Invalid date: {args.date}", file=sys.stderr)
        sys.exit(1)

    project_data = db["projects"][project_name]
    project_data["events"][event] = str(event_date)

    if args.notes:
        existing_notes = project_data.get("notes", "")
        project_data["notes"] = f"{existing_notes}\n[{event_date}] {args.notes}".strip()

    db["projects"][project_name] = project_data
    save_db(db)

    print(f"✅ Event '{EVENT_TYPES[event]['label']}' recorded for '{project_name}'.")
    print(f"   Date: {event_date}")

    # Show overdue alerts
    project = Project.from_dict(project_data)
    alerts = project.overdue_alerts
    if alerts:
        print("\n⚠️  Alerts:")
        for alert in alerts:
            print(f"   {alert}")


def cmd_status(args):
    """Show detailed status for a project."""
    db = load_db()

    if args.project not in db["projects"]:
        print(f"Project '{args.project}' not found.", file=sys.stderr)
        sys.exit(1)

    project = Project.from_dict(db["projects"][args.project])

    print("=" * 60)
    print(f"  PROJECT STATUS: {project.name}")
    print("=" * 60)
    print(f"  Filing Date: {project.filing_date}")
    print(f"  Current Phase: {project.current_phase} ({EVENT_TYPES.get(project.current_phase, {}).get('label', 'Unknown')})")
    print(f"  Events completed: {len(project.events)}/{len(PHASE_ORDER)}")
    print("")
    print("─" * 60)
    print("  EVENT HISTORY")
    print("─" * 60)

    for phase_id in PHASE_ORDER:
        event_info = EVENT_TYPES.get(phase_id, {})
        label = event_info.get("label", phase_id)
        if phase_id in project.events:
            d = project.events[phase_id]
            elapsed = ""
            if isinstance(d, str):
                d = date.fromisoformat(d)
            # Calculate elapsed from filing
            days_from_filing = (d - project.filing_date).days
            elapsed = f" (Day +{days_from_filing})"
            print(f"  ✅ {d}  {label}{elapsed}")
        else:
            # Show expected for current+next phase
            if phase_id == project.current_phase:
                print(f"  ⏳ PENDING  {label}")
            else:
                print(f"  ⬜          {label}")

    print("")
    print("─" * 60)
    print("  ALERTS")
    print("─" * 60)

    alerts = project.overdue_alerts
    if alerts:
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("  ✅ No overdue items.")

    # Registration expiry countdown
    if "registration" in project.events and "offering" not in project.events:
        reg_date = project.events["registration"]
        if isinstance(reg_date, str):
            reg_date = date.fromisoformat(reg_date)
        expiry = reg_date.replace(year=reg_date.year + 1)
        days_left = (expiry - date.today()).days
        print(f"\n  Registration approval expires: {expiry} ({days_left} days)")
        print(f"  Must complete offering within 12 months of registration (批文有效期)")

    if project.notes:
        print(f"\n  Notes: {project.notes}")

    print("=" * 60)


def cmd_dashboard(args):
    """Show dashboard of all tracked projects."""
    db = load_db()

    if not db["projects"]:
        print("No projects tracked yet. Use 'init' to create one.")
        return

    projects = [Project.from_dict(p) for p in db["projects"].values()]

    print("=" * 80)
    print("  FILING TRACKER DASHBOARD")
    print("=" * 80)
    print(f"  Projects tracked: {len(projects)}")
    print(f"  Date: {date.today()}")
    print("")

    # Summary table
    print(f"  {'Project':<20s} {'Phase':<20s} {'Progress':<12s} {'Alerts':<10s}")
    print(f"  {'─'*20} {'─'*20} {'─'*12} {'─'*10}")

    total_alerts = 0
    for p in projects:
        phase_label = EVENT_TYPES.get(p.current_phase, {}).get("label", p.current_phase)
        progress = f"{len(p.events)}/{len(PHASE_ORDER)}"
        alerts = len(p.overdue_alerts)
        total_alerts += alerts
        alert_str = f"{alerts} ⚠️" if alerts > 0 else "✅"

        print(f"  {p.name:<20s} {phase_label:<20s} {progress:<12s} {alert_str:<10s}")

    print("")

    # Detailed alerts
    if total_alerts > 0:
        print("─" * 80)
        print("  ALL ALERTS")
        print("─" * 80)
        for p in projects:
            for alert in p.overdue_alerts:
                print(f"  [{p.name}] {alert}")

    # Statistics
    print("\n─" * 80)
    print("  HISTORICAL STATISTICS")
    print("─" * 80)

    # Average time between events
    print("\n  Phase Duration Analysis (avg days):")
    phase_durations: Dict[str, List[int]] = {}
    for p in projects:
        sorted_events = sorted(
            [(k, v) for k, v in p.events.items()],
            key=lambda x: PHASE_ORDER.index(x[0]) if x[0] in PHASE_ORDER else 999,
        )
        for i in range(len(sorted_events) - 1):
            curr_phase, curr_date = sorted_events[i]
            next_phase, next_date = sorted_events[i + 1]
            duration = (next_date - curr_date).days
            phase_key = f"{EVENT_TYPES.get(curr_phase, {}).get('label', curr_phase)} → {EVENT_TYPES.get(next_phase, {}).get('label', next_phase)}"
            if phase_key not in phase_durations:
                phase_durations[phase_key] = []
            phase_durations[phase_key].append(duration)

    for phase_key, durations in phase_durations.items():
        avg = sum(durations) / len(durations)
        print(f"    {phase_key}: avg {avg:.0f} days (n={len(durations)})")

    print("\n" + "=" * 80)


def cmd_delete(args):
    """Delete a project from the tracker."""
    db = load_db()

    if args.project not in db["projects"]:
        print(f"Project '{args.project}' not found.", file=sys.stderr)
        sys.exit(1)

    del db["projects"][args.project]
    save_db(db)
    print(f"🗑️  Project '{args.project}' removed from tracker.")


def cmd_list(args):
    """List all tracked projects."""
    db = load_db()

    if not db["projects"]:
        print("No projects tracked.")
        return

    print("Tracked projects:")
    for name in sorted(db["projects"].keys()):
        pdata = db["projects"][name]
        events_count = len(pdata.get("events", {}))
        print(f"  • {name} (filed: {pdata['filing_date']}, {events_count} events)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Track regulatory filing progress for IB projects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  init      Initialize a new project
  update    Record an event for a project
  status    Show detailed status for a project
  dashboard Show all tracked projects
  list      List all tracked projects
  delete    Remove a project

Examples:
  %(prog)s init --project "Project Alpha" --filing-date 2026-01-15
  %(prog)s update --project "Project Alpha" --event hearing --date 2026-06-10
  %(prog)s status --project "Project Alpha"
  %(prog)s dashboard
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # init
    p_init = subparsers.add_parser("init", help="Initialize a new project")
    p_init.add_argument("--project", required=True, help="Project name")
    p_init.add_argument("--filing-date", required=True, help="Filing date (YYYY-MM-DD)")

    # update
    p_update = subparsers.add_parser("update", help="Record an event")
    p_update.add_argument("--project", required=True, help="Project name")
    p_update.add_argument("--event", required=True,
                          choices=list(EVENT_TYPES.keys()),
                          help="Event type")
    p_update.add_argument("--date", required=True, help="Event date (YYYY-MM-DD)")
    p_update.add_argument("--notes", default=None, help="Optional notes")

    # status
    p_status = subparsers.add_parser("status", help="Show project status")
    p_status.add_argument("--project", required=True, help="Project name")

    # dashboard
    subparsers.add_parser("dashboard", help="Show dashboard")

    # list
    subparsers.add_parser("list", help="List all projects")

    # delete
    p_delete = subparsers.add_parser("delete", help="Remove a project")
    p_delete.add_argument("--project", required=True, help="Project name to remove")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "delete":
        cmd_delete(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()