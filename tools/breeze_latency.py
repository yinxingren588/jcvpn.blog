"""Breezenet snapshot chart using the existing node-latency visual system."""
from html import escape as e
import json
from pathlib import Path

COLORS = {'香港': '#2484c5', '台湾': '#31a1a8', '新加坡': '#e2a149',
          '日本': '#bba180', '美国': '#597895', '日本·直连': '#746bc3'}
MAX_MS = 120


def build_module(root):
    data = json.loads((root / 'data/breezenet-latency.json').read_text(encoding='utf-8'))
    summary = data['summary']
    rows = []
    for region in data['regions']:
        name = region['region']
        median = region['median_ms']
        if median is None:
            track = '<div class="lat-region-track is-unmeasured" aria-label="本组无延迟数值"></div>'
            value = '<strong>—</strong><small>全部超时</small>'
        else:
            track = f'<div class="lat-region-track"><span style="width:{median / MAX_MS * 100:.3f}%;background:{COLORS[name]}"></span></div>'
            value = f'<strong>{median:g}</strong><span>ms</span><small>{region["min_ms"]}—{region["max_ms"]} ms</small>'
        rows.append(f'<div class="lat-region"><div class="lat-region-name"><b>{e(name)}</b><small>{region["response_count"]}条数值 / {region["timeout_count"]}条超时</small></div>{track}<div class="lat-region-value">{value}</div></div>')
    nodes = []
    for record in data['records']:
        ms = record['latency_ms']
        color = COLORS[record['group']]
        value = '<strong>超时</strong>' if ms is None else f'<strong>{ms}</strong><span>ms</span>'
        width = 0 if ms is None else ms / MAX_MS * 100
        nodes.append(f'<article class="lat-node {"is-timeout" if ms is None else ""}" data-region="{e(record["group"], quote=True)}" data-id="{record["id"]}" data-latency="{ms if ms is not None else ""}"><div><span class="lat-node-dot" style="background:{color}"></span><b>{e(record["label"])}</b><span class="lat-node-state">{"本次超时" if ms is None else "延迟记录"}</span></div><p>{value}</p><div class="lat-node-line"><span style="width:{width:.3f}%;background:{color}"></span></div></article>')
    buttons = '<button type="button" data-lat-region="all" aria-pressed="true">全部分组</button>'
    buttons += ''.join('<button type="button" data-lat-region="' + e(region['region'], quote=True) + '" aria-pressed="false">' + e(region['region']) + '</button>' for region in data['regions'])
    return f'''<section class="section latency-panel breeze-latency" id="peak-latency" aria-labelledby="latency-title"><div class="latency-top"><div><span class="overline">MIDDAY NODE LATENCY</span><h2 id="latency-title">午间节点延迟，一目了然。</h2><p>2026-10-29 12:00（北京时间） · 上海电信 · 第三方延迟记录</p></div></div><div class="lat-kpis"><div><small>记录节点</small><strong>{summary['node_count']}<span>个</span></strong></div><div><small>有延迟数值</small><strong>{summary['response_count']}<span>条</span></strong></div><div class="lat-kpi-alert"><small>本次超时</small><strong>{summary['timeout_count']}<span>条</span></strong></div><div><small>最低延迟</small><strong>{summary['min_ms']}<span>ms</span></strong></div></div><div class="lat-overview"><div class="lat-chart-title"><h3>各分组延迟中位数</h3><span>横轴 0—120 ms · 只统计有数值记录</span></div>{''.join(rows)}<div class="lat-axis"><span>0</span><span>60 ms</span><span>120 ms</span></div></div><div class="lat-method-note"><b>怎样读这批记录？</b><p>39条数值参与延迟统计，13条超时单独保留，不记成0ms。日本01—10本次均超时，名称带“直连”的日本01—04另组展示；香港13未出现在资料中，不补节点或数值。</p><p>每个节点仅一条记录，本图是第三方延迟快照，不代表下载速度、长期可用率或实时监测。</p></div><details class="lat-details" open><summary>查看52个节点明细</summary><div class="lat-controls"><div class="lat-filters" role="group" aria-label="按节点分组筛选延迟记录">{buttons}</div><label class="lat-sort">排序<select id="latency-sort" aria-label="节点排序"><option value="node">节点编号</option><option value="ascending">延迟从低到高</option><option value="descending">延迟从高到低</option></select></label></div><div class="lat-node-grid">{''.join(nodes)}</div><div class="lat-pagination"><button type="button" id="lat-prev">← 上一页</button><p id="lat-count" aria-live="polite">共52条记录</p><button type="button" id="lat-next">下一页 →</button></div></details><div class="lat-metadata" id="latency-metadata"><div><span>资料来源</span><b>第三方提供的5张截图，经站长转交</b></div><div><span>采样时间</span><b>2026-10-29 12:00（北京时间）</b></div><div><span>地点 / 运营商</span><b>上海 / 电信</b></div><div><span>测试客户端</span><b>{e(data['client'])}</b></div></div><details class="lat-static"><summary>查看可分享概览图</summary><img src="assets/breezenet-latency.svg" alt="微风网络2026年10月29日12时上海电信节点延迟记录：52个节点，39条数值，13条超时，日本直连节点单列" width="1400" height="1060" loading="lazy"></details><div class="lat-downloads"><a href="assets/breezenet-latency.png" download>下载概览图 PNG ↓</a><a href="assets/breezenet-latency.svg" download>下载概览图 SVG ↓</a><a href="data/breezenet-latency.csv" download>下载完整数据 CSV ↓</a><a href="data/breezenet-latency.json" download>数据与统计说明 JSON ↓</a></div></section>'''


def markdown(root):
    data = json.loads((root / 'data/breezenet-latency.json').read_text(encoding='utf-8'))
    text = '\n## 午间节点延迟记录\n\n来源：第三方提供的5张截图，经站长转交。用户补充采样时间为2026-10-29 12:00（北京时间），上海电信，Windows版“微风网络”客户端。\n\n共52个节点、39条数值、13条超时；数值范围11—111ms，全部数值中位数28ms。超时不作为0ms参与统计，日本直连另列。香港13未在资料中展示，未补值。\n\n| 分组 | 数值 / 总数 | 超时 | 中位数 | 范围 |\n| --- | --- | --- | --- | --- |\n'
    for region in data['regions']:
        median = '无数值' if region['median_ms'] is None else f'{region["median_ms"]:g}ms'
        spread = '全部超时' if region['min_ms'] is None else f'{region["min_ms"]}—{region["max_ms"]}ms'
        text += f'| {region["region"]} | {region["response_count"]} / {region["count"]} | {region["timeout_count"]} | {median} | {spread} |\n'
    text += '\n单次延迟记录不推导下载速度、丢包率、长期可用率或实时监测结果。图表按数据重绘，未重新测量，未发布原照片。\n'
    return text
