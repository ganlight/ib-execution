---
name: ib-execution-equity
version: 2.0
description: 股权线子入口。覆盖IPO（主板/科创板/创业板/北交所）、再融资（定增/配股/可转债）、并购重组三类子线的七阶段全生命周期。含上市评估、尽调启动、招股书撰写、反馈回复、再融资方案设计、并购重组方案与交割执行。
---

# 股权线技能入口 (Equity Sub-Entry)

> 股权承做七阶段管线 · IPO · 再融资 · 并购重组

## 一、股权产品线总览

### 子线A：IPO上市

| 板块 | 核心条件 | 适用企业 | 审核机构 | 制度 |
|------|---------|---------|---------|------|
| 主板 | 营收≥100亿或利润≥10亿（3年累计） | 成熟蓝筹、大市值 | 交易所审核+证监会注册 | 注册制 |
| 科创板 | 市值≥40亿 + 科创属性6项（研发/专利/市占等） | 硬科技企业 | 上交所审核+注册 | 注册制 |
| 创业板 | 最近2年净利润均为正且累计≥1亿 | 成长型创新创业 | 深交所审核+注册 | 注册制 |
| 北交所 | 净利润≥1500万或营收≥2亿 | 专精特新中小企业 | 北交所审核+注册 | 注册制 |

### 子线B：再融资

| 品种 | 适用对象 | 定价机制 | 锁定期 | 核心规则 |
|------|---------|---------|--------|---------|
| 定增（竞价） | 已上市公司 | 市场询价 | 6个月 | 18个月间隔、30%总股本限制 |
| 定增（锁价） | 已上市公司 | 董事会定价 | 18个月 | 战投认定+发行期首日定价 |
| 配股 | 已上市公司 | 固定价 | 无 | 控股股东认购≥70%+代销 |
| 可转债 | 已上市公司 | 询价 | 无 | 6个月转股期+转股价下修条款 |
| 优先股 | 已上市公司 | 协商 | 无 | 固定股息+非累积 |

### 子线C：并购重组

| 类型 | 核心条件 | 审核 | 业绩承诺锁定期 |
|------|---------|------|-------------|
| 发行股份购买资产 | 无明确指标门槛（视重组规模） | 证监会/重组委 | 12-36个月 |
| 重大资产重组 | 购买/出售资产≥上市公司50% | 重组委审核 | 12-36个月 |
| 借壳上市 | 控制权变更+注入资产≥100% | 重组委审核（等同IPO） | 36个月 |
| 换股吸收合并 | 合并方×被合并方→存续 | 股东大会+证监会 | 视约定 |
| 要约收购 | 持股≥30%触发全面要约义务 | 证监会 | — |

---

## 二、七阶段快速路由

### Stage 01：项目启动

```
入口文件：01_项目启动/SKILL_01_项目启动.md

IPO/再融资 → 读取以下子技能：
  SKILL_01a_客户KYC.md    — KYC/AML核查 + 反洗钱筛查
  SKILL_01b_利益冲突.md    — 利益冲突检查（关联交易/竞业禁止/信息隔离）
  SKILL_01c_初步方案.md    — 初步方案建议书 + Pitch Book框架

关键参考：
  references/equity/ipo-board-conditions.md — 四板块上市条件对比
  references/shared/intermediary-roles.md    — 券商/律所/会所/评估机构分工

脚本工具：
  scripts/ipo_board_check.py — 企业数据→各板块符合性报告

META叠加：
  00-META-01_项目冷启动.md  — 新项目五步法
  00-META-11_投行项目生命周期管理模型.md — 全周期规划
```

---

### Stage 02：尽职调查

```
入口文件：02_尽职调查/SKILL_00_尽调总览.md → 分发至6个子技能

  SKILL_02a_法律尽调.md    — 主体资格、股权沿革、资产权属、重大合同、诉讼仲裁
  SKILL_02b_财务尽调.md    — 银行流水、函证、关联方交易、收入穿透、存货盘点
  SKILL_02c_业务尽调.md    — 行业分析、客户供应商、技术壁垒、竞争格局
  SKILL_02d_底稿体系.md    — 工作底稿目录编制、归档标准、电子化
  SKILL_02e_问题追踪.md    — RED/AMBER/GREEN三级分类 + 闭环整改
  SKILL_02f_尽调报告.md    — 尽调总结报告模板（法律/财务/业务分册）

关键参考：
  references/shared/dd-checklist-master.md       — 尽调总清单（按阶段/行业分类）
  references/shared/dd-redflag-industry-library.md — 6大行业51种红旗信号
  references/shared/qoe-analysis-framework.md   — QOE质量盈利分析（U型调节法）
  references/shared/management-interview-guide.md — 管理层访谈7类提纲
  references/shared/site-inspection-procedures.md — 实地走访/盘点程序
  references/shared/revenue-quality-analysis.md — 收入质量四象限分析

脚本工具：
  scripts/dd_checklist_gen.py      — 按项目类型+行业生成定制清单
  scripts/dd_issue_tracker.py      — 问题追踪（RED/AMBER/GREEN + 6个CLI命令）
  scripts/financial_ratio_calc.py  — 财务比率完整计算表

META叠加：
  00-META-05_交叉校验质量控制.md — 尽调数据与审计报告交叉验证
  00-META-06_中介机构协调.md     — 律所/会所分工时间衔接
```

---

### Stage 03：方案设计（三子线分发）

```
入口文件：03_方案设计/SKILL_00_方案总览.md

━━ 子线A：IPO ━━
  SKILL_03a_IPO方案.md
    ├─ 板块选择决策（四板块条件矩阵对比）
    ├─ 发行方案设计（发行股数/价格区间/锁定期安排）
    ├─ 募投项目核定（四类：扩产/研发/补流/并购）
    └─ 时间表规划（辅导→申报→问询→上会→注册→发行）
    参考：references/equity/ipo-board-conditions.md + ipo-timeline.md
    工具：scripts/ipo_board_check.py

━━ 子线B：再融资 ━━
  SKILL_03b_再融资方案.md
    ├─ 发行方式选择（定增竞价/锁价/配股/可转债/优先股）
    ├─ 定价基准选择（发行期首日/董事会决议日）
    ├─ 认购对象遴选（战投认定标准+锁价安排）
    └─ 募集资金用途规划
    参考：references/equity/refinancing-rules.md

━━ 子线C：并购重组 ━━
  SKILL_03c_并购重组.md
    ├─ 交易结构设计（换股/现金/混合 + 支付节奏）
    ├─ 业绩承诺与对赌条款（3年/4年承诺期 + 补偿公式）
    ├─ 整合方案与协同效应
    └─ 交易对方与标的资产合规
    参考：references/ma/restructuring-standards.md + deal-structures.md
  SKILL_03d_财务建模.md
    ├─ DCF估值模型 + 可比公司估值
    ├─ 协同效应量化
    └─ 敏感性分析
    工具：scripts/ma_valuation_calc.py

META叠加：
  00-META-13_风险定价决策模型.md    — IPO定价/并购估值决策
  00-META-15_跨产品线协同工作法.md  — IPO vs 再融资 vs 债券比选
```

---

### Stage 04：文件撰写（三子线分发）

```
入口文件：04_文件撰写/SKILL_00_撰写总览.md

━━ IPO/再融资 ━━
  SKILL_04a_招股书.md
    ├─ 招股说明书13章逐章撰写指引
    ├─ 各章审核重点关键词 + 常见反馈意见
    └─ 正面审查清单 + 反面排除清单
    参考：references/equity/prospectus-sections.md

━━ 并购重组 ━━
  SKILL_04b_重组报告书.md
    ├─ 重组报告书结构（独立财务顾问报告/法律意见书/审计报告）
    ├─ 交易对方+标的资产详细披露
    └─ 业绩承诺与补偿安排

━━ 通用文件 ━━
  SKILL_04c_法律意见书.md — 律师核查要点与意见出具标准
  SKILL_04d_审计报告.md    — 会计师报告核阅要点
  SKILL_04e_版本管理.md    — 文件版本控制 + diff对比

关键参考：
  references/shared/document-cross-ref.md — 文件交叉引用关系图
  references/compliance/related-party-rules.md — 关联交易规则
  references/compliance/independence-rules.md — 独立性规则

脚本工具：
  scripts/doc_version_diff.py  — 版本差异对比报告
  scripts/cross_ref_check.py   — 文件间数据一致性检查

META叠加：
  00-META-02_文件迭代工作流.md  — P0初稿→V3终稿全流程
  00-META-16_文件质量内控标准.md — 三级审阅+五维评分卡
```

---

### Stage 05：监管申报（三子线分发）

```
入口文件：05_监管申报/SKILL_00_申报总览.md

━━ IPO ━━
  SKILL_05a_IPO材料清单.md — 全套申报文件checklist（招股书+法律意见书+审计报告+...）
  SKILL_05b_IPO审核流程.md  — 受理→问询→多轮反馈→上市委审议→证监会注册

━━ 并购重组 ━━
  SKILL_05c_重组审核.md — 重组委审核流程（受理→问询→重组委会议→注册）

━━ 通用反馈 ━━
  SKILL_05d_反馈回复.md — 回复撰写策略（事实型/分析型/补充型）
  SKILL_05e_审核进度.md — 申报进度追踪表

关键参考：
  references/shared/regulatory-feedback-patterns.md — 反馈模式库数据

脚本工具：
  scripts/filing_tracker.py — 审核进度可视化追踪

META叠加：
  00-META-03_反馈回复模式库.md      — 八大类问询回复范式
  00-META-12_监管审核分析框架.md    — 三层规则金字塔
```

---

### Stage 06：发行执行（两子线分发）

```
入口文件：06_发行执行/SKILL_00_发行总览.md

━━ IPO ━━
  SKILL_06a_IPO路演.md
    ├─ 路演材料准备（投资故事+行业分析+财务亮点+风险揭示）
    ├─ 预路演→正式路演→簿记建档→定价
    └─ 询价应对策略（锚定投资者+网下投资者管理）

━━ 并购 ━━
  SKILL_06b_并购交割.md
    ├─ 交割先决条件清单（CP确认+资产过户+股权变更登记）
    ├─ 交割日操作流程
    └─ 交割后确认事项

META叠加：
  00-META-13_风险定价决策模型.md — IPO定价/发行窗口研判
```

---

### Stage 07：存续期管理（两子线分发）

```
入口文件：07_存续期管理/SKILL_00_存续总览.md

━━ IPO持续督导 ━━
  SKILL_07a_IPO持续督导.md
    ├─ 定期报告核查（年报/半年报/季报）
    ├─ 募集资金使用核查
    ├─ 重大事项持续跟踪
    └─ 持续督导工作报告

━━ 并购整合 ━━
  SKILL_07b_并购整合.md
    ├─ 业绩承诺期内跟踪（季度/年度考核）
    ├─ 商誉减值测试
    └─ 整合效果评估报告
```

---

## 三、三个子线阶段差异化对照

| 阶段 | 子线A：IPO | 子线B：再融资 | 子线C：并购重组 |
|------|----------|------------|--------------|
| **01 启动** | SKILL_01a/b/c + 板块评估 | 01a/b/c + 定增/配股条件 | 01a/b/c + 标的初步评估 |
| **02 尽调** | 6文件完整集（法律/财务/业务/底稿/追踪/报告） | 复用IPO尽调框架，侧重盈利能力+再融资条件 | 扩展至交易对方DD + 协同效应分析 |
| **03 方案** | SKILL_03a（板块选择+募投+发行方案） | SKILL_03b（方式选择+定价基准+认购对象） | SKILL_03c+03d（交易结构+对赌+估值建模） |
| **04 文件** | SKILL_04a（招股说明书13章） | 复用招股书框架+再融资专项披露 | SKILL_04b（重组报告书+独立财务顾问报告） |
| **05 申报** | SKILL_05a+05b（交易所审核流程） | 参照IPO流程，反馈问题不同 | SKILL_05c（重组委审核流程） |
| **06 发行** | SKILL_06a（路演+簿记+定价） | 路演简化（定增/配股无正式路演） | SKILL_06b（交割先决条件+过户） |
| **07 存续** | SKILL_07a（持续督导3年） | 募集资金持续核查 | SKILL_07b（业绩承诺期跟踪+商誉减值） |

---

## 四、场景示例（6个）

### 场景1：上市板块评估
> "公司净利润3年累计1.2亿，行业工业软件，27项发明专利，研发投入占比8%，上哪个板块？"

```
路由：equity/SKILL.md → 03_方案设计/SKILL_03a_IPO方案.md
参考：references/equity/ipo-board-conditions.md（四板块条件矩阵）
工具：scripts/ipo_board_check.py（输入企业数据→输出各板块符合性）
产出：板块建议 + 各板块上市概率评估 + 时间表初估
```

---

### 场景2：IPO尽调启动
> "新接手一个IPO项目，第一天开始，从财务尽调入手怎么开展工作？"

```
路由：equity/SKILL.md → 02_尽职调查/SKILL_00_尽调总览.md
     → SKILL_02b_财务尽调.md（银行流水穿透+函证+关联方+收入分析）
参考：references/shared/dd-checklist-master.md（财务尽调部分）
工具：scripts/dd_checklist_gen.py（自动生成IPO财务尽调清单）
     scripts/financial_ratio_calc.py（财务比率基线计算）
产出：财务尽调启动计划（23项检查点排序 + 时间安排）
```

---

### 场景3：招股书撰写
> "客户是工业机器人企业，国内市占率12%，有5项核心技术，帮我写招股书业务与技术章节"

```
路由：equity/SKILL.md → 04_文件撰写/SKILL_04a_招股书.md
参考：references/equity/prospectus-sections.md（第五章撰写指引）
META：00-META-02_文件迭代工作流.md（P0→V2迭代路径）
     00-META-16_文件质量内控标准.md（撰写质量自检）
产出：招股书业务与技术章节初稿（含行业分析+技术壁垒+竞争格局）
```

---

### 场景4：交易所问询回复
> "上交所发了38条问询，重点在收入真实性和毛利率异常，帮我分类并制定回复策略"

```
路由：equity/SKILL.md → 05_监管申报/SKILL_05d_反馈回复.md
META：00-META-03_反馈回复模式库.md（八类问询回复范式）
     00-META-12_监管审核分析框架.md（三层规则金字塔）
参考：references/shared/regulatory-feedback-patterns.md（历史反馈模式）
工具：scripts/filing_tracker.py（问题分类+状态追踪）
产出：38条问题分类表 + 优先级排序 + 各类回复策略 + 时间排期
```

---

### 场景5：再融资方案设计
> "上市公司总资产120亿，想定增募资20亿做产能扩建，怎么设计发行方案？"

```
路由：equity/SKILL.md → 03_方案设计/SKILL_03b_再融资方案.md
参考：references/equity/refinancing-rules.md（定增规则+定价限制+锁定期）
产出：定增方案要点（发行价测算+认购对象条件+锁定期安排+募集资金用途规划）
```

---

### 场景6：并购交割执行
> "并购重组委审核通过，现在进入交割阶段，先决条件清单和交割日操作流程怎么做？"

```
路由：equity/SKILL.md → 06_发行执行/SKILL_06b_并购交割.md
参考：references/ma/deal-structures.md（交割条款参考）
产出：交割先决条件清单（CP确认项+资产过户+股权变更） + 交割日操作手册
```

---

## 五、Token 预算

| 场景 | 加载序列 | 预估 tokens |
|------|---------|------------|
| IPO冷启动评估 | equity/SKILL.md + 01_启动(3子) + board-conditions + ipo_board_check | ~5,000 |
| IPO尽调启动 | equity/SKILL.md + 02_尽调总览 + 1个子技能(02a~02f) + ref×2 | ~6,500 |
| 招股书撰写 | equity/SKILL.md + 04_撰写总览 + 04a招股书 + prospectus-sections | ~7,000 |
| IPO反馈回复 | equity/SKILL.md + 05_申报总览 + 05d反馈 + META-03 + ref | ~5,500 |
| 再融资方案 | equity/SKILL.md + 03_方案总览 + 03b再融资 + refinancing-rules | ~5,000 |
| 并购方案+估值 | equity/SKILL.md + 03_方案总览 + 03c+03d + ma refs + ma_valuation | ~7,000 |
| 并购交割 | equity/SKILL.md + 06_发行总览 + 06b交割 + deal-structures | ~4,500 |
| IPO持续督导 | equity/SKILL.md + 07_存续总览 + 07a督导 | ~3,500 |

---

## 快速导航

| 需求 | 查找位置 |
|------|----------|
| 评估上市板块 | `03_方案设计/SKILL_03a_IPO方案.md` + `ref:ipo-board-conditions.md` |
| 启动尽调 | `02_尽职调查/SKILL_00_尽调总览.md` → 分发至02a~02f |
| 写招股书 | `04_文件撰写/SKILL_04a_招股书.md` + `META-02迭代` |
| 做定增方案 | `03_方案设计/SKILL_03b_再融资方案.md` + `ref:refinancing-rules.md` |
| 做并购方案 | `03_方案设计/SKILL_03c_并购重组.md` + `SKILL_03d_财务建模.md` |
| 准备IPO申报 | `05_监管申报/SKILL_05a_IPO材料清单.md` + `SKILL_05b_IPO审核流程.md` |
| 处理反馈问询 | `05_监管申报/SKILL_05d_反馈回复.md` + `META-03` + `META-12` |
| IPO持续督导 | `07_存续期管理/SKILL_07a_IPO持续督导.md` |
| 并购整合跟踪 | `07_存续期管理/SKILL_07b_并购整合.md` |

---

# v2.0 三线重组 | 2026-05