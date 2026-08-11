"""
Reddit 数据源采集器
通过 Reddit JSON API 获取热门帖子
"""

import requests
from datetime import datetime, timezone
from .base import BaseSource, HotItem


class RedditSource(BaseSource):
    """Reddit 热门帖子采集器"""

    BASE_URL = "https://www.reddit.com"

    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "reddit"
        self.subreddits = config.get("subreddits", ["technology"])
        self.max_items = config.get("max_items_per_sub", 15)
        self.time_filter = config.get("time_filter", "day")

    def fetch(self) -> list[HotItem]:
        if not self.enabled:
            return []

        results = []
        headers = {
            "User-Agent": "HotspotAgent/1.0 (research bot; contact@example.com)",
        }

        for sub in self.subreddits:
            try:
                url = f"{self.BASE_URL}/r/{sub}/hot.json"
                params = {
                    "limit": self.max_items,
                    "t": self.time_filter,
                }
                resp = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()

                posts = data.get("data", {}).get("children", [])
                for post_data in posts:
                    try:
                        post = post_data["data"]
                        created_utc = post.get("created_utc", 0)
                        ts = datetime.fromtimestamp(created_utc, tz=timezone.utc).isoformat()

                        flair = post.get("link_flair_text", "")
                        tags = [sub]
                        if flair:
                            tags.append(flair)

                        score_val = post.get("score", 0)
                        num_comments = post.get("num_comments", 0)

                        item = HotItem(
                            id=self._make_id(sub, post["id"]),
                            title=post["title"],
                            url=f"{self.BASE_URL}{post['permalink']}",
                            source=f"Reddit r/{sub}",
                            source_type="reddit",
                            timestamp=ts,
                            summary=post.get("selftext", "")[:500],
                            author=post.get("author", ""),
                            tags=tags,
                            score=score_val * 1.0 + num_comments * 2.0,
                            popularity={
                                "upvotes": score_val,
                                "comments": num_comments,
                                "upvote_ratio": post.get("upvote_ratio", 0),
                                "subreddit": sub,
                            },
                        )
                        results.append(item)

                    except Exception:
                        continue

            except Exception as e:
                print(f"[Reddit r/{sub}] 采集失败: {e}")

        return results
