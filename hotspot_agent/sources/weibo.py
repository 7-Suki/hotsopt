"""
微博热搜 数据源采集器
通过微博公开接口获取实时热搜榜单
"""

import requests
import json
from datetime import datetime, timezone
from .base import BaseSource, HotItem


class WeiboSource(BaseSource):
    """微博热搜采集器"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "weibo"
        self.max_items = config.get("max_items", 50)

    def fetch(self) -> list[HotItem]:
        if not self.enabled:
            return []

        results = []
        try:
            # 微博热搜 API
            url = "https://weibo.com/ajax/side/hotSearch"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://weibo.com/",
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            realtime = data.get("data", {}).get("realtime", [])

            for i, item in enumerate(realtime[:self.max_items]):
                try:
                    word = item.get("word", "")
                    if not word:
                        continue
                    raw_hot = item.get("raw_hot", 0) or item.get("num", 0)
                    category = item.get("category", "")

                    tags = []
                    if category:
                        tags.append(category)
                    if item.get("label_name"):
                        tags.append(item.get("label_name", ""))

                    # 评分：基于热搜指数
                    score = float(raw_hot) if raw_hot else 10.0 - i * 0.1

                    hot_item = HotItem(
                        id=self._make_id("hotsearch", str(i), word[:30]),
                        title=word,
                        url=f"https://s.weibo.com/weibo?q={requests.utils.quote(word)}",
                        source="微博热搜",
                        source_type="weibo",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        summary=f"微博热搜第{i+1}位" + (f" [{category}]" if category else ""),
                        author="",
                        tags=tags,
                        score=score,
                        popularity={
                            "rank": i + 1,
                            "raw_hot": raw_hot,
                            "category": category,
                        },
                    )
                    results.append(hot_item)

                except Exception:
                    continue

        except Exception as e:
            print(f"[微博] 采集失败: {e}")

        return results
