"""
从报告 HTML 中提取热点数据，生成邮件版 HTML 正文
"""
from html.parser import HTMLParser
import re


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.current = None
        self.in_card = False
        self.in_title = False
        self.in_summary = False
        self.in_category = False
        self.in_score_value = False
        self.in_score_reason = False
        self.in_cred_value = False
        self.in_cred_reason = False
        self.in_heat = False
        self.in_source = False
        self.in_index = False
        self.in_tag = False
        self.in_viewpoint = False
        self.in_trend = False
        self.text_buf = ""
        self.score_type = ""  # "value" or "cred"
        self.trend_text = ""
        self.trend_risks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "")

        if tag == "div" and "card" in cls:
            if "trend-card" in cls:
                self.in_trend = True
            else:
                self.in_card = True
                self.current = {
                    "index": "", "heat": "", "source": "", "title": "", "url": "",
                    "tags": [], "summary": "", "category": "",
                    "value_score": "", "value_reason": "",
                    "cred_score": "", "cred_reason": "",
                    "viewpoints": [],
                }
        elif self.in_card or self.in_trend:
            if "card-index" in cls:
                self.in_index = True
            elif "card-score" in cls:
                self.in_heat = True
            elif "card-source" in cls:
                self.in_source = True
            elif "card-title" in cls:
                self.in_title = True
            elif "ai-summary" in cls:
                self.in_summary = True
            elif "category" in cls:
                self.in_category = True
            elif "tag" in cls:
                self.in_tag = True
            elif "score-value" in cls:
                self.in_score_value = True
            elif "score-reason" in cls:
                self.in_score_reason = True
            elif "viewpoints" in cls:
                self.in_viewpoint = True

        if self.in_title and tag == "a":
            self.current["url"] = attrs.get("href", "")
        if self.in_card and tag == "li" and self.in_viewpoint:
            self.text_buf = ""

    def handle_endtag(self, tag):
        if self.in_card:
            if self.in_index:
                self.current["index"] = self.text_buf.strip()
                self.in_index = False
            elif self.in_heat:
                self.current["heat"] = self.text_buf.strip()
                self.in_heat = False
            elif self.in_source:
                self.current["source"] = self.text_buf.strip()
                self.in_source = False
            elif self.in_title:
                self.current["title"] = self.text_buf.strip()
                self.in_title = False
            elif self.in_summary:
                text = self.text_buf.strip()
                if text.startswith("AI总结:"):
                    text = text[4:].strip()
                self.current["summary"] = text
                self.in_summary = False
            elif self.in_category:
                text = self.text_buf.strip()
                if text.startswith("分类:"):
                    text = text[3:].strip()
                self.current["category"] = text
                self.in_category = False
            elif self.in_score_value:
                val = self.text_buf.strip()
                if self.score_type == "cred":
                    self.current["cred_score"] = val
                else:
                    self.current["value_score"] = val
                self.in_score_value = False
            elif self.in_score_reason:
                reason = self.text_buf.strip()
                if self.score_type == "cred":
                    self.current["cred_reason"] = reason
                else:
                    self.current["value_reason"] = reason
                self.in_score_reason = False
            elif self.in_tag:
                t = self.text_buf.strip()
                if t:
                    self.current["tags"].append(t)
                self.in_tag = False
            elif self.in_viewpoint and tag == "li":
                t = self.text_buf.strip()
                if t:
                    self.current["viewpoints"].append(t)
            self.text_buf = ""

        if tag == "div" and self.in_card:
            # Check if we should close the card
            pass

    def handle_endtag_close(self, tag, attrs=None):
        """Special handling"""
        pass

    def handle_data(self, data):
        if self.in_card or self.in_trend:
            self.text_buf += data
        if self.in_trend:
            self.trend_text += data

    def feed_endtag(self, tag, attrs):
        """Process div end tags to detect card closure"""
        if tag == "div":
            cls = attrs.get("class", "") if attrs else ""
            if self.in_card and "card" in cls and "trend-card" not in cls:
                if self.current and self.current["title"]:
                    self.cards.append(self.current)
                self.current = None
                self.in_card = False
            elif self.in_trend and "trend-card" in cls:
                self.in_trend = False
            elif self.in_viewpoint and "viewpoints" in cls:
                self.in_viewpoint = False


def parse_report(html_path: str) -> list:
    """Parse report HTML and extract card data using regex"""
    with open(html_path, "r", encoding="utf-8-sig") as f:
        html = f.read()

    cards = []

    # Find all card blocks (excluding trend-card)
    card_pattern = re.compile(
        r'<div class="card(?! trend-card)".*?</div>\s*</div>\s*(?=<div class="card|</div>\s*<div class="methodology")',
        re.DOTALL
    )

    # Simpler approach: split by card blocks
    # Find all cards
    card_blocks = re.findall(
        r'<div class="card">(.*?)</div>\s*</div>',
        html, re.DOTALL
    )

    for block in card_blocks:
        card = {}

        # Index
        idx_m = re.search(r'card-index">\s*(.*?)\s*</span>', block)
        if idx_m:
            card["index"] = idx_m.group(1).strip().lstrip("#")

        # Heat
        heat_m = re.search(r'card-score">(.*?)</span>', block)
        if heat_m:
            card["heat"] = heat_m.group(1).strip()

        # Source
        src_m = re.search(r'card-source">(.*?)</span>', block)
        if src_m:
            card["source"] = src_m.group(1).strip()

        # Title & URL
        title_m = re.search(r'card-title"><a href="([^"]+)".*?>(.*?)</a>', block)
        if title_m:
            card["url"] = title_m.group(1)
            card["title"] = title_m.group(2).strip()

        # Tags
        tags = re.findall(r'<span class="tag">(.*?)</span>', block)
        card["tags"] = [t.strip() for t in tags]

        # AI Summary
        summary_m = re.search(r'ai-summary">\s*AI总结:\s*(.*?)\s*</p>', block)
        if summary_m:
            card["summary"] = summary_m.group(1).strip()

        # Category
        cat_m = re.search(r'class="category">\s*分类:\s*(.*?)\s*</p>', block)
        if cat_m:
            card["category"] = cat_m.group(1).strip()

        # Value score
        val_m = re.search(r'价值评分.*?score-value">(.*?)</span>', block, re.DOTALL)
        if val_m:
            card["value_score"] = val_m.group(1).strip()
        val_r = re.search(r'价值评分.*?score-reason">(.*?)</span>', block, re.DOTALL)
        if val_r:
            card["value_reason"] = val_r.group(1).strip()

        # Credibility score
        cred_m = re.search(r'可信度.*?score-value">(.*?)</span>', block, re.DOTALL)
        if cred_m:
            card["cred_score"] = cred_m.group(1).strip()
        cred_r = re.search(r'可信度.*?score-reason">(.*?)</span>', block, re.DOTALL)
        if cred_r:
            card["cred_reason"] = cred_r.group(1).strip()

        # Viewpoints
        vps = re.findall(r'<li>(.*?)</li>', block)
        card["viewpoints"] = [v.strip() for v in vps]

        cards.append(card)

    return cards


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_email_html(cards: list, date_str: str) -> str:
    """Build email-optimized HTML body"""

    # Category stats
    categories = {}
    for c in cards:
        cat = c.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1

    cat_colors = {
        "AI/机器学习": ("#e8f5e9", "#2e7d32"),
        "科技/互联网": ("#e3f2fd", "#1565c0"),
        "安全/隐私": ("#fce4ec", "#c62828"),
        "金融/投资": ("#fff3e0", "#e65100"),
        "科学/研究": ("#f3e5f5", "#6a1b9a"),
        "创业/商业": ("#e0f2f1", "#00695c"),
    }
    cat_tags = ""
    for cat, cnt in categories.items():
        bg, fg = cat_colors.get(cat, ("#f0f0f0", "#666"))
        cat_tags += f'<span style="display:inline-block;padding:3px 12px;margin:2px;font-size:12px;border-radius:12px;background:{bg};color:{fg};">{escape_html(cat)} ({cnt})</span>'

    # Source stats
    sources = {}
    for c in cards:
        src = c.get("source", "未知")
        sources[src] = sources.get(src, 0) + 1
    src_tags = ""
    for src, cnt in sources.items():
        src_tags += f'<span style="display:inline-block;padding:3px 12px;margin:2px;font-size:12px;border-radius:12px;background:#e3f2fd;color:#1565c0;">{escape_html(src)}</span>'

    # TOP 5 items
    top5_html = ""
    for i, card in enumerate(cards[:5]):
        idx = i + 1
        title = card.get("title", "")
        summary = card.get("summary", "")
        url = card.get("url", "#")
        source = card.get("source", "")
        heat = card.get("heat", "")
        category = card.get("category", "")
        v_score = card.get("value_score", "")

        heat_html = ""
        if heat and heat != "热度: 5":
            heat_num = re.search(r'[\d,]+', heat)
            if heat_num:
                heat_html = f'<span style="display:inline-block;background:#fff3e0;color:#e65100;padding:2px 10px;border-radius:8px;font-size:12px;font-weight:600;">{heat}</span>'

        v_color = "#e74c3c"
        try:
            vs = float(v_score.split("/")[0])
            if vs < 7:
                v_color = "#888"
            elif vs < 8:
                v_color = "#f39c12"
        except:
            pass

        top5_html += f"""
        <tr>
            <td style="padding:16px 20px;border-bottom:1px solid #eee;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td style="font-size:18px;font-weight:700;color:#667eea;width:36px;vertical-align:top;">#{idx}</td>
                        <td style="vertical-align:top;">
                            <div style="margin-bottom:6px;">
                                {heat_html}
                                <span style="font-size:12px;color:#999;margin-left:8px;">{escape_html(source)}</span>
                                <span style="display:inline-block;margin-left:12px;font-size:12px;color:#999;">{escape_html(category)}</span>
                            </div>
                            <a href="{url}" style="font-size:16px;color:#333;text-decoration:none;font-weight:600;line-height:1.4;">{escape_html(title)}</a>
                            <p style="margin:8px 0;font-size:13px;color:#555;line-height:1.6;background:#f8f9ff;padding:10px 14px;border-radius:6px;border-left:3px solid #667eea;">{escape_html(summary)}</p>
                            <span style="display:inline-block;font-size:13px;color:{v_color};font-weight:600;">⭐ 价值: {v_score}</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
</head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Arial,sans-serif;">

<table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f0f2f5;">
<tr><td align="center" style="padding:20px;">

<table cellpadding="0" cellspacing="0" border="0" width="600" style="background:white;border-radius:12px;overflow:hidden;">

<!-- Header -->
<tr>
    <td style="background:#667eea;padding:40px 28px;text-align:center;border-radius:12px 12px 0 0;">
        <h1 style="margin:0;font-size:28px;color:#fff;font-weight:700;">热点发现日报</h1>
        <p style="margin:10px 0 0;font-size:13px;color:rgba(255,255,255,0.85);line-height:1.8;">
            多源聚合 | AI智能分析 | 价值评估<br>
            GitHub Trending · TechCrunch · Ars Technica · The Verge · Wired · VentureBeat<br>
            生成时间: {date_str}
        </p>
    </td>
</tr>

<!-- Stats -->
<tr>
    <td style="padding:24px 24px 12px;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
                <td width="24%" style="text-align:center;padding:14px 8px;background:#f8f9ff;border-radius:8px;">
                    <div style="font-size:28px;font-weight:700;color:#667eea;">{len(cards)}</div>
                    <div style="font-size:11px;color:#888;margin-top:2px;">精选热点</div>
                </td>
                <td width="2%"></td>
                <td width="24%" style="text-align:center;padding:14px 8px;background:#f8f9ff;border-radius:8px;">
                    <div style="font-size:28px;font-weight:700;color:#e65100;">78</div>
                    <div style="font-size:11px;color:#888;margin-top:2px;">原始数据</div>
                </td>
                <td width="2%"></td>
                <td width="24%" style="text-align:center;padding:14px 8px;background:#f8f9ff;border-radius:8px;">
                    <div style="font-size:28px;font-weight:700;color:#2e7d32;">{len(sources)}</div>
                    <div style="font-size:11px;color:#888;margin-top:2px;">数据来源</div>
                </td>
                <td width="2%"></td>
                <td width="24%" style="text-align:center;padding:14px 8px;background:#f8f9ff;border-radius:8px;">
                    <div style="font-size:28px;font-weight:700;color:#c62828;">{len(categories)}</div>
                    <div style="font-size:11px;color:#888;margin-top:2px;">覆盖分类</div>
                </td>
            </tr>
        </table>
    </td>
</tr>

<!-- Category Tags -->
<tr>
    <td style="padding:8px 24px;">
        <div style="background:#f8f9ff;border-radius:8px;padding:14px 16px;">
            <div style="font-size:13px;font-weight:600;color:#333;margin-bottom:8px;">分类分布</div>
            {cat_tags}
        </div>
    </td>
</tr>

<!-- Source Tags -->
<tr>
    <td style="padding:4px 24px 12px;">
        <div style="background:#f8f9ff;border-radius:8px;padding:14px 16px;">
            <div style="font-size:13px;font-weight:600;color:#333;margin-bottom:8px;">数据来源</div>
            {src_tags}
        </div>
    </td>
</tr>

<!-- TOP 5 -->
<tr>
    <td style="padding:12px 24px 4px;">
        <h2 style="margin:0;font-size:18px;color:#333;border-bottom:2px solid #667eea;padding-bottom:8px;">TOP 5 热点</h2>
    </td>
</tr>

{top5_html}

<!-- View full report -->
<tr>
    <td style="padding:20px 24px 24px;text-align:center;">
        <div style="background:#f8f9ff;border:2px solid #667eea33;border-radius:10px;padding:18px;">
            <p style="margin:0 0 6px;font-size:15px;color:#667eea;font-weight:600;">完整 20 条热点分析 + 趋势研判</p>
            <p style="margin:0;font-size:13px;color:#666;">详见附件 <strong style="color:#333;">hotspot_report_2026-08-11.html</strong></p>
            <p style="margin:6px 0 0;font-size:12px;color:#aaa;">下载后用浏览器打开，即可查看完整排版与交互效果</p>
        </div>
    </td>
</tr>

<!-- Footer -->
<tr>
    <td style="background:#f8f9ff;padding:24px;text-align:center;border-radius:0 0 12px 12px;">
        <p style="margin:0;font-size:12px;color:#aaa;line-height:1.8;">
            本报告由 <strong style="color:#667eea;">热点发现Agent v1.0</strong> 自动生成<br>
            报告仅供信息参考，不构成任何投资、商业或决策建议<br>
            每日 8:00 自动推送
        </p>
    </td>
</tr>

</table>
</td></tr>
</table>

</body>
</html>"""
    return html


if __name__ == "__main__":
    import sys
    date_str = sys.argv[1] if len(sys.argv) > 1 else "2026-08-11"

    report_path = f"hotspot_agent/data/hotspot_report_{date_str}.html"
    cards = parse_report(report_path)
    print(f"Parsed {len(cards)} cards from report")

    if cards:
        html = build_email_html(cards, f"{date_str} 15:22 (GMT+8)")
        output_path = f"hotspot_agent/data/email_body_{date_str}.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Email body saved to: {output_path} ({len(html)} chars)")
    else:
        print("ERROR: No cards parsed from report!")
