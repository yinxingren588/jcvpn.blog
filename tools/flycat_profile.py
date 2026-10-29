"""Build only the Flycat profile from attributed, brand-specific materials."""
from hashlib import sha256
from html import escape as e
import json
from pathlib import Path
import re

from site_chrome import header, footer, write_changed
from flycat_plans import render_plans, render_floating, plan_faqs, plans_csv, plans_markdown


def faqs(data, plans):
    counted = '、'.join(item['name'] + str(item['reported_node_count']) + '个' for item in data['regions'] if item['reported_node_count'] is not None)
    others = '、'.join(item['name'] for item in data['regions'] if item['reported_node_count'] is None)
    return [
        ('飞猫云采用什么线路？', '根据站长提供的品牌介绍，飞猫云采用IPLC专线，提供原生IP线路选择。本页按该资料介绍线路方向。'),
        ('飞猫云有哪些节点地区？', '本次资料列明：' + counted + '；另外包括' + others + '等地区。后九个地区未提供节点数量，具体可用节点以后台当时显示为准。'),
        ('飞猫云限制连接设备数量吗？', '站长提供的品牌介绍说明不限制设备连接数量，支持多端同时登录使用。具体客户端、套餐额度和其他使用规则，将按飞猫云的对应资料整理。'),
        ('飞猫云支持哪些流媒体和AI平台？', '品牌介绍列明Netflix、Disney+、ChatGPT与TikTok等平台支持方向。这属于服务说明；实际访问记录需要注明具体日期、节点和验证操作后另行整理。'),
        ('这份飞猫云介绍是否包含实际测速？', '当前提供的是品牌介绍和节点分布，尚未提供该品牌的延迟、下载速度或平台访问测试记录。节点数量和平台支持说明不直接作为测速结果。')
    ] + plan_faqs(plans)


def build_flycat_profile(root):
    root = Path(root)
    data = json.loads((root / 'data/feimaoyun-profile.json').read_text(encoding='utf-8'))
    plans = json.loads((root / 'data/feimaoyun-plans.json').read_text(encoding='utf-8'))
    url = e(data['entry_url'], quote=True)
    features = ''.join('<article><h3>' + e(item['title']) + '</h3><p>' + e(item['description']) + '</p></article>' for item in data['features'])
    counted = ''.join('<article class="flycat-region"><h3>' + e(item['name']) + '</h3><strong>' + str(item['reported_node_count']) + '<small>个</small></strong></article>' for item in data['regions'] if item['reported_node_count'] is not None)
    other_regions = ''.join('<span>' + e(item['name']) + '</span>' for item in data['regions'] if item['reported_node_count'] is None)
    platforms = ''.join('<article><h3>' + e(item['name']) + '</h3><p>' + e(item['category']) + '</p></article>' for item in data['declared_platforms'])
    faq_html = ''.join('<details class="flycat-faq"><summary>' + e(question) + '</summary><p>' + e(answer) + '</p></details>' for question, answer in faqs(data, plans))
    packages = render_plans(plans, url)
    body = f'''<section class="flycat-hero" id="flycat-about"><span class="overline">FLYCAT / BRAND PROFILE</span><h1>飞猫云</h1><p class="flycat-tagline">原生IP与多地区节点，面向多端使用。</p><p class="flycat-intro">{e(data['intro'])}</p><div class="flycat-highlights"><span>IPLC专线</span><span>原生IP线路</span><span>不限设备连接</span><span>{len(data['regions'])}个资料列明地区</span></div><div class="flycat-actions"><a class="btn" href="{url}" target="_blank" rel="sponsored noopener noreferrer">访问飞猫云入口 <span aria-hidden="true">↗</span></a><a class="textlink" href="#flycat-regions">查看节点地区 →</a></div><p class="flycat-date">品牌资料由站长提供 · 整理日期：{data['updated_on']}</p></section>
<nav class="flycat-jumps" aria-label="飞猫云页面目录"><a href="#flycat-about">品牌介绍</a><a href="#flycat-plans">7款套餐</a><a href="#flycat-compare">价格对比</a><a href="#flycat-choose">如何选择</a><a href="#flycat-features">线路与设备</a><a href="#flycat-regions">节点地区</a><a href="#flycat-platforms">平台支持</a><a href="#flycat-faq">常见问题</a><a href="#flycat-sources">资料来源</a></nav>
{packages}
<section class="section" id="flycat-features"><div class="flycat-section-title"><span class="overline">CONNECTION & DEVICES</span><h2>从线路到多端连接，了解服务方向。</h2><p>围绕IPLC、原生IP与设备使用方式整理品牌介绍。</p></div><div class="flycat-feature-grid">{features}</div></section>
<section class="section" id="flycat-regions"><div class="flycat-section-title"><span class="overline">REGIONAL NODE DISTRIBUTION</span><h2>节点地区与数量，按提供资料列明。</h2><p>以下六个地区提供了具体节点数量。</p></div><div class="flycat-region-grid">{counted}</div><div class="flycat-region-more"><h3>另有以下地区</h3><div class="flycat-region-chips">{other_regions}</div></div><p class="flycat-note">其余地区未提供节点数量，按地区名称展示。这里记录的是品牌资料中的分布说明，具体可用节点以后台当时显示为准。</p></section>
<section class="section" id="flycat-platforms"><div class="flycat-section-title"><span class="overline">STREAMING, AI & SHORT VIDEO</span><h2>流媒体、AI与短视频平台支持方向。</h2><p>以下平台来自站长提供的服务说明。</p></div><div class="flycat-platform-grid">{platforms}</div><p class="flycat-note">平台支持说明与实际访问记录分别整理；后续验证会注明日期、节点地区与完成的具体操作。</p></section>
<section class="section" id="flycat-faq"><div class="flycat-section-title"><span class="overline">FLYCAT QUESTIONS & ANSWERS</span><h2>飞猫云常见问题</h2></div><div class="flycat-faqs">{faq_html}</div></section>
<section class="section" id="flycat-sources"><div class="flycat-section-title"><span class="overline">SOURCES & REVISIONS</span><h2>资料来源与更新说明</h2><p>{e(data['source'])}；另有站长提供的3张套餐截图及价格确认，整理日期为{data['updated_on']}。本页据此整理线路、设备、节点分布、套餐与平台支持方向。</p></div><p class="flycat-note">客户端详情、优惠码、售后规则及实际测试记录，将按飞猫云自身资料补充。学生版最终年价与其余四款周期套餐仅列月价的方式，已由站长确认。访问入口保留站长提供的推广参数。</p><div class="flycat-source-links"><a href="data/feimaoyun-profile.json">品牌资料 JSON ↓</a><a href="data/feimaoyun-plans.json">套餐资料 JSON ↓</a><a href="data/feimaoyun-plans.csv" download>套餐价格表 CSV ↓</a><a href="{url}" target="_blank" rel="sponsored noopener noreferrer">飞猫云访问入口 ↗</a><a href="brands.html">返回品牌目录 →</a></div></section>'''
    revision = sha256((root / 'assets/flycat.css').read_bytes()).hexdigest()[:12]
    description = '飞猫云机场套餐与品牌介绍：学生版84元/年、每月50GB，另有150GB至1000GB月度套餐、680元不限时流量包及定制方案。整理IPLC专线、原生IP、节点地区、流量刷新、价格对比与常见问题，帮助按用量选择。'
    floating_revision = sha256((root / 'assets/flycat-floating.js').read_bytes()).hexdigest()[:12]
    floating_css_revision = sha256((root / 'assets/invisible-floating.css').read_bytes()).hexdigest()[:12]
    page = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>飞猫云机场套餐价格｜IPLC专线、原生IP与节点介绍｜叮当观察</title><meta name="description" content="' + e(description, quote=True) + '"><link rel="stylesheet" href="assets/site-base.css"><link rel="stylesheet" href="assets/doraemon-theme.css"><link rel="stylesheet" href="assets/topics.css"><link rel="stylesheet" href="assets/invisible-floating.css?v=' + floating_css_revision + '"><link rel="stylesheet" href="assets/flycat.css?v=' + revision + '"></head><body class="has-floating-promo has-flycat-floating">' + render_floating(url) + '<div class="shell">' + header('brands') + '<main>' + body + '</main>' + footer() + '</div><script src="assets/flycat-floating.js?v=' + floating_revision + '" defer></script></body></html>'
    page = page.replace('查看节点地区 →', '查看7款套餐 →', 1).replace('href="#flycat-regions">查看7款套餐', 'href="#flycat-plans">查看7款套餐', 1)
    write_changed(root / 'brand-feimaoyun.html', page)
    for name in ('index.html', 'brands.html'):
        path = root / name
        original = path.read_text(encoding='utf-8')
        updated = re.sub(r'<a\b[^>]*href="brand-feimaoyun\.html"[^>]*>.*?</a>', lambda match: re.sub(r'<p>.*?</p>', '<p>IPLC线路 · 7款套餐与原生IP介绍</p>', match[0], count=1, flags=re.S), original, flags=re.S)
        write_changed(path, updated)
    catalog_path = root / 'data/brands.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    brand = next(item for item in catalog['brands'] if item['id'] == 'feimaoyun')
    brand.update(profile_status='station_supplied_introduction_and_7_plans', verification_status='station_provided_not_independently_verified', source_type=data['source'] + '；' + plans['source'], source_date=data['updated_on'], line_type_from_materials=data['line_type'], listed_region_count=len(data['regions']), plan_count=len(plans['plans']), page_checked_on=data['entry_observation']['checked_on'], page_observation=data['entry_observation']['observation'])
    write_changed(catalog_path, json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    text = '# 飞猫云\n\n整理日期：' + data['updated_on'] + '。来源：' + data['source'] + '。\n\n## 品牌介绍\n\n' + data['intro'] + '\n\n'
    text += '## 线路与设备\n\n' + ''.join('### ' + item['title'] + '\n\n' + item['description'] + '\n\n' for item in data['features'])
    text += '## 节点地区\n\n| 地区 | 资料提供的节点数量 |\n| --- | --- |\n'
    text += ''.join('| ' + item['name'] + ' | ' + (str(item['reported_node_count']) if item['reported_node_count'] is not None else '未提供数量') + ' |\n' for item in data['regions'])
    text += '\n' + plans_markdown(plans)
    text += '\n## 平台支持方向\n\n' + '、'.join(item['name'] for item in data['declared_platforms']) + '。来源为品牌服务说明，实际访问记录另行整理。\n\n## 常见问题\n\n'
    text += ''.join('### ' + question + '\n\n' + answer + '\n\n' for question, answer in faqs(data, plans))
    text += '## 访问入口\n\n[飞猫云访问入口](' + data['entry_url'] + ')。保留站长提供的原推广参数。\n'
    folder = root / 'content/brands'
    folder.mkdir(parents=True, exist_ok=True)
    write_changed(folder / 'feimaoyun.md', text)
    write_changed(root / 'data/feimaoyun-plans.csv', plans_csv(plans))


if __name__ == '__main__':
    build_flycat_profile(Path(__file__).resolve().parents[1])
