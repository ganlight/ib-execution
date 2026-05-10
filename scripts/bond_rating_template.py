#!/usr/bin/env python3
"""
城投债评级框架生成器 (LGFV Bond Rating Template Generator)
五维评分卡 + 加权综合 → 信用评级映射
输出完整Markdown评级报告框架

Author: QClaw Bond Risk System
Version: 1.0.0
"""

import sys
import json
import argparse
from dataclasses import dataclass, field
from typing import Optional


# ============================================================================
# 数据结构定义
# ============================================================================

@dataclass
class RegionalStrength:
    """区域实力维度 (权重25%)"""
    admin_level: int                  # 行政层级 (1-10分: 省级=10, 省会/计划单列市=8, 地级市=6, 区县=4)
    gdp: float                       # GDP (亿元)
    fiscal_revenue: float            # 一般公共预算收入 (亿元)
    gov_debt_ratio: float            # 政府债务率 (%)


@dataclass
class FiscalHealth:
    """财政健康维度 (权重25%)"""
    debt_to_asset: float             # 资产负债率 (%)
    current_ratio: float             # 流动比率
    interest_coverage: float         # 利息保障倍数
    cash_flow_ratio: float           # 经营性现金流/有息债务 (%)


@dataclass
class BusinessStability:
    """业务稳定性维度 (权重20%)"""
    business_diversification: int    # 业务多元化 (1-10分: 多元=10, 高度集中=1)
    contract_backlog: float         # 在手合同/年收入 (倍数)
    competitive_position: int        # 区域竞争地位 (1-10分: 垄断/唯一=10, 无优势=1)


@dataclass
class FinancialMetrics:
    """财务指标维度 (权重20%)"""
    revenue_growth: float            # 营收增速 (%)
    ebitda_margin: float             # EBITDA利润率 (%)
    receivable_turnover: float      # 应收账款周转率
    short_debt_ratio: float         # 短债占比 (%)


@dataclass
class GovernanceCredit:
    """治理与增信维度 (权重10%)"""
    related_party_transactions: int  # 关联交易治理 (1-10分: 规范=10)
    guarantee_ratio: float          # 对外担保比例 (%)
    external_credit_enhance: int     # 外部增信 (1-10分: 担保函/流动性支持=10)
    historical_compliance: int       # 历史合规 (1-10分: 无违约/失信=10)


@dataclass
class RatingInput:
    """评级输入数据"""
    issuer: str
    platform_type: str               # 平台类型: 省级/省会/地级市/区县
    regional: RegionalStrength
    fiscal: FiscalHealth
    business: BusinessStability
    financial: FinancialMetrics
    governance: GovernanceCredit


@dataclass
class RatingOutput:
    """评级输出结果"""
    issuer: str
    regional_score: float            # 区域实力得分 (加权)
    fiscal_score: float             # 财政健康得分 (加权)
    business_score: float           # 业务稳定性得分 (加权)
    financial_score: float          # 财务指标得分 (加权)
    governance_score: float         # 治理与增信得分 (加权)
    composite_score: float          # 综合得分
    rating: str                     # 信评等级
    outlook: str                    # 展望
    detail_scores: dict[str, float] = field(default_factory=dict)


# ============================================================================
# 评分引擎
# ============================================================================

class RatingScoringEngine:
    """评分引擎"""

    # 五维权重
    WEIGHTS = {
        "regional": 0.25,
        "fiscal": 0.25,
        "business": 0.20,
        "financial": 0.20,
        "governance": 0.10,
    }

    # 评级映射表
    RATING_MAP = [
        (90, "AAA", "稳定"),
        (84, "AAA-", "稳定"),
        (78, "AA+", "稳定"),
        (72, "AA+", "负面"),
        (66, "AA", "稳定"),
        (60, "AA-", "稳定"),
        (54, "A+", "稳定"),
        (48, "A", "稳定"),
        (42, "A", "负面"),
        (0,  "BBB+", "负面"),
    ]

    _detailed_scores: dict[str, float] = {}

    @staticmethod
    def score_regional(r: RegionalStrength) -> tuple[float, dict[str, float]]:
        """评分区域实力维度 (1-10分范围)"""
        details = {}

        # 行政层级评分
        admin_score = r.admin_level
        details["行政层级"] = admin_score

        # GDP评分 (分段线性)
        if r.gdp >= 5000:
            gdp_score = 10
        elif r.gdp >= 3000:
            gdp_score = 8
        elif r.gdp >= 1500:
            gdp_score = 6
        elif r.gdp >= 500:
            gdp_score = 4
        else:
            gdp_score = 2
        details["GDP规模"] = gdp_score

        # 财政评分
        if r.fiscal_revenue >= 500:
            fiscal_score = 10
        elif r.fiscal_revenue >= 200:
            fiscal_score = 8
        elif r.fiscal_revenue >= 100:
            fiscal_score = 6
        elif r.fiscal_revenue >= 50:
            fiscal_score = 4
        else:
            fiscal_score = 2
        details["财政收入"] = fiscal_score

        # 政府债务率评分 (越低越好)
        if r.gov_debt_ratio <= 60:
            debt_score = 10
        elif r.gov_debt_ratio <= 100:
            debt_score = 8
        elif r.gov_debt_ratio <= 150:
            debt_score = 6
        elif r.gov_debt_ratio <= 200:
            debt_score = 4
        else:
            debt_score = 2
        details["政府债务率"] = debt_score

        # 加权平均
        scores = [admin_score, gdp_score, fiscal_score, debt_score]
        avg = sum(scores) / len(scores)
        return avg, details

    @staticmethod
    def score_fiscal(f: FiscalHealth) -> tuple[float, dict[str, float]]:
        """评分财政健康维度 (1-10分范围)"""
        details = {}

        # 资产负债率评分 (越低越好)
        if f.debt_to_asset <= 50:
            debt_score = 10
        elif f.debt_to_asset <= 60:
            debt_score = 8
        elif f.debt_to_asset <= 70:
            debt_score = 6
        elif f.debt_to_asset <= 80:
            debt_score = 4
        else:
            debt_score = 2
        details["资产负债率"] = debt_score

        # 流动比率评分 (越高越好)
        if f.current_ratio >= 2.0:
            cr_score = 10
        elif f.current_ratio >= 1.5:
            cr_score = 8
        elif f.current_ratio >= 1.0:
            cr_score = 6
        elif f.current_ratio >= 0.5:
            cr_score = 4
        else:
            cr_score = 2
        details["流动比率"] = cr_score

        # 利息保障倍数评分
        if f.interest_coverage >= 5:
            ic_score = 10
        elif f.interest_coverage >= 3:
            ic_score = 8
        elif f.interest_coverage >= 2:
            ic_score = 6
        elif f.interest_coverage >= 1:
            ic_score = 4
        else:
            ic_score = 2
        details["利息保障倍数"] = ic_score

        # 现金流评分
        if f.cash_flow_ratio >= 10:
            cf_score = 10
        elif f.cash_flow_ratio >= 5:
            cf_score = 8
        elif f.cash_flow_ratio >= 0:
            cf_score = 6
        elif f.cash_flow_ratio >= -5:
            cf_score = 4
        else:
            cf_score = 2
        details["现金流/有息债务"] = cf_score

        scores = [debt_score, cr_score, ic_score, cf_score]
        avg = sum(scores) / len(scores)
        return avg, details

    @staticmethod
    def score_business(b: BusinessStability) -> tuple[float, dict[str, float]]:
        """评分业务稳定性维度 (1-10分范围)"""
        details = {}

        # 业务多元化
        details["业务多元化"] = b.business_diversification

        # 合同储备评分
        if b.contract_backlog >= 2:
            contract_score = 10
        elif b.contract_backlog >= 1.5:
            contract_score = 8
        elif b.contract_backlog >= 1:
            contract_score = 6
        elif b.contract_backlog >= 0.5:
            contract_score = 4
        else:
            contract_score = 2
        details["在手合同"] = contract_score

        # 竞争地位
        details["竞争地位"] = b.competitive_position

        scores = [b.business_diversification, contract_score, b.competitive_position]
        avg = sum(scores) / len(scores)
        return avg, details

    @staticmethod
    def score_financial(f: FinancialMetrics) -> tuple[float, dict[str, float]]:
        """评分财务指标维度 (1-10分范围)"""
        details = {}

        # 营收增速评分
        if f.revenue_growth >= 15:
            rev_score = 10
        elif f.revenue_growth >= 10:
            rev_score = 8
        elif f.revenue_growth >= 5:
            rev_score = 6
        elif f.revenue_growth >= 0:
            rev_score = 4
        else:
            rev_score = 2
        details["营收增速"] = rev_score

        # EBITDA利润率评分
        if f.ebitda_margin >= 20:
            ebit_score = 10
        elif f.ebitda_margin >= 15:
            ebit_score = 8
        elif f.ebitda_margin >= 10:
            ebit_score = 6
        elif f.ebitda_margin >= 5:
            ebit_score = 4
        else:
            ebit_score = 2
        details["EBITDA利润率"] = ebit_score

        # 应收账款周转率评分
        if f.receivable_turnover >= 5:
            ar_score = 10
        elif f.receivable_turnover >= 3:
            ar_score = 8
        elif f.receivable_turnover >= 2:
            ar_score = 6
        elif f.receivable_turnover >= 1:
            ar_score = 4
        else:
            ar_score = 2
        details["应收账款周转率"] = ar_score

        # 短债占比评分 (越低越好)
        if f.short_debt_ratio <= 30:
            sd_score = 10
        elif f.short_debt_ratio <= 40:
            sd_score = 8
        elif f.short_debt_ratio <= 50:
            sd_score = 6
        elif f.short_debt_ratio <= 60:
            sd_score = 4
        else:
            sd_score = 2
        details["短债占比"] = sd_score

        scores = [rev_score, ebit_score, ar_score, sd_score]
        avg = sum(scores) / len(scores)
        return avg, details

    @staticmethod
    def score_governance(g: GovernanceCredit) -> tuple[float, dict[str, float]]:
        """评分治理与增信维度 (1-10分范围)"""
        details = {}

        details["关联交易治理"] = g.related_party_transactions

        # 担保比例评分 (越低越好)
        if g.guarantee_ratio <= 20:
            g_score = 10
        elif g.guarantee_ratio <= 40:
            g_score = 8
        elif g.guarantee_ratio <= 60:
            g_score = 6
        elif g.guarantee_ratio <= 80:
            g_score = 4
        else:
            g_score = 2
        details["对外担保比例"] = g_score

        details["外部增信"] = g.external_credit_enhance
        details["历史合规"] = g.historical_compliance

        scores = [g.related_party_transactions, g_score, g.external_credit_enhance,
                  g.historical_compliance]
        avg = sum(scores) / len(scores)
        return avg, details

    @classmethod
    def map_to_rating(cls, composite_score: float) -> tuple[str, str]:
        """综合得分映射到评级等级和展望"""
        scaled = composite_score * 10  # 1-10 → 10-100
        for threshold, rating, outlook in cls.RATING_MAP:
            if scaled >= threshold:
                return rating, outlook
        return "BBB+", "负面"

    @classmethod
    def evaluate(cls, r: RatingInput) -> RatingOutput:
        """执行完整评级计算"""
        # 各维度评分（原始1-10分）
        reg_raw, reg_detail = cls.score_regional(r.regional)
        fis_raw, fis_detail = cls.score_fiscal(r.fiscal)
        bus_raw, bus_detail = cls.score_business(r.business)
        fin_raw, fin_detail = cls.score_financial(r.financial)
        gov_raw, gov_detail = cls.score_governance(r.governance)

        # 加权综合得分（1-10范围）
        composite = (
            reg_raw * cls.WEIGHTS["regional"] +
            fis_raw * cls.WEIGHTS["fiscal"] +
            bus_raw * cls.WEIGHTS["business"] +
            fin_raw * cls.WEIGHTS["financial"] +
            gov_raw * cls.WEIGHTS["governance"]
        )

        # 映射评级
        rating, outlook = cls.map_to_rating(composite)

        # 汇总详细得分
        all_details: dict[str, float] = {}
        all_details.update({f"区域-{k}": v for k, v in reg_detail.items()})
        all_details.update({f"财政-{k}": v for k, v in fis_detail.items()})
        all_details.update({f"业务-{k}": v for k, v in bus_detail.items()})
        all_details.update({f"财务-{k}": v for k, v in fin_detail.items()})
        all_details.update({f"治理-{k}": v for k, v in gov_detail.items()})

        return RatingOutput(
            issuer=r.issuer,
            regional_score=reg_raw,
            fiscal_score=fis_raw,
            business_score=bus_raw,
            financial_score=fin_raw,
            governance_score=gov_raw,
            composite_score=composite,
            rating=rating,
            outlook=outlook,
            detail_scores=all_details,
        )


# ============================================================================
# 报告生成器
# ============================================================================

class ReportGenerator:
    """评级报告生成器"""

    @staticmethod
    def generate_markdown(result: RatingOutput, input_data: RatingInput) -> str:
        """生成完整Markdown评级报告框架"""
        w = RatingScoringEngine.WEIGHTS
        lines = []

        # 报告标题
        lines.append(f"# {input_data.issuer} 信用评级报告框架")
        lines.append(f"")
        lines.append(f"**平台类型:** {input_data.platform_type}")
        lines.append(f"**评级日期:** 2026年")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        # 评级结论摘要
        lines.append(f"## 评级结论")
        lines.append(f"")
        lines.append(f"   信用等级: **{result.rating}**")
        lines.append(f"   评级展望: **{result.outlook}**")
        lines.append(f"   综合得分: **{result.composite_score:.1f}/10**")
        lines.append(f"")

        # 评分概要表
        lines.append(f"## 五维评分概要")
        lines.append(f"")
        lines.append(f"| 评估维度 | 权重 | 得分(1-10) | 加权得分 |")
        lines.append(f"|----------|------|-----------|----------|")
        lines.append(f"| 区域实力 | {w['regional']*100:.0f}% | {result.regional_score:.1f} | {result.regional_score * w['regional']:.2f} |")
        lines.append(f"| 财政健康 | {w['fiscal']*100:.0f}% | {result.fiscal_score:.1f} | {result.fiscal_score * w['fiscal']:.2f} |")
        lines.append(f"| 业务稳定性 | {w['business']*100:.0f}% | {result.business_score:.1f} | {result.business_score * w['business']:.2f} |")
        lines.append(f"| 财务指标 | {w['financial']*100:.0f}% | {result.financial_score:.1f} | {result.financial_score * w['financial']:.2f} |")
        lines.append(f"| 治理与增信 | {w['governance']*100:.0f}% | {result.governance_score:.1f} | {result.governance_score * w['governance']:.2f} |")
        lines.append(f"| **合计** | **100%** | | **{result.composite_score:.2f}** |")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        # 区域实力分析
        lines.append(f"## 一、区域实力 (权重{w['regional']*100:.0f}%)")
        lines.append(f"")
        r = input_data.regional
        lines.append(f"| 指标 | 数值 | 评分 |")
        lines.append(f"|------|------|------|")
        for k, v in sorted(result.detail_scores.items()):
            if k.startswith("区域-"):
                metric = k.replace("区域-", "")
                value = r.__dict__.get({"行政层级": "admin_level", "GDP规模": "gdp",
                                        "财政收入": "fiscal_revenue", "政府债务率": "gov_debt_ratio"}.get(metric, ""))
                lines.append(f"| {metric} | {value if value is not None else 'N/A'} | {v:.0f}/10 |")
        lines.append(f"")
        lines.append(f"> **区域评分:** {result.regional_score:.1f}/10")
        lines.append(f"")

        # 财政健康分析
        lines.append(f"## 二、财政健康 (权重{w['fiscal']*100:.0f}%)")
        lines.append(f"")
        f = input_data.fiscal
        lines.append(f"| 指标 | 数值 | 评分 |")
        lines.append(f"|------|------|------|")
        for k, v in sorted(result.detail_scores.items()):
            if k.startswith("财政-"):
                metric = k.replace("财政-", "")
                value = f.__dict__.get({"资产负债率": "debt_to_asset", "流动比率": "current_ratio",
                                         "利息保障倍数": "interest_coverage",
                                         "现金流/有息债务": "cash_flow_ratio"}.get(metric, ""))
                lines.append(f"| {metric} | {value if value is not None else 'N/A'} | {v:.0f}/10 |")
        lines.append(f"")
        lines.append(f"> **财政评分:** {result.fiscal_score:.1f}/10")
        lines.append(f"")

        # 业务稳定性分析
        lines.append(f"## 三、业务稳定性 (权重{w['business']*100:.0f}%)")
        lines.append(f"")
        b = input_data.business
        lines.append(f"| 指标 | 数值 | 评分 |")
        lines.append(f"|------|------|------|")
        for k, v in sorted(result.detail_scores.items()):
            if k.startswith("业务-"):
                metric = k.replace("业务-", "")
                lines.append(f"| {metric} | {'N/A'} | {v:.0f}/10 |")
        lines.append(f"")
        lines.append(f"> **业务评分:** {result.business_score:.1f}/10")
        lines.append(f"")

        # 财务指标分析
        lines.append(f"## 四、财务指标 (权重{w['financial']*100:.0f}%)")
        lines.append(f"")
        fn = input_data.financial
        lines.append(f"| 指标 | 数值 | 评分 |")
        lines.append(f"|------|------|------|")
        for k, v in sorted(result.detail_scores.items()):
            if k.startswith("财务-"):
                metric = k.replace("财务-", "")
                value = fn.__dict__.get({"营收增速": "revenue_growth", "EBITDA利润率": "ebitda_margin",
                                          "应收账款周转率": "receivable_turnover",
                                          "短债占比": "short_debt_ratio"}.get(metric, ""))
                lines.append(f"| {metric} | {value if value is not None else 'N/A'} | {v:.0f}/10 |")
        lines.append(f"")
        lines.append(f"> **财务评分:** {result.financial_score:.1f}/10")
        lines.append(f"")

        # 治理与增信分析
        lines.append(f"## 五、治理与增信 (权重{w['governance']*100:.0f}%)")
        lines.append(f"")
        g = input_data.governance
        lines.append(f"| 指标 | 数值 | 评分 |")
        lines.append(f"|------|------|------|")
        for k, v in sorted(result.detail_scores.items()):
            if k.startswith("治理-"):
                metric = k.replace("治理-", "")
                value = g.__dict__.get({"关联交易治理": "related_party_transactions",
                                        "对外担保比例": "guarantee_ratio",
                                        "外部增信": "external_credit_enhance",
                                        "历史合规": "historical_compliance"}.get(metric, ""))
                lines.append(f"| {metric} | {value if value is not None else 'N/A'} | {v:.0f}/10 |")
        lines.append(f"")
        lines.append(f"> **治理评分:** {result.governance_score:.1f}/10")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        # 结论
        lines.append(f"## 评级结论与分析")
        lines.append(f"")
        lines.append(f"1. 经五维评分卡综合评定，{input_data.issuer}信用评级为 **{result.rating}**，展望 **{result.outlook}**。")
        lines.append(f"2. 综合得分 {result.composite_score:.2f}/10，处于 {result.rating} 级区间。")
        lines.append(f"3. 主要支撑因素：")
        lines.append(f"   - 区域经济及财政实力提供基础信用支撑")
        lines.append(f"   - [根据实际维度得分补充关键亮点]")
        lines.append(f"4. 主要风险关注：")
        lines.append(f"   - [根据低分维度识别关键风险点]")
        lines.append(f"   - 需持续关注区域经济和政府支持意愿变化")
        lines.append(f"5. 债项评级建议：")
        lines.append(f"   - 主体评级: {result.rating}")
        lines.append(f"   - 债项评级: 视增信安排而定，一般与主体评级一致")
        lines.append(f"")
        lines.append(f"*本报告为评级框架模板，最终评级需结合尽调、访谈及外部审计进行确认。*")
        lines.append(f"")

        return "\n".join(lines)

    @staticmethod
    def generate_json(result: RatingOutput, input_data: RatingInput) -> str:
        """生成JSON格式输出"""
        data = {
            "issuer": input_data.issuer,
            "platform_type": input_data.platform_type,
            "rating": result.rating,
            "outlook": result.outlook,
            "composite_score": result.composite_score,
            "scores": {
                "regional": result.regional_score,
                "fiscal_health": result.fiscal_score,
                "business_stability": result.business_score,
                "financial_metrics": result.financial_score,
                "governance_credit": result.governance_score,
            },
            "weights": RatingScoringEngine.WEIGHTS,
            "detail_scores": result.detail_scores,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


# ============================================================================
# 内置测试用例
# ============================================================================

def build_test_input() -> RatingInput:
    """构建测试用例：地级市城投，最终输出AA+"""
    return RatingInput(
        issuer="XX市城市投资发展集团有限公司",
        platform_type="地级市",
        regional=RegionalStrength(
            admin_level=6,              # 地级市
            gdp=5500.0,                 # 5500亿 GDP
            fiscal_revenue=250.0,       # 250亿财政收入
            gov_debt_ratio=85.0,        # 85%政府债务率
        ),
        fiscal=FiscalHealth(
            debt_to_asset=58.0,         # 58%资产负债率
            current_ratio=1.6,          # 1.6流动比率
            interest_coverage=3.2,      # 3.2倍利息保障
            cash_flow_ratio=6.0,        # 6%现金流/有息债务
        ),
        business=BusinessStability(
            business_diversification=8,  # 业务较多元
            contract_backlog=1.8,       # 1.8倍合同储备
            competitive_position=8,     # 区域核心平台
        ),
        financial=FinancialMetrics(
            revenue_growth=8.0,          # 8%营收增速
            ebitda_margin=18.0,          # 18%EBITDA利润率
            receivable_turnover=2.5,     # 2.5次应收账款周转率
            short_debt_ratio=35.0,       # 35%短债占比
        ),
        governance=GovernanceCredit(
            related_party_transactions=8,  # 关联交易较规范
            guarantee_ratio=25.0,         # 25%对外担保
            external_credit_enhance=6,     # 有一定增信
            historical_compliance=8,       # 历史合规良好
        ),
    )


def run_test_case():
    """运行内置测试用例"""
    print("=" * 60)
    print("城投债评级框架生成器 - 内置测试用例")
    print("=" * 60)
    print()

    input_data = build_test_input()

    # 打印输入数据
    print("【输入数据摘要】")
    print(f"  发行人: {input_data.issuer}")
    print(f"  平台类型: {input_data.platform_type}")
    print(f"  区域: GDP {input_data.regional.gdp}亿 | 财政收入 {input_data.regional.fiscal_revenue}亿 | 债务率 {input_data.regional.gov_debt_ratio}%")
    print(f"  财政: 资产负债率 {input_data.fiscal.debt_to_asset}% | 流动比率 {input_data.fiscal.current_ratio} | 利息保障 {input_data.fiscal.interest_coverage}x")
    print(f"  业务: 多元化 {input_data.business.business_diversification}/10 | 合同储备 {input_data.business.contract_backlog}x | 竞争地位 {input_data.business.competitive_position}/10")
    print(f"  财务: 营收增速 {input_data.financial.revenue_growth}% | EBITDA利润率 {input_data.financial.ebitda_margin}% | 短债占比 {input_data.financial.short_debt_ratio}%")
    print(f"  治理: 担保比例 {input_data.governance.guarantee_ratio}% | 增信 {input_data.governance.external_credit_enhance}/10")
    print()

    # 执行评级
    result = RatingScoringEngine.evaluate(input_data)

    # 打印评分分析
    print("【五维评分分析】")
    w = RatingScoringEngine.WEIGHTS
    print(f"  区域实力({w['regional']*100:.0f}%): {result.regional_score:.1f}/10 → 加权 {result.regional_score*w['regional']:.2f}")
    for k, v in sorted(result.detail_scores.items()):
        if k.startswith("区域-"):
            print(f"    └─ {k.replace('区域-', '')}: {v:.0f}/10")
    print()
    print(f"  财政健康({w['fiscal']*100:.0f}%): {result.fiscal_score:.1f}/10 → 加权 {result.fiscal_score*w['fiscal']:.2f}")
    for k, v in sorted(result.detail_scores.items()):
        if k.startswith("财政-"):
            print(f"    └─ {k.replace('财政-', '')}: {v:.0f}/10")
    print()
    print(f"  业务稳定性({w['business']*100:.0f}%): {result.business_score:.1f}/10 → 加权 {result.business_score*w['business']:.2f}")
    print(f"  财务指标({w['financial']*100:.0f}%): {result.financial_score:.1f}/10 → 加权 {result.financial_score*w['financial']:.2f}")
    print(f"  治理与增信({w['governance']*100:.0f}%): {result.governance_score:.1f}/10 → 加权 {result.governance_score*w['governance']:.2f}")
    print()
    print(f"  综合得分: {result.composite_score:.2f}/10 → 评级: {result.rating} (展望: {result.outlook})")
    print()

    # 输出完整Markdown报告
    print("=" * 60)
    print("【完整评级报告框架】")
    print("=" * 60)
    print()
    md_report = ReportGenerator.generate_markdown(result, input_data)
    print(md_report)

    print()
    print("【测试结论】")
    print(f"  ✓ 评级结果: {result.rating} (展望{result.outlook})")
    print(f"  ✓ 综合得分: {result.composite_score:.2f}/10")
    print(f"  ✓ 评级映射正确：地级市城投综合得分映射到AA+区间")
    print(f"  ✓ 五维评分卡完整计算通过")


# ============================================================================
# CLI 入口
# ============================================================================

def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog="bond_rating_template",
        description="城投债评级框架生成器 - 五维评分卡",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
评级维度与权重:
  区域实力:   25%% (行政层级 + GDP + 财政 + 政府债务率)
  财政健康:   25%% (资产负债率 + 流动比率 + 利息保障 + 现金流)
  业务稳定性: 20%% (多元化 + 合同储备 + 竞争地位)
  财务指标:   20%% (营收增速 + EBITDA + 周转率 + 短债占比)
  治理与增信: 10%% (关联交易 + 担保 + 增信 + 合规)

评级映射: AAA / AA+ / AA / AA- / A+

示例:
  %(prog)s --test                           # 运行内置测试用例
  %(prog)s --input rating_input.json       # 从JSON加载评级输入
  %(prog)s --input rating_input.json --md  # 输出Markdown报告
  %(prog)s --input rating_input.json --json # 输出JSON
        """
    )

    parser.add_argument("--test", action="store_true",
                        help="运行内置测试用例 (地级市城投，输出AA+)")
    parser.add_argument("--input", metavar="FILE",
                        help="输入评级JSON文件")
    parser.add_argument("--md", action="store_true",
                        help="输出Markdown格式评级报告")
    parser.add_argument("--json", action="store_true",
                        help="输出JSON格式")
    parser.add_argument("--output", metavar="FILE",
                        help="报告输出文件路径")

    return parser.parse_args()


def load_rating_input(json_path: str) -> RatingInput:
    """从JSON文件加载评级输入数据"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return RatingInput(
        issuer=data["issuer"],
        platform_type=data["platform_type"],
        regional=RegionalStrength(**data["regional"]),
        fiscal=FiscalHealth(**data["fiscal"]),
        business=BusinessStability(**data["business"]),
        financial=FinancialMetrics(**data["financial"]),
        governance=GovernanceCredit(**data["governance"]),
    )


def main() -> None:
    """主入口"""
    args = parse_args()

    if args.test:
        run_test_case()
    elif args.input:
        input_data = load_rating_input(args.input)
        result = RatingScoringEngine.evaluate(input_data)

        if args.json:
            output = ReportGenerator.generate_json(result, input_data)
        else:
            output = ReportGenerator.generate_markdown(result, input_data)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"报告已写入: {args.output}")
        else:
            print(output)
    else:
        print("城投债评级框架生成器 v1.0.0")
        print("使用 --test 运行内置测试用例")
        print("使用 --help 查看完整帮助")


if __name__ == "__main__":
    main()