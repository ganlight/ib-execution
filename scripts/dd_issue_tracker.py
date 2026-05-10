#!/usr/bin/env python3
"""
尽调问题追踪工具（DD Issue Tracker）
用于管理投行尽调过程中的问题清单，支持RED/AMBER/GREEN三级分类。

用法示例：
    python dd_issue_tracker.py init --project "XXIPO项目" --output issues.json
    python dd_issue_tracker.py add --file issues.json --title "应收账款账龄偏长" \
        --category 财务 --severity AMBER --reporter "张三" --target-fix 2026-03-31
    python dd_issue_tracker.py list --file issues.json
    python dd_issue_tracker.py list --file issues.json --severity RED
    python dd_issue_tracker.py update --file issues.json --id ISS-2026-0001 --status Resolved
    python dd_issue_tracker.py summary --file issues.json
    python dd_issue_tracker.py export --file issues.json --format markdown --output issues_report.md
    python dd_issue_tracker.py --test
"""

import argparse
import csv
import datetime
import json
import os
import sys
import textwrap
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

@dataclass
class DDIssue:
    """单条尽调问题数据模型"""
    id: str = ""                     # 自动生成：ISS-YYYY-NNNN
    title: str = ""                  # 问题标题
    category: str = ""              # 法律/财务/业务/合规/其他
    severity: str = ""              # RED/AMBER/GREEN
    status: str = ""                 # Open/InProgress/Resolved/Closed/Waived
    reporter: str = ""               # 发现人
    date_found: str = ""             # YYYY-MM-DD
    target_fix: str = ""             # 计划解决日期
    description: str = ""           # 问题描述
    impact: str = ""                # 对项目的影响
    recommendation: str = ""        # 建议处理方式
    resolution: str = ""            # 解决方案（完成后填写）
    date_resolved: str = ""         # 实际解决日期
    evidence_files: List[str] = field(default_factory=list)   # 支持性文件列表
    related_issues: List[str] = field(default_factory=list)   # 关联问题

    VALID_CATEGORIES = {"法律", "财务", "业务", "合规", "其他"}
    VALID_SEVERITIES = {"RED", "AMBER", "GREEN"}
    VALID_STATUSES = {"Open", "InProgress", "Resolved", "Closed", "Waived"}

    def validate(self) -> List[str]:
        errors = []
        if not self.title.strip():
            errors.append("问题标题不能为空")
        if self.category not in self.VALID_CATEGORIES:
            errors.append(f"类别必须是以下之一：{','.join(self.VALID_CATEGORIES)}")
        if self.severity not in self.VALID_SEVERITIES:
            errors.append(f"严重程度必须是：{','.join(self.VALID_SEVERITIES)}")
        if self.status not in self.VALID_STATUSES:
            errors.append(f"状态必须是：{','.join(self.VALID_STATUSES)}")
        return errors


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

@dataclass
class DDProject:
    project: str = ""
    created: str = ""
    issues: List[DDIssue] = field(default_factory=list)


def _now() -> str:
    return datetime.date.today().isoformat()


def _issue_counter(issues: List[DDIssue], year: str) -> int:
    """计算当年已分配的最大序号"""
    max_n = 0
    for iss in issues:
        if iss.id.startswith(f"ISS-{year}-"):
            try:
                n = int(iss.id.split("-")[-1])
                if n > max_n:
                    max_n = n
            except ValueError:
                pass
    return max_n


def load_project(path: str) -> DDProject:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    issues = [DDIssue(**item) for item in raw.get("issues", [])]
    return DDProject(project=raw.get("project", ""), created=raw.get("created", ""), issues=issues)


def save_project(project: DDProject, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "project": project.project,
            "created": project.created,
            "issues": [asdict(iss) for iss in project.issues]
        }, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args) -> int:
    if os.path.exists(args.output) and not args.force:
        print(f"错误：文件已存在，请使用 --force 覆盖：{args.output}", file=sys.stderr)
        return 1

    project = DDProject(project=args.project, created=_now(), issues=[])
    save_project(project, args.output)
    print(f"✓ 项目已初始化：{args.project}")
    print(f"  输出文件：{args.output}")
    print(f"  创建日期：{project.created}")
    return 0


def cmd_add(args) -> int:
    project = load_project(args.file)
    year = _now()[:4]
    next_n = _issue_counter(project.issues, year) + 1
    issue_id = f"ISS-{year}-{next_n:04d}"

    issue = DDIssue(
        id=issue_id,
        title=args.title,
        category=args.category,
        severity=args.severity,
        status="Open",
        reporter=args.reporter,
        date_found=_now(),
        target_fix=args.target_fix or "",
        description=args.description or "",
        impact=args.impact or "",
        recommendation=args.recommendation or "",
        resolution="",
        date_resolved="",
        evidence_files=[],
        related_issues=[]
    )

    errors = issue.validate()
    if errors:
        for e in errors:
            print(f"✗ 验证失败：{e}", file=sys.stderr)
        return 1

    project.issues.append(issue)
    save_project(project, args.file)
    print(f"✓ 已添加问题 [{issue_id}]：{issue.title}")
    print(f"  严重程度：{issue.severity} | 类别：{issue.category}")
    return 0


def cmd_list(args) -> int:
    project = load_project(args.file)

    severity_filter = args.severity.upper() if args.severity else None
    status_filter = args.status.capitalize() if args.status else None

    filtered = project.issues
    if severity_filter:
        filtered = [i for i in filtered if i.severity == severity_filter]
    if status_filter:
        filtered = [i for i in filtered if i.status == status_filter]

    if not filtered:
        print(f"（无匹配问题）")
        return 0

    # 彩色输出（基于ANSI）
    sev_color = {"RED": "\033[91m", "AMBER": "\033[93m", "GREEN": "\033[92m"}
    reset = "\033[0m"

    header = (f"{'ID':<18} {'严重':<6} {'类别':<6} {'状态':<12} "
              f"{'发现日期':<12} {'计划解决':<12} {'问题标题'}")
    sep = "─" * 110
    print(f"\n{'='*30} {project.project} {'='*30}")
    print(header)
    print(sep)

    for iss in filtered:
        color = sev_color.get(iss.severity, "")
        title = iss.title[:45] + ("…" if len(iss.title) > 45 else "")
        print(
            f"{color}{iss.id:<18}{reset} "
            f"{iss.severity:<6} {iss.category:<6} "
            f"{iss.status:<12} {iss.date_found:<12} "
            f"{iss.target_fix:<12} {title}"
        )
    print(f"\n共 {len(filtered)} 条记录（总问题数：{len(project.issues)}）")
    return 0


def cmd_update(args) -> int:
    project = load_project(args.file)

    found = None
    for iss in project.issues:
        if iss.id == args.id:
            found = iss
            break

    if not found:
        print(f"错误：未找到问题ID：{args.id}", file=sys.stderr)
        return 1

    changes = []
    if args.status:
        found.status = args.status.capitalize()
        changes.append(f"状态 → {found.status}")
    if args.severity:
        found.severity = args.severity.upper()
        changes.append(f"严重程度 → {found.severity}")
    if args.title:
        found.title = args.title
        changes.append(f"标题 → {found.title}")
    if args.category:
        found.category = args.category
        changes.append(f"类别 → {found.category}")
    if args.resolution:
        found.resolution = args.resolution
        changes.append("解决方案已更新")
        found.date_resolved = _now()
        found.status = "Resolved"
        changes.append(f"状态 → Resolved（{found.date_resolved}）")
    if args.related_issue:
        issues_list = [i.strip() for i in args.related_issue.split(",")]
        for rid in issues_list:
            if rid not in found.related_issues:
                found.related_issues.append(rid)
        changes.append(f"关联问题 → {', '.join(found.related_issues)}")
    if args.evidence_file:
        files_list = [f.strip() for f in args.evidence_file.split(",")]
        for fn in files_list:
            if fn not in found.evidence_files:
                found.evidence_files.append(fn)
        changes.append(f"支持文件 → {', '.join(found.evidence_files)}")

    if not changes:
        print("提示：未指定任何更新内容（请使用 --status/--severity/--title 等参数）")
        return 0

    save_project(project, args.file)
    print(f"✓ 已更新 [{found.id}]：{' | '.join(changes)}")
    return 0


def cmd_summary(args) -> int:
    project = load_project(args.file)
    issues = project.issues

    if not issues:
        print(f"（项目「{project.project}」暂无问题记录）")
        return 0

    total = len(issues)

    # 按严重程度统计
    red = [i for i in issues if i.severity == "RED"]
    amber = [i for i in issues if i.severity == "AMBER"]
    green = [i for i in issues if i.severity == "GREEN"]

    # 按状态统计
    status_counts = {}
    for iss in issues:
        status_counts[iss.status] = status_counts.get(iss.status, 0) + 1

    # 按类别统计
    cat_counts = {}
    for iss in issues:
        cat_counts[iss.category] = cat_counts.get(iss.category, 0) + 1

    width = 60
    print(f"\n{'='*width}")
    print(f"  {project.project} 尽调问题追踪")
    print(f"{'='*width}")
    print(f"  项目创建日期：{project.created}    问题总数：{total}")
    print(f"{'─'*width}")
    print(f"  【严重程度分布】")
    print(f"    🔴 RED   ：{len(red):>3}  ({len(red)*100//max(total,1)}%)")
    print(f"    🟡 AMBER ：{len(amber):>3}  ({len(amber)*100//max(total,1)}%)")
    print(f"    🟢 GREEN ：{len(green):>3}  ({len(green)*100//max(total,1)}%)")
    print(f"{'─'*width}")
    print(f"  【状态分布】")
    for st, cnt in sorted(status_counts.items()):
        bar = "█" * (cnt * 20 // max(total, 1))
        print(f"    {st:<12} {cnt:>3}  {bar}")
    print(f"{'─'*width}")
    print(f"  【类别分布】")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat:<8} {cnt:>3}")
    print(f"{'─'*width}")

    if red:
        print(f"  【🔴 RED级问题（需优先处理）】")
        for iss in red:
            print(f"    {iss.id}  {iss.title}")
            print(f"             类别：{iss.category} | 状态：{iss.status} | 责任人：{iss.reporter}")
            if iss.target_fix:
                print(f"             计划解决：{iss.target_fix}")
            if iss.impact:
                print(f"             影响：{iss.impact}")
        print()

    # 未解决问题提示
    open_count = status_counts.get("Open", 0) + status_counts.get("InProgress", 0)
    if open_count > 0:
        print(f"  ⚠  仍有 {open_count} 个问题待解决，请尽快推进。")
    return 0


def cmd_export(args) -> int:
    project = load_project(args.file)
    issues = project.issues

    if not issues:
        print("（无问题可导出）")
        return 0

    if args.format == "markdown":
        lines = []
        lines.append(f"# {project.project} 尽调问题追踪报告\n")
        lines.append(f"**项目创建日期**：{project.created}  |  **导出日期**：{_now()}  |  **问题总数**：{len(issues)}\n")

        # 统计摘要
        red = len([i for i in issues if i.severity == "RED"])
        amber = len([i for i in issues if i.severity == "AMBER"])
        green = len([i for i in issues if i.severity == "GREEN"])
        status_map = {}
        for iss in issues:
            status_map[iss.status] = status_map.get(iss.status, 0) + 1

        lines.append("## 统计摘要\n")
        lines.append(f"| 严重程度 | 数量 |")
        lines.append(f"|----------|------|")
        lines.append(f"| 🔴 RED   | {red} |")
        lines.append(f"| 🟡 AMBER | {amber} |")
        lines.append(f"| 🟢 GREEN | {green} |\n")
        lines.append(f"| 状态 | 数量 |")
        lines.append(f"|------|------|")
        for st, cnt in sorted(status_map.items()):
            lines.append(f"| {st} | {cnt} |")
        lines.append("")

        # 按严重程度分组
        for sev in ["RED", "AMBER", "GREEN"]:
            group = [i for i in issues if i.severity == sev]
            if not group:
                continue
            emoji = {"RED": "🔴", "AMBER": "🟡", "GREEN": "🟢"}[sev]
            lines.append(f"## {emoji} {sev} 级问题\n")
            for iss in group:
                lines.append(f"### {iss.id}：{iss.title}\n")
                fields = [
                    ("状态", iss.status),
                    ("类别", iss.category),
                    ("发现人", iss.reporter),
                    ("发现日期", iss.date_found),
                    ("计划解决", iss.target_fix),
                    ("实际解决", iss.date_resolved),
                ]
                for k, v in fields:
                    if v:
                        lines.append(f"- **{k}**：{v}")
                if iss.description:
                    lines.append(f"- **问题描述**：{iss.description}")
                if iss.impact:
                    lines.append(f"- **影响**：{iss.impact}")
                if iss.recommendation:
                    lines.append(f"- **建议处理方式**：{iss.recommendation}")
                if iss.resolution:
                    lines.append(f"- **解决方案**：{iss.resolution}")
                if iss.evidence_files:
                    lines.append(f"- **支持文件**：{', '.join(iss.evidence_files)}")
                if iss.related_issues:
                    lines.append(f"- **关联问题**：{', '.join(iss.related_issues)}")
                lines.append("")
            lines.append("---\n")

        content = "\n".join(lines)

    elif args.format == "csv":
        import io as sio
        output = sio.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "问题标题", "类别", "严重程度", "状态",
            "发现人", "发现日期", "计划解决日期", "实际解决日期",
            "问题描述", "影响", "建议处理方式", "解决方案",
            "支持文件", "关联问题"
        ])
        for iss in issues:
            writer.writerow([
                iss.id, iss.title, iss.category, iss.severity, iss.status,
                iss.reporter, iss.date_found, iss.target_fix, iss.date_resolved,
                iss.description, iss.impact, iss.recommendation, iss.resolution,
                "|".join(iss.evidence_files), "|".join(iss.related_issues)
            ])
        content = output.getvalue()

    else:
        print(f"错误：不支持的格式：{args.format}（支持：markdown, csv）", file=sys.stderr)
        return 1

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ 已导出 {len(issues)} 条记录 → {args.output}（格式：{args.format}）")
    return 0


# ---------------------------------------------------------------------------
# Built-in Test
# ---------------------------------------------------------------------------

def _run_tests() -> int:
    import tempfile, os as _os

    print("\n" + "=" * 60)
    print("  dd_issue_tracker 内部测试")
    print("=" * 60)

    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    tmp_path = tmp.name
    tmp.close()
    os.unlink(tmp_path)  # Remove empty file so init can create it fresh

    errors = []

    # Test 1: init
    print("\n[测试1] 初始化项目...")
    ok = os.system(f'python3 "{__file__}" init --project "测试IPO项目" --output "{tmp_path}" > /dev/null 2>&1') == 0
    if not ok:
        errors.append("init 命令失败")
        return 1
    with open(tmp_path, encoding="utf-8") as f:
        data = json.load(f)
    if data["project"] != "测试IPO项目":
        errors.append("init 项目名称不匹配")
    print(f"  ✓ init 通过（{tmp_path}）")

    # Test 2: add
    print("[测试2] 添加3个示例问题（RED/AMBER/GREEN）...")
    test_cases = [
        ("RED", "法律", "发行人存在未披露的关联方担保", "李四", "重大法律瑕疵，可能构成发行障碍"),
        ("AMBER", "财务", "应收账款账龄偏长（>1年占比约40%）", "王五", "流动性风险上升"),
        ("GREEN", "业务", "客户集中度较高（第一大客户占比约35%）", "赵六", "建议拓展新客户降低依赖"),
    ]
    ids = []
    for sev, cat, title, reporter, impact in test_cases:
        out = tempfile.mktemp(suffix=".json")
        rc = os.system(
            f'python3 "{__file__}" add --file "{tmp_path}" --title "{title}" '
            f'--category {cat} --severity {sev} --reporter {reporter} '
            f'--impact "{impact}" --target-fix 2026-04-30 > /dev/null 2>&1'
        )
        if rc != 0:
            errors.append(f"add 命令失败（{sev}）")
        # 获取最后生成的ID
        with open(tmp_path, encoding="utf-8") as f:
            d = json.load(f)
        ids.append(d["issues"][-1]["id"])
    print(f"  ✓ add 通过（共添加{len(test_cases)}条）")

    # Test 3: list
    print("[测试3] 列出所有问题...")
    rc = os.system(f'python3 "{__file__}" list --file "{tmp_path}" > /dev/null 2>&1') == 0
    if not rc:
        errors.append("list 命令失败")
    print("  ✓ list 通过")

    # Test 4: list with filter
    print("[测试4] 按严重程度过滤（RED）...")
    rc = os.system(f'python3 "{__file__}" list --file "{tmp_path}" --severity RED > /dev/null 2>&1') == 0
    if not rc:
        errors.append("list --severity 命令失败")
    print("  ✓ list --severity 通过")

    # Test 5: update
    print("[测试5] 更新问题状态...")
    rc = os.system(
        f'python3 "{__file__}" update --file "{tmp_path}" --id {ids[1]} '
        f'--status InProgress > /dev/null 2>&1'
    ) == 0
    if not rc:
        errors.append("update 命令失败")
    print("  ✓ update 通过")

    # Test 6: summary
    print("[测试6] 生成摘要报告...")
    rc = os.system(f'python3 "{__file__}" summary --file "{tmp_path}" > /dev/null 2>&1') == 0
    if not rc:
        errors.append("summary 命令失败")
    print("  ✓ summary 通过")

    # Test 7: export markdown
    print("[测试7] 导出Markdown报告...")
    md_path = tempfile.mktemp(suffix=".md")
    rc = os.system(
        f'python3 "{__file__}" export --file "{tmp_path}" --format markdown '
        f'--output "{md_path}" > /dev/null 2>&1'
    ) == 0
    if not rc:
        errors.append("export markdown 命令失败")
    with open(md_path, encoding="utf-8") as f:
        md_content = f.read()
    if "尽调问题追踪报告" not in md_content:
        errors.append("Markdown 导出内容异常")
    print("  ✓ export markdown 通过")

    # Test 8: export csv
    print("[测试8] 导出CSV报告...")
    csv_path = tempfile.mktemp(suffix=".csv")
    rc = os.system(
        f'python3 "{__file__}" export --file "{tmp_path}" --format csv '
        f'--output "{csv_path}" > /dev/null 2>&1'
    ) == 0
    if not rc:
        errors.append("export csv 命令失败")
    with open(csv_path, encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) < 2:
        errors.append("CSV 导出内容异常")
    print("  ✓ export csv 通过")

    # Cleanup
    for p in [tmp_path, md_path, csv_path]:
        try:
            os.unlink(p)
        except Exception:
            pass

    print()
    if errors:
        print("❌ 测试失败：")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("✅ 全部测试通过（8/8）")
        return 0


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="尽调问题追踪工具（DD Issue Tracker）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            示例：
              init：     python dd_issue_tracker.py init --project "XXIPO项目" --output issues.json
              add：      python dd_issue_tracker.py add --file issues.json --title "应收账款偏高" --category 财务 --severity AMBER --reporter 张三
              list：     python dd_issue_tracker.py list --file issues.json
              update：   python dd_issue_tracker.py update --file issues.json --id ISS-2026-0001 --status Resolved
              summary：  python dd_issue_tracker.py summary --file issues.json
              export：   python dd_issue_tracker.py export --file issues.json --format markdown --output report.md
              test：     python dd_issue_tracker.py --test
            """)
    )
    parser.add_argument("--test", action="store_true", help="运行内置测试")

    subparsers = parser.add_subparsers(dest="command", title="子命令")

    # init
    p_init = subparsers.add_parser("init", help="初始化新项目")
    p_init.add_argument("--project", required=True, help="项目名称")
    p_init.add_argument("--output", required=True, help="输出JSON文件路径")
    p_init.add_argument("--force", action="store_true", help="覆盖已存在的文件")

    # add
    p_add = subparsers.add_parser("add", help="添加新问题")
    p_add.add_argument("--file", required=True, help="issues.json文件路径")
    p_add.add_argument("--title", required=True, help="问题标题")
    p_add.add_argument("--category", required=True,
                       choices=["法律", "财务", "业务", "合规", "其他"],
                       help="问题类别")
    p_add.add_argument("--severity", required=True,
                       choices=["RED", "AMBER", "GREEN"],
                       help="严重程度")
    p_add.add_argument("--reporter", required=True, help="发现人")
    p_add.add_argument("--description", default="", help="问题详细描述")
    p_add.add_argument("--impact", default="", help="对项目的影响")
    p_add.add_argument("--recommendation", default="", help="建议处理方式")
    p_add.add_argument("--target-fix", default="", help="计划解决日期（YYYY-MM-DD）")

    # list
    p_list = subparsers.add_parser("list", help="列出问题")
    p_list.add_argument("--file", required=True, help="issues.json文件路径")
    p_list.add_argument("--severity", default="", help="按严重程度过滤（RED/AMBER/GREEN）")
    p_list.add_argument("--status", default="", help="按状态过滤（Open/InProgress/Resolved/Closed/Waived）")

    # update
    p_upd = subparsers.add_parser("update", help="更新问题")
    p_upd.add_argument("--file", required=True, help="issues.json文件路径")
    p_upd.add_argument("--id", required=True, help="问题ID（如ISS-2026-0001）")
    p_upd.add_argument("--status", default="", help="新状态")
    p_upd.add_argument("--severity", default="", help="新严重程度")
    p_upd.add_argument("--title", default="", help="新标题")
    p_upd.add_argument("--category", default="", help="新类别")
    p_upd.add_argument("--resolution", default="", help="解决方案（填写后状态自动更新为Resolved）")
    p_upd.add_argument("--related-issue", default="", help="关联问题ID，逗号分隔")
    p_upd.add_argument("--evidence-file", default="", help="支持性文件，逗号分隔")

    # summary
    p_sum = subparsers.add_parser("summary", help="生成统计摘要")
    p_sum.add_argument("--file", required=True, help="issues.json文件路径")

    # export
    p_exp = subparsers.add_parser("export", help="导出报告")
    p_exp.add_argument("--file", required=True, help="issues.json文件路径")
    p_exp.add_argument("--format", required=True, choices=["markdown", "csv"], help="导出格式")
    p_exp.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args(argv)

    if args.test:
        return _run_tests()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "list": cmd_list,
        "update": cmd_update,
        "summary": cmd_summary,
        "export": cmd_export,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
