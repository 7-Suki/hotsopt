"""
RSS 数据源采集器
支持多个 RSS 订阅源的聚合采集
"""

import re
import requests
from datetime import datetime, timezone
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
        """解析单个RSS/Atom源"""
        import xml.etree.ElementTree as ET

        headers = {
            "User-Agent": "HotspotAgent/1.0 (RSS Reader; contact@example.com)",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        content = resp.text
        root = ET.fromstring(content)

        items = []

        # 判断是 RSS 2.0 还是 Atom
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # Atom 格式
        atom_entries = root.findall("atom:entry", ns) or root.findall("entry")
        if atom_entries:
            for entry in atom_entries:
                item = self._parse_atom_entry(name, entry, ns)
                if item:
                    items.append(item)
        else:
            # RSS 2.0 格式
            for entry in root.iter("item"):
                item = self._parse_rss_item(name, entry)
                if item:
                    items.append(item)

        return items

    def _parse_atom_entry(self, name: str, entry, ns: dict) -> HotItem:
        """解析Atom格式条目"""
        try:
            title_el = entry.find("atom:title", ns) or entry.find("title")
            title = title_el.text if title_el is not None else ""

            link_el = entry.find("atom:link", ns) or entry.find("link")
            link = ""
            if link_el is not None:
                link = link_el.get("href", "") or link_el.text or ""

            summary_el = (
                entry.find("atom:summary", ns)
                or entry.find("summary")
                or entry.find("atom:content", ns)
                or entry.find("content")
            )
            summary = self._clean_html(summary_el.text) if summary_el is not None and summary_el.text else ""

            updated_el = entry.find("atom:updated", ns) or entry.find("updated")
            ts = datetime.now(timezone.utc).isoformat()
            if updated_el is not None and updated_el.text:
                try:
                    ts = parsedate_to_datetime(updated_el.text).isoformat()
                except Exception:
                    pass

            # 分类标签
            tags = []
            for cat_el in entry.findall("atom:category", ns) or entry.findall("category"):
                term = cat_el.get("term", "")
                if term:
                    tags.append(term)

            item_id = link or title

            return HotItem(
                id=self._make_id(name, item_id[:80]) if item_id else self._make_id(name, str(hash(title))),
                title=title,
                url=link,
                source=name,
                source_type="rss",
                timestamp=ts,
                summary=summary[:500],
                author="",
                tags=tags,
                score=5.0,
                popularity={"source": name},
            )

        except Exception:
            return None

    def _parse_rss_item(self, name: str, entry) -> HotItem:
        """解析RSS 2.0格式条目"""
        try:
            title = entry.find("title")
            title_text = title.text if title is not None else ""

            link = entry.find("link")
            link_text = link.text if link is not None else ""

            desc = entry.find("description")
            desc_text = self._clean_html(desc.text) if desc is not None and desc.text else ""

            pub_date = entry.find("pubDate")
            ts = datetime.now(timezone.utc).isoformat()
            if pub_date is not None and pub_date.text:
                try:
                    ts = parsedate_to_datetime(pub_date.text).isoformat()
                except Exception:
                    pass

            # 分类
            tags = []
            for cat in entry.findall("category"):
                if cat.text:
                    tags.append(cat.text)

            item_id = link_text or title_text

            return HotItem(
                id=self._make_id(name, item_id[:80]) if item_id else self._make_id(name, str(hash(title_text))),
                title=title_text,
                url=link_text,
                source=name,
                source_type="rss",
                timestamp=ts,
                summary=desc_text[:500],
                author="",
                tags=tags,
                score=5.0,
                popularity={"source": name},
            )

        except Exception:
            return None
