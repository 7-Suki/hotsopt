"""
数据源管理器 - 统一管理和调度所有数据源
"""

import json
import os
from datetime import datetime, timedelta

from .base import HotItem
from .github import GitHubSource
from .reddit import RedditSource
from .hackernews import HackerNewsSource
from .rss_feeds import RSSSource
from .weibo import WeiboSource
from .zhihu import ZhihuSource
from .baidu import BaiduSource


class SourceManager:
    """数据源管理器"""

    def __init__(self, config: dict):
        self.config = config.get("sources", {})
        self.sources = []

        # 注册所有数据源
        self._register_sources()

    def _register_sources(self):
        """注册所有启用的数据源"""
        source_classes = {
            "github": GitHubSource,
            "reddit": RedditSource,
            "hackernews": HackerNewsSource,
            "rss_feeds": RSSSource,
            "weibo": WeiboSource,
            "zhihu": ZhihuSource,
            "baidu": BaiduSource,
        }

        for name, cls in source_classes.items():
            source_config = self.config.get(name, {})
            if source_config.get("enabled", True):
                self.sources.append(cls(source_config))

        print(f"已注册 {len(self.sources)} 个数据源")

    def fetch_all(self) -> list[HotItem]:
        """采集所有数据源的数据"""
        all_items = []

        for source in self.sources:
            try:
                print(f"正在采集: {source.name} ...")
                items = source.fetch()
                all_items.extend(items)
                print(f"  -> 获取 {len(items)} 条数据")
            except Exception as e:
                print(f"  -> 采集失败: {e}")

        # 按热度分数排序
        all_items.sort(key=lambda x: x.score, reverse=True)

        print(f"\n总计采集 {len(all_items)} 条原始数据")
        return all_items

    def save_raw_data(self, items: list[HotItem], output_dir: str):
        """保存原始采集数据"""
        os.makedirs(output_dir, exist_ok=True)

        today = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        filepath = os.path.join(output_dir, f"raw_data_{today}.json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                [item.to_dict() for item in items],
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"原始数据已保存到: {filepath}")
        return filepath
