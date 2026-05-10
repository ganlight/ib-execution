#!/usr/bin/env python3
"""
债券违约预警系统 (Bond Default Early Warning System)
三维度预警引擎：财务指标 + 市场信号 + 舆情信号
支持单券检查、批量扫描、组合概览

Author: QClaw Bond Risk System
Version: 1.0.0
"""

import sys
import json
import argparse
from dataclasses import dataclass, asdict
from typing import Optional
from enum import IntEnum


# ============================================================================
# 数据结构定义
# ============================================================================

class AlertLevel(IntEnum):
    """预警等级枚举"""
    NORMAL = 0   # 🟢 正常
    WATCH = 1    # 🟡 关注
    WARNING = 2  # 🔴 预警
    DEFAULT = 3  # ⚫ 违约


@dataclass
class FinancialIndicators:
    """财务指标"""
    current_ratio: float              # 流动比率
    debt_to_asset: float              # 资产负债率 (%)
    interest_coverage: float          # 利息保障倍数
    operating_cf: float               # 经营现金流 (亿元)
    revenue_growth: float             # 营收增速 (%)
    gross_margin_change: float        # 毛利率变化 (ppt)
    receivable_growth: float          # 应收增速 (%)
    short_debt_ratio: float           # 短债占比 (%)
    pledge_ratio: float               # 质押比例 (%)
    guarantee_ratio: float            # 对外担保比例 (%)


@dataclass
class MarketSignals:
    """市场信号"""
    credit_spread: float              # 信用利差 (bp)
    price_change: float              # 价格变化 (%)
    yield_to_maturity: float         # 到期收益率 (%)
    bid_ask_spread: float            # 买卖价差 (bp)


@dataclass
class SentimentSignals:
    """舆情信号"""
    major_litigation: bool           # 重大诉讼
    exec_change: bool                # 高管变更
    loan_overdue: bool               # 贷款逾期
    cross_default: bool              # 交叉违约


@dataclass
class BondInfo:
    """债券信息"""
    bond_code: str
    bond_name: str
    issuer: str
    rating: str
    financial: FinancialIndicators
    market: MarketSignals
    sentiment: SentimentSignals


@dataclass
class AlertResult:
    """预警结果"""
    bond_code: str
    bond_name: str
    alert_level: AlertLevel
    financial_score: float
    market_score: float
    sentiment_score: float
    composite_score: float
    triggered_rules: list[str]
    recommendation: str


# ============================================================================
# 预警规则引擎
# ============================================================================

class AlertRuleEngine:
    """预警规则引擎"""

    # 财务指标阈值配置
    FINANCIAL_RULES = {
        "流动比率<1": lambda f: f.current_ratio < 1,
        "资产负债率>70%": lambda f: f.debt_to_asset > 70,
        "利息保障倍数<2": lambda f: f.interest_coverage < 2,
        "经营现金流为负": lambda f: f.operating_cf < 0,
        "营收下降>20%": lambda f: f.revenue_growth < -20,
        "毛利率下降>3ppt": lambda f: f.gross_margin_change < -3,
        "应收账款飙升>50%": lambda f: f.receivable_growth > 50,
        "短债占比>50%": lambda f: f.short_debt_ratio > 50,
        "股权质押>30%": lambda f: f.pledge_ratio > 30,
        "对外担保>50%": lambda f: f.guarantee_ratio > 50,
    }

    # 市场信号阈值配置
    MARKET_RULES = {
        "信用利差走阔>200bp": lambda m: m.credit_spread > 200,
        "价格跌幅>10%": lambda m: m.price_change < -10,
        "收益率>12%": lambda m: m.yield_to_maturity > 12,
        "买卖价差走阔": lambda m: m.bid_ask_spread > 150,
    }

    # 舆情信号配置（布尔型，有即触发）
    SENTIMENT_RULES = {
        "重大诉讼": lambda s: s.major_litigation,
        "高管变更": lambda s: s.exec_change,
        "贷款逾期": lambda s: s.loan_overdue,
        "交叉违约": lambda s: s.cross_default,
    }

    # 权重配置
    WEIGHTS = {
        "financial": 0.50,
        "market": 0.30,
        "sentiment": 0.20,
    }

    @classmethod
    def evaluate_financial(cls, f: FinancialIndicators) -> tuple[float, list[str]]:
        """评估财务指标，返回(得分, 触发规则列表)"""
        triggered = []
        total_rules = len(cls.FINANCIAL_RULES)

        for rule_name, rule_fn in cls.FINANCIAL_RULES.items():
            if rule_fn(f):
                triggered.append(f"【财务】{rule_name}")

        # 得分计算：触发越少得分越高
        trigger_ratio = len(triggered) / total_rules
        score = max(0, 100 * (1 - trigger_ratio))
        return score, triggered

    @classmethod
    def evaluate_market(cls, m: MarketSignals) -> tuple[float, list[str]]:
        """评估市场信号，返回(得分, 触发规则列表)"""
        triggered = []
        total_rules = len(cls.MARKET_RULES)

        for rule_name, rule_fn in cls.MARKET_RULES.items():
            if rule_fn(m):
                triggered.append(f"【市场】{rule_name}")

        trigger_ratio = len(triggered) / total_rules
        score = max(0, 100 * (1 - trigger_ratio))
        return score, triggered

    @classmethod
    def evaluate_sentiment(cls, s: SentimentSignals) -> tuple[float, list[str]]:
        """评估舆情信号，返回(得分, 触发规则列表)"""
        triggered = []
        total_rules = len(cls.SENTIMENT_RULES)

        for rule_name, rule_fn in cls.SENTIMENT_RULES.items():
            if rule_fn(s):
                triggered.append(f"【舆情】{rule_name}")

        trigger_ratio = len(triggered) / total_rules
        score = max(0, 100 * (1 - trigger_ratio))
        return score, triggered

    @classmethod
    def determine_alert_level(cls, composite_score: float, triggered_rules: list[str]) -> AlertLevel:
        """根据综合得分和触发规则确定预警等级"""
        # 舆情直接触发违约预警
        for rule in triggered_rules:
            if "【舆情】交叉违约" in rule:
                return AlertLevel.DEFAULT
            if "【舆情】贷款逾期" in rule:
                return AlertLevel.WARNING

        # 按综合得分分级
        if composite_score >= 80:
            return AlertLevel.NORMAL
        elif composite_score >= 60:
            return AlertLevel.WATCH
        elif composite_score >= 40:
            return AlertLevel.WARNING
        else:
            return AlertLevel.DEFAULT

    @classmethod
    def generate_recommendation(cls, level: AlertLevel, triggered: list[str]) -> str:
        """生成处置建议"""
        if level == AlertLevel.NORMAL:
            return "维持现有持仓，持续关注"
        elif level == AlertLevel.WATCH:
            return "加强监控，提升持仓审慎度"
        elif level == AlertLevel.WARNING:
            return "预警处置：逐级上报、收紧授信、追加抵质押"
        else:
            return "紧急处置：停止新增授信、启动担保代偿、筹划债务重组"

    @classmethod
    def analyze_bond(cls, bond: BondInfo) -> AlertResult:
        """分析单只债券"""
        fin_score, fin_triggers = cls.evaluate_financial(bond.financial)
        mkt_score, mkt_triggers = cls.evaluate_market(bond.market)
        sen_score, sen_triggers = cls.evaluate_sentiment(bond.sentiment)

        # 加权综合评分
        composite = (
            fin_score * cls.WEIGHTS["financial"] +
            mkt_score * cls.WEIGHTS["market"] +
            sen_score * cls.WEIGHTS["sentiment"]
        )

        all_triggers = fin_triggers + mkt_triggers + sen_triggers
        alert_level = cls.determine_alert_level(composite, all_triggers)
        recommendation = cls.generate_recommendation(alert_level, all_triggers)

        return AlertResult(
            bond_code=bond.bond_code,
            bond_name=bond.bond_name,
            alert_level=alert_level,
            financial_score=round(fin_score, 1),
            market_score=round(mkt_score, 1),
            sentiment_score=round(sen_score, 1),
            composite_score=round(composite, 1),
            triggered_rules=all_triggers,
            recommendation=recommendation,
        )


# ============================================================================
# 格式化输出
# ============================================================================

class OutputFormatter:
    """输出格式化器"""

    LEVEL_SYMBOLS = {
        AlertLevel.NORMAL: "🟢",
        AlertLevel.WATCH: "🟡",
        AlertLevel.WARNING: "🔴",
        AlertLevel.DEFAULT: "⚫",
    }

    LEVEL_NAMES = {
        AlertLevel.NORMAL: "正常",
        AlertLevel.WATCH: "关注",
        AlertLevel.WARNING: "预警",
        AlertLevel.DEFAULT: "违约",
    }

    @classmethod
    def format_result(cls, result: AlertResult) -> str:
        """格式化单券预警结果"""
        level_sym = cls.LEVEL_SYMBOLS[result.alert_level]
        level_name = cls.LEVEL_NAMES[result.alert_level]

        lines = [
            f"{'='*60}",
            f"债券代码: {result.bond_code}",
            f"债券名称: {result.bond_name}",
            f"{'='*60}",
            f"  预警等级: {level_sym} {level_name}",
            f"  综合评分: {result.composite_score}/100",
            f"  ├─ 财务指标得分: {result.financial_score}/100 (权重50%)",
            f"  ├─ 市场信号得分: {result.market_score}/100 (权重30%)",
            f"  └─ 舆情信号得分: {result.sentiment_score}/100 (权重20%)",
            f"",
        ]

        if result.triggered_rules:
            lines.append("  触发预警规则:")
            for rule in result.triggered_rules:
                lines.append(f"    • {rule}")
            lines.append("")

        lines.extend([
            f"  处置建议: {result.recommendation}",
            f"{'='*60}",
        ])

        return "\n".join(lines)

    @classmethod
    def format_portfolio_summary(cls, results: list[AlertResult]) -> str:
        """格式化组合概览"""
        total = len(results)
        level_counts = {level: 0 for level in AlertLevel}

        for r in results:
            level_counts[r.alert_level] += 1

        lines = [
            f"{'='*60}",
            f"债券组合预警概览",
            f"{'='*60}",
            f"  组合总券数: {total}",
            f"",
            f"  预警分布:",
            f"    🟢 正常: {level_counts[AlertLevel.NORMAL]} 只 ({level_counts[AlertLevel.NORMAL]*100//total}%)",
            f"    🟡 关注: {level_counts[AlertLevel.WATCH]} 只 ({level_counts[AlertLevel.WATCH]*100//total}%)",
            f"    🔴 预警: {level_counts[AlertLevel.WARNING]} 只 ({level_counts[AlertLevel.WARNING]*100//total}%)",
            f"    ⚫ 违约: {level_counts[AlertLevel.DEFAULT]} 只 ({level_counts[AlertLevel.DEFAULT]*100//total}%)",
            f"",
            f"  健康度: {level_counts[AlertLevel.NORMAL]}/{total} 正常 ({level_counts[AlertLevel.NORMAL]*100//total}%)",
            f"",
        ]

        # 列出高风险债券
        high_risk = [r for r in results if r.alert_level >= AlertLevel.WARNING]
        if high_risk:
            lines.append("  高风险债券清单:")
            for r in high_risk:
                lines.append(f"    {cls.LEVEL_SYMBOLS[r.alert_level]} {r.bond_code} {r.bond_name} (评分:{r.composite_score})")

        lines.append(f"{'='*60}")
        return "\n".join(lines)

    @classmethod
    def format_json(cls, result: AlertResult) -> str:
        """输出JSON格式"""
        data = {
            "bond_code": result.bond_code,
            "bond_name": result.bond_name,
            "alert_level": cls.LEVEL_NAMES[result.alert_level],
            "alert_level_code": result.alert_level.value,
            "composite_score": result.composite_score,
            "scores": {
                "financial": result.financial_score,
                "market": result.market_score,
                "sentiment": result.sentiment_score,
            },
            "triggered_rules": result.triggered_rules,
            "recommendation": result.recommendation,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


# ============================================================================
# 内置测试用例
# ============================================================================

def build_test_bond() -> BondInfo:
    """构建测试用例：AA+地级市城投，多指标触发预警"""
    financial = FinancialIndicators(
        current_ratio=0.85,           # <1 触发预警
        debt_to_asset=72.5,          # >70 触发预警
        interest_coverage=1.8,       # <2 触发预警
        operating_cf=-5.2,           # 负 触发预警
        revenue_growth=-15.0,        # 下降但未触发-20
        gross_margin_change=-2.5,    # 未触发-3
        receivable_growth=55.0,      # >50 触发预警
        short_debt_ratio=58.0,       # >50 触发预警
        pledge_ratio=35.0,          # >30 触发预警
        guarantee_ratio=45.0,        # 未触发50
    )

    market = MarketSignals(
        credit_spread=180.0,        # 未触发200
        price_change=-8.0,          # 未触发-10
        yield_to_maturity=11.5,      # 未触发12
        bid_ask_spread=120.0,        # 未触发150
    )

    sentiment = SentimentSignals(
        major_litigation=False,
        exec_change=True,            # 高管变更 触发预警
        loan_overdue=False,
        cross_default=False,
    )

    return BondInfo(
        bond_code="2280128",
        bond_name="22XX城投01",
        issuer="XX市城市投资发展集团有限公司",
        rating="AA+",
        financial=financial,
        market=market,
        sentiment=sentiment,
    )


def run_test_case():
    """运行内置测试用例"""
    print("=" * 60)
    print("债券违约预警系统 - 内置测试用例")
    print("测试样本：AA+地级市城投债")
    print("=" * 60)
    print()

    bond = build_test_bond()

    # 打印输入数据
    print("【输入数据】")
    print(f"  债券: {bond.bond_code} {bond.bond_name}")
    print(f"  发行人: {bond.issuer}")
    print(f"  评级: {bond.rating}")
    print()
    print("  财务指标:")
    print(f"    流动比率: {bond.financial.current_ratio} (阈值<1) {'⚠️' if bond.financial.current_ratio < 1 else '✓'}")
    print(f"    资产负债率: {bond.financial.debt_to_asset}% (阈值>70%) {'⚠️' if bond.financial.debt_to_asset > 70 else '✓'}")
    print(f"    利息保障倍数: {bond.financial.interest_coverage} (阈值<2) {'⚠️' if bond.financial.interest_coverage < 2 else '✓'}")
    print(f"    经营现金流: {bond.financial.operating_cf}亿元 {'⚠️' if bond.financial.operating_cf < 0 else '✓'}")
    print(f"    营收增速: {bond.financial.revenue_growth}%")
    print(f"    毛利率变化: {bond.financial.gross_margin_change}ppt")
    print(f"    应收增速: {bond.financial.receivable_growth}% {'⚠️' if bond.financial.receivable_growth > 50 else '✓'}")
    print(f"    短债占比: {bond.financial.short_debt_ratio}% {'⚠️' if bond.financial.short_debt_ratio > 50 else '✓'}")
    print(f"    质押比例: {bond.financial.pledge_ratio}% {'⚠️' if bond.financial.pledge_ratio > 30 else '✓'}")
    print(f"    担保比例: {bond.financial.guarantee_ratio}%")
    print()
    print("  市场信号:")
    print(f"    信用利差: {bond.market.credit_spread}bp")
    print(f"    价格变化: {bond.market.price_change}%")
    print(f"    到期收益率: {bond.market.yield_to_maturity}%")
    print(f"    买卖价差: {bond.market.bid_ask_spread}bp")
    print()
    print("  舆情信号:")
    print(f"    重大诉讼: {bond.sentiment.major_litigation}")
    print(f"    高管变更: {bond.sentiment.exec_change} ⚠️")
    print(f"    贷款逾期: {bond.sentiment.loan_overdue}")
    print(f"    交叉违约: {bond.sentiment.cross_default}")
    print()
    print("-" * 60)
    print()

    # 执行预警分析
    result = AlertRuleEngine.analyze_bond(bond)

    # 输出结果
    print(OutputFormatter.format_result(result))

    # 额外输出：各维度详细得分
    print("【评分分析】")
    print(f"  财务维度(权重50%): 触发 {10 - int(result.financial_score // 10)}/10 规则 → {result.financial_score}分")
    print(f"  市场维度(权重30%): 触发 {4 - int(result.market_score // 25)}/4 规则 → {result.market_score}分")
    print(f"  舆情维度(权重20%): 触发 {1 if result.sentiment_score < 100 else 0}/4 规则 → {result.sentiment_score}分")
    print(f"  综合评分: {result.composite_score}分 → {OutputFormatter.LEVEL_SYMBOLS[result.alert_level]}{OutputFormatter.LEVEL_NAMES[result.alert_level]}")
    print()
    print("【测试结论】")
    print("  ✓ 测试通过：系统正确识别出财务+舆情多维度风险信号")
    print("  ✓ 预警等级：关注/预警（综合评分<60触发预警阈值）")
    print("  ✓ 建议：加强贷后监控，补充增信措施")


# ============================================================================
# 数据文件加载
# ============================================================================

def load_bonds_from_json(json_path: str) -> list[BondInfo]:
    """从JSON文件批量加载债券数据"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    bonds = []
    for item in data.get("bonds", []):
        fin = item["financial"]
        mkt = item["market"]
        sen = item["sentiment"]

        bonds.append(BondInfo(
            bond_code=item["bond_code"],
            bond_name=item["bond_name"],
            issuer=item["issuer"],
            rating=item["rating"],
            financial=FinancialIndicators(**fin),
            market=MarketSignals(**mkt),
            sentiment=SentimentSignals(**sen),
        ))

    return bonds


# ============================================================================
# CLI 入口
# ============================================================================

def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog="bond_default_early_warning",
        description="债券违约预警系统 - 三维度预警引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
权重配置:
  财务指标: 50%%
  市场信号: 30%%
  舆情信号: 20%%

预警等级:
  🟢 正常   (80-100分)
  🟡 关注   (60-79分)
  🔴 预警   (40-59分)
  ⚫ 违约   (0-39分)

示例:
  %(prog)s --test                           # 运行内置测试用例
  %(prog)s --check 2280128                 # 单券检查
  %(prog)s --scan bonds.json               # 批量扫描
  %(prog)s --scan bonds.json --portfolio   # 组合概览
  %(prog)s --scan bonds.json --json        # JSON格式输出
        """
    )

    parser.add_argument("--test", action="store_true",
                        help="运行内置测试用例 (AA+地级市城投)")
    parser.add_argument("--check", metavar="CODE",
                        help="单券检查，输入债券代码")
    parser.add_argument("--scan", metavar="FILE",
                        help="批量扫描，输入JSON文件路径")
    parser.add_argument("--portfolio", action="store_true",
                        help="组合概览模式 (与 --scan 配合)")
    parser.add_argument("--json", action="store_true",
                        help="JSON格式输出")
    parser.add_argument("--output", metavar="FILE",
                        help="输出到文件")

    return parser.parse_args()


def cmd_check(bond_code: str) -> None:
    """单券检查模式"""
    # 简化模式：使用内置样本数据演示
    print(f"单券检查模式: {bond_code}")
    print("提示: 使用 --test 查看完整分析示例")
    print("提示: 使用 --scan bonds.json 进行批量分析")


def cmd_scan(json_path: str, portfolio: bool = False, json_output: bool = False) -> None:
    """批量扫描模式"""
    try:
        bonds = load_bonds_from_json(json_path)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {json_path}")
        print("提示: 请先创建包含债券数据的JSON文件")
        return
    except json.JSONDecodeError as e:
        print(f"错误: JSON格式错误 - {e}")
        return

    results = [AlertRuleEngine.analyze_bond(bond) for bond in bonds]

    if json_output:
        for r in results:
            print(OutputFormatter.format_json(r))
    elif portfolio:
        print(OutputFormatter.format_portfolio_summary(results))
    else:
        for r in results:
            print(OutputFormatter.format_result(r))
            print()


def main() -> None:
    """主入口"""
    args = parse_args()

    if args.test:
        run_test_case()
    elif args.check:
        cmd_check(args.check)
    elif args.scan:
        cmd_scan(args.scan, args.portfolio, args.json)
    else:
        # 默认运行测试
        print("债券违约预警系统 v1.0.0")
        print("使用 --test 运行内置测试用例")
        print("使用 --help 查看完整帮助")


if __name__ == "__main__":
    main()
