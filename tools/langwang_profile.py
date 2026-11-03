"""Build WaveNet's factual plan, coverage and noon-snapshot profile."""
from html import escape as e
from pathlib import Path
import json

from site_chrome import shell, write_changed
from langwang_nodes import validate_snapshot, build_snapshot_assets, render_snapshot, time_label
from langwang_plans import validate_plans, build_plan_csv, render_plans, plan_faqs
from langwang_clients import render_clients, client_faqs


def load(root, path):
    return json.loads((root/path).read_text(encoding='utf-8'))


def build_langwang_profile(root, brand):
    root = Path(root)
    overview = load(root, brand['overview_path'])
    coverage = load(root, brand['coverage_path'])
    snapshot = load(root, brand['latency_path'])
    plans = load(root, brand['plans_path'])
    clients = load(root, brand['clients_path']) if brand.get('clients_path') else None
    clients_ready = clients is not None and clients['collection_status'] == 'basic_flows_confirmed'
    validate_snapshot(snapshot)
    validate_plans(plans)
    assert overview['brand_id'] == coverage['brand_id'] == 'langwang'
    assert coverage['total_node_count'] == snapshot['summary']['node_count'] == 60
    assert {g['id']: g['node_count'] for g in coverage['regions']} == {g['id']: g['node_count'] for g in snapshot['regions']}
    build_snapshot_assets(root, snapshot)
    build_plan_csv(root, plans)
    entry = e(brand['url'], quote=True)
    mark = ('<img class="langwang-mark" src="'+e(brand['logo_path'], quote=True)+'" width="'+str(brand['logo_width'])
            +'" height="'+str(brand['logo_height'])+'" alt="浪网Logo" decoding="async">' if brand.get('logo_path')
            else '<span class="langwang-mark" aria-hidden="true">浪</span>')
    features = [
        ('BGP入口与SS协议', '品牌介绍为BGP智能多线入口与专线中继互联，站长另已确认节点采用Shadowsocks（SS）协议。'),
        ('年付标准单独列IPLC', '119元年付标准的全IPLC说明已由站长单独确认；每30天刷新80GB。其他套餐按各自线路条目阅读。'),
        ('平台使用方向', '品牌资料列4K流媒体、TikTok与AI工具方向。本页提供的是节点延迟截图，相应实际播放或问答反馈继续补充。')
    ]
    feature_cards = ''.join('<article><span class="overline">0'+str(index)+' / BRAND MATERIAL</span><h3>'+e(title)
                            +'</h3><p>'+e(text)+'</p></article>' for index, (title, text) in enumerate(features, 1))
    region_cards = ''.join('<li><h3>'+e(g['name'])+'</h3><p><strong>'+str(g['node_count'])
                           +'</strong><span>个节点</span></p></li>' for g in coverage['regions'])
    questions = [
        ('浪网当前覆盖哪些地区，有多少个节点？', '以站长确认的完整截图为准，共60个：香港20个，台湾、日本、新加坡、美国各10个。年付详情另列地区的原文保留在源资料，当前覆盖表依据后续确认的截图整理。'),
        ('这批浪网节点延迟的采样条件是什么？', time_label(snapshot)+'，上海电信，Windows版浪网客户端。日期、时间、城市、运营商与客户端均由站长逐项确认，客户端版本和探测方法未提供。'),
        ('超时和1028ms这类较高数值怎样统计？', '台湾04保留为Timeout，不按0ms参与数值统计。其余59条数值范围50—1028ms，中位数169ms；台湾01的1028ms、美国01的565ms等按原值保留。'),
        ('这批截图能证明晚高峰一直稳定吗？', '本批为11月3日12点的静态节点截图。品牌介绍中的晚高峰表现说明仍需要对应时段和连续观察材料；当前记录不生成长期可用率或同条件性能排名。'),
        ('浪网已有4K、TikTok和ChatGPT的实际任务结果吗？', '这些是品牌介绍与套餐材料列明的使用方向，目前尚未提供对应平台的实际播放、账号任务或问答记录。客户端显示的延迟与实际任务结果分别记录。'),
        ('浪网的优惠、付款、使用与退款规则在哪里查看？', '四个平台的基础使用教程已列明，具体版本和最低系统要求请查看下载页。优惠、付款、流量与售后规则继续按浪网资料补充，选购时请核对官网订单与客服说明。' if clients_ready else '本页已整理9款套餐和60节点记录。各平台完整使用流程、优惠、付款与售后规则按后续提供的浪网资料继续补充，选购时请核对官网订单与客服说明。')
    ] + plan_faqs(plans) + (client_faqs(clients) if clients_ready else [])
    faq = ''.join('<details class="langwang-faq"><summary>'+e(question)+'</summary><p>'+e(answer)+'</p></details>' for question, answer in questions)
    body = ('<section class="info-hero langwang-hero" id="langwang-about"><span class="info-kicker">WAVENET / BGP & SS</span>'
            '<div class="langwang-heading">'+mark+'<div><h1>浪网 WaveNet</h1><p>BGP智能多线入口 · SS协议 · 年付标准单独列IPLC</p></div></div>'
            '<p>'+e(overview['editorial_description'])+'</p><div class="contact-buttons">'
            '<a class="contact-action" href="#langwang-plans">查看9款套餐 →</a>'
            '<a class="copy-contact" href="#langwang-latency">查看60节点记录 →</a>'
            '<a class="copy-contact" href="'+entry+'" target="_blank" rel="sponsored noopener noreferrer">访问浪网推广入口 ↗</a></div>'
            '<p class="langwang-source-date">资料由站长提供并逐项确认 · 更新：'+e(overview['updated_on'])+'</p></section>'
            '<nav class="info-breadcrumb" aria-label="当前位置"><a href="index.html">首页</a><span>/</span><a href="brands.html">品牌介绍</a><span>/</span><span>浪网 WaveNet</span></nav>'
            '<nav class="langwang-jumps" aria-label="浪网页面重点内容"><a href="#langwang-intro">线路与使用方向</a><a href="#langwang-plans">9款套餐</a>'
            '<a href="#langwang-plan-comparison">价格对照表</a><a href="#langwang-coverage">五地区节点覆盖</a><a href="#langwang-latency">12点延迟记录</a>'
            '<a href="#langwang-materials">使用与售后资料</a><a href="#langwang-faq">常见问题</a><a href="#langwang-sources">资料来源</a></nav>'
            '<section class="section" id="langwang-intro"><span class="overline">CONFIRMED BRAND MATERIALS</span><h2 id="quick-section-1">目前已确认的资料</h2>'
            '<div class="langwang-feature-grid">'+feature_cards+'</div><p class="langwang-note">线路、协议和平台方向按站长提供的资料整理，下方截图注明独立的采样条件与统计范围。</p></section>'
            +render_plans(plans, brand['url'])+
            '<section class="section" id="langwang-coverage" aria-labelledby="langwang-coverage-title"><span class="overline">5 REGIONS / 60 NODES</span>'
            '<h2 id="langwang-coverage-title">5个地区，60个节点。</h2><p class="langwang-lead">站长于'+e(coverage['confirmed_on'])
            +'确认这6张截图为完整列表，并确认当前覆盖以截图为准：香港20个，台湾、日本、新加坡、美国各10个。</p>'
            '<ul class="langwang-coverage-grid">'+region_cards+'</ul><p class="langwang-note"><a href="data/langwang-coverage.json">查看完整覆盖确认与来源 JSON ↓</a></p></section>'
            +render_snapshot(snapshot)+
            '<section class="section" id="langwang-materials"><span class="overline">USING THE SERVICE</span><h2 id="quick-section-2">选择前先核对什么</h2>'
            '<div class="langwang-pending"><h3>客户端下载与服务规则继续补充</h3><p>本次采样已确认使用Windows版浪网；各平台完整使用流程、优惠、付款与售后条件继续补充。选购前请在官网订单和客服说明中核对相应细则。</p>'
            '<a href="'+entry+'" target="_blank" rel="sponsored noopener noreferrer">前往浪网推广入口 ↗</a></div></section>'
            '<section class="section" id="langwang-faq"><span class="overline">WAVENET QUESTIONS</span><h2 id="langwang-faq-title">浪网套餐与节点常见问题</h2>'+faq+'</section>'
            '<section class="section" id="langwang-sources"><span class="overline">SOURCES & SCOPE</span><h2 id="langwang-sources-title">资料来源与适用范围</h2>'
            '<p class="langwang-lead">品牌介绍、BGP与SS说明由站长提供。9款套餐来自两张截图，三款重复展示合并计数；年付80GB、定制680元/月、年付IPLC、一次性总流量与当前节点覆盖均另行确认。'
            '延迟记录来自6张截图，采样于2026年11月3日12点，上海电信，Windows版浪网客户端，时间按小时提供。本页为资料整理，本站未独立复测。</p>'
            '<div class="langwang-source-links"><a href="data/langwang-overview.json">品牌资料 JSON ↓</a><a href="data/langwang-plans.json">套餐来源与确认 JSON ↓</a>'
            '<a href="data/langwang-plans.csv" download>套餐对照表 CSV ↓</a><a href="data/langwang-latency.json">节点记录与统计 JSON ↓</a>'
            '<a href="data/langwang-latency.csv" download>60节点对照表 CSV ↓</a><a href="assets/langwang-latency-overview.svg" download>高清概览图 SVG ↓</a>'
            '<a href="topic-reviews-guide.html">机场测评与证据范围 →</a><a href="brands.html">返回品牌目录 →</a></div></section>')
    if clients_ready:
        marker = '<section class="section" id="langwang-materials">'
        body = body.replace(marker, render_clients(clients, brand['url'])+'\n'+marker, 1)
        body = body.replace('<a href="#langwang-materials">使用与售后资料</a>', '<a href="#langwang-clients">各平台使用教程</a><a href="#langwang-materials">使用与售后资料</a>', 1)
        body = body.replace('客户端下载与服务规则继续补充', '优惠、流量与售后规则继续补充', 1)
        body = body.replace('本次采样已确认使用Windows版浪网；各平台完整使用流程、优惠、付款与售后条件继续补充。选购前请在官网订单和客服说明中核对相应细则。', '四个平台的基础下载、登录与连接流程已在上方列出。具体版本和最低系统要求以下载页说明为准；优惠、付款、流量与售后条件继续按浪网资料补充。', 1)
        body = body.replace('本页为资料整理，本站未独立复测。', '各平台下载、登录与连接步骤另由站长逐项确认。本页为资料整理，本站未独立复测。', 1)
        body = body.replace('<a href="data/langwang-overview.json">品牌资料 JSON ↓</a>', '<a href="data/langwang-overview.json">品牌资料 JSON ↓</a><a href="data/langwang-clients.json">各平台使用资料 JSON ↓</a>', 1)
    html = shell('浪网 WaveNet套餐与节点｜9款价格、年付IPLC与午间记录', '浪网9款套餐与60节点记录，附BGP、SS、年付IPLC及各平台使用教程。', body)
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/langwang-profile.css"><link rel="stylesheet" href="assets/invisible-latency.css"><link rel="stylesheet" href="assets/langwang-latency.css"></head>', 1)
    html = html.replace('</body>', '<script src="assets/langwang-latency.js" defer></script></body>', 1)
    write_changed(root/brand['profile_path'], html)
