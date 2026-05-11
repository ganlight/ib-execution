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
import math


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
# Newton-Raphson YTM Solver (v1.8)
# ---------------------------------------------------------------------------

def _price_from_ytm(
    face_value: float,
    coupon_rate: float,
    frequency: int,
    maturity_years: float,
    ytm: float,
) -> float:
    """Dirty price via periodic DCF for a given annual-percent YTM."""
    n = round(maturity_years * frequency)
    y_per = (ytm / 100.0) / frequency
    cpn = face_value * (coupon_rate / 100.0) / frequency
    pv = 0.0
    for i in range(1, n + 1):
        cf = cpn + (face_value if i == n else 0.0)
        pv += cf / ((1.0 + y_per) ** i)
    return pv


def _price_dy(
    face_value: float,
    coupon_rate: float,
    frequency: int,
    maturity_years: float,
    ytm: float,
) -> float:
    """Analytical dP/dytm for Newton-Raphson (price change per 1% yield change)."""
    n = round(maturity_years * frequency)
    y_per = (ytm / 100.0) / frequency
    cpn = face_value * (coupon_rate / 100.0) / frequency
    deriv = 0.0
    for i in range(1, n + 1):
        t = i / frequency
        cf = cpn + (face_value if i == n else 0.0)
        pv = cf / ((1.0 + y_per) ** i)
        deriv -= t * pv / (1.0 + y_per) / 100.0
    return deriv


def compute_ytm_nr(
    price: float,
    face_value: float = 100.0,
    coupon_rate: float = 3.5,
    frequency: int = 2,
    maturity_years: float = 5.0,
    initial_guess: float = 5.0,
    precision: float = 0.0001,
    max_iter: int = 100,
) -> Dict:
    """
    Compute YTM via Newton-Raphson iteration with analytical derivative.

    Args:
        price: Market dirty price.
        face_value: Par / face value per bond unit.
        coupon_rate: Annual coupon rate in %.
        frequency: 1 (annual) or 2 (semi-annual).
        maturity_years: Remaining maturity in years.
        initial_guess: Starting YTM guess in % (default 5.0).
        precision: Convergence tolerance in price units (default 0.0001).
        max_iter: Maximum iterations (default 100).

    Returns:
        dict with ytm_pct, iterations, converged, price_error, precision, max_iter.
    """
    if price <= 0:
        raise ValueError("Price must be positive.")

    ytm = float(initial_guess)
    for i in range(max_iter):
        p_est = _price_from_ytm(face_value, coupon_rate, frequency, maturity_years, ytm)
        err = p_est - price
        if abs(err) < precision:
            return {
                "ytm_pct": round(ytm, 6),
                "iterations": i + 1,
                "converged": True,
                "price_error": round(err, 8),
                "precision": precision,
                "max_iter": max_iter,
            }
        dp = _price_dy(face_value, coupon_rate, frequency, maturity_years, ytm)
        if abs(dp) < 1e-15:
            break
        ytm_new = ytm - err / dp
        ytm_new = max(-99.0, min(200.0, ytm_new))
        if abs(ytm_new - ytm) < precision * 0.01:
            p_final = _price_from_ytm(face_value, coupon_rate, frequency, maturity_years, ytm_new)
            return {
                "ytm_pct": round(ytm_new, 6),
                "iterations": i + 1,
                "converged": True,
                "price_error": round(p_final - price, 8),
                "precision": precision,
                "max_iter": max_iter,
            }
        ytm = ytm_new

    p_final = _price_from_ytm(face_value, coupon_rate, frequency, maturity_years, ytm)
    return {
        "ytm_pct": round(ytm, 6),
        "iterations": max_iter,
        "converged": False,
        "price_error": round(p_final - price, 8),
        "precision": precision,
        "max_iter": max_iter,
    }


# ---------------------------------------------------------------------------
# Duration & Convexity Standalone Calculator (v1.8)
# ---------------------------------------------------------------------------

def compute_duration_convexity(
    face_value: float = 100.0,
    coupon_rate: float = 3.5,
    frequency: int = 2,
    maturity_years: float = 5.0,
    ytm: float = 4.0,
) -> Dict:
    """
    Compute Macaulay/Modified duration, convexity, PVBP, and DV01.

    Returns dict with dirty_price, macaulay_duration, modified_duration,
    convexity, dollar_duration, pvbp, dv01, ytm_pct.
    """
    n = round(maturity_years * frequency)
    y_per = (ytm / 100.0) / frequency
    cpn = face_value * (coupon_rate / 100.0) / frequency

    total_pv = 0.0
    w_sum = 0.0      # sum(t * PV_i)
    w2_sum = 0.0     # sum(PV_i * t * (t + 1/f))

    for i in range(1, n + 1):
        t = i / frequency
        cf = cpn + (face_value if i == n else 0.0)
        pv = cf / ((1.0 + y_per) ** i)
        total_pv += pv
        w_sum += t * pv
        w2_sum += pv * t * (t + 1.0 / frequency)

    if total_pv <= 0:
        raise ValueError("Cannot compute duration/convexity: non-positive PV.")

    macaulay = w_sum / total_pv
    modified = macaulay / (1.0 + y_per)
    convexity = w2_sum / (total_pv * (1.0 + y_per) ** 2)
    dollar_duration = modified * total_pv / 100.0
    pvbp = dollar_duration * 0.0001
    dv01 = pvbp

    return {
        "dirty_price": round(total_pv, 6),
        "macaulay_duration": round(macaulay, 4),
        "modified_duration": round(modified, 4),
        "convexity": round(convexity, 4),
        "dollar_duration": round(dollar_duration, 6),
        "pvbp": round(pvbp, 8),
        "dv01": round(dv01, 8),
        "ytm_pct": ytm,
    }


# ---------------------------------------------------------------------------
# Yield Curve Interpolation (v1.8)
# ---------------------------------------------------------------------------

def _solve_tridiagonal(
    a: List[float], b: List[float], c: List[float], d: List[float],
) -> List[float]:
    """
    Solve n×n tridiagonal system: a_i * x_{i-1} + b_i * x_i + c_i * x_{i+1} = d_i.

    a[0] and c[n-1] are unused.  Returns x[0..n-1].
    Uses the Thomas algorithm (pure Python stdlib).
    """
    n = len(b)
    cp = list(c)
    dp = list(d)
    x = [0.0] * n

    for i in range(1, n):
        w = a[i] / b[i - 1] if b[i - 1] != 0 else 0.0
        b[i] -= w * cp[i - 1]
        dp[i] -= w * dp[i - 1]

    x[n - 1] = dp[n - 1] / b[n - 1] if b[n - 1] != 0 else 0.0
    for i in range(n - 2, -1, -1):
        x[i] = (dp[i] - cp[i] * x[i + 1]) / b[i] if b[i] != 0 else 0.0
    return x


def _natural_cubic_spline(
    xs: List[float], ys: List[float],
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Natural cubic spline coefficients for data points (xs, ys).

    Returns (a, b, c, d) where on segment [x_i, x_{i+1}]:
        S(x) = a_i + b_i·(x-x_i) + c_i·(x-x_i)² + d_i·(x-x_i)³

    Natural spline: second derivatives at endpoints = 0.
    """
    n = len(xs) - 1
    if n < 1:
        raise ValueError("Need at least 2 points.")

    h = [xs[i + 1] - xs[i] for i in range(n)]
    a = list(ys)

    A = [0.0] * (n + 1)
    B = [1.0] * (n + 1)
    C = [0.0] * (n + 1)
    D_rhs = [0.0] * (n + 1)

    B[0] = 1.0
    B[n] = 1.0

    for i in range(1, n):
        A[i] = h[i - 1]
        B[i] = 2.0 * (h[i - 1] + h[i])
        C[i] = h[i]
        D_rhs[i] = 3.0 * ((ys[i + 1] - ys[i]) / h[i] - (ys[i] - ys[i - 1]) / h[i - 1])

    c_coeff = _solve_tridiagonal(A, B, C, D_rhs)

    b_coeff = [0.0] * n
    d_coeff = [0.0] * n
    for i in range(n):
        b_coeff[i] = (ys[i + 1] - ys[i]) / h[i] - h[i] * (2.0 * c_coeff[i] + c_coeff[i + 1]) / 3.0
        d_coeff[i] = (c_coeff[i + 1] - c_coeff[i]) / (3.0 * h[i])

    return a, b_coeff, c_coeff, d_coeff


def _eval_spline(
    xs: List[float],
    a: List[float],
    b: List[float],
    c: List[float],
    d: List[float],
    x: float,
) -> float:
    """Evaluate natural cubic spline at x."""
    n = len(xs) - 1
    if x <= xs[0]:
        i = 0
    elif x >= xs[n]:
        i = n - 1
    else:
        i = n - 1
        for j in range(n):
            if xs[j] <= x <= xs[j + 1]:
                i = j
                break
    dx = x - xs[i]
    return a[i] + b[i] * dx + c[i] * dx * dx + d[i] * dx * dx * dx


def yield_curve_interpolate(
    tenors: List[float],
    yields: List[float],
    target_tenor: float,
    method: str = "linear",
) -> float:
    """
    Interpolate yield for a target tenor from (tenor, yield) data points.

    Args:
        tenors: List of tenors in years (sorted ascending).
        yields: Corresponding yields in %.
        target_tenor: Target tenor in years.
        method: "linear" for linear interpolation or "spline" for natural cubic spline.

    Returns:
        Interpolated yield in %.
    """
    if len(tenors) < 2:
        raise ValueError("Need at least 2 data points.")
    if len(tenors) != len(yields):
        raise ValueError("tenors and yields must have same length.")
    if any(t1 >= t2 for t1, t2 in zip(tenors, tenors[1:])):
        raise ValueError("Tenors must be strictly ascending.")

    if method == "linear":
        # Handle extrapolation with nearest-segment slope
        if target_tenor <= tenors[0]:
            slope = (yields[1] - yields[0]) / (tenors[1] - tenors[0])
            return yields[0] + slope * (target_tenor - tenors[0])
        if target_tenor >= tenors[-1]:
            slope = (yields[-1] - yields[-2]) / (tenors[-1] - tenors[-2])
            return yields[-1] + slope * (target_tenor - tenors[-1])
        # Binary search for segment
        lo, hi = 0, len(tenors) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if tenors[mid] <= target_tenor:
                lo = mid
            else:
                hi = mid
        frac = (target_tenor - tenors[lo]) / (tenors[hi] - tenors[lo])
        return yields[lo] + frac * (yields[hi] - yields[lo])

    elif method == "spline":
        a, b, c, d = _natural_cubic_spline(tenors, yields)
        # Clamp to range
        clamped = max(tenors[0], min(tenors[-1], target_tenor))
        return _eval_spline(tenors, a, b, c, d, clamped)

    else:
        raise ValueError(f"Unknown method '{method}'. Use 'linear' or 'spline'.")


# ---------------------------------------------------------------------------
# Credit Spread Analysis (v1.8)
# ---------------------------------------------------------------------------

def compute_credit_spread(
    bond_ytm: float,
    benchmark_ytm: float,
) -> Dict:
    """
    Compute credit spread of a bond vs benchmark.

    Args:
        bond_ytm: Bond YTM in %.
        benchmark_ytm: Benchmark (e.g. government bond) YTM in %.

    Returns:
        dict with spread_bps, spread_pct, and qualitative assessment.
    """
    spread_bps = (bond_ytm - benchmark_ytm) * 100.0
    spread_pct = bond_ytm - benchmark_ytm

    if spread_bps <= 0:
        level = "negative/zero — bond trades at or below benchmark"
    elif spread_bps < 50:
        level = "narrow (<50 bp) — investment grade, low risk premium"
    elif spread_bps < 200:
        level = "moderate (50–200 bp) — typical IG corporate range"
    elif spread_bps < 500:
        level = "wide (200–500 bp) — high-yield territory"
    else:
        level = "very wide (>500 bp) — distressed credit"

    return {
        "bond_ytm_pct": bond_ytm,
        "benchmark_ytm_pct": benchmark_ytm,
        "spread_bps": round(spread_bps, 2),
        "spread_pct": round(spread_pct, 4),
        "assessment": level,
    }


def credit_spread_by_comps(
    bond_ytm: float,
    bond_tenor: float,
    comparable_bonds: List[Dict],
    interpolate_method: str = "linear",
) -> Dict:
    """
    Compute credit spread vs comparable bonds (same rating/tenor).

    comparable_bonds: list of {"tenor": float, "ytm": float, "rating": str, ...}

    Returns credit spread dict with interpolated benchmark yield.
    """
    if not comparable_bonds:
        return {"error": "No comparable bonds provided."}

    comp_tenors = sorted(set(b["tenor"] for b in comparable_bonds))
    comp_yields: Dict[float, List[float]] = {}
    for b in comparable_bonds:
        comp_yields.setdefault(b["tenor"], []).append(b["ytm"])
    avg_yields = [sum(comp_yields[t]) / len(comp_yields[t]) for t in comp_tenors]

    if len(comp_tenors) < 2:
        bench_ytm = avg_yields[0] if comp_tenors else comparable_bonds[0]["ytm"]
    else:
        bench_ytm = yield_curve_interpolate(
            comp_tenors, avg_yields, bond_tenor, method=interpolate_method,
        )

    return compute_credit_spread(bond_ytm, bench_ytm)


# ---------------------------------------------------------------------------
# Sensitivity Matrix (v1.8)
# ---------------------------------------------------------------------------

def sensitivity_matrix(
    face_value: float = 100.0,
    coupon_rate: float = 3.5,
    frequency: int = 2,
    base_ytm: float = 4.0,
    rate_shifts: Optional[List[float]] = None,
    tenors: Optional[List[float]] = None,
) -> Dict:
    """
    Generate sensitivity matrix: rate shifts × tenor grid.

    Args:
        face_value: Par value.
        coupon_rate: Annual coupon in %.
        frequency: Coupon frequency.
        base_ytm: Base YTM in %.
        rate_shifts: Rate shift list in bp (default: ±200bp in 50bp steps).
        tenors: Maturity list in years (default: 1–10yr).

    Returns dict with matrix rows (tenor, shift, price, duration, convexity, dv01).
    """
    if rate_shifts is None:
        rate_shifts = [s * 50.0 for s in range(-4, 5)]
    if tenors is None:
        tenors = [float(y) for y in range(1, 11)]

    matrix: List[Dict] = []
    for tenor in tenors:
        for shift in rate_shifts:
            ytm_shifted = base_ytm + shift / 100.0
            try:
                dc = compute_duration_convexity(
                    face_value, coupon_rate, frequency, tenor, ytm_shifted,
                )
            except ValueError:
                continue
            matrix.append({
                "tenor_yr": tenor,
                "rate_shift_bp": shift,
                "ytm_pct": round(ytm_shifted, 4),
                "dirty_price": dc["dirty_price"],
                "modified_duration": dc["modified_duration"],
                "convexity": dc["convexity"],
                "dv01": dc["dv01"],
            })

    return {
        "base_ytm_pct": base_ytm,
        "rate_shifts_bp": rate_shifts,
        "tenors_yr": tenors,
        "matrix": matrix,
        "n_points": len(matrix),
    }


def print_sensitivity_matrix(data: Dict) -> None:
    """Print sensitivity matrix as a formatted table."""
    tenors = data["tenors_yr"]
    shifts = data["rate_shifts_bp"]

    print("\nSENSITIVITY MATRIX — Modified Duration")
    print(f"  Base YTM: {data['base_ytm_pct']}%")
    print()
    # Header
    header = f"{'Tenor':>8s}"
    for s in shifts:
        header += f"{s:>10.0f}bp"
    print(f"  {header}")
    sep = "  " + "─" * len(header)
    print(sep)

    # Reconstruct lookup
    by_tenor: Dict[float, Dict[float, float]] = {t: {} for t in tenors}
    for row in data["matrix"]:
        by_tenor[row["tenor_yr"]][row["rate_shift_bp"]] = row["modified_duration"]

    for tenor in tenors:
        line = f"  {tenor:>6.1f}yr"
        for s in shifts:
            val = by_tenor.get(tenor, {}).get(s)
            line += f"{val:>10.4f}" if val is not None else f"{'N/A':>10s}"
        print(line)

    print(sep)


# ---------------------------------------------------------------------------
# Embedded Option / OAS Analysis (v1.8)
# ---------------------------------------------------------------------------

def compute_oas(
    face_value: float = 100.0,
    coupon_rate: float = 4.0,
    frequency: int = 2,
    maturity_years: float = 10.0,
    market_price: float = 102.0,
    call_price: float = 100.0,
    call_years: Optional[List[float]] = None,
    ref_curve_tenors: Optional[List[float]] = None,
    ref_curve_yields: Optional[List[float]] = None,
) -> Dict:
    """
    Simplified OAS (Option-Adjusted Spread) analysis for callable bonds.

    Approach:
      1. Price the bond as plain-vanilla → get option-free value.
      2. Estimate option cost = max(0, vanilla_price – market_price).
      3. Find Z-spread (the constant spread added to benchmark curve
         to match market price).
      4. OAS ≈ Z-spread – option_cost (yield-basis approximation).

    Args:
        face_value: Par value.
        coupon_rate: Annual coupon in %.
        frequency: Coupon frequency.
        maturity_years: Final maturity.
        market_price: Observed market dirty price.
        call_price: Call / prepayment strike price.
        call_years: List of call dates in years from now.
        ref_curve_tenors: Reference curve tenors.
        ref_curve_yields: Reference curve yields.

    Returns dict with z_spread_bps, oas_est_bps, option_cost, vanilla_price, etc.
    """
    if call_years is None:
        call_years = [maturity_years / 2.0]
    if ref_curve_tenors is None:
        ref_curve_tenors = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
    if ref_curve_yields is None:
        ref_curve_yields = [2.0, 2.2, 2.5, 2.8, 3.0, 3.2, 3.5, 4.0, 4.2]

    # Benchmark yield interpolated from reference curve
    bench_ytm = yield_curve_interpolate(
        ref_curve_tenors, ref_curve_yields, maturity_years, "linear",
    )

    # 1. Vanilla (option-free) price at benchmark
    vanilla_price = _price_from_ytm(face_value, coupon_rate, frequency, maturity_years, bench_ytm)

    # 2. Option cost estimate
    #    (difference between option-free value and market price)
    option_cost = max(0.0, vanilla_price - market_price)

    # 3. Z-spread via bisection search
    def _pv_with_spread(spread_bps: float) -> float:
        adj = bench_ytm + spread_bps / 100.0
        return _price_from_ytm(face_value, coupon_rate, frequency, maturity_years, adj)

    lo, hi = -1000.0, 1000.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if _pv_with_spread(mid) > market_price:
            lo = mid
        else:
            hi = mid
        if abs(hi - lo) < 0.01:
            break
    z_spread_bps = (lo + hi) / 2.0

    # 4. OAS estimate
    option_cost_bps = (option_cost / vanilla_price * 10000.0) if vanilla_price > 0 else 0.0
    oas_bps = max(-500.0, z_spread_bps - option_cost_bps)

    return {
        "market_price": market_price,
        "vanilla_price": round(vanilla_price, 6),
        "benchmark_ytm_pct": round(bench_ytm, 4),
        "call_price": call_price,
        "call_years": call_years,
        "z_spread_bps": round(z_spread_bps, 2),
        "option_cost_est_bps": round(option_cost_bps, 2),
        "oas_est_bps": round(oas_bps, 2),
        "option_value_pct": round(option_cost / market_price * 100, 4) if market_price else 0.0,
        "note": "Simplified OAS; full binomial/lattice model recommended for production.",
    }


# ---------------------------------------------------------------------------
# Cross-Product Bond Type Comparison (v1.8)
# ---------------------------------------------------------------------------

BOND_PRODUCT_PARAMS: Dict[str, Dict] = {
    "企业债": {
        "issuer": "中央/地方国企为主",
        "market": "银行间+交易所",
        "regulator": "发改委",
        "typical_tenor": "5–10年",
        "liquidity_premium_bps": 20,
        "credit_adj_bps": 0,
        "issue_size": "≥10亿",
        "rating_req": "AA及以上",
        "collateral": "通常无担保",
        "tax_treatment": "利息收入征所得税",
        "investor_base": "银行、保险为主",
    },
    "私募债": {
        "issuer": "中小企业/非上市",
        "market": "交易所私募",
        "regulator": "证监会/交易所",
        "typical_tenor": "1–5年",
        "liquidity_premium_bps": 80,
        "credit_adj_bps": 50,
        "issue_size": "≥3000万",
        "rating_req": "无强制评级",
        "collateral": "常含增信措施",
        "tax_treatment": "利息收入征所得税",
        "investor_base": "≤200合格投资者",
        "transfer_restriction": "限售期内不可转让",
    },
    "MTN": {
        "issuer": "大型企业/上市公司",
        "market": "银行间债券市场",
        "regulator": "交易商协会（NAFMII）",
        "typical_tenor": "3、5年为主",
        "liquidity_premium_bps": 15,
        "credit_adj_bps": 0,
        "issue_size": "≥1亿",
        "rating_req": "无强制评级（注册制）",
        "collateral": "无担保，注册制",
        "tax_treatment": "利息收入征所得税",
        "investor_base": "银行间市场全体成员",
        "shelf_registration": "DFI/TDFI储架发行",
    },
    "ABS": {
        "issuer": "SPV/信托计划",
        "market": "交易所+银行间",
        "regulator": "证监会/交易商协会/银保监会",
        "typical_tenor": "1–5年（多档）",
        "liquidity_premium_bps": 50,
        "credit_adj_bps": 30,
        "issue_size": "≥1亿",
        "rating_req": "优先档≥AA",
        "collateral": "基础资产池",
        "tax_treatment": "视SPV结构而定",
        "investor_base": "机构投资者",
        "structural_features": "优先/次级分层、超额利差、信用触发",
    },
    "公司债": {
        "issuer": "上市公司/非上市公众公司",
        "market": "交易所",
        "regulator": "证监会",
        "typical_tenor": "3–7年",
        "liquidity_premium_bps": 30,
        "credit_adj_bps": 5,
        "issue_size": "≥5000万",
        "rating_req": "AA及以上（大公募）",
        "collateral": "大公募无担保",
        "tax_treatment": "利息收入征所得税",
        "investor_base": "大公募面向公众+机构",
    },
}


def cross_product_comparison(
    face_value: float = 100.0,
    coupon_rate: float = 4.0,
    frequency: int = 2,
    maturity_years: float = 5.0,
    base_ytm: float = 4.0,
    product_types: Optional[List[str]] = None,
) -> Dict:
    """
    Compare bond pricing across product types with product-specific adjustments.

    For each product type, adjusts the YTM with liquidity premium and credit spread
    parameters, then computes the adjusted price and yield differential vs plain vanilla.

    Args:
        face_value: Par value.
        coupon_rate: Annual coupon %.
        frequency: Coupon frequency.
        maturity_years: Maturity in years.
        base_ytm: Base YTM in % (vanilla benchmark).
        product_types: List of product keys (default all).

    Returns dict with vanilla_price and per-product comparison rows.
    """
    if product_types is None:
        product_types = list(BOND_PRODUCT_PARAMS.keys())

    vanilla_price = _price_from_ytm(face_value, coupon_rate, frequency, maturity_years, base_ytm)

    results: List[Dict] = []
    for pt in product_types:
        params = BOND_PRODUCT_PARAMS.get(pt)
        if params is None:
            continue
        liq_bps = float(params.get("liquidity_premium_bps", 0))
        cred_bps = float(params.get("credit_adj_bps", 0))
        total_adj_bps = liq_bps + cred_bps
        adj_ytm = base_ytm + total_adj_bps / 100.0
        adj_price = _price_from_ytm(face_value, coupon_rate, frequency, maturity_years, adj_ytm)

        results.append({
            "product": pt,
            "market": str(params.get("market", "N/A")),
            "regulator": str(params.get("regulator", "N/A")),
            "liquidity_premium_bps": liq_bps,
            "credit_adj_bps": cred_bps,
            "total_adj_bps": total_adj_bps,
            "adjusted_ytm_pct": round(adj_ytm, 4),
            "adjusted_price": round(adj_price, 6),
            "price_diff_vs_vanilla": round(adj_price - vanilla_price, 6),
            "yield_spread_vs_vanilla_bps": total_adj_bps,
        })

    return {
        "face_value": face_value,
        "coupon_rate_pct": coupon_rate,
        "maturity_years": maturity_years,
        "base_ytm_pct": base_ytm,
        "vanilla_price": round(vanilla_price, 6),
        "products": results,
    }


def print_cross_product(data: Dict) -> None:
    """Print cross-product comparison table."""
    print("\nCROSS-PRODUCT BOND PRICING COMPARISON")
    print(f"  Base YTM: {data['base_ytm_pct']}%  |  Maturity: {data['maturity_years']}yr  "
          f"|  Vanilla Price: {data['vanilla_price']:.4f}")
    print()
    hdr = (f"  {'Product':<10s} {'Market':<14s} {'Adj YTM':>8s} "
           f"{'Price':>10s} {'ΔPrice':>10s} {'Sprd':>6s}")
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))
    for p in data["products"]:
        print(
            f"  {p['product']:<10s} {p['market']:<14s} "
            f"{p['adjusted_ytm_pct']:>8.4f} {p['adjusted_price']:>10.4f} "
            f"{p['price_diff_vs_vanilla']:>10.4f} {p['total_adj_bps']:>5.0f}bp"
        )
    print()


# ---------------------------------------------------------------------------
# Built-in Test Suite (v1.8)
# ---------------------------------------------------------------------------

def run_tests() -> Tuple[bool, List[str]]:
    """
    Run comprehensive built-in tests covering all v1.8 functions.

    Returns (all_passed: bool, failure_messages: list[str]).
    """
    failures: List[str] = []

    def _check(name: str, cond: bool, detail: str = "") -> None:
        if not cond:
            failures.append(f"  FAIL: {name} — {detail}")

    print("=" * 64)
    print("  BOND PRICING CALC — BUILT-IN TESTS (v1.8)")
    print("=" * 64)

    # ── 1. Newton-Raphson YTM ──
    print("\n── [1] Newton-Raphson YTM Solver")
    nr = compute_ytm_nr(price=100.0, face_value=100.0, coupon_rate=4.0,
                        maturity_years=5.0, precision=0.0001)
    _check("NR: YTM ≈ coupon when price ≈ par", abs(nr["ytm_pct"] - 4.0) < 0.15,
           f"got {nr['ytm_pct']:.6f}%")
    _check("NR: converged", nr["converged"])
    _check("NR: iterations ≤ max_iter", nr["iterations"] <= nr["max_iter"])
    _check("NR: price_error < precision", abs(nr["price_error"]) < 0.001)
    print(f"  Par (5yr, 4%): YTM={nr['ytm_pct']:.6f}%, iters={nr['iterations']}, "
          f"converged={nr['converged']}")

    nr2 = compute_ytm_nr(price=95.0, face_value=100.0, coupon_rate=3.5, maturity_years=3.0)
    _check("NR: discount bond YTM > coupon", nr2["ytm_pct"] > 3.5,
           f"got {nr2['ytm_pct']:.4f}%")
    print(f"  Discount (3yr, 3.5% cpn, price=95): YTM={nr2['ytm_pct']:.6f}%")

    nr3 = compute_ytm_nr(price=105.0, face_value=100.0, coupon_rate=5.0, maturity_years=2.0)
    _check("NR: premium bond YTM < coupon", nr3["ytm_pct"] < 5.0,
           f"got {nr3['ytm_pct']:.4f}%")
    print(f"  Premium (2yr, 5% cpn, price=105): YTM={nr3['ytm_pct']:.6f}%")

    # Round-trip: price at solved YTM ≈ input price
    p_back = _price_from_ytm(100.0, 4.0, 2, 5.0, nr["ytm_pct"])
    _check("NR: round-trip price", abs(p_back - 100.0) < 0.02, f"got {p_back:.6f}")

    # ── 2. Duration & Convexity ──
    print("\n── [2] Duration & Convexity")
    dc = compute_duration_convexity(face_value=100.0, coupon_rate=4.0,
                                    frequency=2, maturity_years=5.0, ytm=4.0)
    _check("DC: price ≈ par", abs(dc["dirty_price"] - 100.0) < 0.05,
           f"got {dc['dirty_price']:.6f}")
    _check("DC: Macaulay > 0", dc["macaulay_duration"] > 0)
    _check("DC: Modified < Macaulay", dc["modified_duration"] < dc["macaulay_duration"])
    _check("DC: convexity > 0", dc["convexity"] > 0)
    _check("DC: PVBP > 0", dc["pvbp"] > 0)
    print(f"  Price={dc['dirty_price']:.6f}, MacD={dc['macaulay_duration']:.4f}, "
          f"ModD={dc['modified_duration']:.4f}, Cx={dc['convexity']:.4f}")

    # Zero coupon: Macaulay ≈ maturity
    dc_zc = compute_duration_convexity(face_value=100.0, coupon_rate=0.0,
                                       frequency=1, maturity_years=5.0, ytm=5.0)
    _check("DC: zero Macaulay ≈ maturity", abs(dc_zc["macaulay_duration"] - 5.0) < 0.05,
           f"got {dc_zc['macaulay_duration']:.4f}")
    print(f"  Zero-coupon: MacD={dc_zc['macaulay_duration']:.4f} (≈5.0)")

    # ── 3. Yield Curve ──
    print("\n── [3] Yield Curve Interpolation")
    tenors = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 30.0]
    ylds = [2.00, 2.20, 2.50, 2.75, 3.00, 3.20, 3.50, 4.00]

    y3 = yield_curve_interpolate(tenors, ylds, 3.0, "linear")
    _check("CV: linear at exact knot", abs(y3 - 2.75) < 0.01, f"got {y3:.4f}")
    print(f"  Linear @ 3.0yr: {y3:.4f}% (exact: 2.75%)")

    y15 = yield_curve_interpolate(tenors, ylds, 1.5, "linear")
    _check("CV: linear interpolation", 2.2 < y15 < 2.5, f"got {y15:.4f}")
    print(f"  Linear @ 1.5yr: {y15:.4f}%")

    y5s = yield_curve_interpolate(tenors, ylds, 5.0, "spline")
    _check("CV: spline at exact knot near", abs(y5s - 3.00) < 0.01, f"got {y5s:.4f}")
    print(f"  Spline @ 5.0yr: {y5s:.4f}% (exact: 3.00%)")

    y3s = yield_curve_interpolate(tenors, ylds, 3.0, "spline")
    _check("CV: spline smooth", 2.6 < y3s < 3.0, f"got {y3s:.4f}")
    print(f"  Spline @ 3.0yr: {y3s:.4f}%")

    # ── 4. Credit Spread ──
    print("\n── [4] Credit Spread")
    cs = compute_credit_spread(4.5, 3.0)
    _check("CS: spread = 150 bp", abs(cs["spread_bps"] - 150.0) < 0.1)
    _check("CS: moderate assessment", "moderate" in cs["assessment"])
    print(f"  Bond 4.5% vs Bench 3.0%: {cs['spread_bps']:.1f}bp → {cs['assessment']}")

    cs2 = compute_credit_spread(8.0, 2.5)
    _check("CS: wide spread", cs2["spread_bps"] > 400)

    # ── 5. Sensitivity Matrix ──
    print("\n── [5] Sensitivity Matrix")
    sm = sensitivity_matrix(face_value=100.0, coupon_rate=3.5, frequency=2, base_ytm=4.0)
    _check("SM: has data rows", sm["n_points"] > 0)
    _check("SM: matrix is list", isinstance(sm["matrix"], list))
    # Price should decrease with increasing rate (same tenor)
    prices_low = [r["dirty_price"] for r in sm["matrix"]
                  if r["tenor_yr"] == 5.0 and r["rate_shift_bp"] == -200.0]
    prices_high = [r["dirty_price"] for r in sm["matrix"]
                   if r["tenor_yr"] == 5.0 and r["rate_shift_bp"] == 200.0]
    if prices_low and prices_high:
        _check("SM: price(-200bp) > price(+200bp)", prices_low[0] > prices_high[0])
    print(f"  Matrix: {sm['n_points']} pts ({len(sm['tenors_yr'])} tenors × "
          f"{len(sm['rate_shifts_bp'])} shifts)")

    # ── 6. OAS ──
    print("\n── [6] OAS Analysis")
    oas = compute_oas(face_value=100.0, coupon_rate=4.0, frequency=2,
                      maturity_years=10.0, market_price=100.0, call_price=100.0,
                      call_years=[5.0])
    _check("OAS: has z_spread", "z_spread_bps" in oas)
    _check("OAS: has oas_est", "oas_est_bps" in oas)
    _check("OAS: oas_est is finite", math.isfinite(oas["oas_est_bps"]))
    print(f"  Z-Spread={oas['z_spread_bps']:.2f}bp, OAS={oas['oas_est_bps']:.2f}bp, "
          f"Note={oas['note'][:40]}...")

    # OAS for callable bond trading above par
    oas2 = compute_oas(face_value=100.0, coupon_rate=5.0, maturity_years=10.0,
                       market_price=105.0, call_price=100.0, call_years=[3.0, 5.0, 7.0])
    _check("OAS2: callable premium priced", math.isfinite(oas2["oas_est_bps"]))
    print(f"  Callable (5% cpn, mkt=105): OAS={oas2['oas_est_bps']:.2f}bp")

    # ── 7. Cross-Product ──
    print("\n── [7] Cross-Product Comparison")
    cmp = cross_product_comparison(base_ytm=4.0, maturity_years=5.0)
    _check("CP: has all 5 product types", len(cmp["products"]) >= 5)
    mtn = next((p for p in cmp["products"] if p["product"] == "MTN"), None)
    abs_p = next((p for p in cmp["products"] if p["product"] == "ABS"), None)
    私募 = next((p for p in cmp["products"] if p["product"] == "私募债"), None)
    if mtn and abs_p:
        _check("CP: MTN liq premium < ABS", mtn["liquidity_premium_bps"] < abs_p["liquidity_premium_bps"])
    if 私募 and mtn:
        _check("CP: 私募债 spread > MTN", 私募["total_adj_bps"] > mtn["total_adj_bps"])
    print(f"  Compared {len(cmp['products'])} product types")
    for p in cmp["products"]:
        print(f"    {p['product']:<8s} YTM={p['adjusted_ytm_pct']:.4f}%  "
              f"Px={p['adjusted_price']:.4f}  Adj={p['total_adj_bps']:.0f}bp")

    # ── 8. Error Handling ──
    print("\n── [8] Error Handling")
    try:
        compute_ytm_nr(price=-1.0)
        _check("EH: negative price rejected", False)
    except ValueError:
        _check("EH: negative price rejected", True)
    print("  Negative price → ValueError ✓")

    try:
        yield_curve_interpolate([1.0], [2.0], 3.0, "linear")
        _check("EH: too few curve points", False)
    except ValueError:
        _check("EH: too few curve points", True)
    print("  Too few curve points → ValueError ✓")

    try:
        yield_curve_interpolate([2.0, 1.0], [3.0, 4.0], 1.5, "linear")
        _check("EH: non-ascending tenors", False)
    except ValueError:
        _check("EH: non-ascending tenors", True)
    print("  Non-ascending tenors → ValueError ✓")

    # ── 9. Summary ──
    print("\n" + "=" * 64)
    if not failures:
        print("  ALL TESTS PASSED  ✓")
        print("=" * 64)
        return True, []
    else:
        print(f"  {len(failures)} TEST(S) FAILED  ✗")
        for f in failures:
            print(f"    {f}")
        print("=" * 64)
        return False, failures


# ---------------------------------------------------------------------------
# CLI (v1.8 — subcommand-based)
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Bond pricing & analytics calculator — v1.8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic pricing (backward-compat — no subcommand)
  %(prog)s --coupon-rate 3.5 --maturity-years 5 --ytm 4.2

  # YTM solver (Newton-Raphson)
  %(prog)s solve-ytm --price 95.0 --coupon-rate 3.5 --maturity-years 5

  # Duration / convexity
  %(prog)s duration --coupon-rate 4.0 --maturity-years 5 --ytm 4.0

  # Yield curve interpolation
  %(prog)s yield-curve --tenors 0.5,1,2,5,10,30 \\
      --yields 2.0,2.2,2.5,3.0,3.5,4.0 --target 7.0 --method spline

  # Credit spread
  %(prog)s credit-spread --bond-ytm 5.5 --benchmark-ytm 3.0

  # Sensitivity matrix
  %(prog)s sensitivity --coupon-rate 3.5 --base-ytm 4.0

  # OAS for callable bonds
  %(prog)s oas --coupon-rate 4.0 --maturity-years 10 \\
      --market-price 100.0 --call-price 100.0

  # Cross-product comparison
  %(prog)s compare-products --coupon-rate 4.0 --maturity-years 5 --base-ytm 4.0

  # Run built-in tests
  %(prog)s --test
        """,
    )
    p.add_argument("--test", dest="run_tests", action="store_true",
                   help="Run built-in test suite and exit")

    sub = p.add_subparsers(dest="command", metavar="COMMAND")

    # ── solve-ytm ──
    p_ytm = sub.add_parser("solve-ytm",
                           help="Newton-Raphson YTM solver from market price")
    p_ytm.add_argument("--price", type=float, required=True,
                       help="Observed market dirty price")
    p_ytm.add_argument("--face-value", type=float, default=100.0)
    p_ytm.add_argument("--coupon-rate", type=float, required=True,
                       help="Annual coupon rate in %%")
    p_ytm.add_argument("--frequency", type=int, default=2, choices=[1, 2])
    p_ytm.add_argument("--maturity-years", type=float, required=True)
    p_ytm.add_argument("--initial-guess", type=float, default=5.0,
                       help="Initial YTM guess in %% (default: 5.0)")
    p_ytm.add_argument("--precision", type=float, default=0.0001)
    p_ytm.add_argument("--max-iter", type=int, default=100)
    p_ytm.add_argument("--json", dest="json_out", action="store_true")

    # ── duration ──
    p_dur = sub.add_parser("duration",
                           help="Standalone duration / convexity calculator")
    p_dur.add_argument("--face-value", type=float, default=100.0)
    p_dur.add_argument("--coupon-rate", type=float, required=True)
    p_dur.add_argument("--frequency", type=int, default=2, choices=[1, 2])
    p_dur.add_argument("--maturity-years", type=float, required=True)
    p_dur.add_argument("--ytm", type=float, required=True)
    p_dur.add_argument("--json", dest="json_out", action="store_true")

    # ── yield-curve ──
    p_yc = sub.add_parser("yield-curve",
                           help="Yield curve interpolation (linear / cubic spline)")
    p_yc.add_argument("--tenors", type=str, required=True,
                      help="Comma-separated tenors (yr), e.g. 0.5,1,2,5,10")
    p_yc.add_argument("--yields", type=str, required=True,
                      help="Comma-separated yields (%%), same order as --tenors")
    p_yc.add_argument("--target", type=float, required=True,
                      help="Target tenor to interpolate")
    p_yc.add_argument("--method", type=str, default="linear",
                      choices=["linear", "spline"],
                      help="Interpolation method (default: linear)")
    p_yc.add_argument("--json", dest="json_out", action="store_true")

    # ── credit-spread ──
    p_cs = sub.add_parser("credit-spread",
                           help="Compute credit spread vs benchmark")
    p_cs.add_argument("--bond-ytm", type=float, required=True,
                     help="Bond YTM in %%")
    p_cs.add_argument("--benchmark-ytm", type=float, required=True,
                     help="Benchmark (e.g. government bond) YTM in %%")
    p_cs.add_argument("--json", dest="json_out", action="store_true")

    # ── sensitivity ──
    p_sen = sub.add_parser("sensitivity",
                           help="Sensitivity matrix (rate shifts x tenors)")
    p_sen.add_argument("--face-value", type=float, default=100.0)
    p_sen.add_argument("--coupon-rate", type=float, required=True)
    p_sen.add_argument("--frequency", type=int, default=2, choices=[1, 2])
    p_sen.add_argument("--base-ytm", type=float, default=4.0,
                      help="Base YTM in %% (default: 4.0)")
    p_sen.add_argument("--shifts", type=str, default=None,
                       help="Comma-sep rate shifts in bp (default: -200..200 step 50)")
    p_sen.add_argument("--tenors", type=str, default=None,
                       help="Comma-sep tenors in yr (default: 1..10)")
    p_sen.add_argument("--json", dest="json_out", action="store_true")

    # ── oas ──
    p_oas = sub.add_parser("oas",
                            help="Simplified OAS analysis for callable bonds")
    p_oas.add_argument("--face-value", type=float, default=100.0)
    p_oas.add_argument("--coupon-rate", type=float, default=4.0)
    p_oas.add_argument("--frequency", type=int, default=2, choices=[1, 2])
    p_oas.add_argument("--maturity-years", type=float, default=10.0)
    p_oas.add_argument("--market-price", type=float, required=True,
                       help="Observed market dirty price")
    p_oas.add_argument("--call-price", type=float, default=100.0,
                       help="Call / prepayment price (default: 100)")
    p_oas.add_argument("--call-years", type=str, default=None,
                       help="Comma-sep call dates in yr (default: half maturity)")
    p_oas.add_argument("--ref-tenors", type=str, default=None,
                       help="Comma-sep ref curve tenors")
    p_oas.add_argument("--ref-yields", type=str, default=None,
                       help="Comma-sep ref curve yields in %%")
    p_oas.add_argument("--json", dest="json_out", action="store_true")

    # ── compare-products ──
    p_cp = sub.add_parser("compare-products",
                           help="Cross-product bond pricing comparison")
    p_cp.add_argument("--face-value", type=float, default=100.0)
    p_cp.add_argument("--coupon-rate", type=float, default=4.0)
    p_cp.add_argument("--frequency", type=int, default=2, choices=[1, 2])
    p_cp.add_argument("--maturity-years", type=float, default=5.0)
    p_cp.add_argument("--base-ytm", type=float, default=4.0,
                      help="Base benchmark YTM in %%")
    p_cp.add_argument("--products", type=str, default=None,
                      help="Comma-sep product list (default: all 5 types)")
    p_cp.add_argument("--json", dest="json_out", action="store_true")

    # ── Backward-compat: top-level args without subcommand = original pricing ──
    p.add_argument("--face-value", type=float, default=100.0,
                   help="Par / face value per bond unit (default: 100)")
    p.add_argument("--coupon-rate", type=float, default=None,
                   help="Annual coupon rate in %%")
    p.add_argument("--frequency", type=int, default=2,
                   choices=[1, 2],
                   help="Coupon frequency: 1=annual, 2=semi-annual (default: 2)")
    p.add_argument("--maturity-years", type=float, default=None,
                   help="Remaining time to maturity in years")
    p.add_argument("--ytm", type=float, default=None,
                   help="Yield-to-maturity in %%")
    p.add_argument("--settlement-days", type=int, default=0,
                   help="Settlement days from today (default: 0)")
    p.add_argument("--json", dest="json_out", action="store_true",
                   help="Output JSON instead of formatted text")
    return p


def _parse_floats(arg: Optional[str]) -> Optional[List[float]]:
    """Parse comma-separated floats, or None."""
    if arg is None:
        return None
    return [float(x.strip()) for x in arg.split(",")]


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # ── --test ──
    if getattr(args, "run_tests", False):
        ok, failures = run_tests()
        sys.exit(0 if ok else 1)

    # ── Subcommand dispatch ──
    cmd = getattr(args, "command", None)

    if cmd == "solve-ytm":
        try:
            r = compute_ytm_nr(
                price=args.price, face_value=args.face_value,
                coupon_rate=args.coupon_rate, frequency=args.frequency,
                maturity_years=args.maturity_years,
                initial_guess=args.initial_guess,
                precision=args.precision, max_iter=args.max_iter,
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        if getattr(args, "json_out", False):
            json.dump(r, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"\nNewton-Raphson YTM Solver (precision={args.precision})")
            print(f"  Price:         {args.price:.6f}")
            print(f"  Face Value:    {args.face_value:.2f}")
            print(f"  Coupon Rate:   {args.coupon_rate:.4f}%")
            print(f"  Maturity:      {args.maturity_years:.2f} yr")
            print(f"  Frequency:     {'Annual' if args.frequency == 1 else 'Semi-annual'}")
            print(f"  Computed YTM:  {r['ytm_pct']:.6f}%")
            print(f"  Iterations:    {r['iterations']}  |  Converged: {r['converged']}")
            print(f"  Price Error:   {r['price_error']:.8f}")

    elif cmd == "duration":
        try:
            r = compute_duration_convexity(
                face_value=args.face_value, coupon_rate=args.coupon_rate,
                frequency=args.frequency, maturity_years=args.maturity_years,
                ytm=args.ytm,
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        if getattr(args, "json_out", False):
            json.dump(r, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"\nDURATION & CONVEXITY (YTM={r['ytm_pct']}%)")
            print(f"  Dirty Price:       {r['dirty_price']:.6f}")
            print(f"  Macaulay Duration: {r['macaulay_duration']:.4f} yr")
            print(f"  Modified Duration: {r['modified_duration']:.4f} yr")
            print(f"  Convexity:         {r['convexity']:.4f}")
            print(f"  Dollar Duration:   {r['dollar_duration']:.6f}")
            print(f"  PVBP (1bp):        {r['pvbp']:.8f}")
            print(f"  DV01:              {r['dv01']:.8f}")

    elif cmd == "yield-curve":
        tenors = [float(x.strip()) for x in args.tenors.split(",")]
        yields = [float(x.strip()) for x in args.yields.split(",")]
        try:
            y = yield_curve_interpolate(tenors, yields, args.target, args.method)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        out = {"target": args.target, "method": args.method, "interpolated_yield": round(y, 6)}
        if getattr(args, "json_out", False):
            json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"\nYIELD CURVE INTERPOLATION ({args.method})")
            print(f"  Target Tenor: {args.target:.2f} yr")
            print(f"  Yield:        {y:.6f}%")

    elif cmd == "credit-spread":
        r = compute_credit_spread(args.bond_ytm, args.benchmark_ytm)
        if getattr(args, "json_out", False):
            json.dump(r, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"\nCREDIT SPREAD")
            print(f"  Bond YTM:        {r['bond_ytm_pct']:.4f}%")
            print(f"  Benchmark YTM:   {r['benchmark_ytm_pct']:.4f}%")
            print(f"  Spread:          {r['spread_bps']:.2f} bp")
            print(f"  Assessment:      {r['assessment']}")

    elif cmd == "sensitivity":
        shifts = _parse_floats(getattr(args, "shifts", None))
        tenors = _parse_floats(getattr(args, "tenors", None))
        data = sensitivity_matrix(
            face_value=args.face_value, coupon_rate=args.coupon_rate,
            frequency=args.frequency, base_ytm=args.base_ytm,
            rate_shifts=shifts, tenors=tenors,
        )
        if getattr(args, "json_out", False):
            json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print_sensitivity_matrix(data)

    elif cmd == "oas":
        call_yrs = _parse_floats(getattr(args, "call_years", None))
        ref_t = _parse_floats(getattr(args, "ref_tenors", None))
        ref_y = _parse_floats(getattr(args, "ref_yields", None))
        r = compute_oas(
            face_value=args.face_value, coupon_rate=args.coupon_rate,
            frequency=args.frequency, maturity_years=args.maturity_years,
            market_price=args.market_price, call_price=args.call_price,
            call_years=call_yrs,
            ref_curve_tenors=ref_t, ref_curve_yields=ref_y,
        )
        if getattr(args, "json_out", False):
            json.dump(r, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"\nOAS ANALYSIS (simplified)")
            print(f"  Market Price:     {r['market_price']:.4f}")
            print(f"  Vanilla (no-opt): {r['vanilla_price']:.4f}")
            print(f"  Benchmark YTM:    {r['benchmark_ytm_pct']:.4f}%")
            print(f"  Call Price:       {r['call_price']:.2f}")
            print(f"  Call Dates:       {r['call_years']}")
            print(f"  Z-Spread:         {r['z_spread_bps']:.2f} bp")
            print(f"  Option Cost (est):{r['option_cost_est_bps']:.2f} bp")
            print(f"  OAS Estimate:     {r['oas_est_bps']:.2f} bp")
            print(f"  Note:             {r['note']}")

    elif cmd == "compare-products":
        products = None
        if getattr(args, "products", None):
            products = [p.strip() for p in args.products.split(",")]
        data = cross_product_comparison(
            face_value=args.face_value, coupon_rate=args.coupon_rate,
            frequency=args.frequency, maturity_years=args.maturity_years,
            base_ytm=args.base_ytm, product_types=products,
        )
        if getattr(args, "json_out", False):
            json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print_cross_product(data)

    else:
        # ── No subcommand: backward-compat original pricing ──
        if getattr(args, "coupon_rate", None) is None:
            parser.print_help()
            sys.exit(1)
        if getattr(args, "maturity_years", None) is None:
            parser.error("--maturity-years is required")
        if getattr(args, "ytm", None) is None:
            parser.error("--ytm is required")

        if args.frequency == 2 and args.maturity_years < 0.5:
            parser.error("Semi-annual maturity >= 0.5 yr for at least 1 period.")
        if args.frequency == 1 and args.maturity_years < 1.0:
            parser.error("Annual maturity >= 1.0 yr for at least 1 period.")
        if args.ytm < -99.0 or args.ytm > 99.0:
            parser.error("YTM seems unreasonable.")
        if args.coupon_rate < 0:
            parser.error("Coupon rate must be non-negative.")

        try:
            result = compute_analytics(
                face_value=args.face_value, coupon_rate=args.coupon_rate,
                frequency=args.frequency, maturity_years=args.maturity_years,
                ytm=args.ytm, settlement_days_from_now=args.settlement_days,
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        if getattr(args, "json_out", False):
            json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
        else:
            print_analytics(result)


if __name__ == "__main__":
    main()

# v1.8 定价增强 | 2026-05-11