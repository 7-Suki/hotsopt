"""
知乎热榜 数据源采集器
通过知乎公开 API 获取实时热榜
"""

import requests
from datetime import datetime, timezone
from .base import BaseSource, HotItem


class ZhihuSource(BaseSource):
    """知乎热榜采集器"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "zhihu"
        self.max_items = config.get("max_items", 50)

    def fetch(self) -> list[HotItem]:
        if not self.enabled:
            return []

        results = []
        try:
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            params = {"limit": min(self.max_items, 50), "desktop": "true"}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            items = data.get("data", [])

            for i, item in enumerate(items):
                try:
                    target = item.get("target", {})
                    title = target.get("title", "")
                    if not title:
                        continue

                    qid = target.get("id", "")
                    excerpt = target.get("excerpt", "")
                    answer_count = target.get("answer_count", 0)
                    follower_count = target.get("follower_count", 0)
                    comment_count = target.get("comment_count", 0)
                    detail_text = item.get("detail_text", "")

                    # 热度评分
                    score = float(answer_count) * 0.3 + float(follower_count) * 0.5 + float(comment_count) * 0.2
                    score = min(score, 10000)

                    tags = self._extract_tags(target)

                    hot_item = HotItem(
                        id=self._make_id("hot", str(qid)[:40]),
                        title=title,
                        url=f"https://www.zhihu.com/question/{qid}" if qid else "",
                        source="知乎热榜",
                        source_type="zhihu",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        summary=excerpt or detail_text or f"知乎热榜第{i+1}位",
                        author="",
                        tags=tags,
                        score=score,
                        popularity={
                            "rank": i + 1,
                            "answer_count": answer_count,
                            "follower_count": follower_count,
                            "comment_count": comment_count,
                        },
                    )
                    results.append(hot_item)

                except Exception:
                    continue

        except Exception as e:
            print(f"[知乎] 采集失败: {e}")

        return results

    def _extract_tags(self, target: dict) -> list:
        tags = []
        for tag in target.get("topics", [])[:5]:
            if isinstance(tag, dict) and tag.get("name"):
                tags.append(tag["name"])
        return tags
