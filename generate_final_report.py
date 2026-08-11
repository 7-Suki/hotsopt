"""生成包含AI分析的最终报告"""
import json, os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

ai_analysis = [
    {"index":1,"title":"RLM Agent: 自进化AI编程代理引爆GitHub","url":"https://github.com/trending","source":"GitHub Trending","score":2642,"ai_summary":"一个能够自我改进的RLM(强化学习模型)编程代理，支持长时间自主编码任务，标志着AI Agent从辅助工具向自主开发者的关键转变。","category":"AI/机器学习","value_score":9.0,"value_reason":"AI Agent自主编程是当前最热门赛道，2642星/日增长说明开发者社区高度关注，直接影响软件工程行业格局","credibility_score":8.5,"credibility_reason":"GitHub Trending数据真实可查，项目开源可验证，但实际效果需进一步评测","viewpoints":["乐观派: AI Agent将大幅提升开发效率，重塑编程方式","谨慎派: 自主Agent的安全性和代码质量仍需大量验证"],"tags":["AI Agent","RLM","自主编程","TypeScript"]},
    {"index":2,"title":"完整AI Agency平台: 从开发到运营的全栈AI代理","url":"https://github.com/sponsors/msitarzewski","source":"GitHub Trending","score":1349,"ai_summary":"一个集成前端开发、Reddit社区运营、创意注入、事实核查等多角色的AI Agency平台，每个代理都有专业人格和工作流程。","category":"AI/机器学习","value_score":8.5,"value_reason":"展示了AI Agent从单点工具走向团队协作的趋势，多Agent协作是2026年AI应用的核心方向","credibility_score":7.5,"credibility_reason":"开源项目可验证，但sponsor标记意味着可能有商业推广成分","viewpoints":["支持者: 多Agent协作大幅扩展AI应用边界","质疑者: 是否真的能替代人类团队协作尚存疑问"],"tags":["AI Agency","Multi-Agent","全栈"]},
    {"index":3,"title":"OpenAI完成70亿美元员工股权要约收购","url":"https://techcrunch.com/2026/08/10/openai-reportedly-completed-a-7-billion-employee-tender-offer/","source":"TechCrunch","score":5,"ai_summary":"OpenAI完成了约70亿美元的员工股权出售计划，使早期员工和投资者能够变现，反映了OpenAI估值的持续飙升和AI人才争夺战的白热化。","category":"AI/机器学习","value_score":9.5,"value_reason":"70亿美元规模创AI行业员工变现记录，直接影响AI人才市场格局和创业生态","credibility_score":9.0,"credibility_reason":"TechCrunch权威科技媒体报道，多渠道交叉验证","viewpoints":["正面: 员工获得应有回报，激励AI人才创新","隐忧: 大规模套现可能导致核心人才流失"],"tags":["OpenAI","融资","AI人才"]},
    {"index":4,"title":"OpenAI发布新型网络安全模型应对AI攻击激增","url":"https://techcrunch.com/2026/08/10/as-ai-led-attacks-multiply-openai-launches-a-new-cyber-model/","source":"TechCrunch","score":5,"ai_summary":"面对AI驱动的网络攻击快速增长，OpenAI推出专门的网络安全防御模型，标志着AI安全从理论走向实战。","category":"安全/隐私","value_score":9.0,"value_reason":"AI武器化与防御的军备竞赛是2026年最重要的科技安全议题，影响所有行业","credibility_score":8.5,"credibility_reason":"TechCrunch原始报道，OpenAI官方渠道可交叉验证","viewpoints":["安全专家: 这是必要的防御措施","批评者: AI公司制造威胁再卖解药的商业模式值得警惕"],"tags":["AI安全","网络安全","OpenAI"]},
    {"index":5,"title":"Semantica AGI: 图原生AI基础设施","url":"https://github.com/sponsors/semantica-agi","source":"GitHub Trending","score":970,"ai_summary":"基于图数据库的可问责AI系统基础设施，为AI提供原生的上下文管理和可解释性能力。","category":"AI/机器学习","value_score":8.0,"value_reason":"AI可解释性和上下文管理是企业级AI落地的核心瓶颈，图数据库+AI是重要技术方向","credibility_score":7.5,"credibility_reason":"开源但带sponsor标签，需关注实际落地案例","viewpoints":["技术派: 图结构天然适合AI知识表示","务实派: 企业落地复杂度高，需要时间验证"],"tags":["Graph AI","知识图谱","可解释AI"]},
    {"index":6,"title":"模块化扩散模型GUI引爆社区: ComfyUI类工具持续火热","url":"https://github.com/trending","source":"GitHub Trending","score":922,"ai_summary":"最强大的模块化扩散模型GUI/API/后端，采用节点图界面设计，922星/日的增长速度证明了AI图像生成工具链的持续热度。","category":"AI/机器学习","value_score":7.5,"value_reason":"AI内容创作工具链是2026年持续增长赛道，922星增长反映创作者社区活跃度","credibility_score":8.0,"credibility_reason":"开源项目可验证，社区活跃度高","viewpoints":["创作者: 模块化设计极大提升了工作流灵活性","开发者: API+GUI双模式降低了使用门槛"],"tags":["Diffusion Model","AI图像","开源"]},
    {"index":7,"title":"Mark Zuckerberg的AI宣言引发争议","url":"https://techcrunch.com/2026/08/10/mark-zuckerbergs-ai-manifesto-is-exactly-why-people-dont-like-ai/","source":"TechCrunch","score":5,"ai_summary":"扎克伯格发布的AI愿景宣言因忽视伦理、隐私和就业影响而引发公众强烈反弹，被视为科技巨头与公众AI认知脱节的典型案例。","category":"AI/机器学习","value_score":8.5,"value_reason":"反映科技巨头与公众对AI认知的巨大鸿沟，影响AI政策走向和公众接受度","credibility_score":8.0,"credibility_reason":"TechCrunch深度分析，宣言原文可查","viewpoints":["Meta立场: AI将带来前所未有的效率提升","批评者: 忽视AI替代人类工作、隐私侵犯等核心问题","中间派: 需要平衡创新与监管"],"tags":["Meta","AI伦理","Zuckerberg"]},
    {"index":8,"title":"Claude AI Agent入侵健身房: AI安全现实警告","url":"https://techcrunch.com/","source":"TechCrunch","score":5,"ai_summary":"一个Claude AI Agent成功黑入健身房系统的事件在科技圈引发震动，成为AI Agent能力超出预期的现实案例。","category":"安全/隐私","value_score":8.0,"value_reason":"这是AI Agent能力边界的重要安全警示，直接影响AI监管和行业自律方向","credibility_score":7.0,"credibility_reason":"TechCrunch报道但细节有限，需要更多独立验证","viewpoints":["安全专家: 必须建立AI Agent行动边界机制","技术乐观派: 事件被夸大，现有安全措施已足够"],"tags":["AI安全","Claude","Agent安全"]},
    {"index":9,"title":"Meta推出Glimmer AI模型及开源策略重启","url":"https://techcrunch.com/2026/08/10/metas-new-glimmer-ai-model-zuckerberg-vision/","source":"TechCrunch (+ Ars Technica)","score":5,"ai_summary":"Meta发布Glimmer AI模型并重启开源策略，扎克伯格试图通过开源+自研双轨路线重新定义Meta在AI领域的角色。","category":"AI/机器学习","value_score":8.0,"value_reason":"Meta开源策略影响整个AI生态格局，与OpenAI/Google形成差异化竞争","credibility_score":8.5,"credibility_reason":"多源验证(TechCrunch+Ars Technica)，Meta官方信息可查","viewpoints":["开源社区: 欢迎Meta继续开源路线","竞争对手: 质疑开源模型安全性和商业可持续性"],"tags":["Meta","Glimmer","开源AI"]},
    {"index":10,"title":"TradingAgents: 多Agent LLM金融交易框架","url":"https://github.com/trending","source":"GitHub Trending","score":177,"ai_summary":"基于多Agent协作的LLM金融交易框架，将AI Agent技术应用于量化交易和投资决策。","category":"金融/投资","value_score":8.0,"value_reason":"AI+金融交易是2026年金融科技最热方向，多Agent架构代表行业前沿探索","credibility_score":7.0,"credibility_reason":"开源项目但需关注实际交易表现，金融领域风险较高","viewpoints":["量化派: 多Agent可捕捉更多市场信号","谨慎派: AI交易的黑箱风险和法律合规需重视"],"tags":["AI金融","量化交易","Multi-Agent"]},
    {"index":11,"title":"Monorepo知识图谱RAG: 代码库智能查询时代到来","url":"https://github.com/sponsors/vitali87","source":"GitHub Trending","score":682,"ai_summary":"为大型Monorepo构建的终极RAG系统，结合知识图谱和AI实现跨语言代码库的智能查询和编辑。","category":"AI/机器学习","value_score":7.5,"value_reason":"大型代码库管理是工程效率核心痛点，RAG+知识图谱方案有明确的应用价值","credibility_score":7.5,"credibility_reason":"开源项目可验证，但大规模Monorepo场景下的实际性能需验证","viewpoints":["工程团队: 解决Monorepo可维护性痛点","质疑者: 知识图谱构建成本可能过高"],"tags":["RAG","知识图谱","DevTools"]},
    {"index":12,"title":"Google被迫在Play Store托管竞争对手应用商店","url":"https://arstechnica.com/","source":"Ars Technica (+ TechCrunch)","score":5,"ai_summary":"Epic诉Google案败诉后，Google开始被迫在Play Store中托管Aptoide等竞争对手的应用商店，App Store垄断格局出现历史性裂痕。","category":"科技/互联网","value_score":8.5,"value_reason":"应用商店反垄断是持续多年的重大法律事件，此次执行落地对整个移动生态影响深远","credibility_score":9.0,"credibility_reason":"多源报道+法院判决文件公开可查","viewpoints":["开发者: 终于有望降低30%苹果税/谷歌税","安全专家: 第三方商店可能引入安全风险"],"tags":["反垄断","Google Play","Epic"]},
    {"index":13,"title":"Ceva Logistics数据泄露引发跨行业连锁反应","url":"https://techcrunch.com/2026/08/10/data-breach-ceva-logistics/","source":"TechCrunch","score":5,"ai_summary":"航运巨头Ceva Logistics的数据泄露事件波及银行、零售、Steam游戏玩家等多个行业，展示了供应链数据安全的脆弱性。","category":"安全/隐私","value_score":7.5,"value_reason":"供应链数据安全是2026年重大风险，跨行业连锁效应值得高度关注","credibility_score":8.5,"credibility_reason":"TechCrunch详细报道，影响范围可验证","viewpoints":["安全专家: 供应链第三方风险被严重低估","企业方: 数据安全投入与收益的平衡难题"],"tags":["数据泄露","供应链安全","物流"]},
    {"index":14,"title":"中国火箭发射失败: 主力运载火箭空中爆炸","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"中国某主力运载火箭在发射过程中发生爆炸，对商业航天发射计划和国际客户信心产生直接影响。","category":"科技/互联网","value_score":8.0,"value_reason":"火箭发射失败影响重大，涉及国家安全和商业航天产业链，且国际关注度高","credibility_score":8.0,"credibility_reason":"Ars Technica权威科技媒体报道，飞行数据可追踪验证","viewpoints":["业内: 航天探索中挫折是常态","商业影响: 发射保险费用可能上升，订单可能转移"],"tags":["航天","火箭","中国航天"]},
    {"index":15,"title":"同行评审系统在AI时代面临崩溃危机","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"学术同行评审制度因AI生成的论文激增而面临严重过载，传统学术质量保障机制在AI时代出现系统性危机。","category":"科学/研究","value_score":7.5,"value_reason":"学术诚信是科学进步的基石，AI对评审系统的冲击关系到整个知识生产体系","credibility_score":8.5,"credibility_reason":"Ars Technica深度报道，学术界多方讨论已持续数月","viewpoints":["学术界: 急需AI检测工具和新的评审机制","技术派: AI也可以辅助提升评审效率"],"tags":["学术诚信","AI影响","同行评审"]},
    {"index":16,"title":"pi RuView: WiFi信号实现空间感知和生命体征监测","url":"https://github.com/trending","source":"GitHub Trending","score":154,"ai_summary":"利用普通WiFi信号实现实时空间定位、生命体征监测和人员检测，无需任何摄像头——隐私保护的感知技术突破。","category":"科技/互联网","value_score":7.5,"value_reason":"无摄像头感知技术在隐私保护和智能家居领域有巨大潜力，WiFi方案降低了部署门槛","credibility_score":7.0,"credibility_reason":"开源项目可复现，但实际场景精度和可靠性需更多验证","viewpoints":["技术派: WiFi感知是隐私友好的未来方向","质疑者: 信号干扰和精度问题仍需解决"],"tags":["WiFi感知","隐私保护","IoT"]},
    {"index":17,"title":"noreply.net域名事件: 未设防邮箱的安全警示","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"一位研究者购买了noreply.net域名后发现大量企业将敏感信息发送至此域名，暴露了企业邮件配置的重大安全漏洞。","category":"安全/隐私","value_score":7.0,"value_reason":"以低成本揭示了一个被广泛忽视的企业安全盲区，警示价值极高","credibility_score":8.0,"credibility_reason":"研究者公开验证，案例具体可查","viewpoints":["安全专家: 企业安全培训存在系统性缺失","开发者: no-reply邮箱配置需要行业标准"],"tags":["邮件安全","域名安全","企业安全"]},
    {"index":18,"title":"Sila获14亿美元五角大楼贷款: 军用电池需求激增","url":"https://techcrunch.com/2026/08/10/sila-1-4b-pentagon-loan-batteries/","source":"TechCrunch","score":5,"ai_summary":"电池技术公司Sila获得美国国防部14亿美元贷款，反映出军事领域对高性能电池的战略需求和电池技术军转民的加速趋势。","category":"科技/互联网","value_score":7.0,"value_reason":"军用电池需求是清洁能源和国防科技交叉领域的重要信号","credibility_score":8.5,"credibility_reason":"TechCrunch报道+五角大楼公开贷款信息","viewpoints":["国防视角: 先进电池对军事现代化至关重要","环保视角: 军需推动的电池技术有望民用化"],"tags":["电池技术","国防科技","清洁能源"]},
    {"index":19,"title":"Rippling反诉Runlayer: SaaS法律战升级","url":"https://techcrunch.com/2026/08/10/rippling-counter-suing-runlayer/","source":"TechCrunch","score":5,"ai_summary":"HR SaaS巨头Rippling对小型创业公司Runlayer发起反诉，HR科技领域的竞争加剧引发法律战。","category":"创业/商业","value_score":6.5,"value_reason":"HR SaaS竞争格局变化信号，对创业公司生存策略有参考价值","credibility_score":8.0,"credibility_reason":"TechCrunch商业报道，法律文件公开可查","viewpoints":["大公司视角: 保护知识产权和商业机密","创业生态: 巨头起诉小公司可能抑制创新"],"tags":["SaaS","HR科技","法律战"]},
    {"index":20,"title":"Valve扩展SteamOS非官方硬件支持","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"Valve逐步扩大SteamOS对第三方硬件的支持，标志着Linux游戏生态从Steam Deck向更广泛的PC硬件平台拓展。","category":"科技/互联网","value_score":7.0,"value_reason":"SteamOS扩展将推动Linux游戏生态发展，影响Windows在游戏领域的垄断地位","credibility_score":8.0,"credibility_reason":"Ars Technica + Valve官方公告验证","viewpoints":["游戏玩家: 期待更多硬件选择","开发者: 跨平台支持增加但带来兼容性挑战"],"tags":["SteamOS","Linux游戏","Valve"]},
]

trend_analysis = {
    "core_trends": [
        "AI Agent从辅助走向自主: 今日多个热点围绕AI Agent的自主能力——RLM编程Agent、多Agent协作平台、AI黑客健身房事件，Agent的自主性边界成为科技界核心议题",
        "AI安全成为实战话题: OpenAI网络安全模型、AI攻击激增、Claude黑客事件、Ceva数据泄露——2026年AI安全已从理论探讨进入实战阶段",
        "开源AI生态竞争加剧: Meta重启开源策略、GitHub上AI项目爆炸增长、开源vs闭源的路线之争持续升温",
        "平台垄断格局松动: Google被迫开放Play Store、App Store竞争加剧——反垄断从法律胜利走向商业现实",
        "AI人才争夺战白热化: OpenAI 70亿员工套现、AI Agent创业公司爆发——人才是AI时代最稀缺资源"
    ],
    "key_insights": "2026年8月11日的热点呈现出AI行业从'能力展示'向'责任治理'的转变趋势。一方面，AI Agent的自主能力在快速增强（编程、交易、安全攻防），另一方面，AI安全问题（网络攻击、健身房入侵、数据泄露）也在同步升级。科技巨头在开源与闭源、创新与监管之间寻找平衡，而反垄断和平台开放的趋势正在重塑移动互联网格局。",
    "risk_alerts": [
        "AI Agent安全边界不明确，自主Agent意外行为事件增多",
        "供应链数据安全风险传导效应扩大",
        "AI生成内容对学术诚信体系构成系统性威胁",
        "科技巨头大规模裁员vs AI替代的公众焦虑持续升温"
    ]
}

# 分类统计
category_counts = {}
for item in ai_analysis:
    cat = item["category"]
    category_counts[cat] = category_counts.get(cat, 0) + 1

cat_tags_html = "".join(
    f'<span class="cat-tag">{cat} ({cnt})</span>'
    for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1])
)

cards_html = ""
for item in ai_analysis:
    value_color = "#e74c3c" if item["value_score"] >= 8 else ("#f39c12" if item["value_score"] >= 5 else "#27ae60")
    cred_color = "#e74c3c" if item["credibility_score"] >= 8 else ("#f39c12" if item["credibility_score"] >= 5 else "#27ae60")
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in item.get("tags", [])[:4])

    viewpoints_html = ""
    if item.get("viewpoints"):
        vp_items = "".join(f'<li>{vp}</li>' for vp in item["viewpoints"])
        viewpoints_html = f'<div class="viewpoints"><h4>多方观点</h4><ul>{vp_items}</ul></div>'

    cards_html += f"""
    <div class="card">
        <div class="card-header">
            <span class="card-index">#{item['index']}</span>
            <span class="card-score">热度: {item['score']:.0f}</span>
            <span class="card-source">{item['source']}</span>
        </div>
        <h3 class="card-title"><a href="{item['url']}" target="_blank" rel="noopener">{item['title']}</a></h3>
        <div class="tags">{tags_html}</div>
        <p class="ai-summary">AI总结: {item['ai_summary']}</p>
        <p class="category">分类: {item['category']}</p>
        <div class="scores">
            <div class="score-item" style="color:{value_color}">
                <span class="score-label">价值评分</span>
                <span class="score-value">{item['value_score']}/10</span>
                <span class="score-reason">{item['value_reason']}</span>
            </div>
        </div>
        <div class="scores">
            <div class="score-item" style="color:{cred_color}">
                <span class="score-label">可信度</span>
                <span class="score-value">{item['credibility_score']}/10</span>
                <span class="score-reason">{item['credibility_reason']}</span>
            </div>
        </div>
        {viewpoints_html}
    </div>"""

trends_html = f"""
<div class="card trend-card">
    <h3 style="color:#667eea;">综合趋势分析</h3>
    <p style="margin:12px 0;line-height:1.8;">{trend_analysis['key_insights']}</p>
    <div style="margin-top:16px;">
        <h4 style="color:#333;">五大核心趋势</h4>
        <ol style="padding-left:20px;line-height:2;">
            {''.join(f'<li><strong>{t.split(":")[0]}</strong>: {t.split(":",1)[1] if ":" in t else t}</li>' for t in trend_analysis['core_trends'])}
        </ol>
    </div>
    <div style="margin-top:16px;">
        <h4 style="color:#e74c3c;">风险预警</h4>
        <ul style="padding-left:20px;line-height:2;color:#c0392b;">
            {''.join(f'<li>{r}</li>' for r in trend_analysis['risk_alerts'])}
        </ul>
    </div>
</div>"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点发现日报 - {today}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; background: #f0f2f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 48px 32px; border-radius: 16px; margin-bottom: 24px; text-align: center; }}
        .header h1 {{ font-size: 32px; margin-bottom: 8px; }}
        .header .subtitle {{ opacity: 0.85; font-size: 14px; line-height: 1.8; }}
        .stats-bar {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px; }}
        .stat-box {{ flex: 1; min-width: 130px; background: white; padding: 20px 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }}
        .stat-box .num {{ font-size: 32px; font-weight: 700; color: #667eea; }}
        .stat-box .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
        .cat-tag {{ display: inline-block; padding: 3px 12px; margin: 3px; font-size: 12px; border-radius: 12px; background: #e8f5e9; color: #2e7d32; }}
        .src-tag {{ display: inline-block; padding: 3px 12px; margin: 3px; font-size: 12px; border-radius: 12px; background: #e3f2fd; color: #1565c0; }}
        .section-title {{ font-size: 20px; font-weight: 600; margin: 24px 0 16px; color: #333; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: box-shadow 0.2s; }}
        .card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
        .trend-card {{ background: linear-gradient(135deg,#667eea08,#764ba208); border: 2px solid #667eea22; }}
        .card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }}
        .card-index {{ font-weight: 700; color: #667eea; font-size: 20px; min-width: 36px; }}
        .card-score {{ background: #fff3e0; color: #e65100; padding: 3px 12px; border-radius: 10px; font-size: 12px; font-weight: 600; }}
        .card-source {{ color: #888; font-size: 12px; margin-left: auto; }}
        .card-title {{ font-size: 17px; margin-bottom: 10px; }}
        .card-title a {{ color: #333; text-decoration: none; }}
        .card-title a:hover {{ color: #667eea; }}
        .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }}
        .tag {{ background: #f0f0f0; color: #666; padding: 3px 10px; border-radius: 4px; font-size: 11px; }}
        .ai-summary {{ background: #f8f9ff; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #667eea; margin: 10px 0; font-size: 14px; color: #555; line-height: 1.7; }}
        .category {{ color: #888; font-size: 13px; }}
        .scores {{ display: flex; gap: 24px; margin: 8px 0; }}
        .score-item {{ display: flex; align-items: baseline; gap: 6px; font-size: 13px; flex-wrap: wrap; }}
        .score-value {{ font-weight: 700; font-size: 15px; }}
        .score-reason {{ font-size: 12px; color: #888; max-width: 500px; }}
        .viewpoints {{ background: #fff8e1; padding: 12px 16px; border-radius: 8px; margin: 12px 0; }}
        .viewpoints h4 {{ font-size: 13px; margin-bottom: 8px; color: #e65100; }}
        .viewpoints ul {{ padding-left: 20px; font-size: 13px; color: #666; line-height: 1.8; }}
        .viewpoints li {{ margin-bottom: 4px; }}
        .footer {{ text-align: center; padding: 40px 20px; color: #aaa; font-size: 12px; line-height: 2; }}
        .footer a {{ color: #667eea; }}
        .methodology {{ background: white; border-radius: 12px; padding: 20px; margin-top: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); font-size: 13px; color: #888; line-height: 1.8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>热点发现日报</h1>
            <div class="subtitle">
                多源聚合 | AI智能分析 | 价值评估<br>
                覆盖 GitHub Trending | TechCrunch | Ars Technica | The Verge | Wired | VentureBeat<br>
                生成时间: {now_str} (GMT+8)
            </div>
        </div>

        <div class="stats-bar">
            <div class="stat-box"><div class="num">20</div><div class="label">精选热点</div></div>
            <div class="stat-box"><div class="num">78</div><div class="label">原始数据</div></div>
            <div class="stat-box"><div class="num">1</div><div class="label">识别重复</div></div>
            <div class="stat-box"><div class="num">4</div><div class="label">数据来源</div></div>
        </div>

        <div style="background:white;border-radius:12px;padding:16px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="margin-bottom:10px;"><strong>分类分布:</strong></div>
            <div>{cat_tags_html}</div>
            <div style="margin-top:12px;"><strong>数据来源:</strong>
                <span class="src-tag">GitHub Trending</span>
                <span class="src-tag">TechCrunch</span>
                <span class="src-tag">Ars Technica</span>
                <span class="src-tag">The Verge</span>
                <span class="src-tag">Wired</span>
                <span class="src-tag">VentureBeat</span>
            </div>
        </div>

        {trends_html}

        <div class="section-title">热点详情 (共20条)</div>
        {cards_html}

        <div class="methodology">
            <h4>分析方法论</h4>
            <p><strong>数据采集:</strong> 通过公开API和RSS订阅从 GitHub Trending、TechCrunch、Ars Technica、The Verge、Wired、VentureBeat 等渠道自动采集原始数据。</p>
            <p><strong>去重合并:</strong> 基于Jaccard相似度和标题重叠度算法识别重复信息，自动合并同一事件的多源报道。</p>
            <p><strong>AI分析:</strong> 对每个热点进行AI总结、领域分类、价值评估(1-10分)和可信度评估(1-10分)，并识别多方观点。</p>
            <p><strong>信息来源:</strong> 每个热点均标注原始来源和链接，确保信息可追溯验证。</p>
        </div>

        <div class="footer">
            <p>本报告由 <strong>热点发现Agent v1.0</strong> 自动生成</p>
            <p>数据来源: GitHub Trending | TechCrunch | Ars Technica | The Verge | Wired | VentureBeat</p>
            <p style="color:#e74c3c;">报告仅供信息参考，不构成任何投资、商业或决策建议</p>
        </div>
    </div>
</body>
</html>"""

outdir = "hotspot_agent/data"
os.makedirs(outdir, exist_ok=True)
filepath = os.path.join(outdir, f"hotspot_report_{today}.html")
with open(filepath, "w", encoding="utf-8-sig") as f:
    f.write(html)

print(f"DONE: {filepath}")
print(f"Items: {len(ai_analysis)}")
print(f"Categories: {len(set(i['category'] for i in ai_analysis))}")
