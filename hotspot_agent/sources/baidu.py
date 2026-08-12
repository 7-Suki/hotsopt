"""
百度热搜 数据源采集器
通过百度热搜公开接口获取实时热搜榜单
"""

import requests
import json
from datetime import datetime, timezone
from .base import BaseSource, HotItem


class BaiduSource(BaseSource):
    """百度热搜采集器"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "baidu"
        self.max_items = config.get("max_items", 50)

    def fetch(self) -> list[HotItem]:
        if not self.enabled:
            return []

        results = []
        try:
            # 百度热搜 API
            url = "https://top.baidu.com/board?tab=realtime"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text

            # 从 HTML 中提取热搜数据
            import re
            # 匹配热搜卡片数据
            pattern = r'<!--s-data:({.*?})-->'
            match = re.search(pattern, html)
            if not match:
                # 尝试另一种模式
                data_match = re.search(r'"cards":\s*(\[.*?\])', html)
                if data_match:
                    cards_str = data_match.group(1)
                    cards = json.loads(cards_str)
                    return self._parse_cards(cards)

            if match:
                try:
                    data = json.loads(match.group(1))
                    cards = data.get("data", {}).get("cards", [])
                    return self._parse_cards(cards)
                except json.JSONDecodeError:
                    pass

            # 备用方案：直接搜索抓取热榜
            return self._fallback_fetch()

        except Exception as e:
            print(f"[百度] 主接口采集失败: {e}，尝试备用方案")
            return self._fallback_fetch()

        return results

    def _parse_cards(self, cards: list) -> list[HotItem]:
        results = []
        idx = 0

        for card in cards:
            content_list = card.get("content", [])
            if not isinstance(content_list, list):
                content_list = []

            for item in content_list:
                if idx >= self.max_items:
                    break
                try:
                    word = item.get("word", "") or item.get("query", "")
                    if not word:
                        continue

                    desc = item.get("desc", "")
                    hot_score = item.get("hotScore", 0) or item.get("score", 0)
                    is_hot = item.get("isHot", False)
                    url = item.get("url", "") or item.get("rawUrl", "")

                    tags = []
                    if is_hot:
                        tags.append("热门")

                    score = float(hot_score) if hot_score else 50.0 - idx * 1.0

                    hot_item = HotItem(
                        id=self._make_id("hot", str(idx), word[:30]),
                        title=word,
                        url=url or f"https://www.baidu.com/s?wd={requests.utils.quote(word)}",
                        source="百度热搜",
                        source_type="baidu",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        summary=desc or f"百度实时热搜第{idx+1}位",
                        author="",
                        tags=tags,
                        score=score,
                        popularity={
                            "rank": idx + 1,
                            "hot_score": hot_score,
                            "is_hot": is_hot,
                        },
                    )
                    results.append(hot_item)
                    idx += 1

                except Exception:
                    continue

        return results

    def _fallback_fetch(self) -> list[HotItem]:
        """备用采集方案：抓取热搜趋势页"""
        results = []
        try:
            url = "https://www.baidu.com/s?tn=news&word=%E7%83%AD%E6%90%9C"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text

            import re
            # 尝试提取热搜关键词
            hot_matches = re.findall(r'<a[^>]*>([^<]{2,40})</a>', html)
            seen = set()
            idx = 0
            for m in hot_matches:
                m = m.strip()
                if m in seen or len(m) < 2 or "百度" in m or "搜索" in m:
                    continue
                if idx >= self.max_items:
                    break
                seen.add(m)
                results.append(HotItem(
                    id=self._make_id("fallback", str(idx), m[:20]),
                    title=m,
                    url=f"https://www.baidu.com/s?wd={requests.utils.quote(m)}",
                    source="百度搜索",
                    source_type="baidu_fallback",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    summary="",
                    author="",
                    tags=[],
                    score=30.0 - idx * 1.0,
                    popularity={"rank": idx + 1},
                ))
                idx += 1

        except Exception as e:
            print(f"[百度] 备用方案也失败: {e}")

        return results
