# 脚本工具集

ib-execution 配套的 10 个 Python 自动化脚本。所有脚本均通过 `argparse` 提供命令行接口，使用 `--help` 查看详细用法。

## 脚本索引

| 脚本 | 功能 | 适用阶段 | 典型输入 | 输出 |
|------|------|---------|---------|------|
| `ipo_board_check.py` | 检查公司符合哪个IPO板块条件 | 01 项目启动 | 财务数据+行业+专利 | 板块逐项通过/不通过 |
| `dd_checklist_gen.py` | 生成尽调清单 | 02 尽职调查 | 产品类型+行业 | CSV尽调清单 |
| `timeline_gen.py` | 生成项目时间表 | 03 方案设计 | 产品+板块+起止日期 | CSV里程碑表 |
| `financial_ratio_calc.py` | 计算财务比率 | 02/04 尽调/撰写 | 三年一期财务报表 | Markdown分析表 |
| `cross_ref_check.py` | 交叉引用数据一致性检查 | 04/05 撰写/申报 | 多文件数据源 | 差异报告 |
| `doc_version_diff.py` | 文件版本差异对比 | 04/05/06 多阶段 | v1+v2文件 | Markdown对比表 |
| `filing_tracker.py` | 监管申报进度追踪 | 05 监管申报 | 项目名+申报日期 | Dashboard+预警 |
| `bond_product_matcher.py` | 🆕 债券品种智能匹配 | 03 方案设计 | 发行人画像 | 品种排名+评分+排除原因 |
| `bond_pricing_calc.py` | 🆕 债券定价与分析计算器 | 06 发行执行 | 票面利率+期限+YTM | 净价/全价/久期/凸性/现金流 |
| `credit_spread_analyzer.py` | 🆕 信用利差与可比分析 | 06 发行执行 | 可比债券列表+基准利率 | 利差统计+评级分桶+公平YTM |
| `bond_cashflow_cover.py` | 🆕 偿债覆盖率计算器 | 02 尽调/03 方案 | 现金流+债务还本付息 | DSCR逐期表+敏感性分析 |
| `bond_filing_checklist.py` | 🆕 申报文件清单生成器 | 05 监管申报 | 债券品种 | 品种专项文件清单+状态跟踪 |

## 快速使用

```bash
# 板块检查
python scripts/ipo_board_check.py --revenue 1500 --net-profit-3y 180 --market-cap 3000 \
    --r-and-d-pct 6.5 --patents 8 --industry "新一代信息技术" --neeq-months 0

# 尽调清单生成
python scripts/dd_checklist_gen.py --type IPO --board 科创板 --industry "半导体"

# 时间表生成  
python scripts/timeline_gen.py --product IPO --board 科创板 --start 2026-06-01

# 财务比率
python scripts/financial_ratio_calc.py -f financial_data.json

# 交叉检查
python scripts/cross_ref_check.py --prospectus draft.md --audit audit.json --legal legal.json

# 版本对比
python scripts/doc_version_diff.py --old v2.3.md --new v3.1.md

# 申报追踪
python scripts/filing_tracker.py init --project "XX项目" --filing-date 2026-03-15 --board 科创板
python scripts/filing_tracker.py update --project "XX项目" --stage acceptance --date 2026-03-18
python scripts/filing_tracker.py status --project "XX项目"
```

## 债券脚本

```bash
# 品种匹配：帮发行人找最合适的债券品种
python scripts/bond_product_matcher.py --type LGFV --rating AA+ --industry infrastructure \
    --asset-size 200 --revenue 30 --net-profit 5 --debt-ratio 60 \
    --amount 15 --tenor 5 --purpose project
python scripts/bond_product_matcher.py --json --type private --rating AA --amount 5 --tenor 1 --purpose general
python scripts/bond_product_matcher.py --test  # 内置3个测试用例

# 债券定价：计算净价/全价/久期/凸性
python scripts/bond_pricing_calc.py --coupon 3.8 --ytm 4.1 --maturity 5 --frequency 1
python scripts/bond_pricing_calc.py --coupon 4.2 --ytm 3.9 --maturity 3 --frequency 2 --settlement-days 45
python scripts/bond_pricing_calc.py --json --coupon 3.5 --ytm 3.8 --maturity 5

# 信用利差分析：可比债券筛选与定价参考
python scripts/credit_spread_analyzer.py --test  # 内置10支可比债券数据
python scripts/credit_spread_analyzer.py --file comps.json --benchmark 2.85 --target-rating AA+
python scripts/credit_spread_analyzer.py --json --file comps.json --benchmark 2.85 --benchmark-label "CGB 3Y"

# 偿债覆盖率：DSCR计算+还款计划+敏感性分析
python scripts/bond_cashflow_cover.py --amount 10e8 --coupon 4.2 --tenor 5 --type bullet \
    --cashflows 2.5e8,2.8e8,3.0e8,3.2e8,3.5e8 \
    --existing 1.8e8,1.5e8,1.2e8,1.0e8,8e7
python scripts/bond_cashflow_cover.py --file cashflow_input.json --cash-balance 5e7
python scripts/bond_cashflow_cover.py --test  # 3个内置测试（amortizing/bullet/sinking紧平衡）

# 申报文件清单：按品种生成监管要求的文件清单
python scripts/bond_filing_checklist.py --product MTN
python scripts/bond_filing_checklist.py --product 企业债 --output json
python scripts/bond_filing_checklist.py --product ABS --status existing_files.csv
python scripts/bond_filing_checklist.py --test  # 3个内置测试（MTN/企业债/ABS）
```

## 依赖

所有脚本仅依赖 Python 3.8+ 标准库（`argparse`, `json`, `csv`, `datetime`, `dataclasses`, `difflib`, `statistics`）。无需额外安装。