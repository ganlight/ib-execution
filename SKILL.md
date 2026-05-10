---
name: ib-execution
version: 2.0
description: 投行承做全产品线技能。覆盖债券（企业债/公司债/MTN/CP/ABS/REITs等）、ABS（信贷/企业/ABN）、股权（IPO/再融资/并购重组）三线七阶段全生命周期。触发场景：债券发行、ABS融资、IPO上市、定增配股、并购重组、尽职调查、文件撰写、监管申报、反馈回复、路演定价、存续期管理。
---

# 投行承做技能 (ib-execution) v2.0

> 三线入口 · 七阶段管线 · 按需路由

## ⚡ 快速路由地图

```
用户任务
  │
  ├── 债券类 → skills/bond/SKILL.md  ──→ 7阶段子路由
  ├── ABS类  → skills/abs/SKILL.md   ──→ 7阶段子路由
  └── 股权类 → skills/equity/SKILL.md ──→ IPO / 再融资 / 并购 三子线
```

| 任务类型 | 子入口 | 适用场景 |
|---------|--------|---------|
| 债券发行（企业债/公司债/MTN/CP/PPN等） | `skills/bond/SKILL.md` | 发债启动、尽调、品种选择、募集书、申报、簿记、受托 |
| ABS融资（信贷/企业/ABN） | `skills/abs/SKILL.md` | 资产池分析、交易结构、计划说明书、存续期 |
| 股权（IPO/再融资/并购） | `skills/equity/SKILL.md` | 上市评估、尽调启动、招股书、反馈回复、再融资方案、并购交割 |
| 跨产品线通用（META方法论） | `skills/00-META/*.md` | 冷启动、文件迭代、反馈回复、质量控制、时间表、中介协调 |
| 无法判断产品线 | 加载本文件 + `skills/SKILL_00_管线总览.md` | 综合评估 |

---

## 第一部分：产品线快速路由（三线七阶段）

### 🟡 债券线 → `skills/bond/`

```
触发词：企业债、公司债、债券、MTN、短期融资券、CP、SCP、超短融、定向工具、PPN、
       永续债、绿债、可转债、可交债、金融债、城投债、募集说明书、评级报告、
       簿记建档、受托管理、信用利差、隐债、债券定价、债券品种、债券尽调、
       债券申报、债券发行

skills/bond/ 路由：
  01_项目启动/SKILL_01_债券项目启动.md
  02_尽职调查/SKILL_02_债券尽调.md
  03_方案设计/SKILL_03_债券品种选择.md
  04_文件撰写/SKILL_04_债券募集说明书.md
  05_监管申报/SKILL_05_债券申报注册.md
  06_发行执行/SKILL_06_债券簿记建档.md
  07_存续期管理/SKILL_07_债券受托管理.md
```

### 🔵 ABS线 → `skills/abs/`

```
触发词：ABS、资产支持证券、资产证券化、ABN、资产支持票据、CMBS、类REITs、
       住房抵押贷款证券化、信贷资产证券化、企业ABS、银行ABS、交易所ABS、
       供应链ABS、应收账款ABS、融资租赁ABS、门票收入ABS、收费权ABS、
       资产池、计划说明书、专项计划、特殊目的载体SPV、信用增级、内部增信、
       外部增信、超额抵押、优先级/次级分层、现金流归集

skills/abs/ 路由：
  01_项目启动/SKILL_01_ABS项目启动.md
  02_尽职调查/SKILL_02_ABS尽调.md
  03_方案设计/SKILL_03_ABS方案设计.md
  04_文件撰写/SKILL_04_ABS计划说明书.md
  05_监管申报/SKILL_05_ABS申报.md
  06_发行执行/SKILL_06_ABS发行.md
  07_存续期管理/SKILL_07_ABS存续.md
```

### 🟢 股权线 → `skills/equity/`

```
触发词：IPO、上市、招股书、路演、科创板、创业板、主板、北交所、定增、配股、
       可转债、再融资、并购、重组、重大资产重组、借壳上市、换股吸收合并、
       辅导、股改、上会、注册、发行审核委、发审委、重组委、问询函、反馈意见

skills/equity/ 路由：
  01_项目启动/SKILL_01_项目启动.md
  02_尽职调查/SKILL_00_尽调总览.md
  03_方案设计/SKILL_00_方案总览.md  ← 分发至 SKILL_03a_IPO方案 / SKILL_03b_再融资方案 / SKILL_03c_并购重组
  04_文件撰写/SKILL_00_撰写总览.md  ← 分发至 SKILL_04a_招股书 / SKILL_04b_重组报告书
  05_监管申报/SKILL_00_申报总览.md   ← 分发至 SKILL_05a_IPO材料 / SKILL_05c_重组审核
  06_发行执行/SKILL_00_发行总览.md  ← 分发至 SKILL_06a_IPO路演 / SKILL_06b_并购交割
  07_存续期管理/SKILL_00_存续总览.md ← 分发至 SKILL_07a_IPO督导 / SKILL_07b_并购整合
```

---

## 第二部分：详细路由决策树（9类关键词 → 产品线 → 阶段 → 文件）

### 1. 债券识别（60+关键词）→ `bond` 线

**核心关键词**：债券、企业债、公司债、金融债、城投债、MTN、中期票据、短期融资券、CP、SCP、超短融、定向工具、PPN、永续债、可转债、可交债、绿色债券、碳中和债、蓝色债券、乡村振兴债、保障性住房债、项目收益债

**结构关键词**：募集说明书、评级报告、信用评级、隐债筛查、隐债、债券定价、久期、凸性、票面利率、发行利率、信用利差、簿记建档、建档发行、招标发行、承销团、主承销商联席主承销、联席主承、受托管理人、持有人会议、提前偿还、回售条款、赎回条款、担保增信、抵押质押、信用缓释工具CRMW、CRMA

**市场关键词**：银行间市场、交易所、NAFMII、交易商协会、证监会、发改委、企业债审批、公司债注册、ABS挂牌

**品种细分关键词**：CMBS、类REITs → ABS 线（见下）

---

### 2. ABS识别（30+关键词）→ `abs` 线

**核心关键词**：ABS、资产支持证券、资产证券化、资产支持票据 ABN、资产支持专项计划、SPV、特殊目的载体、基础资产、资产池

**基础资产类型**：信贷资产（RMBS/CLO/CAR/CSUSA）、企业债权（应收账款/租赁/保理/小贷）、收费权（门票/公路/水电/学费）、类REITs/CMBS、不动产抵押贷款、供应链

**结构设计关键词**：分层结构、优先级证券、次级证券、超额抵押、折价发行、现金流归集、循环购买、结构分层、内部增信、外部增信、信用触发、权利完善事件、资产替换

**文件关键词**：计划说明书、计划管理报告、托管报告、资产服务报告、清算报告

---

### 3. 股权IPO识别（40+关键词）→ `equity` 线（子线A）

**核心关键词**：IPO、首次公开发行、上市、招股书、招股说明书、主板上市、科创板上市、创业板上市、北交所上市

**审核关键词**：辅导备案、辅导验收、股改、改制设立股份公司、发行审核、注册生效、上会、发审会、上市委、创业板委、科创板委、受理、补正材料

**板块关键词**：主板（主板上市条件）、科创板（科创属性评价、研发投入、发明专利、市值/营收/研发指标）、创业板（三创四新、第二套上市标准、成长型创新创业）、北交所（专精特新、北交所上市条件）

**申报关键词**：申报文件、审核材料、问询函、审核问询、落实审核意见、补充材料、预先披露

---

### 4. 再融资识别（20+关键词）→ `equity` 线（子线B）

**核心关键词**：定增、定向增发、非公开发行、配股、公开增发、可转债（股权）、优先股、上市公司再融资

**竞价/定价关键词**：竞价发行、锁价发行、发行底价、基准日前20日均价、战投、战略投资者、认购对象、特定对象

**规则关键词**：再融资新规、18个月间隔、融资规模限制、创业板定增放开

---

### 5. 并购重组识别（30+关键词）→ `equity` 线（子线C）

**重组类型关键词**：并购、重大资产重组、借壳上市、买壳上市、换股吸收合并、定增并购、发行股份购买资产、现金收购、协议收购、要约收购

**交易结构关键词**：标的资产、交易对方、业绩承诺、对赌条款、业绩补偿、估值调整、三年承诺、股权交割、资产过户、交割审计

**审核关键词**：并购重组委、重组委审核、重组报告书、重大资产重组管理办法

---

### 6. 尽职调查（通用）→ 按产品线分发

**通用关键词**：尽调、尽职调查、DD、工作底稿、底稿、银行流水穿透、函证核实、现场盘点、监盘、访谈、核查验证

**分发规则**：
- 债券尽调 → `skills/bond/02_尽职调查/SKILL_02_债券尽调.md`
- ABS尽调 → `skills/abs/02_尽职调查/SKILL_02_ABS尽调.md`
- 股权尽调 → `skills/equity/02_尽职调查/SKILL_00_尽调总览.md` → 再分发至法律/财务/业务

---

### 7. 文件撰写（通用）→ 按产品线分发

**分发规则**：
- 债券募集说明书 → `skills/bond/04_文件撰写/SKILL_04_债券募集说明书.md`
- ABS计划说明书 → `skills/abs/04_文件撰写/SKILL_04_ABS计划说明书.md`
- 招股说明书 → `skills/equity/04_文件撰写/SKILL_04a_招股书.md`
- 重组报告书 → `skills/equity/04_文件撰写/SKILL_04b_重组报告书.md`
- 法律意见书 → `skills/equity/04_文件撰写/SKILL_04c_法律意见书.md`
- 审计报告核查 → `skills/equity/04_文件撰写/SKILL_04d_审计报告.md`

---

### 8. 监管反馈（通用）→ 按产品线分发

**分发规则**：
- 债券反馈（交易商协会/发改委反馈）→ `skills/bond/05_监管申报/SKILL_05_债券申报注册.md`
- ABS反馈（交易所/银登反馈）→ `skills/abs/05_监管申报/SKILL_05_ABS申报.md`
- IPO反馈（问询函）→ `skills/equity/05_监管申报/SKILL_05a_IPO材料清单.md` + `SKILL_05b_IPO审核流程.md`
- 重组反馈 → `skills/equity/05_监管申报/SKILL_05c_重组审核.md`

---

### 9. 项目管理/质量控制 → `00-META/`

**META路由**：
- 新项目冷启动 → `00-META-01_项目冷启动.md`
- 文件迭代管理 → `00-META-02_文件迭代工作流.md`
- 反馈问询回复 → `00-META-03_反馈回复模式库.md`
- AI辅助混合工作 → `00-META-04_柳叶刀混合工作法.md`
- 交叉校验质量控制 → `00-META-05_交叉校验质量控制.md`
- 中介机构协调 → `00-META-06_中介机构协调.md`
- 时间表管理 → `00-META-07_时间表管理.md`
- 技能优化演化 → `00-META-08_SKILL优化与演化.md`
- 全生命周期 → `00-META-11_投行项目生命周期管理模型.md`
- 监管审核分析 → `00-META-12_监管审核分析框架.md`
- 风险定价决策 → `00-META-13_风险定价决策模型.md`
- 跨产品线协同 → `00-META-15_跨产品线协同工作法.md`
- 文件质量内控 → `00-META-16_文件质量内控标准.md`

---

## 第三部分：HOW TO USE — 10个场景自然语言路由示例

### 场景1：债券发债
> "客户想发行中期票据，AA+城投，5年期，10亿规模，怎么选品种和注册机构？"

```
识别：债券 + MTN + 品种选择 + 申报注册
路由：skills/bond/SKILL.md → 03_方案设计/SKILL_03_债券品种选择.md
参考：references/bond/bond-product-matrix.md + bond-filing-regulators.md
工具：scripts/bond_product_matcher.py（--test）
```

---

### 场景2：ABS融资
> "帮我们设计一个供应链ABS，应收账款5亿，评级要AA+，怎么搭结构？"

```
识别：ABS + 供应链 + 结构设计
路由：skills/abs/SKILL.md → 03_方案设计/SKILL_03_ABS方案设计.md
参考：references/bond/abs-asset-pool-analysis.md
工具：scripts/bond_cashflow_cover.py
```

---

### 场景3：IPO上市
> "某半导体设备公司，营收8亿，净利润1.2亿，发明专利20项，适合上哪个板块？"

```
识别：IPO + 板块选择
路由：skills/equity/SKILL.md → 03_方案设计/SKILL_03a_IPO方案.md
参考：references/equity/ipo-board-conditions.md
工具：scripts/ipo_board_check.py
```

---

### 场景4：再融资
> "上市公司想做定增，募资12亿收购标的，标的净资产2亿，怎么设计发行方案？"

```
识别：定增 + 再融资 + 发行方案
路由：skills/equity/SKILL.md → 03_方案设计/SKILL_03b_再融资方案.md
参考：references/equity/refinancing-rules.md
```

---

### 场景5：并购重组
> "上市公司想换股吸收合并一家工业软件公司，标的营收8000万，估值怎么定？"

```
识别：并购 + 重组 + 换股 + 估值
路由：skills/equity/SKILL.md → 03_方案设计/SKILL_03c_并购重组.md
参考：references/ma/valuation-methods.md + restructuring-standards.md
工具：scripts/ma_valuation_calc.py
```

---

### 场景6：尽职调查
> "启动一个债券项目的尽调，发行人是县级城投，有隐债压力，怎么开展尽调？"

```
识别：债券 + 尽调 + 城投
路由：skills/bond/SKILL.md → 02_尽职调查/SKILL_02_债券尽调.md
参考：references/bond/urban-bond-credit-analysis.md + references/shared/dd-redflag-industry-library.md
工具：scripts/dd_checklist_gen.py + dd_issue_tracker.py
META：00-META-05_交叉校验质量控制.md
```

---

### 场景7：募集说明书撰写
> "帮我写XX公司债券募集说明书的第一章和第二章，公司做高速公路运营"

```
识别：债券 + 募集书 + 文件撰写
路由：skills/bond/SKILL.md → 04_文件撰写/SKILL_04_债券募集说明书.md
参考：references/bond/bond-prospectus-detail.md
META：00-META-02_文件迭代工作流.md + 00-META-16_文件质量内控标准.md
```

---

### 场景8：监管反馈回复
> "交易商协会给了反馈意见，12条问题，主要是财务数据和担保披露问题，怎么回复？"

```
识别：债券 + 反馈 + 申报
路由：skills/bond/SKILL.md → 05_监管申报/SKILL_05_债券申报注册.md
META：00-META-03_反馈回复模式库.md + 00-META-12_监管审核分析框架.md
参考：references/shared/regulatory-feedback-patterns.md
工具：scripts/filing_tracker.py
```

---

### 场景9：项目管理
> "这个IPO项目准备上科创板，审计已进场两周，帮排一个完整时间表"

```
识别：IPO + 时间表 + 项目管理
路由：skills/equity/SKILL.md → 07_存续期管理/SKILL_00_存续总览.md（参考ipo-timeline）
META：00-META-07_时间表管理.md + 00-META-11_投行项目生命周期管理模型.md
参考：references/equity/ipo-timeline.md
工具：scripts/timeline_gen.py
```

---

### 场景10：质量控制
> "检查一下这份招股书和审计报告之间的财务数据交叉引用是否一致"

```
识别：质量控制 + 交叉引用 + IPO文件
路由：META：00-META-05_交叉校验质量控制.md + 00-META-16_文件质量内控标准.md
参考：references/shared/document-cross-ref.md
工具：scripts/cross_ref_check.py + scripts/doc_version_diff.py
```

---

## 第四部分：Token 预算原则（按产品线分表）

⚠️ 原则：主入口保持轻量（<5,000 tokens），场景按需加载子技能。

### 债券线 Token 预算

| 场景 | 加载文件 | 预估 tokens |
|------|---------|------------|
| 债券品种选择 | bond/SKILL.md + 03_方案设计 + ref | ~4,000 |
| 债券尽调启动 | bond/SKILL.md + 02_尽调 + ref | ~5,000 |
| 募集说明书撰写 | bond/SKILL.md + 04_文件撰写 + ref | ~6,000 |
| 债券申报注册 | bond/SKILL.md + 05_申报 + ref | ~4,500 |
| 债券定价计算 | bond/SKILL.md + 06_发行 + bond-modeler | ~3,000 |
| 债券受托管理 | bond/SKILL.md + 07_存续 | ~3,500 |
| 债券尽调+建模联合 | bond线 + bond-dcm-core + bond-modeler | ~8,000 |

### ABS线 Token 预算

| 场景 | 加载文件 | 预估 tokens |
|------|---------|------------|
| ABS方案设计 | abs/SKILL.md + 03_方案设计 + ref | ~5,000 |
| ABS尽调 | abs/SKILL.md + 02_尽调 + abs-asset-pool + ref | ~5,500 |
| ABS计划说明书撰写 | abs/SKILL.md + 04_文件撰写 + ref | ~6,000 |
| ABS申报 | abs/SKILL.md + 05_申报 | ~4,000 |
| ABS发行 | abs/SKILL.md + 06_发行 + abs线 | ~4,000 |

### 股权线 Token 预算

| 场景 | 加载文件 | 预估 tokens |
|------|---------|------------|
| IPO冷启动评估 | equity/SKILL.md + 01_启动 + ref + ipo_board_check | ~4,500 |
| IPO尽调 | equity/SKILL.md + 02_尽调 + ref | ~6,000 |
| 招股书撰写 | equity/SKILL.md + 04_撰写 + SKILL_04a + ref | ~7,000 |
| IPO反馈回复 | equity/SKILL.md + 05_申报 + SKILL_05b + META-03 | ~5,500 |
| 再融资方案 | equity/SKILL.md + 03_方案 + SKILL_03b + ref | ~4,500 |
| 并购方案 | equity/SKILL.md + 03_方案 + SKILL_03c + ma refs | ~6,000 |
| 交割执行 | equity/SKILL.md + 06_发行 + SKILL_06b | ~3,500 |

### 跨产品线 META 预算

| 场景 | 加载文件 | 预估 tokens |
|------|---------|------------|
| 新项目冷启动 | META-01 + META-11 | ~3,500 |
| 文件迭代管理 | META-02 + META-16 | ~3,000 |
| 反馈回复 | META-03 + META-12 | ~4,000 |
| 质量控制 | META-05 + META-16 | ~3,000 |
| 时间表管理 | META-07 + META-11 | ~3,500 |
| 跨产品协同 | META-15 | ~2,500 |

---

## 第五部分：跨产品线共享资源

### META 元技能（16个，三线通用）

```
skills/00-META/
  00-META-01_项目冷启动.md         新项目五步法
  00-META-02_文件迭代工作流.md      初稿→内核→申报→反馈→定稿
  00-META-03_反馈回复模式库.md      八大类监管问询回复范式
  00-META-04_柳叶刀混合工作法.md    LLM+模板+脚本+人工分工
  00-META-05_交叉校验质量控制.md    文件间数据一致性+Lint规则
  00-META-06_中介机构协调.md        四中介分工矩阵+时间衔接
  00-META-07_时间表管理.md          里程碑+关键路径+风险预警
  00-META-08_SKILL优化与演化.md     从项目持续学习进化
  00-META-11_投行项目生命周期管理模型.md  七阶段完整生命周期
  00-META-12_监管审核分析框架.md    三层规则金字塔+反馈回复方法论
  00-META-13_风险定价决策模型.md    债券/股票/并购定价决策
  00-META-15_跨产品线协同工作法.md  三线资源复用+方案比选
  00-META-16_文件质量内控标准.md    三级审阅体系+五维评分卡
  00-META-17_中介机构协调方法论.md  中介选聘+分工+冲突管理
  00-META-18_AI辅助投行工作伦理准则.md AI使用边界+保密+披露
```

### 共享参考文件（references/shared/）

```
references/shared/
  dd-checklist-master.md           尽调总清单（通用）
  dd-filing-standards.md            底稿归档标准（DD-01~DD-07）
  dd-redflag-industry-library.md    各行业红旗库（6大行业，51种模式）
  dd_report_template.md             尽调报告模板
  document-cross-ref.md             文件交叉引用关系图
  intermediary-roles.md             中介角色分工矩阵
  management-interview-guide.md      管理层访谈指南（7类提纲）
  qoe-analysis-framework.md         QOE质量盈利分析（U型调节法）
  regulatory-feedback-patterns.md   反馈模式库数据
  revenue-quality-analysis.md       收入质量分析（四象限矩阵）
  site-inspection-procedures.md     实地走访程序（监盘八步法）
```

### 质量/合规参考（references/compliance/）

```
references/compliance/
  related-party-rules.md            关联交易规则（IPO/重组）
  independence-rules.md             独立性规则（IPO/债券）
  materiality-thresholds.md         重大性判断标准（全线）
```

---

## 第六部分：专项技能委托接口

债券/ABS线任务涉及以下专项技能时，委托至独立技能：

| 任务类型 | 委托目标 | 说明 |
|---------|---------|------|
| 债券深度品种分析 | `bond-dcm-core` | 监管框架、市场惯例、发行条件 |
| 债券尽调 | `bond-due-diligence` | 法律/财务/业务DD全清单 |
| 债券募集说明书深度撰写 | `bond-documenter` | 逐章详解、内容要点、常见错误 |
| 债券建模定价 | `bond-modeler` | 收益率、久期、凸性、YTM敏感性 |
| 债券全流程管理 | `ib-bond-executor` | 债券项目执行总入口 |
| ABS品种/结构咨询 | `abs-asset-pool-analysis` | 资产池分析（reference文件） |

---

## 第七部分：自动化脚本索引（全线通用）

```
scripts/
  bond_pricing_calc.py          债券定价：全价/净价/久期/凸性/YTM
  bond_product_matcher.py       品种匹配：发行人画像→候选品种
  bond_filing_checklist.py      申报清单：11品种文件清单+M/C/O跟踪
  credit_spread_analyzer.py     信用利差：可比债券筛选+利差估算
  bond_cashflow_cover.py        现金流覆盖：DSCR+还款计划+敏感性
  bond_default_early_warning.py 违约预警：财务数据→预警信号
  bond_stress_test.py           压力测试：多情景敏感性分析
  dd_checklist_gen.py           尽调清单：按类型+行业生成
  dd_issue_tracker.py           问题追踪：RED/AMBER/GREEN三级
  cross_ref_check.py            交叉引用核查：文件间数据一致性
  doc_version_diff.py           版本对比：两版本文件差异报告
  filing_tracker.py             审核进度：申报状态可视化追踪
  financial_ratio_calc.py       财务比率：完整比率表
  ipo_board_check.py            板块条件核查：各板块符合性
  ma_valuation_calc.py          并购估值：DCF/可比/敏感性
  timeline_gen.py               时间表生成：里程碑甘特图
  bond_rating_template.py       评级报告模板
```

---

## Fallback 规则

> 无法确定产品线时，加载以下组合：

```
skills/SKILL_00_管线总览.md   三线七阶段全景图
skills/00-META-01_项目冷启动.md  新项目五步法
```

---

## 版本说明

本文件（v2.0）为三线重组后的主入口，重写了完整路由决策树和Token预算体系。
- v1.x（2026-01~2026-04）：股权/债券/并购三线并行，债券委托bond专项技能
- **v2.0（2026-05）：三线七阶段独立路由（bond/abs/equity），ABS线新增，META层完善**

# v2.0 三线重组 | 2026-05
