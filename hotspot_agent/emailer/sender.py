"""
邮件推送模块 - 通过 QQ 邮箱发送热点分析报告
支持 HTML 和纯文本邮件
默认发送方式: mcp__qq-mail__SendMessage → 2972231200@qq.com
"""

import os
import json
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from hotspot_agent.generate_email_body import parse_report, build_email_html, inline_report_for_email


class EmailSender:
    """邮件发送器 - 使用 QQ 邮箱服务 (mcp__qq-mail__SendMessage)"""

    def __init__(self, config: dict):
        self.email_config = config.get("email", {})
        self.enabled = self.email_config.get("enabled", False)
        self.recipients = self.email_config.get("recipients", [])
        self.subject_prefix = self.email_config.get("subject_prefix", "[热点日报]")

    def send_report(self, report_path: str, stats: dict = None) -> dict:
        """
        发送报告邮件
        report_path: 报告文件路径（HTML或Markdown）
        stats: 统计数据
        返回: 发送结果
        """
        if not self.enabled:
            return {"success": False, "error": "邮件功能未启用"}

        if not self.recipients:
            return {"success": False, "error": "未配置收件人"}

        if not os.path.exists(report_path):
            return {"success": False, "error": f"报告文件不存在: {report_path}"}

        # 报告日期统一使用前一天（与数据采集周期保持一致）
        report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        subject = f"{self.subject_prefix}{report_date} - 热点日报"

        # 生成邮件正文（图片中的卡片形式）
        is_html = report_path.endswith(".html")
        body, email_body_path = self._build_email_body(report_path, report_date, stats, is_html)

        # 准备发送指令（供Agent Mail调用）
        send_instruction = {
            "action": "send_report",
            "subject": subject,
            "recipients": self.recipients,
            "body": body,
            "is_html": is_html,
            "email_body_path": email_body_path,
            "attachment_path": report_path,
        }

        # 保存发送指令到JSON（供 QQ 邮箱 MCP 调用读取）
        instruction_path = os.path.join(
            os.path.dirname(report_path),
            f"email_instruction_{report_date}.json",
        )
        with open(instruction_path, "w", encoding="utf-8") as f:
            json.dump(send_instruction, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "subject": subject,
            "recipients": self.recipients,
            "email_body_path": email_body_path,
            "attachment_path": report_path,
            "instruction_file": instruction_path,
            "message": f"邮件发送指令已准备就绪，请通过 QQ 邮箱发送。\n"
                       f"主题: {subject}\n"
                       f"收件人: {', '.join(self.recipients)}\n"
                       f"邮件正文: {email_body_path}\n"
                       f"附件: {report_path}",
        }

    def _build_email_body(self, report_path: str, report_date: str, stats: dict, is_html: bool):
        """构建邮件正文，返回 (body_content, email_body_path)"""
        if is_html:
            # 尝试 CSS 内联模式：将完整报告样式内联，确保邮件与浏览器视觉一致
            try:
                body = inline_report_for_email(report_path)
                if not body or len(body.strip()) < 100:
                    raise ValueError("Inline result too short, falling back")
            except Exception as e:
                print(f"CSS inline failed ({e}), trying legacy parse+rebuild...")
                # 回退到旧方法：解析报告 → 重建邮件 HTML
                try:
                    parsed_stats, cards = parse_report(report_path)
                    if stats:
                        dedup_stats = stats.get("dedup", {})
                        parsed_stats["raw"] = str(dedup_stats.get("total", parsed_stats.get("raw", "78")))
                        parsed_stats["duplicates"] = str(dedup_stats.get("duplicates_found", parsed_stats.get("duplicates", "0")))
                        parsed_stats["selected"] = str(stats.get("final_count", parsed_stats.get("selected", "20")))

                    source_list = "GitHub Trending · TechCrunch · Ars Technica · The Verge · Wired · VentureBeat"
                    body = build_email_html(cards, parsed_stats, report_date, source_list)
                except Exception:
                    with open(report_path, "r", encoding="utf-8") as f:
                        body = f.read()

            # 保存邮件正文文件
            email_body_path = os.path.join(
                os.path.dirname(report_path),
                f"email_body_{report_date}.html",
            )
            with open(email_body_path, "w", encoding="utf-8") as f:
                f.write(body)
            return body, email_body_path
        else:
            # 纯文本邮件
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            dedup_stats = stats.get("dedup", {}) if stats else {}
            body = (
                f"热点日报\n"
                f"{'=' * 40}\n"
                f"报告日期: {report_date}\n"
                f"原始数据: {dedup_stats.get('total', 0)} 条\n"
                f"精选热点: {stats.get('final_count', 0)} 条\n"
                f"重复识别: {dedup_stats.get('duplicates_found', 0)} 条\n"
                f"{'=' * 40}\n\n"
                f"{content}"
            )
            email_body_path = os.path.join(
                os.path.dirname(report_path),
                f"email_body_{report_date}.txt",
            )
            with open(email_body_path, "w", encoding="utf-8") as f:
                f.write(body)
            return body, email_body_path

    def set_recipients(self, recipients: list):
        """更新收件人列表"""
        self.recipients = recipients
        self.email_config["recipients"] = recipients

    def toggle(self, enable: bool = None):
        """切换邮件发送开关"""
        if enable is not None:
            self.enabled = enable
        else:
            self.enabled = not self.enabled
        self.email_config["enabled"] = self.enabled
        return self.enabled
