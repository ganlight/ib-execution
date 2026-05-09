---
name: ib-execution
version: 1.0
description: 投行承做全产品线技能。覆盖IPO（主板/科创板/创业板/北交所）、再融资（定增/配股/可转债）、债券（企业债/公司债/MTN/ABS/REITs等）、并购重组（换股吸收合并/重大资产重组/借壳上市）的全生命周期承做。触发场景：IPO承做、招股书撰写、尽职调查、再融资方案、并购重组、资产重组、估值建模、投行文件准备、监管申报、反馈回复、路演定价、持续督导、项目时间表、中介协调等。对债券类任务自动路由到债券专项技能体系。
---

# 投行承做技能 (ib-execution)

> 🚀 新用户？先看 [QUICK_START.md](QUICK_START.md) | 📇 文件索引见 [INDEX.md](INDEX.md)

## 产品线识别

| 产品线 | 关键词 | 路由 |
|--------|--------|------|
| 股权融资 | IPO、上市、招股书、路演、科创板、创业板、主板、北交所、定增、配股、可转债、再融资 | → equity 路径 |
| 债券融资 | 企业债、公司债、MTN、CP、SCP、PPN、ABS、REITs、债券、募集说明书 | → bond 路径（委托现有债券技能） |
| 并购重组 | 并购、重组、重大资产重组、借壳、换股、吸收合并、业绩承诺 | → ma 路径 |

## 快速路由

1. **新项目冷启动** → `skills/00-META/00-META-01_项目冷启动.md`
2. **尽调工作** → `skills/02_尽职调查/SKILL_02_尽职调查总览.md`
3. **写文件/招股书** → `skills/04_文件撰写/SKILL_04_文件撰写总览.md`
4. **监管反馈** → `skills/00-META/00-META-03_反馈回复模式库.md`
5. **项目时间表** → `skills/00-META/00-META-07_时间表管理.md`
6. **质量控制** → `skills/00-META/00-META-05_交叉校验质量控制.md`

## 详细路由决策树（按优先级匹配，命中即停）

### 1. 债券识别 → 委托现有技能
触发词：债券、企业债、公司债、金融债、ABS、REITs、中期票据、MTN、短期融资券、CP、SCP、超短融、定向工具、PPN、可转债、可交债、募集说明书、评级报告、收益率、久期、凸性、簿记建档、受托管理、信用利差、债券品种选择、债券定价

### 债券本技能内置资源（优先加载）
- **项目启动** → `skills/01_项目启动/SKILL_01_债券项目启动.md`（KYC+隐债筛查+评级预沟通+承销团组建+红色阻断10项）
- **债券尽调** → `skills/02_尽职调查/SKILL_02_债券尽调.md`（信用+担保增信+城投专项+ABS资产池+RAG三级）
- **品种选择** → `skills/03_方案设计/SKILL_03c_债券品种选择.md`（决策树+匹配矩阵+组合策略）
- **募集书撰写** → `skills/04_文件撰写/SKILL_04b_债券募集说明书.md`（逐章详解+审核意见+条款设计）
- **申报注册** → `skills/05_监管申报/SKILL_05c_债券申报注册.md`（三套注册体系+文件清单+时间窗口）
- **簿记建档** → `skills/06_发行执行/SKILL_06b_债券簿记建档.md`（日级全流程+定价方法+应急预案）
- **受托管理** → `skills/07_存续期管理/SKILL_07b_债券受托管理.md`（23项重大事项+持有人会议+风险处置）

### 债券参考文件
- `references/bond/bond-product-matrix.md` — 16品种全景对比矩阵
- `references/bond/credit-analysis-framework.md` — 五维信用分析框架（含城投/产业专项、30项财务比率）
- `references/bond/bond-filing-regulators.md` — 三套监管体系详解
- `references/bond/bond-router.md` — 关键词到子技能的路由映射
- `references/bond/abs-asset-pool-analysis.md` — ABS/REITs资产池尽调框架（影子评级+压力测试）
- `references/bond/guarantee-chain-analysis.md` — 担保增信分析框架（12种担保类型+抵押率上限）

### 债券自动化工具
- `scripts/bond_product_matcher.py` — 发行人画像→品种智能匹配（--test 含3个内置用例）
- `scripts/bond_pricing_calc.py` — 净价/全价/久期/凸性/现金流计算器
- `scripts/credit_spread_analyzer.py` — 信用利差分析与可比债券筛选（--test 含10支可比债券）
- `scripts/bond_cashflow_cover.py` — DSCR计算器+还款计划+敏感性分析（--test 含3个内置用例）
- `scripts/bond_filing_checklist.py` — 11品种申报文件清单+M/C/O状态跟踪（--test 含3个内置用例）

### 债券模板
- `assets/templates/bond_term_sheet.md` — 债券条款清单（11模块，全部占位符）
- `assets/templates/investor_q_and_a.md` — 投资者问答准备（25题结构化，含陷阱提示）
- `assets/templates/bond_roadshow_outline.md` — 债券路演材料提纲（9模块完整版）
- `assets/templates/bond_underwriting_checklist.md` — 债券承销协议勾选审核清单（10大模块）

### 债券委托已有技能（复杂分析时使用）
- 深度品种分析/市场惯例 → `bond-dcm-core` (`~/.qclaw/skills/bond-dcm-core/SKILL.md`)
- 尽调 → `bond-due-diligence` (`~/.qclaw/skills/bond-due-diligence/SKILL.md`)
- 深度文件撰写 → `bond-documenter` (`~/.qclaw/skills/bond-documenter/SKILL.md`)
- 复杂建模定价 → `bond-modeler` (`~/.qclaw/skills/bond-modeler/SKILL.md`)
- 全流程管理 → `ib-bond-executor` (`~/.qclaw/skills/ib-bond-executor/SKILL.md`)

债券任务也可叠加本技能的 META 方法论（META-02 迭代、META-03 反馈回复）。

### 2. 并购重组识别
触发词：并购、重组、重大资产重组、借壳上市、吸收合并、换股、收购、标的资产、业绩承诺、对赌、商誉、整合、交割

→ 读取 `skills/03_方案设计/SKILL_03d_并购重组方案.md`
→ 如涉及估值 → 读取 `skills/03_方案设计/SKILL_03e_财务建模.md`
→ 如涉及写文件 → 读取 `skills/04_文件撰写/SKILL_04c_重组报告书撰写.md`

### 3. 再融资识别
触发词：定增、定向增发、配股、公开增发、非公开发行、再融资、锁定期、发行底价、战投、认购对象

→ 读取 `skills/03_方案设计/SKILL_03b_再融资方案设计.md`
→ `references/equity/refinancing-rules.md`

### 4. IPO/上市识别
触发词：IPO、上市、首次公开发行、招股书、招股说明书、路演、科创板、创业板、主板、北交所、辅导、股改、上会、注册

→ 读取 `skills/03_方案设计/SKILL_03a_IPO方案设计.md`
→ `references/equity/ipo-board-conditions.md`

### 5. 尽职调查（跨产品通用）
触发词：尽调、DD、尽职调查、底稿、工作底稿、核查、核验、银行流水穿透

→ 读取 `skills/02_尽职调查/SKILL_02_尽职调查总览.md`

**核心参考文件：**
- `references/shared/qoe-analysis-framework.md` — 🆕 QOE质量盈利分析（U型调节法、Add-back清单）
- `references/shared/revenue-quality-analysis.md` — 🆕 收入质量深度分析（四象限矩阵、10分制）
- `references/shared/dd-redflag-industry-library.md` — 🆕 各行业红旗库（6大行业、51种模式）
- `references/shared/management-interview-guide.md` — 🆕 管理层访谈指引（7类提纲）
- `references/shared/site-inspection-procedures.md` — 🆕 现场盘点程序（监盘八步法）
- `references/shared/dd-filing-standards.md` — 🆕 底稿归档标准（DD-01~DD-07）

**尽调脚本工具：**
- `scripts/dd_checklist_gen.py` — 按项目类型生成核查清单
- `scripts/dd_issue_tracker.py` — 🆕 尽调问题追踪（RED/AMBER/GREEN三级、6个CLI命令）

### 6. 文件撰写识别
触发词：写招股书、撰写、募集说明书、重组报告书、法律意见、审计报告核查

→ 识别产品线 → 加载对应 SKILL_04a/b/c/d/e

### 7. 监管反馈识别（跨产品通用）
触发词：反馈、问询、审核意见、回复、申报、提交、受理、注册

→ 读取 `skills/00-META/00-META-03_反馈回复模式库.md`
→ 读取 `skills/05_监管申报/SKILL_05e_反馈回复撰写策略.md`

### 8. 项目管理识别（跨产品通用）
触发词：时间表、进度、里程碑、甘特图、项目计划、中介协调

→ 读取 `skills/00-META/00-META-07_时间表管理.md`
→ 如需协调 → `skills/00-META/00-META-06_中介机构协调.md`

### 9. 通用方法论
触发词：冷启动、新项目、怎么做、质量控制、检查

→ 加载 META-00 总纲 或 META-01 冷启动

### Fallback
如果无法识别 → 加载 `skills/SKILL_00_管线总览.md` + `skills/00-META/00-META-00_IB方法论总纲.md`

## 管线总览

参见 `skills/SKILL_00_管线总览.md`

---

## HOW TO USE — 直接对 QClaw 说的话

不需要记文件名。用自然语言描述任务，主入口自动路由：

### 💡 新项目
```
"帮我评估一下这家公司：营收5亿，3年净利润累计8000万，
行业是半导体设备，有12项发明专利，研发投入占比8%，
看能上哪个板块"
```
→ 自动加载 ipo-board-conditions.md + SKILL_03a + ipo_board_check.py

### 💡 启动尽调
```
"启动XX公司的IPO尽调，先从财务入手，
公司去年营收3.2亿，毛利率35%，应收账款1.1亿"
```
→ 自动加载 SKILL_02 + SKILL_02b + dd_checklist_gen.py

### 💡 写招股书
```
"帮我写XX公司招股书的业务与技术章节（第五章），
公司做工业机器人，国内市占率12%，有5项核心技术"
```
→ 自动加载 SKILL_04a + prospectus-sections.md + META-04

### 💡 收到问询
```
"交易所给了反馈，38条问题，帮我分类整理，
先看收入和毛利率相关的问题怎么回复"
```
→ 自动加载 META-03 + SKILL_05e + regulatory-feedback-patterns.md

### 💡 排时间表
```
"这个IPO项目准备上科创板，帮我排一个完整时间表，
现在改制刚开始，审计进场第2周"
```
→ 自动加载 META-07 + ipo-timeline.md + timeline_gen.py

### 💡 并购方案
```
"客户想收购一家做工业软件的公司，标的一年营收8000万，
净利润1200万，总资产1.5亿，客户自己总资产8亿，营收5亿"
```
→ 自动加载 SKILL_03d + restructuring-standards.md + valuation-methods.md

### 💡 发债（内置资源+工具）
```
"客户是AA+评级城投，想发行中期票据，5年期，规模10亿，
请选择合适的注册机构和品种"
```
→ 自动加载 SKILL_03c（决策树+匹配矩阵）+ bond-product-matrix.md

```
"帮我匹配一下：央企AAA，资产500亿，收入200亿，利润50亿，
想发30亿5年期项目债"
```
→ 加载 SKILL_03c + 运行 bond_product_matcher.py

```
"计算这支3年期债券的全价和久期，票面4.2%，YTM 3.9%"
```
→ 加载 SKILL_06b + 运行 bond_pricing_calc.py

```
"分析10支可比券信用利差，对标3年期国债2.85%"
```
→ 加载 credit-analysis-framework.md + credit_spread_analyzer.py --test

```
"这支MTN的受托管理年度工作怎么做？"
```
→ 加载 SKILL_07b（23项重大事项监控+月度工作日历）

### 💡 质量控制
```
"检查一下这份招股书的交叉引用数据是否一致"
```
→ 自动加载 META-05 + cross_ref_check.py

---

## Token 预算原则

⚠️ 不要一次性加载全部文件。主入口 SKILL.md 很轻，场景按需加载：

| 场景 | 加载文件 | 预估 tokens |
|------|---------|------------|
| 新项目冷启动 | META-01 + 板块条件 + 时间表 | ~3,500 |
| 尽调启动 | SKILL_02总览 + 子技能(1-2个) | ~4,000 |
| 写招股书 | SKILL_04a + ref + META-04 | ~4,500 |
| 反馈回复 | META-03 + SKILL_05e + ref | ~4,500 |
| 项目管理 | META-06 + META-07 | ~3,000 |

💡 进阶路线：先用场景1-3（IPO核心流程），再加并购（场景5），最后深入META方法论

## 现有技能整合

本技能覆盖股权和并购的全生命周期。债券线拥有完整的内置资源（5阶段文件+4参考+3脚本+2模板），复杂场景委托已有专项技能：
- `bond-dcm-core`: 深度品种分析、市场惯例参考
- `bond-due-diligence`: 债券尽调
- `bond-documenter`: 深度债券发行文件撰写指导
- `bond-modeler`: 债券建模与定价
- `ib-bond-executor`: 债券项目执行总入口

## Token 预算

每个场景只加载所需文件，预估：
- 新项目冷启动：~3,500 tokens
- 尽调阶段：~4,000 tokens
- 写招股书：~5,000 tokens
- 反馈回复：~4,500 tokens
- 债券品种匹配：~3,000 tokens
- 债券定价分析：~1,500 tokens（直接调用脚本）
- 债券受托管理：~3,500 tokens