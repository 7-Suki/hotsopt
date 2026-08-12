"""
热点发现Agent - 主入口程序
使用方法:
  python main.py              # 采集数据并生成报告
  python main.py --analyze    # 采集 + AI分析 + 生成报告
  python main.py --email      # 采集 + 分析 + 发送邮件报告
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hotspot_agent.config import load_config, save_config, DATA_DIR
from hotspot_agent.sources.manager import SourceManager
from hotspot_agent.analyzer.ai_pipeline import AIPipeline
from hotspot_agent.reporter.generator import ReportGenerator
from hotspot_agent.emailer.sender import EmailSender


def main():
    parser = argparse.ArgumentParser(description="热点发现Agent")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="执行AI分析",
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="通过邮件发送报告",
    )
    parser.add_argument(
        "--format",
        choices=["html", "markdown"],
        default=None,
        help="报告格式",
    )
    parser.add_argument(
        "--recipients",
        nargs="+",
        help="邮件收件人列表",
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="打开配置向导",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="指定输出目录",
    )
    args = parser.parse_args()

    # 配置模式
    if args.config:
        setup_wizard()
        return

    try:
        run(args)
    except Exception as e:
        print(f"\n❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run(args):
    """运行热点发现流程"""
    config = load_config()

    print("=" * 50)
    print("🔥 热点发现Agent v1.0")
    print("=" * 50)

    # Step 1: 数据采集
    print("\n📡 步骤1: 多源数据采集")
    print("-" * 30)
    source_manager = SourceManager(config)
    all_items = source_manager.fetch_all()

    if not all_items:
        print("⚠️  未采集到任何数据，请检查网络连接和数据源配置")
        return

    # 保存原始数据
    source_manager.save_raw_data(all_items, DATA_DIR)

    # Step 2: 去重 + AI分析提示
    print("\n🔍 步骤2: 数据处理与分析")
    print("-" * 30)
    pipeline = AIPipeline(config)
    top_items, stats, ai_prompt = pipeline.run_pipeline(all_items)

    # 保存AI分析提示（使用前一天日期，与数据周期保持一致）
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    prompt_path = os.path.join(DATA_DIR, f"ai_prompt_{report_date}.md")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(ai_prompt)
    print(f"AI分析提示已保存到: {prompt_path}")

    # Step 3: 生成报告
    print("\n📄 步骤3: 生成分析报告")
    print("-" * 30)

    # 应用格式设置
    if args.format:
        config["report"]["format"] = args.format

    reporter = ReportGenerator(config)
    report_path = reporter.generate(top_items, stats)
    print(f"✅ 报告已生成: {report_path}")

    # Step 4: 发送邮件（可选）
    if args.email:
        print("\n📧 步骤4: 邮件推送")
        print("-" * 30)

        sender = EmailSender(config)
        if args.recipients:
            sender.set_recipients(args.recipients)

        if not sender.enabled:
            # 询问是否启用
            print("邮件功能未启用，正在启用...")
            sender.toggle(True)

        result = sender.send_report(report_path, stats)
        if result.get("success"):
            print(f"✅ {result.get('message', '邮件准备完成')}")
        else:
            print(f"⚠️  {result.get('error', '发送失败')}")

    # 输出总结
    dedup_stats = stats.get("dedup", {})
    print("\n" + "=" * 50)
    print("📊 执行总结")
    print("=" * 50)
    print(f"  原始数据: {dedup_stats.get('total', 0)} 条")
    print(f"  发现重复: {dedup_stats.get('duplicates_found', 0)} 条")
    print(f"  合并事件: {dedup_stats.get('merged_groups', 0)} 组")
    print(f"  精选热点: {stats.get('final_count', 0)} 条")
    print(f"  报告文件: {report_path}")
    if args.analyze:
        print(f"  AI提示词: {prompt_path}")
    print("=" * 50)

    return top_items, stats, report_path


def setup_wizard():
    """交互式配置向导"""
    config = load_config()

    print("\n⚙️  配置向导")
    print("=" * 40)

    # 数据源配置
    print("\n📡 数据源设置:")
    for src_name in ["github", "reddit", "hackernews", "rss_feeds"]:
        current = config["sources"].get(src_name, {}).get("enabled", True)
        answer = input(f"  启用 {src_name}? [Y/n]: ").strip().lower()
        if answer == "n":
            config["sources"][src_name]["enabled"] = False
        elif answer == "y" or answer == "":
            config["sources"][src_name]["enabled"] = True

    # 报告格式
    print(f"\n📄 报告格式设置:")
    fmt = input(f"  选择格式 [html/markdown] (当前: {config['report']['format']}): ").strip()
    if fmt in ("html", "markdown"):
        config["report"]["format"] = fmt

    # 显示数量
    try:
        max_n = input(f"  报告中最多显示热点数 (当前: {config['report']['max_topics']}): ").strip()
        if max_n:
            config["report"]["max_topics"] = int(max_n)
    except ValueError:
        pass

    # 邮件配置
    print(f"\n📧 邮件推送设置:")
    email_enable = input(f"  启用邮件推送? [y/N]: ").strip().lower()
    if email_enable == "y":
        config["email"]["enabled"] = True
        recipients = input(f"  输入收件人邮箱 (用空格分隔): ").strip()
        if recipients:
            config["email"]["recipients"] = recipients.split()
    else:
        config["email"]["enabled"] = False

    # 保存
    save_config(config)
    print(f"\n✅ 配置已保存到: {os.path.join(os.path.dirname(__file__), 'hotspot_agent', 'config.json')}")


if __name__ == "__main__":
    main()
