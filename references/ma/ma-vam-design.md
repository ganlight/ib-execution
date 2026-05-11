# VAM Design (对赌协议设计) — Comprehensive Reference

> **Purpose:** Reference for Value Adjustment Mechanism (VAM) design, compensation structures, legal enforceability, accounting treatment, and tax implications in M&A transactions.
> **Last Updated:** 2026-05

---

## 1. VAM Overview

A Value Adjustment Mechanism (VAM, 对赌协议) is a contingent consideration arrangement whereby the buyer and seller agree on future performance targets; if the target is not met, the seller compensates the buyer (or vice versa if exceeded). VAMs bridge valuation gaps in M&A by linking final consideration to actual post-closing performance.

| Dimension | Description |
|---|---|
| **Legal Basis** | Contract law principles; no standalone VAM statute — enforced under PRC Civil Code & Supreme People's Court (SPC) interpretations |
| **Primary Users** | PE/VC investments, listed company M&A, SOE acquisitions |
| **Typical Duration** | 3–5 years post-closing |
| **Key Function** | Price adjustment; risk allocation; incentive alignment; signaling mechanism |
| **Market Prevalence** | >70% of A-share M&A deals incorporate some form of VAM (2019–2025) |

---

## 2. Performance Target Types (业绩对赌类型)

### 2.1 Net Profit VAM (净利润对赌)

**Most common type in Chinese M&A practice.**

| Parameter | Typical Structure |
|---|---|
| **Indicator** | Deducted non-recurring P&L net profit attributable to parent (扣非归母净利润) |
| **Benchmark** | 15%–30% CAGR over 3 years vs. pre-deal audited baseline |
| **Measurement Period** | 3 consecutive fiscal years post-closing |
| **Cumulative vs. Annual** | Typically cumulative with annual floors; e.g., total 3-year ≥ RMB 150M with each year ≥ RMB 40M |
| **Adjustments** | May exclude: extraordinary items, new business investment losses, acquisition-related amortization |

**Formula Example:**
```
Cumulative Actual NP ≥ Cumulative Committed NP × 90%  → No compensation
Cumulative Actual NP < Cumulative Committed NP × 90%  → Trigger compensation
Compensation = (1 − Actual/Cumulative Committed) × Total Consideration × Cap%
```

### 2.2 Revenue VAM (营业收入对赌)

**Used when profitability metric is unreliable (e.g., rapid expansion phase).**

| Parameter | Typical Structure |
|---|---|
| **Indicator** | Audited operating revenue (主营业务收入) |
| **Benchmark** | 20%–40% CAGR |
| **Caveat** | Often combined with gross margin floor (e.g., GM ≥ 25%) to prevent revenue-buying |
| **Measurement** | Annual + cumulative; usually 3-year period |
| **Suitable For** | SaaS/Internet, biotech (pre-revenue), consumer brands in expansion phase |

**Risk Mitigation:**
- Revenue recognition policy clause (must follow PRC GAAP / CAS 14)
- Customer concentration cap
- Related-party revenue exclusion

### 2.3 Quantitative Operational Metric VAM (量化经营指标对赌)

**Customized KPIs beyond P&L; growing in popularity for asset-light / platform businesses.**

| Metric Category | Examples | Typical Threshold |
|---|---|---|
| **User Metrics** | MAU, DAU, paying users | ≥ target × 90% |
| **Operational KPIs** | Gross billing volume (GMV), contract value, order volume | ≥ target × 85% |
| **Technical Milestones** | Patent filings (quantity + quality), clinical trial phases, regulatory approvals | Binary pass/fail |
| **Market Position** | Market share ranking, customer retention rate | Maintain top-3 or ≥ 80% retention |
| **R&D Pipeline** | IND filings, Phase completion, NDA submission | Milestone-based |

**Key Drafting Considerations:**
- Metric definition must be unambiguous (e.g., "active user" = logged-in + performed transaction within 30 days)
- Data source: auditable third-party platform or Big Four-verified internal systems
- Dispute resolution: third-party technical expert binding determination

---

## 3. Compensation Mechanisms (补偿方式)

### 3.1 Cash Compensation (现金补偿)

**Structure:**
```
Compensation Amount = (1 − Actual Performance / Committed Performance) × Transaction Consideration × Adjustment Factor
```

| Parameter | Market Standard |
|---|---|
| **Adjustment Factor** | 0.8–1.2×; commonly 1.0× |
| **Cap** | Typically 30%–50% of total consideration |
| **Payment Timing** | Within 30–90 days after audit report issuance |
| **Escrow** | 10%–20% of consideration held in escrow for VAM period |
| **Late Payment Penalty** | Daily penalty of 0.05% of unpaid amount |

**Pros:**
- Simple calculation, low dispute risk
- Immediate liquidity for acquirer
- No shareholder dilution concerns

**Cons:**
- Cash availability risk for seller (often individual founders)
- No upside participation for seller if targets exceeded
- May incentivize short-term behavior at expense of long-term value

### 3.2 Share-Based Compensation (股份补偿)

**Structure:**
```
Shares to Return = (1 − Actual / Committed) × Shares Issued × Share Adjustment Ratio
```

| Parameter | Market Standard |
|---|---|
| **Return Mechanism** | 1) Acquirer repurchases at RMB 1.00/share (total price cancellation); 2) Free transfer of shares to acquirer-designated entity |
| **Share Adjustment Ratio** | 0.5–1.0×; higher for founder-led deals |
| **Cap** | Up to 100% of issued shares (maximum consideration clawback) |
| **Lock-up Extension** | Remaining shares locked for additional 12–24 months |
| **Voting Rights** | VAM shares typically carry restricted voting rights during VAM period |

**Pros:**
- Strong alignment — seller shares acquirer downside risk
- No immediate cash burden on seller
- More effective deterrent against over-optimistic projections
- CSRC-preferred structure for major asset restructurings

**Cons:**
- Complex calculation and execution
- Share dilution recovery may be delayed
- Acquired entity must maintain independent legal status (cannot use in absorption mergers)

### 3.3 Hybrid Compensation (混合补偿)

| Structure | Cash First + Share Backup |
|---|---|
| **Tier 1 (≤20% shortfall)** | Cash compensation at 1.0× shortfall |
| **Tier 2 (20%–50% shortfall)** | Share compensation at 1.0× shortfall |
| **Tier 3 (>50% shortfall)** | Maximum clause — acquirer right to rescind deal or claw back 100% consideration |

### 3.4 Reverse VAM (反向对赌 / 超额奖励)

**Trigger:** Actual performance exceeds committed targets by ≥10%–20%.

| Reward Type | Typical Structure |
|---|---|
| **Cash Bonus** | 20%–50% of excess profit paid to seller/management team |
| **Additional Shares** | Acquirer issues bonus shares (3%–5% of original issuance) |
| **Management Incentive Pool** | 10%–30% of excess allocated to key management retention fund |
| **Earn-Out Extension** | Extended performance period with higher targets |

---

## 4. Adjustment Mechanisms (调整机制)

### 4.1 Directional Adjustment Types

| Type | Mechanism | Use Case |
|---|---|---|
| **Unidirectional Downward (单向向下)** | Seller compensates buyer for underperformance; no upside reward | Most common; buyer-friendly |
| **Unidirectional Upward (单向向上)** | Buyer rewards seller for outperformance; no penalty for underperformance | Rare; earn-out in friendly deals |
| **Bidirectional (双向调整)** | Underperformance → compensation; outperformance → reward | Balanced deals; management buy-ins |
| **Bidirectional with Asymmetric Cap** | Downside: 50% clawback cap; Upside: 20% bonus cap | Common in PE/VC with strong management |

### 4.2 Trigger Conditions

| Trigger | Threshold | Grace Period |
|---|---|---|
| **Annual Shortfall** | Actual < 80%–95% of annual committed | None — triggers on audit issuance |
| **Cumulative Shortfall** | 3-year cumulative < 90%–100% of total committed | Final year only |
| **Material Adverse Change (MAC)** | 30%+ revenue decline; key license revocation; major litigation loss >RMB 50M | 10 business day cure period |
| **Financial Fraud** | Material misstatement in audited financials | Immediate trigger; full clawback |
| **Change of Control** | Unauthorized transfer of ≥30% equity by founder | Immediate trigger |
| **Non-Competition Breach** | Founder starts competing business | 30%–100% clawback |

### 4.3 Adjustment Formula Variations

**Standard Linear Model:**
```
Compensation = (Committed − Actual) / Committed × Consideration
```

**Non-Linear / Graduated Model:**
| Shortfall Band | Compensation Rate |
|---|---|
| 0%–10% | 0.5× shortfall |
| 10%–20% | 0.8× shortfall |
| 20%–30% | 1.0× shortfall |
| 30%–50% | 1.2× shortfall |
| >50% | Full clawback + penalty interest |

**Independently Reviewed Adjustments:**
- EBITDA-to-NP reconciliation for non-operating items
- Fair value adjustments (PPA — purchase price allocation effects)
- Intercompany transaction adjustments
- Tax rate normalization

---

## 5. Judicial Practice & Enforceability (司法实践)

### 5.1 SPC Guiding Framework

The Supreme People's Court's position evolved through key milestones:

| Period | Judicial Attitude | Key Authority |
|---|---|---|
| **Pre-2012** | Largely unenforceable — VAM viewed as gambling | Hai Fu Case (海富案), SPC (2012) Min Ti Zi No.38 |
| **2012–2019** | VAM between PE and founders enforceable; VAM with target company itself problematic | Hai Fu established the "founder-VAM valid; target-VAM invalid" dichotomy |
| **2019–Present** | Pro-enforceability era; VAM with target company enforceable if legally compliant | SPC Minutes of National Court Civil and Commercial Trial Work Conference (九民纪要, 2019) |
| **2024–Present** | New Company Law revisions; clarified capital reduction & dividend distribution procedures |

### 5.2 Key SPC Precedent Cases

| Case (Nickname) | Year | Ruling Summary | Significance |
|---|---|---|---|
| **海富案 (Hai Fu v. Shi Heng)** | 2012 | VAM between PE and target company invalid (violated capital maintenance principle); VAM between PE and founders valid | Established the basic framework |
| **翰霖案 (Han Lin)** | 2014 | PE-filed VAM enforced against founders; share repurchase obligation upheld | Extended enforceability to share repurchase |
| **强静延案 (Qiang Jing Yan)** | 2018 | Share repurchase obligation of target company recognized if legally performed | Narrowed Hai Fu — target company can be obligated party if compliant |
| **银海通案 (Yin Hai Tong)** | 2020 | Target company VAM valid if company has distributable profits; capital reduction procedure required for share repurchase | Applied 九民纪要 framework |
| **蓝鼎案 (Lan Ding)** | 2023 | "Performance VAM + listing VAM" dual-trigger structure upheld; cumulative remedy allowed | Confirmed sophistication of VAM structures permissible |

### 5.3 Enforceability Checklist (Current Law)

| Test | Requirement |
|---|---|
| **Contract Formation** | Written agreement; clear performance metrics; definite compensation formula |
| **Target Company as Obligor** | 1) Have distributable retained earnings; 2) Complete statutory capital reduction procedure for share repurchase; 3) Not violate capital maintenance principle |
| **Founder as Obligor** | Generally enforceable; no special restrictions beyond general contract law principles |
| **Fairness Review** | Courts may reduce excessive penalties (≥30% deviation from committed may be adjusted) |
| **No Fraud/Misrepresentation** | VAM induced by fraudulent financials → voidable; full rescission possible |
| **Regulatory Compliance** | Listed company VAM must comply with CSRC disclosure and approval requirements |

### 5.4 Risk Mitigation Recommendations

1. **Structure VAM primarily between acquirer and original shareholders** (not target company alone)
2. **Include target company as joint guarantor** (with board resolution approving guarantee)
3. **Pre-negotiate capital reduction procedures** — obtain board/shareholder resolution at closing
4. **Escrow mechanism** — holdback 10%–20% of consideration to secure VAM obligations
5. **Arbitration vs. litigation** — consider CIETAC arbitration for confidentiality and speed
6. **Governing law** — PRC law for domestic deals; consider HK law for cross-border VAM structures with better common law enforceability precedent

---

## 6. Accounting Treatment (会计处理)

### 6.1 Classification Framework

Under **CAS 22 (金融工具确认和计量)** and **CAS 37 (金融工具列报)**:

| VAM Structure | Accounting Classification | Measurement |
|---|---|---|
| **Cash Compensation (downward-only)** | Financial liability (衍生金融负债) | FVTPL (以公允价值计量且其变动计入当期损益) |
| **Cash Compensation (bidirectional)** | Financial liability | FVTPL initially; remeasured at each reporting date |
| **Share Compensation (fixed number of shares)** | Equity instrument (权益工具) | No remeasurement; initially measured at fair value |
| **Share Compensation (variable number of shares)** | Financial liability | FVTPL — remeasured each period |
| **Reverse VAM (rewards payable)** | Provision or financial liability | Best estimate at each reporting date |

### 6.2 Purchase Price Allocation (PPA) Impact

| Step | Treatment |
|---|---|
| **Initial Recognition** | VAM liability recorded at fair value as part of purchase consideration |
| **Subsequent Measurement** | Remeasure at each reporting date; changes through P&L |
| **Settlement** | Cash settlement → liability derecognition; share settlement → equity adjustment |
| **Goodwill Impact** | Effective VAM reduces goodwill (true price was lower) during measurement period (≤12 months) |
| **Post Measurement-Period Adjustments** | Changes to VAM recognized in P&L (not goodwill adjustment) |

### 6.3 Illustrative Journal Entries

**At Acquisition Date:**
```
Dr. Long-term Equity Investment (or Net Assets Acquired)   RMB 1,000M
    Cr. Cash                                                     RMB  800M
    Cr. Financial Liability — Contingent Consideration           RMB  200M
```

**Year 1: Target Misses — Remeasurement of Liability:**
```
Dr. Fair Value Change (P&L)                                   RMB   50M
    Cr. Financial Liability — Contingent Consideration           RMB   50M
```

**Year 1: Settlement via Cash:**
```
Dr. Financial Liability — Contingent Consideration             RMB  250M
    Cr. Cash                                                     RMB  250M
```

**Settlement via Share Repurchase (fixed number):**
```
Dr. Treasury Shares                                           RMB  250M
    Cr. Cash (RMB 1.00 repurchase price)                         RMB    1M
    Cr. Capital Reserve                                          RMB  249M
```

---

## 7. Tax Treatment (税务处理)

### 7.1 Income Tax — Seller's Perspective

| Scenario | Tax Treatment | Basis |
|---|---|---|
| **Cash Compensation to Acquirer** | Deductible loss (investment loss / contract penalty) for corporate seller; capital loss for individual | PRC EIT Law Art. 8; Individual Income Tax implementing rules |
| **Share Compensation (shares returned)** | Deemed partial rescission of original share transfer; adjusted capital gains calculation | SAT Announcement [2014] No.67 |
| **Reverse VAM — Bonus Received** | Taxable as separate income (service income or other income) | General EIT / IIT rules |
| **PE/VC Fund Seller** | Pass-through treatment depending on partnership structure; may benefit from 20% capital gains rate for individuals | Caishui [2019] No.8 |

### 7.2 Income Tax — Acquirer's Perspective

| Scenario | Tax Treatment |
|---|---|
| **Cash Compensation Received** | Taxable income; not eligible for special tax treatment |
| **Share Compensation (shares cancelled)** | Capital reduction — no immediate tax impact; adjusted tax basis in remaining shares |
| **Reverse VAM — Bonus Paid** | Deductible expense if directly related to acquisition and commercially reasonable |
| **Goodwill Adjustment from VAM** | Reduced goodwill → reduced amortization deduction (indirect tax impact) |

### 7.3 Special Tax Treatment (财税[2009]59号)

| Condition | VAM Impact |
|---|---|
| **Eligible for Special Tax Treatment** | Share-based VAM does NOT disqualify special treatment if VAM is ancillary to qualifying share swap |
| **Cash Component >15%** | May disqualify the entire restructuring from special treatment |
| **VAM Cash Settlement** | Sellers must recalculate original tax basis — may trigger additional tax in year of settlement |
| **Tax Filing Requirement** | VAM outcomes must be reported to tax authorities; refund claims for overpaid tax may have 3-year limitations |

### 7.4 VAT & Stamp Duty

| Tax Type | Treatment |
|---|---|
| **VAT** | Cash compensation under VAM generally NOT subject to VAT (not goods/services); financial liability settlement excluded |
| **Stamp Duty** | Share repurchase/cancellation under VAM attracts 0.05% stamp duty on capital reduction amount |
| **Deed Tax (契税)** | Not applicable to pure VAM settlements unless real property transfer involved |

---

## 8. Core VAM Clause Checklist (协议核心条款清单)

### 8.1 Mandatory Clauses

| # | Clause | Key Content |
|---|---|---|
| 1 | **Definitions & Interpretation** | Precise definition of each performance metric; accounting standards reference (CAS); audit firm designation |
| 2 | **Performance Commitment** | Annual targets (Year 1/2/3); cumulative total; calculation methodology; adjustment exclusions |
| 3 | **Compensation Formula** | Cash formula; share formula; hybrid formula; cap and floor provisions |
| 4 | **Compensation Mechanism** | Payment timeline; funding source guarantee; escrow arrangement; default interest |
| 5 | **Information Rights** | Acquirer audit rights; quarterly reporting; management access; whistleblower provisions |
| 6 | **Representations & Warranties** | Historical financial accuracy; no undisclosed liabilities; full disclosure until closing |
| 7 | **MAC Clause** | Material adverse change definition; carve-outs; consequences |
| 8 | **Covenants During VAM Period** | Business conduct restrictions; capital expenditure limits; dividend restrictions; related-party transaction approval |
| 9 | **Dispute Resolution** | Governing law; arbitration clause (CIETAC / HKIAC); venue; language |
| 10 | **Default & Remedies** | Event of default; cure period; acceleration; cumulative remedies |

### 8.2 Optional / Negotiated Clauses

| # | Clause | Purpose |
|---|---|---|
| 11 | **Earn-Out Upside** | Reverse VAM — reward for exceeding targets |
| 12 | **Insurance / Guarantee** | Third-party guarantee or M&A insurance for VAM obligations |
| 13 | **Accounting Policy Lock** | Pre-agreed accounting policies to prevent earnings management |
| 14 | **Step-In Rights** | Acquirer right to appoint CFO or board observer upon early warning trigger |
| 15 | **Early Buy-Out** | Seller option to prepay remaining VAM at NPV discount |
| 16 | **Listing VAM** | Additional compensation if IPO not achieved within agreed period |
| 17 | **Non-Compete Linked VAM** | Non-compete breach triggers immediate VAM acceleration |
| 18 | **FX / Macro Adjustment** | VAM target adjustment for material forex moves or regulatory changes |
| 19 | **Tax Gross-Up** | Tax treatment of VAM payments pre-agreed; indemnity for adverse tax changes |
| 20 | **Survival Period** | VAM obligations survive closing; specify duration (typically 3–5 years) |

---

## 9. Market Data & Trends

### 9.1 VAM Prevalence by Deal Type (2021–2025 A-share)

| Deal Type | VAM Incidence | Dominant Structure | Avg. Performance Period | Avg. CAGR Committed |
|---|---|---|---|---|
| **Major Asset Restructuring** | ~85% | Cash + Share hybrid; 3-year | 3 years | 18–22% |
| **Controlling Stake Acquisition** | ~60% | Cash VAM; 2–3 year | 2.5 years | 15–20% |
| **Minority PE/VC Investment** | ~95% | Share VAM + listing VAM | 3–5 years | Net profit; IPO timeline |
| **SOE Acquisition** | ~50% | Cash VAM with lower caps | 3 years | 10–15% |
| **Cross-Border** | ~30% | Cash earn-out with escrow | 2–4 years | Revenue/EBITDA-based |

### 9.2 Common Pitfalls

1. **Over-promising leading to systemic VAM failure** — 2021–23: ~40% of A-share M&A VAMs missed at least one year target
2. **Post-VAM performance collapse** — target management departs after VAM period; acquirer left with hollowed-out business
3. **Window-dressing** — aggressive revenue recognition in final VAM year to meet targets
4. **Enforcement difficulty** — founder personal asset dissipation; cross-border enforcement challenges
5. **Accounting complexity** — FVTPL volatility distorts acquirer P&L; quarterly remeasurement burden
6. **Tax ambiguity** — inconsistent local tax authority treatment of VAM settlements

# v2.0 MA参考文件 | 2026-05