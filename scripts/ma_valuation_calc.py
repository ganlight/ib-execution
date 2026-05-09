#!/usr/bin/env python3
"""
并购估值计算工具
支持：DCF估值 / 可比公司法 / 国有资产备案格式
输出：估值区间 + Markdown分析报告

Usage:
    python ma_valuation_calc.py dcf --fcf 1.0 1.2 1.4 1.5 1.6 --wacc 0.10 --tg 0.02 --net-debt 5.0 --shares 1.0
    python ma_valuation_calc.py comp --ebitda 3.0 --revenue 10.0 --multiples 8.0 10.0 12.0
    python ma_valuation_calc.py full --fcf 1.0 1.2 1.4 1.5 1.6 --wacc 0.10 --tg 0.02 \\
        --ebitda 3.0 --revenue 10.0 --multiples 8.0 10.0 12.0
    python ma_valuation_calc.py state-owned --fcf 1.0 1.2 1.4 1.5 1.6 --wacc 0.09 \\
        --tg 0.025 --net-debt 3.0 --shares 1.0 --ebitda 3.0 --revenue 10.0 --multiples 8.0 10.0 12.0
    python ma_valuation_calc.py --test
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Tuple


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class DCFResult:
    """DCF估值结果"""
    pv_fcf: float          # 预测期现金流现值（亿元）
    terminal_value: float  # 永续价值（亿元）
    pv_terminal: float     # 永续价值现值（亿元）
    enterprise_value: float  # 企业价值（亿元）
    equity_value: float    # 股权价值（亿元）
    wacc: float            # 加权平均资本成本
    terminal_growth: float  # 永续增长率
    net_debt: float        # 净债务
    shares: float          # 股本（亿股）
    per_share: float       # 每股价值（元/股）
    sensitivity: Dict[str, float]  # 敏感性分析结果

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pv_fcf": round(self.pv_fcf, 2),
            "terminal_value": round(self.terminal_value, 2),
            "pv_terminal": round(self.pv_terminal, 2),
            "enterprise_value": round(self.enterprise_value, 2),
            "equity_value": round(self.equity_value, 2),
            "wacc": round(self.wacc, 4),
            "terminal_growth": round(self.terminal_growth, 4),
            "net_debt": round(self.net_debt, 2),
            "shares": round(self.shares, 4),
            "per_share": round(self.per_share, 2),
            "sensitivity": {k: round(v, 2) for k, v in self.sensitivity.items()},
        }


@dataclass
class ComparableResult:
    """可比公司法估值结果"""
    ev_ebitda_low: float
    ev_ebitda_mid: float
    ev_ebitda_high: float
    ev_rev_low: Optional[float] = None
    ev_rev_mid: Optional[float] = None
    ev_rev_high: Optional[float] = None
    combined_low: Optional[float] = None
    combined_mid: Optional[float] = None
    combined_high: Optional[float] = None
    implied_per_share: Optional[float] = None
    peer_details: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        return {k: round(v, 2) if isinstance(v, float) else v for k, v in result.items()}


@dataclass
class StateOwnedFiling:
    """国有资产评估备案格式"""
    project_name: str
    report_number: str
    valuation_date: str
    target_name: str
    target_industry: str
    valuation_methods: List[str]
    dcf_result: DCFResult
    comp_result: Optional[ComparableResult]
    final_equity_value: float
    final_per_share: float
    currency: str = "CNY"
    unit: str = "万元"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "report_number": self.report_number,
            "valuation_date": self.valuation_date,
            "target_name": self.target_name,
            "target_industry": self.target_industry,
            "valuation_methods": self.valuation_methods,
            "dcf_result": self.dcf_result.to_dict(),
            "comp_result": self.comp_result.to_dict() if self.comp_result else None,
            "final_equity_value": round(self.final_equity_value, 2),
            "final_per_share": round(self.final_per_share, 2),
            "currency": self.currency,
            "unit": self.unit,
        }


# ============================================================================
# DCF 核心计算
# ============================================================================

def dcf_calculate(
    fcf_list: List[float],
    wacc: float,
    terminal_growth: float,
    net_debt: float = 0.0,
    shares: float = 1.0,
) -> DCFResult:
    """
    DCF估值核心函数

    Args:
        fcf_list: 预测自由现金流序列（亿元），长度N代表预测N年
        wacc: 加权平均资本成本（小数，如0.10代表10%）
        terminal_growth: 永续增长率（小数，如0.02代表2%）
        net_debt: 净债务（亿元）
        shares: 股本（亿股）

    Returns:
        DCFResult: 包含所有DCF估值指标的对象

    Raises:
        ValueError: 如果 wacc <= terminal_growth（数学上无意义）
    """
    if wacc <= terminal_growth:
        raise ValueError(
            f"WACC ({wacc:.2%}) must be greater than terminal growth ({terminal_growth:.2%})"
        )

    n = len(fcf_list)

    # 1. 预测期现金流现值
    pv_fcf = sum(
        fcf / (1 + wacc) ** (t + 1)
        for t, fcf in enumerate(fcf_list)
    )

    # 2. 永续价值
    terminal_value = fcf_list[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** n

    # 3. 企业价值
    enterprise_value = pv_fcf + pv_terminal

    # 4. 股权价值
    equity_value = enterprise_value - net_debt

    # 5. 每股价值
    per_share = equity_value / shares if shares > 0 else 0.0

    # 6. 敏感性分析（WACC × 永续增长率）
    sensitivity: Dict[str, float] = {}
    wacc_vals = [wacc - 0.01, wacc, wacc + 0.01]
    tg_vals = [terminal_growth - 0.005, terminal_growth, terminal_growth + 0.005]

    for w in wacc_vals:
        for tg in tg_vals:
            if w > tg > 0:
                tv = fcf_list[-1] * (1 + tg) / (w - tg)
                pv_t = tv / (1 + w) ** n
                pv_fcf_adj = sum(
                    fcf / (1 + w) ** (t + 1) for t, fcf in enumerate(fcf_list)
                )
                ev_adj = pv_fcf_adj + pv_t
                e_adj = (ev_adj - net_debt) / shares if shares != 0 else 0.0
                sensitivity[f"WACC={w:.1%}_TG={tg:.1%}"] = round(e_adj, 2)

    return DCFResult(
        pv_fcf=round(pv_fcf, 2),
        terminal_value=round(terminal_value, 2),
        pv_terminal=round(pv_terminal, 2),
        enterprise_value=round(enterprise_value, 2),
        equity_value=round(equity_value, 2),
        wacc=round(wacc, 4),
        terminal_growth=round(terminal_growth, 4),
        net_debt=round(net_debt, 2),
        shares=round(shares, 4),
        per_share=round(per_share, 2),
        sensitivity=sensitivity,
    )


# ============================================================================
# 可比公司法
# ============================================================================

def comparable_calculate(
    target_ebitda: float,
    target_revenue: float,
    comp_ev_ebitda: List[float],
    comp_ev_rev: Optional[List[float]] = None,
    weights: Tuple[float, float] = (0.7, 0.3),
    net_debt: float = 0.0,
    shares: float = 1.0,
) -> ComparableResult:
    """
    可比公司法估值

    Args:
        target_ebitda: 目标公司EBITDA（亿元）
        target_revenue: 目标公司营业收入（亿元）
        comp_ev_ebitda: 可比公司EV/EBITDA倍数列表
        comp_ev_rev: 可比公司EV/Revenue倍数列表
        weights: (EV/EBITDA权重, EV/Revenue权重)
        net_debt: 净债务（亿元），用于计算每股价值
        shares: 股本（亿股）

    Returns:
        ComparableResult: 可比公司法估值结果
    """
    # EV/EBITDA法
    ev_ebitda_values = sorted([target_ebitda * m for m in comp_ev_ebitda])
    ev_ebitda_low = ev_ebitda_values[0]
    ev_ebitda_high = ev_ebitda_values[-1]
    ev_ebitda_mid = ev_ebitda_values[len(ev_ebitda_values) // 2]

    result = ComparableResult(
        ev_ebitda_low=round(ev_ebitda_low, 2),
        ev_ebitda_mid=round(ev_ebitda_mid, 2),
        ev_ebitda_high=round(ev_ebitda_high, 2),
    )

    # EV/Revenue法（如果有）
    if comp_ev_rev:
        ev_rev_values = sorted([target_revenue * m for m in comp_ev_rev])
        result.ev_rev_low = round(ev_rev_values[0], 2)
        result.ev_rev_mid = round(ev_rev_values[len(ev_rev_values) // 2], 2)
        result.ev_rev_high = round(ev_rev_values[-1], 2)

        # 加权综合
        w1, w2 = weights
        ev_values_low = sorted([ev_ebitda_low, result.ev_rev_low])
        ev_values_mid = sorted([ev_ebitda_mid, result.ev_rev_mid])
        ev_values_high = sorted([ev_ebitda_high, result.ev_rev_high])

        result.combined_low = round(
            ev_values_low[0] * w1 + result.ev_rev_low * w2, 2
        )
        result.combined_mid = round(
            ev_values_mid[len(ev_values_mid) // 2] * w1 + result.ev_rev_mid * w2, 2
        )
        result.combined_high = round(
            ev_values_high[-1] * w1 + result.ev_rev_high * w2, 2
        )

    # 每股价值（使用中间值）
    use_ev = result.combined_mid if result.combined_mid else ev_ebitda_mid
    implied_equity = use_ev - net_debt
    result.implied_per_share = round(implied_equity / shares, 2) if shares > 0 else 0.0

    return result


# ============================================================================
# 综合估值
# ============================================================================

def 综合估值(
    dcf_result: DCFResult,
    comp_result: ComparableResult,
    dcf_weight: float = 0.5,
) -> Dict[str, float]:
    """
    综合DCF和可比公司法，给出最终估值区间

    Args:
        dcf_result: DCF估值结果
        comp_result: 可比公司法结果
        dcf_weight: DCF权重（1 - dcf_weight为可比公司法权重）

    Returns:
        dict: 包含 low/mid/high 股权价值和每股价值
    """
    comp_mid = (comp_result.combined_mid if comp_result.combined_mid
                else comp_result.ev_ebitda_mid)

    # 股权价值
    low = dcf_result.equity_value * (1 - 0.2)  # DCF下浮20%
    mid = (dcf_result.equity_value * dcf_weight +
           comp_mid * (1 - dcf_weight))
    high = comp_mid * (1 + 0.2)  # 可比公司法上浮20%

    shares = dcf_result.shares
    return {
        "equity_low": round(low, 2),
        "equity_mid": round(mid, 2),
        "equity_high": round(high, 2),
        "per_share_low": round(low / shares, 2) if shares else 0.0,
        "per_share_mid": round(mid / shares, 2) if shares else 0.0,
        "per_share_high": round(high / shares, 2) if shares else 0.0,
    }


# ============================================================================
# 国有资产备案格式
# ============================================================================

def format_state_owned_filing(
    filing: StateOwnedFiling,
) -> str:
    """生成国有资产评估备案格式的Markdown报告"""
    lines: List[str] = []

    lines.append("# 国有资产评估项目备案表")
    lines.append("")
    lines.append(f"| 项目名称 | {filing.project_name} |")
    lines.append(f"| 报告编号 | {filing.report_number} |")
    lines.append(f"| 评估基准日 | {filing.valuation_date} |")
    lines.append(f"| 评估对象 | {filing.target_name} |")
    lines.append(f"| 所属行业 | {filing.target_industry} |")
    lines.append(f"| 评估方法 | {', '.join(filing.valuation_methods)} |")
    lines.append(f"| 币种 | {filing.currency} |")
    lines.append("")

    lines.append("## 一、DCF估值结果")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 预测期现金流现值 | {filing.dcf_result.pv_fcf:.2f} 亿元 |")
    lines.append(f"| 永续价值 | {filing.dcf_result.terminal_value:.2f} 亿元 |")
    lines.append(f"| 永续价值现值 | {filing.dcf_result.pv_terminal:.2f} 亿元 |")
    lines.append(f"| 企业价值（EV） | {filing.dcf_result.enterprise_value:.2f} 亿元 |")
    lines.append(f"| 减：净债务 | {filing.dcf_result.net_debt:.2f} 亿元 |")
    lines.append(f"| **股权价值** | **{filing.dcf_result.equity_value:.2f} 亿元** |")
    lines.append(f"| 股本 | {filing.dcf_result.shares:.4f} 亿股 |")
    lines.append(f"| **每股价值** | **{filing.dcf_result.per_share:.2f} 元/股** |")
    lines.append(f"| WACC | {filing.dcf_result.wacc:.2%} |")
    lines.append(f"| 永续增长率 | {filing.dcf_result.terminal_growth:.2%} |")
    lines.append("")

    # 敏感性分析
    lines.append("### DCF敏感性分析（每股价值，元/股）")
    lines.append("")
    lines.append("| WACC \\ 永续增长率 | 永续-0.5% | 永续 | 永续+0.5% |")
    lines.append("|------|-----------|------|-----------|")

    wacc_vals = [filing.dcf_result.wacc - 0.01, filing.dcf_result.wacc,
                 filing.dcf_result.wacc + 0.01]
    tg_offsets = [-0.005, 0.0, 0.005]

    for w in wacc_vals:
        row = [f"{w:.1%}"]
        for tg_off in tg_offsets:
            key = f"WACC={w:.1%}_TG={filing.dcf_result.wacc + tg_off:.1%}"
            val = filing.dcf_result.sensitivity.get(key, 0.0)
            row.append(f"{val:.2f}")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    if filing.comp_result:
        lines.append("## 二、可比公司法估值结果")
        lines.append("")
        lines.append(f"| 指标 | 低值 | 中值 | 高值 |")
        lines.append(f"|------|------|------|------|")
        lines.append(f"| EV/EBITDA法 | {filing.comp_result.ev_ebitda_low:.2f}亿 | "
                      f"{filing.comp_result.ev_ebitda_mid:.2f}亿 | "
                      f"{filing.comp_result.ev_ebitda_high:.2f}亿 |")
        if filing.comp_result.ev_rev_mid:
            lines.append(f"| EV/Revenue法 | {filing.comp_result.ev_rev_low:.2f}亿 | "
                          f"{filing.comp_result.ev_rev_mid:.2f}亿 | "
                          f"{filing.comp_result.ev_rev_high:.2f}亿 |")
            lines.append(f"| 加权综合 | {filing.comp_result.combined_low:.2f}亿 | "
                          f"{filing.comp_result.combined_mid:.2f}亿 | "
                          f"{filing.comp_result.combined_high:.2f}亿 |")
        lines.append("")

    lines.append("## 三、最终评估结论")
    lines.append("")
    lines.append(f"| 项目 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| **最终股权价值** | **{filing.final_equity_value:.2f} 亿元** |")
    lines.append(f"| **每股价值** | **{filing.final_per_share:.2f} 元/股** |")
    lines.append("")
    lines.append(f"*本报告按 {filing.currency} / {filing.unit} 为单位*")
    lines.append(f"*由 ma_valuation_calc.py 生成 | 国有资产评估备案格式*")

    return "\n".join(lines)


# ============================================================================
# Markdown 报告
# ============================================================================

def format_ma_report(
    dcf: DCFResult,
    comp: Optional[ComparableResult],
    net_debt: float,
    shares: float,
    target_name: str = "目标公司",
    industry: str = "一般",
) -> str:
    """生成并购估值分析Markdown报告"""
    lines: List[str] = []

    lines.append(f"# 并购估值分析报告")
    lines.append(f"")
    lines.append(f"**目标公司：** {target_name}  |  **行业：** {industry}")
    lines.append(f"")

    # DCF结果
    lines.append(f"## 一、DCF估值结果")
    lines.append(f"")
    lines.append(f"| 指标 | 数值（亿元） | 说明 |")
    lines.append(f"|------|------------|------|")
    lines.append(f"| 预测期现金流现值 | {dcf.pv_fcf:.2f} | |")
    lines.append(f"| 永续价值 | {dcf.terminal_value:.2f} | |")
    lines.append(f"| 永续价值现值 | {dcf.pv_terminal:.2f} | |")
    lines.append(f"| **企业价值（EV）** | **{dcf.enterprise_value:.2f}** | |")
    lines.append(f"| 减：净债务 | {net_debt:.2f} | |")
    lines.append(f"| **股权价值** | **{dcf.equity_value:.2f}** | |")
    lines.append(f"| 股本 | {shares:.4f}亿股 | |")
    lines.append(f"| **每股价值** | **{dcf.per_share:.2f}元/股** | |")
    lines.append(f"")
    lines.append(f"**参数设定：** WACC = {dcf.wacc:.1%}，永续增长率 = {dcf.terminal_growth:.2%}")
    lines.append(f"")

    # 敏感性分析
    lines.append(f"### 敏感性分析（每股价值，元/股）")
    lines.append(f"")
    lines.append(f"| WACC \\ 永续增长率 | 永续-0.5% | 永续 | 永续+0.5% |")
    lines.append(f"|------|-----------|------|-----------|")

    wacc_vals = [dcf.wacc - 0.01, dcf.wacc, dcf.wacc + 0.01]
    tg_offsets = [-0.005, 0.0, 0.005]

    for w in wacc_vals:
        row = [f"{w:.1%}"]
        for tg_off in tg_offsets:
            key = f"WACC={w:.1%}_TG={dcf.wacc + tg_off:.1%}"
            val = dcf.sensitivity.get(key, 0.0)
            row.append(f"{val:.2f}")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # 可比公司法
    if comp:
        lines.append(f"## 二、可比公司法估值")
        lines.append(f"")
        lines.append(f"| 指标 | 低值 | 中值 | 高值 |")
        lines.append(f"|------|------|------|------|")
        lines.append(f"| EV/EBITDA法 | {comp.ev_ebitda_low:.2f}亿 | "
                      f"{comp.ev_ebitda_mid:.2f}亿 | {comp.ev_ebitda_high:.2f}亿 |")
        if comp.ev_rev_mid:
            lines.append(f"| EV/Revenue法 | {comp.ev_rev_low:.2f}亿 | "
                          f"{comp.ev_rev_mid:.2f}亿 | {comp.ev_rev_high:.2f}亿 |")
            lines.append(f"| **加权综合** | **{comp.combined_low:.2f}亿** | "
                          f"**{comp.combined_mid:.2f}亿** | **{comp.combined_high:.2f}亿** |")
        if comp.implied_per_share:
            lines.append(f"| 隐含每股价值 | - | {comp.implied_per_share:.2f}元/股 | - |")
        lines.append("")

        # 综合结论
        combined = 综合估值(dcf, comp, dcf_weight=0.5)
        lines.append(f"## 三、综合估值结论")
        lines.append(f"")
        lines.append(f"| 情景 | 股权价值（亿元） | 每股价值（元/股） |")
        lines.append(f"|------|------------------|-----------------|")
        lines.append(f"| 保守（DCF-20%） | {combined['equity_low']:.2f} | "
                      f"{combined['per_share_low']:.2f} |")
        lines.append(f"| **基准（DCF 50% + 可比 50%）** | **{combined['equity_mid']:.2f}** | "
                      f"**{combined['per_share_mid']:.2f}** |")
        lines.append(f"| 乐观（可比+20%） | {combined['equity_high']:.2f} | "
                      f"{combined['per_share_high']:.2f} |")
        lines.append("")
        mid_per_share = combined['per_share_mid']
        lines.append(f"**估值中枢：{mid_per_share:.2f} 元/股**（"
                     f"股权价值 {combined['equity_mid']:.2f} 亿元）")
        lines.append("")

    lines.append(f"---")
    lines.append(f"*由 ma_valuation_calc.py 生成 | ib-execution 技能库*")

    return "\n".join(lines)


# ============================================================================
# 内置测试用例
# ============================================================================

def run_tests() -> bool:
    """运行内置测试用例，验证所有关键计算路径"""
    print("=" * 60)
    print("  Running Built-in Test Cases - MA Valuation")
    print("=" * 60)

    all_passed = True

    # TEST 1: DCF基础计算
    print("\n[TEST 1] DCF基础计算")
    fcf_list = [1.0, 1.2, 1.4, 1.5, 1.6]
    result = dcf_calculate(fcf_list, wacc=0.10, terminal_growth=0.02,
                           net_debt=5.0, shares=1.0)
    assert result.wacc == 0.1
    assert result.terminal_growth == 0.02
    assert result.net_debt == 5.0
    assert result.equity_value == result.enterprise_value - 5.0
    assert result.per_share == result.equity_value
    print(f"  ✓ EV={result.enterprise_value:.2f}亿, 股权价值={result.equity_value:.2f}亿, "
          f"每股={result.per_share:.2f}元")

    # TEST 2: DCF数学验证
    print("[TEST 2] DCF数学验证")
    # 已知: FCF=[1,1.2], WACC=10%, TG=2%
    # PV_FCF = 1/1.1 + 1.2/1.1^2 = 0.9091 + 0.9917 = 1.9008
    # TV = 1.2*1.02/(0.10-0.02) = 1.224/0.08 = 15.30
    # PV_TV = 15.30/1.1^2 = 12.64
    # EV = 1.9008 + 12.64 = 14.54
    result2 = dcf_calculate([1.0, 1.2], wacc=0.10, terminal_growth=0.02)
    assert abs(result2.pv_fcf - 1.90) < 0.1, f"pv_fcf={result2.pv_fcf}"
    assert abs(result2.terminal_value - 15.30) < 0.5, f"tv={result2.terminal_value}"
    print(f"  ✓ PV_FCF={result2.pv_fcf:.2f}亿, 永续价值={result2.terminal_value:.2f}亿, "
          f"EV={result2.enterprise_value:.2f}亿")

    # TEST 3: 敏感性分析
    print("[TEST 3] 敏感性分析")
    assert len(result.sensitivity) == 9  # 3x3
    for key, val in result.sensitivity.items():
        assert val >= 0, f"negative per share in {key}: {val}"
    print(f"  ✓ {len(result.sensitivity)} 个敏感性情景均非负")

    # TEST 4: WACC <= TG 应报错
    print("[TEST 4] WACC <= TG 异常处理")
    try:
        dcf_calculate([1.0, 1.2], wacc=0.02, terminal_growth=0.03)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ 正确抛出 ValueError")

    # TEST 5: 可比公司法基础
    print("[TEST 5] 可比公司法 - EV/EBITDA")
    comp = comparable_calculate(
        target_ebitda=3.0,
        target_revenue=10.0,
        comp_ev_ebitda=[8.0, 10.0, 12.0],
    )
    assert comp.ev_ebitda_low == 24.0   # 3*8
    assert comp.ev_ebitda_mid == 30.0   # 3*10
    assert comp.ev_ebitda_high == 36.0  # 3*12
    print(f"  ✓ EV区间: {comp.ev_ebitda_low:.1f}-{comp.ev_ebitda_high:.1f}亿")

    # TEST 6: 可比公司法 - EV/Revenue
    print("[TEST 6] 可比公司法 - EV/Revenue + 加权综合")
    comp2 = comparable_calculate(
        target_ebitda=3.0,
        target_revenue=10.0,
        comp_ev_ebitda=[8.0, 10.0, 12.0],
        comp_ev_rev=[1.0, 1.5, 2.0],
        weights=(0.7, 0.3),
        net_debt=2.0,
        shares=1.0,
    )
    assert comp2.ev_rev_low == 10.0   # 10*1.0
    assert comp2.ev_rev_mid == 15.0   # 10*1.5
    assert comp2.ev_rev_high == 20.0  # 10*2.0
    assert comp2.combined_low is not None
    assert comp2.combined_mid is not None
    assert comp2.combined_high is not None
    # 每股价值: (mid - net_debt) / shares
    assert comp2.implied_per_share == (comp2.combined_mid - 2.0), \
        f"implied={comp2.implied_per_share}"
    print(f"  ✓ EV/EBITDA: {comp2.ev_ebitda_mid:.1f}亿, EV/Rev: {comp2.ev_rev_mid:.1f}亿, "
          f"加权: {comp2.combined_mid:.1f}亿, 每股: {comp2.implied_per_share:.2f}元")

    # TEST 7: 综合估值
    print("[TEST 7] 综合估值（DCF + 可比）")
    dcf = dcf_calculate([1.0, 1.2, 1.4], wacc=0.10, terminal_growth=0.02,
                        net_debt=2.0, shares=1.0)
    comp = comparable_calculate(3.0, 10.0, [8.0, 10.0, 12.0],
                                comp_ev_rev=[1.0, 1.5, 2.0],
                                weights=(0.7, 0.3), net_debt=2.0, shares=1.0)
    combined = 综合估值(dcf, comp, dcf_weight=0.5)
    assert "equity_low" in combined
    assert "equity_mid" in combined
    assert "equity_high" in combined
    assert combined["equity_low"] <= combined["equity_mid"] <= combined["equity_high"]
    print(f"  ✓ 估值区间: {combined['equity_low']:.2f} - {combined['equity_high']:.2f}亿, "
          f"中枢: {combined['equity_mid']:.2f}亿")

    # TEST 8: Markdown报告生成
    print("[TEST 8] Markdown报告生成")
    comp3 = comparable_calculate(3.0, 10.0, [8.0, 10.0, 12.0])
    report = format_ma_report(dcf, comp3, net_debt=2.0, shares=1.0,
                              target_name="测试标的", industry="软件")
    assert "# 并购估值分析报告" in report
    assert "DCF估值结果" in report
    assert "敏感性分析" in report
    assert "每股价值" in report
    print(f"  ✓ Markdown报告 {len(report)} 字符")

    # TEST 9: 国有资产备案格式
    print("[TEST 9] 国有资产评估备案格式")
    filing = StateOwnedFiling(
        project_name="XX集团收购XX公司100%股权",
        report_number="国资评估[2024]第001号",
        valuation_date="2024-06-30",
        target_name="XX公司",
        target_industry="软件和信息技术服务业",
        valuation_methods=["DCF法", "可比公司法"],
        dcf_result=dcf,
        comp_result=comp,
        final_equity_value=combined["equity_mid"],
        final_per_share=combined["per_share_mid"],
    )
    filing_md = format_state_owned_filing(filing)
    assert "国有资产评估项目备案表" in filing_md
    assert "DCF估值结果" in filing_md
    assert "最终评估结论" in filing_md
    print(f"  ✓ 备案格式报告 {len(filing_md)} 字符")

    # TEST 10: JSON序列化
    print("[TEST 10] JSON序列化")
    dcf_json = json.dumps(dcf.to_dict(), ensure_ascii=False, indent=2)
    parsed = json.loads(dcf_json)
    assert "enterprise_value" in parsed
    assert "sensitivity" in parsed
    print(f"  ✓ DCF JSON包含 {len(parsed)} 个字段")

    # TEST 11: 零值保护
    print("[TEST 11] 零值保护（shares=0）")
    dcf_zero = dcf_calculate([1.0, 1.2], wacc=0.10, terminal_growth=0.02,
                             net_debt=0.0, shares=0.0)
    assert dcf_zero.per_share == 0.0
    print(f"  ✓ shares=0时 per_share=0（无除零崩溃）")

    # TEST 12: 长预测期
    print("[TEST 12] 长预测期（10年）")
    fcf_long = [1.0 + i * 0.1 for i in range(10)]
    dcf_long = dcf_calculate(fcf_long, wacc=0.10, terminal_growth=0.025,
                             net_debt=5.0, shares=1.0)
    assert dcf_long.enterprise_value > 0
    assert len(dcf_long.sensitivity) == 9
    print(f"  ✓ 10年DCF: EV={dcf_long.enterprise_value:.2f}亿, 每股={dcf_long.per_share:.2f}元")

    # TEST 13: comparable_calculate 权重验证
    print("[TEST 13] 可比公司法权重验证")
    comp_w = comparable_calculate(
        target_ebitda=10.0,
        target_revenue=50.0,
        comp_ev_ebitda=[10.0],  # 仅一个可比公司
        comp_ev_rev=[2.0],
        weights=(0.6, 0.4),
        net_debt=0.0,
        shares=1.0,
    )
    # ev_ebitda_mid = 100, ev_rev_mid = 100
    # combined_mid = 100*0.6 + 100*0.4 = 100
    assert comp_w.combined_mid == 100.0
    print(f"  ✓ 单一可比公司加权: {comp_w.combined_mid:.1f}亿")

    # TEST 14: 国有资产备案JSON
    print("[TEST 14] 国有资产备案JSON输出")
    filing_dict = filing.to_dict()
    assert "dcf_result" in filing_dict
    assert "final_equity_value" in filing_dict
    assert filing_dict["currency"] == "CNY"
    print(f"  ✓ 备案JSON包含 {len(filing_dict)} 个字段")

    print("\n" + "=" * 60)
    print("  ✅ All 14 tests passed!")
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
        description="并购估值计算工具（DCF + 可比公司法 + 国有资产备案格式）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # DCF估值
  %(prog)s dcf --fcf 1.0 1.2 1.4 1.5 1.6 --wacc 0.10 --tg 0.02

  # 可比公司法
  %(prog)s comp --ebitda 3.0 --revenue 10.0 --multiples 8.0 10.0 12.0

  # 综合估值
  %(prog)s full --fcf 1.0 1.2 1.4 1.5 1.6 --wacc 0.10 --tg 0.02 \\
      --ebitda 3.0 --revenue 10.0 --multiples 8.0 10.0 12.0

  # 国有资产评估备案格式
  %(prog)s state-owned --fcf 1.0 1.2 1.4 1.5 1.6 --wacc 0.09 --tg 0.025 \\
      --net-debt 3.0 --shares 1.0 --ebitda 3.0 --revenue 10.0 \\
      --multiples 8.0 10.0 12.0 \\
      --project-name "XX集团收购XX公司100%股权" \\
      --report-number "国资评估[2024]第001号" \\
      --target-name "XX公司"

  # 内置测试
  %(prog)s --test
        """,
    )

    sub = parser.add_subparsers(dest="cmd", title="命令模式")

    # DCF子命令
    p_dcf = sub.add_parser("dcf", help="DCF估值")
    p_dcf.add_argument("--fcf", nargs="+", type=float, required=True,
                       help="预测FCF序列（亿元）")
    p_dcf.add_argument("--wacc", type=float, required=True,
                       help="WACC（小数，如0.10）")
    p_dcf.add_argument("--tg", "--terminal-growth", type=float, required=True,
                       help="永续增长率（小数，如0.02）")
    p_dcf.add_argument("--net-debt", type=float, default=0.0,
                       help="净债务（亿元，默认0）")
    p_dcf.add_argument("--shares", type=float, default=1.0,
                       help="股本（亿股，默认1.0）")
    p_dcf.add_argument("--json", action="store_true", help="JSON格式输出")
    p_dcf.add_argument("--output", "-o", help="输出文件路径")

    # 可比公司法子命令
    p_comp = sub.add_parser("comp", help="可比公司法")
    p_comp.add_argument("--ebitda", type=float, required=True,
                        help="目标EBITDA（亿元）")
    p_comp.add_argument("--revenue", type=float, required=True,
                        help="目标营业收入（亿元）")
    p_comp.add_argument("--multiples", nargs="+", type=float, required=True,
                        help="可比EV/EBITDA倍数列表")
    p_comp.add_argument("--rev-multiples", nargs="+", type=float,
                        help="可比EV/Revenue倍数列表（可选）")
    p_comp.add_argument("--weights", nargs=2, type=float, default=[0.7, 0.3],
                        metavar=("W_EBITDA", "W_REV"),
                        help="EV/EBITDA和EV/Revenue权重（默认0.7 0.3）")
    p_comp.add_argument("--net-debt", type=float, default=0.0)
    p_comp.add_argument("--shares", type=float, default=1.0)
    p_comp.add_argument("--json", action="store_true")
    p_comp.add_argument("--output", "-o", help="输出文件路径")

    # 综合估值子命令
    p_full = sub.add_parser("full", help="综合估值（DCF + 可比公司法）")
    p_full.add_argument("--fcf", nargs="+", type=float, required=True)
    p_full.add_argument("--wacc", type=float, required=True)
    p_full.add_argument("--tg", type=float, required=True)
    p_full.add_argument("--net-debt", type=float, default=0.0)
    p_full.add_argument("--shares", type=float, default=1.0)
    p_full.add_argument("--ebitda", type=float, required=True)
    p_full.add_argument("--revenue", type=float, required=True)
    p_full.add_argument("--multiples", nargs="+", type=float, required=True)
    p_full.add_argument("--rev-multiples", nargs="+", type=float)
    p_full.add_argument("--weights", nargs=2, type=float, default=[0.7, 0.3])
    p_full.add_argument("--target-name", default="目标公司")
    p_full.add_argument("--industry", default="一般")
    p_full.add_argument("--json", action="store_true")
    p_full.add_argument("--output", "-o", help="输出文件路径")

    # 国有资产备案格式
    p_so = sub.add_parser("state-owned", help="国有资产评估备案格式")
    p_so.add_argument("--fcf", nargs="+", type=float, required=True)
    p_so.add_argument("--wacc", type=float, required=True)
    p_so.add_argument("--tg", type=float, required=True)
    p_so.add_argument("--net-debt", type=float, default=0.0)
    p_so.add_argument("--shares", type=float, default=1.0)
    p_so.add_argument("--ebitda", type=float, required=True)
    p_so.add_argument("--revenue", type=float, required=True)
    p_so.add_argument("--multiples", nargs="+", type=float, required=True)
    p_so.add_argument("--rev-multiples", nargs="+", type=float)
    p_so.add_argument("--weights", nargs=2, type=float, default=[0.7, 0.3])
    p_so.add_argument("--project-name", required=True,
                      help="项目名称")
    p_so.add_argument("--report-number", required=True,
                      help="报告编号")
    p_so.add_argument("--target-name", required=True)
    p_so.add_argument("--target-industry", default="一般")
    p_so.add_argument("--valuation-date", default="2024-06-30")
    p_so.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    # 测试模式
    output: str = ""
    is_json = getattr(args, "json", False)

    try:
        if args.cmd == "dcf":
            dcf = dcf_calculate(args.fcf, args.wacc, args.tg,
                                args.net_debt, args.shares)
            if is_json:
                output = json.dumps(dcf.to_dict(), ensure_ascii=False, indent=2)
            else:
                output = (f"DCF估值结果：\n"
                          f"  企业价值(EV) = {dcf.enterprise_value:.2f} 亿元\n"
                          f"  股权价值 = {dcf.equity_value:.2f} 亿元\n"
                          f"  每股价值 = {dcf.per_share:.2f} 元/股\n"
                          f"  WACC = {dcf.wacc:.1%} | 永续增长率 = {dcf.terminal_growth:.2%}\n"
                          f"  敏感性分析（{len(dcf.sensitivity)}个情景）: "
                          f"{min(dcf.sensitivity.values()):.2f} ~ "
                          f"{max(dcf.sensitivity.values()):.2f} 元/股")

        elif args.cmd == "comp":
            rev_mult = getattr(args, "rev_multiples", None)
            weights = tuple(args.weights) if hasattr(args, "weights") else (0.7, 0.3)
            comp = comparable_calculate(
                args.ebitda, args.revenue, args.multiples,
                comp_ev_rev=rev_mult, weights=weights,
                net_debt=args.net_debt, shares=args.shares,
            )
            if is_json:
                output = json.dumps(comp.to_dict(), ensure_ascii=False, indent=2)
            else:
                lines = [
                    "可比公司法估值结果：",
                    f"  EV/EBITDA: {comp.ev_ebitda_low:.2f} ~ {comp.ev_ebitda_high:.2f} 亿元",
                    f"  中值: {comp.ev_ebitda_mid:.2f} 亿元",
                ]
                if comp.ev_rev_mid:
                    lines.append(f"  EV/Revenue: {comp.ev_rev_low:.2f} ~ {comp.ev_rev_high:.2f} 亿元")
                    lines.append(f"  加权综合: {comp.combined_low:.2f} ~ {comp.combined_high:.2f} 亿元")
                if comp.implied_per_share:
                    lines.append(f"  隐含每股价值: {comp.implied_per_share:.2f} 元/股")
                output = "\n".join(lines)

        elif args.cmd == "full":
            dcf = dcf_calculate(args.fcf, args.wacc, args.tg,
                                args.net_debt, args.shares)
            rev_mult = getattr(args, "rev_multiples", None)
            weights = tuple(args.weights) if hasattr(args, "weights") else (0.7, 0.3)
            comp = comparable_calculate(
                args.ebitda, args.revenue, args.multiples,
                comp_ev_rev=rev_mult, weights=weights,
                net_debt=args.net_debt, shares=args.shares,
            )
            if is_json:
                combined = 综合估值(dcf, comp)
                output = json.dumps({
                    "dcf": dcf.to_dict(),
                    "comp": comp.to_dict(),
                    "combined": {k: round(v, 2) for k, v in combined.items()},
                }, ensure_ascii=False, indent=2)
            else:
                output = format_ma_report(
                    dcf, comp, args.net_debt, args.shares,
                    target_name=getattr(args, "target_name", "目标公司"),
                    industry=getattr(args, "industry", "一般"),
                )

        elif args.cmd == "state-owned":
            dcf = dcf_calculate(args.fcf, args.wacc, args.tg,
                                args.net_debt, args.shares)
            rev_mult = getattr(args, "rev_multiples", None)
            weights = tuple(args.weights) if hasattr(args, "weights") else (0.7, 0.3)
            comp = comparable_calculate(
                args.ebitda, args.revenue, args.multiples,
                comp_ev_rev=rev_mult, weights=weights,
                net_debt=args.net_debt, shares=args.shares,
            )
            combined = 综合估值(dcf, comp)
            filing = StateOwnedFiling(
                project_name=args.project_name,
                report_number=args.report_number,
                valuation_date=getattr(args, "valuation_date", "2024-06-30"),
                target_name=args.target_name,
                target_industry=getattr(args, "target_industry", "一般"),
                valuation_methods=["DCF法", "可比公司法"],
                dcf_result=dcf,
                comp_result=comp,
                final_equity_value=combined["equity_mid"],
                final_per_share=combined["per_share_mid"],
            )
            output = format_state_owned_filing(filing)

        else:
            parser.print_help()
            return

        # 输出
        if getattr(args, "output", None):
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 结果已保存至 {args.output}")
        else:
            print(output)

    except ValueError as e:
        print(f"❌ 计算错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未知错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
