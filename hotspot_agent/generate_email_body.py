"""
从报告 HTML 中提取热点数据，生成邮件版 HTML 正文。
支持两种模式：
1. CSS 内联模式（推荐）：将完整报告 HTML 的 <style> 全部转为内联样式，邮件与浏览器视觉完全一致
2. 解析重建模式（legacy）：从报告中解析数据，用 table 布局重建邮件 HTML
"""
from html.parser import HTMLParser
import re
import os
from datetime import datetime, timedelta
from collections import Counter


class ReportParser(HTMLParser):
    """解析报告 HTML，提取统计数字和热点卡片"""

    def __init__(self):
        super().__init__()
        self.stats = {
            "selected": "20",
            "raw": "78",
            "duplicates": "0",
            "sources": "6",
        }
        self.cards = []
        self.current = None
        self.text_buf = ""

        # 状态标志
        self.in_ds_num = False
        self.in_ds_label = False
        self.ds_values = []
        self.ds_labels = []

        self.in_card = False
        self.in_index = False
        self.in_heat = False
        self.in_source = False
        self.in_title = False
        self.in_summary = False
        self.in_category = False
        self.in_tag = False
        self.in_score_value = False
        self.in_score_reason = False
        self.score_type = ""  # "value" or "cred"
        self.in_viewpoint = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "")

        # 解析统计数字
        if "ds-num" in cls:
            self.in_ds_num = True
            self.text_buf = ""
        elif "ds-label" in cls:
            self.in_ds_label = True
            self.text_buf = ""

        # 解析卡片
        if tag == "div" and "card" in cls and "trend-card" not in cls:
            self.in_card = True
            self.current = {
                "index": "",
                "heat": "",
                "source": "",
                "title": "",
                "url": "",
                "tags": [],
                "summary": "",
                "category": "",
                "value_score": "",
                "value_reason": "",
                "credibility_score": "",
                "credibility_reason": "",
                "viewpoints": [],
            }
        elif self.in_card:
            if "card-index" in cls:
                self.in_index = True
                self.text_buf = ""
            elif "card-score" in cls:
                self.in_heat = True
                self.text_buf = ""
            elif "card-source" in cls:
                self.in_source = True
                self.text_buf = ""
            elif "card-title" in cls:
                self.in_title = True
                self.text_buf = ""
            elif "ai-summary" in cls:
                self.in_summary = True
                self.text_buf = ""
            elif "category" in cls:
                self.in_category = True
                self.text_buf = ""
            elif "tag" in cls:
                self.in_tag = True
                self.text_buf = ""
            elif "score-value" in cls:
                self.in_score_value = True
                self.text_buf = ""
            elif "score-desc" in cls or "score-reason" in cls:
                self.in_score_reason = True
                self.text_buf = ""
            elif "viewpoints" in cls:
                self.in_viewpoint = True

        # 判断当前是价值评分还是可信度评分
        if self.in_score_value or self.in_score_reason:
            parent = attrs.get("data-type", "")
            if not parent:
                # 通过兄弟节点的前一个 score-name 判断（在 endtag 中处理）
                pass

        if self.in_title and tag == "a":
            self.current["url"] = attrs.get("href", "")

    def handle_endtag(self, tag):
        # 统计数字
        if self.in_ds_num:
            self.ds_values.append(self.text_buf.strip())
            self.in_ds_num = False
            self.text_buf = ""
        elif self.in_ds_label:
            self.ds_labels.append(self.text_buf.strip())
            self.in_ds_label = False
            self.text_buf = ""

        if not self.in_card:
            return

        if self.in_index:
            self.current["index"] = self.text_buf.strip().lstrip("#")
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
            # 去除 "📝" 或 "AI总结:" 前缀
            text = re.sub(r"^[📝]|^AI总结[:：]", "", text).strip()
            self.current["summary"] = text
            self.in_summary = False
        elif self.in_category:
            text = self.text_buf.strip()
            text = re.sub(r"^.*分类[:：]", "", text).strip()
            text = text.replace("</strong>", "").replace("<strong>", "").strip()
            self.current["category"] = text
            self.in_category = False
        elif self.in_tag:
            t = self.text_buf.strip()
            if t:
                self.current["tags"].append(t)
            self.in_tag = False
        elif self.in_score_value:
            val = self.text_buf.strip()
            if self.score_type == "cred":
                self.current["credibility_score"] = val
            else:
                self.current["value_score"] = val
            self.in_score_value = False
        elif self.in_score_reason:
            reason = self.text_buf.strip()
            if self.score_type == "cred":
                self.current["credibility_reason"] = reason
            else:
                self.current["value_reason"] = reason
            self.in_score_reason = False

        self.text_buf = ""

        if tag == "div" and self.in_card:
            cls = ""
            # HTMLParser 的 endtag 不直接提供 attrs，这里通过正则辅助判断已在 parse_report 中处理
            pass

    def handle_data(self, data):
        if self.in_ds_num or self.in_ds_label or self.in_card:
            self.text_buf += data

        # 判断当前 score 类型（value 还是 cred）
        if self.in_score_value or self.in_score_reason:
            # 利用 handle_data 捕获的 score-name 文本判断类型
            # 这里我们在遇到 score-name 数据时直接记录类型
            pass


class TypeTrackingParser(HTMLParser):
    """辅助解析器：用于判断 score-value 是属于价值评分还是可信度"""

    def __init__(self):
        super().__init__()
        self.type_sequence = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "")
        if "score-name" in cls:
            self._last_type_start = True
            self._buf = ""

    def handle_data(self, data):
        if getattr(self, "_last_type_start", False):
            self._buf += data

    def handle_endtag(self, tag):
        if getattr(self, "_last_type_start", False):
            name = self._buf.strip()
            if "价值" in name:
                self.type_sequence.append("value")
            elif "可信" in name or "可信度" in name:
                self.type_sequence.append("cred")
            self._last_type_start = False


def parse_report(html_path: str) -> tuple:
    """Parse report HTML and extract stats + card data"""
    with open(html_path, "r", encoding="utf-8-sig") as f:
        html = f.read()

    # 1. 提取统计数字
    ds_items = re.findall(
        r'<div class="ds-item">\s*<div class="ds-num">(.*?)</div>\s*<div class="ds-label">(.*?)</div>\s*</div>',
        html,
        re.DOTALL,
    )
    stats = {"selected": "20", "raw": "78", "duplicates": "0", "sources": "6"}
    label_map = {
        "精选热点": "selected",
        "原始数据": "raw",
        "识别重复": "duplicates",
        "数据来源": "sources",
    }
    for num, label in ds_items:
        clean_label = re.sub(r"<[^>]+>", "", label).strip()
        clean_num = re.sub(r"<[^>]+>", "", num).strip()
        key = label_map.get(clean_label)
        if key:
            stats[key] = clean_num

    # 2. 提取 score 类型顺序
    type_parser = TypeTrackingParser()
    type_parser.feed(html)
    score_types = type_parser.type_sequence

    # 3. 提取所有卡片
    cards = []
    card_blocks = re.findall(
        r'<div class="card">(.*?)</div>\s*</div>',
        html, re.DOTALL
    )

    for idx, block in enumerate(card_blocks):
        card = {}

        # Index
        idx_m = re.search(r'card-index">\s*(.*?)\s*</span>', block)
        if idx_m:
            card["index"] = idx_m.group(1).strip().lstrip("#")

        # Heat
        heat_m = re.search(r'card-score">(.*?)<', block)
        if heat_m:
            heat = re.sub(r"<[^>]+>", "", heat_m.group(1)).strip()
            # 去除"热度:"前缀和emoji
            heat = re.sub(r"^[🔥\s]*热度[:：]?\s*", "", heat).strip()
            card["heat"] = heat

        # Source
        src_m = re.search(r'card-source">(.*?)</span>', block)
        if src_m:
            card["source"] = re.sub(r"<[^>]+>", "", src_m.group(1)).strip()

        # Title & URL
        title_m = re.search(r'card-title"><a href="([^"]+)".*?>(.*?)</a>', block)
        if title_m:
            card["url"] = title_m.group(1)
            card["title"] = re.sub(r"<[^>]+>", "", title_m.group(2)).strip()
        else:
            title_m2 = re.search(r'card-title">(.*?)<', block)
            if title_m2:
                card["title"] = re.sub(r"<[^>]+>", "", title_m2.group(1)).strip()

        # Tags
        tags = re.findall(r'<span class="tag">(.*?)</span>', block)
        card["tags"] = [re.sub(r"<[^>]+>", "", t).strip() for t in tags]

        # AI Summary
        summary_m = re.search(r'ai-summary">\s*(.*?)\s*</p>', block)
        if summary_m:
            summary = re.sub(r"<[^>]+>", "", summary_m.group(1)).strip()
            summary = re.sub(r"^[📝]|^AI总结[:：]", "", summary).strip()
            card["summary"] = summary

        # Category
        cat_m = re.search(r'class="category">\s*(.*?)\s*</p>', block)
        if cat_m:
            cat = re.sub(r"<[^>]+>", "", cat_m.group(1)).strip()
            cat = re.sub(r"^.*分类[:：]", "", cat).strip()
            card["category"] = cat

        # Scores and reasons
        score_values = re.findall(r'class="score-number">(.*?)</span>', block)
        score_reasons = re.findall(r'class="score-desc">(.*?)</span>', block)
        for i, stype in enumerate(score_types):
            if i < len(score_values):
                val = re.sub(r"<[^>]+>", "", score_values[i]).strip()
                reason = re.sub(r"<[^>]+>", "", score_reasons[i]).strip() if i < len(score_reasons) else ""
                if stype == "value":
                    card["value_score"] = val
                    card["value_reason"] = reason
                elif stype == "cred":
                    card["credibility_score"] = val
                    card["credibility_reason"] = reason

        # Viewpoints
        vps = re.findall(r'<span class="vp-item">(.*?)</span>', block)
        card["viewpoints"] = [re.sub(r"<[^>]+>", "", v).strip() for v in vps]

        if card.get("title"):
            cards.append(card)

    return stats, cards


def escape_html(text: str) -> str:
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_email_html(cards: list, stats: dict, date_str: str, source_list: str = "") -> str:
    """Build email body HTML matching the screenshot card layout"""

    # 默认数据源
    if not source_list:
        source_list = "GitHub Trending · TechCrunch · Ars Technica · The Verge · Wired · VentureBeat"

    # 热点卡片 HTML
    items_html = ""
    for i, card in enumerate(cards[:20]):
        idx = card.get("index", str(i + 1))
        title = card.get("title", "")
        url = card.get("url", "#")
        source = card.get("source", "")
        heat = card.get("heat", "")
        summary = card.get("summary", "")
        value_score = card.get("value_score", "")
        value_reason = card.get("value_reason", "")

        # 热度标签：只保留数字
        heat_num = re.search(r"[\d,]+", str(heat))
        heat_display = f"热度 {heat_num.group(0)}" if heat_num else str(heat)

        title_link = f'<a href="{url}" style="color:#333;text-decoration:none;font-weight:600;">{escape_html(title)}</a>'

        items_html += f"""
    <tr>
      <td style="padding:0 0 14px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <tr><td style="padding:18px 20px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-size:20px;font-weight:700;color:#667eea;padding-right:8px;vertical-align:top;" width="36">#{idx}</td>
                <td>
                  <span style="display:inline-block;background:#fff3e0;color:#e65100;padding:3px 10px;border-radius:10px;font-size:12px;font-weight:600;margin-right:6px;">{escape_html(heat_display)}</span>
                  <span style="font-size:12px;color:#888;">{escape_html(source)}</span>
                </td>
              </tr>
            </table>
            <div style="font-size:16px;font-weight:600;color:#333;margin:10px 0 8px 0;line-height:1.5;">{title_link}</div>
            <div style="background:#f8f9ff;padding:12px 14px;border-left:4px solid #667eea;border-radius:6px;font-size:13px;color:#555;line-height:1.7;margin:8px 0;">
              {escape_html(summary)}
            </div>
            <div style="font-size:12px;color:#667eea;margin-top:8px;">
              <span style="display:inline-block;margin-right:4px;">💎</span>
              <strong>{escape_html(value_score)}</strong>
              <span style="color:#888;margin-left:4px;">— {escape_html(value_reason)}</span>
            </div>
          </td></tr>
        </table>
      </td>
    </tr>
    """

    selected = stats.get("selected", "20")
    raw = stats.get("raw", "78")
    sources = stats.get("sources", "6")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>热点发现日报 - {date_str}</title>
</head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f0f2f5;">
    <tr><td align="center" style="padding:20px 10px;">
      <table width="680" cellpadding="0" cellspacing="0" border="0" style="max-width:680px;width:100%;">
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:16px;padding:40px 24px;text-align:center;color:#ffffff;">
          <h1 style="margin:0 0 8px 0;font-size:28px;font-weight:700;">🔥 热点发现日报</h1>
          <p style="margin:0;font-size:13px;opacity:0.9;line-height:1.8;">
            {date_str} | 多源聚合 · AI分析 · 价值评估<br>
            {source_list}
          </p>
        </td></tr>

        <!-- Stats -->
        <tr><td style="padding:16px 0;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td width="32%" style="padding-right:8px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;padding:18px 10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                  <tr><td style="font-size:28px;font-weight:700;color:#667eea;">{selected}</td></tr>
                  <tr><td style="font-size:12px;color:#888;padding-top:4px;">精选热点</td></tr>
                </table>
              </td>
              <td width="32%" style="padding:0 4px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;padding:18px 10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                  <tr><td style="font-size:28px;font-weight:700;color:#667eea;">{raw}</td></tr>
                  <tr><td style="font-size:12px;color:#888;padding-top:4px;">原始数据</td></tr>
                </table>
              </td>
              <td width="32%" style="padding-left:8px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;padding:18px 10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                  <tr><td style="font-size:28px;font-weight:700;color:#667eea;">{sources}</td></tr>
                  <tr><td style="font-size:12px;color:#888;padding-top:4px;">数据来源</td></tr>
                </table>
              </td>
            </tr>
          </table>
        </td></tr>

        <!-- Items -->
        {items_html}

        <!-- Footer -->
        <tr><td style="text-align:center;padding:30px 10px;color:#aaa;font-size:12px;line-height:2;">
          <p style="margin:0;">🤖 本报告由 <strong>热点发现Agent v1.0</strong> 自动生成 | 每日 8:00 推送</p>
          <p style="margin:0;color:#e74c3c;">⚠️ 报告仅供信息参考，不构成任何投资、商业或决策建议</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return html


def inline_report_for_email(report_path: str) -> str:
    """
    将完整报告 HTML 的 CSS 全部内联，使邮件正文与浏览器报告视觉一致。
    使用 premailer 将 <style> 标签中的样式转换为 inline style 属性。

    Args:
        report_path: 完整报告 HTML 文件路径

    Returns:
        CSS 已内联的 HTML 字符串（适合作为邮件正文）
    """
    try:
        from premailer import Premailer

        with open(report_path, "r", encoding="utf-8-sig") as f:
            html = f.read()

        # 修复 premailer 不支持的 CSS 值
        # 8-digit hex colors with alpha (e.g., #667eea22) are not valid CSS 2.1
        html = re.sub(r'#667eea22\b', 'rgba(102,126,234,0.13)', html)

        # 使用 premailer 将 CSS 内联
        p = Premailer(
            html,
            keep_style_tags=False,         # 移除 <style> 标签
            remove_classes=False,          # 保留 class（方便调试）
            strip_important=False,         # 保留 !important
            allow_network=False,           # 不加载外部资源
            css_text=None,
        )
        inlined = p.transform()

        # 邮件兼容性调整：移除残留的 <style> 标签（如 @media 查询）
        inlined = re.sub(r'<style[^>]*>.*?</style>', '', inlined, flags=re.DOTALL)

        # 将 container 宽度调整为邮件友好的宽度
        inlined = inlined.replace('max-width:900px', 'max-width:680px')

        return inlined

    except ImportError:
        # premailer 不可用时，回退到原始 HTML（仍有 <style> 标签，但至少内容完整）
        print("Warning: premailer not available, email body will use <style> tags (may not render in some email clients)")
        with open(report_path, "r", encoding="utf-8-sig") as f:
            return f.read()


if __name__ == "__main__":
    import sys

    date_str = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    report_path = f"hotspot_agent/data/hotspot_report_{date_str}.html"

    # 默认使用 CSS 内联模式，生成与浏览器一致的邮件正文
    if "--legacy" in sys.argv:
        stats, cards = parse_report(report_path)
        print(f"Parsed {len(cards)} cards from report (legacy mode)")
        if cards:
            html = build_email_html(cards, stats, date_str)
        else:
            print("ERROR: No cards parsed from report!")
            sys.exit(1)
    else:
        print(f"Inlining CSS from: {report_path}")
        html = inline_report_for_email(report_path)

    output_path = f"hotspot_agent/data/email_body_{date_str}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Email body saved to: {output_path} ({len(html):,} chars)")
