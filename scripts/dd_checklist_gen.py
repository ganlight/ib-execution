#!/usr/bin/env python3
"""
DD Checklist Generator — Generate structured due diligence checklists.

Generates file-level checklists for IPO, M&A, and Bond projects across
three DD stages (pre-DD / formal DD / deep DD). Output as Markdown, plain text, or JSON.

Usage:
    python dd_checklist_gen.py --type ipo --stage dd1
    python dd_checklist_gen.py --type ipo --stage dd2 --format markdown
    python dd_checklist_gen.py --type ma --stage dd0 --json
    python dd_checklist_gen.py --test
"""

import argparse
import json
import sys
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Checklist database — IPO (7 modules: DD-00 through DD-06)
# ---------------------------------------------------------------------------

IPO_CHECKLIST: Dict[str, List[Dict[str, str]]] = {
    "DD-00 项目管理": [
        {"id": "DD-00-001", "file": "委任书及补充协议", "req": "含服务范围、收费安排、终止条款；签字盖章页完整", "stage": "dd0"},
        {"id": "DD-00-002", "file": "项目时间表和里程碑计划", "req": "甘特图形式，含各中介机构关键节点，标注依赖关系", "stage": "dd0"},
        {"id": "DD-00-003", "file": "项目启动会纪要", "req": "含参会人员名单、讨论要点、决议事项、下一步分工", "stage": "dd0"},
        {"id": "DD-00-004", "file": "中介机构保密协议及利益冲突声明", "req": "各中介签字版，含独立性确认", "stage": "dd0"},
        {"id": "DD-00-005", "file": "发行人资料需求清单（初始版）", "req": "按DD模块分类列示，含预计提供时间", "stage": "dd0"},
        {"id": "DD-00-006", "file": "阶段性工作会议纪要", "req": "每次工作会议后24小时内完成，含出席、议题、决议、行动项", "stage": "dd1"},
        {"id": "DD-00-007", "file": "重大事项沟通记录", "req": "发行人重大事项（如重组、处罚、诉讼）的专项沟通和核查结论", "stage": "dd1"},
        {"id": "DD-00-008", "file": "内外部沟通往来函件", "req": "按时间顺序归档，标注事项类别和跟进状态", "stage": "dd1"},
        {"id": "DD-00-009", "file": "项目进度报告（周报/月报）", "req": "含本期完成事项、异常事项、风险提示、下期计划", "stage": "dd2"},
        {"id": "DD-00-010", "file": "中介机构协调会纪要及任务跟踪表", "req": "含各中介任务完成率、阻塞项清单、协调会议决议", "stage": "dd2"},
    ],
    "DD-01 主体资格": [
        {"id": "DD-01-001", "file": "营业执照（含历史版本）", "req": "最新版+历史变更版本，验证经营范围、有效期、统一社会信用代码", "stage": "dd0"},
        {"id": "DD-01-002", "file": "公司章程及修正案", "req": "现行有效版本+历次修正案，与工商档案一致", "stage": "dd0"},
        {"id": "DD-01-003", "file": "工商登记档案全册", "req": "自设立至今全部工商登记资料，加盖市监局查询章", "stage": "dd0"},
        {"id": "DD-01-004", "file": "设立批文/核准文件", "req": "含行业主管部门和国资部门批复（如适用）", "stage": "dd0"},
        {"id": "DD-01-005", "file": "历次验资报告", "req": "含历次增资、减资验资报告，非货币出资评估报告", "stage": "dd1"},
        {"id": "DD-01-006", "file": "非货币出资评估报告及过户证明", "req": "评估基准日至出资日的资产评估报告+资产过户文件", "stage": "dd1"},
        {"id": "DD-01-007", "file": "历次股东会/董事会/监事会决议", "req": "自设立起完整记录，含通知、签到、表决票、决议、纪要", "stage": "dd1"},
        {"id": "DD-01-008", "file": "改制方案及批文（如有）", "req": "含整体变更方案、审计/评估报告、创立大会文件", "stage": "dd1"},
        {"id": "DD-01-009", "file": "业务资质/许可证清单及复印件", "req": "所有生产经营所需资质，标注有效期和续期条件", "stage": "dd1"},
        {"id": "DD-01-010", "file": "境外经营合规证明", "req": "境外子公司当地律师出具的法律意见+经营资质", "stage": "dd2"},
        {"id": "DD-01-011", "file": "历史沿革专项法律意见书", "req": "重点核查：出资瑕疵、国资流失、集体企业改制合规性", "stage": "dd2"},
        {"id": "DD-01-012", "file": "公司章程与治理规则对比分析", "req": "与公司法/必备条款/上市规则的逐条对比", "stage": "dd2"},
    ],
    "DD-02 股权结构": [
        {"id": "DD-02-001", "file": "股权架构图（穿透至最终权益持有人）", "req": "含控制路径、持股比例、投票权与收益权差异", "stage": "dd0"},
        {"id": "DD-02-002", "file": "股东名册及出资证明", "req": "含股东姓名/名称、证件号、出资额、出资比例、出资方式", "stage": "dd0"},
        {"id": "DD-02-003", "file": "实际控制人身份证明及简历", "req": "含身份证明文件、教育/工作经历、对外投资和任职情况", "stage": "dd0"},
        {"id": "DD-02-004", "file": "一致行动协议/控制协议", "req": "含签署各方、期限、决策机制、争议解决条款", "stage": "dd1"},
        {"id": "DD-02-005", "file": "员工持股平台全套文件", "req": "含合伙协议、份额持有清单、流转限制、退出机制", "stage": "dd1"},
        {"id": "DD-02-006", "file": "股权代持确认函及解除协议", "req": "含代持人/被代持人确认、税务处理、不存在纠纷声明", "stage": "dd1"},
        {"id": "DD-02-007", "file": "股权质押/冻结查询记录", "req": "市监局动产融资登记+中登公司查询结果", "stage": "dd1"},
        {"id": "DD-02-008", "file": "VIE协议全套（如适用）", "req": "含独家购买权、表决权代理、股权质押、独家业务合作等全套协议", "stage": "dd1"},
        {"id": "DD-02-009", "file": "股东穿透核查报告", "req": "穿透至自然人/国资/上市公司，含三类股东核查", "stage": "dd2"},
        {"id": "DD-02-010", "file": "股东适格性核查报告", "req": "含股东负面清单排查、PE/VC备案合规、锁定期承诺", "stage": "dd2"},
        {"id": "DD-02-011", "file": "特殊权利条款汇总及终止协议", "req": "对赌/回购/反稀释/优先清算等条款清理情况", "stage": "dd2"},
    ],
    "DD-03 主要资产": [
        {"id": "DD-03-001", "file": "不动产权证/土地使用权证", "req": "含出让合同、土地出让金缴纳凭证、使用权证；标注权利限制", "stage": "dd0"},
        {"id": "DD-03-002", "file": "房屋所有权证/不动产权证书", "req": "自建+购买房产全部权证，标注抵押/查封情况", "stage": "dd0"},
        {"id": "DD-03-003", "file": "专利证书及年费缴纳凭证", "req": "含发明/实用新型/外观设计全部专利，验证法律状态", "stage": "dd0"},
        {"id": "DD-03-004", "file": "商标注册证", "req": "含境内/境外全部注册商标，标注类别和使用证据", "stage": "dd0"},
        {"id": "DD-03-005", "file": "租赁合同汇编及出租方权属证明", "req": "含租赁备案登记、出租方产权证、租赁稳定性评估", "stage": "dd1"},
        {"id": "DD-03-006", "file": "在建工程审批文件", "req": "建设用地规划许可、建设工程规划许可、施工许可、竣工备案", "stage": "dd1"},
        {"id": "DD-03-007", "file": "固定资产盘点表", "req": "含机器设备/车辆/电子设备分类汇总，与账面核对一致", "stage": "dd1"},
        {"id": "DD-03-008", "file": "融资租赁/经营租赁合同", "req": "含租赁物清单、起止日期、租金、所有权转移条款", "stage": "dd1"},
        {"id": "DD-03-009", "file": "软件著作权证书及登记公告", "req": "含登记号、著作权人、开发完成日期、权利范围", "stage": "dd1"},
        {"id": "DD-03-010", "file": "知识产权许可/转让合同", "req": "入许可+出许可全部合同，含许可范围、排他性、期限、费率", "stage": "dd1"},
        {"id": "DD-03-011", "file": "知识产权法律状态检索报告", "req": "CNIPA/CTMO/CPCC官方检索结果，标注有效期和权利状态", "stage": "dd2"},
        {"id": "DD-03-012", "file": "知识产权独立性分析", "req": "核心技术/商标是否独立于第三方许可，许可终止风险分析", "stage": "dd2"},
        {"id": "DD-03-013", "file": "重大资产收购/处置文件", "req": "含评估报告、董事会/股东会决议、交易合同、交割文件", "stage": "dd2"},
    ],
    "DD-04 重大合同": [
        {"id": "DD-04-001", "file": "银行借款合同及授信协议", "req": "全部存续借款合同，含金额/利率/期限/担保/约束性条款", "stage": "dd0"},
        {"id": "DD-04-002", "file": "对外担保合同", "req": "含保证/抵押/质押合同、主债权合同、担保决议文件", "stage": "dd0"},
        {"id": "DD-04-003", "file": "前5大采购框架合同及订单", "req": "含定价机制、付款条件、排他性条款、违约责任", "stage": "dd1"},
        {"id": "DD-04-004", "file": "前5大销售框架合同及订单", "req": "含定价机制、信用期、质量保证、退货条款、排他性安排", "stage": "dd1"},
        {"id": "DD-04-005", "file": "建设工程施工合同", "req": "含工程范围、合同价款、工期、质量标准、进度款支付", "stage": "dd1"},
        {"id": "DD-04-006", "file": "资产/股权转让协议", "req": "含定价依据、交割条件、过渡期安排、陈述保证条款", "stage": "dd1"},
        {"id": "DD-04-007", "file": "合资/合作协议", "req": "含各方出资/权利义务、治理安排、退出机制、僵局解决", "stage": "dd1"},
        {"id": "DD-04-008", "file": "合同异常条款分析报告", "req": "排查void/invalid条款、极端情况下条款、单方不利条款", "stage": "dd2"},
        {"id": "DD-04-009", "file": "约束性条款合规性分析（Covenant Check）", "req": "与借款/担保合同的约束性条款逐条对比实际履行情况", "stage": "dd2"},
    ],
    "DD-05 财务资料": [
        {"id": "DD-05-001", "file": "审计报告（最近3年+1期）", "req": "含审计意见、附注、关键审计事项；若含否定/保留/强调事项需专项分析", "stage": "dd0"},
        {"id": "DD-05-002", "file": "银行账户清单及对账单", "req": "含全部开户行/账号/币种/余额；报告期每月对账单（银行盖章）", "stage": "dd0"},
        {"id": "DD-05-003", "file": "大额资金流水核查底稿", "req": "单笔或5日内累计>=重要性水平的交易，含对手方/用途/凭证", "stage": "dd1"},
        {"id": "DD-05-004", "file": "应收账款明细及账龄分析表", "req": "分客户列示余额/账龄/坏账准备，与审定数一致", "stage": "dd1"},
        {"id": "DD-05-005", "file": "收入确认底稿及穿行测试", "req": "按收入类型各选代表性样本，走通从合同到回款全流程", "stage": "dd1"},
        {"id": "DD-05-006", "file": "银行函证汇总表", "req": "含发函/回函率、不符项汇总、跟进处理情况", "stage": "dd1"},
        {"id": "DD-05-007", "file": "往来函证汇总表", "req": "含应收账款/应付账款函证、替代程序执行记录", "stage": "dd1"},
        {"id": "DD-05-008", "file": "纳税申报表及完税证明", "req": "报告期各税种申报表+税务局出具的无违规证明", "stage": "dd1"},
        {"id": "DD-05-009", "file": "关联交易明细及定价分析", "req": "含交易内容/金额/定价依据/必要性/公允性分析/决策程序", "stage": "dd1"},
        {"id": "DD-05-010", "file": "存货明细及盘点底稿", "req": "含品种/数量/金额/库龄/跌价准备，最近一次全面盘点记录", "stage": "dd1"},
        {"id": "DD-05-011", "file": "毛利率分析表（分产品/分客户）", "req": "与同行业可比公司对比，异常波动专项分析", "stage": "dd1"},
        {"id": "DD-05-012", "file": "政府补助明细及合规性分析", "req": "含补助项目/金额/文件依据/确认条件/可持续性评估", "stage": "dd2"},
        {"id": "DD-05-013", "file": "研发费用资本化分析", "req": "资本化条件逐条论证、开发阶段判定、同行业政策比较", "stage": "dd2"},
        {"id": "DD-05-014", "file": "内部控制鉴证报告", "req": "会计师出具的内部控制鉴证/审计报告及管理建议书", "stage": "dd2"},
        {"id": "DD-05-015", "file": "盈利预测/业绩预计文件（如有）", "req": "含核心假设、敏感性分析、可实现性论证", "stage": "dd2"},
    ],
    "DD-06 业务与技术": [
        {"id": "DD-06-001", "file": "行业研究报告", "req": "多家独立第三方（≥2家），含市场规模/增速/竞争格局", "stage": "dd0"},
        {"id": "DD-06-002", "file": "可比公司分析", "req": "境内外≥5家，含关键财务指标/估值/业务模式对比", "stage": "dd0"},
        {"id": "DD-06-003", "file": "核心技术清单及先进程度说明", "req": "技术来源/对应产品/知识产权/先进程度/技术壁垒/迭代路径", "stage": "dd1"},
        {"id": "DD-06-004", "file": "销售明细（分客户/分产品/分区域）", "req": "报告期数据，可追溯至合同/发票/物流单据", "stage": "dd1"},
        {"id": "DD-06-005", "file": "采购明细（分供应商/分品类）", "req": "报告期数据，含核心原材料价格变动趋势", "stage": "dd1"},
        {"id": "DD-06-006", "file": "产能及产量数据统计", "req": "分产品线产能利用率/产销率数据及变化趋势分析", "stage": "dd1"},
        {"id": "DD-06-007", "file": "管理层访谈纪要", "req": "董事长/总经理/财务负责人/技术负责人/销售负责人分别访谈", "stage": "dd1"},
        {"id": "DD-06-008", "file": "职能部门访谈纪要", "req": "涵盖研发/采购/生产/销售/HR/法务/IT各职能部门", "stage": "dd1"},
        {"id": "DD-06-009", "file": "客户/供应商现场走访记录", "req": "前10大客户+供应商走访报告，含照片、访谈纪要、现场观察", "stage": "dd2"},
        {"id": "DD-06-010", "file": "研发立项及成果转化文件", "req": "含立项书/验收报告/成果证明/产业化应用数据", "stage": "dd2"},
        {"id": "DD-06-011", "file": "核心技术先进性论证报告", "req": "含与国内外主流技术对比、第三方技术评价、专利引证分析", "stage": "dd2"},
        {"id": "DD-06-012", "file": "环境/安全/质量合规核查", "req": "环评批复+环保验收+排污许可证+安全生产许可证+ISO体系认证", "stage": "dd2"},
    ],
}

MA_CHECKLIST: Dict[str, List[Dict[str, str]]] = {
    "DD-M&A-01 战略与交易": [
        {"id": "MA-01-001", "file": "交易方案概述及商业逻辑分析", "req": "含交易背景、战略意图、协同效应测算、交易方案设计", "stage": "dd0"},
        {"id": "MA-01-002", "file": "标的公司初步尽调报告", "req": "含基本信息、主要资产、财务状况、核心风险", "stage": "dd0"},
        {"id": "MA-01-003", "file": "估值方法选择及分析备忘录", "req": "方法选择依据、可比公司/交易数据、敏感性分析", "stage": "dd1"},
        {"id": "MA-01-004", "file": "交易定价合理性分析", "req": "含溢价率分析、可比交易对比、业绩承诺合理性", "stage": "dd1"},
        {"id": "MA-01-005", "file": "整合计划及实施方案", "req": "含时间表、关键节点、职能部门整合、IT系统对接", "stage": "dd2"},
        {"id": "MA-01-006", "file": "协同效应量化及追踪方案", "req": "成本协同/收入协同分别量化，含追踪KPI", "stage": "dd2"},
    ],
    "DD-M&A-02 法律": [
        {"id": "MA-02-001", "file": "标的公司法律尽调报告", "req": "含主体资格、股权、资产、合同、诉讼等全维度", "stage": "dd0"},
        {"id": "MA-02-002", "file": "标的公司实际控制人及关联方核查", "req": "含控制链穿透、关联方清单、关联交易汇总", "stage": "dd0"},
        {"id": "MA-02-003", "file": "交易协议全套文件", "req": "含框架协议/股权转让协议/资产购买协议/担保文件", "stage": "dd1"},
        {"id": "MA-02-004", "file": "陈述保证条款清单及例外披露", "req": "买方/卖方陈述保证对比分析，例外事项影响评估", "stage": "dd1"},
        {"id": "MA-02-005", "file": "交易前置条件/先决条件汇总", "req": "含反垄断/国家安全/行业准入/第三方同意等审批条件", "stage": "dd2"},
        {"id": "MA-02-006", "file": "赔偿机制及托管安排分析", "req": "含赔偿上限/下限/期限/托管金额/托管释放条件", "stage": "dd2"},
    ],
    "DD-M&A-03 财务": [
        {"id": "MA-03-001", "file": "标的公司审计报告（3年+1期）", "req": "含审计意见、重要会计政策、关键审计事项", "stage": "dd0"},
        {"id": "MA-03-002", "file": "标的公司财务尽调报告（买方DD）", "req": "含收入质量/盈利质量/资产质量/负债/现金流全维度分析", "stage": "dd1"},
        {"id": "MA-03-003", "file": "备考合并财务报表", "req": "含备考调整分录、合并后关键财务指标、每股收益影响", "stage": "dd1"},
        {"id": "MA-03-004", "file": "标的公司应收/应付/存货质量分析", "req": "含账龄、坏账/跌价准备充足性、周转指标与行业对比", "stage": "dd1"},
        {"id": "MA-03-005", "file": "交易后偿债能力分析", "req": "含合并资产负债率、利息保障倍数、现金流覆盖分析", "stage": "dd2"},
        {"id": "MA-03-006", "file": "商誉减值测试参数及模型", "req": "含资产组划分、增长率/折现率假设、敏感性分析", "stage": "dd2"},
    ],
    "DD-M&A-04 税务": [
        {"id": "MA-04-001", "file": "标的公司纳税合规性核查", "req": "含各税种申报表、完税证明、税务稽查记录", "stage": "dd0"},
        {"id": "MA-04-002", "file": "交易所涉税种及税负测算", "req": "含企业所得税/增值税/印花税/土地增值税等测算", "stage": "dd1"},
        {"id": "MA-04-003", "file": "特殊性税务处理适用性论证", "req": "对照财税[2009]59号/财税[2014]109号逐条件论证", "stage": "dd1"},
        {"id": "MA-04-004", "file": "历史税务风险/争议汇总", "req": "含未决税务争议、历史补税/罚款、税收优惠依赖度", "stage": "dd2"},
        {"id": "MA-04-005", "file": "交易后税务整合方案", "req": "含税务架构优化、转移定价调整、税收优惠延续方案", "stage": "dd2"},
    ],
}

BOND_CHECKLIST: Dict[str, List[Dict[str, str]]] = {
    "DD-BOND-01 发行人与主体资格": [
        {"id": "BOND-01-001", "file": "营业执照及工商档案", "req": "含主营业务与债券品种准入要求的匹配性核查", "stage": "dd0"},
        {"id": "BOND-01-002", "file": "股权结构及实际控制人文件", "req": "含穿透核查、一致行动人、国资批复文件", "stage": "dd0"},
        {"id": "BOND-01-003", "file": "公司章程及治理文件", "req": "含债券发行内部决策程序合规性", "stage": "dd0"},
        {"id": "BOND-01-004", "file": "业务资质或许可证", "req": "验证主体业务合法合规性", "stage": "dd1"},
    ],
    "DD-BOND-02 财务信用": [
        {"id": "BOND-02-001", "file": "审计报告（3年+1期）", "req": "关注审计意见类型、关键审计事项、持续经营能力", "stage": "dd0"},
        {"id": "BOND-02-002", "file": "有息负债明细表", "req": "含品种/金额/利率/期限/到期日/担保方式", "stage": "dd0"},
        {"id": "BOND-02-003", "file": "偿债能力分析报告", "req": "含利息保障倍数/DSCR/资产负债率/现金流覆盖率", "stage": "dd1"},
        {"id": "BOND-02-004", "file": "银行授信及使用情况", "req": "含各银行授信额度/已使用/未使用/授信条件", "stage": "dd1"},
        {"id": "BOND-02-005", "file": "对外担保及或有负债清单", "req": "含被担保方/金额/期限/反担保/代偿风险评估", "stage": "dd2"},
        {"id": "BOND-02-006", "file": "募集资金用途可行性分析", "req": "含项目备案/环评/用地/资本金到位证明", "stage": "dd2"},
    ],
    "DD-BOND-03 增信与担保": [
        {"id": "BOND-03-001", "file": "担保方主体资格及内部决议", "req": "含担保方营业执照、章程、董事会/股东会决议", "stage": "dd1"},
        {"id": "BOND-03-002", "file": "担保方审计报告及信用分析", "req": "含资产负债率、偿债能力、或有负债、代偿能力评估", "stage": "dd1"},
        {"id": "BOND-03-003", "file": "抵/质押资产评估报告", "req": "含评估基准日/评估方法/评估结论/抵押率/变现分析", "stage": "dd1"},
        {"id": "BOND-03-004", "file": "差额补偿/流动性支持/维好协议", "req": "含触发条件、补偿上限、法律可执行性分析", "stage": "dd2"},
        {"id": "BOND-03-005", "file": "交叉违约及加速到期条款汇总", "req": "含全部融资文件中可能触发交叉违约的条款", "stage": "dd2"},
    ],
    "DD-BOND-04 合规与评级": [
        {"id": "BOND-04-001", "file": "信用评级报告（如有）", "req": "含主体评级/债项评级/评级展望/关键假设", "stage": "dd0"},
        {"id": "BOND-04-002", "file": "诉讼/仲裁/行政处罚汇总", "req": "含案件清单、涉案金额、对偿债能力影响评估", "stage": "dd1"},
        {"id": "BOND-04-003", "file": "合规证明文件汇编", "req": "含税务/社保/公积金/海关/外汇/环保等合规证明", "stage": "dd1"},
        {"id": "BOND-04-004", "file": "隐性债务排查报告（城投适用）", "req": "含地方政府隐性债务、公益性资产注入、财政补贴依赖分析", "stage": "dd2"},
    ],
}

TYPE_MAP = {"ipo": IPO_CHECKLIST, "ma": MA_CHECKLIST, "bond": BOND_CHECKLIST}
TYPE_LABELS = {"ipo": "IPO", "ma": "M&A", "bond": "Bond"}
STAGE_LABELS = {"dd0": "Pre-DD (预尽调)", "dd1": "Formal DD (正式尽调)", "dd2": "Deep DD (深度尽调)"}
STAGE_MIN_LEVELS = {"dd0": ["dd0"], "dd1": ["dd0", "dd1"], "dd2": ["dd0", "dd1", "dd2"]}


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def generate_checklist(proj_type: str, stage: str) -> Dict[str, List[Dict[str, str]]]:
    """Generate filtered checklist for project type and stage."""
    checklist = TYPE_MAP[proj_type]
    allowed_stages = STAGE_MIN_LEVELS[stage]
    result: Dict[str, List[Dict[str, str]]] = {}

    for section, items in checklist.items():
        filtered = [item for item in items if item["stage"] in allowed_stages]
        if filtered:
            result[section] = filtered

    return result


def count_items(checklist: Dict[str, List[Dict[str, str]]]) -> int:
    return sum(len(items) for items in checklist.values())


def format_markdown(checklist: Dict[str, List[Dict[str, str]]], proj_type: str, stage: str) -> str:
    lines = [
        f"# {TYPE_LABELS[proj_type]} 尽职调查资料清单",
        f"## 阶段：{STAGE_LABELS[stage]}",
        f"## 统计：{count_items(checklist)} 项资料\n",
    ]
    for section, items in checklist.items():
        lines.append(f"### {section}（{len(items)} 项）\n")
        lines.append("| 编号 | 文件名称 | 要求说明 |")
        lines.append("|------|----------|----------|")
        for item in items:
            lines.append(f"| {item['id']} | {item['file']} | {item['req']} |")
        lines.append("")
    return "\n".join(lines)


def format_text(checklist: Dict[str, List[Dict[str, str]]], proj_type: str, stage: str) -> str:
    lines = [
        f"{'=' * 60}",
        f"  {TYPE_LABELS[proj_type]} 尽职调查资料清单",
        f"  阶段：{STAGE_LABELS[stage]}",
        f"  合计：{count_items(checklist)} 项资料",
        f"{'=' * 60}",
    ]
    for section, items in checklist.items():
        lines.append(f"\n--- {section}（{len(items)} 项） ---")
        for item in items:
            lines.append(f"  [{item['id']}] {item['file']}")
            lines.append(f"       要求：{item['req']}")
    lines.append(f"\n{'=' * 60}\n")
    return "\n".join(lines)


def format_json(checklist: Dict[str, List[Dict[str, str]]], proj_type: str, stage: str) -> str:
    output = {
        "project_type": TYPE_LABELS[proj_type],
        "stage": STAGE_LABELS[stage],
        "total_items": count_items(checklist),
        "sections": [],
    }
    for section, items in checklist.items():
        output["sections"].append({
            "section": section,
            "count": len(items),
            "items": items,
        })
    return json.dumps(output, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Built-in test case (15 representative IPO items)
# ---------------------------------------------------------------------------

TEST_OUTPUT = """
============================================================
  IPO 尽职调查资料清单 — Test Case（15个代表性文件）
  阶段：Formal DD (正式尽调)
============================================================

--- DD-00 项目管理（代表性 3 项）---
  [DD-00-001] 委任书及补充协议
       要求：含服务范围、收费安排、终止条款；签字盖章页完整
  [DD-00-004] 中介机构保密协议及利益冲突声明
       要求：各中介签字版，含独立性确认
  [DD-00-006] 阶段性工作会议纪要
       要求：每次工作会议后24小时内完成，含出席、议题、决议、行动项

--- DD-01 主体资格（代表性 3 项）---
  [DD-01-001] 营业执照（含历史版本）
       要求：最新版+历史变更版本，验证经营范围、有效期、统一社会信用代码
  [DD-01-003] 工商登记档案全册
       要求：自设立至今全部工商登记资料，加盖市监局查询章
  [DD-01-009] 业务资质/许可证清单及复印件
       要求：所有生产经营所需资质，标注有效期和续期条件

--- DD-02 股权结构（代表性 2 项）---
  [DD-02-001] 股权架构图（穿透至最终权益持有人）
       要求：含控制路径、持股比例、投票权与收益权差异
  [DD-02-003] 实际控制人身份证明及简历
       要求：含身份证明文件、教育/工作经历、对外投资和任职情况

--- DD-03 主要资产（代表性 2 项）---
  [DD-03-001] 不动产权证/土地使用权证
       要求：含出让合同、土地出让金缴纳凭证、使用权证；标注权利限制
  [DD-03-003] 专利证书及年费缴纳凭证
       要求：含发明/实用新型/外观设计全部专利，验证法律状态

--- DD-04 重大合同（代表性 2 项）---
  [DD-04-001] 银行借款合同及授信协议
       要求：全部存续借款合同，含金额/利率/期限/担保/约束性条款
  [DD-04-002] 对外担保合同
       要求：含保证/抵押/质押合同、主债权合同、担保决议文件

--- DD-05 财务资料（代表性 2 项）---
  [DD-05-001] 审计报告（最近3年+1期）
       要求：含审计意见、附注、关键审计事项；若含否定/保留/强调事项需专项分析
  [DD-05-002] 银行账户清单及对账单
       要求：含全部开户行/账号/币种/余额；报告期每月对账单（银行盖章）

--- DD-06 业务与技术（代表性 1 项）---
  [DD-06-001] 行业研究报告
       要求：多家独立第三方（≥2家），含市场规模/增速/竞争格局

============================================================
  合计：15 项代表性文件（完整版共 100+ 项）
============================================================
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="IB Due Diligence Checklist Generator — 尽调资料清单生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --type ipo --stage dd1
  %(prog)s --type ipo --stage dd2 --format markdown
  %(prog)s --type ma --stage dd0 --json
  %(prog)s --test
        """,
    )
    parser.add_argument("--type", choices=["ipo", "ma", "bond"],
                        help="项目类型")
    parser.add_argument("--stage", choices=["dd0", "dd1", "dd2"], default="dd1",
                        help="尽调深度阶段 (dd0=预尽调/dd1=正式尽调/dd2=深度尽调)")
    parser.add_argument("--format", choices=["markdown", "text"], default="text",
                        help="输出格式")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式")
    parser.add_argument("--test", action="store_true",
                        help="运行内置测试用例（展示15个代表性IPO文件）")

    args = parser.parse_args()

    # --test mode
    if args.test:
        print(TEST_OUTPUT.strip())
        return

    if not args.type:
        parser.error("--type is required (unless --test)")

    proj_type = args.type
    stage = args.stage
    checklist = generate_checklist(proj_type, stage)

    if args.json:
        print(format_json(checklist, proj_type, stage))
    elif args.format == "markdown":
        print(format_markdown(checklist, proj_type, stage))
    else:
        print(format_text(checklist, proj_type, stage))


if __name__ == "__main__":
    main()