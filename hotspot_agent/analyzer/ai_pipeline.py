"""
AI分析管道 - 综合分析器，协调所有分析步骤
生成结构化的分析提示，供AI进行深度分析
"""

import json
import math
from datetime import datetime
from collections import defaultdict
from .base_module import BaseAnalyzer, AnalysisResult
from .deduplicator import Deduplicator


class AIPipeline(BaseAnalyzer):
    """AI分析管道 - 串联所有分析步骤"""

    # 数据源领域权重：科技/AI/金融类源获得更高权重
    SOURCE_DOMAIN_WEIGHTS = {
        # 科技/AI 源 - 高权重
        "Hacker News": 1.4,
        "Ars Technica": 1.3,
        "TechCrunch": 1.3,
        "The Verge": 1.2,
        "Wired": 1.2,
        "VentureBeat": 1.2,
        "GitHub Trending": 1.3,
        "InfoQ 中文": 1.2,
        "少数派": 1.2,
        "机器之心": 1.3,
        "36氪": 1.2,
        "虎嗅": 1.2,
        # 金融/商业源 - 中等偏高权重
        "金融/商业": 1.1,
        # 社交/聚合源 - 降权（内容偏向社会民生）
        "微博热搜": 0.65,
        "百度热搜": 0.55,
        "Reddit": 1.0,
        "知乎热榜": 0.8,
    }

    TOPIC_KEYWORDS = {
        "AI/机器学习": ["ai", "machine learning", "llm", "gpt", "claude", "model", "人工智能", "模型", "算法",
                         "智能", "agent", "openai", "meta", "deepseek", "大模型", "机器学习", "深度学习",
                         "neural", "transformer", "llama", "mistral", "gemini", "copilot", "chatgpt"],
        "科技/互联网": ["tech", "互联网", "app", "ios", "android", "手机", "芯片", "google", "apple",
                         "microsoft", "rust", "python", "sql", "linux", "github", "半导体", "云计算",
                         "saas", "api", "开源", "自动驾驶", "新能源汽车", "电动车", "电动化"],
        "金融/投资": ["股票", "金融", "投资", "融资", "ipo", "美元", "人民币", "银行", "利率", "收购",
                       "经济", "基金", "a股", "港股", "美股", "crypto", "bitcoin", "区块链", "web3",
                       "风投", "vc", "pe", "估值", "上市", "财报", "营收"],
        "安全/隐私": ["安全", "隐私", "漏洞", "攻击", "泄露", "黑客", "cve", "网络安全", "数据安全",
                       "加密", "零信任"],
        "科学/研究": ["科学", "研究", "论文", "天文", "物理", "量子", "生物", "基因", "crispr",
                       "nasa", "spacex", "太空", "核聚变"],
    }

    def __init__(self, config: dict):
        super().__init__(config)
        analysis_config = config.get("analysis", {})
        self.deduplicator = Deduplicator(analysis_config)
        self.categories = analysis_config.get("categories", [])
        self.max_items = config.get("report", {}).get("max_topics", 20)

    def _classify_topic(self, title: str) -> str:
        """基于关键词快速分类"""
        title_lower = title.lower()
        scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in title_lower)
            if score > 0:
                scores[topic] = score
        if scores:
            return max(scores, key=scores.get)
        return "其他"

    def _apply_domain_boost(self, items: list) -> list:
        """对科技/AI/金融领域的热点进行评分加权提升"""
        for item in items:
            weight = self.SOURCE_DOMAIN_WEIGHTS.get(item.source, 1.0)

            # 额外检查：如果来自社交源但标题明显是科技话题，适当恢复权重
            if weight < 1.0:
                topic = self._classify_topic(item.title)
                if topic in ("AI/机器学习", "科技/互联网", "金融/投资"):
                    weight = 1.0  # 恢复为正常权重

            item.score = round(item.score * weight, 1)
        return items

    def _normalize_scores(self, items: list) -> list:
        """跨数据源评分归一化，使不同来源的分数可比较"""
        if not items:
            return items

        # 按 source 分组
        groups = defaultdict(list)
        for item in items:
            groups[item.source].append(item)

        for source, group in groups.items():
            scores = [item.score for item in group]
            min_s = min(scores)
            max_s = max(scores)

            if max_s == min_s:
                # 所有同分，给一个中等归一化分数
                for item in group:
                    item.score = 50.0
            else:
                # Min-Max 归一化到 0-100
                for item in group:
                    item.score = round((item.score - min_s) / (max_s - min_s) * 100, 1)

        return items

    def run_pipeline(self, items: list) -> tuple[list, dict, str]:
        """
        运行完整分析管道
        返回: (分析后的items, 统计信息, AI分析提示)
        """
        stats = {}

        # Step 1: 去重合并
        print("\n[分析] 步骤1: 去重与合并...")
        dedup_result = self.deduplicator.analyze(items)
        deduped_items = dedup_result.items
        stats["dedup"] = dedup_result.stats
        print(f"  -> 原始: {dedup_result.stats.get('total', 0)}, "
              f"去重后: {dedup_result.stats.get('final_count', 0)}")

        # Step 2: 跨源评分归一化
        print("[分析] 步骤2: 评分归一化...")
        deduped_items = self._normalize_scores(deduped_items)

        # Step 2.5: 领域加权（科技/AI/金融优先）
        print("[分析] 步骤2.5: 领域加权（科技/AI/金融优先）...")
        deduped_items = self._apply_domain_boost(deduped_items)

        # Step 3: 按分数排序取Top
        deduped_items.sort(key=lambda x: x.score, reverse=True)
        top_items = deduped_items[:self.max_items]
        stats["final_count"] = len(top_items)
        print(f"  -> Top {len(top_items)} 热点, 最高分: {top_items[0].score if top_items else 0}")

        # Step 4: 准备AI分析提示
        print("[分析] 步骤3: 生成AI分析提示...")
        ai_prompt = self._generate_ai_prompt(top_items, stats)

        return top_items, stats, ai_prompt

    def _generate_ai_prompt(self, items: list, stats: dict) -> str:
        """生成AI分析的系统提示词"""
        data = self.prepare_ai_input(items, max_items=self.max_items)

        prompt = f"""# 热点发现与分析任务

## 原始数据概览
- 采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 去重前条目数: {stats.get('dedup', {}).get('total', 0)}
- 发现重复: {stats.get('dedup', {}).get('duplicates_found', 0)}条
- 合并组数: {stats.get('dedup', {}).get('merged_groups', 0)}组
- 最终热点数: {stats.get('final_count', 0)}

## 热点数据

```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```

## 请完成以下分析任务：

### 1. AI总结热点 (每个热点50-100字)
对每个热点进行简短精炼的总结，抓住核心要点。

### 2. 生成内容标签 (每个热点2-5个标签)
为每个热点生成贴切的内容标签，标签应精炼准确、能概括内容核心。标签要求：
- 每个标签2-6个字，中文优先，专有名词可用英文
- 必须贴合热点实际内容，不要照搬数据源的原始标签
- 优先使用领域术语（如"端侧AI"、"新能源汽车"、"量化交易"）
- 示例：Muse Glimmer → ["端侧AI", "Meta", "大模型", "Agent"]
- 示例：7月销量 → ["新能源汽车", "电动化", "市场数据"]

### 3. 分类
为每个热点分配一个或多个分类标签:
- 分类选项: {', '.join(self.categories)}

### 4. 价值评估 (1-10分)
评估每个热点的传播价值和关注价值，说明理由:
- 8-10分: 重大事件，行业影响深远
- 5-7分: 有一定关注度，值得了解
- 1-4分: 小众话题或时效性弱

### 5. 可信度评估 (1-10分)  
评估信息的可信程度，说明理由:
- 8-10分: 官方来源/多方验证
- 5-7分: 知名媒体/有一定可信度
- 1-4分: 来源不明/信息不全

### 6. 识别不同观点
对存在争议的话题，总结不同立场和观点。

### 7. 综合趋势分析
基于所有热点，总结今日的核心趋势和值得关注的方向。

请以结构化JSON格式输出分析结果，每个热点的分析格式如下：
```json
{{
  "index": 1,
  "ai_summary": "...",
  "tags": ["标签1", "标签2", "标签3"],
  "category": "...",
  "value_score": 8,
  "value_reason": "...",
  "credibility_score": 7,
  "credibility_reason": "...",
  "viewpoints": ["观点1", "观点2"],
  "trend_analysis": "..."
}}
```
"""
        return prompt
