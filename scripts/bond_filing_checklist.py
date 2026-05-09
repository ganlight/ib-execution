#!/usr/bin/env python3
"""
Bond Filing Checklist Generator — Chinese Bond Registration Document Builder.

Generates a complete, regulation-compliant filing checklist for major onshore
Chinese bond products, organized by document category with M/C/O (mandatory /
conditional / optional) markings.

Supported products:
  MTN           中期票据 (NAFMII)
  CP            短期融资券 (NAFMII)
  SCP           超短期融资券 (NAFMII)
  PPN           定向工具 (NAFMII)
  企业债         企业债券 (NDRC)
  公司债（公募）  公募公司债 (CSRC + Exchange)
  公司债（私募）  私募公司债 (Exchange filing)
  金融债         金融债券 (PBOC/CBIRC/NFRA)
  ABS           资产支持证券 (Exchange/NAFMII)
  REITs         基础设施公募REITs (CSRC)
  可转债         可转换公司债 (CSRC)

Usage:
  python bond_filing_checklist.py --product MTN
  python bond_filing_checklist.py --product 企业债 --status filed.txt
  python bond_filing_checklist.py --json --product ABS
  python bond_filing_checklist.py --test
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class FilingItem:
    """A single filing/document item in the checklist."""

    file_name: str          # 文件名（监管标准命名）
    category: str           # 文件大类
    subcategory: str        # 文件小类
    issuer: str             # 出具方
    copies_original: int    # 正本份数
    copies_duplicate: int   # 副本份数
    requirement: str        # M=必需, C=条件性, O=可选
    remarks: str            # 备注（特殊要求）
    product_tag: str = ""   # 品种标签（用于差异化过滤）


@dataclass
class ChecklistResult:
    """Complete filing checklist for one bond product."""

    product: str
    product_full_name: str
    regulatory_system: str
    regulatory_notes: str
    categories: Dict[str, List[FilingItem]]
    summary: Dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Product metadata
# ---------------------------------------------------------------------------

PRODUCT_META: Dict[str, Dict] = {
    "MTN": {
        "full_name": "中期票据 (Medium-Term Note)",
        "system": "NAFMII银行间市场交易商协会",
        "notes": (
            "NAFMII注册制，DFI/TDFI分层管理，有效期2年可续期。"
            "NAFMII公告〔2023〕1号及配套指引适用。"
        ),
    },
    "CP": {
        "full_name": "短期融资券 (Commercial Paper)",
        "system": "NAFMII银行间市场交易商协会",
        "notes": (
            "期限≤1年，NAFMII注册制，面向银行间市场合格机构投资者。"
        ),
    },
    "SCP": {
        "full_name": "超短期融资券 (Super Commercial Paper)",
        "system": "NAFMII银行间市场交易商协会",
        "notes": (
            "期限≤270天，AAA主体专用，NAFMII注册制，可用于流动资金周转。"
        ),
    },
    "PPN": {
        "full_name": "定向工具 (Private Placement Note)",
        "system": "NAFMII银行间市场交易商协会",
        "notes": (
            "定向发行，≤200名合格投资者，信息披露要求较低，不强制评级。"
        ),
    },
    "企业债": {
        "full_name": "企业债券 (Enterprise Bond)",
        "system": "国家发展改革委 (NDRC)",
        "notes": (
            "发改委注册制（2020年改革后），需省级发改委转报。"
            "募投项目需取得可研批复、环评、土地预审等文件。"
            "仅限国有企业或国有控股企业发行。"
        ),
    },
    "公司债（公募）": {
        "full_name": "公募公司债券 (Public Corporate Bond)",
        "system": "中国证监会 (CSRC) + 证券交易所",
        "notes": (
            "需取得CSRC注册批复，面向公众投资者或合格投资者。"
            "发行人应符合《证券法》《公司债券发行与交易管理办法》要求。"
            "公开发行债券累计余额不超过最近一期净资产的40%。"
        ),
    },
    "公司债（私募）": {
        "full_name": "私募公司债券 (Private Corporate Bond)",
        "system": "证券交易所备案制",
        "notes": (
            "交易所备案，无需CSRC注册批复。≤200名合格投资者。"
            "备案后由交易所出具《无异议函》即可发行。"
            "信息披露不公开，挂牌转让（非上市交易）。"
        ),
    },
    "金融债": {
        "full_name": "金融债券 (Financial Bond)",
        "system": "中国人民银行 (PBOC) + 国家金融监督管理总局 (NFRA)",
        "notes": (
            "金融监管总局（原银保监会）批复 + 人民银行核准。"
            "仅限持牌金融机构发行。包括普通金融债、二级资本债、永续债等。"
        ),
    },
    "ABS": {
        "full_name": "资产支持证券 (Asset-Backed Security)",
        "system": "证券交易所/NAFMII（信贷ABS为银登中心）",
        "notes": (
            "以基础资产产生的现金流为偿付支持，结构化分层设计。"
            "需提供资产池尽调报告、现金流预测报告等特殊文件。"
        ),
    },
    "REITs": {
        "full_name": "基础设施公募REITs (Public Infrastructure REIT)",
        "system": "中国证监会 (CSRC) + 证券交易所",
        "notes": (
            "试点阶段，需取得基础设施项目合规文件（土地证、规划许可、环评等）。"
            "原始权益人需持有不低于20%的份额。资产评估报告由独立评估机构出具。"
        ),
    },
    "可转债": {
        "full_name": "可转换公司债券 (Convertible Bond)",
        "system": "中国证监会 (CSRC) + 证券交易所",
        "notes": (
            "上市公司发行，需取得CSRC核准批文。"
            "转股价格不低于募集说明书公告日前20个交易日股票均价。"
            "需提供最近三年加权平均净资产收益率（ROE）≥6%。"
        ),
    },
}


# ---------------------------------------------------------------------------
# Checklist data — organized by category with product tags
# ---------------------------------------------------------------------------

def _build_all_items() -> Dict[str, List[FilingItem]]:
    """Build the full catalog of filing items across all categories.

    Tags indicate which products the item applies to:
      ALL  = all products
      NAF  = NAFMII products (MTN, CP, SCP, PPN)
      NDRC = 企业债
      CSC  = CSRC public (公司债公募, 可转债)
      CSCP = CSRC private (公司债私募)
      ABS  = ABS
      REIT = REITs
      FIN  = 金融债
      C   = 公司债公募+私募
      L   = 仅上市公司（可转债+公募公司债）
    """

    categories: Dict[str, List[FilingItem]] = {}

    # ---- 1. 注册/备案文件 ----
    categories["注册/备案文件"] = [
        FilingItem("注册申请书/备案登记表", "注册/备案文件", "主文件",
                   "主承销商", 3, 3, "M",
                   "发行人盖章+法定代表人签字", "ALL"),
        FilingItem("有权机构决议文件（董事会/股东会决议）", "注册/备案文件", "内部决议",
                   "发行人", 1, 3, "M",
                   "需原件，载明发行额度、期限、募集资金用途等事项", "ALL"),
        FilingItem("接受注册通知书",
                   "注册/备案文件", "监管批复",
                   "NAFMII", 1, 3, "M",
                   "NAFMII出具，有效期2年", "NAF"),
        FilingItem("国家发展改革委注册通知书/批文",
                   "注册/备案文件", "监管批复",
                   "国家发改委", 1, 3, "M",
                   "发改委注册制批复文件", "NDRC"),
        FilingItem("省级发改委转报文件",
                   "注册/备案文件", "监管批复",
                   "省级发改委", 1, 3, "M",
                   "省级发改委向国家发改委转报的请示文件", "NDRC"),
        FilingItem("募投项目可行性研究报告批复",
                   "注册/备案文件", "监管批复",
                   "项目审批部门", 1, 2, "M",
                   "各募投项目均需取得可研批复", "NDRC"),
        FilingItem("中国证监会注册批复",
                   "注册/备案文件", "监管批复",
                   "中国证监会", 1, 3, "M",
                   "《关于同意XX公司向专业投资者公开发行公司债券注册的批复》",
                   "CSC"),
        FilingItem("交易所无异议函/挂牌转让无异议函",
                   "注册/备案文件", "监管批复",
                   "证券交易所", 1, 3, "M",
                   "交易所出具，私募公司债为备案确认函",
                   "CSCP"),
        FilingItem("金融监管总局（原银保监会）批复文件",
                   "注册/备案文件", "监管批复",
                   "金融监管总局", 1, 3, "M",
                   "金融监管总局出具的同意发行批复", "FIN"),
        FilingItem("中国人民银行行政许可决定书",
                   "注册/备案文件", "监管批复",
                   "中国人民银行", 1, 3, "M",
                   "人民银行金融市场司核准", "FIN"),
        FilingItem("金融许可证",
                   "注册/备案文件", "资质证明",
                   "金融监管总局", 1, 2, "M",
                   "发行人金融许可证复印件加盖公章", "FIN"),
        FilingItem("中国证监会核准批复（可转债）",
                   "注册/备案文件", "监管批复",
                   "中国证监会", 1, 3, "M",
                   "可转债需CSRC核准批文，有效期12个月", "L"),
        FilingItem("上交所/深交所挂牌转让无异议函（REITs）",
                   "注册/备案文件", "监管批复",
                   "证券交易所", 1, 3, "M",
                   "交易所出具，作为上市交易的依据", "REIT"),
    ]

    # ---- 2. 募集说明书及相关 ----
    categories["募集说明书及相关"] = [
        FilingItem("募集说明书", "募集说明书及相关", "主文件",
                   "主承销商/发行人", 5, 10, "M",
                   "全体董监高签署声明，主承销商加盖公章", "ALL"),
        FilingItem("募集说明书摘要", "募集说明书及相关", "主文件",
                   "主承销商", 2, 5, "M",
                   "2000-3000字摘要，用于公开信息披露", "ALL"),
        FilingItem("发行人关于本次债券发行的申请报告", "募集说明书及相关", "申请报告",
                   "发行人", 1, 3, "M",
                   "发行人的正式申请报告文件", "ALL"),
        FilingItem("尽职调查报告", "募集说明书及相关", "尽调文件",
                   "主承销商", 1, 3, "M",
                   "主承销商内核后出具，含财务分析、业务分析、风险分析", "ALL"),
        FilingItem("发行人全体董监高对发行文件的确认意见", "募集说明书及相关", "承诺文件",
                   "发行人董监高", 1, 2, "M",
                   "全体签字，不可代签", "ALL"),
        FilingItem("信用评级机构出具的跟踪评级安排说明",
                   "募集说明书及相关", "评级安排",
                   "信用评级机构", 1, 2, "C",
                   "如有评级，需明确跟踪评级安排", "ALL"),
    ]

    # ---- 3. 财务文件 ----
    categories["财务文件"] = [
        FilingItem("最近三年及一期审计报告（合并口径）",
                   "财务文件", "审计报告",
                   "会计师事务所", 1, 3, "M",
                   "具备证券期货从业资格的会计师事务所出具，标准无保留意见",
                   "ALL"),
        FilingItem("最近一期未经审计财务报表", "财务文件", "财务报表",
                   "发行人", 1, 2, "M",
                   "最近一期（季度或半年），发行人盖章", "ALL"),
        FilingItem("备考合并财务报表（如有重大资产重组）",
                   "财务文件", "备考报表",
                   "会计师事务所", 1, 2, "C",
                   "最近一年内有重大资产重组时提供", "ALL"),
        FilingItem("发行人财务情况说明书", "财务文件", "财务说明",
                   "发行人", 1, 2, "M",
                   "对主要财务指标变动原因的说明", "ALL"),
        FilingItem("最近三年加权平均净资产收益率（ROE）计算表",
                   "财务文件", "专项计算",
                   "会计师事务所", 1, 2, "M",
                   "ROE≥6%（可转债要求），会计师出具专项鉴证报告",
                   "L"),
        FilingItem("资产池基础资产财务数据及统计分析",
                   "财务文件", "资产池",
                   "原始权益人/计划管理人", 1, 3, "M",
                   "含入池资产明细、历史违约率、早偿率等", "ABS"),
        FilingItem("基础设施项目财务报告及预测", "财务文件", "项目财务",
                   "原始权益人/基金管理人", 1, 3, "M",
                   "含历史运营数据和未来现金流预测", "REIT"),
    ]

    # ---- 4. 评级文件 ----
    categories["评级文件"] = [
        FilingItem("主体信用评级报告", "评级文件", "主体评级",
                   "信用评级机构", 1, 3, "C",
                   "NAFMII要求主体评级在AA及以上（PPN除外）；有评级时需提供评级报告全文",
                   "ALL"),
        FilingItem("债项信用评级报告", "评级文件", "债项评级",
                   "信用评级机构", 1, 3, "C",
                   "如有债项评级则需提供；PPN可不评级",
                   "ALL"),
        FilingItem("跟踪评级安排说明", "评级文件", "评级安排",
                   "信用评级机构", 1, 2, "C",
                   "明确跟踪评级的时间安排和方法", "ALL"),
        FilingItem("资产支持证券分层评级报告",
                   "评级文件", "分层评级",
                   "信用评级机构", 1, 3, "M",
                   "对各档证券（优先/夹层/次级）分别出具评级", "ABS"),
    ]

    # ---- 5. 法律文件 ----
    categories["法律文件"] = [
        FilingItem("法律意见书", "法律文件", "主文件",
                   "律师事务所", 1, 3, "M",
                   "具备证券法律业务资格的律所出具，两名律师签字",
                   "ALL"),
        FilingItem("内控鉴证报告/内控审计报告", "法律文件", "内控文件",
                   "会计师事务所", 1, 2, "C",
                   "部分品种要求内控审计报告", "ALL"),
        FilingItem("发行人近三年合规经营证明（工商、税务、社保等）",
                   "法律文件", "合规文件",
                   "各主管部门", 1, 2, "M",
                   "工商、税务、社保、海关、环保等部门的无重大违法违规证明",
                   "ALL"),
        FilingItem("发行人及控股股东/实际控制人征信报告",
                   "法律文件", "征信文件",
                   "人民银行征信中心", 1, 2, "M",
                   "最近一期企业信用报告", "ALL"),
        FilingItem("发行人不存在重大诉讼/仲裁的声明",
                   "法律文件", "声明文件",
                   "发行人/律师事务所", 1, 2, "M",
                   "发行人盖章声明，律师在法律意见书中确认", "ALL"),
        FilingItem("发改委募投项目合规性审查意见",
                   "法律文件", "募投合规",
                   "省级发改委", 1, 2, "M",
                   "就募投项目的合规性出具审查意见", "NDRC"),
        FilingItem("募投项目环评批复/备案",
                   "法律文件", "募投合规",
                   "环保部门", 1, 2, "M",
                   "每个募投项目均需取得环评批复", "NDRC"),
        FilingItem("募投项目土地预审意见",
                   "法律文件", "募投合规",
                   "自然资源部门", 1, 2, "M",
                   "每个募投项目均需取得土地预审意见", "NDRC"),
        FilingItem("募投项目规划许可",
                   "法律文件", "募投合规",
                   "规划部门", 1, 2, "M",
                   "建设用地规划许可证+建设工程规划许可证", "NDRC"),
    ]

    # ---- 6. 承销文件 ----
    categories["承销文件"] = [
        FilingItem("承销协议", "承销文件", "主协议",
                   "发行人与主承销商", 3, 3, "M",
                   "双方签字盖章，载明承销方式、费率、权利义务",
                   "ALL"),
        FilingItem("承销团协议（如有承销团）", "承销文件", "承销团",
                   "主承销商与联席承销商", 1, 3, "C",
                   "由多家承销商组成承销团时签署",
                   "ALL"),
        FilingItem("主承销商尽职调查报告", "承销文件", "尽调报告",
                   "主承销商", 1, 3, "M",
                   "主承销商内核委员会审议通过", "ALL"),
        FilingItem("主承销商推荐意见/内核意见", "承销文件", "推荐意见",
                   "主承销商", 1, 2, "M",
                   "主承销商内部立项、内核通过的文件", "ALL"),
        FilingItem("资产服务协议", "承销文件", "特殊协议",
                   "计划管理人与资产服务机构", 2, 2, "M",
                   "约定资产服务机构的管理职责和服务报酬", "ABS"),
        FilingItem("承销协议（REITs）", "承销文件", "主协议",
                   "基金管理人与财务顾问/承销商", 3, 3, "M",
                   "公募REITs的基金份额销售协议", "REIT"),
    ]

    # ---- 7. 担保/增信文件 ----
    categories["担保/增信文件"] = [
        FilingItem("担保函/保证合同", "担保/增信文件", "保证担保",
                   "担保人", 1, 3, "C",
                   "如有第三方保证担保时提供，担保人盖章+法定代表人签字",
                   "ALL"),
        FilingItem("抵/质押合同", "担保/增信文件", "抵质押担保",
                   "担保人与发行人", 1, 3, "C",
                   "如有资产抵质押时提供，需完成抵质押登记",
                   "ALL"),
        FilingItem("担保人最近一年审计报告", "担保/增信文件", "担保人财务",
                   "担保人/会计师事务所", 1, 2, "C",
                   "如有担保人，需提供其最新审计报告", "ALL"),
        FilingItem("担保人内部有权机构决议文件",
                   "担保/增信文件", "担保人决议",
                   "担保人", 1, 2, "C",
                   "担保人董事会/股东会同意提供担保的决议", "ALL"),
        FilingItem("差额补足承诺函", "担保/增信文件", "增信文件",
                   "增信方", 1, 2, "C",
                   "如有差额补足安排", "ALL"),
        FilingItem("流动性支持函", "担保/增信文件", "增信文件",
                   "支持方", 1, 2, "C",
                   "如有流动性支持安排", "ALL"),
        FilingItem("内部分层/优先劣后结构化安排说明",
                   "担保/增信文件", "结构化增信",
                   "计划管理人", 1, 3, "M",
                   "ABS结构化增信安排", "ABS"),
    ]

    # ---- 8. 发行人资质文件 ----
    categories["发行人资质文件"] = [
        FilingItem("营业执照（副本）复印件", "发行人资质文件", "主体资格",
                   "发行人", 1, 3, "M",
                   "加盖发行人公章的最新营业执照", "ALL"),
        FilingItem("公司章程（含修正案）", "发行人资质文件", "主体资格",
                   "发行人", 1, 3, "M",
                   "工商备案的最新章程及所有修正案", "ALL"),
        FilingItem("行业资质/许可证书", "发行人资质文件", "行业许可",
                   "各主管部门", 1, 2, "C",
                   "如属于特许经营行业，需提供相关资质证书", "ALL"),
        FilingItem("金融许可证", "发行人资质文件", "行业许可",
                   "金融监管总局", 1, 2, "M",
                   "金融机构必备的金融许可证", "FIN"),
        FilingItem("发行人公司章程规定的对外担保/借款权限说明",
                   "发行人资质文件", "授权说明",
                   "发行人", 1, 2, "M",
                   "说明本次发行是否符合公司章程规定的权限", "ALL"),
        FilingItem("基础设施项目合规文件（土地证+规划许可+环评）",
                   "发行人资质文件", "项目合规",
                   "各主管部门", 1, 3, "M",
                   "每个基础设施项目的全套合规文件", "REIT"),
        FilingItem("资产评估报告",
                   "发行人资质文件", "评估报告",
                   "独立资产评估机构", 1, 3, "M",
                   "基础设施项目的市场价值评估报告", "REIT"),
    ]

    # ---- 9. ABS 特殊文件 ----
    categories["资产支持证券专项文件"] = [
        FilingItem("资产池尽调报告", "资产支持证券专项文件", "尽调",
                   "计划管理人/律师事务所", 1, 3, "M",
                   "对基础资产的全面尽职调查", "ABS"),
        FilingItem("现金流预测报告/压力测试报告",
                   "资产支持证券专项文件", "现金流分析",
                   "会计师事务所/评级机构", 1, 3, "M",
                   "对基础资产未来现金流的预测及压力测试分析", "ABS"),
        FilingItem("标准条款/信托合同", "资产支持证券专项文件", "交易文件",
                   "计划管理人", 1, 3, "M",
                   "约定证券化交易结构的核心文件", "ABS"),
        FilingItem("资产买卖协议", "资产支持证券专项文件", "交易文件",
                   "原始权益人与计划管理人", 2, 3, "M",
                   "基础资产的买卖/转让协议", "ABS"),
        FilingItem("托管协议", "资产支持证券专项文件", "交易文件",
                   "计划管理人与托管银行", 1, 2, "M",
                   "托管银行负责资金监管和划付", "ABS"),
    ]

    # ---- 10. REITs 特殊文件 (beyond usual) ----
    categories["REITs专项文件"] = [
        FilingItem("基金合同/招募说明书", "REITs专项文件", "基金文件",
                   "基金管理人", 3, 10, "M",
                   "公募REITs的基金合同和招募说明书", "REIT"),
        FilingItem("基础设施项目运营管理协议", "REITs专项文件", "运营协议",
                   "基金管理人与运营管理机构", 3, 3, "M",
                   "基础设施的运营管理安排", "REIT"),
        FilingItem("基金托管协议（REITs）", "REITs专项文件", "托管协议",
                   "基金管理人与托管银行", 1, 2, "M",
                   "公募REITs的基金资产托管", "REIT"),
        FilingItem("原始权益人持有份额承诺函",
                   "REITs专项文件", "承诺文件",
                   "原始权益人", 1, 2, "M",
                   "承诺持有不低于20%份额且锁定不少于5年", "REIT"),
        FilingItem("项目公司股权转让协议",
                   "REITs专项文件", "交易文件",
                   "原始权益人与项目公司", 2, 3, "M",
                   "基础设施项目公司的股权转让安排", "REIT"),
    ]

    return categories


ALL_CATEGORIES = _build_all_items()

# Map tags to product names
TAG_PRODUCT_MAP: Dict[str, List[str]] = {
    "ALL":  ["MTN", "CP", "SCP", "PPN", "企业债", "公司债（公募）", "公司债（私募）",
             "金融债", "ABS", "REITs", "可转债"],
    "NAF":  ["MTN", "CP", "SCP", "PPN"],
    "NDRC": ["企业债"],
    "CSC":  ["公司债（公募）", "可转债"],
    "CSCP": ["公司债（私募）"],
    "C":    ["公司债（公募）", "公司债（私募）"],
    "L":    ["公司债（公募）", "可转债"],
    "ABS":  ["ABS"],
    "REIT": ["REITs"],
    "FIN":  ["金融债"],
}


def product_matches_tag(product: str, tag: str) -> bool:
    """Check if a product is covered by a given tag."""
    if tag == "ALL":
        return True
    products = TAG_PRODUCT_MAP.get(tag, [])
    return product in products


# ---------------------------------------------------------------------------
# Checklist filtering
# ---------------------------------------------------------------------------

def generate_checklist(product: str) -> ChecklistResult:
    """Generate the complete filing checklist for a given bond product.

    Args:
        product: The bond product identifier (e.g. MTN, 企业债, ABS).

    Returns:
        A ChecklistResult with all applicable filing items organized by category.
    """
    if product not in PRODUCT_META:
        valid = ", ".join(PRODUCT_META.keys())
        raise ValueError(f"Unknown product: {product}. Valid options: {valid}")

    meta = PRODUCT_META[product]
    result = ChecklistResult(
        product=product,
        product_full_name=meta["full_name"],
        regulatory_system=meta["system"],
        regulatory_notes=meta["notes"],
        categories={},
        summary={"M": 0, "C": 0, "O": 0, "total": 0},
    )

    for cat_name, items in ALL_CATEGORIES.items():
        applicable = [
            item for item in items
            if product_matches_tag(product, item.product_tag)
        ]
        if applicable:
            result.categories[cat_name] = applicable
            for item in applicable:
                result.summary[item.requirement] = result.summary.get(item.requirement, 0) + 1
                result.summary["total"] += 1

    return result


# ---------------------------------------------------------------------------
# Status check helper
# ---------------------------------------------------------------------------

def load_status(status_path: Optional[str]) -> Set[str]:
    """Load completed file names from a status file (one per line)."""
    if not status_path:
        return set()
    try:
        with open(status_path, "r", encoding="utf-8") as fh:
            return {line.strip() for line in fh if line.strip()}
    except FileNotFoundError:
        print(f"Warning: status file not found: {status_path}", file=sys.stderr)
        return set()


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------

def _req_label(req: str) -> str:
    """Return M/C/O display label."""
    if req == "M":
        return "必需[M]"
    elif req == "C":
        return "条件[C]"
    return "可选[O]"


def _check_mark(name: str, completed: Set[str]) -> str:
    """Return ✅ if the file name appears in the completed set."""
    # Try exact match and fuzzy (substring) match
    if name in completed:
        return "✅"
    for done in completed:
        if done in name or name in done:
            return "✅"
    return "⬜"


def print_checklist(checklist: ChecklistResult,
                    completed: Set[str] = None) -> None:
    """Pretty-print the filing checklist with categories and items."""
    if completed is None:
        completed = set()
    has_status = bool(completed)

    print("=" * 80)
    print(f"  债券申报文件清单 — {checklist.product_full_name}")
    print("=" * 80)
    print(f"  品种:         {checklist.product}")
    print(f"  监管体系:     {checklist.regulatory_system}")
    print(f"  监管说明:     {checklist.regulatory_notes}")
    print(f"  文件总计:     {checklist.summary['total']} "
          f"(M必需: {checklist.summary.get('M', 0)}, "
          f"C条件: {checklist.summary.get('C', 0)}, "
          f"O可选: {checklist.summary.get('O', 0)})")
    if has_status:
        done_count = sum(
            1 for items in checklist.categories.values()
            for item in items
            if _check_mark(item.file_name, completed) == "✅"
        )
        pct = done_count / checklist.summary["total"] * 100 if checklist.summary["total"] else 0
        print(f"  完成进度:     {done_count}/{checklist.summary['total']} ({pct:.0f}%)")
    print()

    cat_num = 0
    for cat_name, items in checklist.categories.items():
        cat_num += 1
        print("-" * 80)
        print(f"  #{cat_num} {cat_name}  ({len(items)} 项)")
        print("-" * 80)

        # Column headers
        status_col = "完成" if has_status else ""
        if has_status:
            print(f"  {'状态':<6s} {'序号':<5s} {'文件名':<36s} {'出具方':<12s} {'份数':<6s} {'必需':<6s}")
        else:
            print(f"  {'序号':<5s} {'文件名':<36s} {'出具方':<12s} {'份数':<6s} {'必需':<6s}")

        for idx, item in enumerate(items, 1):
            copies = f"{item.copies_original}+{item.copies_duplicate}"
            if has_status:
                mark = _check_mark(item.file_name, completed)
                print(
                    f"  {mark:<6s} {idx:<5d} {item.file_name:<36s} "
                    f"{item.issuer:<12s} {copies:<6s} {_req_label(item.requirement):<6s}"
                )
            else:
                print(
                    f"  {idx:<5d} {item.file_name:<36s} "
                    f"{item.issuer:<12s} {copies:<6s} {_req_label(item.requirement):<6s}"
                )

            # Print remarks if they exist
            if item.remarks:
                indent = " " * (8 if has_status else 8)
                print(f"  {indent}→ {item.remarks}")

        print()

    print("=" * 80)
    print("  M = 必需 (Mandatory)    C = 条件性 (Conditional)    O = 可选 (Optional)")
    print("  ✅ = 已完成    ⬜ = 待处理")
    print("=" * 80)


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def json_output(checklist: ChecklistResult,
                completed: Set[str] = None) -> None:
    """Output structured checklist as JSON."""
    if completed is None:
        completed = set()
    has_status = bool(completed)

    payload = {
        "product": checklist.product,
        "product_full_name": checklist.product_full_name,
        "regulatory_system": checklist.regulatory_system,
        "regulatory_notes": checklist.regulatory_notes,
        "summary": checklist.summary,
        "checklist": {},
    }

    for cat_name, items in checklist.categories.items():
        payload["checklist"][cat_name] = []
        for item in items:
            entry = {
                "file_name": item.file_name,
                "category": item.category,
                "subcategory": item.subcategory,
                "issuer": item.issuer,
                "copies": {
                    "original": item.copies_original,
                    "duplicate": item.copies_duplicate,
                },
                "requirement": item.requirement,
                "remarks": item.remarks,
            }
            if has_status:
                entry["completed"] = _check_mark(item.file_name, completed) == "✅"
            payload["checklist"][cat_name].append(entry)

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    product_choices = list(PRODUCT_META.keys())
    p = argparse.ArgumentParser(
        description="债券申报文件清单生成器 (Bond Filing Checklist Generator)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported products: {', '.join(product_choices)}

Examples:
  %(prog)s --product MTN
  %(prog)s --product 企业债 --status completed_files.txt
  %(prog)s --json --product ABS
  %(prog)s --product REITs --status progress.txt
        """,
    )
    p.add_argument("--product", choices=product_choices, required=True,
                   help="债券品种")
    p.add_argument("--status", dest="status_path", default=None,
                   help="已完成文件列表的路径（每行一个文件名），用于显示 ✅/⬜ 状态")
    p.add_argument("--json", dest="json_out", action="store_true",
                   help="Output JSON instead of formatted text")
    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        checklist = generate_checklist(args.product)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    completed = load_status(args.status_path)

    if args.json_out:
        json_output(checklist, completed)
    else:
        print_checklist(checklist, completed)


# ---------------------------------------------------------------------------
# Built-in test cases (run with: python bond_filing_checklist.py --test)
# ---------------------------------------------------------------------------

_TEST_CASES: List[List[str]] = [
    # Test 1: MTN (NAFMII system)
    ["--product", "MTN"],

    # Test 2: 企业债 (NDRC system with 募投项目 files)
    ["--product", "企业债"],

    # Test 3: ABS (asset pool differentiated files)
    ["--product", "ABS"],
]


def run_tests() -> None:
    """Exercise the checklist generator with built-in test products."""
    for i, args in enumerate(_TEST_CASES, 1):
        product = args[1]
        meta = PRODUCT_META.get(product, {})
        print(f"\n{'='*80}")
        print(f"  TEST CASE {i}: {product} — {meta.get('full_name', '')}")
        print(f"{'='*80}")
        main(args)
        print()


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        run_tests()
    else:
        main()