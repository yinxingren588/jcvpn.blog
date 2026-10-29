"""Build the Twilight page using only its own supplied service materials."""
from hashlib import sha256
from html import escape as e
from pathlib import Path
import json
import re

from site_chrome import header, footer, write_changed


def twilight_faqs(data):
    counted='、'.join(item['name']+str(item['reported_node_count'])+'个' for item in data['regions'] if item['reported_node_count'] is not None)
    other='、'.join(item['name'] for item in data['regions'] if item['reported_node_count'] is None)
    return [
        ('暮光网络采用什么线路？', '站长提供的服务介绍说明采用全IPLC专线。本页据此整理线路方向，实际连接表现需结合所在地、运营商、节点与时段记录。'),
        ('单节点峰值最高2.5Gbps，应该怎样理解？', '2.5Gbps是资料列明的单节点峰值规格，描述服务提供的网络规格，不等于每位用户在任意时段持续获得的下载速度。实际速度需要在具体条件下另行测量。'),
        ('暮光网络有哪些节点地区和数量？', '本次资料列明'+counted+'；另外包括'+other+'等地区。后8个地区没有提供节点数量，按名称保留，具体可用节点以后台当时显示为准。'),
        ('暮光网络限制同时连接的客户端数量吗？', '资料说明不限制同时使用客户端数量，支持多设备在线。各设备的具体客户端名称、下载入口和使用流程，将按暮光网络自身资料整理。'),
        ('暮光网络支持哪些流媒体与AI平台？', '站长提供的服务介绍列明Netflix、Disney+、ChatGPT与TikTok等平台。这里记录服务说明，逐平台使用记录需要另附日期、节点和完成的具体操作。'),
        ('暮光网络的原生IP是否等于独享IP或住宅IP？', '本次资料确认的是原生IP线路，没有确认独享IP或住宅IP。选择时应按具体套餐与节点说明分别核对这些属性。'),
        ('这份暮光网络介绍包含实际测试记录吗？', '目前整理的是站长提供的服务规格、节点分布及平台支持说明，本次未提供该品牌的延迟、下载速度或平台使用测试记录。')
    ]


def build_twilight_profile(root):
    root=Path(root)
    data=json.loads((root/'data/muguang-profile.json').read_text(encoding='utf-8'))
    url=e(data['entry_url'],quote=True)
    counted=[item for item in data['regions'] if item['reported_node_count'] is not None]
    others=[item for item in data['regions'] if item['reported_node_count'] is None]
    region_cards=''.join('<article class="twilight-region"><h3>'+e(item['name'])+'</h3><strong>'+str(item['reported_node_count'])+'<small>个</small></strong></article>' for item in counted)
    region_chips=''.join('<span>'+e(item['name'])+'</span>' for item in others)
    platforms=''.join('<article><span>'+e(item['category'])+'</span><h3>'+e(item['name'])+'</h3></article>' for item in data['platforms'])
    questions=''.join('<details class="twilight-faq"><summary>'+e(question)+'</summary><p>'+e(answer)+'</p></details>' for question,answer in twilight_faqs(data))
    body=f'''<section class="twilight-hero" id="twilight-about"><span class="overline">TWILIGHT / CONNECTION PROFILE</span><div class="twilight-hero-heading"><div><h1>暮光网络</h1><p class="twilight-tagline">IPLC专线与原生IP，面向多端日常。</p></div><span class="twilight-intro-stamp">线路 · 地区 · 使用方向</span></div><p class="twilight-intro">{e(data['intro'])}</p><div class="twilight-hero-facts"><div><span>线路方案</span><strong>IPLC专线</strong></div><div><span>资料列明的单节点峰值</span><strong>2.5<small>Gbps</small></strong></div><div><span>同时使用客户端数量</span><strong>不限数量</strong></div></div><div class="twilight-actions"><a class="btn" href="{url}" target="_blank" rel="sponsored noopener noreferrer">访问暮光网络入口 <span aria-hidden="true">↗</span></a><a href="#twilight-regions">查看节点地区 →</a></div><p class="twilight-date">服务资料由博客站长提供 · 整理日期：{data['updated_on']}</p></section>
<nav class="twilight-jumps" aria-label="暮光网络页面目录"><a href="#twilight-about">品牌介绍</a><a href="#twilight-service">线路与设备</a><a href="#twilight-regions">节点地区</a><a href="#twilight-platforms">平台支持</a><a href="#twilight-faq">常见问题</a><a href="#twilight-sources">资料来源</a></nav>
<section class="section" id="twilight-service"><div class="twilight-section-title"><span class="overline">NETWORK & MULTI-DEVICE USE</span><h2>把线路、IP与多端使用放在一起看。</h2><p>从网络规格到客户端数量，按提供的服务介绍逐项整理。</p></div><div class="twilight-service-grid"><article><span class="twilight-index">01 / NETWORK</span><h3>全IPLC专线</h3><p>资料以低延迟的跨地区连接为服务方向，列明单节点峰值最高2.5Gbps。峰值规格与用户实际下载速度分别记录。</p></article><article><span class="twilight-index">02 / NATIVE IP</span><h3>原生IP线路</h3><p>提供原生IP线路，服务介绍覆盖流媒体、AI工具与短视频平台等使用场景。IP具体属性按对应节点与套餐说明核对。</p></article><article><span class="twilight-index">03 / DEVICES</span><h3>多设备同时在线</h3><p>不限制同时使用客户端数量，支持不同设备在线使用。具体系统和客户端下载方式将随对应平台资料补充。</p></article><article><span class="twilight-index">04 / SUPPORT</span><h3>客服处理使用问题</h3><p>资料说明提供高效客服响应，协助处理使用问题。当前未提供具体联系渠道或响应时间，因此按服务方向介绍。</p></article></div></section>
<section class="section" id="twilight-regions"><div class="twilight-section-title"><span class="overline">REGIONS IN THE SUPPLIED MATERIALS</span><h2>七个地区列明数量，其他地区按名称记录。</h2><p>本次服务资料列出15个地区。以下7个地区提供具体节点数量。</p></div><div class="twilight-region-grid">{region_cards}</div><div class="twilight-other-regions"><h3>资料另外列明的地区</h3><div>{region_chips}</div></div><p class="twilight-note">其余8个地区未提供数量，不补造节点数。以上为资料中的地区分布，具体可用节点以后台当时显示为准。</p></section>
<section class="section" id="twilight-platforms"><div class="twilight-section-title"><span class="overline">STREAMING, AI & SHORT VIDEO</span><h2>围绕观看、问答与短视频的连接需求。</h2><p>以下平台来自站长提供的服务说明。</p></div><div class="twilight-platform-grid">{platforms}</div><p class="twilight-note">平台支持说明与实际使用记录分别整理；有具体记录时，注明日期、节点地区和完成的操作。</p></section>
<section class="section" id="twilight-faq"><div class="twilight-section-title"><span class="overline">TWILIGHT QUESTIONS & ANSWERS</span><h2>暮光网络常见问题</h2></div><div class="twilight-faqs">{questions}</div></section>
<section class="section" id="twilight-reading"><div class="twilight-section-title"><span class="overline">READ BEFORE COMPARING</span><h2>选择之前，把这些条件看清。</h2></div><div class="twilight-reading-grid"><a href="article-brand-record-template.html"><span>资料来源</span><strong>每个数字，找到对应出处。</strong><small>阅读品牌资料整理方法 →</small></a><a href="article-plan-comparison-sheet.html"><span>套餐比较</span><strong>把金额、额度与周期分开。</strong><small>阅读套餐对比指南 →</small></a><a href="article-fair-comparison.html"><span>连接记录</span><strong>比较表现，先确认相同条件。</strong><small>阅读同条件比较方法 →</small></a></div></section>
<section class="section" id="twilight-sources"><div class="twilight-section-title"><span class="overline">SOURCES & REVISIONS</span><h2>资料来源与更新说明</h2><p>本页依据{e(data['source'])}整理，日期为{data['updated_on']}。内容涵盖IPLC线路、单节点峰值规格、原生IP、多设备并发、客服服务方向与节点地区。</p></div><p class="twilight-note">套餐价格、优惠码、客户端流程、售后细则、Logo与实际测试记录，将按后续提供的暮光网络资料补充。入口保留站长提供的原推广参数。</p><div class="twilight-source-links"><a href="data/muguang-profile.json">查看暮光网络资料 JSON ↓</a><a href="{url}" target="_blank" rel="sponsored noopener noreferrer">暮光网络访问入口 ↗</a><a href="brands.html">返回品牌目录 →</a></div></section>'''
    css_revision=sha256((root/'assets/twilight.css').read_bytes()).hexdigest()[:12]
    description='暮光网络机场介绍：依据站长提供资料整理全IPLC专线、原生IP、多设备同时使用与单节点峰值最高2.5Gbps的服务规格。列明香港、台湾、日本、新加坡、美国、韩国、阿根廷等节点地区与数量，并说明Netflix、Disney+、ChatGPT和TikTok支持方向。'
    page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>暮光网络机场介绍｜IPLC专线、原生IP与节点地区｜叮当观察</title><meta name="description" content="'+e(description,quote=True)+'"><link rel="stylesheet" href="assets/site-base.css"><link rel="stylesheet" href="assets/doraemon-theme.css"><link rel="stylesheet" href="assets/topics.css"><link rel="stylesheet" href="assets/twilight.css?v='+css_revision+'"></head><body><div class="shell">'+header('brands')+'<main>'+body+'</main>'+footer()+'</div></body></html>'
    write_changed(root/'brand-muguang.html',page)
    for name in ('index.html','brands.html'):
        path=root/name
        original=path.read_text(encoding='utf-8')
        changed=re.sub(r'<a\b[^>]*href="brand-muguang\.html"[^>]*>.*?</a>',lambda match: re.sub(r'<p>.*?</p>','<p>IPLC专线 · 原生IP与节点地区</p>',match[0],count=1,flags=re.S),original,flags=re.S)
        write_changed(path,changed)
    catalog_path=root/'data/brands.json'
    catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
    brand=next(item for item in catalog['brands'] if item['id']=='muguang')
    brand.update(profile_status='station_supplied_service_introduction',verification_status='station_provided_not_independently_verified',source_type=data['source'],source_date=data['updated_on'],line_type_from_materials=data['line_type'],listed_region_count=len(data['regions']),advertised_single_node_peak_gbps=data['advertised_single_node_peak_gbps'])
    write_changed(catalog_path,json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    text='# 暮光网络\n\n整理日期：'+data['updated_on']+'。来源：'+data['source']+'。\n\n## 品牌介绍\n\n'+data['intro']+'\n\n'
    text+='## 服务规格\n\n- 线路：IPLC专线。\n- 资料列明的单节点峰值：最高2.5Gbps，不等于实测下载速度。\n- IP：原生IP线路。\n- 设备：不限制同时使用客户端数量，多设备在线。\n- 客服：资料说明高效响应，处理使用问题；未提供具体渠道或响应时限。\n\n'
    text+='## 节点地区\n\n| 地区 | 资料提供的节点数量 |\n| --- | --- |\n'
    text+=''.join('| '+item['name']+' | '+(str(item['reported_node_count']) if item['reported_node_count'] is not None else '未提供数量')+' |\n' for item in data['regions'])
    text+='\n## 平台支持方向\n\n'+ '、'.join(item['name'] for item in data['platforms'])+'。以上来自服务介绍，实际使用记录另行整理。\n\n## 常见问题\n\n'
    text+=''.join('### '+question+'\n\n'+answer+'\n\n' for question,answer in twilight_faqs(data))
    text+='## 访问入口\n\n[暮光网络访问入口]('+data['entry_url']+')。保留站长提供的推广参数。\n'
    folder=root/'content/brands'
    folder.mkdir(parents=True,exist_ok=True)
    write_changed(folder/'muguang.md',text)


if __name__=='__main__':
    build_twilight_profile(Path(__file__).resolve().parents[1])
