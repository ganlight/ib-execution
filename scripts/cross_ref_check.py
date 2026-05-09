#!/usr/bin/env python3
"""
Cross-Reference Data Consistency Checker for IB Documents.

Checks data consistency across the audit report, prospectus text, and legal
opinion for key financial and legal data points. Reports discrepancies with
specific value differences and source references.

Usage:
    python cross_ref_check.py --audit audit.json --prospectus prospectus.txt \\
        --legal legal_opinion.json

    python cross_ref_check.py --audit audit.json --prospectus prospectus.txt \\
        --legal legal_opinion.json --output report.md
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    check_id: str
    label: str
    passed: bool
    sources: Dict[str, float] = field(default_factory=dict)
    discrepancies: List[str] = field(default_factory=list)


@dataclass
class CrossRefReport:
    product_type: str
    results: List[CheckResult] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_numbers_from_text(text: str, keywords: List[str]) -> Dict[str, List[float]]:
    """Extract numeric values near given keywords from text.

    Returns dict mapping keyword to list of nearby numbers found.
    """
    result: Dict[str, List[float]] = {}
    lines = text.split("\n")
    for kw in keywords:
        result[kw] = []
        for line in lines:
            if kw in line:
                # Find all numbers in the line (in millions / 万元 / 亿元)
                numbers = re.findall(r'[\d,]+\.?\d*', line)
                for n in numbers:
                    try:
                        val = float(n.replace(",", ""))
                        if val > 0.01:
                            result[kw].append(val)
                    except ValueError:
                        pass
    return result


def load_audit_data(path: str) -> Dict[str, Any]:
    """Load and normalize audit report JSON data."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_legal_data(path: str) -> Dict[str, Any]:
    """Load and normalize legal opinion JSON data."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_prospectus_text(path: str) -> str:
    """Load prospectus as raw text."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Core check functions
# ---------------------------------------------------------------------------

def get_audit_value(data: dict, *keys, unit: str = "CNY_M") -> Optional[float]:
    """Safely navigate nested dict to get a numeric value."""
    val = data
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        elif isinstance(val, list) and isinstance(k, int):
            val = val[k] if k < len(val) else None
        else:
            return None
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def extract_prospectus_value(text: str, patterns: List[str]) -> Optional[float]:
    """Try multiple regex patterns to extract a numeric value from prospectus text."""
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except (ValueError, IndexError):
                continue
    return None


def check_net_assets(audit: dict, prospectus_text: str) -> CheckResult:
    """Check net assets consistency."""
    result = CheckResult(check_id="NET_ASSETS", label="Net Assets (净资产)")
    sources: Dict[str, float] = {}

    # From audit report
    audit_val = get_audit_value(audit, "balance_sheet", "net_assets")
    if audit_val is not None:
        sources["audit_report"] = audit_val

    # From prospectus
    patterns = [
        r"净资产[：:]\s*([\d,]+\.?\d*)\s*万",
        r"归属于母公司.*?净资产[：:]\s*([\d,]+\.?\d*)\s*万",
        r"net.?assets.*?([\d,]+\.?\d*)",
        r"归属于.*?股东权益[：:]\s*([\d,]+\.?\d*)\s*万",
    ]
    pros_val = extract_prospectus_value(prospectus_text, patterns)
    if pros_val is not None:
        sources["prospectus"] = pros_val

    # Check consistency
    vals = list(sources.values())
    if len(vals) < 2:
        result.passed = True
        return result

    base = vals[0]
    for i, v in enumerate(vals[1:], 1):
        if abs(base - v) / max(abs(base), 1) > 0.02:  # 2% tolerance
            src_name = list(sources.keys())[i]
            result.discrepancies.append(
                f"Net assets differ: audit={base:.2f}M vs {src_name}={v:.2f}M "
                f"(diff={abs(base - v):.2f}M, {abs(base - v) / max(abs(base), 1) * 100:.1f}%)"
            )

    result.passed = len(result.discrepancies) == 0
    result.sources = sources
    return result


def check_net_profit(audit: dict, prospectus_text: str) -> CheckResult:
    """Check net profit consistency."""
    result = CheckResult(check_id="NET_PROFIT", label="Net Profit (净利润)")
    sources: Dict[str, float] = {}

    audit_val = get_audit_value(audit, "income_statement", "net_profit")
    if audit_val is None:
        # Try list format
        audit_val = get_audit_value(audit, "income_statement", 0, "net_profit")
    if audit_val is not None:
        sources["audit_report"] = audit_val

    patterns = [
        r"净利润[：:]\s*([\d,]+\.?\d*)\s*万",
        r"归属于.*?净利润[：:]\s*([\d,]+\.?\d*)\s*万",
        r"net.?profit.*?([\d,]+\.?\d*)",
    ]
    pros_val = extract_prospectus_value(prospectus_text, patterns)
    if pros_val is not None:
        sources["prospectus"] = pros_val

    vals = list(sources.values())
    if len(vals) < 2:
        result.passed = True
        return result

    base = vals[0]
    for i, v in enumerate(vals[1:], 1):
        if abs(base - v) / max(abs(base), 1) > 0.01:
            src_name = list(sources.keys())[i]
            result.discrepancies.append(
                f"Net profit differs: audit={base:.2f}M vs {src_name}={v:.2f}M"
            )

    result.passed = len(result.discrepancies) == 0
    result.sources = sources
    return result


def check_revenue(audit: dict, prospectus_text: str) -> CheckResult:
    """Check revenue consistency."""
    result = CheckResult(check_id="REVENUE", label="Revenue (营业收入)")
    sources: Dict[str, float] = {}

    audit_val = get_audit_value(audit, "income_statement", "revenue")
    if audit_val is not None:
        sources["audit_report"] = audit_val

    patterns = [
        r"营业收入[：:]\s*([\d,]+\.?\d*)\s*万",
        r"营业总收入[：:]\s*([\d,]+\.?\d*)\s*万",
        r"revenue.*?([\d,]+\.?\d*)",
    ]
    pros_val = extract_prospectus_value(prospectus_text, patterns)
    if pros_val is not None:
        sources["prospectus"] = pros_val

    vals = list(sources.values())
    if len(vals) < 2:
        result.passed = True
        return result

    base = vals[0]
    for i, v in enumerate(vals[1:], 1):
        if abs(base - v) / max(abs(base), 1) > 0.01:
            src_name = list(sources.keys())[i]
            result.discrepancies.append(
                f"Revenue differs: audit={base:.2f}M vs {src_name}={v:.2f}M"
            )

    result.passed = len(result.discrepancies) == 0
    result.sources = sources
    return result


def check_related_party(audit: dict, prospectus_text: str) -> CheckResult:
    """Check related party amounts consistency."""
    result = CheckResult(check_id="RELATED_PARTY", label="Related Party Transactions")
    sources: Dict[str, float] = {}

    # From audit footnote
    rpt_items = get_audit_value(audit, "footnote", "rpt_revenue")
    if isinstance(rpt_items, list):
        total = sum(
            float(item.get("amount", 0)) if isinstance(item, dict) else 0
            for item in rpt_items
        )
        if total > 0:
            sources["audit_report"] = total
    elif isinstance(rpt_items, (int, float)):
        sources["audit_report"] = float(rpt_items)

    patterns = [
        r"关联.*?销售[：:]\s*([\d,]+\.?\d*)\s*万",
        r"关联交易.*?金额[：:]\s*([\d,]+\.?\d*)\s*万",
        r"关联方.*?收入[：:]\s*([\d,]+\.?\d*)\s*万",
    ]
    pros_val = extract_prospectus_value(prospectus_text, patterns)
    if pros_val is not None:
        sources["prospectus"] = pros_val

    vals = list(sources.values())
    result.passed = len(vals) <= 1 or (len(vals) > 1 and abs(vals[0] - vals[1]) / max(abs(vals[0]), 1) <= 0.05)

    if len(vals) > 1 and abs(vals[0] - vals[1]) / max(abs(vals[0]), 1) > 0.05:
        result.discrepancies.append(
            f"RPT amounts differ: audit={vals[0]:.2f}M vs prospectus={vals[1]:.2f}M"
        )

    result.sources = sources
    return result


def check_guarantees(audit: dict, legal: Optional[dict], prospectus_text: str) -> CheckResult:
    """Check guarantee amounts consistency."""
    result = CheckResult(check_id="GUARANTEES", label="Guarantee Amounts")
    sources: Dict[str, float] = {}

    # Audit
    g_items = get_audit_value(audit, "footnote", "guarantees")
    if isinstance(g_items, list):
        total = sum(
            float(item.get("amount", 0)) if isinstance(item, dict) else 0
            for item in g_items
        )
        if total > 0:
            sources["audit_report"] = total

    # Legal opinion
    if legal:
        lg = get_audit_value(legal, "section_10", "guarantees")
        if isinstance(lg, list):
            total = sum(
                float(item.get("amount", 0)) if isinstance(item, dict) else 0
                for item in lg
            )
            if total > 0:
                sources["legal_opinion"] = total
        elif isinstance(lg, (int, float)):
            sources["legal_opinion"] = float(lg)

    # Prospectus
    patterns = [
        r"对外担保.*?([\d,]+\.?\d*)\s*万",
        r"担保.*?余额[：:]\s*([\d,]+\.?\d*)\s*万",
    ]
    pros_val = extract_prospectus_value(prospectus_text, patterns)
    if pros_val is not None:
        sources["prospectus"] = pros_val

    vals = list(sources.values())
    if len(vals) >= 2:
        base = vals[0]
        for i, v in enumerate(vals[1:], 1):
            if abs(base - v) / max(abs(base), 1) > 0.05:
                result.discrepancies.append(
                    f"Guarantee amounts differ: {list(sources.keys())[0]}={base:.2f}M "
                    f"vs {list(sources.keys())[i]}={v:.2f}M"
                )

    result.passed = len(result.discrepancies) == 0
    result.sources = sources
    return result


def check_litigation(legal: Optional[dict], prospectus_text: str) -> CheckResult:
    """Check litigation amounts consistency."""
    result = CheckResult(check_id="LITIGATION", label="Litigation Amounts")
    sources: Dict[str, float] = {}

    if legal:
        lit = get_audit_value(legal, "section_9", "litigation_amount")
        if lit is not None:
            sources["legal_opinion"] = lit

    patterns = [
        r"诉讼.*?涉及金额[：:]\s*([\d,]+\.?\d*)\s*万",
        r"未决诉讼.*?金额[：:]\s*([\d,]+\.?\d*)\s*万",
    ]
    pros_val = extract_prospectus_value(prospectus_text, patterns)
    if pros_val is not None:
        sources["prospectus"] = pros_val

    vals = list(sources.values())
    if len(vals) >= 2 and abs(vals[0] - vals[1]) / max(abs(vals[0]), 1) > 0.05:
        result.discrepancies.append(
            f"Litigation amounts differ: legal={vals[0]:.2f}M vs prospectus={vals[1]:.2f}M"
        )

    result.passed = len(result.discrepancies) == 0
    result.sources = sources
    return result


def check_investment(prospectus_text: str) -> CheckResult:
    """Check use-of-proceeds: total raise vs sum of project costs."""
    result = CheckResult(check_id="INVESTMENT", label="Use of Proceeds (募集资金)")
    sources: Dict[str, float] = {}

    # Extract total fundraising
    patterns_total = [
        r"募集资金总额[：:]\s*([\d,]+\.?\d*)\s*万",
        r"拟募集资金[：:]\s*([\d,]+\.?\d*)\s*万",
        r"发行新股.*?募集[：:]\s*([\d,]+\.?\d*)\s*万",
    ]
    total = extract_prospectus_value(prospectus_text, patterns_total)
    if total is not None:
        sources["total_fundraise"] = total

    # Extract sum of project costs
    patterns_projects = [
        r"项目.*?投资总额[：:]\s*([\d,]+\.?\d*)\s*万",
        r"合计.*?([\d,]+\.?\d*)\s*万元",
    ]
    # Try to find all project amounts and sum them
    project_amounts = re.findall(r"项目\d.*?(\d[\d,]*\.?\d*)\s*万", prospectus_text)
    if project_amounts:
        total_projects = sum(
            float(a.replace(",", "")) for a in project_amounts if float(a.replace(",", "")) > 100
        )
        if total_projects > 0:
            sources["sum_of_projects"] = total_projects

    vals = list(sources.values())
    if len(vals) >= 2:
        if abs(vals[0] - vals[1]) / max(abs(vals[0]), 1) > 0.05:
            result.discrepancies.append(
                f"Use-of-proceeds mismatch: total={vals[0]:.2f}M vs sum of projects={vals[1]:.2f}M "
                f"(diff={abs(vals[0] - vals[1]):.2f}M)"
            )

    result.passed = len(result.discrepancies) == 0
    result.sources = sources
    return result


def check_capital(audit: dict, legal: Optional[dict], prospectus_text: str) -> CheckResult:
    """Check registered capital consistency."""
    result = CheckResult(check_id="CAPITAL", label="Registered Capital (实收资本)")
    sources: Dict[str, float] = {}

    cap = get_audit_value(audit, "footnote", "equity", "paid_in_capital")
    if cap is not None:
        sources["audit_report"] = cap

    if legal:
        lc = get_audit_value(legal, "section_1", "registered_capital")
        if lc is not None:
            sources["legal_opinion"] = lc

    patterns = [
        r"注册资本[：:]\s*([\d,]+\.?\d*)\s*万",
        r"实收资本[：:]\s*([\d,]+\.?\d*)\s*万",
    ]
    pros_val = extract_prospectus_value(prospectus_text, patterns)
    if pros_val is not None:
        sources["prospectus"] = pros_val

    vals = list(sources.values())
    if len(vals) >= 2:
        if abs(vals[0] - vals[1]) / max(abs(vals[0]), 1) > 0.01:
            result.discrepancies.append(
                f"Capital differs: {list(sources.keys())[0]}={vals[0]:.2f}M "
                f"vs {list(sources.keys())[1]}={vals[1]:.2f}M"
            )

    result.passed = len(result.discrepancies) == 0
    result.sources = sources
    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(results: List[CheckResult]) -> str:
    """Generate markdown report."""
    lines = []
    lines.append("# Cross-Reference Data Consistency Report")
    lines.append("")
    lines.append(f"**Generated:** Automated cross-reference check")
    lines.append("")

    # Summary
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Status | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| ✅ Passed | {passed} |")
    lines.append(f"| ❌ Failed | {failed} |")
    lines.append(f"| **Total** | **{total}** |")
    lines.append("")

    # Details
    lines.append("## Detailed Results")
    lines.append("")

    for r in results:
        icon = "✅" if r.passed else "❌"
        lines.append(f"### {icon} {r.label} (`{r.check_id}`)")
        lines.append("")

        if r.sources:
            lines.append("| Source | Value |")
            lines.append("|---|---|")
            for src, val in r.sources.items():
                lines.append(f"| {src} | {val:,.2f}M |")
            lines.append("")

        if r.discrepancies:
            lines.append("**Discrepancies:**")
            for d in r.discrepancies:
                lines.append(f"- ⚠️ {d}")
            lines.append("")
        elif r.passed and len(r.sources) >= 2:
            lines.append("✅ All sources consistent.")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Check data consistency across IB documents (audit report, "
                    "prospectus text, legal opinion).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --audit audit_data.json --prospectus prospectus.txt --legal legal_data.json
  %(prog)s --audit audit_data.json --prospectus prospectus.txt --output report.md
        """,
    )

    parser.add_argument("--audit", required=True, help="Path to audit report JSON")
    parser.add_argument("--prospectus", required=True, help="Path to prospectus text file")
    parser.add_argument("--legal", default=None, help="Path to legal opinion JSON (optional)")
    parser.add_argument("--output", "-o", default=None, help="Output markdown report path")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Load documents
    try:
        audit_data = load_audit_data(args.audit)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR loading audit report: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        prospectus_text = load_prospectus_text(args.prospectus)
    except FileNotFoundError as e:
        print(f"ERROR loading prospectus: {e}", file=sys.stderr)
        sys.exit(1)

    legal_data = None
    if args.legal:
        try:
            legal_data = load_legal_data(args.legal)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"WARNING: Could not load legal opinion: {e}", file=sys.stderr)

    # Run all checks
    results = []

    print("Running cross-reference checks...\n")
    checks = [
        ("Net Assets", lambda: check_net_assets(audit_data, prospectus_text)),
        ("Net Profit", lambda: check_net_profit(audit_data, prospectus_text)),
        ("Revenue", lambda: check_revenue(audit_data, prospectus_text)),
        ("Related Party", lambda: check_related_party(audit_data, prospectus_text)),
        ("Guarantees", lambda: check_guarantees(audit_data, legal_data, prospectus_text)),
        ("Litigation", lambda: check_litigation(legal_data, prospectus_text)),
        ("Use of Proceeds", lambda: check_investment(prospectus_text)),
        ("Capital", lambda: check_capital(audit_data, legal_data, prospectus_text)),
    ]

    for label, check_fn in checks:
        try:
            result = check_fn()
            results.append(result)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"  [{status}] {label}")
            for d in result.discrepancies:
                print(f"    ⚠️  {d}")
        except Exception as e:
            print(f"  [⚠️  ERROR] {label}: {e}")
            # Add a failed result for this check
            error_result = CheckResult(
                check_id=label.upper().replace(" ", "_"),
                label=label,
                passed=False,
                discrepancies=[f"Error during check: {e}"],
            )
            results.append(error_result)

    # Generate output
    if args.json:
        output = []
        for r in results:
            output.append({
                "check_id": r.check_id,
                "label": r.label,
                "passed": r.passed,
                "sources": r.sources,
                "discrepancies": r.discrepancies,
            })
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"\nJSON report written to {args.output}")
        else:
            print(json_str)
    else:
        report = generate_report(results)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\nMarkdown report written to {args.output}")
        else:
            print("\n" + report)

    # Exit code
    if any(not r.passed for r in results):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()