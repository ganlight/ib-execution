#!/usr/bin/env python3
"""
Bond Pricing & Analytics Calculator.

Computes full bond analytics from standard inputs using discounted-cash-flow
bond mathematics.  Handles both annual and semi-annual coupon bonds with
arbitrary settlement dates.

Outputs:
  Dirty price, clean price, accrued interest
  Macaulay / modified duration, convexity
  Current yield
  Cash-flow schedule (date, coupon, principal, PV)

Usage:
  python bond_pricing_calc.py --face-value 100 --coupon-rate 3.5 \\
      --frequency 2 --maturity-years 5 --ytm 4.2 \\
      --settlement-days 0

  python bond_pricing_calc.py --json --face-value 100 --coupon-rate 3.5 \\
      --frequency 2 --maturity-years 5 --ytm 4.2
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Core bond math
# ---------------------------------------------------------------------------

def bond_cash_flows(
    face_value: float,
    coupon_rate: float,       # annual % (e.g. 3.5 means 3.5%)
    frequency: int,           # 1 = annual, 2 = semi-annual
    maturity_years: float,
    settlement_date: date,
) -> List[Tuple[date, float, float]]:
    """
    Return list of (payment_date, coupon, principal) cash flows.

    All cash flows *after* the settlement date are included.  If settlement
    falls between coupon dates, the next coupon is a full-period payment.
    """
    n_periods = round(maturity_years * frequency)
    if n_periods < 1:
        raise ValueError("Maturity must yield at least one remaining period.")

    coupon_per_period = face_value * (coupon_rate / 100.0) / frequency

    # Work backwards from maturity
    maturity_date = settlement_date + timedelta(days=round(maturity_years * 365))
    flows: List[Tuple[date, float, float]] = []

    for p in range(n_periods, 0, -1):
        days_back = round((p / frequency) * 365)
        pay_date = settlement_date + timedelta(days=days_back)
        if pay_date <= settlement_date:
            continue
        principal = face_value if p == n_periods else 0.0
        flows.append((pay_date, coupon_per_period, principal))

    flows.sort(key=lambda x: x[0])
    return flows


def accrued_interest(
    face_value: float,
    coupon_rate: float,
    frequency: int,
    settlement_date: date,
    last_coupon_date: date,
) -> float:
    """Accrued interest since last coupon date, per bond unit."""
    coupon_per_period = face_value * (coupon_rate / 100.0) / frequency
    days_in_period = 365.0 / frequency
    days_since = (settlement_date - last_coupon_date).days
    if days_since < 0:
        return 0.0
    days_since = min(days_since, days_in_period)
    return coupon_per_period * (days_since / days_in_period)


def compute_analytics(
    face_value: float,
    coupon_rate: float,
    frequency: int,
    maturity_years: float,
    ytm: float,
    settlement_days_from_now: int = 0,
) -> dict:
    """
    Compute full bond analytics.

    Returns a dictionary with all pricing, duration, convexity, and cash-flow data.
    """
    today = date.today()
    settlement_date = today + timedelta(days=settlement_days_from_now)

    # Determine last coupon date (the most recent before or on settlement)
    coupon_interval_days = 365.0 / frequency
    n_periods = round(maturity_years * frequency)
    maturity_date = settlement_date + timedelta(days=round(maturity_years * 365))

    # Walk back from maturity to find coupon dates
    coupon_dates: List[date] = []
    for p in range(n_periods, 0, -1):
        cd = settlement_date + timedelta(days=round((p / frequency) * 365))
        coupon_dates.append(cd)
    coupon_dates.sort()

    # Last coupon date is the most recent coupon date <= settlement
    past_coupons = [d for d in coupon_dates if d <= settlement_date]
    last_coupon_date = past_coupons[-1] if past_coupons else (
        settlement_date - timedelta(days=round(coupon_interval_days))
    )

    # Accrued interest
    ai = accrued_interest(face_value, coupon_rate, frequency, settlement_date, last_coupon_date)

    # Cash flows after settlement
    flows = bond_cash_flows(face_value, coupon_rate, frequency, maturity_years, settlement_date)

    # Periodic YTM
    ytm_periodic = (ytm / 100.0) / frequency

    # Discount cash flows
    acc_frac = (settlement_date - last_coupon_date).days / coupon_interval_days
    acc_frac = min(max(acc_frac, 0.0), 1.0)

    total_pv = 0.0
    weighted_time_pv = 0.0
    convexity_sum = 0.0
    total_coupon_pv = 0.0
    cash_flow_detail: List[Dict] = []

    for idx, (pay_date, cpn, prin) in enumerate(flows, 1):
        # Time in years and periods from settlement to cash flow
        t_years = (pay_date - settlement_date).days / 365.0
        t_periods = t_years * frequency
        discount_factor = (1.0 + ytm_periodic) ** t_periods
        pv = (cpn + prin) / discount_factor
        total_pv += pv
        weighted_time_pv += t_years * pv
        convexity_sum += pv * t_years * (t_years + 1.0 / frequency)
        total_coupon_pv += cpn / discount_factor

        cash_flow_detail.append({
            "period": idx,
            "date": pay_date.isoformat(),
            "days_from_settlement": (pay_date - settlement_date).days,
            "coupon": round(cpn, 6),
            "principal": round(prin, 6),
            "total_cf": round(cpn + prin, 6),
            "discount_factor": round(discount_factor, 8),
            "present_value": round(pv, 6),
        })

    dirty_price = total_pv
    clean_price = dirty_price - ai

    # Duration
    macaulay_duration = weighted_time_pv / dirty_price if dirty_price else 0.0
    modified_duration = macaulay_duration / (1.0 + ytm_periodic) if dirty_price else 0.0

    # Convexity
    convexity = convexity_sum / (dirty_price * (1.0 + ytm_periodic) ** 2) if dirty_price else 0.0

    # Current yield
    annual_coupon = face_value * (coupon_rate / 100.0)
    current_yield = annual_coupon / dirty_price * 100 if dirty_price else 0.0

    return {
        "inputs": {
            "face_value": face_value,
            "coupon_rate_pct": coupon_rate,
            "frequency": frequency,
            "frequency_label": "Annual" if frequency == 1 else "Semi-annual",
            "maturity_years": maturity_years,
            "ytm_pct": ytm,
            "settlement_days_from_now": settlement_days_from_now,
            "settlement_date": settlement_date.isoformat(),
            "maturity_date": maturity_date.isoformat(),
            "last_coupon_date": last_coupon_date.isoformat(),
        },
        "results": {
            "dirty_price": round(dirty_price, 6),
            "clean_price": round(clean_price, 6),
            "accrued_interest": round(ai, 6),
            "macaulay_duration_years": round(macaulay_duration, 4),
            "modified_duration_years": round(modified_duration, 4),
            "convexity": round(convexity, 4),
            "current_yield_pct": round(current_yield, 4),
        },
        "cash_flows": cash_flow_detail,
    }


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------

def print_analytics(result: dict) -> None:
    """Pretty-print the analytics as formatted tables."""
    inp = result["inputs"]
    res = result["results"]
    cf = result["cash_flows"]

    # ---- Input summary ----
    print("=" * 72)
    print("  BOND PRICING & ANALYTICS")
    print("=" * 72)
    print(f"  Face Value:        {inp['face_value']:>14.2f}")
    print(f"  Coupon Rate:       {inp['coupon_rate_pct']:>13.4f} %")
    print(f"  Frequency:         {inp['frequency_label']:>14s}")
    print(f"  Maturity:          {inp['maturity_years']:>13.2f} yr")
    print(f"  YTM:               {inp['ytm_pct']:>13.4f} %")
    print(f"  Settlement:        {inp['settlement_date']:>14s}")
    print(f"  Maturity Date:     {inp['maturity_date']:>14s}")
    print(f"  Last Coupon:       {inp['last_coupon_date']:>14s}")
    print("-" * 72)

    # ---- Pricing ----
    print(f"  {'Dirty Price:':<24s} {res['dirty_price']:>12.6f}")
    print(f"  {'Accrued Interest:':<24s} {res['accrued_interest']:>12.6f}")
    print(f"  {'Clean Price:':<24s} {res['clean_price']:>12.6f}")
    print()

    # ---- Risk metrics ----
    print(f"  {'Macaulay Duration:':<24s} {res['macaulay_duration_years']:>8.4f} yr")
    print(f"  {'Modified Duration:':<24s} {res['modified_duration_years']:>8.4f} yr")
    print(f"  {'Convexity:':<24s} {res['convexity']:>8.4f}")
    print(f"  {'Current Yield:':<24s} {res['current_yield_pct']:>8.4f} %")
    print()

    # ---- Cash-flow schedule ----
    print("-" * 72)
    print(f"  CASH-FLOW SCHEDULE  ({len(cf)} periods)")
    print("-" * 72)
    header = (
        f"  {'#':>3s}  {'Date':>12s}  "
        f"{'Coupon':>10s}  {'Principal':>10s}  "
        f"{'Total CF':>10s}  {'PV':>10s}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))

    for row in cf:
        print(
            f"  {row['period']:3d}  {row['date']:>12s}  "
            f"{row['coupon']:10.4f}  {row['principal']:10.4f}  "
            f"{row['total_cf']:10.4f}  {row['present_value']:10.4f}"
        )
    print("=" * 72)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Pricing and analytics calculator for plain-vanilla fixed-rate bonds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --face-value 100 --coupon-rate 3.5 --frequency 2 \\
      --maturity-years 5 --ytm 4.2

  %(prog)s --face-value 100 --coupon-rate 4.0 --frequency 1 \\
      --maturity-years 10 --ytm 3.8 --settlement-days 60

  %(prog)s --json --face-value 100 --coupon-rate 3.5 \\
      --frequency 2 --maturity-years 5 --ytm 4.2
        """,
    )
    p.add_argument("--face-value", type=float, default=100.0,
                   help="Par / face value per bond unit (default: 100)")
    p.add_argument("--coupon-rate", type=float, required=True,
                   help="Annual coupon rate in %% (e.g. 3.5)")
    p.add_argument("--frequency", type=int, default=2,
                   choices=[1, 2], help="Coupon frequency: 1=annual, 2=semi-annual (default: 2)")
    p.add_argument("--maturity-years", type=float, required=True,
                   help="Remaining time to maturity in years")
    p.add_argument("--ytm", type=float, required=True,
                   help="Yield-to-maturity in %% (e.g. 4.2)")
    p.add_argument("--settlement-days", type=int, default=0,
                   help="Settlement days from today (default: 0 = today)")
    p.add_argument("--json", dest="json_out", action="store_true",
                   help="Output JSON instead of formatted text")
    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.frequency == 2 and args.maturity_years < 0.5:
        parser.error("Semi-annual maturity must yield at least 1 remaining period (≥0.5 yr).")
    if args.frequency == 1 and args.maturity_years < 1.0:
        parser.error("Annual maturity must yield at least 1 remaining period (≥1.0 yr).")
    if args.ytm < -99.0 or args.ytm > 99.0:
        parser.error("YTM seems unreasonable; check input.")
    if args.coupon_rate < 0:
        parser.error("Coupon rate must be non-negative.")

    try:
        result = compute_analytics(
            face_value=args.face_value,
            coupon_rate=args.coupon_rate,
            frequency=args.frequency,
            maturity_years=args.maturity_years,
            ytm=args.ytm,
            settlement_days_from_now=args.settlement_days,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json_out:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print_analytics(result)


if __name__ == "__main__":
    main()