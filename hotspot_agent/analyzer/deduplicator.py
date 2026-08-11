"""
去重合并模块 - 识别重复信息，合并同一事件的不同报道
"""

import re
from collections import defaultdict
from .base_module import BaseAnalyzer, AnalysisResult


class Deduplicator(BaseAnalyzer):
    """重复检测与合并"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.threshold = config.get("dedup_threshold", 0.65)

    def analyze(self, items: list) -> AnalysisResult:
        """检测并标记重复条目"""
        n = len(items)
        if n <= 1:
            return AnalysisResult(
                items=items,
                stats={"total": n, "duplicates_found": 0, "merged_groups": 0},
            )

        # 构建相似度矩阵
        to_merge = []  # [(i, j, similarity)]
        for i in range(n):
            if items[i].is_duplicate:
                continue
            for j in range(i + 1, n):
                if items[j].is_duplicate:
                    continue
                sim = self._calculate_similarity(items[i], items[j])
                if sim >= self.threshold:
                    to_merge.append((i, j, sim))

        # 使用 Union-Find 合并
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[py] = px

        for i, j, _ in to_merge:
            union(i, j)

        # 按组归类
        groups = defaultdict(list)
        for idx in range(n):
            root = find(idx)
            groups[root].append(idx)

        # 合并每组
        merged_items = []
        merged_count = 0
        duplicate_count = 0

        processed = set()
        for root, indices in sorted(groups.items()):
            if root in processed:
                continue
            processed.add(root)

            if len(indices) == 1:
                merged_items.append(items[indices[0]])
            else:
                merged_count += 1
                duplicate_count += len(indices) - 1
                primary = self._merge_group([items[i] for i in indices])
                merged_items.append(primary)

        # 按分数排序
        merged_items.sort(key=lambda x: x.score, reverse=True)

        return AnalysisResult(
            items=merged_items,
            stats={
                "total": n,
                "duplicates_found": duplicate_count,
                "merged_groups": merged_count,
                "final_count": len(merged_items),
            },
        )

    def _calculate_similarity(self, item1, item2) -> float:
        """计算两个条目的文本相似度（基于TF-like词袋模型）"""
        text1 = f"{item1.title} {item1.summary}"
        text2 = f"{item2.title} {item2.summary}"

        # 分词（简单实现：按非字母数字字符分割）
        def tokenize(text):
            # 中文按字符，英文按词
            tokens = []
            # 提取中文
            chinese = re.findall(r"[\u4e00-\u9fff]+", text.lower())
            for phrase in chinese:
                tokens.extend(list(phrase))
            # 提取英文
            english = re.findall(r"[a-zA-Z]+", text.lower())
            tokens.extend(english)
            return tokens

        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)

        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard 相似度
        set1 = set(tokens1)
        set2 = set(tokens2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        jaccard = intersection / union if union > 0 else 0.0

        # 标题重叠加分
        title_tokens1 = set(tokenize(item1.title))
        title_tokens2 = set(tokenize(item2.title))
        title_union = len(title_tokens1 | title_tokens2)
        title_overlap = (
            len(title_tokens1 & title_tokens2) / title_union
            if title_union > 0
            else 0.0
        )

        # 加权组合
        return jaccard * 0.6 + title_overlap * 0.4

    def _merge_group(self, group: list) -> object:
        """合并一组相似条目，保留最有信息量的作为主条目"""
        # 选择分数最高的作为主条目
        primary = max(group, key=lambda x: x.score)

        # 合并信息
        all_sources = []
        all_summaries = []
        merged_ids = []

        for item in group:
            if item is not primary:
                merged_ids.append(item.id)
                all_sources.append(item.source)
                if item.summary and item.summary not in primary.summary:
                    all_summaries.append(item.summary)
                item.is_duplicate = True

        # 更新主条目
        if all_sources:
            primary.source += f" (+{len(all_sources)}个来源: {', '.join(all_sources[:3])}{'...' if len(all_sources) > 3 else ''})"
        primary.merged_from = merged_ids

        # 合并热度指标
        for item in group:
            if item is not primary:
                for k, v in item.popularity.items():
                    if k in primary.popularity and isinstance(v, (int, float)):
                        primary.popularity[k] = max(primary.popularity[k], v)

        return primary
