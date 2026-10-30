"""Build Lingdong's first profile only from its own supplied brand materials."""
from hashlib import sha256
from html import escape as e
from pathlib import Path
import json
import re

from site_chrome import header, footer, write_changed
from lingdong_plans import render_plans, render_floating, plan_faqs, plans_csv, plans_markdown


def lingdong_faqs(data,plans):
    counted='、'.join(r['name']+str(r['reported_node_count'])+'个' for r in data['regions'] if r['reported_node_count'] is not None)
    return [
        ('灵动云主要面向哪些使用场景？','主要面向网页浏览、社交、短视频与追剧，也提供流媒体与AI工具访问的服务方向。可以结合自身用量、节点地区和平台需求了解对应服务。'),
        ('灵动云采用什么线路？','品牌介绍采用BGP多网专线，具体套餐线路按对应资料分别核对，不从其他品牌推断灵动云的网络架构。'),
        ('高峰不限速是否等于始终固定速度？','不是。不限速是服务资料中的速率政策表述。实际连接表现与所在地、运营商、节点、设备和时段有关，需要对应条件下的延迟或速度记录。'),
        ('灵动云1.0x流量计费怎样理解？','1.0x表示按该倍率计算流量消耗。例如以10GB为示意用量，按1.0x计算为10GB。这个示例只解释计费倍率，不代表某款套餐额度，也不是网速提升倍数。'),
        ('灵动云支持哪些流媒体和AI平台？','服务资料列明Netflix、Disney+、HBO，以及ChatGPT和Claude。4K/8K属于资料中的视频支持方向；尚未提供实际播放或问答记录，不由介绍推断所有节点、功能和时段的结果。'),
        ('纯净IP优化是否等于原生IP、独享IP或住宅IP？','品牌介绍说明纯净IP优化。套餐资料另列驭浪、穿云的原生IP，以及至尊私人定制的独立公网IP与独立带宽，应按套餐分别核对。本次未确认住宅IP属性。'),
        ('SS是客户端名称吗，支持多设备吗？','SS指Shadowsocks协议，不是专属客户端名称。资料说明支持多设备同时在线、不限制设备连接数量；具体系统的软件名称、下载与登录连接流程按后续品牌指引补充。'),
        ('灵动云覆盖哪些节点地区？','资料列明'+counted+'；另有马来西亚、越南、菲律宾、泰国、印度、德国、法国、英国等地区。后8个地区未提供数量，具体可用节点以后台显示为准。'),
        ('这份灵动云介绍包含独立测速或播放验证吗？','当前内容来自站长提供的品牌介绍与节点资料，尚无本品牌实际延迟、下载速度、流媒体播放或AI问答记录。后续记录将分别注明日期、网络、节点与完成的操作。')
    ]+plan_faqs(plans)


def build_lingdong_profile(root):
    root=Path(root)
    data=json.loads((root/'data/lingdongyun-profile.json').read_text(encoding='utf-8'))
    plans=json.loads((root/'data/lingdongyun-plans.json').read_text(encoding='utf-8'))
    url=e(data['entry_url'],quote=True)
    counted=[r for r in data['regions'] if r['reported_node_count'] is not None]
    others=[r for r in data['regions'] if r['reported_node_count'] is None]
    region_cards=''.join('<article class="lingdong-region"><h3>'+e(r['name'])+'</h3><strong>'+str(r['reported_node_count'])+'<small>个</small></strong></article>' for r in counted)
    region_chips=''.join('<span>'+e(r['name'])+'</span>' for r in others)
    streaming=''.join('<span>'+e(name)+'</span>' for name in data['declared_streaming_platforms'])
    ai=''.join('<span>'+e(name)+'</span>' for name in data['declared_ai_platforms'])
    questions=''.join('<details class="lingdong-faq"><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in lingdong_faqs(data,plans))
    plan_sections=render_plans(plans,url)
    body=f'''<section class="lingdong-hero" id="lingdong-about"><span class="overline">LINGDONG / EVERYDAY CONNECTION</span><div class="lingdong-hero-grid"><div class="lingdong-hero-copy"><h1>灵动云</h1><p class="lingdong-tagline">从日常浏览，到影音与AI。</p><p class="lingdong-intro">{e(data['intro'])}</p><div class="lingdong-actions"><a class="btn" href="{url}" target="_blank" rel="sponsored noopener noreferrer">访问灵动云入口 <span aria-hidden="true">↗</span></a><a href="#lingdong-plans">查看9款套餐 →</a></div></div><dl class="lingdong-brief" aria-label="灵动云方案要点"><div><dt>线路方案</dt><dd>BGP多网专线</dd></div><div><dt>流量倍率</dt><dd>1.0<small>x</small></dd></div><div><dt>接入协议</dt><dd>SS</dd></div><div><dt>设备连接</dt><dd>不限数量</dd></div></dl></div><p class="lingdong-date">资料由博客站长提供 · 整理日期：{data['updated_on']}</p></section>
<nav class="lingdong-jumps" aria-label="灵动云页面目录"><a href="#lingdong-about">品牌介绍</a><a href="#lingdong-plans">9款套餐</a><a href="#lingdong-plan-comparison">价格对比</a><a href="#lingdong-plan-guide">如何选择</a><a href="#lingdong-connection">线路与接入</a><a href="#lingdong-platforms">使用方向</a><a href="#lingdong-regions">节点地区</a><a href="#lingdong-faq">常见问题</a><a href="#lingdong-sources">资料来源</a></nav>
{plan_sections}
<section class="section" id="lingdong-connection"><div class="lingdong-section-title"><span class="overline">NETWORK, TRAFFIC & DEVICES</span><h2>连接、用量、设备，分别看清。</h2><p>按灵动云提供的服务资料，整理选择之前需要了解的三项条件。</p></div><div class="lingdong-connection-grid"><article><span class="lingdong-index">01 / NETWORK</span><h3>BGP多网专线</h3><p>服务介绍列明专线不限速、高峰不限速，面向日常网络连接需求。实际延迟与下载表现需要结合具体网络和时段记录。</p></article><article><span class="lingdong-index">02 / TRAFFIC</span><h3>1.0x流量计费</h3><p>流量按1.0x倍率计算，便于按实际消耗了解用量。倍率说明计费关系，套餐额度与刷新周期按对应套餐分别核对。</p></article><article><span class="lingdong-index">03 / ACCESS</span><h3>SS协议，多设备在线</h3><p>资料说明SS协议全平台兼容，不限制设备连接数量。具体软件、系统版本和操作流程，按灵动云自身的客户端指引补充。</p></article></div></section>
<section class="section" id="lingdong-platforms"><div class="lingdong-section-title"><span class="overline">STREAMING & AI / USE CASES</span><h2>从追剧观看，到对话与辅助工作。</h2><p>以下为服务介绍列明的平台与使用方向。</p></div><div class="lingdong-platform-panels"><article><span class="lingdong-index">STREAMING</span><h3>观看与追剧</h3><div class="lingdong-platform-tags">{streaming}</div><p>围绕日常流媒体观看需求，资料提到4K与8K内容支持。具体节点与播放结果可在实际使用记录中分别验证。</p></article><article><span class="lingdong-index">AI TOOLS</span><h3>对话与辅助工作</h3><div class="lingdong-platform-tags">{ai}</div><p>以纯净IP优化为服务方向，面向AI工具的日常访问。IP具体属性、账户功能与实际问答结果按对应条件分别确认。</p></article></div></section>
<section class="section" id="lingdong-regions"><div class="lingdong-section-title"><span class="overline">REGIONS IN THE SUPPLIED MATERIALS</span><h2>节点地区，按资料逐项列明。</h2><p>本次资料覆盖15个地区，其中7个列明节点数量。</p></div><div class="lingdong-region-grid">{region_cards}</div><div class="lingdong-other-regions"><h3>资料另外列明的地区</h3><div>{region_chips}</div></div><p class="lingdong-note">其余8个地区仅提供名称，具体可用节点以后台当时显示为准。</p></section>
<section class="section" id="lingdong-faq"><div class="lingdong-section-title"><span class="overline">LINGDONG QUESTIONS & ANSWERS</span><h2>灵动云常见问题</h2></div><div class="lingdong-faqs">{questions}</div></section>
<section class="section" id="lingdong-sources"><div class="lingdong-section-title"><span class="overline">SOURCES & REVISIONS</span><h2>资料来源与更新说明</h2><p>本页依据{e(data['source'])}整理，日期为{data['updated_on']}。内容涵盖BGP多网专线、1.0x计费、SS协议、多设备使用、平台支持方向与节点地区。</p></div><p class="lingdong-note">套餐部分依据站长提供的6张图片整理为9款，包含月付、年付、一次性与私人定制；原图片只作资料来源。客户端流程、优惠码、售后规则、Logo和实际测试记录，将按后续资料补充。访问入口保留站长提供的原推广参数。</p><div class="lingdong-source-links"><a href="data/lingdongyun-profile.json">灵动云资料 JSON ↓</a><a href="data/lingdongyun-plans.json">9款套餐资料 JSON ↓</a><a href="data/lingdongyun-plans.csv" download>套餐对比表 CSV ↓</a><a href="{url}" target="_blank" rel="sponsored noopener noreferrer">灵动云访问入口 ↗</a><a href="brands.html">返回品牌目录 →</a></div></section>'''
    revision=sha256((root/'assets/lingdong.css').read_bytes()).hexdigest()[:12]
    description='灵动云机场套餐价格：4款月付20至180元，穿云99元/年、70GB每30天刷新，折合8.25元/月。对比9款周期、不限时与私人定制套餐，了解BGP多网专线、SS协议、节点地区和平台支持方向。'
    page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>灵动云机场套餐｜9款价格、BGP专线与SS协议｜叮当观察</title><meta name="description" content="'+e(description,quote=True)+'"><link rel="stylesheet" href="assets/site-base.css"><link rel="stylesheet" href="assets/doraemon-theme.css"><link rel="stylesheet" href="assets/topics.css"><link rel="stylesheet" href="assets/lingdong.css?v='+revision+'"></head><body><div class="shell">'+header('brands')+'<main>'+body+'</main>'+footer()+'</div></body></html>'
    plans_revision=sha256((root/'assets/lingdong-plans.css').read_bytes()).hexdigest()[:12]
    floating_revision=sha256((root/'assets/lingdong-floating.js').read_bytes()).hexdigest()[:12]
    filters_revision=sha256((root/'assets/lingdong-plans.js').read_bytes()).hexdigest()[:12]
    floating_css_revision=sha256((root/'assets/invisible-floating.css').read_bytes()).hexdigest()[:12]
    page=page.replace('</head>','<link rel="stylesheet" href="assets/invisible-floating.css?v='+floating_css_revision+'"><link rel="stylesheet" href="assets/lingdong-plans.css?v='+plans_revision+'"></head>',1)
    page=page.replace('<body>','<body class="has-floating-promo has-lingdong-floating">'+render_floating(plans,url),1)
    page=page.replace('</body>','<script src="assets/lingdong-floating.js?v='+floating_revision+'" defer></script><script src="assets/lingdong-plans.js?v='+filters_revision+'" defer></script></body>',1)
    write_changed(root/'brand-lingdongyun.html',page)
    for name in ('index.html','brands.html'):
        path=root/name
        original=path.read_text(encoding='utf-8')
        changed=re.sub(r'<a\b[^>]*href="brand-lingdongyun\.html"[^>]*>.*?</a>',lambda match: re.sub(r'<p>.*?</p>','<p>BGP专线 · 9款套餐与独享定制</p>',match[0],count=1,flags=re.S),original,flags=re.S)
        write_changed(path,changed)
    catalog_path=root/'data/brands.json'
    catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
    brand=next(x for x in catalog['brands'] if x['id']=='lingdongyun')
    brand.update(profile_status='station_supplied_service_introduction',verification_status='station_provided_not_independently_verified',source_type=data['source'],source_date=data['updated_on'],line_type_from_materials=data['line_type'],listed_region_count=len(data['regions']),traffic_multiplier=data['traffic_multiplier'],protocol=data['protocol'])
    brand['page_observation']='已按站长提供的品牌介绍与节点地区资料整理，尚无本品牌实际测速或平台操作记录。'
    brand['profile_status']='station_supplied_introduction_and_9_plans'
    brand['plan_count']=len(plans['plans'])
    write_changed(catalog_path,json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    text='# 灵动云\n\n整理日期：'+data['updated_on']+'。来源：'+data['source']+'。\n\n## 品牌介绍\n\n'+data['intro']+'\n\n'
    text+='## 方案要点\n\n- 线路：BGP多网专线。\n- 速率政策：资料写明专线不限速、高峰不限速，不作为实际速度记录。\n- 流量：1.0x计费。\n- 协议：SS（Shadowsocks）。\n- 设备：不限制连接数量，支持多设备同时在线。\n- IP：品牌资料说明纯净IP优化；驭浪、穿云资料列明原生IP，至尊私人定制单独列明独立公网IP。\n\n'
    text+=plans_markdown(plans)
    text+='## 节点地区\n\n| 地区 | 资料提供的节点数量 |\n| --- | --- |\n'+''.join('| '+r['name']+' | '+(str(r['reported_node_count']) if r['reported_node_count'] is not None else '未提供数量')+' |\n' for r in data['regions'])
    text+='\n## 平台支持方向\n\n流媒体：'+ '、'.join(data['declared_streaming_platforms'])+'；资料提到4K/8K。AI：'+ '、'.join(data['declared_ai_platforms'])+'。以上来自服务介绍，尚无实际播放或问答记录。\n\n## 常见问题\n\n'
    text+=''.join('### '+q+'\n\n'+a+'\n\n' for q,a in lingdong_faqs(data,plans))
    text+='## 访问入口\n\n[灵动云访问入口]('+data['entry_url']+')。保留站长提供的原推广参数。\n'
    folder=root/'content/brands'
    folder.mkdir(parents=True,exist_ok=True)
    write_changed(folder/'lingdongyun.md',text)
    write_changed(root/'data/lingdongyun-plans.csv',plans_csv(plans))


if __name__=='__main__':
    build_lingdong_profile(Path(__file__).resolve().parents[1])
