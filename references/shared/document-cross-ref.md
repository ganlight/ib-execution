# Document Cross-Reference Map — Data Lineage & Consistency Requirements

> **Purpose:** Powers `scripts/cross_ref_check.py` — maps which data points originate where and MUST match across which downstream documents.
> **Last Updated:** 2026-05

---

## 1. Data Dependency Overview

```
                     ┌─────────────────────────┐
                     │     AUDIT REPORT         │
                     │   (审计报告 + 附注)       │
                     └───────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   PROSPECTUS    │   │ LEGAL OPINION   │   │ IC AUDIT REPORT │
│  (招股说明书)    │   │  (法律意见书)    │   │  (内控审计报告)  │
└────────┬────────┘   └────────┬────────┘   └─────────────────┘
         │                     │
         │     ┌───────────────┘
         │     │
         ▼     ▼
┌─────────────────┐
│ RESTRUCTURING   │
│ REPORT (重组报告)│──Only for M&A
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ APPRAISAL REPORT│──Only for M&A
│   (评估报告)     │
└─────────────────┘
```

---

## 2. Audit Report → Prospectus Cross-Reference Matrix

| # | Data Point | Audit Report Source | Prospectus Section | Must Match Item |
|---|---|---|---|---|
| A1 | Net assets (期末净资产) | Balance Sheet | §2 Overview, §11 Financial Summary | Exact match |
| A2 | Total assets | Balance Sheet | §11 Financial Summary | Exact match |
| A3 | Revenue (营业收入) | Income Statement | §2 Overview, §5 Business (product breakdown), §11 MD&A | Revenue total = sum of product/region breakdowns |
| A4 | Net profit (净利润) | Income Statement | §2 Overview, §11 MD&A | Exact match |
| A5 | Net profit (扣非) | Income Statement footnote | §2, §11 Non-recurring items | Exact match |
| A6 | Operating cash flow | Cash Flow Statement | §2, §11 Cash flow analysis | Exact match |
| A7 | Gross margin by product | Footnote — segment reporting | §5 Business, §11 MD&A | Product margins match across §5 and §11 |
| A8 | R&D expenditure | Footnote — R&D | §5 R&D section, §4 (innovation attributes) | Exact match |
| A9 | Related-party revenue | Footnote — RPTs | §5 Business (customer analysis) | Amounts per counterparty match |
| A10 | Related-party purchases | Footnote — RPTs | §5 Business (supplier analysis) | Amounts per counterparty match |
| A11 | Related-party AR/AP balances | Footnote — RPTs | §11 Balance sheet analysis | Exact match |
| A12 | Management compensation | Footnote — RPT or Compensation | §6 Remuneration | Total compensation = §6 sum |
| A13 | Tax rates & holidays | Footnote — Income tax | §4 Profile, §5 Business | Tax rate consistency |
| A14 | Government subsidies | Footnote — Other income | §11 Non-recurring items | Exact match |
| A15 | Goodwill | Balance Sheet + Footnote | §5 Acquisitions history | Amount → business narrative |
| A16 | PP&E + CIP | Balance Sheet + Footnote | §8 Use of Proceeds (future capex compatibility) | Future capex ≤ reasonable PP&E growth |
| A17 | Guarantees | Footnote — Contingencies | §3 Risk factors, §11 Contingent liabilities | Amounts match |
| A18 | Capital changes (实收资本) | Footnote — Equity | §4 Historical capital changes | Chronology + amounts match |
| A19 | Dividend history | Footnote — Equity | §9 Dividend policy | Dividend amounts match |
| A20 | Earnings per share | Income Statement footnote | §2 Overview | EPS exact match |
| A21 | Financial ratios | Calculated from FS | §11 Financial ratios | All ratios consistent with FS |

---

## 3. Legal Opinion → Prospectus Cross-Reference Matrix

| # | Data Point | Legal Opinion Source | Prospectus Section | Must Match Item |
|---|---|---|---|---|
| L1 | Issuer legal name & address | §1 Basic info | §1 Cover, §4 Profile | Exact match |
| L2 | Registered capital & paid-in | §1 | §4 Profile | Exact match |
| L3 | Shareholder structure | §1 Shareholders | §4 Shareholders | Names + % exact match |
| L4 | Actual controller | §1 | §4 Actual controller | Same person/entity |
| L5 | Litigation (pending, amounts) | §9 Litigation | §3 Risk factors, §11 Contingent liabilities | Case names + amounts match |
| L6 | Patents (invention + utility + design) | §5 IP | §5 Technology | Count + registration numbers match |
| L7 | Trademarks | §5 IP | §5 Technology | Match |
| L8 | Land use rights | §6 Major assets | §4 Profile, §11 Footnote | Land certificate numbers match |
| L9 | Real property | §6 | §4 Profile, §11 Footnote | Certificate numbers match |
| L10 | Environmental compliance | §7 Compliance | §5 Environment | Penalty info consistent |
| L11 | Labor/social insurance | §7 | §3 Risk factors | Contribution compliance consistent |
| L12 | Board and management | §8 | §6 | Names, roles exact match |
| L13 | Related-party legal definition | §10 RPT | §4, §5, §11 | Same definition scope = same RPT list |
| L14 | VAM / special rights termination | §10 | §4 | Termination confirmation |
| L15 | Non-compete undertaking | §10 | §4 | Existence confirmed |

---

## 4. Legal Opinion → Audit Report Consistency Check

| # | Cross-Check | Legal Opinion | Audit Report |
|---|---|---|---|
| LX1 | Registered capital timeline | §1 Capital contribution history | Footnote — Equity |
| LX2 | Subsidiaries list | §3 Subsidiaries | Footnote — Consolidation scope |
| LX3 | Litigation provisions | §9 Amounts | Footnote — Provisions |
| LX4 | Guarantee amounts | §10 Guarantees | Footnote — Contingent liabilities |
| LX5 | RPT counterparty list | §10 Related parties | Footnote — RPTs |

---

## 5. Appraisal Report → Restructuring Report Cross-Reference (M&A only)

| # | Data Point | Appraisal Report Source | Restructuring Report Section | Must Match |
|---|---|---|---|---|
| AP1 | Valuation result (total equity) | Summary | §Valuation | Exact match |
| AP2 | DCF key assumptions | DCF methodology | §Valuation methodology | WACC, g, projection years identical |
| AP3 | Comparable companies list | Market approach | §Valuation methodology | Same list |
| AP4 | Asset-based result | Asset approach | §Valuation cross-check | Exact match |

---

## 6. Cross-Reference Check Logic (for cross_ref_check.py)

### Check Definitions
```python
CROSS_REF_CHECKS = [
    {
        "id": "NET_ASSETS",
        "label": "Net Assets (净资产)",
        "sources": ["audit_report.balance_sheet.net_assets",
                     "prospectus.section_2.net_assets",
                     "prospectus.section_11.net_assets"],
        "tolerance": 0,  # exact
        "unit": "CNY"
    },
    {
        "id": "NET_PROFIT",
        "label": "Net Profit (净利润)",
        "sources": ["audit_report.income_statement.net_profit",
                     "prospectus.section_2.net_profit",
                     "prospectus.section_11.net_profit"],
        "tolerance": 0,
        "unit": "CNY"
    },
    {
        "id": "REVENUE",
        "label": "Revenue (营业收入)",
        "sources": ["audit_report.income_statement.revenue",
                     "prospectus.section_2.revenue",
                     "prospectus.section_5.revenue_breakdown_sum",
                     "prospectus.section_11.revenue"],
        "tolerance": 0.01,  # 1% for rounding in product breakdown
        "unit": "CNY"
    },
    {
        "id": "RD_EXPENDITURE",
        "label": "R&D Expenditure (研发费用)",
        "sources": ["audit_report.footnote.rd_expense",
                     "prospectus.section_5.rd_expenditure",
                     "prospectus.section_4.rd_percentage"],
        "tolerance": 0,
        "unit": "CNY"
    },
    {
        "id": "RELATED_PARTY_REVENUE",
        "label": "Related Party Revenue",
        "sources": ["audit_report.footnote.rpt_revenue",
                     "prospectus.section_5.rpt_revenue",
                     "prospectus.section_11.rpt_revenue"],
        "tolerance": 0,
        "unit": "CNY"
    },
    {
        "id": "GUARANTEES",
        "label": "Guarantee Amounts",
        "sources": ["audit_report.footnote.guarantees",
                     "legal_opinion.section_10.guarantees",
                     "prospectus.section_11.guarantees"],
        "tolerance": 0,
        "unit": "CNY"
    },
    {
        "id": "LITIGATION_AMOUNTS",
        "label": "Litigation Amounts",
        "sources": ["legal_opinion.section_9.litigation_amount",
                     "prospectus.section_11.litigation_provisions"],
        "tolerance": 0,
        "unit": "CNY"
    },
    {
        "id": "INVESTMENT_AMOUNTS",
        "label": "Use-of-Proceeds Project Amounts",
        "sources": ["prospectus.section_8.total_fundraise",
                     "prospectus.section_8.sum_of_project_costs"],
        "tolerance": 0,
        "unit": "CNY"
    },
    {
        "id": "GOODWILL",
        "label": "Goodwill",
        "sources": ["audit_report.balance_sheet.goodwill",
                     "prospectus.section_5.goodwill_narrative"],
        "tolerance": 0,
        "unit": "CNY"
    },
    {
        "id": "CAPITAL_CHANGES",
        "label": "Capital / Registered Capital",
        "sources": ["audit_report.footnote.equity.paid_in_capital",
                     "prospectus.section_4.registered_capital",
                     "legal_opinion.section_1.registered_capital"],
        "tolerance": 0,
        "unit": "CNY"
    }
]
```

---

## 7. Document Data Extraction Guidance

For automated cross-referencing, each document should have structured data extractable via JSON:

### Audit Report JSON Structure (extract from TB/working papers)
```json
{
  "balance_sheet": {
    "total_assets": float,
    "net_assets": float,
    "goodwill": float,
    "period": "YYYY-MM-DD"
  },
  "income_statement": {
    "revenue": {"amount": float, "period": "YYYY"},
    "net_profit": {"amount": float, "period": "YYYY"},
    "net_profit_recurring": {"amount": float, "period": "YYYY"}
  },
  "footnote": {
    "rd_expense": float,
    "rpt_revenue": {"counterparty": str, "amount": float}[],
    "rpt_purchases": {"counterparty": str, "amount": float}[],
    "guarantees": {"beneficiary": str, "amount": float}[],
    "equity": {"paid_in_capital": float}
  }
}
```

### Legal Opinion JSON Structure
```json
{
  "section_1": {
    "issuer_name": str,
    "registered_capital": float
  },
  "section_5": {
    "patents": {"invention": int, "utility": int, "design": int}[],
    "trademarks": int
  },
  "section_9": {
    "litigation_amount": float,
    "litigation_cases": {"case_name": str, "amount": float}[]
  },
  "section_10": {
    "guarantees": {"beneficiary": str, "amount": float}[],
    "related_parties": str[]
  }
}
```

---

## 8. Common Inconsistency Patterns

| Pattern | Example | Root Cause |
|---|---|---|
| Typo/rounding | Revenue §2 = 1,560M vs §11 = 1,558M | Rounding in executive summary |
| Breakdown mismatch | Revenue §5 product sum = 1,500M vs Audit = 1,550M | Missing product category in business section |
| RPT incomplete | Audit RPT list has 8 parties, §4 lists 6 | Lawyer used different RPT definition |
| Data staleness | §5 market data is 2019, Audit is 2023 | Business chapter not updated |
| VAM discrepancy | §4 says "terminated", legal opinion says "suspended" | Different interpretation of PE agreement |
| Personnel count | §5 R&D = 85 people, HR = 78 | Different cutoff date |
| Capital history | §4 shows 5 capital increases, Audit footnote shows 4 | Missing one capital increase in financial footnote |