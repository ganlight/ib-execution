#!/usr/bin/env python3
"""
DD Checklist Generator — Generate comprehensive due diligence checklists.

Generates structured checklists across legal, financial, and business dimensions
for IPO, Refinancing, and M&A products. Output as CSV for Excel import.

Usage:
    python dd_checklist_gen.py --product IPO --board 科创板 --industry "生物医药"
    python dd_checklist_gen.py --product M&A --industry "半导体" -o checklist.csv
    python dd_checklist_gen.py --product IPO --board 主板 --json
"""

import argparse
import csv
import json
import sys
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Checklist database
# ---------------------------------------------------------------------------

DD_ITEMS: Dict[str, List[Tuple[str, str, str, str]]] = {
    "DD-01": [
        # (ID, Item, Verification Focus, Data Source)
        ("DD-01-001", "Business License (营业执照)", "Validity period, registered scope, unified social credit code", "SAIC registration (市监局)"),
        ("DD-01-002", "Articles of Association", "Current version, amendment history, compliance", "Company records"),
        ("DD-01-003", "Establishment approval documents", "Legal establishment, state-asset approval (if SOE)", "Government archives"),
        ("DD-01-004", "Capital contributions — verification", "Full payment, no false capital contribution, no withdrawal", "Capital verification reports (验资报告)"),
        ("DD-01-005", "Shareholder register", "Complete list, no nominee arrangements, no disputes", "Company register + SAIC filing"),
        ("DD-01-006", "Actual controller determination", "Chain of control, no ultimate controller ambiguity", "Shareholder structure + Concert Party agreements"),
        ("DD-01-007", "Control stability (3 years)", "No change in actual controller in past 3 years", "Historical shareholder records"),
        ("DD-01-008", "Board resolutions — major decisions", "Compliance with Articles, no ultra vires, proper quorum", "Board meeting minutes"),
        ("DD-01-009", "Shareholder meeting resolutions", "Proper notice, quorum, voting procedures", "Shareholder meeting minutes"),
        ("DD-01-010", "ESOP plan", "Registration, compliance with CSRC rules, pricing fairness", "ESOP documents + SAIC registration"),
        ("DD-01-011", "VAM / Special rights", "Full termination (not suspension), no revival clauses", "Investment agreements + termination letters"),
        ("DD-01-012", "Subsidiaries register", "Full ownership chain, consolidated entities, all licensed", "SAIC filings + company register"),
        ("DD-01-013", "Foreign investment approvals", "MOFCOM filing, FDI register compliance (if applicable)", "MOFCOM records"),
        ("DD-01-014", "Board committee structure", "Audit, Nomination, Comp., Strategy committees established", "Board resolutions + committee charters"),
        ("DD-01-015", "Independent directors", "≥1/3 of board, qualified, no disqualification events", "Appointment letters, CVs, independence declarations"),
    ],
    "DD-02": [
        ("DD-02-001", "Business scope vs. actual operations", "Match between license scope and actual business", "Business license + main contracts"),
        ("DD-02-002", "Revenue breakdown by product", "3-year trend, key product concentration risk", "Financial system + management accounts"),
        ("DD-02-003", "Revenue breakdown by region", "Domestic vs. overseas, export compliance", "Financial system + customs data"),
        ("DD-02-004", "Top 5 customers per year", "Concentration risk, related-party status check", "Sales records + contract files"),
        ("DD-02-005", "Customer contracts — key accounts", "Standard terms, no unusual clauses or side agreements", "Contract files (full set)"),
        ("DD-02-006", "Top 5 suppliers per year", "Concentration risk, related-party status, supply chain resilience", "Procurement records"),
        ("DD-02-007", "Supplier contracts — key vendors", "Standard terms, pricing mechanisms, force majeure", "Contract files (full set)"),
        ("DD-02-008", "Sales model", "Direct vs. distributor vs. agent; channel inventory", "Sales policy documents + management interviews"),
        ("DD-02-009", "Pricing policy", "Consistency, discounting trends, no transfer pricing", "Price lists + discount approval records"),
        ("DD-02-010", "Market share data", "Source reliability, data vintage, methodology", "Industry reports (Frost & Sullivan, CCID, etc.)"),
        ("DD-02-011", "Competitive landscape", "Key competitors, differentiation, barriers to entry", "Management interviews + competitor analysis"),
        ("DD-02-012", "Manufacturing capacity", "Utilization rate, expansion plans, bottlenecks", "Production records + capacity model"),
        ("DD-02-013", "Production permits", "All required permits held, validity, renewal schedule", "Permit files from relevant bureaus"),
        ("DD-02-014", "Environmental permits (环评)", "All production sites covered, validity, pending applications", "EIA reports (环境影响评价) + permits"),
        ("DD-02-015", "Environmental compliance record", "No violations, no pending penalties, no remediation orders", "EPB records + Credit China search"),
        ("DD-02-016", "Work safety compliance", "No major accidents in past 3 years, safety permits", "Safety bureau records + accident reports"),
        ("DD-02-017", "Quality certifications", "ISO 9001, industry-specific certs; validity + scope", "Certificate files + audit reports"),
        ("DD-02-018", "Core technology / know-how", "Protection status, employee NDAs, no misappropriation", "IP register + employment contracts + NDAs"),
        ("DD-02-019", "R&D team and expenditure", "Headcount, qualifications, R&D spend trend (must match audit)", "HR records + financial footnote"),
        ("DD-02-020", "Overseas operations", "Local compliance, FX controls, sanctions exposure", "Overseas entity records + local counsel"),
    ],
    "DD-03": [
        ("DD-03-001", "Audit opinion — 3Y+CP", "Unqualified opinion only; no emphasis of matter", "Audit reports (all years)"),
        ("DD-03-002", "Revenue recognition policy", "Consistent across periods, CAS 14 compliant", "Accounting policy manual + management inquiry"),
        ("DD-03-003", "Revenue cutoff testing", "Revenue recorded in correct period; no channel stuffing", "Sales contracts + invoices + shipping records"),
        ("DD-03-004", "Gross margin analysis", "By product line; trends explained; no anomalies", "Financial system + product costing"),
        ("DD-03-005", "Accounts receivable aging", "Aging profile; concentration by customer", "AR sub-ledger + customer confirmations"),
        ("DD-03-006", "Bad debt provision adequacy", "Policy vs. aging vs. actual write-offs; IFRS 9 / CAS 22", "Provision model + write-off history"),
        ("DD-03-007", "AR turnover days trend", "3-year trend; explain significant changes", "Calculated from financial data"),
        ("DD-03-008", "Inventory aging + provision", "Slow-moving, obsolete, NRV assessment", "Inventory sub-ledger + physical count"),
        ("DD-03-009", "Inventory turnover days trend", "3-year trend; explain changes", "Calculated from financial data"),
        ("DD-03-010", "Fixed asset register", "Existence, ownership, depreciation method & rates", "Asset register + physical verification"),
        ("DD-03-011", "Construction in progress (CIP)", "Completion %, no delayed capitalization, impairment", "CIP schedule + project records"),
        ("DD-03-012", "Intangible asset register", "Validity, useful life, impairment test (annual)", "IP register + impairment test reports"),
        ("DD-03-013", "Goodwill — impairment test", "Annual test, reasonable assumptions, no avoidance", "Impairment test reports + valuation models"),
        ("DD-03-014", "Bank loans + credit facilities", "Terms, interest rates, covenants, cross-defaults", "Loan agreements + bank confirmations"),
        ("DD-03-015", "Guarantees provided (对外担保)", "Counterparties, amounts, contingent liability, shareholder approval", "Board resolutions + guarantee contracts"),
        ("DD-03-016", "Related-party transactions list", "Complete register, pricing fairness, materiality", "RPT register + audit footnote"),
        ("DD-03-017", "Related-party AR/AP balances", "Balances, aging, collectability", "Sub-ledger + confirmation letters"),
        ("DD-03-018", "Tax filings — all taxes", "Complete and timely; no overdue amounts; no penalties", "Tax returns + receipts + clearance certificates"),
        ("DD-03-019", "Tax holidays/incentives", "Validity, compliance with conditions, reliance percentage", "Tax bureau approval documents"),
        ("DD-03-020", "Government subsidies", "Reliance % of profit, compliance with conditions, no clawback risk", "Subsidy documents + grant agreements"),
        ("DD-03-021", "Contingent liabilities", "Pending litigation, guarantees, warranties", "Legal opinion + management representation letter"),
        ("DD-03-022", "Post-period events", "Material events between B/S date and DD/signing date", "Management inquiry + subsequent event log"),
        ("DD-03-023", "Cash flow — operating quality", "OCF / Net Profit ratio; free cash flow trend", "Cash flow analysis"),
        ("DD-03-024", "Internal control — auditor opinion", "Unqualified IC opinion (required for IPO)", "IC audit report (内控鉴证报告)"),
        ("DD-03-025", "Financial ratios — full set", "Profitability, solvency, liquidity, efficiency", "Ratio analysis from financials"),
    ],
    "DD-04": [
        ("DD-04-001", "Land use rights", "Full certificate chain, no disputes, no pledges", "Land use right certificates (国有土地使用证)"),
        ("DD-04-002", "Real property — ownership", "Building ownership certificates, no disputes", "Property ownership certificates (房屋所有权证)"),
        ("DD-04-003", "Leased property", "Lease terms, lessor title, lease registration", "Lease agreements + lessor title documents"),
        ("DD-04-004", "Invention patents", "Registration, validity, ownership, no disputes", "CNIPA records (国家知识产权局)"),
        ("DD-04-005", "Utility model patents", "Registration, validity, ownership", "CNIPA records"),
        ("DD-04-006", "Trademarks", "Registration class coverage, validity, no disputes", "CTMO records (商标局)"),
        ("DD-04-007", "Software copyrights", "Registration, ownership, developer assignments", "CPCC records (版权保护中心)"),
        ("DD-04-008", "Domain names", "Registration, ownership, expiry dates", "WHOIS records + registrar account"),
        ("DD-04-009", "IP licensing — in-license", "Terms, royalty, termination risk, exclusivity", "Inbound license agreements"),
        ("DD-04-010", "IP licensing — out-license", "Licensees, terms, territory restrictions, royalties", "Outbound license agreements"),
        ("DD-04-011", "IP disputes", "Pending litigation, claims, oppositions, invalidation", "Litigation search + CNIPA records"),
        ("DD-04-012", "Employee IP assignments", "All inventors assigned IP to company", "Assignment agreements + employment contracts"),
        ("DD-04-013", "Non-compete / confidentiality", "All key employees under NDA + non-compete", "Employment contracts + NDA register"),
        ("DD-04-014", "Production equipment", "Title, no pledges (except disclosed), condition", "Asset register + UCC/pledge search"),
    ],
    "DD-05": [
        ("DD-05-001", "Litigation — company", "All pending/closed cases, amounts, outcomes", "Court records + Credit China + Judgement database"),
        ("DD-05-002", "Litigation — controlling shareholder", "All material cases affecting control or key assets", "Court records + disclosure"),
        ("DD-05-003", "Litigation — directors/executives", "Civil, criminal, disqualification events", "Court records + CSRC disciplinary database"),
        ("DD-05-004", "Arbitration proceedings", "All pending arbitrations, tribunals, amounts", "Arbitration commission records"),
        ("DD-05-005", "Administrative penalties", "Environmental, tax, safety, industry regulation penalties", "Government bureau records + Credit China"),
        ("DD-05-006", "Compliance certificates", "Tax, social insurance, housing fund, customs", "Government compliance certificates (合规证明)"),
        ("DD-05-007", "Social insurance contributions", "Full payment, all employees, correct base amounts", "Social insurance bureau records"),
        ("DD-05-008", "Housing fund contributions", "Full payment, all employees, correct base amounts", "Housing fund center records"),
        ("DD-05-009", "Labor compliance", "Employment contracts for all, no mass disputes", "HR records + labor bureau + labor arbitration"),
        ("DD-05-010", "Anti-corruption / FCPA", "No bribery, facilitation payments, kickbacks", "Internal investigation + whistleblower reports"),
        ("DD-05-011", "Data privacy / cybersecurity", "Personal data handling, cybersecurity review (if >1M users)", "IT policies + data mapping + security audits"),
        ("DD-05-012", "Antitrust / competition", "No anti-competitive practices, no monopoly abuse", "Market analysis + competition authority records"),
    ],
    "DD-06": [
        ("DD-06-001", "Project feasibility study", "IRR, payback period, assumptions reasonable", "Feasibility study reports (可研报告)"),
        ("DD-06-002", "Project filing/approval (项目备案)", "Filed with NDRC/MIIT; valid; match with use-of-proceeds", "Filing certificates (项目备案证)"),
        ("DD-06-003", "Environmental approval (环评批复)", "EIA approved for each use-of-proceeds project", "EIA approval letters (环评批复)"),
        ("DD-06-004", "Land use approval", "Site secured or formal pre-approval obtained", "Land pre-approval / land grant contract"),
        ("DD-06-005", "Working capital calculation", "Detailed working-capital model; ≤30% of total raise", "Working capital model + financial analysis"),
        ("DD-06-006", "Project cost breakdown", "Detailed capex per project; reasonable contingencies", "Project budget / cost estimate documents"),
        ("DD-06-007", "Supplementary financing plan", "Bridge financing plan if project cost > IPO raise", "Financing plan / commitment letters"),
        ("DD-06-008", "Previous fundraising use compliance", "If refinancing: actual use vs. approved plan", "Prior-use report (前次募集资金使用情况报告)"),
    ],
    "DD-07": [
        ("DD-07-001", "Appraisal — DCF method", "Assumptions reasonable, sensitivity analysis included", "Appraisal report (评估报告)"),
        ("DD-07-002", "Appraisal — Market method", "Comparables properly selected; premiums justified", "Appraisal report"),
        ("DD-07-003", "Appraisal — Asset method", "Asset adjustments reasonable; impairment considered", "Appraisal report"),
        ("DD-07-004", "VAM commitment period", "3-year standard; no extension beyond 5 years", "VAM agreement (盈利预测补偿协议)"),
        ("DD-07-005", "VAM profit commitments", "Attainable; not overly aggressive vs. historical", "Financial model + VAM agreement"),
        ("DD-07-006", "VAM compensation capacity", "Asset seller has capacity to compensate if shortfall", "Asset verification of seller"),
        ("DD-07-007", "Target audit — 3 years", "Unqualified audit opinion for target", "Target audit reports"),
        ("DD-07-008", "Target customer concentration", "Post-merger customer retention risk", "Target sales analysis + customer interviews"),
        ("DD-07-009", "Target supplier concentration", "Supply chain disruption risk", "Target procurement analysis"),
        ("DD-07-010", "Target labor issues", "Collective agreements, pending disputes, pension liabilities", "Target HR records"),
        ("DD-07-011", "Synergy quantification", "Cost and revenue synergies; realistic timeline", "Synergy model document"),
        ("DD-07-012", "Integration plan", "Timeline, key milestones, responsible parties, risks", "Integration plan document"),
        ("DD-07-013", "Tax-free reorganization eligibility", "Conditions for special tax treatment under Caishui [2009] No. 59", "Tax advisor opinion"),
        ("DD-07-014", "IFA fairness opinion", "Independent financial advisor opinion on pricing fairness", "IFA opinion (独立财务顾问报告)"),
    ],
}


# ---------------------------------------------------------------------------
# Product-specific configuration
# ---------------------------------------------------------------------------

PRODUCT_SECTIONS: Dict[str, List[str]] = {
    "IPO": ["DD-01", "DD-02", "DD-03", "DD-04", "DD-05", "DD-06"],
    "Refinancing": ["DD-01", "DD-02", "DD-03", "DD-05"],
    "M&A": ["DD-01", "DD-02", "DD-03", "DD-04", "DD-05", "DD-07"],
}

SECTION_LABELS: Dict[str, str] = {
    "DD-01": "Legal — Corporate Existence & Governance",
    "DD-02": "Business — Commercial & Operational",
    "DD-03": "Financial — Accounting & Controls",
    "DD-04": "Legal — Assets & IP",
    "DD-05": "Legal — Compliance & Litigation",
    "DD-06": "IPO-Specific — Use of Proceeds",
    "DD-07": "M&A-Specific — Appraisal & Target DD",
}


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def generate_checklist(product: str, board: str = "", industry: str = "") -> List[Dict[str, str]]:
    """Generate checklist rows for the specified product."""
    sections = PRODUCT_SECTIONS.get(product, ["DD-01", "DD-02", "DD-03", "DD-05"])
    rows: List[Dict[str, str]] = []

    # Product header row
    board_str = f" ({board})" if board else ""
    industry_str = f" — {industry}" if industry else ""
    rows.append({
        "Section": f"# {product} DD Checklist{board_str}{industry_str}",
        "ID": "",
        "Item": "",
        "Verification Focus": "",
        "Data Source": "",
        "Status": "",
    })

    for section_id in sections:
        items = DD_ITEMS.get(section_id, [])
        if not items:
            continue

        # Section header
        rows.append({
            "Section": f"## {section_id}: {SECTION_LABELS.get(section_id, section_id)}",
            "ID": "",
            "Item": "",
            "Verification Focus": "",
            "Data Source": "",
            "Status": "",
        })

        for item_id, item, focus, source in items:
            rows.append({
                "Section": section_id,
                "ID": item_id,
                "Item": item,
                "Verification Focus": focus,
                "Data Source": source,
                "Status": "☐ Pending",
            })

    return rows


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_csv(rows: List[Dict[str, str]], path: str) -> None:
    """Write checklist to CSV."""
    fieldnames = ["Section", "ID", "Item", "Verification Focus", "Data Source", "Status"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_checklist_text(rows: List[Dict[str, str]]) -> str:
    """Format checklist as readable text."""
    lines = []
    for row in rows:
        section = row["Section"]
        item_id = row["ID"]
        item = row["Item"]
        focus = row["Verification Focus"]

        if section.startswith("#"):
            lines.append(section.lstrip("# "))
            lines.append("=" * len(section.lstrip("# ")))
        elif section.startswith("##"):
            lines.append(f"\n{section}")
            print(section)
        elif item_id:
            lines.append(f"  [{item_id}] {item}")
            lines.append(f"       Focus: {focus}")
            lines.append(f"       Source: {row['Data Source']}")
            lines.append(f"       Status: ☐")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive IB due diligence checklists.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --product IPO --board 科创板 --industry "新一代信息技术"
  %(prog)s --product M&A --industry "半导体" -o checklist.csv
  %(prog)s --product IPO --board 主板 --json
  %(prog)s --product Refinancing
        """,
    )

    parser.add_argument("--product", required=True,
                        choices=["IPO", "Refinancing", "M&A"],
                        help="Product type")
    parser.add_argument("--board", default="",
                        choices=["", "主板", "科创板", "创业板", "北交所"],
                        help="Target board (for IPO)")
    parser.add_argument("--industry", default="",
                        help="Company industry classification")
    parser.add_argument("--output", "-o", default=None,
                        help="Output CSV file path")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")

    args = parser.parse_args()

    # Generate checklist
    rows = generate_checklist(args.product, args.board, args.industry)

    # Count items
    item_count = sum(1 for r in rows if r["ID"])

    # Output
    if args.json:
        checklist_items = [r for r in rows if r["ID"]]
        output = {
            "product": args.product,
            "board": args.board or None,
            "industry": args.industry or None,
            "total_items": item_count,
            "items": [
                {
                    "section": r["Section"],
                    "id": r["ID"],
                    "item": r["Item"],
                    "verification_focus": r["Verification Focus"],
                    "data_source": r["Data Source"],
                    "status": "pending",
                }
                for r in checklist_items
            ],
        }
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"JSON checklist ({item_count} items) written to {args.output}")
        else:
            print(json_str)

    elif args.output and args.output.endswith(".csv"):
        write_csv(rows, args.output)
        print(f"CSV checklist ({item_count} items) written to {args.output}")

    else:
        print(format_checklist_text(rows))
        print(f"\nTotal: {item_count} DD items")

    if args.board:
        sections = PRODUCT_SECTIONS.get(args.product, [])
        section_count = len(sections)
        print(f"\nSections included: {', '.join(sections)}")
        if args.product == "IPO":
            print("  DD-01 through DD-05 (core) + DD-06 (Use of Proceeds)")
        elif args.product == "M&A":
            print("  DD-01 through DD-05 (core) + DD-07 (Appraisal & Target)")
        elif args.product == "Refinancing":
            print("  DD-01 through DD-03 + DD-05 (lean checklist)")


if __name__ == "__main__":
    main()