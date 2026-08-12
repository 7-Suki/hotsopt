"""
报告生成器 - 支持 HTML 和 Markdown 格式的热点分析报告
"""

import json
import os
from datetime import datetime, timedelta


class ReportGenerator:
    """热点分析报告生成器"""

    def __init__(self, config: dict):
        self.report_config = config.get("report", {})
        self.output_dir = self.report_config.get("output_dir", "data")
        self.format = self.report_config.get("format", "html")
        self.max_topics = self.report_config.get("max_topics", 20)

    def generate(self, items: list, stats: dict, ai_results: list = None) -> str:
        """
        生成报告
        items: 分析后的热点条目
        stats: 统计信息
        ai_results: AI分析结果列表
        返回: 报告文件路径
        """
        os.makedirs(self.output_dir, exist_ok=True)

        # 合并AI分析结果
        if ai_results:
            items = self._merge_ai_results(items, ai_results)

        if self.format == "html":
            return self._generate_html(items, stats)
        else:
            return self._generate_markdown(items, stats)

    def _merge_ai_results(self, items: list, ai_results: list) -> list:
        """将AI分析结果合并到条目中"""
        result_map = {r.get("index", -1): r for r in ai_results}

        for i, item in enumerate(items):
            result = result_map.get(i + 1, {})
            if result:
                item.ai_summary = result.get("ai_summary", "")
                item.category = result.get("category", "")
                item.value_score = result.get("value_score", 0)
                item.value_reason = result.get("value_reason", "")
                item.credibility_score = result.get("credibility_score", 0)
                item.credibility_reason = result.get("credibility_reason", "")
                item.viewpoints = result.get("viewpoints", [])

        return items

    def _score_to_stars(self, score: float) -> str:
        """分数转星级"""
        full = int(score / 2)
        half = 1 if score % 2 >= 1 else 0
        empty = 5 - full - half
        return "★" * full + "☆" * empty

    def _score_color(self, score: float) -> str:
        """分数转颜色"""
        if score >= 8:
            return "#e74c3c"
        elif score >= 5:
            return "#f39c12"
        else:
            return "#27ae60"

    def _generate_html(self, items: list, stats: dict) -> str:
        """生成HTML格式报告"""
        today = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 统计
        dedup_stats = stats.get("dedup", {})
        total_raw = dedup_stats.get("total", 0)
        duplicates = dedup_stats.get("duplicates_found", 0)
        merged = dedup_stats.get("merged_groups", 0)
        final_count = stats.get("final_count", len(items))

        # 分类统计
        category_counts = {}
        for item in items:
            cat = item.category or "未分类"
            category_counts[cat] = category_counts.get(cat, 0) + 1

        cat_tags_html = "".join(
            f'<span class="cat-tag">{cat} ({cnt})</span>'
            for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1])
        )

        # 数据来源统计
        source_counts = {}
        for item in items:
            src_base = item.source_type or "other"
            source_counts[src_base] = source_counts.get(src_base, 0) + 1

        source_tags_html = "".join(
            f'<span class="src-tag">{src} ({cnt})</span>'
            for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1])
        )

        # 热点卡片
        cards_html = ""
        for i, item in enumerate(items):
            tags_html = ""
            if item.tags:
                tags_html = "".join(
                    f'<span class="tag">{t}</span>' for t in item.tags[:5]
                )

            viewpoints_html = ""
            if item.viewpoints:
                vp_items = "".join(
                    f'<li>{vp}</li>' for vp in item.viewpoints if vp
                )
                viewpoints_html = f"""
                <div class="viewpoints-box">
                    <h4>多方观点</h4>
                    <ul>{vp_items}</ul>
                </div>
                """

            merged_html = ""
            if item.merged_from:
                merged_html = f"""
                <div class="merged-info">
                    🔗 合并了 {len(item.merged_from)} 条重复信息
                </div>
                """

            cards_html += f"""
            <div class="card">
                <div class="card-header">
                    <span class="card-index">#{i + 1}</span>
                    <span class="card-score">热度: {item.score:.0f}</span>
                    <span class="card-source">{item.source}</span>
                </div>
                <h3 class="card-title">
                    <a href="{item.url}" target="_blank" rel="noopener">{item.title}</a>
                </h3>
                {tags_html and f'<div class="tags">{tags_html}</div>'}
                {item.ai_summary and f'<p class="ai-summary">📝 {item.ai_summary}</p>'}
                {item.category and f'<p class="category">📂 分类: {item.category}</p>'}
                <div class="ai-analysis">
                    <div class="score-row">
                        <span class="score-name">价值评分</span>
                        <span class="score-number">{item.value_score:.1f}/10</span>
                        <span class="score-desc">{item.value_reason or ''}</span>
                    </div>
                    <div class="score-row">
                        <span class="score-name">可信度</span>
                        <span class="score-number">{item.credibility_score:.1f}/10</span>
                        <span class="score-desc">{item.credibility_reason or ''}</span>
                    </div>
                    {viewpoints_html}
                </div>
                {merged_html}
                <div class="card-footer">
                    <span class="time">🕐 {item.timestamp[:19] if item.timestamp else ''}</span>
                    {item.author and f'<span class="author">👤 {item.author}</span>'}
                </div>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点发现日报 - {today}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #f0f2f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 16px;
            margin-bottom: 24px;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
        .header .subtitle {{ opacity: 0.85; font-size: 14px; }}
        .stats-bar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }}
        .stat-box {{
            flex: 1;
            min-width: 120px;
            background: white;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-align: center;
        }}
        .stat-box .num {{ font-size: 28px; font-weight: 700; color: #667eea; }}
        .stat-box .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
        .cat-tag, .src-tag {{
            display: inline-block;
            padding: 2px 10px;
            margin: 2px;
            font-size: 12px;
            border-radius: 12px;
        }}
        .cat-tag {{ background: #e8f5e9; color: #2e7d32; }}
        .src-tag {{ background: #e3f2fd; color: #1565c0; }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #333;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: box-shadow 0.2s;
        }}
        .card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
        .card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .card-index {{
            font-weight: 700;
            color: #667eea;
            font-size: 18px;
            min-width: 32px;
        }}
        .card-score {{
            background: #fff3e0;
            color: #e65100;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 600;
        }}
        .card-source {{
            color: #888;
            font-size: 12px;
            margin-left: auto;
        }}
        .card-title {{
            font-size: 16px;
            margin-bottom: 8px;
        }}
        .card-title a {{
            color: #333;
            text-decoration: none;
        }}
        .card-title a:hover {{ color: #667eea; }}
        .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }}
        .tag {{
            background: #f0f0f0;
            color: #666;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
        }}
        .ai-summary {{
            background: #f8f9ff;
            padding: 10px 14px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
            margin: 10px 0;
            font-size: 14px;
            color: #555;
        }}
        .category {{ color: #888; font-size: 13px; }}
        .ai-analysis {{
            margin: 12px 0;
        }}
        .score-row {{
            display: flex;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 6px;
            font-size: 14px;
            line-height: 1.6;
        }}
        .score-name {{
            color: #e74c3c;
            font-weight: 600;
        }}
        .score-number {{
            color: #e74c3c;
            font-weight: 700;
            margin-right: 6px;
        }}
        .score-desc {{
            color: #333;
            font-weight: 400;
        }}
        .viewpoints-box {{
            background: #fff9e6;
            padding: 12px 14px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        .viewpoints-box h4 {{
            font-size: 14px;
            color: #e65100;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .viewpoints-box ul {{
            padding-left: 18px;
            font-size: 14px;
            color: #333;
            line-height: 1.6;
        }}
        .viewpoints-box li {{ margin-bottom: 6px; }}
        .merged-info {{
            color: #e65100;
            font-size: 12px;
            margin: 6px 0;
            padding: 4px 10px;
            background: #fff3e0;
            border-radius: 6px;
            display: inline-block;
        }}
        .card-footer {{
            display: flex;
            gap: 16px;
            margin-top: 10px;
            font-size: 12px;
            color: #aaa;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #aaa;
            font-size: 12px;
        }}
        .footer a {{ color: #667eea; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 热点发现日报</h1>
            <div class="subtitle">覆盖 GitHub · Reddit · Hacker News · RSS 等多源渠道 | 生成时间: {now_str}</div>
        </div>

        <div class="stats-bar">
            <div class="stat-box">
                <div class="num">{final_count}</div>
                <div class="label">精选热点</div>
            </div>
            <div class="stat-box">
                <div class="num">{total_raw}</div>
                <div class="label">原始数据</div>
            </div>
            <div class="stat-box">
                <div class="num">{duplicates}</div>
                <div class="label">重复识别</div>
            </div>
            <div class="stat-box">
                <div class="num">{merged}</div>
                <div class="label">合并事件组</div>
            </div>
        </div>

        <div style="background:white;border-radius:12px;padding:16px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="margin-bottom:8px;"><strong>📂 分类分布:</strong></div>
            <div>{cat_tags_html or '暂无分类数据'}</div>
            <div style="margin-top:10px;"><strong>📡 数据来源:</strong></div>
            <div>{source_tags_html or '暂无来源数据'}</div>
        </div>

        <div class="section-title">📋 热点详情</div>
        {cards_html}

        <div class="footer">
            <p>本报告由 <strong>热点发现Agent</strong> 自动生成 | 数据来源: GitHub Trending、Reddit、Hacker News、RSS订阅源</p>
            <p>报告仅供参考，不构成任何投资或决策建议</p>
        </div>
    </div>
</body>
</html>"""

        filepath = os.path.join(self.output_dir, f"hotspot_report_{today}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"HTML报告已生成: {filepath}")
        return filepath

    def _generate_markdown(self, items: list, stats: dict) -> str:
        """生成Markdown格式报告"""
        today = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dedup_stats = stats.get("dedup", {})
        total_raw = dedup_stats.get("total", 0)
        duplicates = dedup_stats.get("duplicates_found", 0)
        merged = dedup_stats.get("merged_groups", 0)
        final_count = stats.get("final_count", len(items))

        lines = [
            f"# 🔥 热点发现日报 - {today}",
            "",
            f"> 生成时间: {now_str}",
            f"> 数据来源: GitHub Trending · Reddit · Hacker News · RSS",
            "",
            "## 📊 数据概览",
            "",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 精选热点 | {final_count} |",
            f"| 原始数据 | {total_raw} |",
            f"| 重复识别 | {duplicates} |",
            f"| 合并事件组 | {merged} |",
            "",
            "---",
            "",
            "## 📋 热点详情",
            "",
        ]

        for i, item in enumerate(items):
            lines.append(f"### {i + 1}. {item.title}")
            lines.append("")
            lines.append(f"- **来源**: {item.source}")
            lines.append(f"- **链接**: [{item.url}]({item.url})")
            lines.append(f"- **热度**: {item.score:.0f}")

            if item.ai_summary:
                lines.append(f"- **AI总结**: {item.ai_summary}")
            if item.category:
                lines.append(f"- **分类**: {item.category}")
            if item.value_score:
                lines.append(f"- **价值评分**: {item.value_score}/10")
                if item.value_reason:
                    lines.append(f"  - 理由: {item.value_reason}")
            if item.credibility_score:
                lines.append(f"- **可信度**: {item.credibility_score}/10")
                if item.credibility_reason:
                    lines.append(f"  - 理由: {item.credibility_reason}")
            if item.viewpoints:
                lines.append(f"- **多方观点**:")
                for vp in item.viewpoints:
                    lines.append(f"  - {vp}")
            if item.merged_from:
                lines.append(f"- **合并**: 包含 {len(item.merged_from)} 条重复信息")
            if item.tags:
                lines.append(f"- **标签**: {', '.join(item.tags)}")

            lines.append("")
            lines.append("---")
            lines.append("")

        lines.extend([
            "",
            "---",
            "",
            "*本报告由热点发现Agent自动生成 | 仅供参考*",
        ])

        content = "\n".join(lines)
        filepath = os.path.join(self.output_dir, f"hotspot_report_{today}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Markdown报告已生成: {filepath}")
        return filepath
