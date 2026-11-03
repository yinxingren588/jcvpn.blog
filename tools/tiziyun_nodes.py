"""Render LadderCloud's owner-supplied afternoon snapshot and data exports."""
from collections import Counter
from datetime import date
from html import escape as e
from io import StringIO
from math import ceil
from pathlib import Path
from statistics import median
import csv

from site_chrome import write_changed


def time_label(data):
    value=data.get('measured_time') or data.get('period') or '时刻未提供'
    if not data.get('measured_time') and data.get('period'):
        value+='（具体时刻未提供）'
    return data['measured_date']+' '+value


def validate_snapshot(data):
    assert data['brand_id']=='tiziyun' and data['collection_status']=='core_context_confirmed'
    assert data['coverage_completeness_confirmed'] is True
    date.fromisoformat(data['measured_date'])
    assert all(data.get(key) for key in ('location','isp','client','period'))
    records=data['records'];s=data['summary']
    assert len(records)==len({r['id'] for r in records})==s['node_count']
    values=[r['latency_ms'] for r in records if r['latency_ms'] is not None]
    assert len(values)==s['response_count'] and len(records)-len(values)==s['timeout_count']
    assert (min(values),median(values),max(values))==(s['min_ms'],s['median_ms'],s['max_ms'])
    assert all(r['status']==('timeout' if r['latency_ms'] is None else 'numeric') for r in records)
    assert sum(len(r['source_screenshots']) for r in records)==data['source_card_count']
    assert Counter(r['group_id'] for r in records)=={g['id']:g['node_count'] for g in data['regions']}
    assert max(values)<=data['chart_axis_max_ms']
    for group in data['regions']:
        rows=[r for r in records if r['group_id']==group['id']]
        numbers=[r['latency_ms'] for r in rows if r['latency_ms'] is not None]
        assert len(numbers)==group['response_count'] and len(rows)-len(numbers)==group['timeout_count']
        assert (min(numbers),median(numbers),max(numbers))==(group['min_ms'],group['median_ms'],group['max_ms'])


def overview_svg(data):
    validate_snapshot(data)
    s=data['summary'];axis=data['chart_axis_max_ms'];per_column=ceil(len(data['records'])/2)
    last_y=330+(per_column-1)*31;axis_y=last_y+44;footer_y=axis_y+58;height=footer_y+100
    colors={g['id']:g['color'] for g in data['regions']}
    description=f"{time_label(data)}，{data['location']}{data['isp']}，{data['client']}。{s['node_count']}个节点，{s['response_count']}条数值，{s['timeout_count']}条超时。"
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-labelledby="chart-title chart-description">',
           '<title id="chart-title">梯子云 LadderCloud 下午节点延迟记录</title>',
           '<desc id="chart-description">'+e(description)+'</desc>',
           f'<rect width="1600" height="{height}" fill="#f1f7fc"/>',
           '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;fill:#284f6b}.small{font-size:18px;fill:#607f95}.label{font-size:20px}.value{font-size:20px;font-weight:600}</style>',
           f'<rect x="35" y="30" width="1530" height="{height-60}" rx="24" fill="white" stroke="#d2e4f1"/>',
           '<text x="75" y="91" font-size="36" font-weight="700">梯子云 LadderCloud · 下午节点延迟</text>',
           '<text x="75" y="133" class="small">'+e(time_label(data)+' · '+data['location']+data['isp']+' · '+data['client'])+'</text>',
           '<text x="75" y="163" class="small">来源：站长提供的完整节点列表截图及环境确认 · 本站未独立复测</text>']
    metrics=[('本批节点',str(s['node_count'])),('有延迟数值',str(s['response_count'])),('本次超时',str(s['timeout_count'])),('数值中位数',f"{s['median_ms']:g} ms")]
    for i,(label,value) in enumerate(metrics):
        x=75+i*368
        parts.extend([f'<rect x="{x}" y="186" width="345" height="90" rx="13" fill="#edf6fc"/>',
                      f'<text x="{x+19}" y="216" class="small">{e(label)}</text>',
                      f'<text x="{x+19}" y="256" font-size="32" font-weight="700">{e(value)}</text>'])
    for column in range(2):
        start=75+column*755;bar_x=start+144;bar_width=450
        for tick in (0,axis/2,axis):
            x=bar_x+tick/axis*bar_width
            parts.extend([f'<line x1="{x}" x2="{x}" y1="304" y2="{last_y+13}" stroke="#dfebf4"/>',
                          f'<text x="{x}" y="{axis_y}" text-anchor="middle" class="small">{tick:g} ms</text>'])
        for index,record in enumerate(data['records'][column*per_column:(column+1)*per_column]):
            y=330+index*31
            parts.append(f'<text x="{start}" y="{y}" class="label">{e(record["label"])}</text>')
            if record['latency_ms'] is None:
                parts.append(f'<text x="{bar_x+8}" y="{y}" font-size="19" style="fill:#ad6349">Timeout · 本次超时</text>')
            else:
                width=record['latency_ms']/axis*bar_width
                parts.extend([f'<rect x="{bar_x}" y="{y-17}" width="{width:.3f}" height="19" rx="4" fill="{colors[record["group_id"]]}"/>',
                              f'<text x="{bar_x+bar_width+70}" y="{y}" text-anchor="end" class="value">{record["latency_ms"]} ms</text>'])
    parts.extend([f'<text x="75" y="{footer_y}" class="small">完整性经站长确认；香港01按截图原名保留。新加坡09、香港13超时，不按0ms计入数值统计。</text>',
                  f'<text x="75" y="{footer_y+32}" class="small">下午的一次截图记录；具体时刻、客户端版本与探测方法未提供，持续稳定性需另行观察。</text>','</svg>'])
    return ''.join(parts)


def build_snapshot_assets(root,data):
    root=Path(root);validate_snapshot(data)
    stream=StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['节点原名','地区','延迟（ms）','状态','来源截图编号','截图行','截图列','资料接收日期','测试日期','测试时间','测试所在地','运营商','客户端'])
    for r in data['records']:
        writer.writerow([r['original_name'],r['region'],r['latency_ms'] if r['latency_ms'] is not None else '',
                         'Timeout' if r['latency_ms'] is None else '数值','/'.join(map(str,r['source_screenshots'])),
                         r['source_position']['row'],r['source_position']['column'],data['received_on'],data['measured_date'],
                         data.get('measured_time') or data['period']+'（具体时刻未提供）',data['location'],data['isp'],data['client']])
    write_changed(root/'data/tiziyun-latency.csv','\ufeff'+stream.getvalue())
    write_changed(root/'assets/tiziyun-latency-overview.svg',overview_svg(data))


def render_snapshot(data):
    validate_snapshot(data)
    s=data['summary'];axis=data['chart_axis_max_ms']
    colors={g['id']:g['color'] for g in data['regions']}
    regions=''.join('<div class="lat-region"><div class="lat-region-name"><b>'+e(g['region'])+'</b><small>'+str(g['response_count'])+'条数值 / '+str(g['timeout_count'])+'条超时</small></div><div class="lat-region-track"><span style="width:'+format(g['median_ms']/axis*100,'.3f')+'%;background:'+g['color']+'"></span></div><div class="lat-region-value"><strong>'+format(g['median_ms'],'g')+'</strong><span>ms</span><small>'+str(g['min_ms'])+'—'+str(g['max_ms'])+' ms</small></div></div>' for g in data['regions'])
    cards=[]
    for r in data['records']:
        value=r['latency_ms'];timeout=value is None
        display='<strong>Timeout</strong><span>本次超时</span>' if timeout else '<strong>'+str(value)+'</strong><span>ms</span>'
        line='' if timeout else '<div class="lat-node-line"><span style="width:'+format(value/axis*100,'.3f')+'%;background:'+colors[r['group_id']]+'"></span></div>'
        cards.append('<article class="lat-node'+(' is-timeout' if timeout else '')+'" data-node-id="'+r['id']+'" data-region="'+r['group_id']+'" data-order="'+str(r['display_order'])+'" data-source-order="'+str(r['source_order'])+'" data-latency="'+('' if timeout else str(value))+'" data-status="'+r['status']+'"><div><span class="lat-node-dot" style="background:'+colors[r['group_id']]+'"></span><b>'+e(r['label'])+'</b></div><p>'+display+'</p>'+line+'</article>')
    filters='<button type="button" data-tiziyun-region="all" aria-pressed="true">全部地区</button>'+''.join('<button type="button" data-tiziyun-region="'+g['id']+'" aria-pressed="false">'+e(g['region'])+'</button>' for g in data['regions'])
    return f'''<section class="section latency-panel tiziyun-latency" id="tiziyun-latency" aria-labelledby="tiziyun-latency-title">
<div class="latency-top"><div><span class="overline">LADDERCLOUD / AFTERNOON NODE SNAPSHOT</span><h2 id="tiziyun-latency-title">下午采样，{s['node_count']}个节点的延迟记录。</h2><p>{e(time_label(data))} · {e(data['location']+data['isp'])} · {e(data['client'])}</p></div></div>
<div class="lat-kpis"><div><small>本批节点</small><strong>{s['node_count']}<span>个</span></strong></div><div><small>有延迟数值</small><strong>{s['response_count']}<span>条</span></strong></div><div class="lat-kpi-alert"><small>本次超时</small><strong>{s['timeout_count']}<span>条</span></strong></div><div><small>数值中位数</small><strong>{s['median_ms']:g}<span>ms</span></strong></div></div>
<div class="lat-overview"><div class="lat-chart-title"><h3>各地区延迟数值中位数</h3><span>横轴0—{axis}ms · 右侧列最小—最大值</span></div>{regions}<div class="lat-axis"><span>0</span><span>{axis/2:g}ms</span><span>{axis}ms</span></div></div>
<div class="lat-method-note"><b>来源与统计范围</b><p>站长提供5张截图，并确认是完整节点列表。按原名整理{s['node_count']}个节点，其中{s['response_count']}条数值范围{s['min_ms']}—{s['max_ms']}ms，中位数{s['median_ms']:g}ms。新加坡09、香港13超时，保留为Timeout。</p><p>截图中的香港01按原名及147ms保留。编号不连续，不补写其他编号。测试日期、下午时段、上海电信与Windows版梯子云客户端均由站长逐项确认；具体时刻、版本与探测方法未提供。本批为一次下午截图记录，晚高峰与持续稳定性需要相应时段资料。</p></div>
<details class="lat-details" open><summary>查看{s['node_count']}个节点的数值与超时</summary><div class="lat-controls"><div class="lat-filters" role="group" aria-label="按地区筛选梯子云节点">{filters}</div><div class="tiziyun-lat-selects"><label class="lat-sort">状态<select id="tiziyun-lat-status"><option value="all">全部记录</option><option value="numeric">有数值</option><option value="timeout">本次超时</option></select></label><label class="lat-sort">排序<select id="tiziyun-lat-sort"><option value="region">地区与节点编号</option><option value="source">截图原始顺序</option><option value="ascending">延迟从低到高</option><option value="descending">延迟从高到低</option></select></label></div></div><div class="lat-node-grid">{''.join(cards)}</div><p class="tiziyun-lat-empty" hidden>当前筛选条件下没有记录。</p><div class="lat-pagination"><button type="button" id="tiziyun-lat-prev">← 上一页</button><p id="tiziyun-lat-count" role="status" aria-live="polite">共{s['node_count']}条记录</p><button type="button" id="tiziyun-lat-next">下一页 →</button></div></details>
<div class="lat-metadata"><div><span>采样日期与时段</span><b>{e(time_label(data))}</b></div><div><span>所在地 / 运营商</span><b>{e(data['location'])} / {e(data['isp'])}</b></div><div><span>客户端</span><b>{e(data['client'])}，具体版本未提供</b></div><div><span>资料类型</span><b>站长提供截图及补充说明，本站未独立复测</b></div></div><div class="lat-downloads"><a href="assets/tiziyun-latency-overview.svg" download>下载50节点高清概览图 SVG ↓</a><a href="data/tiziyun-latency.csv" download>下载完整节点表 CSV ↓</a><a href="data/tiziyun-latency.json">查看记录与统计说明 JSON ↓</a></div></section>'''
