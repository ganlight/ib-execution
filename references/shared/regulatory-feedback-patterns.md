# Regulatory Feedback Pattern Database

> **Purpose:** Powers META-03 regulatory feedback analysis. Maps common CSRC/exchange inquiry categories with response frameworks.
> **Last Updated:** 2026-05

---

## Data Structure

Each category contains:
- **Frequency**: How often this category appears (ranked)
- **Avg Questions**: Typical number of sub-questions in this category
- **Question Variants**: 5–10 common phrasings
- **Reply Framework**: Standard response structure
- **Evidence Checklist**: Documents/exhibits to support response
- **Regulatory Basis**: Applicable laws/regulations
- **Anonymized Examples**: Real inquiry excerpts (company names removed)

---

## IPO — 10 Inquiry Categories (Ranked by Frequency)

### IPO-01: Financial Data Consistency & Quality (频率: #1, 平均问题数: 6–10)
**Typical Question Phrasings:**
1. "请发行人说明报告期内营业收入、净利润波动的原因及合理性..."
2. "请保荐机构和会计师核查发行人收入确认政策是否符合企业会计准则..."
3. "请说明应收账款大幅增长的原因，坏账准备计提是否充分..."
4. "报告期毛利率逐年上升/下降的原因，与同行业可比公司是否存在重大差异..."
5. "请说明研发费用资本化的具体依据..."
6. "发行人经营活动现金流与净利润存在重大差异，请分析原因..."
7. "请核查财务内控是否健全有效..."
8. "发行人与关联方资金往来的具体情况，是否存在资金占用..."

**Standard Reply Framework:**
1. Acknowledge the data point questioned
2. Provide detailed breakdown (by product/region/customer)
3. Explain year-over-year trends with business rationale
4. Benchmark against 3–5 comparable listed companies
5. Demonstrate accounting policy compliance with CAS
6. Sponsor + auditor verification opinion
7. Conclusion

**Supporting Evidence Checklist:**
- [ ] Revenue breakdown by product / region / customer
- [ ] Gross margin reconciliation by product line
- [ ] AR aging analysis
- [ ] Comparable company data table (Wind/Bloomberg extract)
- [ ] Accounting policy manual excerpt
- [ ] Internal control test results
- [ ] Related-party transaction register
- [ ] Bank statement reconciliation

**Regulatory Basis:**
- CAS (企业会计准则), specifically: CAS 14 (Revenue), CAS 22 (Financial Instruments), CAS 1 (Inventories)
- 《首发管理办法》 — financial standards
- 《保荐人尽职调查工作准则》

**Anonymized Example (2024):**
> Company X (GEM filing, 2024): CSRC Inquiry R1, Q12: "报告期各期，发行人主营业务收入分别为8.2亿元、10.5亿元、12.3亿元，净利润分别为0.8亿元、1.1亿元、0.5亿元。请说明2025年收入增长但净利润大幅下滑的原因，是否存在业绩持续下滑的风险。请保荐机构和申报会计师核查并发表明确意见。"

---

### IPO-02: Innovation Attributes (STAR/GEM) (频率: #2, 平均问题数: 5–8)
**Typical Question Phrasings:**
1. "请发行人说明是否符合科创板定位，是否具备科创属性..."
2. "请说明核心技术的先进性，与行业技术水平的对比情况..."
3. "发行人发明专利中，与主营业务收入相关的发明数量及占比..."
4. "请说明研发投入的具体构成，研发人员薪酬与数量的匹配性..."
5. "核心技术产品收入占比的计算过程..."
6. "请说明发行人是否属于'三创四新'企业..."
7. "发行人是否属于创业板负面清单行业..."

**Standard Reply Framework:**
1. Map to specific board criteria (STAR: 6 sectors; GEM: 三创四新)
2. Document innovation attributes using quantitative checklist
3. Patent-to-revenue mapping
4. R&D expenditure breakdown (personnel + materials + depreciation + others)
5. Core technology contribution to revenue (%)
6. Industry expert / independent technical consultant opinion
7. Conclusion on eligibility

**Supporting Evidence Checklist:**
- [ ] Patent register with CNIPA filing numbers
- [ ] Patent-revenue mapping table
- [ ] R&D expenditure breakdown per audit report footnote
- [ ] R&D team roster with qualifications
- [ ] Industry classification confirmation
- [ ] Independent technical consultant report (optional but helpful)
- [ ] National S&T awards (if any)
- [ ] Participation in national/provincial major projects

**Anonymized Example (2024):**
> Company Y (STAR filing, 2024): Inquiry R1, Q3: "发行人申报材料显示，近三年累计研发投入5,200万元，占累计营业收入比例为4.2%，低于科创板5%的指标要求。请发行人充分说明是否符合科创板定位和科创属性要求，是否具备明显的技术优势..."

---

### IPO-03: Related-Party Transactions (频率: #3, 平均问题数: 4–7)
**Typical Question Phrasings:**
1. "请说明关联方的认定是否完整..."
2. "关联交易的必要性、合理性和公允性..."
3. "关联交易价格与市场价格的对比情况..."
4. "是否存在通过关联交易调节利润的情形..."
5. "关联方资金拆借的具体情况，是否构成资金占用..."
6. "请说明减少和规范关联交易的措施..."

**Standard Reply Framework:**
1. Complete related-party map (control + significant influence + key management)
2. Transaction-by-transaction register: counterparty, amount, pricing
3. Price comparison (3 comparable third-party transactions or market prices)
4. Impact on financials (% of revenue, % of purchases)
5. Internal control — related-party transaction management policy
6. Trend analysis (increasing/decreasing dependency)
7. Commitment to reduce/regulate

**Supporting Evidence Checklist:**
- [ ] Related-party relationship diagram
- [ ] Complete transaction register (period, counterparty, nature, amount)
- [ ] Price comparison analysis (3 arms-length comparables)
- [ ] Board resolutions approving transactions
- [ ] Independent director opinions
- [ ] Related-party management policy
- [ ] Controlling shareholder undertaking (规范关联交易承诺函)

---

### IPO-04: Independence / Five-Separation (频率: #4, 平均问题数: 3–6)
**Typical Question Phrasings:**
1. "请说明发行人在资产、人员、财务、机构、业务方面的独立性..."
2. "控制股东是否与发行人存在同业竞争..."
3. "发行人是否依赖控股股东的资源..."
4. "发行人高级管理人员在控股股东兼职的具体情况..."
5. "发行人是否独立面向市场获取业务..."

**Standard Reply Framework:**
1. Five-separation checklist (assets, personnel, finance, organization, business) — item-by-item
2. Competitive business assessment (same industry? same customers? same region?)
3. Independent procurement and sales systems
4. Non-compete undertakings from controlling shareholder
5. Conclusion

---

### IPO-05: Control Stability & Actual Controller (频率: #5, 平均问题数: 3–5)

### IPO-06: Use of Proceeds (频率: #6, 平均问题数: 3–6)
**Typical Question Phrasings:**
1. "募集资金投资项目的必要性和可行性..."
2. "募集资金数额与发行人现有生产经营规模、财务状况是否匹配..."
3. "铺底流动资金的具体测算过程..."
4. "是否已取得项目所需的相关审批文件..."

---

### IPO-07: Equity Structure & Historical Capital Changes (频率: #7, 平均问题数: 3–5)
Includes: ESOP compliance, PE special rights, VAM termination, historical pricing fairness.

---

### IPO-08: Labor & Social Insurance Compliance (频率: #8, 平均问题数: 2–4)

### IPO-09: Environmental & Safety Compliance (频率: #9, 平均问题数: 2–3)

### IPO-10: Information Disclosure Quality (频率: #10, 平均问题数: 2–5)
Includes: boilerplate language, inconsistency, omission of material matters.

---

## Refinancing — 5 Inquiry Categories

| ID | Category | Avg Questions | Frequency Rank |
|---|---|---|---|
| REF-01 | Prior fundraising use compliance | 4–6 | #1 |
| REF-02 | Financial condition & refinancing necessity | 4–5 | #2 |
| REF-03 | Pricing fairness & dilution impact | 3–5 | #3 |
| REF-04 | Use of proceeds feasibility (new) | 3–4 | #4 |
| REF-05 | Lockup arrangements & insider trading | 2–3 | #5 |

### Sample: REF-01 Prior Fundraising Compliance
**Typical Phrasings:**
1. "前次募集资金使用是否存在变更，是否履行了必要的决策程序和信息披露义务..."
2. "前次募集资金使用进度缓慢的原因..."

**Reply Framework:**
1. Prior fundraising overview (amount, date, regulator approval)
2. Use-of-proceeds vs. plan comparison table
3. Changes: date, approval process, disclosure
4. Current balance and expected completion timeline
5. Conclusion on compliance

---

## M&A — 6 Inquiry Categories

| ID | Category | Avg Questions | Frequency Rank |
|---|---|---|---|
| MA-01 | Target profitability & financial data | 6–10 | #1 |
| MA-02 | Valuation & appraisal (pricing fairness) | 5–8 | #2 |
| MA-03 | VAM reasonableness | 4–6 | #3 |
| MA-04 | Deal rationale & synergy | 3–5 | #4 |
| MA-05 | Post-merger integration | 2–4 | #5 |
| MA-06 | Backdoor listing concerns | 2–4 | #6 |

### Sample: MA-01 Target Profitability
**Anonymized Example (2024):**
> Company Z (M&A filing, 2024): Inquiry R1, Q5: "标的公司最近一期营业收入同比下滑32%，净利润由盈转亏。请说明业绩大幅下滑的具体原因，是否具有持续性，本次交易完成后上市公司是否存在商誉大幅减值的风险..."

---

## Inquiry Response Best Practices

1. **Answer every sub-question explicitly** — Number responses to match inquiry letter
2. **Add intermediary opinions** — Sponsor, Accountant, Lawyer, Appraiser must all opine
3. **Provide quantitative data** — Not qualitative assertions
4. **Include supporting exhibits** — Mark as attachment
5. **Be consistent** — No contradiction with prospectus or prior responses
6. **Meet deadlines** — R1 ≤3 months, R2 ≤2 months, R3 ≤1 month
7. **Iterate** — Each round reduces questions; typical: R1=15–25, R2=5–10, R3=0–3

## 2024–2025 Regulatory Trends

1. **Financial data scrutiny increased** — Revenue recognition and gross margin are heavily questioned
2. **Innovation attribute is make-or-break** for STAR/GEM — many rejections here
3. **Related-party transactions** are red-flagged when >30% of revenue
4. **Prior fundraising compliance** now checked more stringently
5. **"三创四新" for GEM** being tested more rigorously