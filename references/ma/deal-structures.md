# Deal Structure Type Library — M&A Transaction Structures

> **Purpose:** Reference for deal structure design, comparison, and selection in M&A transactions.
> **Last Updated:** 2026-05

---

## 1. Structure Overview

| Structure | Payment Form | Regulatory Review | Timeline | Control Change Risk |
|---|---|---|---|---|
| **Cash Acquisition** | 100% cash | Exchange (light) | 3–6 months | Depends on % acquired |
| **Share Swap** | 100% acquirer shares | M&A Committee | 6–8 months | High |
| **Cash + Shares Hybrid** | Split | M&A Committee | 6–8 months | Depends on ratio |
| **Convertible Bond Payment** | CB issued to seller | M&A Committee | 6–8 months | Depends on conversion |
| **Asset Swap** | Asset exchange | Exchange | 6–12 months | Low if same controller |
| **Absorption Merger** | Share swap + entity dissolution | M&A Committee | 8–12 months | High |

---

## 2. Cash Acquisition (现金收购)

### Pros
- Simple and fast execution
- No share price dilution impact
- No regulatory approval for new share issuance
- Clean exit for seller
- Minimal post-closing entanglement

### Cons
- Significant funding pressure on acquirer
- No seller lock-in (seller exits completely — no incentive alignment)
- Opportunity cost of cash deployment
- May require debt financing, increasing leverage

### Suitable For
- Small deals (RMB <500M)
- Financial buyers exiting
- Acquirer has ample cash reserves
- Non-core asset acquisitions
- Tender offers to minority shareholders

---

## 3. Share Swap (股份支付)

### Pros
- Zero cash outlay — preserves acquirer financial flexibility
- Ties seller to ongoing performance (lockup + shared risk)
- Tax-efficient (special tax treatment for share-for-share exchanges)
- Enables large-scale industrial consolidation
- Seller participates in post-merger upside

### Cons
- Dilution of existing shareholders
- Share price uncertainty — deal value fluctuates
- Complex approval (M&A committee review)
- Longer timeline
- Cultural/integration challenges as seller becomes minority shareholder
- EPS accretion/dilution analysis required

### Suitable For
- Large deals (RMB >1Bn)
- Industrial integration (同行业整合)
- Seller is operating company, not financial investor
- Acquirer share price is liquid and fairly valued
- Consolidation plays in fragmented industries

### Share Exchange Ratio Calculation

```
Exchange Ratio = (Target Equity Value / # Target Shares)
               / (Acquirer Share Price)

Shares Issued = # Target Shares × Exchange Ratio
```

**Valuation reference:** Acquirer share price = average closing price over 20/60/120 trading days before pricing base date.

**Example:**
```
Target equity value: RMB 2,000,000,000
Target total shares: 100,000,000
Target per-share value: RMB 20.00

Acquirer share price (20-day avg): RMB 40.00

Exchange Ratio = 20.00 / 40.00 = 0.50
Shares Issued = 100,000,000 × 0.50 = 50,000,000 new shares
```

### Dilution Analysis
```
Pre-transaction:
  Acquirer shares: 500,000,000
  Acquirer EPS: RMB 1.50

Post-transaction:
  Total shares: 500,000,000 + 50,000,000 = 550,000,000
  Combined net profit (excl. synergies): RMB 750,000,000 + 150,000,000 = 900,000,000
  Pro forma EPS: 900,000,000 / 550,000,000 = RMB 1.636

EPS accretion: (1.636 - 1.50) / 1.50 = 9.1% (accretive)
```

### Control Change Assessment
```
Pre-transaction:
  Controlling shareholder holds: 40% × 500M = 200M shares

Post-transaction:
  Controlling shareholder holds: 200M / 550M = 36.4%
  Seller (target shareholder) becomes: 50M / 550M = 9.1%

If controlling shareholder drops below 30%:
  → May trigger "no actual controller" scenario
  → Regulatory implications: backdoor listing assessment
  → Must disclose control stability analysis
```

---

## 4. Cash + Shares Hybrid (现金+股份)

### Pros
- Best of both worlds:
  - Partial cash provides liquidity to seller
  - Partial shares provides seller incentive alignment
  - Reduces full-share dilution
  - Tax planning flexibility
  - Negotiation flexibility

### Cons
- More complex structuring
- Still requires M&A committee review (shares involved)
- Optimal split is negotiation-intensive
- Cash component still requires funding

### Suitable For
- Universal — most common structure in practice
- Seller wants some immediate liquidity but also long-term participation
- Mid-to-large deals (RMB 500M–5Bn)

### Typical Split Ranges
| Deal Context | Cash % | Share % |
|---|---|---|
| Financial buyer exit | 70%–100% | 0%–30% |
| Industrial integration (friendly) | 30%–50% | 50%–70% |
| Cross-border acquisition | 80%–100% | 0%–20% |
| Under-performance risk high | 40%–60% | 40%–60% |

### Tax Treatment (Special Tax-Free Reorganization)
Condition for tax-free (≥): Cash component ≤ 15% of total consideration.
Then: Share component qualifies for special tax treatment — no immediate capital gains tax for seller.
If cash >15%: Entire gain may be taxable in current period.

---

## 5. Convertible Bond Payment (可转债支付)

### Structure
Acquirer issues convertible bonds to seller as payment consideration. Seller holds bonds with option to:
- Convert to acquirer shares at predetermined conversion price
- Hold to maturity for bond cash flows
- Sell back under put provisions

### Pros
- **Downside protection**: Bond floor value protects seller from share price decline
- **Upside participation**: Conversion feature allows participation if share price rises
- Flexibility for risk-neutral / uncertain sellers
- Lower dilution risk for acquirer if share price doesn't appreciate
- Interest cost is typically low (0.1%–1.0%)

### Cons
- Novel instrument — limited established practice
- Complex valuation (derivatives pricing)
- Accounting complexity (bifurcation of debt/equity components)
- May require guarantee
- Uncertainty about whether bonds convert

### Suitable For
- Risk-neutral sellers
- Uncertain market conditions
- Acquirer wants to defer dilution decision
- Target has moderate-risk profile

### Key Terms
| Parameter | Typical |
|---|---|
| Interest rate | 0.1%–1.0% p.a. |
| Term | 3–6 years |
| Conversion price | ≥ average price of 20 trading days before board resolution date |
| Conversion period | 12 months after issuance |
| Redemption trigger | Stock ≥130% of conversion for 15/30 trading days |
| Put trigger | Stock ≤70% of conversion for 30/30 trading days |

---

## 6. Earn-Out Structure (或有对价)

### When to Use
- Target performance is uncertain (turnaround, early-stage)
- Valuation gap between buyer/seller
- Seller management staying on post-acquisition
- Regulatory uncertainty (pending approvals, litigation)

### Structure
```
Upfront Payment: 70%–85% of base consideration
Earn-Out: 15%–30%, payable upon achievement of pre-agreed milestones
```

| Milestone Type | Sample Metric | Payout |
|---|---|---|
| Financial | Net profit ≥ RMB X in Year 1–3 | Fixed amount per year |
| Operational | Revenue milestone, product launch | Percentage of base |
| Regulatory | Drug approval, permit obtained | Lump-sum |
| Market | IPO / next round at ≥ valuation | Multiplier |

---

## 7. Structure Selection Decision Framework

```
Step 1: Deal size
  < RMB 500M → Consider cash only
  ≥ RMB 500M → Consider shares or hybrid

Step 2: Seller type
  Financial investor → Cash-heavy (70–100%)
  Strategic/industry → Share-heavy (50–100%)

Step 3: Acquirer balance sheet
  Ample cash + low debt → Cash feasible
  Tight cash → Shares or convertible

Step 4: Control assessment
  Will shares issued dilute control >10%?
    YES → Assess backdoor risk, governance stability
    NO → Proceed

Step 5: Tax planning
  Cash ≤15% → Special tax-free treatment possible
  Cash >15% → Discuss tax consequences with seller

Step 6: Timeline
  Urgent → Cash (simpler, faster)
  Flexible → Shares or hybrid (better integration)

Step 7: Risk allocation
  High uncertainty → Earn-out or convertible
  Well-understood → Fixed consideration
```

---

## 8. Regulator Preference

CSRC commentary and feedback patterns indicate:
- **Preferred:** Cash + Shares Hybrid (balances risk, seller lock-in)
- **Neutral:** Pure share swap (accepted for large industrial consolidation)
- **Scrutinized:** Pure cash (especially large deals — "why not shares?")
- **Novel:** Convertible bond payment (limited precedent — expect inquiry)