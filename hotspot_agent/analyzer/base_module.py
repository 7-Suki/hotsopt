"""
分析模块基类 - 定义统一的输入输出格式
"""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisResult:
    """分析结果"""
    items: list          # 处理后的条目列表
    stats: dict = field(default_factory=dict)   # 统计信息
    metadata: dict = field(default_factory=dict) # 元数据


class BaseAnalyzer:
    """分析器基类"""

    def __init__(self, config: dict):
        self.config = config

    def analyze(self, items: list) -> AnalysisResult:
        """执行分析"""
        raise NotImplementedError

    def prepare_ai_input(self, items: list, max_items: int = 30) -> dict:
        """准备发送给AI分析的格式化数据"""
        prepared = []

        # 按分数排序，取top
        sorted_items = sorted(items, key=lambda x: x.score, reverse=True)[:max_items]

        for i, item in enumerate(sorted_items):
            entry = {
                "index": i + 1,
                "title": item.title,
                "url": item.url,
                "source": item.source,
                "source_type": item.source_type,
                "timestamp": item.timestamp,
                "summary": item.summary[:300] if item.summary else "",
                "tags": item.tags,
                "score": item.score,
                "popularity": item.popularity,
                "author": item.author,
            }
            prepared.append(entry)

        return {
            "total_items": len(prepared),
            "items": prepared,
        }
