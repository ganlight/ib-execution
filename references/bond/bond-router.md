# Bond Skill Router — Keyword-to-Sub-Skill Mapping

> **Purpose:** Maps user queries about bond-related IB tasks to the appropriate bond sub-skills.
> **Last Updated:** 2026-05

---

## Bond Sub-Skill Ecosystem

```
ib-execution (this skill)
  └── references/bond/bond-router.md (this file)
        ├── bond-dcm-core/          (DCM orchestration & core workflows)
        ├── bond-due-diligence/     (DD specific to bond products)
        ├── bond-documenter/        (Bond prospectus & legal docs)
        ├── bond-modeler/           (Bond pricing, yield curves, structuring)
        └── ib-bond-executor/       (Bond-specific IB execution workflows)
```

---

## Skill Paths

| Skill | Path |
|---|---|
| bond-dcm-core | `~/.qclaw/skills/bond-dcm-core/SKILL.md` |
| bond-due-diligence | `~/.qclaw/skills/bond-due-diligence/SKILL.md` |
| bond-documenter | `~/.qclaw/skills/bond-documenter/SKILL.md` |
| bond-modeler | `~/.qclaw/skills/bond-modeler/SKILL.md` |
| ib-bond-executor | `~/.qclaw/skills/ib-bond-executor/SKILL.md` |

---

## Keyword → Skill Mapping

### bond-dcm-core
Keywords triggering this skill:
- `债券承销`, `债券发行`, `DCM`, `debt capital market`
- `中期票据`, `MTN`, `超短融`, `SCP`, `短融`, `CP`
- `公司债`, `corporate bond`, `企业债`, `enterprise bond`
- `PPN`, `定向工具`, `定向债务融资工具`
- `金融债`, `financial bond`
- `债券注册`, `bond registration`, `NAFMII`, `交易商协会`
- `债券簿记`, `bookbuilding`
- `债券托管`, `bond custody`
- `债券主承销商`, `lead underwriter bond`
- `债券发行窗口`, `issuance window`
- `债券批文`, `bond approval document`

**Use when:** User asks about bond issuance process, DCM workflow, bond product types, registration procedures, or general bond capital markets work.

### bond-due-diligence
Keywords triggering this skill:
- `债券尽调`, `bond DD`, `bond due diligence`
- `债券尽调清单`, `bond DD checklist`
- `债券发行人`, `bond issuer analysis`
- `城投尽调`, `LGFV due diligence`
- `产业债尽调`, `corporate bond DD`
- `债券信用风险`, `bond credit risk`
- `募集资金用途`, `use of bond proceeds`
- `债券担保`, `bond guarantee`, `增信`, `credit enhancement`
- `债券受托管理人`, `bond trustee`

**Use when:** User asks about bond issuer analysis, bond credit assessment, bond DD procedures, or bond-specific risk factors.

### bond-documenter
Keywords triggering this skill:
- `债券募集说明书`, `bond prospectus`, `bond offering circular`
- `债券法律意见书`, `bond legal opinion`
- `债券评级报告`, `bond rating report`
- `债券受托管理协议`, `bond trustee agreement`
- `债券承销协议`, `bond underwriting agreement`
- `债券条款`, `bond terms`, `bond covenants`
- `债券募集说明书章节`, `bond prospectus sections`
- `债务融资工具`, `debt financing instrument docs`
- `债券申报文件`, `bond filing documents`

**Use when:** User asks about bond document drafting, bond prospectus structure, bond legal documentation, or bond filing requirements.

### bond-modeler
Keywords triggering this skill:
- `债券定价`, `bond pricing`, `bond valuation`
- `收益率曲线`, `yield curve`
- `债券久期`, `bond duration`, `modified duration`
- `债券凸性`, `bond convexity`
- `YTM`, `yield to maturity`
- `债券现金流`, `bond cash flow`
- `债券利率`, `bond coupon`
- `含权债`, `callable bond`, `putable bond`
- `债券期权`, `bond option`
- `债券结构化`, `bond structuring`
- `债券利差`, `bond spread`, `credit spread`
- `Z-spread`, `OAS`

**Use when:** User asks about bond pricing, yield calculations, bond structuring, cash flow modeling, or quantitative bond analysis.

### ib-bond-executor
Keywords triggering this skill:
- `债券执行`, `bond execution`, `bond IB`
- `债券项目`, `bond project`
- `债券申报`, `bond filing`, `bond submission`
- `债券反馈`, `bond regulatory feedback`
- `债券审核`, `bond review`
- `债券发行计划`, `bond issuance plan`
- `债券路演`, `bond roadshow`
- `债券投资人`, `bond investor`
- `债券投标`, `bond bidding`
- `债券缴款`, `bond settlement`
- `债券上市`, `bond listing`
- `ABS`, `资产支持证券`, `asset-backed security`
- `ABN`, `资产支持票据`

**Use when:** User asks about bond deal execution, bond regulatory process, bond issuance management, or securitization products.

---

## Decision Flow

```
User query contains bond-related keywords?
  ├── NO → Stay in ib-executor equity/MA workflows
  └── YES →
        Classify query:
          ├── General DCM / issuance process → bond-dcm-core
          ├── Issuer / credit analysis / DD → bond-due-diligence
          ├── Document drafting / filing docs → bond-documenter
          ├── Pricing / structuring / modeling → bond-modeler
          └── Deal execution / regulatory / pipeline → ib-bond-executor
```

---

## Bond Product Quick Reference

| Product | Regulator | Typical Tenor | Issuer Type |
|---|---|---|---|
| Enterprise Bond (企业债) | NDRC (发改委) | 5–15 yrs | SOEs, LGFVs |
| Corporate Bond (公司债) | CSRC/Exchange | 3–10 yrs | Listed/public companies |
| MTN (中期票据) | NAFMII (交易商协会) | 3–5 yrs (main), 5–10 (long) | All (high credit rating) |
| CP (短期融资券) | NAFMII | ≤1 yr | All |
| SCP (超短期融资券) | NAFMII | ≤270 days | AAA-rated |
| PPN (定向工具) | NAFMII | Flexible | All |
| Financial Bond (金融债) | PBOC/CBRC/CSRC | 3–15 yrs | Financial institutions |
| ABS (资产支持证券) | CSRC | Flexible | Special purpose vehicles |
| ABN (资产支持票据) | NAFMII | Flexible | SPV/Originator |
| Convertible Bond (可转债) | CSRC | 6 yrs | Listed companies |

---

## Cross-Cutting Topics

When queries span multiple bond sub-skills (e.g., "structured bond with complex pricing, document draft, and DD"):
1. Route to **bond-dcm-core** for overall orchestration
2. Then delegate sub-tasks to bond-modeler, bond-documenter, bond-due-diligence as needed