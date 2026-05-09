#!/usr/bin/env python3
"""
Document Version Diff — Compare two versions of an IB document.

Compares document versions line-by-line for regulatory feedback responses.
Outputs added/deleted/modified paragraphs, change statistics, and a comparison
table in markdown format suitable for CSRC/exchange inquiry response appendices.

Usage:
    python doc_version_diff.py v1_draft.md v2_amended.md
    python doc_version_diff.py v1.txt v2.txt -o diff_report.md
    python doc_version_diff.py old.txt new.txt --json --context 3
"""

import argparse
import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class ChangeType(Enum):
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class Change:
    change_type: ChangeType
    old_lines: List[str] = field(default_factory=list)
    new_lines: List[str] = field(default_factory=list)
    old_start: int = 0      # line number in v1
    new_start: int = 0      # line number in v2
    old_end: int = 0
    new_end: int = 0
    summary: str = ""       # brief description

    @property
    def added_count(self) -> int:
        return len(self.new_lines) if self.change_type == ChangeType.ADDED else 0

    @property
    def deleted_count(self) -> int:
        return len(self.old_lines) if self.change_type == ChangeType.DELETED else 0

    @property
    def modified_count(self) -> int:
        return max(len(self.old_lines), len(self.new_lines)) if self.change_type == ChangeType.MODIFIED else 0


@dataclass
class DiffResult:
    v1_path: str
    v2_path: str
    v1_lines: int
    v2_lines: int
    changes: List[Change] = field(default_factory=list)
    total_added: int = 0
    total_deleted: int = 0
    total_modified: int = 0
    total_unchanged: int = 0


# ---------------------------------------------------------------------------
# Core diff logic
# ---------------------------------------------------------------------------

def load_file(path: str) -> List[str]:
    """Load file and return lines."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except UnicodeDecodeError:
        # Try GBK encoding (common for Chinese documents)
        with open(path, "r", encoding="gbk") as f:
            return f.readlines()


def is_meaningful_change(old_block: List[str], new_block: List[str]) -> bool:
    """Determine if a change block is meaningful (not just whitespace/formatting)."""
    if not old_block or not new_block:
        return True

    # Strip whitespace for comparison
    old_clean = [l.strip() for l in old_block if l.strip()]
    new_clean = [l.strip() for l in new_block if l.strip()]

    if old_clean == new_clean:
        return False  # Only whitespace changes
    if not old_clean and not new_clean:
        return False  # All blank lines
    return True


def summarize_change(old_lines: List[str], new_lines: List[str], change_type: ChangeType) -> str:
    """Generate a brief summary of the change."""
    if change_type == ChangeType.ADDED and new_lines:
        first = new_lines[0].strip()
        return f"Added {len(new_lines)} line(s): '{first[:80]}'"
    elif change_type == ChangeType.DELETED and old_lines:
        first = old_lines[0].strip()
        return f"Deleted {len(old_lines)} line(s): '{first[:80]}'"
    elif change_type == ChangeType.MODIFIED:
        return f"Modified {max(len(old_lines), len(new_lines))} line(s)"
    return "No change"


def group_changes(smdiff: difflib.SequenceMatcher) -> List[Change]:
    """Group opcode changes into coherent Change blocks."""
    changes: List[Change] = []

    for tag, i1, i2, j1, j2 in smdiff.get_opcodes():
        if tag == "equal":
            continue

        old_lines = smdiff.a[i1:i2] if smdiff.a else []
        new_lines = smdiff.b[j1:j2] if smdiff.b else []

        if tag == "insert":
            ct = ChangeType.ADDED
        elif tag == "delete":
            ct = ChangeType.DELETED
        elif tag == "replace":
            # Determine if it's a modification or add+delete
            if len(old_lines) <= 3 and len(new_lines) <= 3:
                ct = ChangeType.MODIFIED
            elif abs(len(old_lines) - len(new_lines)) <= 2:
                ct = ChangeType.MODIFIED
            else:
                ct = ChangeType.MODIFIED  # treat all replaces as modified for simplicity
        else:
            continue

        if not is_meaningful_change(old_lines, new_lines):
            continue

        changes.append(Change(
            change_type=ct,
            old_lines=old_lines,
            new_lines=new_lines,
            old_start=i1 + 1,  # 1-indexed
            old_end=i2,
            new_start=j1 + 1,
            new_end=j2,
            summary=summarize_change(old_lines, new_lines, ct),
        ))

    return changes


def compute_diff(v1_path: str, v2_path: str) -> DiffResult:
    """Compute the full diff between two document versions."""
    old_lines_raw = load_file(v1_path)
    new_lines_raw = load_file(v2_path)

    # Normalize: remove trailing newlines for comparison but keep for display
    old_lines = [l.rstrip("\n").rstrip("\r") for l in old_lines_raw]
    new_lines = [l.rstrip("\n").rstrip("\r") for l in new_lines_raw]

    sm = difflib.SequenceMatcher(None, old_lines, new_lines)
    changes = group_changes(sm)

    # Statistics
    total_added = sum(1 for c in changes if c.change_type == ChangeType.ADDED for _ in c.new_lines)
    total_deleted = sum(1 for c in changes if c.change_type == ChangeType.DELETED for _ in c.old_lines)
    total_modified = sum(1 for c in changes if c.change_type == ChangeType.MODIFIED)

    result = DiffResult(
        v1_path=v1_path,
        v2_path=v2_path,
        v1_lines=len(old_lines),
        v2_lines=len(new_lines),
        changes=changes,
        total_added=total_added,
        total_deleted=total_deleted,
        total_modified=total_modified,
        total_unchanged=len(old_lines) - total_deleted,
    )

    return result


# ---------------------------------------------------------------------------
# Formatting output
# ---------------------------------------------------------------------------

def _color_block(lines: List[str], color: str, prefix: str) -> List[str]:
    """Colorize a block of lines with ANSI codes."""
    colors = {"green": "\033[92m", "red": "\033[91m", "yellow": "\033[93m", "reset": "\033[0m"}
    code = colors.get(color, "")
    return [f"{code}{prefix}{line}{colors['reset']}" for line in lines]


def format_text_output(result: DiffResult, show_color: bool = True) -> str:
    """Format diff as human-readable text with optional ANSI colors."""
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("  DOCUMENT VERSION COMPARISON")
    lines.append("=" * 78)
    lines.append(f"  Version 1 (old): {result.v1_path} ({result.v1_lines} lines)")
    lines.append(f"  Version 2 (new): {result.v2_path} ({result.v2_lines} lines)")
    lines.append("")

    # Statistics
    lines.append("─" * 78)
    lines.append("  CHANGE STATISTICS")
    lines.append("─" * 78)
    change_count = len(result.changes)
    lines.append(f"  Total change blocks: {change_count}")
    lines.append(f"  Lines added (🟢):    {result.total_added}")
    lines.append(f"  Lines deleted (🔴):  {result.total_deleted}")
    lines.append(f"  Modified blocks (🟡):{result.total_modified}")
    net_change = result.total_added - result.total_deleted
    sign = "+" if net_change >= 0 else ""
    lines.append(f"  Net line change:     {sign}{net_change}")
    lines.append("")

    # Detailed changes
    if not result.changes:
        lines.append("  ✅ No changes detected. Documents are identical.")
    else:
        lines.append("─" * 78)
        lines.append("  DETAILED CHANGES")
        lines.append("─" * 78)
        lines.append("")

        for i, change in enumerate(result.changes, 1):
            ct = change.change_type
            emoji = {"added": "🟢 ADDED", "deleted": "🔴 DELETED", "modified": "🟡 MODIFIED"}.get(ct.value, "??")
            lines.append(f"  [{i}] {emoji} (v1: L{change.old_start}-{change.old_end}, v2: L{change.new_start}-{change.new_end})")
            lines.append(f"       {change.summary}")

            if ct == ChangeType.ADDED:
                for line in change.new_lines[:8]:  # limit display
                    lines.append(f"       + {line.strip()[:100]}")
                if len(change.new_lines) > 8:
                    lines.append(f"       ... ({len(change.new_lines) - 8} more lines)")

            elif ct == ChangeType.DELETED:
                for line in change.old_lines[:8]:
                    lines.append(f"       - {line.strip()[:100]}")
                if len(change.old_lines) > 8:
                    lines.append(f"       ... ({len(change.old_lines) - 8} more lines)")

            elif ct == ChangeType.MODIFIED:
                lines.append("       OLD → NEW:")
                for old_l, new_l in zip(change.old_lines[:4], change.new_lines[:4]):
                    lines.append(f"       - {old_l.strip()[:80]}")
                    lines.append(f"       + {new_l.strip()[:80]}")

            lines.append("")

    lines.append("=" * 78)
    return "\n".join(lines)


def format_markdown_report(result: DiffResult) -> str:
    """Format diff as a markdown report suitable for regulatory feedback responses."""
    lines: List[str] = []
    lines.append(f"# 招股说明书修订对照表")
    lines.append(f"")
    lines.append(f"**申报稿 (V1):** `{result.v1_path}` ({result.v1_lines} 行)  ")
    lines.append(f"**修订稿 (V2):** `{result.v2_path}` ({result.v2_lines} 行)")
    lines.append(f"")

    # Statistics section
    lines.append(f"## 修订统计")
    lines.append(f"")
    lines.append(f"| 修订类型 | 数量 |")
    lines.append(f"|---|---|")
    lines.append(f"| 新增段落 | {result.total_added} |")
    lines.append(f"| 删除段落 | {result.total_deleted} |")
    lines.append(f"| 修订段落 | {result.total_modified} |")
    lines.append(f"| **合计修订处** | **{len(result.changes)}** |")
    lines.append(f"")

    if not result.changes:
        lines.append("> ✅ 无修订。两个版本一致。")
        return "\n".join(lines)

    # Detailed comparison table
    lines.append(f"## 详细修订对照表")
    lines.append(f"")
    lines.append(f"| 序号 | 修订类型 | 申报稿（V1）行号 | 修订稿（V2）行号 | 修订说明 |")
    lines.append(f"|---|---|---|---|---|")
    lines.append(f"| 序号 | 修订类型 | 申报稿（V1）行号 | 修订稿（V2）行号 | 修订说明 |")
    lines.append(f"")

    for i, change in enumerate(result.changes, 1):
        ct = change.change_type
        type_cn = {"added": "新增", "deleted": "删除", "modified": "修订"}.get(ct.value, "修订")

        v1_range = f"L{change.old_start}-{change.old_end}" if change.old_start else "—"
        v2_range = f"L{change.new_start}-{change.new_end}" if change.new_start else "—"

        desc = change.summary.replace("'", "").replace('"', "")
        if len(desc) > 60:
            desc = desc[:57] + "..."

        lines.append(f"| {i} | {type_cn} | {v1_range} | {v2_range} | {desc} |")
    lines.append(f"")

    # Section-by-section changes
    lines.append(f"## 各章节修订内容")
    lines.append(f"")

    for i, change in enumerate(result.changes, 1):
        ct = change.change_type
        emoji = {"added": "🟢", "deleted": "🔴", "modified": "🟡"}.get(ct.value, "⚪")
        headers = {ct.value: ct.value.upper()}

        lines.append(f"### {emoji} 修订 #{i}: {change.summary[:80]}")
        lines.append(f"")

        if ct == ChangeType.DELETED and change.old_lines:
            lines.append(f"**修订前（V1，已删除）:**")
            lines.append(f"```")
            for line in change.old_lines[:10]:
                lines.append(line.strip()[:120])
            lines.append(f"```")
            lines.append(f"")

        elif ct == ChangeType.ADDED and change.new_lines:
            lines.append(f"**修订后（V2，新增）:**")
            lines.append(f"```")
            for line in change.new_lines[:10]:
                lines.append(line.strip()[:120])
            lines.append(f"```")
            lines.append(f"")

        elif ct == ChangeType.MODIFIED:
            lines.append(f"**修订前（V1）:**")
            lines.append(f"```")
            for line in change.old_lines[:6]:
                lines.append(line.strip()[:120])
            lines.append(f"```")
            lines.append(f"")
            lines.append(f"**修订后（V2）:**")
            lines.append(f"```")
            for line in change.new_lines[:6]:
                lines.append(line.strip()[:120])
            lines.append(f"```")
            lines.append(f"")

        lines.append(f"**修订说明:** {change.summary}")
        lines.append(f"")

    lines.append("---")
    lines.append("*本对照表由 doc_version_diff.py 自动生成*")
    return "\n".join(lines)


def format_json_output(result: DiffResult) -> str:
    """Format diff as JSON."""
    data = {
        "v1_path": result.v1_path,
        "v2_path": result.v2_path,
        "v1_lines": result.v1_lines,
        "v2_lines": result.v2_lines,
        "statistics": {
            "blocks_added": result.total_added,
            "blocks_deleted": result.total_deleted,
            "blocks_modified": result.total_modified,
            "loC_total_changes": len(result.changes),
        },
        "changes": [
            {
                "index": i,
                "type": c.change_type.value,
                "v1_range": [c.old_start, c.old_end],
                "v2_range": [c.new_start, c.new_end],
                "summary": c.summary,
                "old_text_preview": " ".join(l.strip()[:100] for l in c.old_lines[:3]),
                "new_text_preview": " ".join(l.strip()[:100] for l in c.new_lines[:3]),
                "old_line_count": len(c.old_lines),
                "new_line_count": len(c.new_lines),
            }
            for i, c in enumerate(result.changes, 1)
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare two versions of an IB document for regulatory "
                    "feedback response appendices.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Formats:
  --text       ANSI-colored text summary (default when no flags)
  --markdown   Markdown comparison table for CSRC/exchange inquiry appendix
  --json       Machine-readable JSON

Examples:
  %(prog)s draft_v1.txt amended_v1.txt
  %(prog)s old.txt new.txt --markdown -o revision_table.md
  %(prog)s v1.txt v2.txt --json
  %(prog)s old.txt new.txt --text --no-color
        """,
    )

    parser.add_argument("v1", help="Path to older version of document")
    parser.add_argument("v2", help="Path to newer version of document")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--markdown", action="store_true", dest="fmt_md",
                        help="Output as markdown revision comparison table")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI color codes in text output")
    parser.add_argument("--statistics-only", action="store_true",
                        help="Show only statistics, not detailed changes")

    args = parser.parse_args()

    # Compute diff
    try:
        result = compute_diff(args.v1, args.v2)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine output format
    fmt: str
    if args.json:
        fmt = "json"
    elif args.fmt_md:
        fmt = "markdown"
    else:
        fmt = "text"

    # Format output
    output: str
    if fmt == "json":
        output = format_json_output(result)
    elif fmt == "markdown":
        output = format_markdown_report(result)
    else:
        output = format_text_output(result, show_color=not args.no_color)

    # Write
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Diff report written to {args.output}")
    else:
        print(output)

    # Quick summary to stderr
    print(
        f"\n  Summary: +{result.total_added} added, -{result.total_deleted} deleted, "
        f"~{result.total_modified} modified blocks",
        file=sys.stderr,
    )

    # Exit code
    if len(result.changes) == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()