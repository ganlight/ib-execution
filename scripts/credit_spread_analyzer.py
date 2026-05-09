#!/usr/bin/env python3
"""
Credit Spread Analyzer — Bond Comparables Screening Tool.

Reads a set of comparable bonds (from a JSON file or inline data), calculates
credit spreads against a benchmark yield, and produces summary statistics by
rating bucket, implied fair YTMs for target ratings, and a spread-curve table.

Usage:
  # From a JSON file
  python credit_spread_analyzer.py --file comps.json \\
      --benchmark 2.85 --target-rating AA+

  # Inline JSON
  python credit_spread_analyzer.py --data '[{"name":"XXMTN01","issuer":"StateGrid",
      "rating":"AAA","tenor_years":3,"ytm":3.10,"issue_date":"2025-01-10","amount":30}]'
      --benchmark 2.85

  # With benchmark label
  python credit_spread_analyzer.py --file comps.json \\
      --benchmark 2.85 --benchmark-label "CGB 3Y" --target-rating AA+

  # JSON output
  python credit_spread_analyzer.py --json --file comps.json \\
      --benchmark 2.85 --target-rating AA
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ComparableBond:
    """A single comparable bond entry."""
    name: str
    issuer: str
    rating: str
    tenor_years: float
    ytm: float          # %
    issue_date: str
    amount: float       # 亿元


@dataclass
class BondSpread:
    """A bond with its computed credit spread."""
    bond: ComparableBond
    spread_bps: float   # basis points

    @property
    def spread_pct(self) -> float:
        return self.spread_bps / 100.0


@dataclass
class RatingBucketStats:
    """Aggregate statistics for one rating bucket."""
    rating: str
    count: int
    avg_spread_bps: float
    min_spread_bps: float
    max_spread_bps: float
    median_spread_bps: float
    bonds: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def load_comparables(raw: List[dict]) -> List[ComparableBond]:
    """Parse raw dicts into ComparableBond objects with validation."""
    bonds: List[ComparableBond] = []
    for i, item in enumerate(raw):
        try:
            bonds.append(ComparableBond(
                name=item["name"],
                issuer=item["issuer"],
                rating=item["rating"],
                tenor_years=float(item["tenor_years"]),
                ytm=float(item["ytm"]),
                issue_date=str(item["issue_date"]),
                amount=float(item["amount"]),
            ))
        except (KeyError, ValueError, TypeError) as exc:
            print(f"Warning: skipping malformed entry #{i}: {exc}", file=sys.stderr)
            continue
    return bonds


def compute_spreads(
    bonds: List[ComparableBond],
    benchmark_yield: float,
) -> List[BondSpread]:
    """Compute credit spread (YTM – benchmark) in basis points for each bond."""
    return [
        BondSpread(bond=b, spread_bps=round((b.ytm - benchmark_yield) * 100.0, 2))
        for b in bonds
    ]


def aggregate_by_rating(
    spreads: List[BondSpread],
    target_rating: Optional[str] = None,
) -> List[RatingBucketStats]:
    """Group spreads by rating bucket and compute summary statistics."""
    grouped: Dict[str, List[BondSpread]] = {}
    for s in spreads:
        r = s.bond.rating
        if target_rating and r != target_rating:
            continue
        grouped.setdefault(r, []).append(s)

    stats: List[RatingBucketStats] = []
    for rating in sorted(grouped.keys()):
        group = grouped[rating]
        spread_vals = [s.spread_bps for s in group]
        stats.append(RatingBucketStats(
            rating=rating,
            count=len(group),
            avg_spread_bps=round(statistics.mean(spread_vals), 2),
            min_spread_bps=round(min(spread_vals), 2),
            max_spread_bps=round(max(spread_vals), 2),
            median_spread_bps=round(statistics.median(spread_vals), 2),
            bonds=[s.bond.name for s in group],
        ))
    return stats


def implied_fair_ytm(
    all_stats: List[RatingBucketStats],
    target_rating: str,
    benchmark_yield: float,
) -> Optional[float]:
    """
    Estimate a fair YTM for the target rating by taking the average spread
    of that rating bucket and adding the benchmark yield.
    """
    for st in all_stats:
        if st.rating == target_rating:
            return round(benchmark_yield + st.avg_spread_bps / 100.0, 4)
    return None


def spread_curve_data(
    spreads: List[BondSpread],
) -> List[Dict]:
    """Produce (tenor, spread_bps) data points for spread-curve analysis."""
    points = sorted(
        [{"tenor_years": s.bond.tenor_years, "spread_bps": s.spread_bps,
          "name": s.bond.name, "rating": s.bond.rating}
         for s in spreads],
        key=lambda x: x["tenor_years"],
    )
    return points


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------

def print_analysis(
    bonds: List[ComparableBond],
    spreads: List[BondSpread],
    bucket_stats: List[RatingBucketStats],
    curve_data: List[Dict],
    benchmark_yield: float,
    benchmark_label: str,
    target_rating: Optional[str],
    fair_ytm: Optional[float],
    show_all_stats: bool,
) -> None:
    """Pretty-print the full credit-spread analysis."""

    print("=" * 76)
    print("  CREDIT SPREAD ANALYZER — COMPARABLE BOND SCREENING")
    print("=" * 76)
    print(f"  Benchmark:  {benchmark_label} = {benchmark_yield:.4f}%")
    print(f"  Comparables loaded: {len(bonds)}")
    if target_rating:
        print(f"  Target rating filter: {target_rating}")
    print()

    # ---- Summary statistics by rating ----
    print("-" * 76)
    print("  SUMMARY STATISTICS BY RATING BUCKET")
    print("-" * 76)
    header = (
        f"  {'Rating':>6s}  {'Count':>5s}  "
        f"{'Avg(bps)':>9s}  {'Min(bps)':>9s}  "
        f"{'Max(bps)':>9s}  {'Med(bps)':>9s}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for st in bucket_stats:
        print(
            f"  {st.rating:>6s}  {st.count:>5d}  "
            f"{st.avg_spread_bps:>9.2f}  {st.min_spread_bps:>9.2f}  "
            f"{st.max_spread_bps:>9.2f}  {st.median_spread_bps:>9.2f}"
        )
    print()

    # ---- Implied fair YTM ----
    if fair_ytm is not None and target_rating:
        print(f"  → Implied Fair YTM for {target_rating}:  {fair_ytm:.4f}%")
        print(f"    (benchmark {benchmark_yield:.4f}% + avg spread of {target_rating} bucket)")
        print()

    # ---- All rating stats (unfiltered) ----
    if show_all_stats and target_rating:
        print("-" * 76)
        print(f"  ALL RATING BUCKETS (unfiltered overview)")
        print("-" * 76)
        print(header)
        print("  " + "-" * (len(header) - 2))
        for st in bucket_stats:
            print(
                f"  {st.rating:>6s}  {st.count:>5d}  "
                f"{st.avg_spread_bps:>9.2f}  {st.min_spread_bps:>9.2f}  "
                f"{st.max_spread_bps:>9.2f}  {st.median_spread_bps:>9.2f}"
            )
        print()

    # ---- Detailed comparable table ----
    print("-" * 76)
    print("  DETAILED COMPARABLE BOND TABLE")
    print("-" * 76)
    detail_header = (
        f"  {'Name':<18s}  {'Issuer':<14s}  {'Rating':>6s}  "
        f"{'Tenor':>6s}  {'YTM%':>7s}  {'Spread':>8s}  {'Amt(亿)':>8s}"
    )
    print(detail_header)
    print("  " + "-" * (len(detail_header) - 2))

    # Sort by spread descending
    for s in sorted(spreads, key=lambda x: -x.spread_bps):
        b = s.bond
        print(
            f"  {b.name[:17]:<18s}  {b.issuer[:13]:<14s}  {b.rating:>6s}  "
            f"{b.tenor_years:>5.1f}yr  {b.ytm:>7.4f}  {s.spread_bps:>7.1f}bp  "
            f"{b.amount:>8.1f}"
        )
    print()

    # ---- Spread curve analysis ----
    print("-" * 76)
    print("  SPREAD CURVE ANALYSIS (tenor vs spread)")
    print("-" * 76)
    curve_header = (
        f"  {'Tenor(yr)':>10s}  {'Spread(bps)':>12s}  "
        f"{'Rating':>7s}  {'Name':<18s}"
    )
    print(curve_header)
    print("  " + "-" * (len(curve_header) - 2))
    for pt in curve_data:
        print(
            f"  {pt['tenor_years']:>10.2f}  {pt['spread_bps']:>12.2f}  "
            f"{pt['rating']:>7s}  {pt['name'][:17]:<18s}"
        )
    print()

    # ---- Interpretation ----
    if bucket_stats:
        print("-" * 76)
        print("  INTERPRETATION")
        print("-" * 76)
        tightest = min(bucket_stats, key=lambda s: s.avg_spread_bps)
        widest = max(bucket_stats, key=lambda s: s.avg_spread_bps)
        print(f"  Tightest bucket:  {tightest.rating} (avg {tightest.avg_spread_bps:.1f} bp)")
        print(f"  Widest bucket:    {widest.rating}  (avg {widest.avg_spread_bps:.1f} bp)")
        spread_range = widest.avg_spread_bps - tightest.avg_spread_bps
        print(f"  Rating premium:   {spread_range:.1f} bp spread between {tightest.rating} → {widest.rating}")

    print("=" * 76)


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def json_output(
    bonds: List[ComparableBond],
    spreads: List[BondSpread],
    bucket_stats: List[RatingBucketStats],
    curve_data: List[Dict],
    benchmark_yield: float,
    benchmark_label: str,
    target_rating: Optional[str],
    fair_ytm: Optional[float],
) -> None:
    payload = {
        "inputs": {
            "benchmark_yield_pct": benchmark_yield,
            "benchmark_label": benchmark_label,
            "total_comparables": len(bonds),
            "target_rating": target_rating,
        },
        "summary_by_rating": [
            {
                "rating": s.rating,
                "count": s.count,
                "avg_spread_bps": s.avg_spread_bps,
                "min_spread_bps": s.min_spread_bps,
                "max_spread_bps": s.max_spread_bps,
                "median_spread_bps": s.median_spread_bps,
                "bonds": s.bonds,
            }
            for s in bucket_stats
        ],
        "fair_ytm_implied": fair_ytm,
        "comparables": [
            {
                "name": s.bond.name,
                "issuer": s.bond.issuer,
                "rating": s.bond.rating,
                "tenor_years": s.bond.tenor_years,
                "ytm_pct": s.bond.ytm,
                "issue_date": s.bond.issue_date,
                "amount_亿": s.bond.amount,
                "spread_bps": s.spread_bps,
            }
            for s in sorted(spreads, key=lambda x: -x.spread_bps)
        ],
        "spread_curve": curve_data,
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

BENCHMARK_DEFAULTS: Dict[str, float] = {
    "CGB 1Y": 1.85,
    "CGB 3Y": 2.55,
    "CGB 5Y": 2.75,
    "CGB 7Y": 2.90,
    "CGB 10Y": 3.05,
    "CGB 30Y": 3.40,
    "CDB 1Y": 2.10,
    "CDB 3Y": 2.70,
    "CDB 5Y": 2.90,
    "CDB 10Y": 3.20,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Credit spread analysis for bond comparable screening.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file comps.json --benchmark 2.55 --benchmark-label "CGB 3Y"

  %(prog)s --data '[{"name":"XXMTN01","issuer":"GridCo","rating":"AAA",
      "tenor_years":3,"ytm":3.10,"issue_date":"2025-01-10","amount":30},
      {"name":"XXMTN02","issuer":"OilCo","rating":"AA+","tenor_years":5,
      "ytm":3.85,"issue_date":"2025-03-01","amount":20}]'
      --benchmark 2.55 --benchmark-label "CGB 3Y" --target-rating AA

  %(prog)s --json --file comps.json --benchmark 2.55 --target-rating AA+
        """,
    )

    input_group = p.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", dest="file_path",
                             help="Path to JSON file with comparable bond list")
    input_group.add_argument("--data", dest="inline_data",
                             help="Inline JSON array of comparable bonds")

    p.add_argument("--benchmark", type=float, required=True,
                   help="Benchmark yield in %% (e.g. 2.55 for CGB 3Y @ 2.55%%)")
    p.add_argument("--benchmark-label", default="Custom",
                   help="Label for the benchmark (e.g. 'CGB 3Y')")
    p.add_argument("--target-rating", dest="target_rating", default=None,
                   help="Filter comparables to this rating (e.g. AA+)")
    p.add_argument("--all-stats", action="store_true",
                   help="Show stats for all rating buckets, not just target")
    p.add_argument("--json", dest="json_out", action="store_true",
                   help="Output JSON instead of formatted text")
    return p


def load_comparables_from_args(args) -> List[ComparableBond]:
    """Load comparable bonds from --file or --data."""
    raw: List[dict]
    if args.file_path:
        try:
            with open(args.file_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except FileNotFoundError:
            print(f"Error: file not found: {args.file_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid JSON in {args.file_path}: {exc}", file=sys.stderr)
            sys.exit(1)
    elif args.inline_data:
        try:
            raw = json.loads(args.inline_data)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid inline JSON: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: must provide --file or --data", file=sys.stderr)
        sys.exit(1)

    if not isinstance(raw, list):
        print("Error: input JSON must be an array of bond objects", file=sys.stderr)
        sys.exit(1)

    if not raw:
        print("Error: no comparable bonds found in input", file=sys.stderr)
        sys.exit(1)

    return load_comparables(raw)


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    bonds = load_comparables_from_args(args)
    benchmark = args.benchmark
    benchmark_label = args.benchmark_label
    target_rating = args.target_rating

    spreads = compute_spreads(bonds, benchmark)

    # Stats for the filtered view
    filtered_stats = aggregate_by_rating(spreads, target_rating)

    # Full stats (for --all-stats or when no target)
    all_stats = filtered_stats if target_rating else filtered_stats
    if args.all_stats and target_rating:
        all_stats = aggregate_by_rating(spreads, None)

    fair_ytm = implied_fair_ytm(all_stats, target_rating, benchmark) if target_rating else None
    curve_data = spread_curve_data(spreads)

    if args.json_out:
        json_output(
            bonds, spreads,
            bucket_stats=filtered_stats,
            curve_data=curve_data,
            benchmark_yield=benchmark,
            benchmark_label=benchmark_label,
            target_rating=target_rating,
            fair_ytm=fair_ytm,
        )
    else:
        print_analysis(
            bonds, spreads,
            bucket_stats=filtered_stats,
            curve_data=curve_data,
            benchmark_yield=benchmark,
            benchmark_label=benchmark_label,
            target_rating=target_rating,
            fair_ytm=fair_ytm,
            show_all_stats=args.all_stats,
        )


# ---------------------------------------------------------------------------
# Built-in test cases (run with: python credit_spread_analyzer.py --test)
# ---------------------------------------------------------------------------

_TEST_DATA = json.dumps([
    {"name": "CHNGUA MTN 3Y", "issuer": "华能国际", "rating": "AAA",
     "tenor_years": 3.0, "ytm": 2.85, "issue_date": "2025-03-15", "amount": 30},
    {"name": "SINOPEC MTN 5Y", "issuer": "中石化", "rating": "AAA",
     "tenor_years": 5.0, "ytm": 3.10, "issue_date": "2025-04-01", "amount": 50},
    {"name": "SDGOLD MTN 3Y", "issuer": "山东黄金", "rating": "AA+",
     "tenor_years": 3.0, "ytm": 3.35, "issue_date": "2025-02-20", "amount": 20},
    {"name": "ZIJIN MTN 5Y", "issuer": "紫金矿业", "rating": "AA+",
     "tenor_years": 5.0, "ytm": 3.65, "issue_date": "2025-01-10", "amount": 25},
    {"name": "TSINGTAO CP 1Y", "issuer": "青岛啤酒", "rating": "AA+",
     "tenor_years": 1.0, "ytm": 2.65, "issue_date": "2025-05-01", "amount": 15},
    {"name": "SANY MTN 3Y", "issuer": "三一重工", "rating": "AA",
     "tenor_years": 3.0, "ytm": 4.20, "issue_date": "2025-03-05", "amount": 12},
    {"name": "LENOVO MTN 5Y", "issuer": "联想集团", "rating": "AA",
     "tenor_years": 5.0, "ytm": 4.55, "issue_date": "2025-02-28", "amount": 10},
    {"name": "CHALCO MTN 7Y", "issuer": "中国铝业", "rating": "AA+",
     "tenor_years": 7.0, "ytm": 4.10, "issue_date": "2025-01-20", "amount": 18},
    {"name": "CRLAND MTN 3Y", "issuer": "华润置地", "rating": "AAA",
     "tenor_years": 3.0, "ytm": 3.05, "issue_date": "2025-04-10", "amount": 40},
    {"name": "VNKE MTN 3Y", "issuer": "万科企业", "rating": "AA",
     "tenor_years": 3.0, "ytm": 4.80, "issue_date": "2025-05-20", "amount": 8},
])


def run_tests() -> None:
    """Run built-in test cases."""
    print("=== TEST 1: Full analysis with benchmark CGB 3Y @ 2.55% ===")
    main(["--data", _TEST_DATA, "--benchmark", "2.55",
          "--benchmark-label", "CGB 3Y"])

    print("\n\n=== TEST 2: Target rating AA+ only ===")
    main(["--data", _TEST_DATA, "--benchmark", "2.55",
          "--benchmark-label", "CGB 3Y", "--target-rating", "AA+"])

    print("\n\n=== TEST 3: JSON output ===")
    main(["--data", _TEST_DATA, "--benchmark", "2.55",
          "--benchmark-label", "CGB 3Y", "--target-rating", "AA", "--json"])


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        run_tests()
    else:
        main()