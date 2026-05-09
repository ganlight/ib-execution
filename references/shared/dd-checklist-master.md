# Master Due Diligence Checklist — All Products

> **Purpose:** Comprehensive DD checklist powering `scripts/dd_checklist_gen.py`. Generates structured checklists for IPO, Refinancing, and M&A.
> **Last Updated:** 2026-05

---

## Checklist Structure

```
DD-01: Legal — Corporate Existence & Governance
DD-02: Business — Commercial & Operational
DD-03: Financial — Accounting & Controls
DD-04: Legal — Assets & IP
DD-05: Legal — Compliance & Litigation
DD-06: IPO-Specific — Use of Proceeds (IPO only)
DD-07: M&A-Specific — Appraisal & Target (M&A only)
DD-BOND: Bond-Specific — delegate to bond-due-diligence skill
```

---

## DD-01: Legal — Corporate Existence & Governance

| ID | Item | Verification Focus | Data Source | Status |
|---|---|---|---|---|
| DD-01-001 | Business License (营业执照) | Validity period, registered scope | SAIC registration | ☐ |
| DD-01-002 | Articles of Association | Current version, amendment history | Company records | ☐ |
| DD-01-003 | Establishment approval documents | Legal establishment, state-asset approval (if SOE) | Government archives | ☐ |
| DD-01-004 | Capital contributions — verification | Full payment, no false capital contribution | Capital verification reports | ☐ |
| DD-01-005 | Shareholder register | Complete list, no nominee arrangements | Company register + SAIC | ☐ |
| DD-01-006 | Actual controller determination | Chain of control, no ultimate controller | Shareholder structure + Concert Party agreements | ☐ |
| DD-01-007 | Control stability (3 years) | No change in actual controller | Historical shareholder records | ☐ |
| DD-01-008 | Board resolutions — major decisions | Compliance with Articles, no ultra vires | Board meeting minutes | ☐ |
| DD-01-009 | Shareholder meeting resolutions | Proper notice, quorum, voting | Shareholder meeting minutes | ☐ |
| DD-01-010 | ESOP plan | Registration, compliance, pricing | ESOP documents + PRC registration | ☐ |
| DD-01-011 | VAM / Special rights | Full termination, no revival clauses | Investment agreements | ☐ |
| DD-01-012 | Subsidiaries register | Full ownership chain, consolidated entities | SAIC filings | ☐ |
| DD-01-013 | Foreign investment approvals (if applicable) | MOFCOM filing, FDI register | MOFCOM records | ☐ |
| DD-01-014 | Board committee structure | Audit, Nomination, Comp. committees exist | Board resolutions | ☐ |
| DD-01-015 | Independent directors | ≥1/3 of board, qualified | Appointment letters, CVs | ☐ |

---

## DD-02: Business — Commercial & Operational

| ID | Item | Verification Focus | Data Source | Status |
|---|---|---|---|---|
| DD-02-001 | Business scope vs. actual operations | Match, no unlicensed activities | License + contracts | ☐ |
| DD-02-002 | Revenue breakdown by product | 3-year trend, key product concentration | Financial system + contracts | ☐ |
| DD-02-003 | Revenue breakdown by region | Domestic vs. overseas, tax implications | Financial system | ☐ |
| DD-02-004 | Top 5 customers per year | Concentration risk, related-party? | Sales records | ☐ |
| DD-02-005 | Customer contracts — key accounts | Standard terms, no unusual clauses | Contract files | ☐ |
| DD-02-006 | Top 5 suppliers per year | Concentration risk, related-party? | Procurement records | ☐ |
| DD-02-007 | Supplier contracts — key vendors | Standard terms, pricing mechanisms | Contract files | ☐ |
| DD-02-008 | Sales model (direct/distributor/agent) | Channel inventory, returns policy | Sales policy documents | ☐ |
| DD-02-009 | Pricing policy | Consistency, discounting trends | Price lists + approvals | ☐ |
| DD-02-010 | Market share data | Source reliability, vintage | Industry reports | ☐ |
| DD-02-011 | Competitive landscape | Key competitors, differentiation | Management interviews | ☐ |
| DD-02-012 | Manufacturing/production capacity | Utilization rate, expansion plans | Production records | ☐ |
| DD-02-013 | Production permits/certification | All required permits held, validity | Permit files | ☐ |
| DD-02-014 | Environmental permits (环评) | All production sites covered, validity | EIA reports + permits | ☐ |
| DD-02-015 | Environmental compliance record | No violations, no pending penalties | EPB records | ☐ |
| DD-02-016 | Work safety compliance | No major accidents, safety permits current | Safety bureau records | ☐ |
| DD-02-017 | Quality certifications (ISO, etc.) | Validity, scope coverage | Certificates | ☐ |
| DD-02-018 | Key technology / know-how | Protection status, employee NDAs | IP register + contracts | ☐ |
| DD-02-019 | R&D team and expenditure | Number, qualifications, R&D spend trend | HR records + financials | ☐ |
| DD-02-020 | Overseas operations (if any) | Local compliance, FX controls | Overseas entity records | ☐ |

---

## DD-03: Financial — Accounting & Controls

| ID | Item | Verification Focus | Data Source | Status |
|---|---|---|---|---|
| DD-03-001 | Audit opinion — 3Y+CP | Unqualified opinion only | Audit reports | ☐ |
| DD-03-002 | Revenue recognition policy | Consistent, compliant with CAS | Accounting policy manual | ☐ |
| DD-03-003 | Revenue cutoff testing | Revenue recorded in correct period | Sales contracts + invoices | ☐ |
| DD-03-004 | Gross margin analysis — by product | Trends explained, no anomalies | Financial system | ☐ |
| DD-03-005 | Accounts receivable aging | Aging profile, concentration | AR sub-ledger | ☐ |
| DD-03-006 | Bad debt provision adequacy | Provision policy vs. aging vs. write-offs | Accounting estimates | ☐ |
| DD-03-007 | AR turnover days trend | 3-year trend, explain changes | Financial analysis | ☐ |
| DD-03-008 | Inventory aging + provision | Slow-moving, obsolete, NRV | Inventory sub-ledger | ☐ |
| DD-03-009 | Inventory turnover days trend | 3-year trend | Financial analysis | ☐ |
| DD-03-010 | Fixed asset register | Existence, ownership, depreciation | Asset register + physical verification | ☐ |
| DD-03-011 | Construction in progress (CIP) | % completion, no delayed capitalization | CIP schedule | ☐ |
| DD-03-012 | Intangible asset register | Validity, useful life, impairment test | IP register | ☐ |
| DD-03-013 | Goodwill — impairment test | Annual test performed, assumptions | Impairment test report | ☐ |
| DD-03-014 | Bank loans + credit facilities | Terms, covenants, cross-defaults | Loan agreements | ☐ |
| DD-03-015 | Guarantees provided (对外担保) | Counterparties, amounts, contingent liability | Board resolutions + contracts | ☐ |
| DD-03-016 | Related-party transactions list | Complete list, pricing fairness | Related-party register | ☐ |
| DD-03-017 | Related-party balances | AR/AP with related parties | Sub-ledger | ☐ |
| DD-03-018 | Tax filings — all taxes | Complete, no overdue, no penalties | Tax returns + receipts | ☐ |
| DD-03-019 | Tax holidays/incentives | Validity, compliance with conditions | Tax bureau approvals | ☐ |
| DD-03-020 | Government subsidies | Reliance %, compliance, not core profit | Subsidy documents | ☐ |
| DD-03-021 | Contingent liabilities | Pending litigation, guarantees, warranties | Legal opinion | ☐ |
| DD-03-022 | Post-period events | Material events between B/S date and DD date | Management inquiry | ☐ |
| DD-03-023 | Cash flow — operating quality | OCF / Net profit ratio, trend | Cash flow analysis | ☐ |
| DD-03-024 | Internal control — independent auditor opinion | Unqualified IC opinion (IPO) | IC audit report | ☐ |
| DD-03-025 | Financial ratios (full set) | Profitability, solvency, efficiency | Ratio analysis | ☐ |

---

## DD-04: Legal — Assets & IP

| ID | Item | Verification Focus | Data Source | Status |
|---|---|---|---|---|
| DD-04-001 | Land use rights | Full certificate chain, no disputes | Land certificates | ☐ |
| DD-04-002 | Real property — ownership | Building ownership certificates | Property certificates | ☐ |
| DD-04-003 | Leased property — validity | Lease terms, lessor title, registration | Lease agreements | ☐ |
| DD-04-004 | Invention patents | Registration, validity, no disputes | CNIPA records | ☐ |
| DD-04-005 | Utility model patents | Registration, validity | CNIPA records | ☐ |
| DD-04-006 | Trademarks | Registration class coverage, validity | CTMO records | ☐ |
| DD-04-007 | Software copyrights | Registration, ownership | CPCC records | ☐ |
| DD-04-008 | Domain names | Registration, ownership | WHOIS records | ☐ |
| DD-04-009 | IP licensing — in-license | Terms, royalty, termination risk | License agreements | ☐ |
| DD-04-010 | IP licensing — out-license | Licensees, terms, control | License agreements | ☐ |
| DD-04-011 | IP disputes | Pending litigation, claims, oppositions | Litigation search | ☐ |
| DD-04-012 | Employee IP assignments | All inventors assigned to company | Assignment agreements | ☐ |
| DD-04-013 | Non-compete / confidentiality | All key employees, valid | Employment contracts | ☐ |
| DD-04-014 | Production equipment — ownership | Title, no pledges (except disclosed) | Asset register + UCC search | ☐ |

---

## DD-05: Legal — Compliance & Litigation

| ID | Item | Verification Focus | Data Source | Status |
|---|---|---|---|---|
| DD-05-001 | Litigation search — company | All pending/closed cases, amounts | Court records, Credit China | ☐ |
| DD-05-002 | Litigation search — controlling shareholder | All material cases | Court records | ☐ |
| DD-05-003 | Litigation search — directors/executives | Civil/criminal, disqualification | Court + CSRC records | ☐ |
| DD-05-004 | Arbitration proceedings | All pending arbitrations | Arbitration commission records | ☐ |
| DD-05-005 | Administrative penalties | Environmental, tax, safety, etc. | Government bureau records | ☐ |
| DD-05-006 | Compliance certificates | Tax, social insurance, housing fund | Government certificates | ☐ |
| DD-05-007 | Social insurance contributions | Full payment, all employees | Social insurance bureau | ☐ |
| DD-05-008 | Housing fund contributions | Full payment, all employees | Housing fund center | ☐ |
| DD-05-009 | Labor compliance | Employment contracts, no mass disputes | HR records + labor bureau | ☐ |
| DD-05-010 | Anti-corruption / FCPA compliance | No bribery, no facilitation payments | Internal investigation | ☐ |
| DD-05-011 | Data privacy / cybersecurity | Personal data handling, cybersecurity review | IT policies + assessments | ☐ |
| DD-05-012 | Antitrust / competition compliance | No anti-competitive practices | Market analysis | ☐ |

---

## DD-06: IPO-Specific — Use of Proceeds

*(Added to standard checklist when product_type == "IPO")*

| ID | Item | Verification Focus | Data Source | Status |
|---|---|---|---|---|
| DD-06-001 | Project feasibility study | IRR, payback, reasonable assumptions | Feasibility report | ☐ |
| DD-06-002 | Project filing/approval (项目备案) | Filed with NDRC/MIIT | Filing certificate | ☐ |
| DD-06-003 | Environmental approval (环评批复) | EIA approved for each project | EIA approval letters | ☐ |
| DD-06-004 | Land use approval | Site secured or in process | Land pre-approval | ☐ |
| DD-06-005 | Working capital calculation | Detailed calc, ≤30% of total | Working capital model | ☐ |
| DD-06-006 | Project cost breakdown | Detailed capex per project | Budget documents | ☐ |
| DD-06-007 | Fund shortage — supplementary financing | Bridge financing plan if project > IPO raise | Financing plan | ☐ |
| DD-06-008 | Previous fundraising use compliance | If refinancing: prior use vs. plan | Prior-use report | ☐ |

---

## DD-07: M&A-Specific — Appraisal & Target

*(Added when product_type == "M&A")*

| ID | Item | Verification Focus | Data Source | Status |
|---|---|---|---|---|
| DD-07-001 | Appraisal report — DCF method | Assumptions reasonable, sensitivity | Appraisal report | ☐ |
| DD-07-002 | Appraisal report — Market method | Comparables properly selected | Appraisal report | ☐ |
| DD-07-003 | Appraisal report — Asset method | Asset adjustments reasonable | Appraisal report | ☐ |
| DD-07-004 | VAM commitment period | 3-year standard, no extension beyond 5 | VAM agreement | ☐ |
| DD-07-005 | VAM profit commitments | Attainable, not overly aggressive | Financial model | ☐ |
| DD-07-006 | VAM compensation capacity | Asset seller has capacity to compensate | Asset verification | ☐ |
| DD-07-007 | Target audit — 3 years | Unqualified opinion | Audit reports | ☐ |
| DD-07-008 | Target customer concentration | Post-merger integration risk | Sales analysis | ☐ |
| DD-07-009 | Target supplier concentration | Supply chain risk | Procurement analysis | ☐ |
| DD-07-010 | Target labor issues | Collective agreements, pending disputes | HR records | ☐ |
| DD-07-011 | Synergy quantification | Cost/revenue synergies, realistic | Synergy model | ☐ |
| DD-07-012 | Integration plan | Timeline, key milestones, risks | Integration plan document | ☐ |
| DD-07-013 | Tax-free reorganization eligibility | Conditions met, tax opinion obtained | Tax advisor opinion | ☐ |
| DD-07-014 | Appraisal report — independent financial advisor opinion | Fairness opinion issued | IFA opinion | ☐ |

---

## Product-Specific Checklist Variations

| Product | Base Checklist | Add | Notes |
|---|---|---|---|
| **IPO** | DD-01 through DD-05 | DD-06 (Use of Proceeds) | Financial audit must be 3Y+CP |
| **Refinancing** | DD-01 through DD-05 (lean) | Prior-use compliance | Lighter DD; focus on financial health + prior-raise compliance |
| **M&A** | DD-01 through DD-05 | DD-07 (Appraisal & Target) | Focus on target DD; extended by restructuring-specific DD |
| **Bond** | Delegate to bond-due-diligence skill | Bond-specific items | Different regulatory framework |

---

## Data Source Legend

| Source Code | Full Name |
|---|---|
| SAIC | State Administration for Industry & Commerce (市监局) |
| CNIPA | China National Intellectual Property Administration (国家知识产权局) |
| CTMO | China Trademark Office |
| CPCC | China Copyright Protection Center |
| NDRC | National Development and Reform Commission |
| MOFCOM | Ministry of Commerce |
| EPB | Environmental Protection Bureau |
| CSRC | China Securities Regulatory Commission |
| NAFMII | National Association of Financial Market Institutional Investors |