"""Publish confirmed LadderCloud introduction, coverage and snapshot material."""
from html import escape as e
from pathlib import Path
import json

from site_chrome import shell, write_changed
from tiziyun_nodes import build_snapshot_assets, render_snapshot, validate_snapshot, time_label
from tiziyun_plans import build_plan_csv, render_plans, plan_faqs
from tiziyun_clients import render_clients, client_faqs
from tiziyun_coupon import validate_coupon, render_coupon, coupon_faqs
from tiziyun_service import validate_service, render_service, render_refund, service_faqs


def load(root,path):
    return json.loads((root/path).read_text(encoding='utf-8'))


def build_tiziyun_profile(root,brand):
    root=Path(root)
    overview=load(root,brand['overview_path'])
    coverage=load(root,brand['coverage_path'])
    snapshot=load(root,brand['latency_path'])
    plans=load(root,brand['plans_path'])
    clients=load(root,brand['clients_path']) if brand.get('clients_path') else None
    clients_ready=clients is not None and clients['collection_status']=='basic_flows_confirmed'
    coupon=load(root,brand['coupon_path']) if brand.get('coupon_path') else None
    coupon_ready=coupon is not None and coupon['collection_status']=='confirmed'
    rules=load(root,brand['service_rules_path']) if brand.get('service_rules_path') else None
    service_ready=rules is not None and rules['collection_status']=='core_rules_confirmed' and coupon_ready
    active_coupon=coupon if coupon_ready else None
    if coupon_ready:validate_coupon(coupon,plans['plans'])
    if service_ready:validate_service(rules,plans['plans'],coupon)
    validate_snapshot(snapshot)
    assert overview['collection_status']=='core_description_coverage_and_snapshot_confirmed'
    assert coverage['collection_status']=='regions_and_counts_confirmed'
    assert coverage['total_node_count']==snapshot['summary']['node_count']
    assert {r['id']:r['node_count'] for r in coverage['regions']}=={r['id']:r['node_count'] for r in snapshot['regions']}
    build_snapshot_assets(root,snapshot)
    build_plan_csv(root,plans,active_coupon)
    entry=e(brand['url'],quote=True)
    mark=('<img class="tiziyun-mark" src="'+e(brand['logo_path'],quote=True)+'" width="'+str(brand['logo_width'])+'" height="'+str(brand['logo_height'])+'" alt="梯子云Logo" decoding="async">'
          if brand.get('logo_path') else '<span class="tiziyun-mark" aria-hidden="true">梯</span>')
    features=[('BGP 多线入口','品牌介绍列明智能多线入口与专线中继互联；高阶套餐详情另列IEPL骨干，线路条目按各套餐资料保留。'),
              ('SS 节点协议','站长已确认节点使用 Shadowsocks（SS）协议。'),
              ('平台使用方向','品牌资料列出4K流媒体、TikTok跨境运营与AI生产力工具交互等方向；相应任务反馈继续补充。')]
    feature_cards=''.join('<article><span class="overline">0'+str(i)+' / BRAND MATERIAL</span><h3>'+e(title)+'</h3><p>'+e(text)+'</p></article>' for i,(title,text) in enumerate(features,1))
    region_cards=''.join('<li><h3>'+e(r['name'])+'</h3><p><strong>'+str(r['node_count'])+'</strong><span>个节点</span></p></li>' for r in coverage['regions'])
    counts='、'.join(r['name']+str(r['node_count'])+'个' for r in coverage['regions'])
    plans_note='已整理站长确认的9款套餐截图报价与额度。其他付款周期总额、优惠以及使用与售后规则继续补充。'
    if service_ready:
        plans_note='9款报价、流量额度、优惠与主要业务规则已整理。四款月付方案的季付、半年付和年付总额未提供，请在官网订单页核对。'
    questions=[
        ('梯子云使用什么线路和节点协议？','站长提供的线路介绍为BGP智能多线入口与专线中继互联，节点协议另已确认为Shadowsocks（SS）。本页按品牌说明保留这些信息。'),
        ('梯子云覆盖哪些地区，有多少个节点？','站长于'+coverage['confirmed_on']+'确认这5张截图为完整列表，共50个节点：'+counts+'。按节点实际名称统计，编号空缺不补写。'),
        ('这批延迟记录是在什么条件下取得的？',time_label(snapshot)+'，'+snapshot['location']+snapshot['isp']+'，'+snapshot['client']+'。日期、下午时段、所在地、运营商与客户端由站长逐项确认；具体时刻、版本和探测方法未提供。'),
        ('哪些节点显示超时，统计时如何处理？','新加坡09与香港13显示Timeout。50个节点中48条有数值，范围51—479ms，中位数143.5ms；超时保留为独立状态，不按0ms参与数值统计。'),
        ('香港01为什么没有按位置改成香港16？','截图4第五行左侧原名为香港01，数值147ms，因此按原名保留。列表中未出现的编号不补写，避免把整理者的推测当作原始数据。'),
        ('下午的截图能说明晚高峰长期表现吗？','本批记录对应2026年11月3日下午的一次截图。品牌介绍中的晚高峰表现说明还需要对应时段与连续观察材料；本页保留下午数值与超时，不据此生成长期可用率或性能排名。'),
        ('梯子云支持4K播放、TikTok和AI工具，是否都有实际任务记录？','这些是品牌介绍中列出的使用方向。目前提供的是客户端节点延迟截图；实际播放、账号任务或AI问答结果需按具体平台、日期和节点另行记录。'),
        ('梯子云有没有已确认的优惠与售后规则？','已确认2hy85八五折优惠的适用范围、续费和四款月付重置包优惠，支持支付宝付款，并列明普通周期套餐的流量规则与购买后24小时内的技术问题退款条件。' if service_ready else '当前已提供9款截图报价，优惠、付款、续费重置及退款规则继续逐项确认。选购时请核对官网订单和服务条件。')]+plan_faqs(plans,active_coupon)+(client_faqs(clients) if clients_ready else [])+(coupon_faqs(coupon) if coupon_ready else [])+(service_faqs(rules,coupon) if service_ready else [])
    faq=''.join('<details class="tiziyun-faq"><summary>'+e(q)+'</summary><p>'+e(answer)+'</p></details>' for q,answer in questions)
    body='''<section class="info-hero tiziyun-hero" id="tiziyun-about"><span class="info-kicker">LADDERCLOUD / BGP & SS</span><div class="tiziyun-heading">'''+mark+'''<div><h1>梯子云 LadderCloud</h1><p>BGP智能多线入口 · 专线中继互联 · SS节点协议</p></div></div><p>'''+e(overview['editorial_description'])+'''</p><div class="contact-buttons"><a class="contact-action" href="#tiziyun-latency">查看50节点文字图表 →</a><a class="copy-contact" href="'''+entry+'''" target="_blank" rel="sponsored noopener noreferrer">访问梯子云推广入口 ↗</a></div><p class="tiziyun-source-date">资料由站长提供并逐项确认 · 更新：'''+e(overview['updated_on'])+'''</p></section>
<nav class="tiziyun-jumps" aria-label="梯子云页面重点内容"><a href="#tiziyun-intro">线路与使用方向</a><a href="#tiziyun-coverage">五地区节点覆盖</a><a href="#tiziyun-latency">下午延迟记录</a><a href="#tiziyun-materials">套餐与待补资料</a><a href="#tiziyun-faq">常见问题</a><a href="#tiziyun-sources">资料来源</a></nav>
<section class="section" id="tiziyun-intro"><span class="overline">CONFIRMED BRAND MATERIALS</span><h2 id="quick-section-1">目前已确认的资料</h2><div class="tiziyun-feature-grid">'''+feature_cards+'''</div><p class="tiziyun-note">线路、协议与平台方向按站长提供的资料整理。下方节点记录注明了独立的采样条件和统计范围。</p></section>
<section class="section" id="tiziyun-coverage" aria-labelledby="tiziyun-coverage-title"><span class="overline">5 REGIONS / 50 NODES</span><h2 id="tiziyun-coverage-title">5个地区，50个节点。</h2><p class="tiziyun-lead">完整性与各地区数量由站长于'''+e(coverage['confirmed_on'])+'''确认。香港13个、台湾10个、日本10个、新加坡10个、美国7个。</p><ul class="tiziyun-coverage-grid">'''+region_cards+'''</ul><p class="tiziyun-note">节点名称按截图原样保留。<a href="data/tiziyun-coverage.json">查看完整节点覆盖来源 JSON ↓</a></p></section>
'''+render_snapshot(snapshot)+'''
<section class="section" id="tiziyun-materials"><span class="overline">PLANS & USING THE SERVICE</span><h2 id="quick-section-2">选择前先核对什么</h2><div class="tiziyun-pending"><h3>套餐资料继续补充</h3><p>'''+e(plans_note)+'''</p><p>各平台下载安装与连接流程、付款方式、优惠以及续费和售后条件，按梯子云自己的资料继续确认。选购前先查看所选套餐的官网说明。</p><a href="'''+entry+'''" target="_blank" rel="sponsored noopener noreferrer">前往梯子云推广入口 ↗</a></div></section>
<section class="section" id="tiziyun-faq"><span class="overline">LADDERCLOUD QUESTIONS</span><h2 id="tiziyun-faq-title">梯子云节点与使用资料常见问题</h2>'''+faq+'''</section>
<section class="section" id="tiziyun-sources"><span class="overline">SOURCES & SCOPE</span><h2 id="tiziyun-sources-title">资料来源与适用范围</h2><p class="tiziyun-lead">品牌介绍、BGP线路与SS协议由站长提供；9款套餐来源为3张套餐图，按可见报价与说明整理。节点数据来自5张截图，站长另行确认其为完整列表，并逐项补充采样日期、下午时段、上海电信与Windows版梯子云客户端。本页为资料整理，本站未独立复测。</p><p class="tiziyun-note">图表与下载数据依据原始名称和数值重绘。平台方向与下午延迟各按自身来源阅读，后续补充对应任务的实际使用反馈。此页外部入口为站长提供的推广链接。</p><div class="tiziyun-source-links"><a href="data/tiziyun-overview.json">品牌介绍源资料 JSON ↓</a><a href="data/tiziyun-latency.json">节点记录与统计说明 JSON ↓</a><a href="data/tiziyun-latency.csv" download>50节点对照表 CSV ↓</a><a href="assets/tiziyun-latency-overview.svg" download>高清概览图 SVG ↓</a><a href="topic-reviews-guide.html">机场测评与证据范围 →</a><a href="brands.html">返回品牌目录 →</a></div></section>'''
    body=body.replace('<section class="section" id="tiziyun-coverage"',render_plans(plans,brand['url'],active_coupon)+'\n<section class="section" id="tiziyun-coverage"',1)
    body=body.replace('<a href="#tiziyun-coverage">五地区节点覆盖</a>','<a href="#tiziyun-plans">9款套餐与报价</a><a href="#tiziyun-plan-comparison">价格对照表</a><a href="#tiziyun-coverage">五地区节点覆盖</a>',1)
    body=body.replace('<a class="contact-action" href="#tiziyun-latency">查看50节点文字图表 →</a>','<a class="contact-action" href="#tiziyun-plans">查看9款套餐 →</a><a class="copy-contact" href="#tiziyun-latency">查看50节点记录 →</a>',1)
    body=body.replace('<h3>套餐资料继续补充</h3>','<h3>使用条件与售后规则继续补充</h3>',1)
    body=body.replace('<a href="data/tiziyun-overview.json">品牌介绍源资料 JSON ↓</a>','<a href="data/tiziyun-overview.json">品牌介绍源资料 JSON ↓</a><a href="data/tiziyun-plans.json">9款套餐源资料 JSON ↓</a><a href="data/tiziyun-plans.csv" download>套餐对照表 CSV ↓</a>',1)
    if clients_ready:
        body=body.replace('<section class="section" id="tiziyun-materials">',render_clients(clients,brand['url'])+'\n<section class="section" id="tiziyun-materials">',1)
        body=body.replace('<a href="#tiziyun-materials">套餐与待补资料</a>','<a href="#tiziyun-clients">各平台使用教程</a><a href="#tiziyun-materials">使用与售后资料</a>',1)
        body=body.replace('各平台下载安装与连接流程、付款方式、优惠以及续费和售后条件，按梯子云自己的资料继续确认。选购前先查看所选套餐的官网说明。','各平台下载、登录与连接流程已整理于上方教程。付款方式、优惠以及流量重置、续费、升级和退款条件，继续按梯子云自身资料逐项确认。选购前请查看所选套餐的官网说明。',1)
        body=body.replace('本页为资料整理，本站未独立复测。','各平台客户端下载、登录与连接流程另由站长逐项确认。本页为资料整理，本站未独立复测。',1)
        body=body.replace('<a href="data/tiziyun-plans.json">9款套餐源资料 JSON ↓</a>','<a href="data/tiziyun-plans.json">9款套餐源资料 JSON ↓</a><a href="data/tiziyun-clients.json">四个平台客户端资料 JSON ↓</a>',1)
    if coupon_ready:
        body=body.replace('<section class="section" id="tiziyun-plans"',render_coupon(coupon)+'\n<section class="section" id="tiziyun-plans"',1)
        body=body.replace('<a href="#tiziyun-plans">9款套餐与报价</a>','<a href="#tiziyun-coupon">八五折优惠范围</a><a href="#tiziyun-plans">9款套餐与报价</a>',1)
        body=body.replace('<a class="contact-action" href="#tiziyun-plans">查看9款套餐 →</a>','<a class="contact-action" href="#tiziyun-coupon">查看八五折优惠 →</a>',1)
        body=body.replace('<a href="data/tiziyun-plans.json">9款套餐源资料 JSON ↓</a>','<a href="data/tiziyun-plans.json">9款套餐源资料 JSON ↓</a><a href="data/tiziyun-coupon.json">优惠与适用范围 JSON ↓</a>',1)
    if service_ready:
        body=body.replace('<section class="section" id="tiziyun-materials">',render_service(rules,coupon)+'\n'+render_refund(rules,brand['url'])+'\n<section class="section" id="tiziyun-materials">',1)
        body=body.replace('<a href="#tiziyun-faq">常见问题</a>','<a href="#tiziyun-service">流量与付款规则</a><a href="#tiziyun-refund">技术问题退款</a><a href="#tiziyun-faq">常见问题</a>',1)
        body=body.replace('<h3>使用条件与售后规则继续补充</h3>','<h3>选购前核对订单说明</h3>',1)
        body=body.replace('各平台下载、登录与连接流程已整理于上方教程。付款方式、优惠以及流量重置、续费、升级和退款条件，继续按梯子云自身资料逐项确认。选购前请查看所选套餐的官网说明。','各平台基础流程、支付宝付款、优惠及普通周期套餐的重置、续费、升级和技术问题退款条件已整理。其他付款周期总额、版本要求与退款到账安排，请在官网订单和客服说明中核对。',1)
        body=body.replace('本页为资料整理，本站未独立复测。','优惠、付款、流量与技术问题退款规则由站长于'+e(rules['confirmed_on'])+'逐项确认。本页为资料整理，本站未独立复测。',1)
        body=body.replace('<a href="data/tiziyun-plans.json">9款套餐源资料 JSON ↓</a>','<a href="data/tiziyun-plans.json">9款套餐源资料 JSON ↓</a><a href="data/tiziyun-service-rules.json">付款、流量与售后规则 JSON ↓</a>',1)
    html=shell('梯子云 LadderCloud套餐与优惠码｜9款价格及节点记录','梯子云9款套餐、2hy85八五折适用范围及50节点下午记录，附各平台使用流程与技术问题退款条件。',body)
    styles='<link rel="stylesheet" href="assets/tiziyun-profile.css"><link rel="stylesheet" href="assets/invisible-latency.css"><link rel="stylesheet" href="assets/tiziyun-latency.css">'
    html=html.replace('</head>',styles+'</head>',1)
    html=html.replace('</body>','<script src="assets/tiziyun-latency.js" defer></script></body>',1)
    if coupon_ready:html=html.replace('</body>','<script src="assets/tiziyun-coupon.js" defer></script></body>',1)
    write_changed(root/brand['profile_path'],html)
