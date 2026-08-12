"""
RSS 数据源采集器
支持多个 RSS 订阅源的聚合采集，使用 feedparser 库解析
"""

import re
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from .base import BaseSource, HotItem


class RSSSource(BaseSource):
    """RSS 订阅源采集器"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "rss"
        self.feeds = config.get("feeds", [])
        self.max_items = config.get("max_items_per_feed", 15)

    def fetch(self) -> list[HotItem]:
        if not self.enabled:
            return []

        results = []
        for feed_config in self.feeds:
            feed_name = feed_config.get("name", "Unknown")
            feed_url = feed_config.get("url", "")
            if not feed_url:
                continue

            try:
                items = self._parse_feed(feed_name, feed_url)
                results.extend(items[: self.max_items])
            except Exception as e:
                print(f"[RSS {feed_name}] 采集失败: {e}")

        return results

    def _clean_html(self, text: str) -> str:
        """去除HTML标签"""
        if not text:
            return ""
        clean = re.sub(r"<[^>]+>", "", text)
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip()

    def _parse_feed(self, name: str, url: str) -> list[HotItem]:
        """使用 feedparser 解析 RSS/Atom 源"""
        headers = {
            "User-Agent": "HotspotAgent/1.0 (RSS Reader; contact@example.com)",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        # feedparser 可以直接从字符串或响应解析
        feed = feedparser.parse(resp.content)

        if feed.bozo and not feed.entries:
            exc = feed.bozo_exception
            raise Exception(f"Feed解析失败: {exc}")

        items = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        for entry in feed.entries:
            try:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                # 提取链接
                link = entry.get("link", "")
                if not link:
                    # 某些feed将链接放在links列表中
                    links = entry.get("links", [])
                    if links:
                        link = links[0].get("href", "")

                # 提取摘要
                summary = ""
                if entry.get("summary"):
                    summary = self._clean_html(entry.summary)
                elif entry.get("content"):
                    content = entry.content[0].get("value", "") if entry.content else ""
                    summary = self._clean_html(content)
                if entry.get("description"):
                    desc = self._clean_html(entry.description)
                    if len(desc) > len(summary):
                        summary = desc

                # 提取时间
                ts = datetime.now(timezone.utc).isoformat()
                entry_dt = datetime.now(timezone.utc)
                if entry.get("published_parsed"):
                    try:
                        entry_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        ts = entry_dt.isoformat()
                    except Exception:
                        pass
                elif entry.get("updated_parsed"):
                    try:
                        entry_dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                        ts = entry_dt.isoformat()
                    except Exception:
                        pass

                # 仅保留前一日内容
                if entry_dt < cutoff:
                    continue

                # 提取作者
                author = entry.get("author", "")
                if not author and entry.get("authors"):
                    author = entry.authors[0].get("name", "")

                # 提取标签
                tags = []
                if entry.get("tags"):
                    for tag in entry.tags:
                        tag_name = tag.get("term", "")
                        if tag_name:
                            tags.append(tag_name)

                item_id = link or title
                hot_item = HotItem(
                    id=self._make_id(name, item_id[:80]) if item_id else self._make_id(name, str(hash(title))),
                    title=title,
                    url=link,
                    source=name,
                    source_type="rss",
                    timestamp=ts,
                    summary=summary[:500],
                    author=author,
                    tags=tags,
                    score=5.0,
                    popularity={"source": name},
                )
                items.append(hot_item)
            except Exception as e:
                print(f"  [RSS {name}] 跳过一条: {e}")
                continue

        return items
