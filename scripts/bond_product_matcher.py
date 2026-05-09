#!/usr/bin/env python3
"""
Bond Product Matcher — Decision Engine for Chinese Bond Underwriting.

Matches an issuer profile against the full menu of onshore China bond products
and returns a ranked list with match scores, fit reasons, disqualifiers, and
regulatory guidance.

Bond products covered:
  企业债 (Enterprise Bond)         金融债 (Financial Bond)
  公募公司债 (Public Corporate Bond)  PPN (定向工具)
  私募公司债 (Private Corporate Bond) SCP (超短期融资券)
  MTN (中期票据)                     ABS (资产支持证券)
  CP (短期融资券)

Usage:
  python bond_product_matcher.py --type SOE --rating AAA --industry utilities \
      --asset-size 500 --revenue 200 --net-profit 50 --debt-ratio 60 \
      --amount 30 --tenor 5 --purpose project

  python bond_product_matcher.py --json ...   # machine-readable output
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Rating helpers
# ---------------------------------------------------------------------------
RATING_ORDER: Dict[str, int] = {
    "AAA": 6,
    "AA+": 5,
    "AA": 4,
    "AA-": 3,
    "A+": 2,
    "A": 1,
    "A-": 0,
}


def rating_at_least(issuer_rating: str, threshold: str) -> bool:
    """Return True if *issuer_rating* is equal to or better than *threshold*."""
    return RATING_ORDER.get(issuer_rating, -1) >= RATING_ORDER.get(threshold, 99)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class IssuerProfile:
    """All fields describing the prospective issuer."""

    issuer_type: str  # SOE | LGFV | private | listco | financial
    credit_rating: str  # AAA | AA+ | AA | AA- | ...
    industry: str
    asset_size: float  # 亿元
    revenue: float  # 亿元
    net_profit: float  # 亿元
    debt_ratio: float  # %
    desired_amount: float  # 亿元
    desired_tenor: float  # years
    purpose: str  # general | refinance | project | green | M&A
    has_underlying_assets: bool = False  # for ABS
    is_listed: bool = False  # pre-derived for convenience


@dataclass
class ProductMatch:
    """A single bond-product match result."""

    product_name: str
    product_name_cn: str
    match_score: int  # 0–100
    fit_reasons: List[str] = field(default_factory=list)
    disqualifiers: List[str] = field(default_factory=list)
    regulatory_notes: str = ""
    issuer_requirements: str = ""


# ---------------------------------------------------------------------------
# Product evaluators — each returns (score 0..100, fit_reasons, disqualifiers)
# ---------------------------------------------------------------------------


def _score_from_checks(
    passed: int, total: int, scaling: int = 100
) -> int:
    """Simple linear scoring: (passed / total) * scaling, clamped to [0, scaling]."""
    if total == 0:
        return scaling
    return max(0, min(scaling, round(passed / total * scaling)))


# --- Enterprise Bond (企业债) -------------------------------------------------


def eval_enterprise_bond(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 5
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    # Type
    if p.issuer_type in ("SOE", "LGFV"):
        checks_passed += 1
        fit.append(f"Type {p.issuer_type} is eligible")
    else:
        dq.append("Only SOE/LGFV issuers qualify")

    # Rating
    if rating_at_least(p.credit_rating, "AA+"):
        checks_passed += 1
        fit.append(f"Rating {p.credit_rating} meets AA+ minimum")
    else:
        dq.append("Requires AA+ or above")

    # Tenor
    if 5 <= p.desired_tenor <= 15:
        checks_passed += 1
        fit.append(f"Tenor {p.desired_tenor}yr within 5–15yr range")
    elif p.desired_tenor < 5:
        dq.append("Tenor below 5yr minimum (NDRC rarely approves <5yr)")
    else:
        dq.append("Tenor above 15yr maximum")

    # Purpose
    if p.purpose in ("general", "refinance", "project", "green"):
        checks_passed += 1
        fit.append(f"Purpose '{p.purpose}' fits enterprise bond")
    elif p.purpose == "M&A":
        dq.append("Enterprise bonds generally exclude M&A purposes")

    # Asset scale (heuristic: ≥50亿 for NDRC comfort)
    if p.asset_size >= 50:
        checks_passed += 1
        fit.append("Asset scale sufficient for NDRC approval")
    else:
        dq.append("Asset size <50亿 may face NDRC scrutiny")

    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- Public Corporate Bond (公募公司债) ---------------------------------------


def eval_public_corp_bond(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 5
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    # Type
    if p.issuer_type in ("listco",) or p.is_listed:
        checks_passed += 1
        fit.append("Listed/qualified public company")
    elif p.issuer_type == "private":
        dq.append("Requires listed or qualified public-company status")
    else:
        dq.append("SOE/LGFV usually prefer enterprise bonds; CSRC regime applies")

    # Rating
    if rating_at_least(p.credit_rating, "AA"):
        checks_passed += 1
        fit.append(f"Rating {p.credit_rating} meets AA minimum")
    else:
        dq.append("Requires AA or above")

    # Net asset test (asset_size is a proxy for net asset here)
    # CSRC: ≥6亿 for general; ≥12亿 for listed (simplified)
    if p.asset_size >= 12:
        checks_passed += 1
        fit.append(f"Net asset proxy {p.asset_size}≥12亿 (listed OK)")
    elif p.asset_size >= 6:
        fit.append(f"Net asset proxy {p.asset_size}≥6亿 (non-listed OK)")
        checks_passed += 1
    else:
        dq.append("Net asset <6亿 does not meet public-offering threshold")

    # 40% rule (cumulative bonds ≤40% of net asset)
    bond_ratio = (p.desired_amount / p.asset_size) * 100 if p.asset_size else 999
    if bond_ratio <= 40:
        checks_passed += 1
        fit.append(f"Cumulative {bond_ratio:.1f}% ≤ 40% of net asset")
    else:
        dq.append(f"Cumulative {bond_ratio:.1f}% > 40% of net asset ceiling")

    # Purpose
    if p.purpose != "M&A":
        checks_passed += 1
        fit.append(f"Purpose '{p.purpose}' allowed")
    else:
        dq.append("M&A purpose may trigger additional CSRC review")

    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- Private Corporate Bond (私募公司债) --------------------------------------


def eval_private_corp_bond(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 4
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    # Rating — can skip rating
    if rating_at_least(p.credit_rating, "AA-"):
        checks_passed += 1
        fit.append(f"Rating {p.credit_rating} provides investor comfort")
    else:
        fit.append("Rating can be waived for private placement")

    # 200-investor limit (always satisfied for generic check)
    checks_passed += 1
    fit.append("≤200 qualified investors (private placement)")

    # No minimum asset test
    checks_passed += 1
    fit.append("No statutory minimum net-asset test")

    # Purpose flexibility
    checks_passed += 1
    fit.append("Broad use-of-proceeds flexibility")

    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- MTN (中期票据) ------------------------------------------------------------


def eval_mtn(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 5
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    # Any type OK
    checks_passed += 1
    fit.append(f"All issuer types accepted by NAFMII")

    # Rating
    if rating_at_least(p.credit_rating, "AA"):
        checks_passed += 1
        fit.append(f"Rating {p.credit_rating} meets AA minimum")
    else:
        dq.append("Requires AA or above")

    # Tenor sweet spot 3–5yr (but 7–10yr also available)
    if 3 <= p.desired_tenor <= 7:
        checks_passed += 1
        fit.append(f"Tenor {p.desired_tenor}yr fits typical 3–5(–7)yr range")
    elif p.desired_tenor < 3:
        fit.append(f"Tenor {p.desired_tenor}yr is short; consider CP/SCP instead")
    else:
        fit.append(f"Tenor {p.desired_tenor}yr is long; shelf registration still possible")

    # Shelf registration
    checks_passed += 1
    fit.append("NAFMII shelf registration (2yr validity)")

    # Purpose
    if p.purpose in ("general", "refinance", "project", "M&A", "green"):
        checks_passed += 1
        fit.append(f"Purpose '{p.purpose}' allowed")
    else:
        dq.append("Unrecognised purpose")

    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- CP (短期融资券) -----------------------------------------------------------


def eval_cp(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 3
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    if rating_at_least(p.credit_rating, "AA"):
        checks_passed += 1
        fit.append(f"Rating {p.credit_rating} meets AA minimum")
    else:
        dq.append("Requires AA or above")

    if p.desired_tenor <= 1.0:
        checks_passed += 1
        fit.append(f"Tenor {p.desired_tenor}yr ≤ 1yr fits CP")
    else:
        dq.append(f"Tenor {p.desired_tenor}yr exceeds 1yr CP maximum")

    checks_passed += 1
    fit.append("Open to all issuer types under NAFMII")
    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- SCP (超短期融资券) --------------------------------------------------------


def eval_scp(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 3
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    if p.credit_rating == "AAA":
        checks_passed += 1
        fit.append("AAA rating — SCP eligible")
    else:
        dq.append("AAA-only product; current rating does not qualify")

    if p.desired_tenor <= 0.7397:  # ≤270 days
        checks_passed += 1
        fit.append(f"Tenor {p.desired_tenor}yr ≤ 270 days fits SCP")
    else:
        dq.append(f"Tenor {p.desired_tenor}yr exceeds 270-day SCP limit")

    checks_passed += 1
    fit.append("Fast-track NAFMII registration")
    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- PPN (定向工具) -----------------------------------------------------------


def eval_ppn(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 3
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    # Flexible rating
    if p.credit_rating:
        fit.append(f"Rating {p.credit_rating} (can be unrated)")
    else:
        fit.append("Unrated OK for private placement")
    checks_passed += 1

    checks_passed += 1
    fit.append("No public disclosure burdens")

    checks_passed += 1
    fit.append("Flexible tenor and use-of-proceeds")
    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- Financial Bond (金融债) --------------------------------------------------


def eval_financial_bond(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 3
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    if p.issuer_type == "financial":
        checks_passed += 1
        fit.append("Financial institution — eligible for financial bond")
    else:
        dq.append("Restricted to financial institutions (banks, insurers, AMCs, etc.)")

    if rating_at_least(p.credit_rating, "AA"):
        checks_passed += 1
        fit.append(f"Rating {p.credit_rating} meets typical AA threshold")
    else:
        dq.append("Most financial bonds need AA or above per PBOC/CBIRC")

    checks_passed += 1
    fit.append("PBOC/CBIRC dual-approval pathway")
    return _score_from_checks(checks_passed, checks_total), fit, dq


# --- ABS (资产支持证券) -------------------------------------------------------


def eval_abs(p: IssuerProfile) -> Tuple[int, List[str], List[str]]:
    checks_total = 3
    checks_passed = 0
    fit: List[str] = []
    dq: List[str] = []

    if p.has_underlying_assets:
        checks_passed += 1
        fit.append("Underlying assets/cash flows confirmed")
    else:
        dq.append("Requires identifiable underlying assets or predictable cash flows")

    checks_passed += 1
    fit.append("Credit based on asset pool, not issuer rating")

    checks_passed += 1
    fit.append("Multi-tranche structuring possible (senior/mezzanine/equity)")
    return _score_from_checks(checks_passed, checks_total), fit, dq


# ---------------------------------------------------------------------------
# Product registry
# ---------------------------------------------------------------------------

PRODUCT_REGISTRY: List[Tuple[str, str, str, str, callable]] = [
    (
        "enterprise_bond",
        "企业债 (Enterprise Bond)",
        "NDRC approval required; SOE/LGFV, AA+ and above, 5–15yr tenor.",
        "SOE/LGFV status; AA+ or above; project/investment purpose; NDRC quota.",
        eval_enterprise_bond,
    ),
    (
        "public_corp_bond",
        "公募公司债 (Public Corporate Bond)",
        "CSRC-qualified; listed/public company, AA and above, net asset ≥6/12亿, cumulative ≤40% net asset.",
        "Listed/public company status; AA+ recommended for lower coupon; AA bare minimum.",
        eval_public_corp_bond,
    ),
    (
        "private_corp_bond",
        "私募公司债 (Private Corporate Bond)",
        "Flexible; ≤200 qualified investors; rating can be waived; faster exchange filing.",
        "No hard rating floor; suitable for unrated or sub-AA issuers; general corporate.",
        eval_private_corp_bond,
    ),
    (
        "mtn",
        "中期票据 (MTN)",
        "NAFMII shelf registration (2yr validity); AA and above; typical 3–5yr.",
        "AA or above; any non-financial issuer type; 3–5yr sweet spot.",
        eval_mtn,
    ),
    (
        "cp",
        "短期融资券 (CP)",
        "NAFMII registered; AA and above; ≤1yr tenor; working-capital oriented.",
        "AA or above; tenor ≤1yr; working-capital or bridge financing.",
        eval_cp,
    ),
    (
        "scp",
        "超短期融资券 (SCP)",
        "AAA-only; ≤270 days; fast-track NAFMII registration; money-market oriented.",
        "AAA only; tenor ≤270 days; strong short-term liquidity profile.",
        eval_scp,
    ),
    (
        "ppn",
        "定向工具 (PPN)",
        "Private placement under NAFMII; flexible rating/tenor; limited disclosure.",
        "Any type; can be unrated; suitable for smaller/non-public entities.",
        eval_ppn,
    ),
    (
        "financial_bond",
        "金融债 (Financial Bond)",
        "PBOC/CBIRC approval; financial institutions only; includes sub-debt and tier-2.",
        "Licensed financial institution; AA or above typical; subordinated allowed.",
        eval_financial_bond,
    ),
    (
        "abs",
        "资产支持证券 (ABS)",
        "Structured product based on asset pool; SPV/SPT structure; rated by tranche.",
        "Underlying asset pool with predictable cash flows; independent rating per tranche.",
        eval_abs,
    ),
]


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def match_products(profile: IssuerProfile) -> List[ProductMatch]:
    """Evaluate every bond product against the issuer profile and return ranked matches."""
    results: List[ProductMatch] = []
    for prod_id, prod_name_cn, reg_notes, issuer_reqs, evaluator in PRODUCT_REGISTRY:
        score, fit, dq = evaluator(profile)
        total_dq = len(dq)
        # If *any* hard disqualifier, cap the score
        if total_dq > 0:
            score = min(score, max(0, 100 - total_dq * 25))
        results.append(
            ProductMatch(
                product_name=prod_id,
                product_name_cn=prod_name_cn,
                match_score=score,
                fit_reasons=fit,
                disqualifiers=dq,
                regulatory_notes=reg_notes,
                issuer_requirements=issuer_reqs,
            )
        )
    results.sort(key=lambda r: (-r.match_score, r.product_name))
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Match an issuer profile to available Chinese bond products.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --type SOE --rating AAA --industry utilities \\
      --asset-size 500 --revenue 200 --net-profit 50 --debt-ratio 60 \\
      --amount 30 --tenor 5 --purpose project

  %(prog)s --type listco --rating AA --industry tech \\
      --asset-size 80 --revenue 40 --net-profit 8 --debt-ratio 55 \\
      --amount 10 --tenor 3 --purpose refinance --listed

  %(prog)s --json --type SOE --rating AA --industry real-estate \\
      --asset-size 200 --revenue 80 --net-profit 5 --debt-ratio 75 \\
      --amount 20 --tenor 7 --purpose general
        """,
    )
    p.add_argument("--type", required=True,
                   choices=["SOE", "LGFV", "private", "listco", "financial"],
                   help="Issuer type")
    p.add_argument("--rating", required=True,
                   help="External credit rating (e.g. AAA, AA+, AA, AA-)")
    p.add_argument("--industry", required=True, help="Industry sector")
    p.add_argument("--asset-size", type=float, required=True, help="Total assets (亿元)")
    p.add_argument("--revenue", type=float, required=True, help="Annual revenue (亿元)")
    p.add_argument("--net-profit", type=float, required=True, help="Net profit (亿元)")
    p.add_argument("--debt-ratio", type=float, required=True, help="Debt-to-asset ratio (％)")
    p.add_argument("--amount", type=float, required=True, help="Desired issuance amount (亿元)")
    p.add_argument("--tenor", type=float, required=True, help="Desired tenor (years)")
    p.add_argument("--purpose", required=True,
                   choices=["general", "refinance", "project", "green", "M&A"],
                   help="Use of proceeds")
    p.add_argument("--listed", action="store_true", help="Flag if the issuer is listed")
    p.add_argument("--has-assets", action="store_true",
                   help="Flag if underlying assets exist (for ABS)")
    p.add_argument("--json", dest="json_out", action="store_true",
                   help="Output JSON instead of human-readable text")
    return p


def text_output(matches: List[ProductMatch], profile: IssuerProfile) -> None:
    """Print a formatted text table of results."""
    print("=" * 78)
    print("  BOND PRODUCT MATCHER — RESULTS")
    print("=" * 78)
    print(f"  Issuer: {profile.issuer_type} | Rating: {profile.credit_rating}")
    print(f"  Industry: {profile.industry} | Assets: {profile.asset_size:.0f}亿")
    print(f"  Amount: {profile.desired_amount:.0f}亿 | Tenor: {profile.desired_tenor:.1f}yr")
    print(f"  Purpose: {profile.purpose} | Listed: {profile.is_listed}")
    print("-" * 78)

    for rank, m in enumerate(matches, 1):
        bar = "█" * (m.match_score // 5)
        print(f"\n  #{rank}  {m.product_name_cn}")
        print(f"       Score: {m.match_score:3d}/100  {bar}")
        if m.fit_reasons:
            for r in m.fit_reasons:
                print(f"         ✓ {r}")
        if m.disqualifiers:
            for d in m.disqualifiers:
                print(f"         ✗ {d}")
        print(f"       Reg:  {m.regulatory_notes}")
        print(f"       Reqs: {m.issuer_requirements}")

    print("\n" + "=" * 78)
    print("  Legend: ✓ = fit reason   ✗ = disqualifier / concern")
    print("=" * 78)


def json_output(matches: List[ProductMatch], profile: IssuerProfile) -> None:
    """Print JSON output."""
    payload = {
        "issuer_profile": {
            "type": profile.issuer_type,
            "credit_rating": profile.credit_rating,
            "industry": profile.industry,
            "asset_size_亿": profile.asset_size,
            "revenue_亿": profile.revenue,
            "net_profit_亿": profile.net_profit,
            "debt_ratio_pct": profile.debt_ratio,
            "desired_amount_亿": profile.desired_amount,
            "desired_tenor_yr": profile.desired_tenor,
            "purpose": profile.purpose,
            "is_listed": profile.is_listed,
        },
        "matches": [asdict(m) for m in matches],
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    profile = IssuerProfile(
        issuer_type=args.type,
        credit_rating=args.rating.upper(),
        industry=args.industry,
        asset_size=args.asset_size,
        revenue=args.revenue,
        net_profit=args.net_profit,
        debt_ratio=args.debt_ratio,
        desired_amount=args.amount,
        desired_tenor=args.tenor,
        purpose=args.purpose,
        is_listed=args.listed,
    )

    matches = match_products(profile)

    if args.json_out:
        json_output(matches, profile)
    else:
        text_output(matches, profile)


# ---------------------------------------------------------------------------
# Built-in test cases (run with: python bond_product_matcher.py --test)
# ---------------------------------------------------------------------------


_TEST_CASES = [
    # Test 1: Classic SOE project-finance (should favour enterprise bond, MTN)
    ["--type", "SOE", "--rating", "AAA", "--industry", "utilities",
     "--asset-size", "500", "--revenue", "200", "--net-profit", "50",
     "--debt-ratio", "60", "--amount", "30", "--tenor", "7",
     "--purpose", "project"],

    # Test 2: Listed tech company refinancing (should favour MTN, public corp bond)
    ["--type", "listco", "--rating", "AA", "--industry", "tech",
     "--asset-size", "80", "--revenue", "40", "--net-profit", "8",
     "--debt-ratio", "55", "--amount", "10", "--tenor", "3",
     "--purpose", "refinance", "--listed"],

    # Test 3: LGFV with high leverage (should favour PPN, private corp bond)
    ["--type", "LGFV", "--rating", "AA-", "--industry", "real-estate",
     "--asset-size", "200", "--revenue", "60", "--net-profit", "3",
     "--debt-ratio", "82", "--amount", "15", "--tenor", "5",
     "--purpose", "general"],
]


def run_tests() -> None:
    """Exercise the matcher with built-in test profiles."""
    for i, argv in enumerate(_TEST_CASES, 1):
        print(f"\n{'='*78}")
        print(f"  TEST CASE {i}")
        print(f"{'='*78}")
        main(argv)
        print()


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        run_tests()
    else:
        main()