#!/usr/bin/env python3
"""
Bond Cashflow Coverage Calculator & Repayment Schedule Generator.

Computes debt service coverage ratios (DSCR) period-by-period, generates a
full repayment schedule, and performs sensitivity analysis for Chinese bond
issuance scenarios.

Supports three repayment types:
  - bullet:      Principal repaid at maturity
  - amortizing:  Equal principal amortization each period
  - sinking_fund: User-specified sinking fund schedule

Outputs:
  - Interest and principal payments per period
  - Total debt service per period
  - DSCR (period-by-period)
  - Average / minimum DSCR, DSCR volatility
  - Coverage assessment (强 / 充足 / 偏紧 / 不足 / 缺口)
  - Cash coverage ratio (optional, with cash balance)
  - Full repayment schedule table
  - Sensitivity analysis (±100bp rate, -10%/-20% cashflows)

Usage:
  python bond_cashflow_cover.py --file input.json

  python bond_cashflow_cover.py --amount 1000000000 --coupon 4.2 --tenor 5 \\
      --type bullet --cashflows 2.5e8,2.8e8,3.0e8,3.2e8,3.5e8 \\
      --existing 1.8e8,1.5e8,1.2e8,1.0e8,8e7

  python bond_cashflow_cover.py --json --file input.json
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BondInput:
    """Bond issuance parameters."""
    bond_amount: float           # 发行规模（元）
    coupon_rate: float           # 票面利率（%）
    tenor: int                   # 期限（年）
    repayment_type: str          # bullet / amortizing / sinking_fund
    sinking_schedule: List[float] = field(default_factory=list)  # 偿债基金每期还本比例
    frequency: int = 1           # 付息频率（次/年）
    projected_cashflows: List[float] = field(default_factory=list)  # 各期可用于偿债的现金流
    existing_debt_service: List[float] = field(default_factory=list)  # 现有债务各期还本付息
    cash_balance: Optional[float] = None  # 货币资金余额（元）


@dataclass
class PeriodResult:
    """Computed results for a single period."""
    period: int
    beginning_balance: float     # 期初本金余额
    interest_payment: float      # 利息支出
    principal_payment: float     # 本金偿还
    total_debt_service: float    # 本期偿债额（仅本债券）
    total_all_debt_service: float  # 总偿债额（含现有债务）
    projected_cashflow: float    # 可用于偿债的现金流
    dscr: float                  # 偿债覆盖率
    cash_coverage: Optional[float] = None  # 含货币资金的覆盖率
    ending_balance: float = 0.0  # 期末本金余额


@dataclass
class SensitivityRow:
    """One scenario in the sensitivity analysis."""
    scenario: str
    rate_change_bps: float
    cf_change_pct: float
    dscr_values: List[float] = field(default_factory=list)
    avg_dscr: float = 0.0
    min_dscr: float = 0.0


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def compute_principal_schedule(inp: BondInput) -> List[float]:
    """Calculate principal repayment per period based on repayment type.

    Args:
        inp: Bond input parameters.

    Returns:
        List of principal amounts to repay each period.

    Raises:
        ValueError: If repayment_type is unknown or sinking_schedule is mis-specified.
    """
    n = inp.tenor * inp.frequency

    if inp.repayment_type == "bullet":
        principal = [0.0] * n
        principal[-1] = inp.bond_amount
        return principal

    elif inp.repayment_type == "amortizing":
        annual_payment = inp.bond_amount / n
        return [round(annual_payment, 2)] * n

    elif inp.repayment_type == "sinking_fund":
        if not inp.sinking_schedule or len(inp.sinking_schedule) != inp.tenor:
            raise ValueError(
                f"sinking_schedule must have {inp.tenor} entries, "
                f"got {len(inp.sinking_schedule) if inp.sinking_schedule else 0}"
            )
        total_ratio = sum(inp.sinking_schedule)
        if abs(total_ratio - 1.0) > 0.01:
            raise ValueError(
                f"sinking_schedule ratios must sum to 1.0, got {total_ratio:.4f}"
            )
        # Distribute per-period: each year's ratio split evenly across frequency
        result: List[float] = []
        for year_ratio in inp.sinking_schedule:
            per_period = round(inp.bond_amount * year_ratio / inp.frequency, 2)
            for _ in range(inp.frequency):
                result.append(per_period)
        # Adjust last entry for rounding
        diff = inp.bond_amount - sum(result)
        if diff != 0:
            result[-1] += diff
        return result

    else:
        raise ValueError(
            f"Unknown repayment_type: {inp.repayment_type}. "
            f"Use bullet, amortizing, or sinking_fund."
        )


def compute_interest_schedule(inp: BondInput, principal_schedule: List[float]) -> List[float]:
    """Calculate interest payment per period based on remaining principal.

    Args:
        inp: Bond input parameters.
        principal_schedule: List of principal repayments per period.

    Returns:
        List of interest payments per period.
    """
    n = len(principal_schedule)
    coupon_per_period = inp.coupon_rate / 100.0 / inp.frequency
    interest: List[float] = []
    remaining = inp.bond_amount

    for i in range(n):
        int_pmt = round(remaining * coupon_per_period, 2)
        interest.append(int_pmt)
        remaining -= principal_schedule[i]
        remaining = max(remaining, 0.0)

    return interest


def compute_period_results(inp: BondInput,
                           interest: List[float],
                           principal: List[float]) -> List[PeriodResult]:
    """Compute full period-by-period DSCR analysis.

    Args:
        inp: Bond input parameters.
        interest: Interest payments per period.
        principal: Principal payments per period.

    Returns:
        List of PeriodResult for each period.
    """
    n = len(principal)
    results: List[PeriodResult] = []
    remaining = inp.bond_amount

    for i in range(n):
        period = i + 1
        total_this_bond = interest[i] + principal[i]

        # Total debt service including existing
        existing = inp.existing_debt_service[i] if i < len(inp.existing_debt_service) else 0.0
        total_all = total_this_bond + existing

        # Projected cashflow
        cf = inp.projected_cashflows[i] if i < len(inp.projected_cashflows) else 0.0

        # DSCR
        dscr = round(cf / total_all, 4) if total_all > 0 else float('inf')

        # Cash coverage
        cash_cov: Optional[float] = None
        if inp.cash_balance is not None:
            cash_cov = round((cf + inp.cash_balance) / total_all, 4) if total_all > 0 else float('inf')

        remaining -= principal[i]
        remaining = max(remaining, 0.0)

        results.append(PeriodResult(
            period=period,
            beginning_balance=round(inp.bond_amount if i == 0 else remaining + principal[i], 2),
            interest_payment=interest[i],
            principal_payment=principal[i],
            total_debt_service=total_this_bond,
            total_all_debt_service=total_all,
            projected_cashflow=cf,
            dscr=dscr,
            cash_coverage=cash_cov,
            ending_balance=round(remaining, 2),
        ))

    return results


def compute_dscr_stats(results: List[PeriodResult]) -> Dict:
    """Calculate aggregate DSCR statistics.

    Args:
        results: Period-by-period results.

    Returns:
        Dictionary with avg_dscr, min_dscr, min_period, volatility, assessment.
    """
    dscrs = [r.dscr for r in results if r.dscr != float('inf')]
    if not dscrs:
        return {
            "avg_dscr": 0.0,
            "min_dscr": 0.0,
            "min_period": None,
            "volatility": 0.0,
            "assessment": "无法评估",
            "assessment_grade": "N/A",
        }

    avg = round(statistics.mean(dscrs), 4)
    mn = min(dscrs)
    min_idx = dscrs.index(mn) + 1
    vol = round(statistics.stdev(dscrs), 4) if len(dscrs) >= 2 else 0.0

    # Assessment
    if mn > 2.0:
        grade, label = "A", "强 — 偿债能力很强，覆盖充裕"
    elif mn > 1.5:
        grade, label = "B", "充足 — 偿债能力良好，覆盖充足"
    elif mn > 1.2:
        grade, label = "C", "偏紧 — 偿债能力偏紧，需关注现金流波动"
    elif mn >= 1.0:
        grade, label = "D", "不足 — 偿债能力勉强覆盖，风险较高"
    else:
        grade, label = "E", "缺口 — 偿债缺口，需增信或调整融资方案"

    return {
        "avg_dscr": avg,
        "min_dscr": mn,
        "min_period": min_idx,
        "volatility": vol,
        "assessment": label,
        "assessment_grade": grade,
    }


def run_sensitivity(inp: BondInput,
                    base_interest: List[float],
                    base_principal: List[float],
                    base_results: List[PeriodResult]) -> List[SensitivityRow]:
    """Run sensitivity analysis: rate ±100bp, cashflow -10%/-20%.

    Args:
        inp: Original bond input parameters.
        base_interest: Base-case interest schedule.
        base_principal: Base-case principal schedule.
        base_results: Base-case period results.

    Returns:
        List of SensitivityRow for each scenario.
    """
    rows: List[SensitivityRow] = []
    n = len(base_principal)
    base_coupon = inp.coupon_rate

    scenarios = [
        ("基准情景", 0.0, 0.0),
        ("利率+100bp", 1.0, 0.0),
        ("利率-100bp", -1.0, 0.0),
        ("现金流-10%", 0.0, -0.10),
        ("现金流-20%", 0.0, -0.20),
        ("利率+100bp & 现金流-10%", 1.0, -0.10),
        ("利率-100bp & 现金流-20%", -1.0, -0.20),
    ]

    for label, rate_delta, cf_delta in scenarios:
        # Adjusted coupon rate
        adj_coupon = base_coupon + rate_delta
        adj_coupon_per_period = adj_coupon / 100.0 / inp.frequency

        # Recompute interest with adjusted rate
        adj_interest: List[float] = []
        remaining = inp.bond_amount
        for i in range(n):
            int_pmt = round(remaining * adj_coupon_per_period, 2)
            adj_interest.append(int_pmt)
            remaining -= base_principal[i]
            remaining = max(remaining, 0.0)

        # Adjusted cashflows
        adj_cf = [round(cf * (1.0 + cf_delta), 2) for cf in inp.projected_cashflows]

        dscrs: List[float] = []
        for i in range(n):
            total_this = adj_interest[i] + base_principal[i]
            existing = inp.existing_debt_service[i] if i < len(inp.existing_debt_service) else 0.0
            total_all = total_this + existing
            cf = adj_cf[i] if i < len(adj_cf) else 0.0
            dscr = round(cf / total_all, 4) if total_all > 0 else float('inf')
            dscrs.append(dscr)

        finite = [d for d in dscrs if d != float('inf')]
        rows.append(SensitivityRow(
            scenario=label,
            rate_change_bps=rate_delta * 100,
            cf_change_pct=cf_delta * 100,
            dscr_values=dscrs,
            avg_dscr=round(statistics.mean(finite), 4) if finite else 0.0,
            min_dscr=round(min(finite), 4) if finite else 0.0,
        ))

    return rows


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------

def _sep(char: str = "=", width: int = 74) -> str:
    return char * width


def _format_money(val: float) -> str:
    """Format a float as 亿 representation."""
    yi = val / 1e8
    if yi >= 1:
        return f"{yi:,.4f}亿 ({val:,.0f}元)"
    wan = val / 1e4
    if wan >= 1:
        return f"{wan:,.2f}万 ({val:,.0f}元)"
    return f"{val:,.0f}元"


def _dscr_bar(val: float, width: int = 20) -> str:
    """Draw a simple ASCII bar for DSCR."""
    if val == float('inf'):
        return "∞"
    fill = min(int(val * 4), width)  # scale so 2.0 → 8 blocks
    fill = max(fill, 0)
    bar = "█" * fill + "░" * (width - fill)
    return f"{bar} {val:.3f}"


def _repayment_type_cn(rtype: str) -> str:
    """Return Chinese label for repayment type."""
    return {
        "bullet": "到期一次还本",
        "amortizing": "等额还本",
        "sinking_fund": "偿债基金",
    }.get(rtype, rtype)


def print_analysis(inp: BondInput, results: List[PeriodResult],
                   dscr_stats: Dict, sensitivity: List[SensitivityRow]) -> None:
    """Pretty-print the full DSCR analysis."""
    n = len(results)

    # ---- Header ----
    print(_sep())
    print("  债券偿债覆盖率分析 (DSCR Analysis)")
    print(_sep())
    print(f"  发行规模:     {_format_money(inp.bond_amount)}")
    print(f"  票面利率:     {inp.coupon_rate:.2f}%")
    print(f"  期限:         {inp.tenor}年 ({n}期)")
    print(f"  还本方式:     {_repayment_type_cn(inp.repayment_type)}")
    print(f"  付息频率:     每年{inp.frequency}次")
    if inp.repayment_type == "sinking_fund":
        print(f"  偿债基金安排: {', '.join(f'{r:.0%}' for r in inp.sinking_schedule)}")
    if inp.cash_balance is not None:
        print(f"  货币资金余额: {_format_money(inp.cash_balance)}")
    print()

    # ---- Repayment Schedule Table ----
    print(_sep("-"))
    print("  还款计划时间表 (Repayment Schedule)")
    print(_sep("-"))
    header = (
        f"  {'期':>3s}  {'期初本金':>12s}  {'利息':>12s}  {'本金':>12s}  "
        f"{'本债偿债':>12s}  {'总偿债额':>12s}  {'可用现金流':>12s}  {'DSCR':>8s}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))

    for r in results:
        print(
            f"  {r.period:3d}  {r.beginning_balance:>12,.0f}  "
            f"{r.interest_payment:>12,.0f}  {r.principal_payment:>12,.0f}  "
            f"{r.total_debt_service:>12,.0f}  {r.total_all_debt_service:>12,.0f}  "
            f"{r.projected_cashflow:>12,.0f}  {r.dscr:>8.3f}"
        )
    total_interest = sum(r.interest_payment for r in results)
    total_principal = sum(r.principal_payment for r in results)
    print(
        f"  {'合计':>3s}  {'':>12s}  "
        f"{total_interest:>12,.0f}  {total_principal:>12,.0f}  "
        f"{total_interest + total_principal:>12,.0f}"
    )

    # ---- DSCR Summary ----
    print()
    print(_sep("-"))
    print("  DSCR 统计摘要")
    print(_sep("-"))
    print(f"  逐期DSCR:      {', '.join(f'{r.dscr:.3f}' for r in results)}")
    print(f"  平均DSCR:      {dscr_stats['avg_dscr']:.3f}")
    print(f"  最低DSCR:      {dscr_stats['min_dscr']:.3f} (第{dscr_stats['min_period']}期)")
    print(f"  DSCR波动率:    {dscr_stats['volatility']:.3f}")
    print()
    print(f"  覆盖评估:      {dscr_stats['assessment']}")
    print(f"  等级:          {dscr_stats['assessment_grade']}")

    # Cash coverage (if provided)
    if inp.cash_balance is not None:
        cash_covs = [r.cash_coverage for r in results if r.cash_coverage is not None]
        if cash_covs:
            c_avg = statistics.mean(cash_covs) if cash_covs else 0.0
            c_min = min(cash_covs) if cash_covs else 0.0
            print()
            print(f"  含货币资金覆盖率(平均): {c_avg:.3f}")
            print(f"  含货币资金覆盖率(最低): {c_min:.3f}")

    # ---- Sensitivity ----
    print()
    print(_sep("-"))
    print("  敏感性分析 (Sensitivity Analysis)")
    print(_sep("-"))
    sens_header = (
        f"  {'情景':<28s}  {'逐期DSCR':<30s}  {'平均':>7s}  {'最低':>7s}"
    )
    print(sens_header)
    print("  " + "-" * (len(sens_header) - 2))
    for row in sensitivity:
        dscr_str = ", ".join(f"{d:.2f}" for d in row.dscr_values[:6])
        if len(row.dscr_values) > 6:
            dscr_str += ", …"
        print(
            f"  {row.scenario:<28s}  {dscr_str:<30s}  "
            f"{row.avg_dscr:>7.3f}  {row.min_dscr:>7.3f}"
        )

    # ---- DSCR bar chart ----
    print()
    print(_sep("-"))
    print("  DSCR 可视化")
    print(_sep("-"))
    for row in sensitivity:
        print(f"  {row.scenario:<28s}  {_dscr_bar(row.min_dscr)}")

    print(_sep())


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def json_output(inp: BondInput, results: List[PeriodResult],
                dscr_stats: Dict, sensitivity: List[SensitivityRow]) -> None:
    """Output full structured data as JSON."""
    payload = {
        "inputs": {
            "bond_amount": inp.bond_amount,
            "coupon_rate_pct": inp.coupon_rate,
            "tenor_years": inp.tenor,
            "frequency": inp.frequency,
            "repayment_type": inp.repayment_type,
            "repayment_type_cn": _repayment_type_cn(inp.repayment_type),
            "sinking_schedule": inp.sinking_schedule if inp.repayment_type == "sinking_fund" else None,
            "projected_cashflows": inp.projected_cashflows,
            "existing_debt_service": inp.existing_debt_service,
            "cash_balance": inp.cash_balance,
        },
        "repayment_schedule": [
            {
                "period": r.period,
                "beginning_balance": r.beginning_balance,
                "interest_payment": r.interest_payment,
                "principal_payment": r.principal_payment,
                "total_debt_service": r.total_debt_service,
                "total_all_debt_service": r.total_all_debt_service,
                "projected_cashflow": r.projected_cashflow,
                "dscr": r.dscr,
                "cash_coverage": r.cash_coverage,
                "ending_balance": r.ending_balance,
            }
            for r in results
        ],
        "dscr_statistics": dscr_stats,
        "sensitivity_analysis": [
            {
                "scenario": s.scenario,
                "rate_change_bps": s.rate_change_bps,
                "cf_change_pct": s.cf_change_pct,
                "dscr_values": s.dscr_values,
                "avg_dscr": s.avg_dscr,
                "min_dscr": s.min_dscr,
            }
            for s in sensitivity
        ],
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# Input parsing helpers
# ---------------------------------------------------------------------------

def _parse_number_list(raw: str) -> List[float]:
    """Parse a comma-separated list of numbers with scientific notation support.

    2.5e8,2.8e8 → [250000000.0, 280000000.0]
    """
    result: List[float] = []
    for part in raw.split(","):
        part = part.strip()
        # Try 亿 suffix
        if part.endswith("亿"):
            result.append(float(part[:-1]) * 1e8)
        else:
            result.append(float(part))
    return result


def _load_from_file(filepath: str) -> BondInput:
    """Load bond inputs from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {filepath}: {exc}", file=sys.stderr)
        sys.exit(1)

    return BondInput(
        bond_amount=float(data["bond_amount"]),
        coupon_rate=float(data["coupon_rate"]),
        tenor=int(data["tenor"]),
        repayment_type=str(data["repayment_type"]),
        sinking_schedule=[float(x) for x in data.get("sinking_schedule", [])],
        frequency=int(data.get("frequency", 1)),
        projected_cashflows=[float(x) for x in data.get("projected_cashflows", [])],
        existing_debt_service=[float(x) for x in data.get("existing_debt_service", [])],
        cash_balance=float(data["cash_balance"]) if "cash_balance" in data else None,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="债券偿债覆盖率计算器 (Bond DSCR Calculator & Repayment Scheduler)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file input.json

  %(prog)s --amount 1000000000 --coupon 4.2 --tenor 5 --type bullet \\
      --cashflows 2.5e8,2.8e8,3.0e8,3.2e8,3.5e8 \\
      --existing 1.8e8,1.5e8,1.2e8,1.0e8,8e7

  %(prog)s --json --amount 500000000 --coupon 3.8 --tenor 3 \\
      --type bullet --cashflows 3e8,3.5e8,5.5e8 --existing 1e8,8e7,0

  %(prog)s --amount 1e9 --coupon 4.5 --tenor 5 --type amortizing \\
      --cashflows 3e8,3.2e8,3.4e8,3.6e8,3.8e8 --existing 1.5e8,1.2e8,1e8,8e7,5e7 \\
      --cash-balance 2e8
        """,
    )

    input_group = p.add_mutually_exclusive_group()
    input_group.add_argument("--file", dest="file_path",
                             help="Path to JSON input file")

    # Command-line direct inputs
    p.add_argument("--amount", type=float,
                   help="发行规模（元），支持 1e9 / 10亿")
    p.add_argument("--coupon", type=float,
                   help="票面利率（%%），如 4.2")
    p.add_argument("--tenor", type=int,
                   help="期限（年）")
    p.add_argument("--type", dest="repay_type",
                   choices=["bullet", "amortizing", "sinking_fund"],
                   help="还本方式")
    p.add_argument("--sinking", dest="sinking",
                   help="偿债基金每期比例，逗号分隔，如 0,0,0.3,0.3,0.4")
    p.add_argument("--frequency", type=int, default=1,
                   help="付息频率（次/年），默认1")
    p.add_argument("--cashflows",
                   help="各期可用于偿债的现金流（元），逗号分隔，支持 2.5e8 格式")
    p.add_argument("--existing",
                   help="现有债务各期还本付息（元），逗号分隔")
    p.add_argument("--cash-balance", type=float,
                   help="货币资金余额（元）")
    p.add_argument("--json", dest="json_out", action="store_true",
                   help="Output JSON instead of formatted text")
    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Load inputs
    if args.file_path:
        inp = _load_from_file(args.file_path)
        # If other args provided, they override file values
        if args.amount is not None:
            inp.bond_amount = args.amount
        if args.coupon is not None:
            inp.coupon_rate = args.coupon
        if args.tenor is not None:
            inp.tenor = args.tenor
        if args.repay_type is not None:
            inp.repayment_type = args.repay_type
        if args.cashflows is not None:
            inp.projected_cashflows = _parse_number_list(args.cashflows)
        if args.existing is not None:
            inp.existing_debt_service = _parse_number_list(args.existing)
        if args.cash_balance is not None:
            inp.cash_balance = args.cash_balance
    elif args.amount is not None:
        inp = BondInput(
            bond_amount=args.amount,
            coupon_rate=args.coupon or 0.0,
            tenor=args.tenor or 1,
            repayment_type=args.repay_type or "bullet",
            sinking_schedule=(
                [float(x) for x in args.sinking.split(",")] if args.sinking else []
            ),
            frequency=args.frequency,
            projected_cashflows=(
                _parse_number_list(args.cashflows) if args.cashflows else []
            ),
            existing_debt_service=(
                _parse_number_list(args.existing) if args.existing else []
            ),
            cash_balance=args.cash_balance,
        )
    else:
        parser.print_help()
        sys.exit(1)

    # Validate
    if inp.bond_amount <= 0:
        parser.error("bond_amount must be positive")
    if inp.tenor < 1:
        parser.error("tenor must be >= 1")
    if inp.coupon_rate < 0:
        parser.error("coupon_rate must be >= 0")
    expected = inp.tenor * inp.frequency
    if len(inp.projected_cashflows) < expected:
        print(f"Warning: projected_cashflows has {len(inp.projected_cashflows)} entries, "
              f"expected {expected}", file=sys.stderr)
    if inp.existing_debt_service and len(inp.existing_debt_service) < expected:
        print(f"Warning: existing_debt_service has {len(inp.existing_debt_service)} entries, "
              f"expected {expected}", file=sys.stderr)

    # Compute
    try:
        principal = compute_principal_schedule(inp)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    interest = compute_interest_schedule(inp, principal)
    results = compute_period_results(inp, interest, principal)
    dscr_stats = compute_dscr_stats(results)
    sensitivity = run_sensitivity(inp, interest, principal, results)

    # Output
    if args.json_out:
        json_output(inp, results, dscr_stats, sensitivity)
    else:
        print_analysis(inp, results, dscr_stats, sensitivity)


# ---------------------------------------------------------------------------
# Built-in test cases (run with: python bond_cashflow_cover.py --test)
# ---------------------------------------------------------------------------

_TEST_CASES: List[Dict] = [
    # Test 1: Amortizing, 5yr 10亿, coupon 4.5%
    {
        "label": "等额还本 (amortizing)，5年10亿，票面4.5%，现金流充足",
        "args": [
            "--amount", "1e9",
            "--coupon", "4.5",
            "--tenor", "5",
            "--type", "amortizing",
            "--cashflows", "3.5e8,3.3e8,3.1e8,2.9e8,2.7e8",
            "--existing", "1.5e8,1.3e8,1.1e8,9e7,7e7",
            "--cash-balance", "2e8",
        ],
    },
    # Test 2: Bullet, 3yr 5亿, coupon 3.8%, 现金流充足
    {
        "label": "到期一次还本 (bullet)，3年5亿，票面3.8%，现金流充足",
        "args": [
            "--amount", "5e8",
            "--coupon", "3.8",
            "--tenor", "3",
            "--type", "bullet",
            "--cashflows", "3e8,3.5e8,5.8e8",
            "--existing", "1e8,8e7,5e7",
        ],
    },
    # Test 3: Sinking fund, 5yr 15亿, coupon 4.2%, DSCR 接近 1.0
    {
        "label": "偿债基金 (sinking_fund)，5年15亿，票面4.2%，现金流偏紧",
        "args": [
            "--amount", "1.5e9",
            "--coupon", "4.2",
            "--tenor", "5",
            "--type", "sinking_fund",
            "--sinking", "0.10,0.15,0.20,0.25,0.30",
            "--cashflows", "2.8e8,2.5e8,2.9e8,3.2e8,3.1e8",
            "--existing", "1.6e8,1.5e8,1.4e8,1.3e8,1.2e8",
        ],
    },
]


def run_tests() -> None:
    """Exercise the calculator with built-in test cases."""
    for i, case in enumerate(_TEST_CASES, 1):
        print(f"\n{'='*74}")
        print(f"  TEST CASE {i}: {case['label']}")
        print(f"{'='*74}")
        main(case["args"])
        print()


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        run_tests()
    else:
        main()