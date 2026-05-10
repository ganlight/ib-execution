---
name: ib-execution-bond
version: 2.0
description: 债券线子入口。覆盖企业债/公司债/MTN/CP/SCP/PPN/永续债/绿债/可转债/可交债等全品种的全生命周期承做。7阶段独立路由，含品种选择、信用分析、募集书撰写、申报注册、簿记定价、受托管理。
---

# 债券线技能入口 (Bond Sub-Entry)

> 债券承做七阶段管线 · 从启动到存续

## 一、债券产品线总览

### 主要品种覆盖

| 品种 | 监管机构 | 审核方式 | 市场 | 典型期限 | 信用特征 |
|------|---------|---------|------|---------|---------|
| 企业债 | 发改委→证监会 | 核准制 | 银行间+交易所 | 3-7年 | 主体信用 |
| 公司债(公募) | 证监会/交易所 | 注册制 | 交易所 | 1-15年 | 主体信用 |
| 公司债(私募) | 交易所 | 备案制 | 交易所 | 1-8年 | 主体信用 |
| 中期票据(MTN) | 交易商协会 | 注册制 | 银行间 | 2-15年(多7年+) | 主体信用 |
| 短期融资券(CP) | 交易商协会 | 注册制 | 银行间 | 1年 | 主体信用 |
| 超短融(SCP) | 交易商协会 | 注册制 | 银行间 | ≤270天 | 主体信用 |
| 定向工具(PPN) | 交易商协会 | 注册制 | 银行间 | 1-10年 | 主体信用 |
| 永续债 | 交易商协会/证监会 | 注册制 | 银行间+交易所 | N年期=含赎回 | 主体信用+会计计入 |
| 绿色债券 | 多监管 | 对应品种 | 双市场 | 对应品种 | 主体+绿色 |
| 可转债 | 证监会 | 核准制 | 交易所 | 1-6年 | 主体+转股 |
| 可交债 | 交易所 | 对应 | 交易所 | 1-6年 | 主体+换股 |
| 金融债 | 央行/银保监会 | 核准制 | 银行间/交易所 | 3-5年 | 金融机构 |
| 境外债 | 外汇局 | - | 境外交易所 | 多3-5年 | 主体+跨境 |
| 城投债 | 多监管 | 对应 | 双市场 | 多5-7年 | 政府关联+财力 |

### 城投专项

城投企业发债需要额外关注：隐性债务筛查（红橙黄绿分区）、政府性应收款占比、市场化收入占比、财承率、平台分类清理。详见 `references/bond/urban-bond-credit-analysis.md`。

---

## 二、七阶段快速路由

### Stage 01：项目启动
```
技能文件：01_项目启动/SKILL_01_债券项目启动.md
  ├─ 客户KYC与反洗钱核查
  ├─ 隐性债务筛查（全国债务监测平台）
  ├─ 评级预沟通（考量AA-/AA/AA+/AAA）
  ├─ 主承销商/承销团组建评估
  └─ 红色阻断清单（10项：违法犯罪、持续亏损、资不抵债等）

关键参考：
  references/bond/bond-product-matrix.md    — 16品种全景对比
  references/shared/intermediary-roles.md    — 中介角色分工

META叠加：
  00-META-01_项目冷启动.md                  — 新项目五步法
```

---

### Stage 02：尽职调查
```
技能文件：02_尽职调查/SKILL_02_债券尽调.md
  ├─ 信用尽调（五维框架：行业-公司-财务-担保-特检）
  ├─ 担保与增信分析（12种担保类型+抵押率上限）
  ├─ 城投专项尽调（区域财力、平台定位、隐债状态）
  ├─ 关联方与关联交易核查
  └─ RAG三级问题追踪（RED/AMBER/GREEN）+整改闭环

关键参考：
  references/bond/credit-analysis-framework.md  — 五维信用分析（含30项财务比率）
  references/bond/guarantee-chain-analysis.md   — 担保链分析框架
  references/bond/urban-bond-credit-analysis.md — 城投专项信用分析
  references/bond/abs-asset-pool-analysis.md    — ABS资产池分析（如涉及ABS）
  references/shared/dd-checkout-master.md       — 尽调总清单
  references/shared/dd-redflag-industry-library.md — 行业风险信号库

脚本工具：
  scripts/dd_checklist_gen.py     — 按项目类型生成核查清单
  scripts/dd_issue_tracker.py     — 尽调问题追踪（三类等级、6个CLI命令）
  scripts/financial_ratio_calc.py — 财务比率计算

META叠加：
  00-META-05_交叉校验质量控制.md               — 尽调数据交叉比对
  00-META-06_中介机构协调.md                   — 律所/会所/评级分工
```

---

### Stage 03：方案设计（品种选择）
```
技能文件：03_方案设计/SKILL_03_债券品种选择.md
  ├─ 品种决策树（5步骤：发行人画像→需求匹配→约束筛查→多品种比较→推荐方案）
  ├─ 品种匹配矩阵（16品种 × 10维度评分）
  ├─ 组合发行策略（单一品种 vs 多品种组合）
  └─ 关键条款设计（期限、利率、增信、还款方式）

关键参考：
  references/bond/bond-product-matrix.md    — 16品种对比矩阵
  references/bond/bond-filing-regulators.md  — 三套监管体系详解（发改委/证监会/交易商协会）
  references/bond/bond-terms-design.md       — 债券条款设计（含回售/赎回/调整票面等）
  references/bond/bond-registration-comparison.md — 注册备案审批差异对比

脚本工具：
  scripts/bond_product_matcher.py  — 自动匹配算法+三类用例

META叠加：
  00-META-15_跨产品线协同工作法.md  — 债券品种比选
  00-META-13_风险定价决策模型.md    — 利率定价决策
```

---

### Stage 04：文件撰写（募集说明书）
```
技能文件：04_文件撰写/SKILL_04_债券募集说明书.md
  ├─ 募集说明书通用章节结构（13章详解）
  ├─ 各品种差异化披露要求
  ├─ 常见审核反馈意见及回复
  └─ 条款设计定量参考

关键参考：
  references/bond/bond-prospectus-detail.md   — 募集说明书逐章详解（含合同模板）
  references/shared/document-cross-ref.md     — 文件交叉引用关系图
  references/compliance/related-party-rules.md — 关联交易规则

META叠加：
  00-META-02_文件迭代工作流.md    — P0初稿→V3最终稿全流程
  00-META-16_文件质量内控标准.md   — 三级审阅+五维评分
```

---

### Stage 05：监管申报
```
技能文件：05_监管申报/SKILL_05_债券申报注册.md
  ├─ 三套申报体系详解：
  │   ├─ 交易商协会注册（MTN/CP/SCP/PPN）
  │   ├─ 证监会注册（公司债）
  │   └─ 发改委核准（企业债）→ 现已转证监会
  ├─ 各品种申报文件清单
  ├─ 申报时间窗口与预测
  └─ 反馈回复策略（模式匹配+模板化）

关键参考：
  references/bond/bond-filing-regulators.md   — 三套监管体系分工
  references/shared/regulatory-feedback-patterns.md — 反馈回复模式

脚本工具：
  scripts/bond_filing_checklist.py — 申报清单生成+M/C/O状态

META叠加：
  00-META-03_反馈回复模式库.md     — 八大类问询回复范式
  00-META-12_监管审核分析框架.md   — 三层规则金字塔
```

---

### Stage 06：发行执行（簿记建档）
```
技能文件：06_发行执行/SKILL_06_债券簿记建档.md
  ├─ 簿记建档日级全流程（T-7→T日）
  ├─ 三种定价方法：簿记应答、招标、协议定价
  ├─ 利率区间测算（参考信用利差+国债基准）
  └─ 应急预案（利率超上限、申购不足等）

关键参考：
  references/bond/bond-secondary-market.md — 二级市场交易机制
  references/bond/credit-analysis-framework.md — 信用利差估算

脚本工具：
  scripts/bond_pricing_calc.py       — 全价/净价/久期/凸性/YTM
  scripts/credit_spread_analyzer.py   — 信用利差分析（含10支可比券）
  scripts/bond_stress_test.py         — 压力测试多情景

META叠加：
  00-META-13_风险定价决策模型.md    — 三层定价决策
```

---

### Stage 07：存续期管理（受托管理）
```
技能文件：07_存续期管理/SKILL_07_债券受托管理.md
  ├─ 23项重大事项监控体系
  ├─ 持有人会议召集与管理
  ├─ 信息披露（月度/季度/年度）
  ├─ 风险处置（违约预警+重组谈判）
  └─ 受托管理工作计划+工作报告

脚本工具：
  scripts/bond_default_early_warning.py — 违约预警
  scripts/bond_cashflow_cover.py        — 现金流覆盖+DSCR
  scripts/bond_rating_template.py       — 评级报告模板

META叠加：
  META-11（全生命周期闭环）
```

---

## 三、场景示例（5个）

### 场景1：品种选择
> "AA+城投想发行中期票据10亿，AAA央企30亿5年期项目债，分别选什么品种？"

```
路由流程：
1. 发行人画像提取 → bond_product_matcher.py
2. 品种匹配矩阵查询 → SKILL_03_债券品种选择.md
3. 关键约束检查 → bond-product-matrix.md（评级/规模/期限限制）
4. 提供推荐品种+备选方案
```

---

### 场景2：信用分析
> "这家AA级区县城投，负债率58%，年经营性现金流仅覆盖应付债券的本息75%，还能发债吗？"

```
路由流程：
1. 五维框架分析 → credit-analysis-framework.md
2. 城投专项检查 → urban-bond-credit-analysis.md
3. 财务比率计算 → financial_ratio_calc.py
4. 担保/增信建议 → guarantee-chain-analysis.md
阶段：02_尽职调查 → 产出：信用评级建议+风险评分
```

---

### 场景3：募集书撰写
> "客户的20亿永续中期票据，帮我写该笔发行的募集说明书管理层分析与财务信息部分"

```
路由流程：
1. 加载募集书章节详解 → bond-prospectus-detail.md
2. 加载永续债+MTN专门条款 → SKILL_04_债券募集说明书.md
3. 加载文件迭代工作流 → META-02（P0→V2）
4. 加载文件质量检查 → META-16（正向检查10关+反向检查）
阶段：04_文件撰写 → 产出：募集说明书更新版本
```

---

### 场景4：申报注册
> "公司债材料提交交易所，需要有哪些文件？审查周期多久？"

```
路由流程：
1. 监管体系对比 → bond-filing-regulators.md
2. 品种申报清单 → bond_filing_checklist.py（公司债项→完整清单）
3. 反馈回复预判 → META-03（政府采购+尽职检查模块）
4. 审核时间线规划 → META-07（排进度表）
```

---

### 场景5：定价计算
> "这支债券T+3日进入簿记需求阶段，票面利率4%，同期国债2.5%，信用利差明显偏高吗？"

```
路由流程：
1. 利差分析 → credit_spread_analyzer.py（--test含10支可比债券）
2. 定价计算 → bond_pricing_calc.py（净价/全价/久期/凸性/YTM完整输出）
3. 压力测试 → bond_stress_test.py（±50bp情景）
4. 定价框架分析 → META-13（三层定价决策模型）
```

---

## 四、委托接口

### 专项技能委托链表

| 任务复杂度 | 本技能可处理 | 需委托专项技能 |
|-----------|------------|--------------|
| 债券品种快速匹配 | ✅ 基本匹配（SKILL_03） | 深度品种+市场惯例→ `bond-dcm-core` |
| 债券信用分析 | ✅ 五维框架（SKILL_02+ref） | 深度信用→ `bond-due-diligence` |
| 募集说明书章节撰写 | ✅ 模板化撰写（SKILL_04） | 深度逐章指导→ `bond-documenter` |
| 债券定价计算 | ✅ 直接脚本（python） | 深度YTM/曲线→ `bond-modeler` |
| 申报文件清单 | ✅ 自动生成（bond_filing_checklist） | 深度监管咨询→ `bond-dcm-core` |
| 全流程管理 | ✅ 本七阶段 | 物质层整体 → `ib-bond-executor` |
| 募集说明书PDF提取 | 不适用 | `bond-prospectus-parser` |
| 财务比率分析 | ✅ financial_ratio_calc.py | 无 |

### 委托方式

```
⚠️ RED：强制委托（本技能无法覆盖）→ always 委托制
🟡 AMBER：可选委托（本技能基本覆盖，但深度需求可委托）
🟢 GREEN：本技能自行处理（不委托）
```

---

## 五、Token 预算

| 场景 | 加载序列 | 预估 tokens |
|------|---------|------------|
| 项目冷启动 | SKILL_01_债券项目启动.md + ref×1 | ~3,500 |
| 债券尽调 | SKILL_02_债券尽调.md + ref×2 + script×1 | ~5,000 |
| 品种选择 | SKILL_03_债券品种选择.md + ref×2 + script×1 | ~4,000 |
| 募集书 | SKILL_04_债券募集说明书.md + ref×2 | ~6,000 |
| 申报注册 | SKILL_05_债券申报注册.md + ref×1 + script×1 | ~4,500 |
| 簿记定价 | SKILL_06_债券簿记建档.md + 2 scripts | ~3,500 |
| 受托管理 | SKILL_07_债券受托管理.md + 2 scripts | ~3,500 |
| 深度+委托 | 本入口 + bond-dcm-core | ~7,500 |

---

## 六、与ABS线的关系

ABN（资产支持票据）虽然带"票据"两字，但属于 ABS 线（非债券线）。路由规则：
- 资产支持票据 ABN → `skills/abs/`（ABS线）
- 中期票据 MTN、定向工具 PPN → `skills/bond/`（债券线）

---

## 快速导航

| 需求 | 文件 |
|------|------|
| 接到新债券客户 | `01_项目启动/SKILL_01_债券项目启动.md` |
| 做信用分析 | `02_尽职调查/SKILL_02_债券尽调.md` + `credit-analysis-framework.md` |
| 选品种 | `03_方案设计/SKILL_03_债券品种选择.md` + `bond_product_matcher.py` |
| 写募集书 | `04_文件撰写/SKILL_04_债券募集说明书.md` + META-02 |
| 提交申报 | `05_监管申报/SKILL_05_债券申报注册.md` + `bond_filing_checklist.py` |
| 实施簿建 | `06_发行执行/SKILL_06_债券簿记建档.md` + `bond_pricing_calc.py` |
| 做受托 | `07_存续期管理/SKILL_07_债券受托管理.md` + `bond_default_early_warning.py` |

---

# v2.0 三线重组 | 2026-05