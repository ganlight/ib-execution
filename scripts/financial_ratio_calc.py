#!/usr/bin/env python3
"""
A股投行财务比率计算工具
支持：盈利能力 / 偿债能力 / 运营能力 / 成长能力 / 现金流量 五维分析
支持：与行业均值对比（内置行业基准数据）
输出：JSON报告 + Markdown表格

Usage:
    python financial_ratio_calc.py interactive
    python financial_ratio_calc.py benchmark
    python financial_ratio_calc.py file --input data.json --industry software
    python financial_ratio_calc.py file --input data.json --industry software --json
    python financial_ratio_calc.py --test
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any


# ============================================================================
# 行业基准常量
# ============================================================================

INDUSTRY_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "manufacturing": {
        "gross_margin": 0.25,
        "net_margin": 0.08,
        "roe": 0.12,
        "roa": 0.06,
        "debt_ratio": 0.55,
        "current_ratio": 1.5,
        "quick_ratio": 1.0,
        "interest_coverage": 3.0,
        "receivable_days": 60.0,
        "inventory_days": 90.0,
        "ocf_to_netprofit": 1.0,
    },
    "semiconductor": {
        "gross_margin": 0.40,
        "net_margin": 0.15,
        "roe": 0.15,
        "roa": 0.08,
        "debt_ratio": 0.45,
        "current_ratio": 2.0,
        "quick_ratio": 1.5,
        "interest_coverage": 5.0,
        "receivable_days": 45.0,
        "inventory_days": 120.0,
        "ocf_to_netprofit": 1.2,
    },
    "software": {
        "gross_margin": 0.70,
        "net_margin": 0.20,
        "roe": 0.18,
        "roa": 0.12,
        "debt_ratio": 0.35,
        "current_ratio": 2.5,
        "quick_ratio": 2.0,
        "interest_coverage": 8.0,
        "receivable_days": 30.0,
        "inventory_days": 0.0,
        "ocf_to_netprofit": 1.3,
    },
    "pharma": {
        "gross_margin": 0.65,
        "net_margin": 0.12,
        "roe": 0.14,
        "roa": 0.07,
        "debt_ratio": 0.40,
        "current_ratio": 2.0,
        "quick_ratio": 1.5,
        "interest_coverage": 5.0,
        "receivable_days": 60.0,
        "inventory_days": 100.0,
        "ocf_to_netprofit": 1.1,
    },
    "consumer": {
        "gross_margin": 0.35,
        "net_margin": 0.10,
        "roe": 0.15,
        "roa": 0.07,
        "debt_ratio": 0.50,
        "current_ratio": 1.8,
        "quick_ratio": 1.2,
        "interest_coverage": 4.0,
        "receivable_days": 30.0,
        "inventory_days": 60.0,
        "ocf_to_netprofit": 1.0,
    },
    "real_estate": {
        "gross_margin": 0.30,
        "net_margin": 0.08,
        "roe": 0.10,
        "roa": 0.03,
        "debt_ratio": 0.70,
        "current_ratio": 1.2,
        "quick_ratio": 0.5,
        "interest_coverage": 2.0,
        "receivable_days": 10.0,
        "inventory_days": 1500.0,
        "ocf_to_netprofit": 0.8,
    },
    "banking": {
        "gross_margin": 0.50,
        "net_margin": 0.25,
        "roe": 0.12,
        "roa": 0.01,
        "debt_ratio": 0.88,
        "current_ratio": 0.0,
        "quick_ratio": 0.0,
        "interest_coverage": 0.0,
        "receivable_days": 0.0,
        "inventory_days": 0.0,
        "ocf_to_netprofit": 1.0,
    },
    "default": {
        "gross_margin": 0.30,
        "net_margin": 0.10,
        "roe": 0.12,
        "roa": 0.05,
        "debt_ratio": 0.55,
        "current_ratio": 1.5,
        "quick_ratio": 1.0,
        "interest_coverage": 3.0,
        "receivable_days": 60.0,
        "inventory_days": 90.0,
        "ocf_to_netprofit": 1.0,
    },
}


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class FinancialRatios:
    """财务比率结果容器"""
    # 盈利能力
    gross_margin: float
    net_margin: float
    roe: float
    roa: float
    operating_margin: float
    ebitda_margin: float
    # 偿债能力
    debt_ratio: float
    current_ratio: float
    quick_ratio: float
    interest_coverage: float
    # 运营能力
    asset_turnover: float
    inventory_turnover: float
    receivable_turnover: float
    days_sales_outstanding: float
    days_inventory: float
    # 成长能力
    revenue_growth: float
    profit_growth: float
    net_asset_growth: float
    ebitda_growth: float
    # 现金流量
    operating_cf_ratio: float
    free_cf_to_revenue: float
    capex_to_revenue: float
    # 每股指标
    eps: float
    bvps: float


@dataclass
class BenchmarkComparison:
    """与行业基准对比"""
    metric: str
    actual: float
    benchmark: float
    unit: str
    status: str  # "🟢" | "🔴" | "⚠️" | "N/A"
    gap: float  # 差异百分比
    advice: str


@dataclass
class AnalysisReport:
    """完整分析报告"""
    company: str
    industry: str
    period: str
    ratios: FinancialRatios
    comparisons: List[BenchmarkComparison]
    red_flags: List[str]
    summary: str
    score: int  # 1-100


# ============================================================================
# 核心计算函数
# ============================================================================

def safe_div(a: float, b: float, default: float = 0.0) -> float:
    """安全除法，避免除零错误"""
    if b is None or b == 0:
        return default
    return a / b


def compute_ratios(
    revenue: float,
    cogs: float,
    net_profit: float,
    total_assets: float,
    total_liabilities: float,
    current_assets: float,
    current_liabilities: float,
    inventory: float,
    accounts_receivable: float,
    operating_cf: float,
    capex: float,
    interest_expense: float,
    ebit: float,
    revenue_prior: float,
    net_profit_prior: float,
    equity_prior: float,
    depreciation: float = 0.0,
    amortization: float = 0.0,
    shares: float = 1.0,
    equity: Optional[float] = None,
) -> FinancialRatios:
    """
    从原始财务数据计算所有比率

    Args:
        revenue: 营业收入（万元）
        cogs: 营业成本（万元）
        net_profit: 净利润（万元）
        total_assets: 资产总额（万元）
        total_liabilities: 负债总额（万元）
        current_assets: 流动资产（万元）
        current_liabilities: 流动负债（万元）
        inventory: 存货（万元）
        accounts_receivable: 应收账款（万元）
        operating_cf: 经营现金流（万元）
        capex: 资本支出（万元）
        interest_expense: 利息支出（万元）
        ebit: EBIT（万元）
        revenue_prior: 上年营业收入（万元）
        net_profit_prior: 上年净利润（万元）
        equity_prior: 上年净资产（万元）
        depreciation: 折旧（万元）
        amortization: 摊销（万元）
        shares: 股本（亿股）
        equity: 净资产（万元），未提供则用总资产-总负债计算

    Returns:
        FinancialRatios: 包含所有计算比率的对象
    """
    gross_profit = revenue - cogs
    if equity is None:
        equity = total_assets - total_liabilities

    ebitda = ebit + depreciation + amortization
    free_cf = operating_cf - capex

    # 营业收入增长
    revenue_growth = safe_div(revenue - revenue_prior, revenue_prior) if revenue_prior else 0.0
    # 净利润增长
    profit_growth = safe_div(net_profit - net_profit_prior, net_profit_prior) if net_profit_prior else 0.0
    # 净资产增长
    net_asset_growth = safe_div(equity - equity_prior, equity_prior) if equity_prior else 0.0
    # EBITDA增长（简化）
    ebitda_prior = net_profit_prior * 1.5 if net_profit_prior else 0.0
    ebitda_growth = safe_div(ebitda - ebitda_prior, ebitda_prior) if ebitda_prior else 0.0

    # 每股指标
    eps = safe_div(net_profit * 10000, shares * 100000000)  # 元/股
    bvps = safe_div(equity * 10000, shares * 100000000)  # 元/股

    return FinancialRatios(
        # 盈利能力
        gross_margin=safe_div(gross_profit, revenue),
        net_margin=safe_div(net_profit, revenue),
        roe=safe_div(net_profit, equity),
        roa=safe_div(net_profit, total_assets),
        operating_margin=safe_div(gross_profit - 500, revenue),  # 简化运营费用
        ebitda_margin=safe_div(ebitda, revenue),
        # 偿债能力
        debt_ratio=safe_div(total_liabilities, total_assets),
        current_ratio=safe_div(current_assets, current_liabilities),
        quick_ratio=safe_div(current_assets - inventory, current_liabilities),
        interest_coverage=safe_div(ebit, interest_expense),
        # 运营能力
        asset_turnover=safe_div(revenue, total_assets),
        inventory_turnover=safe_div(cogs, inventory),
        receivable_turnover=safe_div(revenue, accounts_receivable),
        days_sales_outstanding=365 * safe_div(accounts_receivable, revenue),
        days_inventory=365 * safe_div(inventory, cogs),
        # 成长能力
        revenue_growth=revenue_growth,
        profit_growth=profit_growth,
        net_asset_growth=net_asset_growth,
        ebitda_growth=ebitda_growth,
        # 现金流量
        operating_cf_ratio=safe_div(operating_cf, net_profit),
        free_cf_to_revenue=safe_div(free_cf, revenue),
        capex_to_revenue=safe_div(capex, revenue),
        # 每股指标
        eps=eps,
        bvps=bvps,
    )


def compare_to_benchmark(
    ratios: FinancialRatios,
    industry: str,
) -> List[BenchmarkComparison]:
    """将计算出的比率与行业基准对比"""
    bench = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["default"])
    comparisons: List[BenchmarkComparison] = []

    mapping = [
        ("毛利率 (Gross Margin)", ratios.gross_margin, bench["gross_margin"], "%", True, 0.05),
        ("净利率 (Net Margin)", ratios.net_margin, bench["net_margin"], "%", True, 0.03),
        ("ROE", ratios.roe, bench["roe"], "%", True, 0.03),
        ("ROA", ratios.roa, bench["roa"], "%", True, 0.02),
        ("资产负债率", ratios.debt_ratio, bench["debt_ratio"], "%", False, 0.05),
        ("流动比率", ratios.current_ratio, bench["current_ratio"], "x", True, 0.3),
        ("速动比率", ratios.quick_ratio, bench["quick_ratio"], "x", True, 0.2),
        ("利息保障倍数", ratios.interest_coverage, bench["interest_coverage"], "x", True, 1.0),
        ("应收账款周转天数", ratios.days_sales_outstanding, bench["receivable_days"], "天", False, 15.0),
        ("存货周转天数", ratios.days_inventory, bench["inventory_days"], "天", False, 20.0),
        ("经营现金流/净利润", ratios.operating_cf_ratio, bench["ocf_to_netprofit"], "x", True, 0.2),
    ]

    for name, actual, bm, unit, good_high, threshold in mapping:
        if bm == 0:
            status = "N/A"
            gap = 0.0
            advice = "无行业基准"
        elif good_high:
            if actual >= bm:
                status = "🟢"
                gap = safe_div(actual - bm, bm)
                advice = "优于行业"
            elif actual >= bm - threshold:
                status = "⚠️"
                gap = safe_div(actual - bm, bm)
                advice = "接近行业均值"
            else:
                status = "🔴"
                gap = safe_div(actual - bm, bm)
                advice = "弱于行业"
        else:
            if actual <= bm:
                status = "🟢"
                gap = safe_div(bm - actual, bm)
                advice = "优于行业"
            elif actual <= bm + threshold:
                status = "⚠️"
                gap = safe_div(actual - bm, bm)
                advice = "接近行业均值"
            else:
                status = "🔴"
                gap = safe_div(actual - bm, bm)
                advice = "弱于行业"

        comparisons.append(BenchmarkComparison(
            metric=name,
            actual=actual,
            benchmark=bm,
            unit=unit,
            status=status,
            gap=gap,
            advice=advice,
        ))

    return comparisons


def detect_red_flags(ratios: FinancialRatios) -> List[str]:
    """检测财务风险红旗"""
    flags: List[str] = []

    if ratios.current_ratio < 1.0:
        flags.append("⚠️ 流动比率 < 1.0，短期偿债压力极大")
    if ratios.quick_ratio < 0.5:
        flags.append("⚠️ 速动比率 < 0.5，即时偿债能力不足")
    if ratios.interest_coverage < 1.0:
        flags.append("🔴 利息保障倍数 < 1.0，息税前利润不足以覆盖利息")
    elif ratios.interest_coverage < 3.0:
        flags.append("⚠️ 利息保障倍数 < 3.0，利息覆盖能力偏弱")
    if ratios.debt_ratio > 0.8:
        flags.append("🔴 资产负债率 > 80%，高杠杆风险")
    elif ratios.debt_ratio > 0.7:
        flags.append("⚠️ 资产负债率 > 70%，接近监管红线")
    if ratios.operating_cf_ratio < 0.0:
        flags.append("🔴 经营现金流为负，盈利质量存疑")
    elif ratios.operating_cf_ratio < 0.5:
        flags.append("⚠️ 经营现金流/净利润 < 50%，盈利质量偏低")
    if ratios.days_sales_outstanding > 180:
        flags.append("🔴 应收账款周转天数 > 180天，坏账风险高")
    elif ratios.days_sales_outstanding > 120:
        flags.append("⚠️ 应收账款周转天数 > 120天，回收周期偏长")
    if ratios.inventory_turnover < 2.0 and ratios.inventory_turnover > 0:
        flags.append("⚠️ 存货周转率偏低，可能存在积压")
    if ratios.revenue_growth < -0.2:
        flags.append("🔴 营业收入同比下滑超过20%")
    elif ratios.revenue_growth < 0.0:
        flags.append("⚠️ 营业收入同比下滑")
    if ratios.net_margin < 0.0:
        flags.append("🔴 净利率为负，持续亏损")
    if ratios.capex_to_revenue > 0.5:
        flags.append("⚠️ 资本支出占收入比超过50%，现金压力较大")

    return flags


def compute_score(comparisons: List[BenchmarkComparison], ratios: FinancialRatios) -> int:
    """计算综合评分（1-100）"""
    if not comparisons:
        return 50

    green_count = sum(1 for c in comparisons if c.status == "🟢")
    yellow_count = sum(1 for c in comparisons if c.status == "⚠️")
    red_count = sum(1 for c in comparisons if c.status == "🔴")
    total = len(comparisons)

    if total == 0:
        return 50

    score = (green_count * 100 + yellow_count * 60 + red_count * 20) / total
    score = max(1, min(100, int(score)))
    return score


def get_grade(score: int) -> str:
    """根据评分返回等级"""
    if score >= 90:
        return "AAA（优秀）"
    elif score >= 75:
        return "AA（良好）"
    elif score >= 60:
        return "A（一般）"
    elif score >= 45:
        return "BBB（尚可）"
    elif score >= 30:
        return "BB（较差）"
    else:
        return "B（很差）"


# ============================================================================
# 格式化输出
# ============================================================================

def format_ratio_table(
    ratios: FinancialRatios,
    industry: str,
    company: str = "目标公司",
    period: str = "本期",
) -> str:
    """生成Markdown格式的财务比率报告"""
    bench = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["default"])
    comparisons = compare_to_benchmark(ratios, industry)
    red_flags = detect_red_flags(ratios)
    score = compute_score(comparisons, ratios)
    grade = get_grade(score)

    lines: List[str] = []

    # 标题
    lines.append(f"# 财务比率分析报告")
    lines.append(f"")
    lines.append(f"**公司：** {company}  |  **行业：** {industry}  |  **期间：** {period}")
    lines.append(f"")

    # 评分摘要
    lines.append(f"## 📊 综合评分")
    lines.append(f"")
    lines.append(f"| 评分 | 等级 | 红旗数 |")
    lines.append(f"|------|------|--------|")
    red_count = len([f for f in red_flags if f.startswith("🔴")])
    warn_count = len([f for f in red_flags if f.startswith("⚠️")])
    lines.append(f"| {score}/100 | {grade} | 🔴{red_count} ⚠️{warn_count} |")
    lines.append(f"")

    # 盈利能力
    lines.append(f"## 盈利能力")
    lines.append(f"")
    lines.append(f"| 指标 | 实际值 | 行业基准 | 状态 | 说明 |")
    lines.append(f"|------|--------|---------|------|------|")
    lines.append(f"| 毛利率 | {ratios.gross_margin:.1%} | {bench['gross_margin']:.1%} | "
                  f"{'🟢' if ratios.gross_margin >= bench['gross_margin'] else '🔴'} | |")
    lines.append(f"| 净利率 | {ratios.net_margin:.1%} | {bench['net_margin']:.1%} | "
                  f"{'🟢' if ratios.net_margin >= bench['net_margin'] else '🔴'} | |")
    lines.append(f"| ROE | {ratios.roe:.1%} | {bench['roe']:.1%} | "
                  f"{'🟢' if ratios.roe >= bench['roe'] else '🔴'} | |")
    lines.append(f"| ROA | {ratios.roa:.1%} | {bench['roa']:.1%} | "
                  f"{'🟢' if ratios.roa >= bench['roa'] else '🔴'} | |")
    lines.append(f"| 营业利润率 | {ratios.operating_margin:.1%} | - | - | |")
    lines.append(f"| EBITDA率 | {ratios.ebitda_margin:.1%} | - | - | |")
    lines.append(f"")

    # 偿债能力
    lines.append(f"## 偿债能力")
    lines.append(f"")
    lines.append(f"| 指标 | 实际值 | 行业基准 | 状态 | 说明 |")
    lines.append(f"|------|--------|---------|------|------|")
    lines.append(f"| 资产负债率 | {ratios.debt_ratio:.1%} | {bench['debt_ratio']:.1%} | "
                  f"{'🟢' if ratios.debt_ratio <= bench['debt_ratio'] else '🔴'} | |")
    lines.append(f"| 流动比率 | {ratios.current_ratio:.2f}x | {bench['current_ratio']:.2f}x | "
                  f"{'🟢' if ratios.current_ratio >= bench['current_ratio'] else '🔴'} | "
                  f"{'良好' if ratios.current_ratio >= 2.0 else '偏弱' if ratios.current_ratio >= 1.0 else '不足'} |")
    lines.append(f"| 速动比率 | {ratios.quick_ratio:.2f}x | {bench['quick_ratio']:.2f}x | "
                  f"{'🟢' if ratios.quick_ratio >= bench['quick_ratio'] else '🔴'} | |")
    lines.append(f"| 利息保障倍数 | {ratios.interest_coverage:.1f}x | >{bench['interest_coverage']:.0f}x | "
                  f"{'🟢' if ratios.interest_coverage >= 3 else '🔴' if ratios.interest_coverage < 1 else '⚠️'} | "
                  f"{'充足' if ratios.interest_coverage >= 5 else '尚可' if ratios.interest_coverage >= 3 else '不足'} |")
    lines.append(f"")

    # 运营能力
    lines.append(f"## 运营能力")
    lines.append(f"")
    lines.append(f"| 指标 | 实际值 | 行业基准 | 状态 | 说明 |")
    lines.append(f"|------|--------|---------|------|------|")
    dso_status = ('🟢' if ratios.days_sales_outstanding <= bench['receivable_days']
                  else '⚠️' if ratios.days_sales_outstanding <= bench['receivable_days'] + 30
                  else '🔴')
    lines.append(f"| 应收账款周转天数 | {ratios.days_sales_outstanding:.0f}天 | {bench['receivable_days']:.0f}天 | "
                  f"{dso_status} | |")
    inv_status = ('🟢' if ratios.days_inventory <= bench['inventory_days']
                  else '⚠️' if ratios.days_inventory <= bench['inventory_days'] + 30
                  else '🔴')
    lines.append(f"| 存货周转天数 | {ratios.days_inventory:.0f}天 | {bench['inventory_days']:.0f}天 | "
                  f"{inv_status} | |")
    lines.append(f"| 资产周转率 | {ratios.asset_turnover:.2f}x | - | - | |")
    lines.append(f"| 存货周转率 | {ratios.inventory_turnover:.1f}x | - | - | |")
    lines.append(f"| 应收账款周转率 | {ratios.receivable_turnover:.1f}x | - | - | |")
    lines.append(f"")

    # 成长能力
    lines.append(f"## 成长能力")
    lines.append(f"")
    lines.append(f"| 指标 | 实际值 | 状态 |")
    lines.append(f"|------|--------|------|")
    rev_status = ('🟢' if ratios.revenue_growth >= 0.15
                  else '⚠️' if ratios.revenue_growth >= 0.0
                  else '🔴')
    lines.append(f"| 营业收入增长 | {ratios.revenue_growth:+.1%} | {rev_status} |")
    profit_status = ('🟢' if ratios.profit_growth >= 0.1
                     else '⚠️' if ratios.profit_growth >= 0.0
                     else '🔴')
    lines.append(f"| 净利润增长 | {ratios.profit_growth:+.1%} | {profit_status} |")
    lines.append(f"| 净资产增长 | {ratios.net_asset_growth:+.1%} | "
                  f"{'🟢' if ratios.net_asset_growth > 0 else '🔴'} |")
    lines.append(f"")

    # 现金流量
    lines.append(f"## 现金流量")
    lines.append(f"")
    lines.append(f"| 指标 | 实际值 | 状态 |")
    lines.append(f"|------|--------|------|")
    ocf_status = ('🟢' if ratios.operating_cf_ratio >= 1.0
                   else '⚠️' if ratios.operating_cf_ratio >= 0.5
                   else '🔴')
    lines.append(f"| 经营现金流/净利润 | {ratios.operating_cf_ratio:.2f}x | {ocf_status} |")
    lines.append(f"| 自由现金流/营收 | {ratios.free_cf_to_revenue:.1%} | "
                  f"{'🟢' if ratios.free_cf_to_revenue >= 0.05 else '⚠️' if ratios.free_cf_to_revenue >= 0 else '🔴'} |")
    lines.append(f"| Capex/营收 | {ratios.capex_to_revenue:.1%} | - |")
    lines.append(f"")

    # 每股指标
    lines.append(f"## 每股指标")
    lines.append(f"")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 每股收益 (EPS) | {ratios.eps:.2f} 元/股 |")
    lines.append(f"| 每股净资产 (BVPS) | {ratios.bvps:.2f} 元/股 |")
    lines.append(f"")

    # 风险红旗
    if red_flags:
        lines.append(f"## 🚩 风险提示")
        lines.append(f"")
        for flag in red_flags:
            lines.append(f"- {flag}")
        lines.append(f"")

    # 行业对比表
    lines.append(f"## 📐 行业对比详情")
    lines.append(f"")
    lines.append(f"| 指标 | 实际值 | 行业基准 | 差距 | 状态 |")
    lines.append(f"|------|--------|---------|------|------|")
    for comp in comparisons:
        gap_str = f"{comp.gap:+.1%}" if comp.unit != "天" else f"{comp.actual - comp.benchmark:+.0f}天"
        lines.append(f"| {comp.metric} | {comp.actual:.2f}{comp.unit} | "
                      f"{comp.benchmark:.2f}{comp.unit} | {gap_str} | {comp.status} {comp.advice} |")
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"*由 financial_ratio_calc.py 生成 | 行业基准来源：ib-execution 技能库*")
    return "\n".join(lines)


def format_json_output(ratios: FinancialRatios, industry: str) -> str:
    """生成JSON格式输出"""
    comparisons = compare_to_benchmark(ratios, industry)
    red_flags = detect_red_flags(ratios)
    score = compute_score(comparisons, ratios)
    grade = get_grade(score)

    output = {
        "report": {
            "industry": industry,
            "score": score,
            "grade": grade,
            "red_flags": red_flags,
        },
        "ratios": {
            "profitability": {
                "gross_margin": round(ratios.gross_margin, 4),
                "net_margin": round(ratios.net_margin, 4),
                "roe": round(ratios.roe, 4),
                "roa": round(ratios.roa, 4),
                "operating_margin": round(ratios.operating_margin, 4),
                "ebitda_margin": round(ratios.ebitda_margin, 4),
            },
            "solvency": {
                "debt_ratio": round(ratios.debt_ratio, 4),
                "current_ratio": round(ratios.current_ratio, 4),
                "quick_ratio": round(ratios.quick_ratio, 4),
                "interest_coverage": round(ratios.interest_coverage, 4),
            },
            "efficiency": {
                "asset_turnover": round(ratios.asset_turnover, 4),
                "inventory_turnover": round(ratios.inventory_turnover, 4),
                "receivable_turnover": round(ratios.receivable_turnover, 4),
                "days_sales_outstanding": round(ratios.days_sales_outstanding, 2),
                "days_inventory": round(ratios.days_inventory, 2),
            },
            "growth": {
                "revenue_growth": round(ratios.revenue_growth, 4),
                "profit_growth": round(ratios.profit_growth, 4),
                "net_asset_growth": round(ratios.net_asset_growth, 4),
                "ebitda_growth": round(ratios.ebitda_growth, 4),
            },
            "cashflow": {
                "operating_cf_ratio": round(ratios.operating_cf_ratio, 4),
                "free_cf_to_revenue": round(ratios.free_cf_to_revenue, 4),
                "capex_to_revenue": round(ratios.capex_to_revenue, 4),
            },
            "per_share": {
                "eps": round(ratios.eps, 4),
                "bvps": round(ratios.bvps, 4),
            },
        },
        "benchmark_comparison": [
            {
                "metric": c.metric,
                "actual": round(c.actual, 4),
                "benchmark": round(c.benchmark, 4),
                "unit": c.unit,
                "status": c.status,
                "gap": round(c.gap, 4),
                "advice": c.advice,
            }
            for c in comparisons
        ],
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


# ============================================================================
# 交互输入
# ============================================================================

def interactive_input() -> Dict[str, Any]:
    """交互式收集财务数据"""
    print("=" * 60)
    print("  A股财务比率计算器 - 交互模式")
    print("=" * 60)
    print("请输入财务数据（直接回车使用0）\n")

    def ask(prompt: str, default: float = 0.0) -> float:
        try:
            val = input(f"  {prompt}: ")
            return float(val) if val.strip() else default
        except ValueError:
            print("  ⚠️ 输入无效，使用默认值0")
            return 0.0

    revenue = ask("营业收入（万元）")
    cogs = ask("营业成本（万元）")
    net_profit = ask("净利润（万元）")
    total_assets = ask("资产总额（万元）")
    total_liabilities = ask("负债总额（万元）")
    current_assets = ask("流动资产（万元）")
    current_liabilities = ask("流动负债（万元）")
    inventory = ask("存货（万元）")
    accounts_receivable = ask("应收账款（万元）")
    operating_cf = ask("经营现金流（万元）")
    capex = ask("资本支出（万元）")
    interest_expense = ask("利息支出（万元）", 100.0)
    ebit = ask("EBIT（万元）", net_profit * 1.2)
    depreciation = ask("折旧（万元）", 0.0)
    amortization = ask("摊销（万元）", 0.0)
    shares = ask("总股本（亿股）", 1.0)

    print("\n--- 上年同期数据（计算增长率用）---")
    revenue_prior = ask("上年营业收入（万元）", revenue)
    net_profit_prior = ask("上年净利润（万元）", 0.0)
    equity_prior = ask("上年净资产（万元）", 0.0)

    print("\n--- 基本信息 ---")
    industry = input("  行业 [manufacturing/semiconductor/software/pharma/consumer/real_estate]: ").strip() or "default"
    if industry not in INDUSTRY_BENCHMARKS:
        print(f"  ⚠️ 未知行业 '{industry}'，使用 default 基准")
        industry = "default"
    company = input("  公司名称: ").strip() or "目标公司"
    period = input("  报告期（如2024年报）: ").strip() or "本期"

    return {
        "revenue": revenue,
        "cogs": cogs,
        "net_profit": net_profit,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "current_assets": current_assets,
        "current_liabilities": current_liabilities,
        "inventory": inventory,
        "accounts_receivable": accounts_receivable,
        "operating_cf": operating_cf,
        "capex": capex,
        "interest_expense": interest_expense,
        "ebit": ebit,
        "depreciation": depreciation,
        "amortization": amortization,
        "shares": shares,
        "revenue_prior": revenue_prior,
        "net_profit_prior": net_profit_prior,
        "equity_prior": equity_prior,
        "industry": industry,
        "company": company,
        "period": period,
    }


# ============================================================================
# 内置测试用例
# ============================================================================

def run_tests() -> bool:
    """运行内置测试用例，验证关键计算路径"""
    print("=" * 60)
    print("  Running Built-in Test Cases")
    print("=" * 60)

    all_passed = True

    # 测试1：基本盈利能力计算
    print("\n[TEST 1] 盈利能力计算")
    r = compute_ratios(
        revenue=10000, cogs=6000, net_profit=800,
        total_assets=20000, total_liabilities=10000,
        current_assets=8000, current_liabilities=4000,
        inventory=2000, accounts_receivable=1500,
        operating_cf=900, capex=200, interest_expense=200,
        ebit=1000, revenue_prior=9000, net_profit_prior=700,
        equity_prior=8000,
    )
    assert abs(r.gross_margin - 0.4) < 0.01, f"gross_margin={r.gross_margin}"
    assert abs(r.net_margin - 0.08) < 0.01, f"net_margin={r.net_margin}"
    print(f"  ✓ 毛利率={r.gross_margin:.1%}, 净利率={r.net_margin:.1%}")

    # 测试2：ROE计算
    print("[TEST 2] ROE计算")
    assert abs(r.roe - 0.08) < 0.01, f"roe={r.roe}"
    print(f"  ✓ ROE={r.roe:.1%}")

    # 测试3：偿债能力
    print("[TEST 3] 偿债能力")
    assert abs(r.debt_ratio - 0.5) < 0.01, f"debt_ratio={r.debt_ratio}"
    assert abs(r.current_ratio - 2.0) < 0.01, f"current_ratio={r.current_ratio}"
    print(f"  ✓ 资产负债率={r.debt_ratio:.1%}, 流动比率={r.current_ratio:.2f}x")

    # 测试4：利息保障倍数
    print("[TEST 4] 利息保障倍数")
    assert abs(r.interest_coverage - 5.0) < 0.01, f"interest_coverage={r.interest_coverage}"
    print(f"  ✓ 利息保障倍数={r.interest_coverage:.1f}x")

    # 测试5：应收账款周转天数
    print("[TEST 5] 应收账款周转天数")
    assert abs(r.days_sales_outstanding - 54.75) < 0.1, f"dso={r.days_sales_outstanding}"
    print(f"  ✓ 应收账款周转天数={r.days_sales_outstanding:.1f}天")

    # 测试6：成长能力
    print("[TEST 6] 成长能力")
    assert abs(r.revenue_growth - 0.111) < 0.01, f"revenue_growth={r.revenue_growth}"
    print(f"  ✓ 收入增长={r.revenue_growth:.1%}")

    # 测试7：速动比率
    print("[TEST 7] 速动比率")
    assert abs(r.quick_ratio - 1.5) < 0.01, f"quick_ratio={r.quick_ratio}"
    print(f"  ✓ 速动比率={r.quick_ratio:.2f}x")

    # 测试8：经营现金流/净利润
    print("[TEST 8] 经营现金流/净利润")
    assert abs(r.operating_cf_ratio - 1.125) < 0.01, f"ocf_ratio={r.operating_cf_ratio}"
    print(f"  ✓ OCF/NetProfit={r.operating_cf_ratio:.3f}x")

    # 测试9：半导体行业对比
    print("[TEST 9] 行业基准对比 - 半导体")
    comps = compare_to_benchmark(r, "semiconductor")
    green_count = sum(1 for c in comps if c.status == "🟢")
    print(f"  ✓ 优于行业基准指标数: {green_count}/{len(comps)}")

    # 测试10：综合评分
    print("[TEST 10] 综合评分")
    score = compute_score(comps, r)
    assert 1 <= score <= 100, f"score={score}"
    grade = get_grade(score)
    print(f"  ✓ 评分={score}/100, 等级={grade}")

    # 测试11：红旗检测
    print("[TEST 11] 红旗检测")
    r_bad = compute_ratios(
        revenue=1000, cogs=900, net_profit=-100,
        total_assets=5000, total_liabilities=4500,
        current_assets=800, current_liabilities=2000,
        inventory=500, accounts_receivable=800,
        operating_cf=-50, capex=100, interest_expense=200,
        ebit=-50, revenue_prior=1200, net_profit_prior=50,
        equity_prior=400,
    )
    flags = detect_red_flags(r_bad)
    assert len(flags) > 0, "应检测到红旗"
    print(f"  ✓ 检测到 {len(flags)} 个风险点: {[f[:20] for f in flags]}")

    # 测试12：格式化为JSON
    print("[TEST 12] JSON输出")
    json_str = format_json_output(r, "manufacturing")
    parsed = json.loads(json_str)
    assert "ratios" in parsed
    assert "profitability" in parsed["ratios"]
    print(f"  ✓ JSON输出包含 {len(parsed['ratios'])} 个类别")

    # 测试13：Markdown输出
    print("[TEST 13] Markdown输出")
    md = format_ratio_table(r, "manufacturing", "测试公司", "2024年报")
    assert "# 财务比率分析报告" in md
    assert "盈利能力" in md
    assert "偿债能力" in md
    print(f"  ✓ Markdown输出包含 {len(md)} 字符")

    # 测试14：除零保护
    print("[TEST 14] 除零保护")
    r_zero = compute_ratios(
        revenue=0, cogs=0, net_profit=0,
        total_assets=0, total_liabilities=0,
        current_assets=0, current_liabilities=0,
        inventory=0, accounts_receivable=0,
        operating_cf=0, capex=0, interest_expense=0,
        ebit=0, revenue_prior=0, net_profit_prior=0,
        equity_prior=0,
    )
    assert r_zero.gross_margin == 0.0
    assert r_zero.current_ratio == 0.0
    print(f"  ✓ 除零场景安全处理")

    # 测试15：行业基准完整性
    print("[TEST 15] 行业基准完整性")
    for ind_name, bench in INDUSTRY_BENCHMARKS.items():
        required = ["gross_margin", "net_margin", "roe", "debt_ratio", "current_ratio"]
        for key in required:
            assert key in bench, f"Missing {key} in {ind_name}"
    print(f"  ✓ {len(INDUSTRY_BENCHMARKS)} 个行业基准完整")

    print("\n" + "=" * 60)
    print("  ✅ All 15 tests passed!")
    print("=" * 60)
    return all_passed


# ============================================================================
# 主入口
# ============================================================================

def main() -> None:
    # 提前处理 --test（必须在 parse_args 之前）
    if "--test" in sys.argv:
        success = run_tests()
        sys.exit(0 if success else 1)

    parser = argparse.ArgumentParser(
        description="A股投行财务比率计算工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的行业: manufacturing | semiconductor | software |
           pharma | consumer | real_estate | banking | default

示例:
  %(prog)s --test                          # 运行内置测试
  %(prog)s interactive                      # 交互式输入
  %(prog)s benchmark                        # 显示行业基准
  %(prog)s file -i data.json --industry software
  %(prog)s file -i data.json --industry software --json
        """,
    )

    sub = parser.add_subparsers(dest="cmd", title="命令模式")

    # 交互输入模式
    sub.add_parser("interactive", help="交互式输入财务数据并计算")

    # 行业基准模式
    sub.add_parser("benchmark", help="显示所有行业基准数据")

    # 文件模式
    file_p = sub.add_parser("file", help="从JSON文件读取财务数据并计算")
    file_p.add_argument("--input", "-i", required=True, help="输入JSON文件路径")
    file_p.add_argument(
        "--industry", "-I", default="default",
        help="行业类型（默认: default）"
    )
    file_p.add_argument("--json", action="store_true", help="JSON格式输出")
    file_p.add_argument(
        "--output", "-o",
        help="输出文件路径（默认: stdout）"
    )
    file_p.add_argument(
        "--company", "-c", default="目标公司",
        help="公司名称（用于报告）"
    )
    file_p.add_argument(
        "--period", "-p", default="本期",
        help="报告期（用于报告）"
    )

    # 测试模式

    args = parser.parse_args()

    # 测试模式
    # 行业基准展示
    if args.cmd == "benchmark":
        print(json.dumps(INDUSTRY_BENCHMARKS, indent=2, ensure_ascii=False))
        return

    # 交互模式
    if args.cmd == "interactive" or args.cmd is None:
        data = interactive_input()
        industry = data.pop("industry")
        company = data.pop("company")
        period = data.pop("period")
        ratios = compute_ratios(**data)
        print("\n" + format_ratio_table(ratios, industry, company, period))
        return

    # 文件模式
    if args.cmd == "file":
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ 文件读取错误: {e}", file=sys.stderr)
            sys.exit(1)

        # 支持两种格式：直接传参式 或 嵌套式
        if isinstance(data, dict) and "revenue" in data:
            # 直接参数式
            params = {k: v for k, v in data.items()
                      if k in ["revenue", "cogs", "net_profit", "total_assets",
                               "total_liabilities", "current_assets", "current_liabilities",
                               "inventory", "accounts_receivable", "operating_cf",
                               "capex", "interest_expense", "ebit",
                               "revenue_prior", "net_profit_prior", "equity_prior",
                               "depreciation", "amortization", "shares"]}
            ratios = compute_ratios(**params)
        elif isinstance(data, dict) and any(k in data for k in ["balance", "income", "cashflow"]):
            # 三表嵌套式
            bal = data.get("balance", {})
            inc = data.get("income", {})
            periods = sorted(bal.keys() if isinstance(bal, dict) else [d.get("period") for d in bal])
            current = periods[-1] if periods else "2024"
            b = bal.get(current, bal) if isinstance(bal, dict) else bal[-1]
            i = inc.get(current, inc) if isinstance(inc, dict) else inc[-1]
            cf_data = data.get("cashflow", {})
            c = cf_data.get(current, cf_data) if isinstance(cf_data, dict) else (cf_data[-1] if cf_data else {})

            def get_val(d, *keys, default=0.0):
                for k in keys:
                    if k in d:
                        v = d[k]
                        return float(v) if v is not None else default
                return default

            ratios = compute_ratios(
                revenue=get_val(i, "revenue"),
                cogs=get_val(i, "cost_of_sales"),
                net_profit=get_val(i, "net_profit"),
                total_assets=get_val(b, "total_assets"),
                total_liabilities=get_val(b, "total_liabilities"),
                current_assets=get_val(b, "current_assets"),
                current_liabilities=get_val(b, "current_liabilities"),
                inventory=get_val(b, "inventory"),
                accounts_receivable=get_val(b, "accounts_receivable"),
                operating_cf=get_val(c, "operating_cf"),
                capex=get_val(c, "capex"),
                interest_expense=get_val(i, "interest_expense"),
                ebit=get_val(i, "ebit", "operating_profit", default=get_val(i, "net_profit") * 1.2),
                revenue_prior=get_val(i, "revenue_prior", default=get_val(i, "revenue") * 0.9),
                net_profit_prior=get_val(i, "net_profit_prior", default=0.0),
                equity_prior=get_val(b, "net_assets", "equity_prior", default=get_val(b, "net_assets", "total_assets") * 0.5),
                depreciation=get_val(i, "depreciation"),
                amortization=get_val(i, "amortization"),
                shares=get_val(data, "shares", default=1.0),
            )
        else:
            print("❌ JSON格式不支持，请使用直接参数式或三表嵌套式", file=sys.stderr)
            sys.exit(1)

        if args.json:
            output_str = format_json_output(ratios, args.industry)
        else:
            output_str = format_ratio_table(ratios, args.industry, args.company, args.period)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"✅ 结果已保存至 {args.output}")
        else:
            print(output_str)
        return

    # 无命令参数时默认进入交互模式
    data = interactive_input()
    industry = data.pop("industry")
    company = data.pop("company")
    period = data.pop("period")
    ratios = compute_ratios(**data)
    print("\n" + format_ratio_table(ratios, industry, company, period))


if __name__ == "__main__":
    main()
