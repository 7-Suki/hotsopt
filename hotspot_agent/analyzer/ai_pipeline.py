"""
AI分析管道 - 综合分析器，协调所有分析步骤
生成结构化的分析提示，供AI进行深度分析
"""

import json
from datetime import datetime
from .base_module import BaseAnalyzer, AnalysisResult
from .deduplicator import Deduplicator


class AIPipeline(BaseAnalyzer):
    """AI分析管道 - 串联所有分析步骤"""

    def __init__(self, config: dict):
        super().__init__(config)
        analysis_config = config.get("analysis", {})
        self.deduplicator = Deduplicator(analysis_config)
        self.categories = analysis_config.get("categories", [])
        self.max_items = config.get("report", {}).get("max_topics", 20)

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

        # Step 2: 按分数排序取Top
        deduped_items.sort(key=lambda x: x.score, reverse=True)
        top_items = deduped_items[:self.max_items]
        stats["final_count"] = len(top_items)

        # Step 3: 准备AI分析提示
        print("[分析] 步骤2: 生成AI分析提示...")
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

### 2. 分类与标签
为每个热点分配一个或多个分类标签:
- 分类选项: {', '.join(self.categories)}

### 3. 价值评估 (1-10分)
评估每个热点的传播价值和关注价值，说明理由:
- 8-10分: 重大事件，行业影响深远
- 5-7分: 有一定关注度，值得了解
- 1-4分: 小众话题或时效性弱

### 4. 可信度评估 (1-10分)  
评估信息的可信程度，说明理由:
- 8-10分: 官方来源/多方验证
- 5-7分: 知名媒体/有一定可信度
- 1-4分: 来源不明/信息不全

### 5. 识别不同观点
对存在争议的话题，总结不同立场和观点。

### 6. 综合趋势分析
基于所有热点，总结今日的核心趋势和值得关注的方向。

请以结构化JSON格式输出分析结果，每个热点的分析格式如下：
```json
{{
  "index": 1,
  "ai_summary": "...",
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
