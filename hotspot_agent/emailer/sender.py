"""
邮件推送模块 - 通过 Agent Mail 发送热点分析报告
支持 HTML 和纯文本邮件
"""

import os
import json
from datetime import datetime


class EmailSender:
    """邮件发送器 - 使用 Agent Mail 服务"""

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

        # 读取报告内容
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"{self.subject_prefix}{today} - 热点分析报告"

        # 构建邮件内容
        is_html = report_path.endswith(".html")
        body = self._build_email_body(content, stats, is_html)

        # 准备发送指令（供Agent Mail调用）
        send_instruction = {
            "action": "send_report",
            "subject": subject,
            "recipients": self.recipients,
            "body": body,
            "is_html": is_html,
            "report_path": report_path,
        }

        # 保存发送指令到JSON（供Agent Mail读取）
        instruction_path = os.path.join(
            os.path.dirname(report_path),
            f"email_instruction_{today}.json",
        )
        with open(instruction_path, "w", encoding="utf-8") as f:
            json.dump(send_instruction, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "subject": subject,
            "recipients": self.recipients,
            "instruction_file": instruction_path,
            "message": f"邮件发送指令已准备就绪，请通过Agent Mail发送。\n"
                       f"主题: {subject}\n"
                       f"收件人: {', '.join(self.recipients)}",
        }

    def _build_email_body(self, content: str, stats: dict, is_html: bool) -> str:
        """构建邮件正文"""
        if is_html:
            # HTML邮件直接使用报告内容
            return content
        else:
            # 纯文本邮件
            dedup_stats = stats.get("dedup", {}) if stats else {}
            summary = (
                f"热点发现日报\n"
                f"{'=' * 40}\n"
                f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"原始数据: {dedup_stats.get('total', 0)} 条\n"
                f"精选热点: {stats.get('final_count', 0)} 条\n"
                f"重复识别: {dedup_stats.get('duplicates_found', 0)} 条\n"
                f"{'=' * 40}\n\n"
                f"{content}"
            )
            return summary

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
