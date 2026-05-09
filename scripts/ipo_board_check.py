#!/usr/bin/env python3
"""
IPO Board Check — Determine which A-share IPO boards a company qualifies for.

Input:
    Revenue, net profit (3Y), market cap estimate, R&D %, patents, industry, NEEQ months.
Output:
    Board-by-board pass/fail with specific standard numbers and fail reasons.

Usage:
    python ipo_board_check.py --revenue 1500 --net-profit-3y 180 --market-cap 3000 \\
        --r-and-d-pct 6.5 --patents 8 --industry "新一代信息技术" --neeq-months 0

    python ipo_board_check.py -f input.json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Data: Board thresholds
# ---------------------------------------------------------------------------

@dataclass
class BoardResult:
    board: str
    passed: bool
    matched_standards: List[str] = field(default_factory=list)
    failed_reasons: List[str] = field(default_factory=list)


STAR_SECTORS = [
    "新一代信息技术", "高端装备", "新材料", "新能源",
    "生物医药", "节能环保",
]

GEM_NEGATIVE_INDUSTRIES = [
    "农、林、牧、渔业", "采矿业", "农副食品加工业", "纺织服装", "纺织业",
    "黑色金属冶炼", "电力、热力生产和供应业", "建筑业",
    "批发和零售业", "交通运输", "住宿和餐饮业",
    "金融业", "房地产业",
]


def check_main_board(revenue: float, net_profit_3y: float, market_cap: float,
                     operating_cf_3y: float, net_profit_1y: float, industry: str) -> BoardResult:
    """Check Main Board (主板) eligibility."""
    result = BoardResult(board="主板", passed=False)
    reasons_ok = []
    reasons_fail = []

    # Standard 1: Net profit 3Y ≥ 300M, OR NP 1Y ≥ 60M AND Revenue 3Y ≥ 3B AND OCF 3Y ≥ 200M
    if net_profit_3y >= 300:
        reasons_ok.append("Std 1a: 3Y cumulative net profit ≥300M")
    elif net_profit_1y >= 60 and revenue >= 3000 and operating_cf_3y >= 200:
        reasons_ok.append("Std 1b: NP 1Y ≥60M + Revenue 3Y ≥3B + OCF 3Y ≥200M")
    else:
        reasons_fail.append(
            "Std 1: Need (NP 3Y ≥300M) OR (NP 1Y ≥60M + 3Y Rev ≥3B + 3Y OCF ≥200M)"
        )

    # Standard 2: NP 3Y ≥ 150M, NP 1Y ≥ 60M, Revenue 1Y ≥ 1B
    if net_profit_3y >= 150 and net_profit_1y >= 60 and revenue >= 1000:
        reasons_ok.append("Std 2: NP 3Y ≥150M + NP 1Y ≥60M + Revenue 1Y ≥1B")
    else:
        reasons_fail.append(
            "Std 2: Need NP 3Y ≥150M + NP 1Y ≥60M + Revenue 1Y ≥1B"
        )

    # Standard 3: Market cap ≥ 8B, Revenue 1Y ≥ 800M, OCF 3Y ≥ 200M
    if market_cap >= 8000 and revenue >= 800 and operating_cf_3y >= 200:
        reasons_ok.append("Std 3: Market cap ≥8B + Revenue 1Y ≥800M + OCF 3Y ≥200M")
    else:
        reasons_fail.append(
            "Std 3: Need Market cap ≥8B + Revenue 1Y ≥800M + OCF 3Y ≥200M"
        )

    if reasons_ok:
        result.passed = True
        result.matched_standards = reasons_ok
    else:
        result.failed_reasons = reasons_fail

    return result


def check_star_board(revenue: float, net_profit_2y: float, market_cap: float,
                     r_and_d_pct: float, patents: int, industry: str,
                     revenue_cagr_3y: float = 0) -> BoardResult:
    """Check STAR Board (科创板) eligibility."""
    result = BoardResult(board="科创板", passed=False)

    # Sector eligibility
    if industry not in STAR_SECTORS:
        result.failed_reasons.append(
            f"Industry '{industry}' not in STAR 6 sectors: {', '.join(STAR_SECTORS)}"
        )
        return result

    # Innovation attributes check (must pass)
    innov_ok = False
    innov_reasons = []

    # R&D check
    rd_pct_ok = r_and_d_pct >= 5.0
    # R&D absolute check (need 3Y cumulative R&D ≥ 60M — approximate from pct * revenue)
    # We use: if r_and_d_pct * revenue * 3 >= 60 (simplified)
    rd_abs_ok = (r_and_d_pct / 100 * revenue * 3) >= 60

    if rd_pct_ok or rd_abs_ok:
        innov_reasons.append("R&D check pass")
    else:
        innov_reasons.append(f"R&D fail: {r_and_d_pct:.1f}% (<5%) AND 3Y R&D <60M")

    # Patents check
    if patents >= 5:
        innov_reasons.append("Patents check pass (>=5)")
    else:
        innov_reasons.append(f"Patents fail: {patents} (<5)")

    # Revenue growth check
    if revenue_cagr_3y >= 20 or revenue >= 3000:
        innov_reasons.append("Revenue growth/market check pass")
    else:
        innov_reasons.append(f"Revenue fail: CAGR {revenue_cagr_3y:.1f}% (<20%) AND Rev <3B")

    # All three must pass
    innov_ok = (rd_pct_ok or rd_abs_ok) and (patents >= 5) and (revenue_cagr_3y >= 20 or revenue >= 3000)

    if not innov_ok:
        result.failed_reasons.append(f"Innovation attributes NOT met: {'; '.join(innov_reasons)}")
        return result

    reasons_ok = []
    reasons_fail = []

    # Standard 1: Market cap ≥ 1B + NP 2Y ≥ 50M (both years positive) — simplified to: net_profit_2y≥50
    if market_cap >= 1000 and net_profit_2y >= 50:
        reasons_ok.append("Std 1: Market cap ≥1B + NP 2Y cum ≥50M (both years positive)")
    else:
        reasons_fail.append(
            "Std 1: Need Market cap ≥1B + NP 2Y cum ≥50M (both positive)"
        )

    # Standard 2: Market cap ≥1.5B + Revenue 1Y ≥200M + R&D ≥15%
    if market_cap >= 1500 and revenue >= 200 and r_and_d_pct >= 15:
        reasons_ok.append("Std 2: Market cap ≥1.5B + Revenue≥200M + R&D≥15%")
    else:
        reasons_fail.append(
            "Std 2: Need Market cap ≥1.5B + Revenue 1Y ≥200M + R&D ≥15%"
        )

    # Standard 3: Market cap ≥2B + Revenue ≥300M + OCF 3Y ≥100M (approximate)
    if market_cap >= 2000 and revenue >= 300 and (r_and_d_pct / 100 * revenue * 0.15) >= 100:
        reasons_ok.append("Std 3: Market cap ≥2B + Revenue≥300M + OCF ≥100M")
    else:
        reasons_fail.append(
            "Std 3: Need Market cap ≥2B + Revenue 1Y ≥300M + OCF 3Y ≥100M"
        )

    # Standard 4: Market cap ≥3B + Revenue ≥300M
    if market_cap >= 3000 and revenue >= 300:
        reasons_ok.append("Std 4: Market cap ≥3B + Revenue ≥300M")
    else:
        reasons_fail.append(
            "Std 4: Need Market cap ≥3B + Revenue 1Y ≥300M"
        )

    # Standard 5: Market cap ≥4B (pre-revenue)
    if market_cap >= 4000:
        reasons_ok.append("Std 5: Market cap ≥4B + breakthrough technology (pre-revenue)")

    if reasons_ok:
        result.passed = True
        result.matched_standards = reasons_ok

    # If still failing, list reasons
    if not result.passed:
        result.failed_reasons = reasons_fail

    return result


def check_gem_board(revenue: float, net_profit_2y: float, market_cap: float,
                    industry: str, net_profit_1y: float = 0) -> BoardResult:
    """Check ChiNext / GEM (创业板) eligibility."""
    result = BoardResult(board="创业板", passed=False)

    # Negative industry list check
    for neg_ind in GEM_NEGATIVE_INDUSTRIES:
        if neg_ind in industry:
            result.failed_reasons.append(
                f"Industry '{industry}' matches negative list item '{neg_ind}'"
            )
    if result.failed_reasons:
        # Check if "三创四新" override applies (marked in input)
        if "三创四新" not in industry:
            return result
        # If explicitly marked as 三创四新, continue evaluation

    reasons_ok = []
    reasons_fail = []

    # Standard 1: NP 2Y cum ≥50M (both years positive)
    if net_profit_2y >= 50:
        reasons_ok.append("Std 1: NP 2Y cumulative ≥50M")
    else:
        reasons_fail.append(f"Std 1: NP 2Y cumulative needs ≥50M, got {net_profit_2y}M")

    # Standard 2: Market cap ≥1B + NP 1Y ≥100M + Revenue 1Y ≥100M
    if market_cap >= 1000 and net_profit_1y >= 100 and revenue >= 100:
        reasons_ok.append("Std 2: Market cap ≥1B + NP 1Y ≥100M + Revenue ≥100M")
    else:
        reasons_fail.append(
            f"Std 2: Need MCap ≥1B+NP≥100M+Rev≥100M (MCap={market_cap}M,NP={net_profit_1y}M,Rev={revenue}M)"
        )

    # Standard 3: Market cap ≥5B + Revenue ≥300M
    if market_cap >= 5000 and revenue >= 300:
        reasons_ok.append("Std 3: Market cap ≥5B + Revenue ≥300M")
    else:
        reasons_fail.append(
            f"Std 3: Need MCap ≥5B+Rev≥300M (MCap={market_cap}M,Rev={revenue}M)"
        )

    if reasons_ok:
        result.passed = True
        result.matched_standards = reasons_ok
    else:
        result.failed_reasons = reasons_fail

    return result


def check_bse_board(revenue: float, net_profit_2y: float, market_cap: float,
                    neeq_months: int, r_and_d_pct: float = 0,
                    revenue_cagr_3y: float = 0) -> BoardResult:
    """Check BSE (北交所) eligibility."""
    result = BoardResult(board="北交所", passed=False)

    # Prerequisite: NEEQ Innovation Layer ≥ 12 months
    if neeq_months < 12:
        result.failed_reasons.append(
            f"NEEQ Innovation Layer requirement: need ≥12 months, got {neeq_months} months"
        )
        return result

    reasons_ok = []
    reasons_fail = []

    # Standard 1: Market cap ≥200M + NP 2Y ≥15M + ROE 2Y avg ≥8%
    # (ROE simplified — using NP/revenue as proxy if not provided separately)
    if market_cap >= 200 and net_profit_2y >= 15:
        reasons_ok.append("Std 1: Market cap ≥200M + NP 2Y ≥15M (+ ROE check)")
    else:
        reasons_fail.append(
            f"Std 1: Need MCap ≥200M+NP 2Y ≥15M (MCap={market_cap}M,NP 2Y={net_profit_2y}M)"
        )

    # Standard 2: Market cap ≥400M + Revenue 2Y avg ≥100M + Revenue CAGR ≥30%
    if market_cap >= 400 and revenue >= 200 and revenue_cagr_3y >= 30:
        reasons_ok.append("Std 2: MCap ≥400M + Rev 2Y avg ≥100M + Rev CAGR ≥30%")
    else:
        reasons_fail.append(
            f"Std 2: Need MCap ≥400M+Rev≥200M+CAGR≥30% (MCap={market_cap}M,Rev={revenue}M,CAGR={revenue_cagr_3y}%)"
        )

    # Standard 3: Market cap ≥800M + Revenue ≥200M + R&D ≥8%
    if market_cap >= 800 and revenue >= 200 and r_and_d_pct >= 8:
        reasons_ok.append("Std 3: MCap ≥800M + Rev ≥200M + R&D ≥8%")
    else:
        reasons_fail.append(
            f"Std 3: Need MCap ≥800M+Rev≥200M+R&D≥8% (MCap={market_cap}M,Rev={revenue}M,R&D={r_and_d_pct}%)"
        )

    # Standard 4: Market cap ≥1.5B (pre-revenue)
    if market_cap >= 1500:
        reasons_ok.append("Std 4: MCap ≥1.5B (+ R&D requirements, pre-revenue)")

    if reasons_ok:
        result.passed = True
        result.matched_standards = reasons_ok
    else:
        result.failed_reasons = reasons_fail

    return result


def format_report(results: List[BoardResult]) -> str:
    """Format board check results as readable report."""
    lines = ["=" * 70, "IPO BOARD ELIGIBILITY REPORT", "=" * 70, ""]

    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        lines.append(f"  {r.board}: {status}")

        if r.passed:
            for std in r.matched_standards:
                lines.append(f"    ↳ {std}")
            if r.failed_reasons:
                lines.append(f"    Note: Other standards not met — {len(r.failed_reasons)}")
        else:
            for reason in r.failed_reasons:
                lines.append(f"    ✗ {reason}")

        lines.append("")

    lines.append("—" * 70)

    # Summary
    passed = [r.board for r in results if r.passed]
    failed = [r.board for r in results if not r.passed]
    lines.append(f"Eligible:   {', '.join(passed) if passed else 'None'}")
    lines.append(f"Ineligible: {', '.join(failed) if failed else 'None'}")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check A-share IPO board eligibility for a company.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --revenue 1500 --net-profit-3y 200 --market-cap 3000 \\
      --r-and-d-pct 6.5 --patents 8 --industry "新一代信息技术" --neeq-months 0

  %(prog)s -f company_data.json

JSON format:
  {"revenue": 1500, "net_profit_3y": 200, "market_cap": 3000,
   "r_and_d_pct": 6.5, "patents": 8, "industry": "新一代信息技术",
   "neeq_months": 0, "operating_cf_3y": 250, "net_profit_1y": 80,
   "revenue_cagr_3y": 22.0}
        """,
    )

    # CLI argument group
    group = parser.add_argument_group("Company Data")
    group.add_argument("--revenue", type=float, default=0,
                       help="Most recent year revenue (RMB in millions)")
    group.add_argument("--net-profit-3y", type=float, default=0,
                       help="3-year cumulative net profit (RMB in millions)")
    group.add_argument("--net-profit-2y", type=float, default=0,
                       help="2-year cumulative net profit (RMB in millions)")
    group.add_argument("--net-profit-1y", type=float, default=0,
                       help="Most recent year net profit (RMB in millions)")
    group.add_argument("--market-cap", type=float, default=0,
                       help="Estimated market cap (RMB in millions)")
    group.add_argument("--r-and-d-pct", type=float, default=0,
                       help="R&D expenditure as %% of revenue (recent 3 years)")
    group.add_argument("--patents", type=int, default=0,
                       help="Number of invention patents forming core revenue")
    group.add_argument("--industry", type=str, default="",
                       help="Company industry classification (Chinese name)")
    group.add_argument("--neeq-months", type=int, default=0,
                       help="Months listed on NEEQ Innovation Layer")
    group.add_argument("--operating-cf-3y", type=float, default=0,
                       help="3-year cumulative operating cash flow (RMB in millions)")
    group.add_argument("--revenue-cagr-3y", type=float, default=0,
                       help="3-year revenue CAGR (percentage)")

    # JSON input option
    parser.add_argument("-f", "--file", type=str,
                        help="JSON file with company data")

    # Output options
    parser.add_argument("-j", "--json", action="store_true",
                        help="Output as JSON")

    args = parser.parse_args()

    # Load data
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        revenue = float(data.get("revenue", 0))
        net_profit_3y = float(data.get("net_profit_3y", 0))
        net_profit_2y = float(data.get("net_profit_2y", 0))
        net_profit_1y = float(data.get("net_profit_1y", 0))
        market_cap = float(data.get("market_cap", 0))
        r_and_d_pct = float(data.get("r_and_d_pct", 0))
        patents = int(data.get("patents", 0))
        industry = str(data.get("industry", ""))
        neeq_months = int(data.get("neeq_months", 0))
        operating_cf_3y = float(data.get("operating_cf_3y", 0))
        revenue_cagr_3y = float(data.get("revenue_cagr_3y", 0))
    else:
        revenue = args.revenue
        net_profit_3y = args.net_profit_3y
        net_profit_2y = args.net_profit_2y
        net_profit_1y = args.net_profit_1y
        market_cap = args.market_cap
        r_and_d_pct = args.r_and_d_pct
        patents = args.patents
        industry = args.industry
        neeq_months = args.neeq_months
        operating_cf_3y = args.operating_cf_3y
        revenue_cagr_3y = args.revenue_cagr_3y

    # Default net_profit_2y from net_profit_3y if not provided
    if net_profit_2y == 0 and net_profit_3y > 0:
        net_profit_2y = net_profit_3y * 0.67  # rough estimate

    # Validate inputs
    if revenue <= 0 and market_cap <= 0:
        print("ERROR: At minimum, --revenue or --market-cap must be provided.", file=sys.stderr)
        sys.exit(1)

    # Run checks
    results = [
        check_main_board(revenue, net_profit_3y, market_cap, operating_cf_3y,
                         max(net_profit_1y, net_profit_3y / 3), industry),
        check_star_board(revenue, net_profit_2y, market_cap, r_and_d_pct, patents,
                         industry, revenue_cagr_3y),
        check_gem_board(revenue, net_profit_2y, market_cap, industry,
                        max(net_profit_1y, net_profit_2y / 2)),
        check_bse_board(revenue, net_profit_2y, market_cap, neeq_months,
                        r_and_d_pct, revenue_cagr_3y),
    ]

    if args.json:
        output = []
        for r in results:
            output.append({
                "board": r.board,
                "passed": r.passed,
                "matched_standards": r.matched_standards,
                "failed_reasons": r.failed_reasons,
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_report(results))


if __name__ == "__main__":
    main()