"""Render all supplied Flycat latency observations with truthful grouping."""
from html import escape as e

MAX_MS = 400


def latency_faqs(data):
    summary = data['summary']
    return [
        ('飞猫云有晚高峰节点延迟记录吗？', f"有。站长提供2026-10-29 20:00的6张客户端截图，采样环境为上海电信、Windows版飞猫云客户端。共{summary['node_count']}条记录，{summary['response_count']}条有数值、{summary['timeout_count']}条超时，数值范围{summary['min_ms']}—{summary['max_ms']}ms。"),
        ('延迟图里的超时怎样统计？', '6条超时单独保留，不记成0ms，也不参与中位数、最低值和最高值计算。截图中的较高延迟数值同样完整保留。'),
        ('为什么有两组直连节点的代码和中文地区不一致？', '截图原文分别为“直连-JP-美国BGP”和“直连-US-日本BGP”。本页按原名分别分组，保留各自4条记录，不根据代码或中文名称擅自确定实际地区。'),
        ('为什么香港节点明细里没有09？', '这批截图展示香港01—08及10—20，共19条，没有展示香港09。本页不补节点或数值；未展示不等于已确认超时或下线。'),
        ('节点名称有IEPL字样，品牌线路为什么仍写IPLC？', '原始节点名称按截图保留，品牌线路介绍继续采用站长明确确认的IPLC。节点命名与品牌线路说明分别记录，不仅凭节点名称判断实际线路架构。')
    ]


def render_latency(data):
    summary = data['summary']
    groups = {group['id']: group for group in data['regions']}
    regions = []
    for group in data['regions']:
        midpoint = group['median_ms']
        if midpoint is None:
            track = '<div class="lat-region-track is-unmeasured" aria-label="本组没有延迟数值"></div>'
            value = '<strong>—</strong><small>本次仅超时记录</small>'
        else:
            track = f'<div class="lat-region-track"><span style="width:{midpoint / MAX_MS * 100:.3f}%;background:{group["color"]}"></span></div>'
            value = f'<strong>{midpoint:g}</strong><span>ms</span><small>{group["min_ms"]}—{group["max_ms"]} ms</small>'
        regions.append(f'<div class="lat-region"><div class="lat-region-name"><b>{e(group["region"])}</b><small>{group["response_count"]}条数值 / {group["timeout_count"]}条超时</small></div>{track}<div class="lat-region-value">{value}</div></div>')
    nodes = []
    for record in data['records']:
        ms = record['latency_ms']
        color = groups[record['group_id']]['color']
        value = '<strong>超时</strong>' if ms is None else f'<strong>{ms}</strong><span>ms</span>'
        width = 0 if ms is None else ms / MAX_MS * 100
        nodes.append(f'''<article class="lat-node{' is-timeout' if ms is None else ''}" data-region="{record['group_id']}" data-order="{record['source_order']}" data-latency="{ms if ms is not None else ''}" data-status="{record['status']}" title="截图原名：{e(record['original_name'], quote=True)}"><div><span class="lat-node-dot" style="background:{color}"></span><b>{e(record['label'])}</b><span class="lat-node-state">{'本次超时' if ms is None else '延迟记录'}</span></div><p>{value}</p><div class="lat-node-line"><span style="width:{width:.3f}%;background:{color}"></span></div></article>''')
    buttons = '<button type="button" data-lat-region="all" aria-pressed="true">全部分组</button>'
    buttons += ''.join('<button type="button" data-lat-region="' + group['id'] + '" aria-pressed="false">' + e(group['region']) + '</button>' for group in data['regions'])
    return f'''<section class="section latency-panel flycat-latency" id="flycat-latency" aria-labelledby="flycat-latency-title"><div class="latency-top"><div><span class="overline">FLYCAT / PEAK-HOUR NODE LATENCY</span><h2 id="flycat-latency-title">晚高峰节点延迟，逐条记录。</h2><p>2026-10-29 20:00（北京时间） · 上海电信 · Windows版飞猫云客户端</p></div></div><div class="lat-kpis"><div><small>截图记录</small><strong>{summary['node_count']}<span>条</span></strong></div><div><small>有延迟数值</small><strong>{summary['response_count']}<span>条</span></strong></div><div class="lat-kpi-alert"><small>本次超时</small><strong>{summary['timeout_count']}<span>条</span></strong></div><div><small>最低延迟</small><strong>{summary['min_ms']}<span>ms</span></strong></div></div><div class="lat-overview"><div class="lat-chart-title"><h3>各分组延迟中位数</h3><span>横轴0—400ms · 右侧列出最小—最大值</span></div>{''.join(regions)}<div class="lat-axis"><span>0</span><span>200ms</span><span>400ms</span></div></div><div class="lat-method-note"><b>这批记录怎样统计？</b><p>63条数值范围29—345ms，总体中位数80ms；6条超时单独保留，不作0ms。香港09未在截图中出现，不补值。截图展示的高延迟数值均保留。</p><p>“直连-JP-美国”与“直连-US-日本”按原名分组，代码与中文地区不一致，暂不判断实际地区。每节点仅一条记录，本图展示本次客户端延迟，不推算下载速度或长期可用率。</p></div><details class="lat-details" open><summary>查看69条节点明细</summary><div class="lat-controls"><div class="lat-filters" role="group" aria-label="按节点分组筛选延迟记录">{buttons}</div><div class="flycat-lat-selects"><label class="lat-sort">状态<select id="flycat-lat-status" aria-label="延迟记录状态"><option value="all">全部记录</option><option value="numeric">有数值</option><option value="timeout">本次超时</option></select></label><label class="lat-sort">排序<select id="flycat-lat-sort" aria-label="飞猫云节点排序"><option value="source">截图原始顺序</option><option value="ascending">延迟从低到高</option><option value="descending">延迟从高到低</option></select></label></div></div><div class="lat-node-grid">{''.join(nodes)}</div><p class="flycat-lat-empty" hidden>本组在这批记录中没有符合当前筛选条件的节点。</p><div class="lat-pagination"><button type="button" id="flycat-lat-prev">← 上一页</button><p id="flycat-lat-count" role="status" aria-live="polite">共69条记录</p><button type="button" id="flycat-lat-next">下一页 →</button></div></details><div class="lat-metadata"><div><span>资料来源</span><b>{e(data['source'])}</b></div><div><span>采样时间</span><b>2026-10-29 20:00（北京时间 · 晚高峰）</b></div><div><span>所在地 / 运营商</span><b>上海 / 电信</b></div><div><span>测试客户端</span><b>Windows版飞猫云客户端</b></div></div><details class="lat-static"><summary>查看可下载的概览图</summary><img src="assets/feimaoyun-latency-overview.svg" alt="飞猫云2026年10月29日20时上海电信延迟记录：69条记录，63条数值，6条超时，延迟范围29至345ms" width="1600" height="1500" loading="lazy"></details><details class="flycat-lat-label-notes"><summary>截图原始命名与分组说明</summary><p>完整数据保留原始节点名称，包括IEPL字样与Vless显示标签。站长确认品牌线路介绍仍保留IPLC；不从节点命名推定实际线路架构。菲律宾的FLB前缀、越南“养号/低价区”及两组矛盾直连命名均按截图保存。</p><p>原截图仅作为整理依据，不作为博客图片发布。本站依据数据重绘图表，未重新测量。</p></details><div class="lat-downloads"><a href="assets/feimaoyun-latency-overview.png" download>下载概览图 PNG ↓</a><a href="assets/feimaoyun-latency-overview.svg" download>下载概览图 SVG ↓</a><a href="data/feimaoyun-latency.csv" download>下载69条完整数据 CSV ↓</a><a href="data/feimaoyun-latency.json" download>数据与统计说明 JSON ↓</a></div></section>'''


def latency_markdown(data):
    s=data['summary']
    text='## 晚高峰节点延迟记录\n\n2026-10-29 20:00（北京时间），上海电信，Windows版飞猫云客户端。来源：'+data['source']+'。\n\n'
    text+=f"共{s['node_count']}条，{s['response_count']}条数值、{s['timeout_count']}条超时；数值范围{s['min_ms']}—{s['max_ms']}ms，总体中位数{s['median_ms']}ms。超时不作0ms。\n\n"
    text+='| 分组 | 数值 / 总数 | 超时 | 中位数 | 范围 |\n| --- | --- | --- | --- | --- |\n'
    for group in data['regions']:
        middle='无数值' if group['median_ms'] is None else f"{group['median_ms']:g}ms"
        spread='仅超时' if group['min_ms'] is None else f"{group['min_ms']}—{group['max_ms']}ms"
        text+=f"| {group['region']} | {group['response_count']} / {group['count']} | {group['timeout_count']} | {middle} | {spread} |\n"
    text+='\n香港09未在这批截图中出现，不补值。两个直连分组按截图命名，不推定实际地区；原始名称中的IEPL保留，品牌线路按站长确认仍为IPLC。单次延迟不推断下载速度、长期可用率或实时监测。原截图不发布。\n\n'
    return text
