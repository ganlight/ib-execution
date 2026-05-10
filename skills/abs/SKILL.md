---
name: ib-execution-abs
version: 2.0
description: ABS线子入口。覆盖三大市场（信贷ABS/企业ABS/ABN）+七大基础资产类型（应收账款/租赁/消费金融/CMBS/类REITs/收费权/基础设施公募REITs）的全生命周期。含资产池分析、交易结构设计、增信方案、计划说明书撰写、存续期管理。
---

# ABS线技能入口 (ABS Sub-Entry)

> 资产证券化七阶段管线 · 三大市场 · 独立路由

## 一、ABS产品线总览

### 三大市场

| 市场 | 监管机构 | 挂牌场所 | 审批方式 | 主流品种 |
|------|---------|---------|---------|---------|
| 信贷ABS | 央行+银保监 | 银行间 | 注册制（银登中心） | 住房抵押RMBS/Auto/CLO/CAR |
| 企业ABS | 证监会 | 交易所+报价系统 | 管理人报告备案 | 应收账款/租金/CMBS/消费金融 |
| 资产支持票据(ABN) | 交易商协会 | 银行间 | 注册制（NAFMII） | 租金/票据/CMBN |

### 七大基础资产类型

| 类型 | 资产特征 | 风控重点 | 典型期限 | 市场 |
|------|---------|---------|---------|------|
| 应收账款 | 账期明确、债务人集中 | 回款率、集中度、账龄 | 1-3年 | 企业ABS/ABN |
| 融资租赁 | 租金分批到账、设备抵押 | 出表条件、现金流配置 | 3-5年 | 企业ABS/ABN |
| 消费金融 | 借款小而多、利率高 | 违约率、迁徙率、梯度结构 | 1-3年 | 信贷ABS/企业ABS |
| CMBS | 商业不动产抵押贷款 | 运营净收入NOI、偿债覆盖比DSCR | 12-18年 | 企业ABS/ABN |
| 类REITs | 特定物业的持有+营运营 | 物业评估、租赁合同稳定 | 5-10年 | 企业ABS/ABN |
| 收费权（门票、公路、水电） | 经营稳定、现金持续 | 运营维护成本、地区政策 | 5-10年 | 企业ABS/ABN |
| REITs(公募) | 基础设施的所有权+运营 | 目标回报率、税务递延 | 长期 | 公募REITs |

---

## 二、七阶段快速路由

### Stage 01：项目启动
```
技能文件：01_项目启动/SKILL_01_ABS项目启动.md
  ├─ 客户/原始权益人KYC
  ├─ 原始权益人资产基础扫描（识别基础资产类型）
  ├─ 初步交易意向规模评估
  ├─ 评级预定沟通（ABS评级 = 基础资产 = 原始权益人/发行人信用）
  └─ 红色阻断清单（资产无独立现金流/债务人极度集中/不合规的转让）

关键参考：
  references/bond/abs-asset-pool-analysis.md  — ABS资产池尽调框架
  references/shared/intermediary-roles.md      — 中介角色分工

META叠加：
  00-META-01_项目冷启动.md — 新项目五步法
```

---

### Stage 02：尽职调查
```
技能文件：02_尽职调查/SKILL_02_ABS尽调.md
  ├─ 基础资产池分析（影子评级+压力测试+集中度分析）
  ├─ 原始权益人主体信用DD（法律+财务+业务老三样扩展）
  ├─ 资产转让法律有效性核查（《信托法》/资产交割标准）
  ├─ 资产管理与服务能力（运营报告/服务协议/管理费）
  └─ RAG三级问题追踪+闭环整改

关键参考：
  references/bond/abs-asset-pool-analysis.md  — 资产池分析（影子评级+MECE切割+分层测试）
  references/bond/guarantee-chain-analysis.md  — 增信+担保链
  references/shared/qoe-analysis-framework.md  — 收入质量分析
  references/shared/revenue-quality-analysis.md — 收入深度分析
  references/shared/dd-redflag-industry-library.md — 行业风险库

脚本工具：
  scripts/dd_checklist_gen.py      — 按ABS类型生成DD清单
  scripts/financial_ratio_calc.py   — 基础现金流比率
  scripts/bond_stress_test.py        — 多情景压力测试
  scripts/bond_cashflow_cover.py     — DSCR/还款覆盖比

META叠加：
  00-META-05_交叉校验质量控制.md  — 资产池数据与运营报告的交叉验证
```

---

### Stage 03：方案设计
```
技能文件：03_方案设计/SKILL_03_ABS方案设计.md
  ├─ 交易结构方案（破产隔离结构、出表的二层SPV方案）
  ├─ 分层结构设计（A级/B级/次级×各档规模比例×利率基线）
  ├─ 信用增级方案（内部增信：超额抵押+折价发行+消费回补结构；
  │                    外部增信：担保/保险/信用证 3维对比）
  ├─ 循环购买与资产替换机制设定
  └─ 关键参考条款表（含4种标准级别 102条）

关键参考：
  references/bond/abs-asset-pool-analysis.md    — 影子评级与覆盖测试
  references/ma/deal-structures.md              — 交易结构类型库
  references/compliance/related-party-rules.md   — 关联交易

脚本工具：
  scripts/bond_cashflow_cover.py  — 动态分层覆盖结果

META叠加：
  00-META-15_跨产品线协同工作法.md — ABS+贷款比选
```

---

### Stage 04：文件撰写（计划说明书）
```
技能文件：04_文件撰写/SKILL_04_ABS计划说明书.md
  ├─ 标准计划说明书章节结构（15章，含评级/托管/主要风险提示/交易流程图）
  ├─ 各基础资产类型差异化条款（7种基础详参）
  ├─ 法律意见书+审计报告附加限制
  └─ 审核常见反馈清单（逾30项定量+定性检查点）

关键参考：
  references/shared/document-cross-ref.md  — 文件交叉引用图
  references/shared/dd_report_template.md  — ABS专项报告模板

META叠加：
  00-META-02_文件迭代工作流.md      — P0→提交版V3
  00-META-16_文件质量内控标准.md     — 三级审阅+评分卡
```

---

### Stage 05：监管申报
```
技能文件：05_监管申报/SKILL_05_ABS申报.md
  ├─ 信贷ABS申报流程（CBIRC+银登中心 → 央行注册证书）
  ├─ 企业ABS挂牌流程（管理人→交易所 20-30天→回复反馈）
  ├─ ABN注册流程（NAFMII注册 → 银行间上市）
  └─ 各品种申报文件一体化清单

META叠加：
  00-META-03_反馈回复模式库.md
  00-META-12_监管审核分析框架.md

参考：
  references/bond/bond-filing-regulators.md — 扩展对比
  references/shared/regulatory-feedback-patterns.md
```

---

### Stage 06：发行执行
```
技能文件：06_发行执行/SKILL_06_ABS发行.md
  ├─ 簿记建档全流程（T-7至T日详细操作手册）
  ├─ 询价与ABP(X)/CP系列等定价方法
  ├─ 投资者认购风控（优先级上限+次级X锁定）
  └─ 应急方案（舍弃某一档→重新切割→补后续+投放利率上限调整）

脚本工具：
  scripts/credit_spread_analyzer.py — 基础比照定价

META叠加：
  00-META-13_风险定价决策模型.md — 分层利率定价
```

---

### Stage 07：存续期管理
```
技能文件：07_存续期管理/SKILL_07_ABS存续.md
  ├─ 动态资产池监控（循环购买、资产替换、提前清偿触发检测）
  ├─ 月度/季度管理人报告编制
  ├─ 清算条件触发响应（确定型/后置敞口/管理层自主）
  └─ 持有人会议管理（含四类标准主题流程）

脚本工具：
  scripts/bond_default_early_warning.py — 转换应用于资产池层
  scripts/bond_cashflow_cover.py        — 循环偿付机制的DSCR复检
```

---

## 三、场景示例（5个）

### 场景1：资产池分析
> "客户的应收账款组合包含75笔企业对企业的应收账款，120家企业债务人遍布全国，集中度最高不超过18%，怎么快速给这个池子评级？"

```
路由流程：
1. 基础资产类型扫描 → 应收账款ABS（企业ABS）
2. 影子评级→ abs-asset-pool-analysis.md（五步评级：债务人分层→违约概率→回收率→初评→压力边界）
3. 集中度红线 → 超25%∈低核心TRIGGER-AV返回检查
4. 输出 → 影子评级+压力测试边界
阶段：02/03 → 产出：资产池初步评分报告
```

---

### 场景2：交易结构设计
> "年租金预期8000万元的6万方商业存量物业，16亿元底层商业物业价值，权益类REITs结构怎么设计？"

```
路由流程：
1. 市场选择 → 交易所 → 企业ABS（类REITs）
2. 出表结构对比 →二层SPV（基金子公司+信托）vs 单一SPV
3. A/B/次结构配置 → 3档（A级占60%、B级占20%、次级20%） → 所有A级都不想为次挡债提供隐性承+超额担保
4. 权利完善事件矩阵设计 → 0.2倍/年触发现金流封闭
阶段：03_方案设计 → 产出：交易结构+分层方案
```

---

### 场景3：增信方案
> "客户资质偏弱评级（投产水电站AA-），投资人要求必须有增信来追到AA+评级。如何设计增信方案？"

```
路由流程：
1. 内外部增信对比 → SKILL_03_ABS方案设计.md（4种内部选择+5种外部结合）
2. 增信链条分析 → guarantee-chain-analysis.md（评分到AA+需要的增信层结构）
3. 超额抵押+外部担保组合分析 →画树状选择的TEM数据计算
4. 输出 → 增信层结构方案：2X超额抵押 + 银行信用证
阶段：03 + ref → 产出：增信方案及条款清单
```

---

### 场景4：计划说明书撰写
> "租金从30家零售商铺来→构成一个CMBS资产池。帮我写专项计划的管理准则章节和信息披露表完成版。"

```
路由流程：
1. 加载CMBS相关条款 → SKILL_04_ABS计划说明书.md (跳章法→运算符基础资产列举)
2. 管理人报告核对数据 →对动态资金池12个月预测 × 0.75×0.85置信连续
3. 关键风险披露批注 →operating risk summary + borrower detail高优先自动按sect关键字调用
4. 版本控制 →META-02（V2.0反馈+交叉引用审查）
阶段：04_文件撰写 → 产出：专项计划补充章节
```

---

### 场景5：存续期管理
> "T+6个月资产池循环购买后，发现运营的动态资金的状态多了1.1X的风险触发点。如何触发相关条款？"

```
路由流程：
1. 动态检测参数触发查询 → SKILL_07_ABS存续.md（每个触发条件的缓解声明）
2. 触发后权利义务对位→新的优先级分层输在项目后获得浮动优化+资金隔分
3. 持有人会议召集 →书面通知→资格验证（持有比例 > 10%或2000万元）
阶段：07_存续期管理 → 产出：接班人恢复方案+触发信
```

---

## 四、与债券线的共用资源

### 直接复用清单

| 资源类型 | 来源 | ABS用途 |
|---------|------|--------|
| **参考文件** | bond/ | |
| bond-product-matrix.md | 16品种全景 | 对比 + ABS品种↔公司债增信进对比 |
| credit-analysis-framework.md | 五维信用 | 基础资产信用三维(评级/历史/分布) |
| bond-filing-regulators.md | 三套监管 | ABS=NAFMII/证监会/央行三个池延展分层 |
| guarantee-chain-analysis.md | 担保链 | ABS专用进行十二类内/外增信 |
| **脚本工具** | scripts/ | |
| dd_checklist_gen.py | 清单生成 | ABS替换→基础资产维度清单节放入 |
| dd_issue_tracker.py | 问题追踪 | RAG→资产层面的问题转变traffic-analyz |
| bond_cashflow_cover.py | 现金流覆盖 | DSCR+ABS资产池并联→扩散基点唤醒 |
| bond_stress_test.py | ✦全新 | 置换多维抵押计划→流量+利息 

### ✦独立文件（ABS专用）
- abs-asset-pool-analysis.md（影子评级+分层测试+压力三套）
- META-13 跨产品+ABS打分

---

## 五、Token 预算

| 场景 | 加载序列 | 预估 tokens |
|------|---------|------------|
| ABS项目冷启动 | ABS/SKILL.md + 01_启动 ×1 + ref×1 | ~3,500 |
| ABS资产池分析 | abs/SKILL.md + 02_尽调/03_方案 + ref×2 | ~5,500 |
| ABS交易结构设计 | abs/SKILL.md + 03_方案 + ref×2 + META-13 | ~6,000 |
| ABS增信+分层设计 | abs/SKILL.md + 03_方案 + guarantee ref + script×1 | ~5,000 |
| ABS计划说明书 | abs/SKILL.md + 04_文件 + ref×2 + META-02 | ~6,500 |
| ABS申报准备 | abs/SKILL.md + 05_申报 + ref×1 | ~4,000 |
| ABS存续 | abs/SKILL.md + 07_存续 + script×1 | ~4,000 |

---

## 快速导航

| 需求 | 文件 |
|------|------|
| 新ABS项目咨询 | `01_项目启动/SKILL_01_ABS项目启动.md` |
| ABS尽调+资产池分析 | `02_尽职调查/SKILL_02_ABS尽调.md` + `abs-asset-pool-analysis.md` |
| 交易结构+分层 | `03_方案设计/SKILL_03_ABS方案设计.md` + `ma/deal-structures.md` |
| 增信方案设计 | `03_方案设计/SKILL_03_ABS方案设计.md` + `guarantee-chain-analysis.md` |
| 计划说明书撰写 | `04_文件撰写/SKILL_04_ABS计划说明书.md` + META-02 |
| 申报流程 | `05_监管申报/SKILL_05_ABS申报.md` + META-12 |
| ABS发行 | `06_发行执行/SKILL_06_ABS发行.md` |
| ABS存续期 | `07_存续期管理/SKILL_07_ABS存续.md` |

---

# v2.0 三线重组 | 2026-05