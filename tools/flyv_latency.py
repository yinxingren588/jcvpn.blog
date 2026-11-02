"""Render the supplied November 2 FlyV latency snapshot without publishing its photos."""
from collections import Counter
from html import escape as e
from io import StringIO
from pathlib import Path
from statistics import median
import csv
import json

from site_chrome import write_changed


def validate_latency(data):
    records=data['records'];s=data['summary']
    assert len({r['id'] for r in records})==len(records)
    numbers=[r['latency_ms'] for r in records if r['latency_ms'] is not None]
    assert len(records)==s['node_count'] and len(numbers)==s['response_count']
    assert len(records)-len(numbers)==s['timeout_count']
    assert (min(numbers),median(numbers),max(numbers))==(s['min_ms'],s['median_ms'],s['max_ms'])
    assert all(r['status']==('timeout' if r['latency_ms'] is None else 'numeric') for r in records)
    assert max(numbers)<=data['chart_axis_max_ms']
    assert sum(len(r['source_screenshots']) for r in records)==data['source_card_count']
    assert data['source_card_count']-len(records)==data['duplicate_card_count']
    assert Counter(r['group_id'] for r in records)=={g['id']:g['node_count'] for g in data['regions']}
    for group in data['regions']:
        rows=[r for r in records if r['group_id']==group['id']]
        values=[r['latency_ms'] for r in rows if r['latency_ms'] is not None]
        assert len(values)==group['response_count'] and len(rows)-len(values)==group['timeout_count']
        assert (min(values),median(values),max(values))==(group['min_ms'],group['median_ms'],group['max_ms'])


def latency_faqs(data):
    s=data['summary']
    return [
        ('飞v这批晚高峰节点延迟是在什么环境记录的？',data['measured_date']+' '+data['measured_time']+'（北京时间），上海电信，时间由站长按小时提供。本批资料来自6张刚提供的客户端截图；客户端名称、系统平台、版本与探测方式尚未提供。'),
        ('飞v这次有多少条记录，哪些节点超时？',f"去重后共{s['node_count']}个节点，{s['response_count']}条有数值，{s['timeout_count']}条超时。新加坡05、美国04显示Timeout，保留为超时，不作为0ms参与数值统计。"),
        ('台湾04、台湾05为什么只统计一次？','两张相邻截图重复展示了台湾04与台湾05，数值分别同为49ms和51ms。原图共有62张节点卡片，合并这两组重复展示后，实际是60个不同节点。'),
        ('这张图能说明下载速度或长期稳定性吗？',f"这里记录的是客户端显示的节点延迟，单位ms；58条数值范围{s['min_ms']}—{s['max_ms']}ms，中位数{s['median_ms']:g}ms。每节点仅一次记录，不能换算成下载带宽，也不是实时监控或长期可用率。")
    ]


def overview_svg(data):
    s=data['summary'];axis=data['chart_axis_max_ms']
    colors={g['id']:g['color'] for g in data['regions']}
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1390" viewBox="0 0 1600 1390" role="img" aria-labelledby="chart-title chart-description">',
           '<title id="chart-title">飞v 2026年11月2日19点 上海电信节点延迟</title>',
           '<desc id="chart-description">60个节点，58条数值，2条超时；超时不计为0ms。58条数值范围32至148ms，中位数70.5ms。</desc>',
           '<rect width="1600" height="1390" fill="#f1f7fc"/>',
           '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;fill:#284f6b}.small{font-size:18px;fill:#607f95}.label{font-size:20px}.value{font-size:20px;font-weight:600}</style>',
           '<rect x="35" y="30" width="1530" height="1330" rx="24" fill="white" stroke="#d2e4f1"/>',
           '<text x="75" y="91" font-size="36" font-weight="700">飞v FlyV · 晚高峰节点延迟</text>',
           '<text x="75" y="133" class="small">2026-11-02 19:00（北京时间） · 上海电信 · 6张截图整理，原图不发布</text>']
    metrics=[('节点总数',str(s['node_count'])),('有延迟数值',str(s['response_count'])),('本次超时',str(s['timeout_count'])),('数值中位数',f"{s['median_ms']:g} ms")]
    for i,(label,value) in enumerate(metrics):
        x=75+i*368
        parts.extend([f'<rect x="{x}" y="164" width="345" height="92" rx="13" fill="#edf6fc"/>',
                      f'<text x="{x+19}" y="195" class="small">{e(label)}</text>',
                      f'<text x="{x+19}" y="235" font-size="32" font-weight="700">{e(value)}</text>'])
    records=data['records']
    for column in range(2):
        start=75+column*755;bar_x=start+144;bar_width=450
        for tick in (0,80,160):
            x=bar_x+tick/axis*bar_width
            parts.extend([f'<line x1="{x}" x2="{x}" y1="300" y2="1210" stroke="#dfebf4"/>',
                          f'<text x="{x}" y="1240" text-anchor="middle" class="small">{tick} ms</text>'])
        for i,r in enumerate(records[column*30:(column+1)*30]):
            y=320+i*30
            parts.append(f'<text x="{start}" y="{y}" class="label">{e(r["label"])}</text>')
            if r['latency_ms'] is None:
                parts.append(f'<text x="{bar_x+8}" y="{y}" font-size="19" style="fill:#bb6252">Timeout · 本次超时</text>')
            else:
                width=r['latency_ms']/axis*bar_width
                parts.extend([f'<rect x="{bar_x}" y="{y-17}" width="{width:.3f}" height="19" rx="4" fill="{colors[r["group_id"]]}"/>',
                              f'<text x="{bar_x+bar_width+70}" y="{y}" text-anchor="end" class="value">{r["latency_ms"]} ms</text>'])
    parts.extend(['<text x="75" y="1286" class="small">重复展示的台湾04、台湾05各计一次；新加坡05、美国04保留超时。客户端名称、版本和探测方法未提供。</text>',
                  '<text x="75" y="1322" class="small">单次截图延迟，不代表下载速度或长期稳定性。数据来源：博客站长；图表由叮当观察按数值重绘。</text>','</svg>'])
    return ''.join(parts)


def build_latency_assets(root,data):
    root=Path(root);validate_latency(data)
    stream=StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['节点原名','地区','延迟（ms）','状态','来源截图编号','日期','时间（北京时间）','所在地','运营商'])
    for r in data['records']:
        writer.writerow([r['original_name'],r['region'],r['latency_ms'] if r['latency_ms'] is not None else '',
                         'Timeout' if r['latency_ms'] is None else '数值','/'.join(map(str,r['source_screenshots'])),
                         data['measured_date'],data['measured_time'],data['location'],data['isp']])
    write_changed(root/'data/feiv-latency.csv','\ufeff'+stream.getvalue())
    write_changed(root/'assets/feiv-latency-overview.svg',overview_svg(data))


def render_latency(data):
    validate_latency(data)
    s=data['summary'];axis=data['chart_axis_max_ms']
    colors={g['id']:g['color'] for g in data['regions']}
    region_rows=''.join('<div class="lat-region"><div class="lat-region-name"><b>'+e(g['region'])+'</b><small>'+str(g['response_count'])+'条数值 / '+str(g['timeout_count'])+'条超时</small></div><div class="lat-region-track"><span style="width:'+format(g['median_ms']/axis*100,'.3f')+'%;background:'+g['color']+'"></span></div><div class="lat-region-value"><strong>'+format(g['median_ms'],'g')+'</strong><span>ms</span><small>'+str(g['min_ms'])+'—'+str(g['max_ms'])+' ms</small></div></div>' for g in data['regions'])
    cards=[]
    for r in data['records']:
        ms=r['latency_ms'];timeout=ms is None
        value='<strong>Timeout</strong><span>本次超时</span>' if timeout else '<strong>'+str(ms)+'</strong><span>ms</span>'
        line='' if timeout else '<div class="lat-node-line"><span style="width:'+format(ms/axis*100,'.3f')+'%;background:'+colors[r['group_id']]+'"></span></div>'
        cards.append('<article class="lat-node'+(' is-timeout' if timeout else '')+'" data-node-id="'+r['id']+'" data-region="'+r['group_id']+'" data-order="'+str(r['display_order'])+'" data-source-order="'+str(r['source_order'])+'" data-latency="'+('' if timeout else str(ms))+'" data-status="'+r['status']+'"><div><span class="lat-node-dot" style="background:'+colors[r['group_id']]+'"></span><b>'+e(r['label'])+'</b></div><p>'+value+'</p>'+line+'</article>')
    filters='<button type="button" data-flyv-region="all" aria-pressed="true">全部地区</button>'+''.join('<button type="button" data-flyv-region="'+g['id']+'" aria-pressed="false">'+e(g['region'])+'</button>' for g in data['regions'])
    return f'''<section class="section latency-panel flyv-latency" id="flyv-latency" aria-labelledby="flyv-latency-title"><div class="latency-top"><div><span class="overline">FLYV / EVENING NODE LATENCY</span><h2 id="flyv-latency-title">晚高峰7点，60个节点延迟记录。</h2><p>{data['measured_date']} {data['measured_time']}（北京时间） · 晚高峰 · 上海电信</p></div></div>
<div class="lat-kpis"><div><small>去重后节点</small><strong>{s['node_count']}<span>个</span></strong></div><div><small>有延迟数值</small><strong>{s['response_count']}<span>条</span></strong></div><div class="lat-kpi-alert"><small>本次超时</small><strong>{s['timeout_count']}<span>条</span></strong></div><div><small>数值中位数</small><strong>{s['median_ms']:g}<span>ms</span></strong></div></div>
<div class="lat-overview"><div class="lat-chart-title"><h3>各地区延迟中位数</h3><span>横轴0—{axis}ms · 右侧列出最小—最大值</span></div>{region_rows}<div class="lat-axis"><span>0</span><span>80ms</span><span>{axis}ms</span></div></div>
<div class="lat-method-note"><b>本次记录怎样统计</b><p>6张截图共有62张节点卡片；台湾04、台湾05重复展示且数值一致，各统计一次。去重后60个节点，58条数值范围32—148ms，中位数70.5ms。新加坡05、美国04超时，单独保留，不作为0ms。</p><p>采样时间、所在地和运营商由站长确认。客户端名称、平台、版本与探测方法尚未提供；每节点仅一次截图记录，ms不换算成下载速度或长期可用率。</p></div>
<details class="lat-details" open><summary>查看60个节点的数值与超时记录</summary><div class="lat-controls"><div class="lat-filters" role="group" aria-label="按地区筛选飞v节点延迟">{filters}</div><div class="flyv-lat-selects"><label class="lat-sort">状态<select id="flyv-lat-status"><option value="all">全部记录</option><option value="numeric">有数值</option><option value="timeout">本次超时</option></select></label><label class="lat-sort">排序<select id="flyv-lat-sort"><option value="region">地区与节点编号</option><option value="source">截图原始顺序</option><option value="ascending">延迟从低到高</option><option value="descending">延迟从高到低</option></select></label></div></div><div class="lat-node-grid">{''.join(cards)}</div><p class="flyv-lat-empty" hidden>当前筛选条件下没有记录。</p><div class="lat-pagination"><button type="button" id="flyv-lat-prev">← 上一页</button><p id="flyv-lat-count" role="status" aria-live="polite">共60条记录</p><button type="button" id="flyv-lat-next">下一页 →</button></div></details>
<div class="lat-metadata"><div><span>采样时间</span><b>2026-11-02 19:00（北京时间 · 晚高峰，按小时提供）</b></div><div><span>测试所在地 / 运营商</span><b>上海 / 电信</b></div><div><span>测试客户端与方法</span><b>名称、平台、版本与探测方法未提供</b></div><div><span>资料来源</span><b>站长提供的6张新截图及环境说明；原截图不发布</b></div></div><div class="lat-downloads"><a href="assets/feiv-latency-overview.svg" download>下载60节点高清概览图 SVG ↓</a><a href="data/feiv-latency.csv" download>下载完整数据 CSV ↓</a><a href="data/feiv-latency.json">数据与统计说明 JSON ↓</a></div></section>'''
