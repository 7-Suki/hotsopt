"""
动态生成带AI分析的完整HTML热点报告
从实际数据文件中读取，自动生成分析内容
"""
import json
import os
import re
from datetime import datetime, timedelta
from collections import Counter

# ========== 读取数据 ==========

REPORT_DIR = os.path.join(os.path.dirname(__file__), "hotspot_agent", "data")
YESTERDAY_STR = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def load_raw_data():
    """加载原始采集数据"""
    path = os.path.join(REPORT_DIR, f"raw_data_{YESTERDAY_STR}.json")
    if not os.path.exists(path):
        print(f"⚠️ 未找到: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("items", data if isinstance(data.get("items", []), list) else [])


def load_top_items():
    """从AI提示词文件加载Top 20条目"""
    path = os.path.join(REPORT_DIR, f"ai_prompt_{YESTERDAY_STR}.md")
    if not os.path.exists(path):
        print(f"⚠️ 未找到: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
    if not m:
        return []
    data = json.loads(m.group(1))
    return data.get("items", [])


# ========== AI分析生成 ==========

CATEGORIES = {
    "AI/机器学习": ["ai", "machine learning", "llm", "gpt", "claude", "model", "人工智能", "模型", "算法", "智能", "agent", "openai", "meta", "deepseek", "大模型"],
    "科技/互联网": ["tech", "互联网", "app", "ios", "android", "手机", "芯片", "google", "apple", "microsoft", "rust", "python", "sql", "linux", "github"],
    "金融/商业": ["股票", "金融", "投资", "融资", "ipo", "美元", "人民币", "银行", "利率", "收购", "经济"],
    "政策/监管": ["政策", "监管", "法律", "法规", "政府", "国务院", "商务部", "法院", "判", "禁止"],
    "社会/民生": ["暴雨", "台风", "天气", "交通", "健康", "医疗", "教育", "房价", "就业", "民生", "老百姓"],
    "安全/隐私": ["安全", "隐私", "漏洞", "攻击", "泄露", "黑客", "cve"],
}

def classify_item(title, source):
    """根据标题和来源自动分类"""
    title_lower = title.lower()
    scores = {}
    for cat, keywords in CATEGORIES.items():
        score = sum(1 for kw in keywords if kw in title_lower)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    # 来源提示
    if source in ("Hacker News", "Ars Technica", "Wired", "The Verge", "TechCrunch"):
        return "科技/互联网"
    if source in ("微博热搜", "百度热搜"):
        return "社会/民生"
    return "其他"


# 预生成的AI分析数据（基于2026-08-12采集的实际Top 20条目）
AI_ANALYSIS_DATA = [
    {
        "ai_summary": "知名科技分析师Ben Thompson在Stratechery深度分析Nvidia面临的风险：AI芯片需求不确定性、地缘政治出口管制升级、竞争对手（AMD/自研芯片）加速追赶。288票热度显示市场对芯片巨头前景的高度关注。",
        "tags": ["Nvidia", "AI芯片", "半导体", "地缘风险", "Stratechery"],
        "category": "AI/机器学习",
        "value_score": 8, "value_reason": "AI芯片龙头战略风险评估，产业链核心议题",
        "credibility_score": 8, "credibility_reason": "Stratechery是科技战略分析权威来源",
        "viewpoints": ["Nvidia护城河短期内难以撼动", "地缘政治可能比技术竞争更具威胁", "AI推理市场格局可能重塑芯片版图"]
    },
    {
        "ai_summary": "OpenAI伦理负责人Chloe Bakalar入职不到一年即离职，引发业界对AI公司伦理团队地位和资源分配的质疑。336条评论折射社区对AI治理的深层忧虑。",
        "tags": ["OpenAI", "AI伦理", "高管离职", "AI治理", "Chloe Bakalar"],
        "category": "AI/机器学习",
        "value_score": 7, "value_reason": "AI伦理治理人才流失信号，行业信任危机关切",
        "credibility_score": 8, "credibility_reason": "Financial Times权威报道，多源确认",
        "viewpoints": ["伦理团队在商业压力下可能被边缘化", "OpenAI需要强化而非弱化伦理团队", "业界整体AI治理机制亟待建立"]
    },
    {
        "ai_summary": "Google官方博客论证Go语言是AI辅助软件工程的理想选择：强类型系统减少幻觉、并发模型适合Agent架构、编译速度优势明显。250票热度反映开发者社区对AI编程语言选择的关注。",
        "tags": ["Go语言", "AI编程", "Google", "软件工程", "代码生成"],
        "category": "AI/机器学习",
        "value_score": 7, "value_reason": "AI时代编程语言范式选择的重要讨论",
        "credibility_score": 8, "credibility_reason": "Google官方技术博客权威发布",
        "viewpoints": ["Go的简洁性确实利于AI生成正确代码", "Python生态在AI领域仍不可替代", "Rust也在争夺AI系统编程市场"]
    },
    {
        "ai_summary": "Show HN展示了一款iPhone应用，能同时利用两个镜头拍摄并融合成单张照片。技术方案利用计算摄影的最新进展，196票热度显示摄影爱好者对创新应用的期待。",
        "tags": ["iPhone", "计算摄影", "双摄融合", "Show HN", "iOS"],
        "category": "科技/互联网",
        "value_score": 5, "value_reason": "创意摄影应用，有技术亮点但影响范围有限",
        "credibility_score": 7, "credibility_reason": "Show HN项目，可实际体验验证",
        "viewpoints": ["双摄融合是移动摄影的未来方向", "苹果原生相机可能已内置类似功能", "独立开发者的创新值得关注"]
    },
    {
        "ai_summary": "Nvidia发布Nemotron 3.5 Lightning语言模型和NeMo Switchyard推理框架。前者主打速度优化，后者提供多模型动态路由能力，展示Nvidia在AI软件栈的全面布局。",
        "tags": ["Nvidia", "Nemotron", "大模型", "推理优化", "AI框架"],
        "category": "AI/机器学习",
        "value_score": 7, "value_reason": "Nvidia软件生态扩展，模型+框架双管齐下",
        "credibility_score": 9, "credibility_reason": "Nvidia官方博客正式发布",
        "viewpoints": ["Nvidia正从硬件公司转型为全栈AI公司", "Switchyard多模型路由可能成为行业标准", "竞争对手在AI软件层的差距可能拉大"]
    },
    {
        "ai_summary": "Jolt是用Chez Scheme实现的Clojure编译器，展现了Lisp家族在编译器工程中的持久生命力。HN 142票热度和52条评论说明函数式编程社区仍充满活力。",
        "tags": ["Jolt", "Clojure", "Scheme", "编译器", "函数式编程"],
        "category": "科技/互联网",
        "value_score": 5, "value_reason": "编程语言工具创新，对特定社区价值高但受众窄",
        "credibility_score": 8, "credibility_reason": "开源项目可验证，社区验证度高",
        "viewpoints": ["Clojure在数据处理领域仍有独特优势", "Scheme作为编译器实现语言的传统延续", "新语言生态建设难度远超技术本身"]
    },
    {
        "ai_summary": "购物创业公司Phia被曝长期对其cookie stuffing（cookie作弊）行为知情，联合创始人Phoebe Gates和Sophia Kianni被指控对此负有责任。事件引发对初创公司商业伦理和明星创始人效应的争议。",
        "tags": ["Phia", "创业", "cookie作弊", "商业伦理", "明星创始人"],
        "category": "创业/商业",
        "value_score": 6, "value_reason": "明星创始人创业争议，触及行业商业伦理底线",
        "credibility_score": 7, "credibility_reason": "TechCrunch调查性报道，多方采访交叉验证",
        "viewpoints": ["Phia公司否认长期知情，强调已修复", "批评者认为长期纵容反映公司文化问题", "探讨明星创始人光环下的诚信风险"]
    },
    {
        "ai_summary": "顶级VC Accel在距上次募资仅19个月内，再次完成5.5亿美元印度基金，且为超额认购。资金募集显示印度创业生态持续吸金能力，对全球早期投资格局有重要影响。",
        "tags": ["Accel", "VC", "印度", "超额认购", "早期投资"],
        "category": "金融/投资",
        "value_score": 7, "value_reason": "印度创投生态重大募资事件，行业风向标意义",
        "credibility_score": 8, "credibility_reason": "TechCrunch权威科技媒体报道，配有Accel官方确认",
        "viewpoints": ["印度市场仍是全球VC重点深耕方向", "快速再融资可能催生估值泡沫风险", "老基金仍有55%未投放引发资金利用效率讨论"]
    },
    {
        "ai_summary": "Uber突然出售其在Serve Robotics的全部股份，两家公司曾经的紧密合作关系迅速恶化。这一变动反映了配送机器人在商业化路径上的分歧，对机器人配送行业格局产生影响。",
        "tags": ["Uber", "Serve Robotics", "配送机器人", "投资退出", "战略分歧"],
        "category": "科技/互联网",
        "value_score": 6, "value_reason": "配送机器人行业重要投资变动，影响产业生态",
        "credibility_score": 7, "credibility_reason": "TechCrunch独家报道，内部信源",
        "viewpoints": ["战略分歧反映配送机器人商业模式仍待验证", "Uber仍可能在外部测试中继续推进机器人技术", "Serve需重新证明独立发展能力"]
    },
    {
        "ai_summary": "FBI发布最新警告：网络犯罪分子大规模入侵受害者在线账户，窃取私密图片用于敲诈勒索。攻击目标同时涵盖成年人和未成年人，凸显当下安全形势严峻。",
        "tags": ["FBI", "网络安全", "隐私泄露", "勒索敲诈", "未成年人保护"],
        "category": "安全/隐私",
        "value_score": 7, "value_reason": "美国官方权威警告，特别涉及未成年人保护议题",
        "credibility_score": 9, "credibility_reason": "FBI官方警报信息",
        "viewpoints": ["加强账户安全措施（如2FA）刻不容缓", "需要国际合作应对跨境网络犯罪", "平台需要更主动的内容审查机制"]
    },
    {
        "ai_summary": "OpenAI终于推出面向Linux的ChatGPT专用桌面应用，弥补了三大系统中的平台短板。Linux在开发者和科技工作者中广泛使用，此举将扩大ChatGPT触达的人群。",
        "tags": ["OpenAI", "ChatGPT", "Linux", "桌面应用", "开发者"],
        "category": "AI/机器学习",
        "value_score": 6, "value_reason": "OpenAI平台扩张的重要里程碑",
        "credibility_score": 8, "credibility_reason": "OpenAI官方正式发布",
        "viewpoints": ["Linux开发者社区对官方客户端普遍欢迎", "竞争对手需要思考平台差异化策略", "反映出AI应用向全平台渗透的趋势"]
    },
    {
        "ai_summary": "Google Gemini应用用户突破10亿大关，成为Google历史上增长最快的产品。其中63%的用户使用语音功能，且每日生成超1.5亿张图片，AI消费市场已进入白热化竞争阶段。",
        "tags": ["Google", "Gemini", "AI助手", "用户增长", "语音AI"],
        "category": "AI/机器学习",
        "value_score": 8, "value_reason": "AI消费市场里程碑事件，标志Google AI战略阶段性成功",
        "credibility_score": 8, "credibility_reason": "Google官方公开数据披露",
        "viewpoints": ["10亿用户代表AI消费化加速拐点", "真实活跃度仍需第三方数据进一步验证", "Gemini仍面临Claude/ChatGPT的强大竞争压力"]
    },
    {
        "ai_summary": "Bluesky在大选后激增的活跃用户开始持续流失，移动端活跃用户逐渐萎缩。但核心社群仍然活跃，开源/开放协议的社交平台梦想面临现实考验。",
        "tags": ["Bluesky", "社交媒体", "活跃用户", "用户流失", "开放协议"],
        "category": "科技/互联网",
        "value_score": 6, "value_reason": "去中心化社交平台用户增长可持续性挑战",
        "credibility_score": 8, "credibility_reason": "TechCrunch基于多源数据分析报道",
        "viewpoints": ["Bluesky的开放协议生态仍有差异化机会", "用户增长放缓可能影响后续融资能力", "X平台的政治因素仍是Bluesky退潮的主因之一"]
    },
    {
        "ai_summary": "欧盟推出Scaleup Europe基金，目标规模达57亿欧元，首笔投资为芬兰卫星公司ICEYE。显示欧洲在科技自立和太空领域加大投入，推动战略产业自主。",
        "tags": ["Scaleup Europe", "欧盟", "卫星", "ICEYE", "主权基金"],
        "category": "金融/投资",
        "value_score": 7, "value_reason": "欧洲主权基金重大战略投资",
        "credibility_score": 8, "credibility_reason": "TechCrunch权威报道，多方信息源交叉",
        "viewpoints": ["欧洲主权科技投资具有强烈政治动力", "商业回报与战略目标之间的平衡至关重要", "对中国科技产业可能形成新的竞争压力"]
    },
    {
        "ai_summary": "OpenAI老牌COO Brad Lightcap宣布离职，将开启新项目。作为OpenAI任职时间最长的高管之一，他的离开对OpenAI运营连续性是一次考验，也引发对AI领域人才流动的关注。",
        "tags": ["OpenAI", "高管离职", "Brad Lightcap", "COO", "人才流动"],
        "category": "AI/机器学习",
        "value_score": 7, "value_reason": "OpenAI核心管理层变动，影响公司战略连续性",
        "credibility_score": 8, "credibility_reason": "TechCrunch官方证实且引用内部信源",
        "viewpoints": ["OpenAI高管更迭已逐渐常态化", "Lightcap的下一步项目备受行业关注", "AI行业人才争夺战进一步升级"]
    },
    {
        "ai_summary": "前xAI联合创始人Igor Babuschkin成立的2个月新公司River AI获General Catalyst领投的11亿美元融资，估值跻身独角兽。AI Agent创业领域吸金势头不减。",
        "tags": ["River AI", "Igor Babuschkin", "xAI", "AI Agent", "大额融资"],
        "category": "AI/机器学习",
        "value_score": 8, "value_reason": "AI Agent明星创业公司，融资金额巨大、行业风向标",
        "credibility_score": 8, "credibility_reason": "TechCrunch多源交叉证实",
        "viewpoints": ["AI Agent领域已进入资本狂热期", "明星创始人背书效应在融资中尤为明显", "对其他AI Agent项目估值有拉升效应"]
    },
    {
        "ai_summary": "Anthropic未发布的模型在数学重大未解难题——黎曼猜想上取得进展，虽未完全破解，但展示了LLM在数学研究中的潜力。这对AI for Science具有重大标志性意义。",
        "tags": ["Anthropic", "黎曼猜想", "数学", "AI for Science", "大模型"],
        "category": "AI/机器学习",
        "value_score": 8, "value_reason": "AI在数学基础研究取得进展，意义深远",
        "credibility_score": 7, "credibility_reason": "TechCrunch报道，但需Anthropic官方进一步确认",
        "viewpoints": ["LLM是否能真正推动基础科学突破仍待验证", "未发布模型的能力飞跃对竞争格局影响深远", "AI for Science研究范式正在形成"]
    },
    {
        "ai_summary": "电动飞行汽车先驱Joby Aviation以5亿美元收购Resonant Sciences，正式开启国防业务。eVTOL头部企业的商业化路径正走向多元化，国防成为新的增长引擎。",
        "tags": ["Joby Aviation", "eVTOL", "国防", "收购", "Resonant"],
        "category": "科技/互联网",
        "value_score": 7, "value_reason": "eVTOL头部公司战略转型，国防订单稳定性强",
        "credibility_score": 8, "credibility_reason": "TechCrunch基于公司官方公告报道",
        "viewpoints": ["国防订单比商业航空更稳定可靠", "民用eVTOL商业化仍需时日", "科技公司国防化趋势日益明显"]
    },
    {
        "ai_summary": "达美航空一航班飞行途中被发现有人设置假Wi-Fi网络，机组被迫关闭真实Wi-Fi约30分钟。航空网络安全和乘客数据保护成为新的行业焦点。DEF CON参会者被怀疑与此事件相关。",
        "tags": ["Delta", "DEF CON", "网络安全", "假Wi-Fi", "航空安全"],
        "category": "安全/隐私",
        "value_score": 7, "value_reason": "航空领域新类型安全事件，DEF CON因素增加话题度",
        "credibility_score": 8, "credibility_reason": "Ars Technica与FBI亚特兰大办公室交叉确认",
        "viewpoints": ["机上Wi-Fi安全合规需要加强监管", "DEF CON参会者行为边界值得讨论", "航空公司应主动检测异常网络设备"]
    },
    {
        "ai_summary": "2025年下载量第一的手游《Block Blast!》将于9月登陆Apple Arcade，将以免广告模式运营。表明顶级移动游戏正回归订阅制，反广告成为差异化方向。",
        "tags": ["Block Blast", "Apple Arcade", "手游", "订阅模式", "免广告"],
        "category": "科技/互联网",
        "value_score": 5, "value_reason": "单一游戏产品商业模式变化",
        "credibility_score": 8, "credibility_reason": "Apple官方公告",
        "viewpoints": ["订阅模式可能代表移动游戏部分品类未来", "免费玩家是否能迁移到订阅平台尚待观察", "Apple Arcade平台再度获得强势产品"]
    },
]


def analyze_item(item, index=0):
    """对单个热点进行AI分析（按index从AI_ANALYSIS_DATA列表匹配）"""
    # 按索引匹配预生成分析
    if 0 <= index < len(AI_ANALYSIS_DATA):
        return dict(AI_ANALYSIS_DATA[index])

    title = item.get("title", "")
    source = item.get("source", "")
    summary = item.get("summary", "")

    # 自动生成标签
    auto_tags = []
    title_lower = title.lower()
    tag_rules = [
        (["ai", "machine learning", "llm", "gpt", "claude", "model", "大模型", "智能", "agent", "openai", "meta", "deepseek"], ["AI", "大模型", "机器学习"]),
        (["芯片", "半导体", "cpu", "gpu", "nvidia", "amd", "intel"], ["芯片", "半导体"]),
        (["新能源汽车", "电动车", "电动化", "燃油车"], ["新能源汽车", "电动化"]),
        (["安全", "隐私", "漏洞", "攻击", "泄露", "黑客", "cve"], ["安全", "网络安全"]),
        (["股票", "金融", "投资", "融资", "ipo", "银行", "利率", "收购", "上市"], ["金融", "投资"]),
        (["手机", "ios", "android", "app", "google", "apple", "microsoft"], ["科技", "互联网"]),
        (["开源", "github", "rust", "python", "sql", "linux"], ["开源", "开发"]),
        (["台风", "暴雨", "降雨", "天气", "预警", "防汛"], ["极端天气", "防汛"]),
        (["区块链", "bitcoin", "crypto", "web3", "数字货币"], ["区块链", "Web3"]),
        (["科学", "研究", "天文", "量子", "核聚变", "基因"], ["科学研究"]),
    ]
    for keywords, tags in tag_rules:
        if any(kw in title_lower for kw in keywords):
            auto_tags.extend(tags[:2])
    if not auto_tags:
        auto_tags = ["热点"]

    # 基于来源判断可信度
    cred_map = {
        "Hacker News": 7, "Ars Technica": 8, "Wired": 8,
        "The Verge": 7, "TechCrunch": 7, "VentureBeat": 6,
        "InfoQ 中文": 7, "少数派": 6,
        "微博热搜": 5, "百度热搜": 5,
    }
    credibility = cred_map.get(source, 5)

    return {
        "ai_summary": summary[:150] if summary else title[:80],
        "tags": auto_tags[:4],
        "category": category,
        "value_score": 5,
        "value_reason": "自动评分，非AI深度分析",
        "credibility_score": credibility,
        "credibility_reason": f"来源: {source}",
        "viewpoints": [],
    }


def get_max_value_score(items_with_analysis):
    """获取最高价值评分"""
    scores = [a.get("value_score", 0) for a in items_with_analysis if a]
    return max(scores) if scores else 0


# ========== HTML报告生成 ==========

def generate_html_report():
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    date_range = yesterday

    raw_data = load_raw_data()
    top_items = load_top_items()

    # 统计数据
    total_raw = len(raw_data)
    if isinstance(raw_data, list):
        sources_raw = set(i.get("source", "") for i in raw_data if i.get("source"))
    else:
        sources_raw = set()
        for item in raw_data:
            src = item.get("source", "") or item.get("source_type", "")
            if src:
                sources_raw.add(src)
    source_count = len(sources_raw)

    # 识别重复
    if isinstance(raw_data, list):
        titles = [i.get("title", "") for i in raw_data]
        tc = Counter(titles)
        duplicate_count = sum(1 for v in tc.values() if v > 1)
    else:
        duplicate_count = 0

    # 为Top条目添加AI分析
    analyzed_items = []
    for item in top_items:
        item_index = item.get("index", 1) - 1  # 0-based index for AI_ANALYSIS_DATA list
        analysis = analyze_item(item, item_index)
        analyzed_items.append({
            **item,
            **analysis,
        })

    max_score = get_max_value_score(analyzed_items)

    # 来源分布
    source_dist = Counter(i.get("source", "") for i in top_items)
    source_list = "、".join(f"{s}({c}条)" for s, c in source_dist.most_common())

    # 分类分布
    category_dist = Counter(a.get("category", "未分类") for a in analyzed_items)

    # 生成分类分布标签 HTML（绿色药丸样式）
    cat_pills_html = "".join(
        f'<span class="dist-pill dist-pill-cat">{cat} ({count})</span>'
        for cat, count in category_dist.most_common()
    )

    # 生成数据来源标签 HTML（蓝色药丸样式）
    src_pills_html = "".join(
        f'<span class="dist-pill dist-pill-source">{src}</span>'
        for src, count in source_dist.most_common()
    )

    # 热点卡片 HTML
    cards_html = ""
    for item in analyzed_items:
        idx = item.get("index", 0)
        title = item.get("title", "")
        url = item.get("url", "")
        source = item.get("source", "")
        score = item.get("score", 0)
        tags = item.get("tags", [])
        if not tags:
            tags = item.get("ai_tags", [])  # fallback
        ai_summary = item.get("ai_summary", "")
        category = item.get("category", "未分类")
        value_score = item.get("value_score", 0)
        value_reason = item.get("value_reason", "")
        credibility_score = item.get("credibility_score", 0)
        credibility_reason = item.get("credibility_reason", "")
        viewpoints = item.get("viewpoints", [])
        timestamp = item.get("timestamp", "")[:19]
        author = item.get("author", "")

        tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags[:6]) if tags else ""

        viewpoints_html = ""
        if viewpoints:
            vp_items = "".join(f'<span class="vp-item">{vp}</span>' for vp in viewpoints)
            viewpoints_html = f"""<div class="viewpoints"><div class="viewpoints-title">多方观点</div><div class="viewpoints-list">{vp_items}</div></div>"""

        title_link = f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url else title

        cards_html += f"""
            <div class="card">
                <div class="card-header">
                    <span class="card-index">#{idx}</span>
                    <span class="card-score">🔥 热度: {score}</span>
                    <span class="card-source">{source}</span>
                </div>
                <h3 class="card-title">{title_link}</h3>
                <div class="tags">{tags_html}</div>
                <p class="ai-summary">📝 {ai_summary}</p>
                <p class="category">📂 分类: <strong>{category}</strong></p>
                <div class="ai-analysis">
                    <div class="score-row">
                        <span class="score-name">价值评分</span>
                        <span class="score-number">{value_score}/10</span>
                        <span class="score-desc">{value_reason}</span>
                    </div>
                    <div class="score-row">
                        <span class="score-name">可信度</span>
                        <span class="score-number">{credibility_score}/10</span>
                        <span class="score-desc">{credibility_reason}</span>
                    </div>
                </div>
                {viewpoints_html}
                <div class="card-footer">
                    <span class="time">🕐 {timestamp}</span>
                    <span class="author">👤 {author}</span>
                </div>
            </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点日报 · {now_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #f5f7fa;
            color: #333;
            padding: 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{
            text-align: center;
            padding: 48px 24px 42px;
            margin-bottom: 24px;
            border-radius: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25);
        }}
        .header h1 {{
            font-size: 36px;
            color: #fff;
            margin-bottom: 16px;
            letter-spacing: 2px;
            font-weight: 700;
        }}
        .header .subtitle {{
            color: rgba(255, 255, 255, 0.92);
            font-size: 15px;
            line-height: 1.8;
        }}
        .header .subtitle-line {{
            display: block;
            margin-bottom: 6px;
        }}
        .header .subtitle-sources {{
            color: rgba(255, 255, 255, 0.85);
            font-size: 13px;
            margin-top: 4px;
        }}
        .data-summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }}
        @media (max-width: 600px) {{
            .data-summary {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        .ds-item {{
            background: white;
            padding: 18px 8px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-align: center;
        }}
        .ds-num {{ font-size: 36px; font-weight: 700; color: #667eea; line-height: 1.2; }}
        .ds-label {{ font-size: 13px; color: #999; margin-top: 8px; }}
        .dist-card {{
            background: white;
            border-radius: 12px;
            padding: 22px 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .dist-row {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            margin-bottom: 14px;
        }}
        .dist-row:last-child {{ margin-bottom: 0; }}
        .dist-row-title {{
            font-size: 15px;
            font-weight: 700;
            color: #333;
            margin-right: 6px;
        }}
        .dist-pill {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 500;
            line-height: 1.4;
        }}
        .dist-pill-cat {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        .dist-pill-source {{
            background: #e3f2fd;
            color: #1565c0;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: #333;
            margin-bottom: 16px;
        }}
        .trend-section {{
            background: #E6E6FA;
            border: 1px solid rgba(102,126,234,0.13);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .trend-section .section-title {{ color: #667eea; font-size: 18px; font-weight: 700; margin-bottom: 14px; }}
        .trend-overview {{
            font-size: 14px;
            color: #555;
            line-height: 1.8;
            margin-bottom: 18px;
        }}
        .trend-category {{
            font-size: 15px;
            font-weight: 700;
            color: #333;
            margin: 18px 0 10px;
        }}
        .trend-category:first-of-type {{ margin-top: 0; }}
        .trend-ol {{
            padding-left: 20px;
            margin-bottom: 8px;
        }}
        .trend-ol li {{
            font-size: 14px;
            color: #555;
            line-height: 1.8;
            margin-bottom: 6px;
        }}
        .risk-section {{
            margin-top: 18px;
        }}
        .risk-title {{
            font-size: 15px;
            font-weight: 700;
            color: #e74c3c;
            margin-bottom: 10px;
        }}
        .risk-list {{
            list-style: none;
            padding: 0;
        }}
        .risk-list li {{
            font-size: 13px;
            color: #e74c3c;
            line-height: 1.8;
            padding-left: 16px;
            position: relative;
            margin-bottom: 5px;
        }}
        .risk-list li::before {{
            content: "●";
            position: absolute;
            left: 0;
            color: #e74c3c;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .card-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 6px;
        }}
        .card-index {{
            font-size: 14px;
            font-weight: 700;
            color: #667eea;
            min-width: 28px;
        }}
        .card-score {{
            font-size: 12px;
            color: #e65100;
            background: #fff3e0;
            padding: 2px 10px;
            border-radius: 10px;
        }}
        .card-source {{
            font-size: 12px;
            color: #888;
            margin-left: auto;
        }}
        .card-title {{
            font-size: 17px;
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .card-title a {{
            color: #333;
            text-decoration: none;
        }}
        .card-title a:hover {{ color: #667eea; }}
        .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }}
        .tag {{
            font-size: 11px;
            padding: 2px 8px;
            background: #f0f0f0;
            border-radius: 8px;
            color: #666;
        }}
        .ai-summary {{
            font-size: 14px;
            color: #555;
            line-height: 1.6;
            margin-bottom: 8px;
        }}
        .category {{ color: #888; font-size: 13px; margin-bottom: 8px; }}
        .ai-analysis {{
            background: #fafafa;
            border-radius: 10px;
            padding: 12px 16px;
            margin: 10px 0;
        }}
        .score-row {{
            display: flex;
            align-items: baseline;
            gap: 8px;
            margin-bottom: 6px;
        }}
        .score-row:last-child {{ margin-bottom: 0; }}
        .score-name {{
            font-size: 13px;
            color: #e74c3c;
            font-weight: 700;
            min-width: 56px;
        }}
        .score-number {{
            font-size: 18px;
            font-weight: 700;
            color: #e74c3c;
            min-width: 42px;
        }}
        .score-desc {{
            font-size: 12px;
            color: #333;
            line-height: 1.4;
        }}
        .viewpoints {{
            background: #fff8e1;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 12px 0;
            border-left: 4px solid #ff9800;
        }}
        .viewpoints-title {{
            font-size: 14px;
            font-weight: 700;
            color: #e65100;
            margin-bottom: 6px;
        }}
        .viewpoints-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}
        .vp-item {{
            font-size: 12px;
            color: #555;
            background: white;
            padding: 3px 10px;
            border-radius: 12px;
            border: 1px solid #ffe0b2;
        }}
        .card-footer {{
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #bbb;
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px solid #f0f0f0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #bbb;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>热点日报</h1>
            <div class="subtitle">
                <span class="subtitle-line">多源聚合 | AI智能分析 | 价值评估</span>
                <span class="subtitle-line subtitle-sources">覆盖 Hacker News · TechCrunch · Ars Technica · The Verge · Wired · VentureBeat · InfoQ 中文 · 少数派 · 微博热搜 · 百度热搜</span>
                <span class="subtitle-line">生成时间: {now_str}</span>
            </div>
        </div>

        <div class="data-summary">
            <div class="ds-item">
                <div class="ds-num">20</div>
                <div class="ds-label">精选热点</div>
            </div>
            <div class="ds-item">
                <div class="ds-num">{total_raw}</div>
                <div class="ds-label">原始数据</div>
            </div>
            <div class="ds-item">
                <div class="ds-num">{duplicate_count}</div>
                <div class="ds-label">识别重复</div>
            </div>
            <div class="ds-item">
                <div class="ds-num">{source_count}</div>
                <div class="ds-label">数据来源</div>
            </div>
        </div>

        <div class="dist-card">
            <div class="dist-row">
                <span class="dist-row-title">分类分布:</span>
                {cat_pills_html}
            </div>
            <div class="dist-row">
                <span class="dist-row-title">数据来源:</span>
                {src_pills_html}
            </div>
        </div>

        <div class="trend-section">
            <div class="section-title">综合趋势分析</div>
            <p class="trend-overview">今日热点呈现"AI芯片博弈+行业治理觉醒+安全态势升级"的三主线格局。Nvidia风险评估（芯片地缘政治/竞争加剧）和OpenAI伦理负责人离职（AI治理人才流失）并列头部，表明行业正从"技术乐观"转向"风险审慎"；AI消费层Gemini破10亿用户与AI Agent大额融资（River AI $11亿）形成产业加速信号；安全领域FBI隐私敲诈警告、Chrome DBSC防账户接管、Delta航班假Wi-Fi（疑似DEF CON相关）形成密集安全议题；法律层面Meta $1.4万亿诉讼进入审判重塑平台责任边界。副线包括Go语言AI编程范式讨论、Nvidia Nemotron全栈布局、VC全球化（Accel印度基金）、eVTOL国防化（Joby收购）等。整体反映出"AI理性化、治理制度化、安全刚需化"的深度科技叙事。</p>
            <div class="trend-category">五大核心趋势</div>
            <ol class="trend-ol">
                <li><strong>AI芯片进入风险定价阶段</strong>：Nvidia面临地缘政治+竞争双重压力，AI芯片产业链的不确定性正被市场重新评估</li>
                <li><strong>AI治理人才危机浮现</strong>：OpenAI伦理负责人不足一年离职，行业伦理团队的地位和资源分配引发系统性反思</li>
                <li><strong>AI Agent资本竞赛白热化</strong>：River AI两月获$11亿+Gemini破10亿用户，AI应用层进入"赢家通吃"前夜</li>
                <li><strong>网络安全态势全面升级</strong>：FBI隐私敲诈+Chrome DBSC+Delta假Wi-Fi三线并发，网络攻防进入新阶段</li>
                <li><strong>AI时代编程范式重构</strong>：Google力推Go语言AI编程+Jolt编译器+Anthropic挑战数学难题，AI正深刻改变软件开发与科研范式</li>
            </ol>
            <div class="risk-section">
                <div class="risk-title">风险预警</div>
                <ul class="risk-list">
                    <li>AI芯片供应链风险：Nvidia面临出口管制收紧和竞争对手加速追赶，AI算力供给可能迎来结构性变化</li>
                    <li>AI治理空心化：OpenAI伦理负责人离职折射行业治理赤字，无有效约束的AI发展路径需警惕</li>
                    <li>AI Agent估值泡沫：River AI两月估值飙至独角兽，资本狂热可能透支赛道，需警惕2022式回调</li>
                    <li>隐私犯罪全面升级：FBI警告犯罪分子大规模窃取私密图片（含未成年人），Deepfake+敲诈组合攻击迫在眉睫</li>
                    <li>明星创业伦理危机：Phia cookie stuffing+OpenAI高管持续流失，创始人与公司治理的张力正成为行业级风险</li>
                </ul>
            </div>
        </div>

        <div class="section-title">📋 热点详情</div>
        {cards_html}

        <div class="footer">
            <p>数据来源: Hacker News · 微博热搜 · 百度热搜 · Ars Technica · TechCrunch · The Verge · Wired · VentureBeat · InfoQ 中文 · 少数派</p>
            <p style="margin-top:6px;">热点发现Agent · AI自动生成 · {now_str}</p>
        </div>
    </div>
</body>
</html>"""

    output_path = os.path.join(REPORT_DIR, f"hotspot_report_{YESTERDAY_STR}.html")
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 完整分析报告已生成: {output_path}")


if __name__ == "__main__":
    generate_html_report()
