"""
GitHub Trending 数据源采集器
通过 GitHub 公开页面获取 Trending 仓库信息
"""

import requests
import re
from datetime import datetime, timezone, timedelta
from .base import BaseSource, HotItem


class GitHubSource(BaseSource):
    """GitHub Trending 采集器"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "github"
        self.max_items = config.get("max_items", 20)
        self.language = config.get("language", "")
        self.since = config.get("since", "daily")

    def fetch(self) -> list[HotItem]:
        if not self.enabled:
            return []

        results = []
        try:
            lang_path = f"/{self.language}" if self.language else ""
            url = f"https://github.com/trending{lang_path}?since={self.since}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text

            # 提取仓库信息
            repo_blocks = re.findall(
                r'<article class="Box-row">(.*?)</article>',
                html,
                re.DOTALL,
            )

            for i, block in enumerate(repo_blocks[:self.max_items]):
                try:
                    # 仓库名 - 匹配真实仓库(非sponsors/非explore)
                    repo_match = re.search(r'<a href="/([^s][^/"]+/[^/"]+)"', block)
                    repo_full = repo_match.group(1) if repo_match else ""
                    # 跳过无效的仓库名
                    if not repo_full or repo_full.startswith("sponsors/") or "/" not in repo_full:
                        continue

                    # 描述
                    desc_match = re.search(
                        r'<p class="col-9 color-fg-muted[^"]*">\s*(.*?)\s*</p>',
                        block,
                        re.DOTALL,
                    )
                    description = desc_match.group(1).strip() if desc_match else ""
                    description = re.sub(r"<[^>]+>", "", description)

                    # 语言
                    lang_match = re.search(
                        r'<span itemprop="programmingLanguage">\s*(.*?)\s*</span>',
                        block,
                    )
                    language = lang_match.group(1).strip() if lang_match else ""

                    # Stars 和 Forks
                    stars_match = re.search(
                        r'(\d[\d,]*)\s*stars today',
                        block,
                        re.IGNORECASE,
                    )
                    stars_today = (
                        stars_match.group(1).replace(",", "")
                        if stars_match
                        else "0"
                    )

                    forks_match = re.search(
                        r'(\d[\d,]*)\s*forks today',
                        block,
                        re.IGNORECASE,
                    )
                    forks_today = (
                        forks_match.group(1).replace(",", "")
                        if forks_match
                        else "0"
                    )

                    item = HotItem(
                        id=self._make_id(repo_full, self.since),
                        title=f"[GitHub Trending] {repo_full}",
                        url=f"https://github.com/{repo_full}",
                        source="GitHub Trending",
                        source_type="github",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        summary=description,
                        author=repo_full.split("/")[0] if "/" in repo_full else "",
                        tags=[language] if language else [],
                        score=float(stars_today) * 1.0 + float(forks_today) * 0.5,
                        popularity={
                            "stars_today": int(stars_today),
                            "forks_today": int(forks_today),
                            "language": language,
                            "since": self.since,
                        },
                    )
                    results.append(item)

                except Exception:
                    continue

        except Exception as e:
            print(f"[GitHub] 采集失败: {e}")

        return results
