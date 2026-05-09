# Valuation Methods — Detailed Guide

> **Purpose:** Comprehensive reference for M&A target valuation, IPO pricing, and appraisal review.
> **Last Updated:** 2026-05

---

## 1. Method Overview

| Method | Best For | Limitations |
|---|---|---|
| **DCF (收益法)** | Stable cash-flow businesses; primary method in Chinese M&A | Sensitive to assumptions; not suitable for early-stage |
| **Market — Comparable Companies (市场法-可比公司)** | Companies with publicly traded peers | Requires genuinely comparable set; thin in niche sectors |
| **Market — Comparable Transactions (市场法-可比交易)** | Similar-industry recent deals | Few true comparables; deal premiums vary |
| **Asset-Based (资产基础法)** | Asset-heavy: real estate, manufacturing, utilities | Ignores going-concern value, IP, brand |
| **Cost Approach (成本法)** | Startups with limited history | Ignores future earnings; only floor value |

**CSRC Guidance:** DCF + Asset-Based dual-approach preferred for material restructurings; DCF primary; asset-based as cross-check.

---

## 2. DCF Method — Detailed Parameters

### Projection Period
| Parameter | Standard Range | Notes |
|---|---|---|
| Explicit projection | 5 years | Regulatory preference |
| Terminal value method | Gordon Growth | Perpetual growth model |
| Terminal growth rate (g) | 2%–3% (<= nominal GDP growth) | Must not exceed long-term GDP |
| High-growth sub-period | Optional 2–3 years before stabilization | Applied where growth doesn't immediately stabilize |

### WACC Components
| Component | Source / Range | Notes |
|---|---|---|
| **Risk-free rate (Rf)** | 10-year China Government Bond (CGB) yield | As of valuation date (~2.5%–3.2% in 2024–2025) |
| **Equity Risk Premium (ERP)** | 5.0%–7.0% | China-specific ERP (Damodaran or local studies) |
| **Unlevered Beta (βu)** | Industry average from comparable listed companies | Bloomberg/Wind terminal |
| **Re-levered Beta (βL)** | βu × [1 + (1−t) × D/E] | Use target capital structure |
| **Target D/E ratio** | Industry average or company plan | For re-levering |
| **Cost of debt (Kd)** | Company borrowing rate or LPR+spread | 3.5%–6.0% typical |
| **Tax rate (t)** | Statutory 25% or actual effective rate | High-tech: 15%; Western regions: 15% |
| **WACC formula** | Ke × E/(D+E) + Kd × (1−t) × D/(D+E) | Standard |

### Sensitivity Table Template
| | Terminal Growth Rate |
|---|---|---|---|---|---|---|
| **WACC** | 1.5% | 2.0% | 2.5% | 3.0% | 3.5% |
| 8.0% | ¥X | ¥X | ¥X | ¥X | ¥X |
| 9.0% | ¥X | ¥X | ¥X | ¥X | ¥X |
| 10.0% | ¥X | ¥X | ¥X | ¥X | ¥X |
| 11.0% | ¥X | ¥X | ¥X | ¥X | ¥X |
| 12.0% | ¥X | ¥X | ¥X | ¥X | ¥X |

### Illiquidity Discount (非流动性折扣)
| Company Type | Discount Range | Note |
|---|---|---|
| Private company (未上市) | 15%–30% | Applied to equity value from DCF |
| Listed company | 0% | No discount |
| NEEQ-listed | 5%–15% | Depending on trading volume |
| STAR/GEM lockup | Per Black-Scholes put option model | For lockup-period valuation |

---

## 3. Market Approach — Comparable Companies

### Selection Criteria
| Criterion | Standard |
|---|---|
| Industry | Same 申万/证监会 industry code (GICS level 3–4) |
| Revenue size | 0.3x–3x of target |
| Profitability | Similar margin profile |
| Geography | A-share listed (primary comparables) |
| Growth rate | Similar revenue/profit CAGR |
| Number of comparables | 3–8 (regulatory preferred range) |
| Time frame | Latest available data (TTM or most recent fiscal year) |

### Multiples
| Multiple | Formula | Best For | Typical Range (China A-Share, 2024) |
|---|---|---|---|
| **PE** | Market Cap / Net Profit | Profitable companies | 12x–45x (varies widely by sector) |
| **PB** | Market Cap / Book Equity | Financials, asset-heavy | 0.8x–5x |
| **PS** | Market Cap / Revenue | High-growth, pre-profit | 1x–10x |
| **EV/EBITDA** | Enterprise Value / EBITDA | Cross-border, capital-structure-neutral | 8x–25x |
| **EV/EBIT** | Enterprise Value / EBIT | Stable capital expenditure | 10x–30x |
| **PEG** | PE / Earnings Growth % | Growth companies | 0.5–2x |

### Selection Matrix
| Sector | Primary Multiple | Secondary Multiple |
|---|---|---|
| Consumer / F&B | PE, PEG | PS |
| Technology / Software | PS, EV/EBITDA | PE |
| Pharma / Biotech | PS, PEG | PE (if profitable) |
| Financials | PB, PE | — |
| Manufacturing | PE, EV/EBITDA | PB |
| Real Estate | PB, P/NAV | — |

---

## 4. Market Approach — Comparable Transactions

### Selection Criteria
| Criterion | Standard |
|---|---|
| Industry | Same or adjacent |
| Transaction date | Last 3 years |
| Deal type | Control acquisition preferred (>50%) |
| Deal size | Similar magnitude (0.5x–3x) |
| Geography | China domestic (primary); cross-border acceptable with premium adjustments |

### Transaction Premiums (Typical, China 2023–2025)
| Sector | Control Premium (over 20D VWAP) |
|---|---|
| Technology | 20%–50% |
| Healthcare | 25%–45% |
| Consumer | 15%–35% |
| Manufacturing | 10%–30% |
| Financial services | 5%–20% |

---

## 5. Asset-Based Approach (资产基础法)

### Application
Best for: asset-heavy companies (manufacturing with significant PP&E, real estate companies, natural resources, utilities).

### Components
| Component | Valuation Method |
|---|---|
| Current assets | Book value (with bad debt/provision check) |
| PP&E | Replacement cost or market comparable |
| Land use rights | Market comparison or benchmark land price |
| Intangible assets (patents, trademarks) | Income approach (relief from royalty) or cost approach |
| Goodwill | Not valued separately (residual) |
| Liabilities | Book value (with contingent liability review) |

### Key Adjustments
| Adjustment | Method |
|---|---|
| Asset impairments | Revalue impaired assets to fair market |
| Hidden liabilities | Environmental remediation, underfunded pensions |
| Off-balance-sheet items | Operating leases, guarantees |

---

## 6. VAM (对赌/估值调整机制) Clauses Library

### Standard VAM Structure
| Component | Standard Formulation |
|---|---|
| **Commitment period** | 3 years (post-acquisition or post-injection) |
| **Performance metric** | Cumulative net profit (扣非归母净利润) |
| **Compensation formula** | (Commitment − Actual) / Total Commitment × Transaction Consideration |
| **Payment method** | Cash or share repurchase at RMB 1.00 |
| **Annual test** | Each year tested; shortfall compensated annually with end-of-period true-up |

### Sample VAM Clause
```
承诺方承诺：标的公司2025年度、2026年度、2027年度
经审计的扣除非经常性损益后归属于母公司股东的净利润
分别不低于人民币[X]万元、[Y]万元、[Z]万元。
三年累计不低于人民币[X+Y+Z]万元。

若任一年度实际净利润低于承诺净利润的85%，
承诺方应于该年度审计报告出具后30日内按以下公式进行补偿：
补偿金额 = (累计承诺净利润 − 累计实际净利润) 
         ÷ 累计承诺净利润 × 本次交易对价 − 已补偿金额。

补偿方式：优先以本次交易取得的股份进行补偿，
不足部分以现金补足。股份补偿价格按人民币1.00元/股计算。
```

### Excess Reward Clause (超额奖励)
| Parameter | Standard |
|---|---|
| Trigger | Cumulative actual ≥ Cumulative commitment × 105–110% |
| Amount | (Actual − Commitment) × 20–50% |
| Recipient | Target management team |
| Payment | Cash bonus, allocated after end of commitment period |

### Key Parameter Ranges
| Parameter | Conservative | Moderate | Aggressive |
|---|---|---|---|
| Profit CAGR commitment | 10%–15% | 15%–25% | 25%+ |
| Compensation coverage ratio | 100% | 100% | 100%+ (over-coverage) |
| Excess reward sharing | 20% | 30% | 50% |
| Extension trigger | <85% of any year | <80% | <90% |

---

## 7. Final Valuation Synthesis

### Weighted Approach (CSRC Preferred)
| Method | Weight | When |
|---|---|---|
| DCF | 60% | Primary method for profitable companies |
| Market — Comparable Companies | 25% | When good comparables exist |
| Asset-Based | 15% | Cross-check; higher weight if asset-heavy |
| Market — Comparable Transactions | Cross-check only | Not weighted |

### Valuation Range Determination
```
Value = W1 × DCF + W2 × Market Comps + W3 × Asset

Final Range = [P25 of composite, P75 of composite]
Deal Price = Within range (with 10% buffer acceptable)
```

---

## 8. Red Flags in Appraisal Reports

| Red Flag | Implication |
|---|---|
| DCF projections >20% revenue CAGR for 5 years | Overly optimistic; likely challenged |
| Terminal value >70% of total DCF | Projection period too short or growth assumptions aggressive |
| Beta <0.6 or >2.0 without justification | Industry mismatch |
| ERP <5% for China | Understated risk |
| Terminal growth >3% | Exceeds GDP; unrealistic |
| WACC <8% for Chinese company | Impossibly low risk premium |
| No sensitivity analysis | Incomplete work; CSRC will ask |
| Single-method valuation | Not compliant with CSRC guidelines |