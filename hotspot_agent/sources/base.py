"""
数据源基类 - 定义标准化数据结构和采集接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class HotItem:
    """标准化热点数据项"""
    # 基本信息
    id: str                          # 唯一标识
    title: str                       # 标题
    url: str                         # 原始链接
    source: str                      # 来源平台名称 (如 "Hacker News")
    source_type: str                 # 来源类型 (github/reddit/hackernews/rss)
    timestamp: str                   # 发布时间 ISO格式

    # 内容
    summary: str = ""                # 摘要/描述
    author: str = ""                 # 作者
    tags: list = field(default_factory=list)  # 标签

    # 热度指标
    score: float = 0.0               # 综合热度分数
    popularity: dict = field(default_factory=dict)  # {"upvotes": 100, "comments": 50, ...}

    # AI 分析结果 (采集后填入)
    ai_summary: str = ""             # AI 生成的简短总结
    category: str = ""               # 分类
    value_score: float = 0.0         # 价值评分 (0-10)
    value_reason: str = ""           # 价值评分理由
    credibility_score: float = 0.0   # 可信度评分 (0-10)
    credibility_reason: str = ""    # 可信度评估理由
    viewpoints: list = field(default_factory=list)  # 不同观点
    merged_from: list = field(default_factory=list)  # 合并自哪些条目 (去重合并)
    is_duplicate: bool = False       # 是否为重复条目

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


class BaseSource(ABC):
    """数据源基类"""

    def __init__(self, config: dict):
        self.config = config
        self.name = "base"

    @property
    def enabled(self) -> bool:
        return self.config.get("enabled", True)

    @abstractmethod
    def fetch(self) -> list[HotItem]:
        """采集数据，返回标准化的 HotItem 列表"""
        pass

    def _make_id(self, *parts: str) -> str:
        """生成唯一ID"""
        raw = "-".join(str(p) for p in parts)
        return f"{self.name}:{raw}"
