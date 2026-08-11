"""
Hacker News 数据源采集器
通过 HN 官方 Firebase API 获取热门文章
"""

import requests
import asyncio
from datetime import datetime, timezone
from .base import BaseSource, HotItem


class HackerNewsSource(BaseSource):
    """Hacker News 采集器"""

    TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "hackernews"
        self.max_items = config.get("max_items", 30)

    def fetch(self) -> list[HotItem]:
        if not self.enabled:
            return []

        results = []
        try:
            # 获取热门文章 ID 列表
            resp = requests.get(self.TOP_STORIES_URL, timeout=10)
            resp.raise_for_status()
            story_ids = resp.json()

            # 批量获取文章详情
            for story_id in story_ids[: self.max_items]:
                try:
                    item_resp = requests.get(
                        self.ITEM_URL.format(story_id),
                        timeout=10,
                    )
                    item_resp.raise_for_status()
                    story = item_resp.json()

                    if not story or story.get("type") != "story":
                        continue

                    ts = datetime.fromtimestamp(
                        story.get("time", 0),
                        tz=timezone.utc,
                    ).isoformat()

                    item = HotItem(
                        id=self._make_id(str(story_id)),
                        title=story.get("title", ""),
                        url=story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        source="Hacker News",
                        source_type="hackernews",
                        timestamp=ts,
                        summary=story.get("text", "")[:500] if story.get("text") else "",
                        author=story.get("by", ""),
                        tags=["tech", "startups"],
                        score=story.get("score", 0),
                        popularity={
                            "upvotes": story.get("score", 0),
                            "comments": story.get("descendants", 0),
                        },
                    )
                    results.append(item)

                except Exception:
                    continue

        except Exception as e:
            print(f"[HackerNews] 采集失败: {e}")

        return results
