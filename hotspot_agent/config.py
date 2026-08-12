"""
热点发现Agent - 配置管理
"""

import os
import json

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# 默认配置
DEFAULT_CONFIG = {
    "sources": {
        "github": {
            "enabled": True,
            "language": "",
            "since": "daily",  # daily, weekly, monthly
            "max_items": 20,
        },
        "reddit": {
            "enabled": True,
            "subreddits": [
                "technology",
                "artificial",
                "MachineLearning",
                "stocks",
                "investing",
                "worldnews",
                "science",
            ],
            "max_items_per_sub": 15,
            "time_filter": "day",  # hour, day, week, month, year, all
        },
        "hackernews": {
            "enabled": True,
            "max_items": 30,
        },
        "rss_feeds": {
            "enabled": True,
            "feeds": [
                {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
                {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
                {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
                {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
                {"name": "VentureBeat", "url": "https://venturebeat.com/feed/"},
                {"name": "36氪", "url": "https://36kr.com/feed"},
                {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
                {"name": "InfoQ 中文", "url": "https://www.infoq.cn/feed"},
                {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0.xml"},
                {"name": "少数派", "url": "https://sspai.com/feed"},
            ],
            "max_items_per_feed": 15,
        },
        "weibo": {
            "enabled": True,
            "max_items": 30,
        },
        "zhihu": {
            "enabled": True,
            "max_items": 30,
        },
        "baidu": {
            "enabled": True,
            "max_items": 30,
        },
    },
    "analysis": {
        "dedup_threshold": 0.65,       # 去重相似度阈值
        "min_credibility_score": 3,    # 最低可信度评分 (1-10)
        "categories": [
            "AI/机器学习",
            "科技/互联网",
            "金融/投资",
            "政策/监管",
            "科学/研究",
            "安全/隐私",
            "创业/商业",
            "其他",
        ],
    },
    "report": {
        "format": "html",              # html, markdown
        "max_topics": 20,              # 报告中最多包含的热点数量
        "include_raw_data": False,
        "output_dir": DATA_DIR,
    },
    "email": {
        "enabled": False,
        "recipients": [],
        "subject_prefix": "[热点日报]",
    },
}


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        return _deep_merge(DEFAULT_CONFIG, user_config)
    return DEFAULT_CONFIG


def save_config(config):
    """保存配置文件"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _deep_merge(base, override):
    """深度合并两个字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
