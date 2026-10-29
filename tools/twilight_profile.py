"""Build the Twilight page using only its own supplied service materials."""
from hashlib import sha256
from html import escape as e
from pathlib import Path
import json
import re

from site_chrome import header, footer, write_changed
from twilight_plans import render_plans, render_usage_rules, floating_recommendation, plan_faqs, plans_csv, plans_markdown
from twilight_access import render_access, access_faqs, access_markdown, access_summary


def twilight_faqs(data,plans,access):
    counted='、'.join(item['name']+str(item['reported_node_count'])+'个' for item in data['regions'] if item['reported_node_count'] is not None)
    other='、'.join(item['name'] for item in data['regions'] if item['reported_node_count'] is None)
    return [
        ('暮光网络采用什么线路？', '站长提供的服务介绍说明采用全IPLC专线。本页据此整理线路方向，实际连接表现需结合所在地、运营商、节点与时段记录。'),
        ('单节点峰值最高2.5Gbps，应该怎样理解？', '2.5Gbps是资料列明的单节点峰值规格，描述服务提供的网络规格，不等于每位用户在任意时段持续获得的下载速度。实际速度需要在具体条件下另行测量。'),
        ('暮光网络有哪些节点地区和数量？', '本次资料列明'+counted+'；另外包括'+other+'等地区。后8个地区没有提供节点数量，按名称保留，具体可用节点以后台当时显示为准。'),
        ('暮光网络限制同时连接的客户端数量吗？', '资料说明不限制同时使用客户端数量，支持多设备在线。Windows、macOS和安卓客户端均为暮光加速，支持从官网首页下载；iOS使用Nextin，登录前填写识别码mgjs。'),
        ('暮光网络Windows、macOS和安卓客户端叫什么，如何连接？', 'Windows、macOS和安卓客户端均为暮光加速，可从暮光官网首页直接下载。打开客户端，使用官网账号登录后，选择需要的节点，再点击连接。版本和系统要求按官方指引核对。'),
        ('暮光网络iOS使用什么客户端，识别码是什么？', 'iOS使用Nextin应用，先填写品牌识别码mgjs，再使用官网账号登录，选择节点后点击连接。iOS下载入口与版本要求以官方指引为准。'),
        ('暮光网络什么情况可以退款，多久内申请？', data['refund_policy']['description']),
        ('暮光网络支持哪些流媒体与AI平台？', '站长提供的服务介绍列明Netflix、Disney+、ChatGPT与TikTok等平台。这里记录服务说明，本页另列上海电信网络、新加坡节点下的ChatGPT问答反馈，时间为2026-10-29 23:00；其余平台按服务说明列示。'),
        ('暮光网络的原生IP是否等于独享IP或住宅IP？', '品牌基础资料说明原生IP线路；独享私人定制节点另行列明独立公网IP与独立带宽，不与他人共享。普通套餐与独享定制分别核对，本次没有确认住宅IP属性。'),
        ('这份暮光网络介绍包含实际使用和测速记录吗？', access_summary(access)+'本条是实际问答反馈，尚未提供暮光网络的延迟、下载或上传速度数据。')
    ]+plan_faqs(plans)+access_faqs(access)


def build_twilight_profile(root):
    root=Path(root)
    data=json.loads((root/'data/muguang-profile.json').read_text(encoding='utf-8'))
    plans=json.loads((root/'data/muguang-plans.json').read_text(encoding='utf-8'))
    access=json.loads((root/'data/muguang-access-records.json').read_text(encoding='utf-8'))
    url=e(data['entry_url'],quote=True)
    counted=[item for item in data['regions'] if item['reported_node_count'] is not None]
    others=[item for item in data['regions'] if item['reported_node_count'] is None]
    region_cards=''.join('<article class="twilight-region"><h3>'+e(item['name'])+'</h3><strong>'+str(item['reported_node_count'])+'<small>个</small></strong></article>' for item in counted)
    region_chips=''.join('<span>'+e(item['name'])+'</span>' for item in others)
    platforms=''.join('<article><span>'+e(item['category'])+'</span><h3>'+e(item['name'])+'</h3></article>' for item in data['platforms'])
    questions=''.join('<details class="twilight-faq"><summary>'+e(question)+'</summary><p>'+e(answer)+'</p></details>' for question,answer in twilight_faqs(data,plans,access))
    access_section=render_access(access)
    plan_sections=render_plans(plans,url)
    usage_rules=render_usage_rules(plans)
    refund_description=e(data['refund_policy']['description'])
    windows=next(client for client in data['clients'] if client['platform']=='Windows')
    windows_name=e(windows['display_name'])
    ios=next(client for client in data['clients'] if client['platform']=='iOS')
    ios_name=e(ios['display_name'])
    ios_code=e(ios['brand_code'])
    windows_steps=''.join('<article><span>步骤 '+str(index)+'</span><h3>'+e(step)+'</h3><p>'+e(note)+'</p></article>' for index,(step,note) in enumerate(zip(windows['connection_steps'],['打开对应系统的'+windows['display_name']+'，使用官网账号登录。','登录后选择需要使用的节点。','选好节点后点击连接，开始使用。']),1))
    body=f'''<section class="twilight-hero" id="twilight-about"><span class="overline">TWILIGHT / CONNECTION PROFILE</span><div class="twilight-hero-heading"><div><h1>暮光网络</h1><p class="twilight-tagline">IPLC专线与原生IP，面向多端日常。</p></div><span class="twilight-intro-stamp">线路 · 地区 · 使用方向</span></div><p class="twilight-intro">{e(data['intro'])}</p><div class="twilight-hero-facts"><div><span>线路方案</span><strong>IPLC专线</strong></div><div><span>资料列明的单节点峰值</span><strong>2.5<small>Gbps</small></strong></div><div><span>同时使用客户端数量</span><strong>不限数量</strong></div></div><div class="twilight-actions"><a class="btn" href="{url}" target="_blank" rel="sponsored noopener noreferrer">访问暮光网络入口 <span aria-hidden="true">↗</span></a><a href="#twilight-regions">查看节点地区 →</a></div><p class="twilight-date">服务资料由博客站长提供 · 整理日期：{data['updated_on']}</p></section>
<nav class="twilight-jumps" aria-label="暮光网络页面目录"><a href="#twilight-about">品牌介绍</a><a href="#twilight-plans">9款套餐</a><a href="#twilight-plan-comparison">价格对比</a><a href="#twilight-plan-guide">如何选择</a><a href="#twilight-clients">使用教程</a><a href="#twilight-traffic">流量规则</a><a href="#twilight-support">售后退款</a><a href="#twilight-service">线路与设备</a><a href="#twilight-regions">节点地区</a><a href="#twilight-platforms">平台支持</a><a href="#twilight-access-records">ChatGPT记录</a><a href="#twilight-faq">常见问题</a><a href="#twilight-sources">资料来源</a></nav>
{plan_sections}
<section class="section" id="twilight-clients"><div class="twilight-section-title"><span class="overline">WINDOWS, MACOS & ANDROID / GET CONNECTED</span><h2>暮光加速：Windows、macOS与安卓使用教程</h2><p>三端均从暮光官网首页下载。打开对应系统的客户端，使用官网账号登录，选择节点后点击连接。</p></div><div class="twilight-plan-guide">{windows_steps}</div><div class="twilight-source-links"><a href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往暮光官网首页获取客户端 ↗</a></div><article class="twilight-plan-notes"><h3>iOS · {ios_name}</h3><p>iOS使用{ios_name}应用。先填写品牌识别码：<strong>{ios_code}</strong>，再使用官网账号登录，选择节点后点击连接。</p></article></section>
{usage_rules}
<section class="section" id="twilight-support"><div class="twilight-section-title"><span class="overline">SUPPORT / TECHNICAL REFUND</span><h2>技术问题先排查，退款条件与期限看清楚。</h2><p>登录暮光官网后台联系客服，说明遇到的使用问题。</p></div><article class="twilight-plan-notes"><h3>符合技术问题条件 · 购买后24小时内申请</h3><p>{refund_description}</p></article></section>
<section class="section" id="twilight-service"><div class="twilight-section-title"><span class="overline">NETWORK & MULTI-DEVICE USE</span><h2>把线路、IP与多端使用放在一起看。</h2><p>从网络规格到客户端数量，按提供的服务介绍逐项整理。</p></div><div class="twilight-service-grid"><article><span class="twilight-index">01 / NETWORK</span><h3>全IPLC专线</h3><p>资料以低延迟的跨地区连接为服务方向，列明单节点峰值最高2.5Gbps。峰值规格与用户实际下载速度分别记录。</p></article><article><span class="twilight-index">02 / NATIVE IP</span><h3>原生IP线路</h3><p>提供原生IP线路，服务介绍覆盖流媒体、AI工具与短视频平台等使用场景。IP具体属性按对应节点与套餐说明核对。</p></article><article><span class="twilight-index">03 / DEVICES</span><h3>多设备同时在线</h3><p>不限制同时使用客户端数量，支持不同设备在线使用。Windows、macOS和安卓均使用{windows_name}，从官网首页下载，使用官网账号登录后，选择节点并点击连接。</p></article><article><span class="twilight-index">04 / SUPPORT</span><h3>客服处理使用问题</h3><p>登录暮光官网后台联系客服，协助处理使用问题并申请符合条件的退款。私人定制需求通过工单沟通，响应时限按实际客服安排。</p></article></div></section>
<section class="section" id="twilight-regions"><div class="twilight-section-title"><span class="overline">REGIONS IN THE SUPPLIED MATERIALS</span><h2>七个地区列明数量，其他地区按名称记录。</h2><p>本次服务资料列出15个地区。以下7个地区提供具体节点数量。</p></div><div class="twilight-region-grid">{region_cards}</div><div class="twilight-other-regions"><h3>资料另外列明的地区</h3><div>{region_chips}</div></div><p class="twilight-note">其余8个地区未提供数量，不补造节点数。以上为资料中的地区分布，具体可用节点以后台当时显示为准。</p></section>
<section class="section" id="twilight-platforms"><div class="twilight-section-title"><span class="overline">STREAMING, AI & SHORT VIDEO</span><h2>围绕观看、问答与短视频的连接需求。</h2><p>以下平台来自站长提供的服务说明。</p></div><div class="twilight-platform-grid">{platforms}</div><p class="twilight-note">平台支持说明与实际使用记录分别整理；下方已列出2026-10-29 23:00上海电信、新加坡节点的ChatGPT问答反馈；其他平台尚待对应记录。</p></section>
{access_section}
<section class="section" id="twilight-faq"><div class="twilight-section-title"><span class="overline">TWILIGHT QUESTIONS & ANSWERS</span><h2>暮光网络常见问题</h2></div><div class="twilight-faqs">{questions}</div></section>
<section class="section" id="twilight-reading"><div class="twilight-section-title"><span class="overline">READ BEFORE COMPARING</span><h2>选择之前，把这些条件看清。</h2></div><div class="twilight-reading-grid"><a href="article-brand-record-template.html"><span>资料来源</span><strong>每个数字，找到对应出处。</strong><small>阅读品牌资料整理方法 →</small></a><a href="article-plan-comparison-sheet.html"><span>套餐比较</span><strong>把金额、额度与周期分开。</strong><small>阅读套餐对比指南 →</small></a><a href="article-fair-comparison.html"><span>连接记录</span><strong>比较表现，先确认相同条件。</strong><small>阅读同条件比较方法 →</small></a></div></section>
<section class="section" id="twilight-sources"><div class="twilight-section-title"><span class="overline">SOURCES & REVISIONS</span><h2>资料来源与更新说明</h2><p>本页依据{e(data['source'])}整理，日期为{data['updated_on']}；套餐部分另据站长提供的3张套餐截图与标准版240GB流量确认记录整理。内容涵盖IPLC线路、单节点峰值规格、原生IP、多设备并发、客服服务方向与节点地区。</p></div><p class="twilight-note">Windows、macOS和安卓的客户端名称、官网下载方式与连接流程已由站长确认。iOS使用Nextin，填写识别码mgjs后，使用官网账号登录、选择节点并点击连接。周期套餐的同价重置、提前续费与升级收费、周期和流量计算规则也已由站长确认。技术问题全额退款的适用条件、购买后24小时内的申请期限和官网后台客服入口也已确认。本页另收录2026-10-29 23:00上海电信、新加坡节点的ChatGPT实际问答反馈。iOS下载入口、优惠码、其他售后细则、Logo、其他平台使用记录及延迟和下载速度数据，将按后续资料补充。入口保留站长提供的原推广参数。</p><div class="twilight-source-links"><a href="data/muguang-profile.json">暮光网络资料 JSON ↓</a><a href="data/muguang-access-records.json">ChatGPT使用记录 JSON ↓</a><a href="data/muguang-plans.json">9款套餐资料 JSON ↓</a><a href="data/muguang-plans.csv" download>套餐对比表 CSV ↓</a><a href="{url}" target="_blank" rel="sponsored noopener noreferrer">暮光网络访问入口 ↗</a><a href="brands.html">返回品牌目录 →</a></div></section>'''
    css_revision=sha256((root/'assets/twilight.css').read_bytes()).hexdigest()[:12]
    description='暮光网络机场套餐与品牌介绍：年付109元、70GB每30天刷新；月付20至180元，覆盖120GB至1500GB。另有150GB、400GB、800GB不限时流量包及680元/月独享定制。对比9款价格、流量、刷新规则，了解IPLC、原生IP和节点地区。'
    page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>暮光网络机场套餐｜9款价格、IPLC专线与原生IP｜叮当观察</title><meta name="description" content="'+e(description,quote=True)+'"><link rel="stylesheet" href="assets/site-base.css"><link rel="stylesheet" href="assets/doraemon-theme.css"><link rel="stylesheet" href="assets/topics.css"><link rel="stylesheet" href="assets/invisible-access.css"><link rel="stylesheet" href="assets/twilight.css?v='+css_revision+'"></head><body><div class="shell">'+header('brands')+'<main>'+body+'</main>'+footer()+'</div></body></html>'
    float_js_revision=sha256((root/'assets/twilight-floating.js').read_bytes()).hexdigest()[:12]
    plans_js_revision=sha256((root/'assets/twilight-plans.js').read_bytes()).hexdigest()[:12]
    float_css_revision=sha256((root/'assets/invisible-floating.css').read_bytes()).hexdigest()[:12]
    page=page.replace('<link rel="stylesheet" href="assets/twilight.css', '<link rel="stylesheet" href="assets/invisible-floating.css?v='+float_css_revision+'"><link rel="stylesheet" href="assets/twilight.css',1)
    page=page.replace('<body>', '<body class="has-floating-promo has-twilight-floating">'+floating_recommendation(plans,url),1)
    page=page.replace('</body>', '<script src="assets/twilight-floating.js?v='+float_js_revision+'" defer></script><script src="assets/twilight-plans.js?v='+plans_js_revision+'" defer></script></body>',1)
    page=page.replace('href="#twilight-regions">查看节点地区 →', 'href="#twilight-plans">查看9款套餐 →',1)
    write_changed(root/'brand-muguang.html',page)
    for name in ('index.html','brands.html'):
        path=root/name
        original=path.read_text(encoding='utf-8')
        changed=re.sub(r'<a\b[^>]*href="brand-muguang\.html"[^>]*>.*?</a>',lambda match: re.sub(r'<p>.*?</p>','<p>IPLC专线 · 9款套餐与独享定制</p>',match[0],count=1,flags=re.S),original,flags=re.S)
        write_changed(path,changed)
    catalog_path=root/'data/brands.json'
    catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
    brand=next(item for item in catalog['brands'] if item['id']=='muguang')
    brand.update(profile_status='station_supplied_service_introduction',verification_status='station_provided_not_independently_verified',source_type=data['source'],source_date=data['updated_on'],line_type_from_materials=data['line_type'],listed_region_count=len(data['regions']),advertised_single_node_peak_gbps=data['advertised_single_node_peak_gbps'])
    brand['profile_status']='station_supplied_introduction_and_9_plans'
    brand['plan_count']=len(plans['plans'])
    brand['access_record_count']=len(access['records'])
    write_changed(catalog_path,json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    text='# 暮光网络\n\n整理日期：'+data['updated_on']+'。来源：'+data['source']+'。\n\n## 品牌介绍\n\n'+data['intro']+'\n\n'
    text+='## 服务规格\n\n- 线路：IPLC专线。\n- 资料列明的单节点峰值：最高2.5Gbps，不等于实测下载速度。\n- IP：原生IP线路。\n- 设备：不限制同时使用客户端数量，多设备在线。\n- 客服：登录官网后台联系客服；私人定制需求通过工单沟通，具体响应时限未提供。\n\n'
    text+='## Windows、macOS与安卓使用教程\n\n客户端名称：'+windows['display_name']+'。获取方式：'+windows['download_location']+'。\n\n'+''.join(str(index)+'. '+step+'。\n' for index,step in enumerate(windows['connection_steps'],1))+'\n'
    text+='## iOS客户端\n\n客户端：'+ios['display_name']+'。\n\n'+''.join(str(index)+'. '+step+'。\n' for index,step in enumerate(ios['connection_steps'],1))+'\n'
    text+='## 售后与技术问题退款\n\n'+data['refund_policy']['description']+'\n\n'
    text+=plans_markdown(plans)
    text+='## 节点地区\n\n| 地区 | 资料提供的节点数量 |\n| --- | --- |\n'
    text+=''.join('| '+item['name']+' | '+(str(item['reported_node_count']) if item['reported_node_count'] is not None else '未提供数量')+' |\n' for item in data['regions'])
    text+='\n## 平台支持方向\n\n'+ '、'.join(item['name'] for item in data['platforms'])+'。以上来自服务介绍，ChatGPT实际使用反馈另列。\n\n'
    text+=access_markdown(access)+'## 常见问题\n\n'
    text+=''.join('### '+question+'\n\n'+answer+'\n\n' for question,answer in twilight_faqs(data,plans,access))
    text+='## 访问入口\n\n[暮光网络访问入口]('+data['entry_url']+')。保留站长提供的推广参数。\n'
    folder=root/'content/brands'
    folder.mkdir(parents=True,exist_ok=True)
    write_changed(folder/'muguang.md',text)
    write_changed(root/'data/muguang-plans.csv',plans_csv(plans))


if __name__=='__main__':
    build_twilight_profile(Path(__file__).resolve().parents[1])
