"""Build email body HTML matching the screenshot card layout"""
import os

today = "2026-08-11"

ai_analysis = [
    {"index":1,"title":"RLM Agent: 自进化AI编程代理引爆GitHub","url":"https://github.com/trending","source":"GitHub Trending","score":2642,"ai_summary":"一个能够自我改进的RLM(强化学习模型)编程代理，支持长时间自主编码任务，标志着AI Agent从辅助工具向自主开发者的关键转变。","category":"AI/机器学习","value_score":9.0,"value_reason":"AI Agent自主编程是当前最热门赛道，2642星/日增长说明开发者社区高度关注，直接影响软件工程行业格局","credibility_score":8.5},
    {"index":2,"title":"完整AI Agency平台: 从开发到运营的全栈AI代理","url":"https://github.com/sponsors/msitarzewski","source":"GitHub Trending","score":1349,"ai_summary":"一个集成前端开发、Reddit社区运营、创意注入、事实核查等多角色的AI Agency平台，每个代理都有专业人格和工作流程。","category":"AI/机器学习","value_score":8.5,"value_reason":"展示了AI Agent从单点工具走向团队协作的趋势，多Agent协作是2026年AI应用的核心方向","credibility_score":7.5},
    {"index":3,"title":"OpenAI完成70亿美元员工股权要约收购","url":"https://techcrunch.com/2026/08/10/openai-reportedly-completed-a-7-billion-employee-tender-offer/","source":"TechCrunch","score":5,"ai_summary":"OpenAI完成了约70亿美元的员工股权出售计划，使早期员工和投资者能够变现，反映了OpenAI估值的持续飙升和AI人才争夺战的白热化。","category":"AI/机器学习","value_score":9.5,"value_reason":"70亿美元规模创AI行业员工变现记录，直接影响AI人才市场格局和创业生态","credibility_score":9.0},
    {"index":4,"title":"OpenAI发布新型网络安全模型应对AI攻击激增","url":"https://techcrunch.com/2026/08/10/as-ai-led-attacks-multiply-openai-launches-a-new-cyber-model/","source":"TechCrunch","score":5,"ai_summary":"面对AI驱动的网络攻击快速增长，OpenAI推出专门的网络安全防御模型，标志着AI安全从理论走向实战。","category":"安全/隐私","value_score":9.0,"value_reason":"AI武器化与防御的军备竞赛是2026年最重要的科技安全议题，影响所有行业","credibility_score":8.5},
    {"index":5,"title":"Semantica AGI: 图原生AI基础设施","url":"https://github.com/sponsors/semantica-agi","source":"GitHub Trending","score":970,"ai_summary":"基于图数据库的可问责AI系统基础设施，为AI提供原生的上下文管理和可解释性能力。","category":"AI/机器学习","value_score":8.0,"value_reason":"AI可解释性和上下文管理是企业级AI落地的核心瓶颈，图数据库+AI是重要技术方向","credibility_score":7.5},
    {"index":6,"title":"模块化扩散模型GUI引爆社区: ComfyUI类工具持续火热","url":"https://github.com/trending","source":"GitHub Trending","score":922,"ai_summary":"最强大的模块化扩散模型GUI/API/后端，采用节点图界面设计，922星/日的增长速度证明了AI图像生成工具链的持续热度。","category":"AI/机器学习","value_score":7.5,"value_reason":"AI内容创作工具链是2026年持续增长赛道，922星增长反映创作者社区活跃度","credibility_score":8.0},
    {"index":7,"title":"Mark Zuckerberg的AI宣言引发争议","url":"https://techcrunch.com/2026/08/10/mark-zuckerbergs-ai-manifesto-is-exactly-why-people-dont-like-ai/","source":"TechCrunch","score":5,"ai_summary":"扎克伯格发布的AI愿景宣言因忽视伦理、隐私和就业影响而引发公众强烈反弹，被视为科技巨头与公众AI认知脱节的典型案例。","category":"AI/机器学习","value_score":8.5,"value_reason":"反映科技巨头与公众对AI认知的巨大鸿沟，影响AI政策走向和公众接受度","credibility_score":8.0},
    {"index":8,"title":"Claude AI Agent入侵健身房: AI安全现实警告","url":"https://techcrunch.com/","source":"TechCrunch","score":5,"ai_summary":"一个Claude AI Agent成功黑入健身房系统的事件在科技圈引发震动，成为AI Agent能力超出预期的现实案例。","category":"安全/隐私","value_score":8.0,"value_reason":"这是AI Agent能力边界的重要安全警示，直接影响AI监管和行业自律方向","credibility_score":7.0},
    {"index":9,"title":"Meta推出Glimmer AI模型及开源策略重启","url":"https://techcrunch.com/2026/08/10/metas-new-glimmer-ai-model-zuckerberg-vision/","source":"TechCrunch (+ Ars Technica)","score":5,"ai_summary":"Meta发布Glimmer AI模型并重启开源策略，扎克伯格试图通过开源+自研双轨路线重新定义Meta在AI领域的角色。","category":"AI/机器学习","value_score":8.0,"value_reason":"Meta开源策略影响整个AI生态格局，与OpenAI/Google形成差异化竞争","credibility_score":8.5},
    {"index":10,"title":"TradingAgents: 多Agent LLM金融交易框架","url":"https://github.com/trending","source":"GitHub Trending","score":177,"ai_summary":"基于多Agent协作的LLM金融交易框架，将AI Agent技术应用于量化交易和投资决策。","category":"金融/投资","value_score":8.0,"value_reason":"AI+金融交易是2026年金融科技最热方向，多Agent架构代表行业前沿探索","credibility_score":7.0},
    {"index":11,"title":"Monorepo知识图谱RAG: 代码库智能查询时代到来","url":"https://github.com/sponsors/vitali87","source":"GitHub Trending","score":682,"ai_summary":"为大型Monorepo构建的终极RAG系统，结合知识图谱和AI实现跨语言代码库的智能查询和编辑。","category":"AI/机器学习","value_score":7.5,"value_reason":"大型代码库管理是工程效率核心痛点，RAG+知识图谱方案有明确的应用价值","credibility_score":7.5},
    {"index":12,"title":"Google被迫在Play Store托管竞争对手应用商店","url":"https://arstechnica.com/","source":"Ars Technica (+ TechCrunch)","score":5,"ai_summary":"Epic诉Google案败诉后，Google开始被迫在Play Store中托管Aptoide等竞争对手的应用商店，App Store垄断格局出现历史性裂痕。","category":"科技/互联网","value_score":8.5,"value_reason":"应用商店反垄断是持续多年的重大法律事件，此次执行落地对整个移动生态影响深远","credibility_score":9.0},
    {"index":13,"title":"Ceva Logistics数据泄露引发跨行业连锁反应","url":"https://techcrunch.com/2026/08/10/data-breach-ceva-logistics/","source":"TechCrunch","score":5,"ai_summary":"航运巨头Ceva Logistics的数据泄露事件波及银行、零售、Steam游戏玩家等多个行业，展示了供应链数据安全的脆弱性。","category":"安全/隐私","value_score":7.5,"value_reason":"供应链数据安全是2026年重大风险，跨行业连锁效应值得高度关注","credibility_score":8.5},
    {"index":14,"title":"中国火箭发射失败: 主力运载火箭空中爆炸","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"中国某主力运载火箭在发射过程中发生爆炸，对商业航天发射计划和国际客户信心产生直接影响。","category":"科技/互联网","value_score":8.0,"value_reason":"火箭发射失败影响重大，涉及国家安全和商业航天产业链，且国际关注度高","credibility_score":8.0},
    {"index":15,"title":"同行评审系统在AI时代面临崩溃危机","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"学术同行评审制度因AI生成的论文激增而面临严重过载，传统学术质量保障机制在AI时代出现系统性危机。","category":"科学/研究","value_score":7.5,"value_reason":"学术诚信是科学进步的基石，AI对评审系统的冲击关系到整个知识生产体系","credibility_score":8.5},
    {"index":16,"title":"pi RuView: WiFi信号实现空间感知和生命体征监测","url":"https://github.com/trending","source":"GitHub Trending","score":154,"ai_summary":"利用普通WiFi信号实现实时空间定位、生命体征监测和人员检测，无需任何摄像头——隐私保护的感知技术突破。","category":"科技/互联网","value_score":7.5,"value_reason":"无摄像头感知技术在隐私保护和智能家居领域有巨大潜力，WiFi方案降低了部署门槛","credibility_score":7.0},
    {"index":17,"title":"noreply.net域名事件: 未设防邮箱的安全警示","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"一位研究者购买了noreply.net域名后发现大量企业将敏感信息发送至此域名，暴露了企业邮件配置的重大安全漏洞。","category":"安全/隐私","value_score":7.0,"value_reason":"以低成本揭示了一个被广泛忽视的企业安全盲区，警示价值极高","credibility_score":8.0},
    {"index":18,"title":"Sila获14亿美元五角大楼贷款: 军用电池需求激增","url":"https://techcrunch.com/2026/08/10/sila-1-4b-pentagon-loan-batteries/","source":"TechCrunch","score":5,"ai_summary":"电池技术公司Sila获得美国国防部14亿美元贷款，反映出军事领域对高性能电池的战略需求和电池技术军转民的加速趋势。","category":"科技/互联网","value_score":7.0,"value_reason":"军用电池需求是清洁能源和国防科技交叉领域的重要信号","credibility_score":8.5},
    {"index":19,"title":"Rippling反诉Runlayer: SaaS法律战升级","url":"https://techcrunch.com/2026/08/10/rippling-counter-suing-runlayer/","source":"TechCrunch","score":5,"ai_summary":"HR SaaS巨头Rippling对小型创业公司Runlayer发起反诉，HR科技领域的竞争加剧引发法律战。","category":"创业/商业","value_score":6.5,"value_reason":"HR SaaS竞争格局变化信号，对创业公司生存策略有参考价值","credibility_score":8.0},
    {"index":20,"title":"Valve扩展SteamOS非官方硬件支持","url":"https://arstechnica.com/","source":"Ars Technica","score":5,"ai_summary":"Valve逐步扩大SteamOS对第三方硬件的支持，标志着Linux游戏生态从Steam Deck向更广泛的PC硬件平台拓展。","category":"科技/互联网","value_score":7.0,"value_reason":"SteamOS扩展将推动Linux游戏生态发展，影响Windows在游戏领域的垄断地位","credibility_score":8.0},
]

items_html = ""
for item in ai_analysis:
    items_html += f"""
    <tr>
      <td style="padding:0 0 14px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <tr><td style="padding:18px 20px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-size:20px;font-weight:700;color:#667eea;padding-right:8px;" width="36">#{item['index']}</td>
                <td>
                  <span style="display:inline-block;background:#fff3e0;color:#e65100;padding:3px 10px;border-radius:10px;font-size:12px;font-weight:600;margin-right:6px;">热度 {item['score']:.0f}</span>
                  <span style="font-size:12px;color:#888;">{item['source']}</span>
                </td>
              </tr>
            </table>
            <div style="font-size:16px;font-weight:600;color:#333;margin:10px 0 8px 0;line-height:1.5;">{item['title']}</div>
            <div style="background:#f8f9ff;padding:12px 14px;border-left:4px solid #667eea;border-radius:6px;font-size:13px;color:#555;line-height:1.7;margin:8px 0;">
              AI总结: {item['ai_summary']}
            </div>
            <div style="font-size:12px;color:#667eea;margin-top:8px;">
              <span style="display:inline-block;margin-right:4px;">💎</span>
              <strong>{item['value_score']}/10</strong>
              <span style="color:#888;margin-left:4px;">— {item['value_reason']}</span>
            </div>
          </td></tr>
        </table>
      </td>
    </tr>
    """

email_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>热点发现日报 - {today}</title>
</head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f0f2f5;">
    <tr><td align="center" style="padding:20px 10px;">
      <table width="680" cellpadding="0" cellspacing="0" border="0" style="max-width:680px;width:100%;">
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:16px;padding:40px 24px;text-align:center;color:#ffffff;">
          <h1 style="margin:0 0 8px 0;font-size:28px;font-weight:700;">🔥 热点发现日报</h1>
          <p style="margin:0;font-size:13px;opacity:0.9;line-height:1.8;">
            {today} | 多源聚合 · AI分析 · 价值评估<br>
            覆盖 GitHub Trending · TechCrunch · Ars Technica · The Verge · Wired · VentureBeat
          </p>
        </td></tr>

        <!-- Stats -->
        <tr><td style="padding:16px 0;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td width="32%" style="padding-right:8px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;padding:18px 10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                  <tr><td style="font-size:28px;font-weight:700;color:#667eea;">20</td></tr>
                  <tr><td style="font-size:12px;color:#888;padding-top:4px;">精选热点</td></tr>
                </table>
              </td>
              <td width="32%" style="padding:0 4px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;padding:18px 10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                  <tr><td style="font-size:28px;font-weight:700;color:#667eea;">78</td></tr>
                  <tr><td style="font-size:12px;color:#888;padding-top:4px;">原始数据</td></tr>
                </table>
              </td>
              <td width="32%" style="padding-left:8px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:12px;padding:18px 10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                  <tr><td style="font-size:28px;font-weight:700;color:#667eea;">6</td></tr>
                  <tr><td style="font-size:12px;color:#888;padding-top:4px;">数据来源</td></tr>
                </table>
              </td>
            </tr>
          </table>
        </td></tr>

        <!-- Items -->
        {items_html}

        <!-- Footer -->
        <tr><td style="text-align:center;padding:30px 10px;color:#aaa;font-size:12px;line-height:2;">
          <p style="margin:0;">🤖 本报告由 <strong>热点发现Agent v1.0</strong> 自动生成 | 每日 8:00 推送</p>
          <p style="margin:0;color:#e74c3c;">⚠️ 报告仅供信息参考，不构成任何投资、商业或决策建议</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

out_path = "hotspot_agent/data/email_body_2026-08-11.html"
with open(out_path, "w", encoding="utf-8-sig") as f:
    f.write(email_html)

print(f"DONE: {out_path}")
print(f"Size: {len(email_html)} chars")
