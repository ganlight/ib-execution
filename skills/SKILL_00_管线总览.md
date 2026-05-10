---
name: skill-00
title: 投行承做管线总览
description: 从项目启动到存续期管理的七阶段全产品管线，含股权/债券/并购三线分叉和四层递进模型
---

# SKILL 00: 投行承做管线总览

> 本文件是总控文档，描述管线工序顺序和依赖关系，具体方法见各阶段 SKILL 和 META 技能。

---

## 一、七阶段管线

```
            ┌──────────────┐
            │  01 项目启动  │  客户KYC、利益冲突、立项
            └──────┬───────┘
                   │
            ┌──────▼───────┐
            │  02 尽职调查  │  法律DD、财务DD、业务DD、底稿
            └──────┬───────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
   ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
   │03a IPO │ │03b再融资│ │03d并购  │  03c债券→委托
   └────┬───┘ └───┬────┘ └───┬────┘
        │         │          │
   ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
   │04a招股书│ │04a招股书│ │04c重组书│  04b债券→委托
   └────┬───┘ └───┬────┘ └───┬────┘
        │         │          │
   ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
   │05a IPO │ │05a IPO │ │05d重组 │  05c债券→委托
   └────┬───┘ └───┬────┘ └───┬────┘
        │         │          │
   ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
   │06a路演  │ │06a路演  │ │06c交割 │  06b债券→委托
   └────┬───┘ └───┬────┘ └───┬────┘
        │         │          │
   ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
   │07a督导  │ │07a督导  │ │07c整合 │  07b债券→委托
   └────────┘ └────────┘ └────────┘
```

## 二、核心原则

1. **先通用后分叉** — Stage 01-02 所有产品线通用，Stage 03 起按产品线分叉
2. **债券委托不重写** — 债券任务路由到已有 bond-* 技能，META 方法可叠加
3. **阶段间数据契约** — 每阶段产出有明确数据格式，下一阶段以此为输入
4. **质量内建** — 每阶段有必过质量门槛，不通过不得进入下一阶段
5. **迭代收敛** — 文件从 P0 初稿到 PN 定稿，用 META-02 迭代工作流驱动

## 三、四层递进模型（IB版）

```
        ┌─────────────────────────────────────────────┐
  4层   │  方案语义 — 交易方案、产品选择、时间表         │  03 方案设计
        │  为什么选科创板？为什么定增不配股？           │
        ├─────────────────────────────────────────────┤
  3层   │  文件语义 — 招股书/重组报告书                 │  04 文件撰写  05 申报
        │  各章节约束、数据一致性、披露完整性            │
        ├─────────────────────────────────────────────┤
  2层   │  事实语义 — 尽调发现、财务数据、法律事实       │  02 尽职调查
        │  收入真实性？关联交易公允？诉讼风险？          │
        ├─────────────────────────────────────────────┤
  1层   │  准入语义 — 客户资质、利益冲突                │  01 项目启动
        │  这个客户能不能做？有没有资格？               │
        └─────────────────────────────────────────────┘
```

每一层是下一层的前提：准入→事实→文件→方案。上层犯错导致下层全部返工。

## 四、META 技能索引

### 4.1 基础META层（00-08）

| 编号 | 文件 | 内容 | 适用场景 |
|------|------|------|----------|
| M00 | 00-META-00_IB方法论总纲.md | OTF+JIT+Bootstrap 投行版 | 全流程方法论基础 |
| M01 | 00-META-01_项目冷启动.md | 从零接手项目的五步法 | 新项目启动 |
| M02 | 00-META-02_文件迭代工作流.md | 初稿→内核→申报→反馈→定稿 | 文件撰写全程 |
| M03 | 00-META-03_反馈回复模式库.md | 八大类监管问询的回复范式 | 审核问询回复 |
| M04 | 00-META-04_柳叶刀混合工作法.md | LLM+模板+脚本+人工分工 | AI辅助工作 |
| M05 | 00-META-05_交叉校验质量控制.md | 文件间数据一致性+Lint规则 | 质量控制 |
| M06 | 00-META-06_中介机构协调.md | 四中介分工矩阵+时间衔接 | 中介管理 |
| M07 | 00-META-07_时间表管理.md | 里程碑+关键路径+风险预警 | 项目管理 |
| M08 | 00-META-08_SKILL优化与演化.md | 从项目中持续学习进化 | 技能迭代 |

### 4.2 扩展META层（11-18）

| 编号 | 文件 | 内容 | 适用场景 |
|------|------|------|----------|
| M11 | 00-META-11_投行项目生命周期管理模型.md | 七阶段完整生命周期模型 | 项目全周期规划 |
| M12 | 00-META-12_监管审核分析框架.md | 三层规则金字塔+反馈回复方法论 | 监管审核应对 |
| M13 | 00-META-13_风险定价决策模型.md | 债券/股票/并购定价决策框架 | 定价决策 |
| M15 | 00-META-15_跨产品线协同工作法.md | 三线资源复用+方案比选 | 多产品线协同 |
| M16 | 00-META-16_文件质量内控标准.md | 三级审阅体系+五维评分卡 | 文件质量控制 |
| M17 | 00-META-17_中介机构协调方法论.md | 中介选聘+分工+冲突管理 | 中介全面协调 |
| M18 | 00-META-18_AI辅助投行工作伦理准则.md | AI使用边界+保密+披露 | AI辅助工作 |

---

## 五、完整路由决策树

### 5.1 用户输入 → 产品线识别

```
用户输入/任务描述
        │
        ▼
┌───────────────────┐
│ 识别产品线关键词   │
└────────┬──────────┘
         │
  ┌──────┼───────┬────────┐
  │      │       │        │
 ▼      ▼       ▼        ▼
IPO   债券    并购    不明确→综合评估
        │       │
        ▼       ▼
    bond路径  ma路径
```

**产品线关键词映射**：

| 产品线 | 关键词 |
|--------|--------|
| **IPO/股权** | IPO、上市、招股书、路演、科创板、创业板、主板、北交所、定增、配股、可转债、再融资 |
| **债券** | 企业债、公司债、MTN、CP、SCP、PPN、ABS、REITs、债券、募集说明书、评级、簿记 |
| **并购** | 并购、重组、重大资产重组、借壳、换股、吸收合并、业绩承诺、对赌、交割 |

### 5.2 产品线 → 阶段路由

#### IPO/股权路径

```
IPO识别
   │
   ▼
Stage01: 项目启动 → SKILL_01c_初步方案建议书.md
   │          └→ 客户KYC+利益冲突+立项
   ▼
Stage02: 尽职调查 → SKILL_02_尽职调查总览.md
   │          └→ 法律+财务+业务DD
   ▼
Stage03: 方案设计 → SKILL_03a_IPO方案设计.md
   │          └→ 板块选择+募投+发行方案
   ▼
Stage04: 文件撰写 → SKILL_04a_招股说明书撰写.md
   │          └→ 逐章撰写+版本管理
   ▼
Stage05: 监管申报 → SKILL_05a_IPO申报材料清单.md
   │          └→ 材料准备+反馈回复
   ▼
Stage06: 发行执行 → SKILL_06a_IPO路演与定价.md
   │          └→ 路演+询价+定价
   ▼
Stage07: 存续期 → SKILL_07a_IPO持续督导.md
            └→ 持续督导+信息披露
```

#### 债券路径（委托bond技能体系）

```
债券识别
   │
   ▼
Stage01: 债券启动 → SKILL_01_债券项目启动.md
   │          └→ KYC+隐债筛查+评级预沟通
   ▼
Stage02: 债券尽调 → SKILL_02_债券尽调.md
   │          └→ 信用+担保增信+城投专项
   ▼
Stage03: 品种选择 → SKILL_03c_债券品种选择.md
   │          └→ 决策树+匹配矩阵
   ▼
Stage04: 募集书撰写 → SKILL_04b_债券募集说明书.md
   │             └→ 逐章详解+审核意见
   ▼
Stage05: 申报注册 → SKILL_05c_债券申报注册.md
   │          └→ 三套注册体系+文件清单
   ▼
Stage06: 簿记建档 → SKILL_06b_债券簿记建档.md
   │          └→ 全流程+定价方法
   ▼
Stage07: 受托管理 → SKILL_07b_债券受托管理.md
            └→ 重大事项+持有人会议
```

#### 并购路径

```
并购识别
   │
   ▼
Stage01: 项目启动 → SKILL_01c_初步方案建议书.md
   │          └→ 战略匹配+交易意向
   ▼
Stage02: 尽职调查 → SKILL_02_尽职调查总览.md（扩展至交易对方）
   │          └→ 估值导向DD+协同效应分析
   ▼
Stage03: 方案设计 → SKILL_03d_并购重组方案.md
   │          └→ 交易结构+对赌+整合方案
   ▼
Stage04: 文件撰写 → SKILL_04c_重组报告书撰写.md
   │          └→ 重组报告+法律意见
   ▼
Stage05: 监管申报 → SKILL_05d_重组审核流程.md
   │          └→ 并购重组委审核
   ▼
Stage06: 交割执行 → SKILL_06c_并购交割.md
   │          └→ 先决条件+过户
   ▼
Stage07: 整合跟踪 → SKILL_07c_并购整合跟踪.md
            └→ 业绩承诺+减值测试
```

---

## 六、技能调用方法

### 6.1 调用标准格式

**格式**：
```
当用户说：[任务描述]
→ 识别产品线：[IPO/债券/并购/综合]
→ 识别阶段：[01-07]
→ 识别具体技能：[SKILL文件名]
→ 调用方法：直接读取+执行
```

### 6.2 债券委托接口

债券产品线的所有任务通过以下接口委托：

```
债券任务 → ib-execution SKILL体系
         → bond-dcm-core 技能（bond-dcm-core）
         → bond-documenter 技能（bond-documenter）
         → bond-prospectus-parser（如有募集说明书解析需求）
         → bond-modeler（如有定价建模需求）
         → bond-due-diligence（如有尽调需求）
```

**债券委托清单**：

| 债券子任务 | 委托目标 | 接口文件 |
|------------|----------|----------|
| 债券品种选择 | bond-dcm-core | SKILL_03c_债券品种选择.md |
| 债券尽调 | bond-due-diligence | SKILL_02_债券尽调.md |
| 募集说明书撰写 | bond-documenter | SKILL_04b_债券募集说明书.md |
| 申报注册 | bond-dcm-core | SKILL_05c_债券申报注册.md |
| 簿记建档 | bond-dcm-core | SKILL_06b_债券簿记建档.md |
| 受托管理 | bond-dcm-core | SKILL_07b_债券受托管理.md |
| 收益率计算 | bond-modeler | scripts/bond_pricing_calc.py |
| 信用分析 | bond-dcm-core | references/bond/credit-analysis-framework.md |

### 6.3 META技能调用时机

| 用户任务 | 推荐调用的META技能 |
|----------|-------------------|
| 新客户首次接触 | META-01 + META-11 |
| 制定项目时间表 | META-07 |
| 尽调发现质量问题 | META-05 |
| 收到监管反馈 | META-03 + META-12 |
| 撰写/修改文件 | META-02 + META-16 |
| 多产品线客户 | META-15 |
| 协调中介机构 | META-06 + META-17 |
| 涉及AI辅助 | META-18 |
| 涉及定价/估值 | META-13 |
| 项目全周期规划 | META-11 |

---

## 七、按场景索引（10个常见场景）

### 场景1：IPO项目冷启动

```
触发词："一个新IPO项目"、"准备做上市"、"科创板IPO"

技能组合：
├─ 快速路由：SKILL_01c_初步方案建议书.md
├─ META配合：
│   ├─ META-01（项目冷启动五步法）
│   └─ META-11（三线检查，评估债券/IPO比选）
├─ 参考文件：
│   ├─ references/equity/ipo-board-conditions.md
│   └─ references/equity/ipo-timeline.md
└─ 脚本工具：scripts/ipo_board_check.py
```

### 场景2：债券项目启动尽调

```
触发词："发行企业债"、"做公司债"、"MTN"、"ABS"

技能组合：
├─ 快速路由：SKILL_01_债券项目启动.md
├─ 债券专项：SKILL_02_债券尽调.md
├─ META配合：
│   ├─ META-11（三线检查，看是否有IPO机会）
│   └─ META-15（跨产品线协同）
├─ 参考文件：
│   ├─ references/bond/bond-product-matrix.md
│   ├─ references/bond/credit-analysis-framework.md
│   └─ references/bond/guarantee-chain-analysis.md
└─ 脚本工具：scripts/bond_filing_checklist.py
```

### 场景3：并购重组方案设计

```
触发词："重大资产重组"、"借壳上市"、"换股吸收合并"

技能组合：
├─ 快速路由：SKILL_03d_并购重组方案.md
├─ 估值建模：SKILL_03e_财务建模.md
├─ META配合：
│   ├─ META-13（对赌条款设计）
│   └─ META-15（IPO vs 借壳方案比选）
├─ 参考文件：
│   ├─ references/ma/restructuring-standards.md
│   ├─ references/ma/valuation-methods.md
│   └─ references/ma/deal-structures.md
└─ 脚本工具：scripts/ma_valuation_calc.py
```

### 场景4：收到监管反馈（IPO）

```
触发词："收到反馈"、"问询回复"、"预审员追问"

技能组合：
├─ 快速路由：SKILL_05e_反馈回复撰写策略.md
├─ META配合：
│   ├─ META-03（反馈回复模式库）
│   └─ META-12（监管审核分析框架）
├─ 参考文件：
│   └─ references/shared/regulatory-feedback-patterns.md
└─ 脚本工具：scripts/filing_tracker.py
```

### 场景5：债券品种选择

```
触发词："发什么债券好"、"品种选择"、"公司债还是MTN"

技能组合：
├─ 快速路由：SKILL_03c_债券品种选择.md
├─ 债券专项：bond-dcm-core bond-product-matrix
├─ META配合：
│   └─ META-13（定价决策）
├─ 参考文件：
│   ├─ references/bond/bond-product-matrix.md
│   └─ references/bond/bond-filing-regulators.md
└─ 脚本工具：scripts/bond_product_matcher.py
```

### 场景6：尽调发现问题整改

```
触发词："尽调发现问题"、"需要整改"、"RAG评级"

技能组合：
├─ 快速路由：SKILL_02e_问题追踪与整改.md
├─ META配合：
│   ├─ META-05（交叉校验质量控制）
│   └─ META-16（文件质量内控）
├─ 参考文件：
│   ├─ references/shared/dd-redflag-industry-library.md
│   └─ references/shared/dd-checklist-master.md
└─ 脚本工具：scripts/dd_issue_tracker.py
```

### 场景7：招股说明书撰写

```
触发词："写招股书"、"招股书第X章"、"申报文件"

技能组合：
├─ 快速路由：SKILL_04a_招股说明书撰写.md
├─ META配合：
│   ├─ META-02（文件迭代工作流）
│   └─ META-16（文件质量内控）
├─ 参考文件：
│   ├─ references/equity/prospectus-sections.md
│   └─ references/shared/document-cross-ref.md
└─ 脚本工具：
    ├─ scripts/doc_version_diff.py（版本对比）
    └─ scripts/cross_ref_check.py（交叉引用核查）
```

### 场景8：债券发行定价

```
触发词："债券定价"、"利率区间"、"簿记建档"

技能组合：
├─ 快速路由：SKILL_06b_债券簿记建档.md
├─ 债券专项：bond-modeler
├─ META配合：
│   └─ META-13（风险定价决策）
├─ 参考文件：
│   └─ references/bond/credit-analysis-framework.md
└─ 脚本工具：
    ├─ scripts/bond_pricing_calc.py（定价计算）
    ├─ scripts/credit_spread_analyzer.py（利差分析）
    └─ scripts/bond_stress_test.py（压力测试）
```

### 场景9：项目时间表管理

```
触发词："项目时间表"、"里程碑"、"关键节点"

技能组合：
├─ 快速路由：SKILL_00（管线总览）
├─ META配合：
│   ├─ META-07（时间表管理）
│   └─ META-11（生命周期管理）
├─ 参考文件：
│   ├─ references/equity/ipo-timeline.md
│   └─ references/shared/dd-filing-standards.md
└─ 脚本工具：
    └─ scripts/timeline_gen.py（时间表生成）
```

### 场景10：尽调报告撰写

```
触发词："尽调报告"、"DD报告"、"法律尽调报告"

技能组合：
├─ 快速路由：SKILL_02f_尽调报告撰写.md
├─ 细分类型：
│   ├─ 法律DD：SKILL_02a_法律尽调.md
│   ├─ 财务DD：SKILL_02b_财务尽调.md
│   └─ 业务DD：SKILL_02c_业务尽调.md
├─ META配合：
│   ├─ META-05（质量控制）
│   └─ META-16（文件质量）
├─ 参考文件：
│   └─ references/shared/dd_report_template.md
└─ 脚本工具：
    ├─ scripts/dd_checklist_gen.py（清单生成）
    └─ scripts/financial_ratio_calc.py（财务比率）
```

---

## 八、文件资产地图

### 8.1 References 目录

| 目录 | 文件 | 用途 | 适用产品线 |
|------|------|------|------------|
| **equity/** | ipo-board-conditions.md | 各板块上市条件详细对比 | IPO |
| **equity/** | ipo-timeline.md | IPO标准时间表 | IPO |
| **equity/** | prospectus-sections.md | 招股书各章节详解 | IPO |
| **equity/** | refinancing-rules.md | 再融资品种对比与规则 | 再融资 |
| **ma/** | restructuring-standards.md | 重大资产重组标准 | 并购 |
| **ma/** | valuation-methods.md | 并购估值方法详解 | 并购 |
| **ma/** | deal-structures.md | 交易结构类型库 | 并购 |
| **bond/** | bond-product-matrix.md | 16种债券品种全景对比 | 债券 |
| **bond/** | credit-analysis-framework.md | 五维信用分析框架 | 债券 |
| **bond/** | bond-filing-regulators.md | 三套监管体系详解 | 债券 |
| **bond/** | bond-router.md | 关键词→子技能路由映射 | 债券 |
| **bond/** | bond-prospectus-detail.md | 募集说明书逐章详解 | 债券 |
| **bond/** | bond-terms-design.md | 债券条款设计参考 | 债券 |
| **bond/** | bond-secondary-market.md | 二级市场交易机制 | 债券 |
| **bond/** | abs-asset-pool-analysis.md | ABS资产池尽调框架 | ABS |
| **bond/** | guarantee-chain-analysis.md | 担保增信分析框架 | 债券 |
| **bond/** | urban-bond-credit-analysis.md | 城投债专项信用分析 | 城投债 |
| **shared/** | dd-checklist-master.md | 尽调总清单（通用） | 全线 |
| **shared/** | dd-filing-standards.md | 底稿归档标准 | 全线 |
| **shared/** | dd-redflag-industry-library.md | 行业风险信号库 | 全线 |
| **shared/** | dd_report_template.md | 尽调报告模板 | 全线 |
| **shared/** | document-cross-ref.md | 文件交叉引用关系图 | 全线 |
| **shared/** | intermediary-roles.md | 中介角色分工矩阵 | 全线 |
| **shared/** | management-interview-guide.md | 管理层访谈指南 | 全线 |
| **shared/** | qoe-analysis-framework.md | 经营质量分析框架 | 全线 |
| **shared/** | regulatory-feedback-patterns.md | 反馈模式库数据 | 全线 |
| **shared/** | revenue-quality-analysis.md | 收入质量分析方法 | 全线 |
| **shared/** | site-inspection-procedures.md | 实地走访程序 | 全线 |
| **compliance/** | related-party-rules.md | 关联交易规则 | IPO/重组 |
| **compliance/** | independence-rules.md | 独立性规则 | IPO/债券 |
| **compliance/** | materiality-thresholds.md | 重大性判断标准 | 全线 |

### 8.2 Scripts 目录

| 脚本文件 | 功能 | 输入 | 输出 |
|----------|------|------|------|
| bond_pricing_calc.py | 债券定价计算 | 票面/期限/市场利率 | 全价/净价/YTM |
| bond_product_matcher.py | 债券品种匹配 | 企业资质+融资需求 | 候选品种列表 |
| bond_filing_checklist.py | 债券申报清单 | 项目基本信息 | 完整申报清单 |
| bond_rating_template.py | 评级报告模板 | 企业财务数据 | 评级报告草稿 |
| bond_cashflow_cover.py | 现金流覆盖分析 | 债券还本付息计划 | 覆盖倍数表 |
| bond_default_early_warning.py | 违约预警 | 企业财务数据 | 预警信号 |
| bond_stress_test.py | 债券压力测试 | 基础情景 | 多情景敏感性 |
| credit_spread_analyzer.py | 信用利差分析 | 企业评级/基准利率 | 利差估算 |
| cross_ref_check.py | 文件交叉引用检查 | 目标文件 | 引用一致性报告 |
| dd_checklist_gen.py | 尽调清单生成 | 项目类型+行业 | 定制化尽调清单 |
| dd_issue_tracker.py | 尽调问题追踪 | 问题描述 | RAG分级+追踪表 |
| doc_version_diff.py | 文件版本对比 | 两个版本文件 | 差异报告 |
| filing_tracker.py | 审核进度追踪 | 项目状态 | 可视化进度表 |
| financial_ratio_calc.py | 财务比率计算 | 财务报表 | 完整财务比率表 |
| ipo_board_check.py | 板块条件核查 | 企业数据 | 各板块符合性报告 |
| ma_valuation_calc.py | 并购估值计算 | 标的财务数据 | DCF/可比估值结果 |
| timeline_gen.py | 项目时间表生成 | 阶段信息 | 标准时间表甘特图 |

### 8.3 Templates 目录

> 当前版本未包含独立 templates 目录，模板功能整合在各 SKILL 文件中。

---

## 九、阶段详细索引

### Stage 01: 项目启动
| 文件 | 内容 |
|------|------|
| SKILL_01_项目启动与客户准入.md | 阶段总览 |
| SKILL_01a_客户KYC与反洗钱.md | KYC/AML核查 |
| SKILL_01b_利益冲突检查.md | 冲突核查流程 |
| SKILL_01c_初步方案建议书.md | Pitch Book/立项报告 |
| SKILL_01_债券项目启动.md | 债券专项KYC+隐债筛查 |

### Stage 02: 尽职调查
| 文件 | 内容 |
|------|------|
| SKILL_02_尽职调查总览.md | 股/债/并购 DD差异 |
| SKILL_02a_法律尽调.md | 主体资格、股权、资产、合同、诉讼 |
| SKILL_02b_财务尽调.md | 银行流水、函证、关联方、收入分析 |
| SKILL_02c_业务尽调.md | 行业、客户供应商、技术研发 |
| SKILL_02d_底稿工作体系.md | 底稿目录、分类、归档 |
| SKILL_02e_问题追踪与整改.md | RAG分级、闭环管理 |
| SKILL_02f_尽调报告撰写.md | 尽调总结模板 |
| SKILL_02_债券尽调.md | 债券专项信用+担保尽调 |

### Stage 03: 方案设计
| 文件 | 内容 |
|------|------|
| SKILL_03_方案设计总览.md | 产品选择决策树 |
| SKILL_03a_IPO方案设计.md | 板块选择+发行方案+募投 |
| SKILL_03b_再融资方案设计.md | 定增/配股/可转债 |
| SKILL_03c_债券品种选择.md | → 委托 bond-dcm-core |
| SKILL_03d_并购重组方案.md | 交易结构+对赌+整合 |
| SKILL_03e_财务建模.md | DCF+可比+敏感性 |

### Stage 04: 文件撰写
| 文件 | 内容 |
|------|------|
| SKILL_04_文件撰写总览.md | 文件体系+中介分工+版本管理 |
| SKILL_04a_招股说明书撰写.md | 各章节详细指引 |
| SKILL_04b_债券募集说明书.md | → 委托 bond-documenter |
| SKILL_04c_重组报告书撰写.md | 重组报告专用 |
| SKILL_04d_法律意见书标准.md | 律师文件核查 |
| SKILL_04e_审计报告核查.md | 会计师文件核查 |
| SKILL_04f_文件版本管理.md | 版本控制与diff |

### Stage 05: 监管申报
| 文件 | 内容 |
|------|------|
| SKILL_05_监管申报总览.md | 各产品审核流程 |
| SKILL_05a_IPO申报材料清单.md | 全套文件checklist |
| SKILL_05b_IPO审核流程与问询.md | 受理→问询→上会→注册 |
| SKILL_05c_债券申报注册.md | → 委托 ib-bond-executor |
| SKILL_05d_重组审核流程.md | 并购重组委审核 |
| SKILL_05e_反馈回复撰写策略.md | 回复范式+质量自检 |
| SKILL_05f_审核进度追踪.md | 申报追踪表 |

### Stage 06: 发行执行
| 文件 | 内容 |
|------|------|
| SKILL_06_发行执行总览.md | 阶段总览 |
| SKILL_06a_IPO路演与定价.md | 投资故事+询价+Q&A |
| SKILL_06b_债券簿记建档.md | → 委托 bond-dcm-core |
| SKILL_06c_并购交割.md | 先决条件+过户+确认 |

### Stage 07: 存续期管理
| 文件 | 内容 |
|------|------|
| SKILL_07_存续期管理总览.md | 阶段总览 |
| SKILL_07a_IPO持续督导.md | 定期报告+募资核查 |
| SKILL_07b_债券受托管理.md | → 委托 bond-dcm-core |
| SKILL_07c_并购整合跟踪.md | 业绩承诺+减值测试 |

---

## 十、更新日志

### v1.6（2026-05-10）— META元技能层扩展

**新增内容**：
- 新增扩展META层文件6个（META-11~META-18）
  - META-11 投行项目生命周期管理模型（七阶段完整框架）
  - META-12 监管审核分析框架（三层规则金字塔）
  - META-13 风险定价决策模型（债券/股票/并购定价）
  - META-15 跨产品线协同工作法（三线复用+比选）
  - META-16 文件质量内控标准（三级审阅+五维评分）
  - META-17 中介机构协调方法论（选聘+分工+冲突）
  - META-18 AI辅助投行工作伦理准则（使用边界）
- 本文件（管线总览）扩展至500+行，新增：
  - 完整路由决策树（关键词→产品线→阶段→子技能）
  - 技能调用方法（含债券委托接口）
  - 按场景索引（10个常见场景及其技能组合）
  - 文件资产地图（references/scripts完整目录表）
  - 更新日志

**新增脚本**：
- ma_valuation_calc.py（并购估值计算）
- bond_default_early_warning.py（违约预警）
- bond_cashflow_cover.py（现金流覆盖分析）

### v1.5（2026-04-25）— 债券专项体系深化

**新增内容**：
- 新增META-05~META-08系列
- 新增债券尽调SKILL（SKILL_02_债券尽调.md）
- 新增城投债专项信用分析

**修改内容**：
- SKILL_00管线总览扩展至173行
- bond-product-matrix增至16品种
- bond-prospectus-detail逐章详解

### v1.4（2026-04-10）— 并购重组体系完善

**新增内容**：
- SKILL_03d/04c/05d/06c/07c 并购全流程文件
- references/ma/ 目录（3个参考文件）
- ma_valuation_calc.py

### v1.3（2026-03-20）— 债券委托体系建立

**新增内容**：
- bond-product-matrix（16品种对比）
- bond-router（关键词路由）
- credit-analysis-framework（五维信用分析）
- guarantee-chain-analysis（担保链分析）
- bond-filing-regulators（三套监管体系）
- bond-prospectus-detail（募集书详解）

### v1.2（2026-03-05）— IPO再融资全流程覆盖

**新增内容**：
- SKILL_03b/04a/05a/05b/06a/07a IPO全流程
- references/equity/ 目录（4个参考文件）
- ipo_board_check.py

### v1.1（2026-02-15）— 核心尽调体系建立

**新增内容**：
- SKILL_02a~02f 完整尽调文件
- SKILL_02_尽职调查总览
- references/shared/ 目录（尽调相关）
- dd_checklist_gen.py / dd_issue_tracker.py

### v1.0（2026-01-30）— 基础框架搭建

**初始内容**：
- SKILL_00 管线总览（173行）
- SKILL_01 项目启动系列
- SKILL_03/04/05/06/07 各阶段总览文件
- META-00 IB方法论总纲
- 基础脚本工具集

---

## 十一、快速导航

| 需求 | 查找位置 |
|------|----------|
| 不知道从哪开始 | 本文件第一章"七阶段管线" |
| 找具体某个文件 | 本文件第五章"阶段详细索引" |
| 找参考文件 | 本文件第八章"文件资产地图" |
| 找META方法论 | 本文件第四章"META技能索引" |
| 找工具脚本 | 本文件8.2节"Scripts目录" |
| 债券专项任务 | 本文件3.3节"债券路径" |
| 按场景找技能 | 本文件第七章"按场景索引" |

---

*版本：v1.6 | 最后更新：2026-05-10 | 投行承做技能体系*
