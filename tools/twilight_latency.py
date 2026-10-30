"""Render supplied Twilight client latency observations, separate from application feedback."""
from html import escape as e


def latency_faqs(data):
    s=data['summary']
    return [
        ('暮光网络有节点延迟记录吗？',f"有。本页整理{data['measured_date']} {data['measured_time']}（北京时间）、上海电信、{data['client']}的6张截图，共{s['node_count']}条延迟数值，范围{s['min_ms']}—{s['max_ms']}ms，中位数{s['median_ms']:g}ms。这是上午记录。"),
        ('这批暮光节点截图出现超时了吗？','没有。这批60条记录均显示数值，0条超时。这里只描述本次截图，不据此推断长期零超时、完整节点在线率或其他网络的表现。'),
        ('这些延迟能代表下载速度或实时表现吗？','不能。ms是客户端显示的延迟，不能换算成Mbps或下载速率。图表按这批截图整理，不会自动重新检测；每节点只有一次记录。'),
        ('香港018、香港020为什么显示为香港18、香港20？','为方便阅读，页面标签统一使用两位节点编号。截图原名分别保存在完整JSON和CSV数据中，不合并不同节点，也不修改延迟数值。')
    ]


def render_latency(data):
    s=data['summary']
    axis=data['chart_axis_max_ms']
    groups={g['id']:g for g in data['regions']}
    region_rows=[]
    for g in data['regions']:
        region_rows.append(f'<div class="lat-region"><div class="lat-region-name"><b>{e(g["region"])}</b><small>{g["response_count"]}条数值 / {g["timeout_count"]}条超时</small></div><div class="lat-region-track"><span style="width:{g["median_ms"]/axis*100:.3f}%;background:{g["color"]}"></span></div><div class="lat-region-value"><strong>{g["median_ms"]:g}</strong><span>ms</span><small>{g["min_ms"]}—{g["max_ms"]} ms</small></div></div>')
    nodes=[]
    for r in data['records']:
        ms=r['latency_ms']
        color=groups[r['group_id']]['color']
        nodes.append(f'<article class="lat-node" data-region="{r["group_id"]}" data-order="{r["source_order"]}" data-latency="{ms}" data-status="numeric" title="截图原名：{e(r["original_name"],quote=True)}"><div><span class="lat-node-dot" style="background:{color}"></span><b>{e(r["label"])}</b><span class="lat-node-state">延迟记录</span></div><p><strong>{ms}</strong><span>ms</span></p><div class="lat-node-line"><span style="width:{ms/axis*100:.3f}%;background:{color}"></span></div></article>')
    filters='<button type="button" data-lat-region="all" aria-pressed="true">全部地区</button>'+''.join('<button type="button" data-lat-region="'+g['id']+'" aria-pressed="false">'+e(g['region'])+'</button>' for g in data['regions'])
    time=data['measured_date']+' '+data['measured_time']+'（北京时间）'
    return f'''<section class="section latency-panel twilight-latency" id="twilight-latency" aria-labelledby="twilight-latency-title"><div class="latency-top"><div><span class="overline">TWILIGHT / MORNING NODE LATENCY</span><h2 id="twilight-latency-title">上午10点，60条节点延迟记录。</h2><p>{time} · 上海电信 · {e(data['client'])}</p></div></div>
<div class="lat-kpis"><div><small>截图记录</small><strong>{s['node_count']}<span>条</span></strong></div><div><small>有延迟数值</small><strong>{s['response_count']}<span>条</span></strong></div><div><small>本次超时</small><strong>{s['timeout_count']}<span>条</span></strong></div><div><small>最低延迟</small><strong>{s['min_ms']}<span>ms</span></strong></div></div>
<div class="lat-overview"><div class="lat-chart-title"><h3>各地区延迟中位数</h3><span>横轴0—{axis}ms · 右侧列出最小—最大值</span></div>{''.join(region_rows)}<div class="lat-axis"><span>0</span><span>{axis//2}ms</span><span>{axis}ms</span></div></div>
<div class="lat-method-note"><b>这批记录怎样统计？</b><p>{s['node_count']}条均有数值，范围{s['min_ms']}—{s['max_ms']}ms，总体中位数{s['median_ms']:g}ms。香港20条，台湾、日本、新加坡、美国各10条。</p><p>每节点仅一条截图记录，0条超时只描述本次展示结果。本图不推算下载速度、长期可用率或实时状态，与前一晚的ChatGPT问答反馈分别记录。</p></div>
<details class="lat-details" open><summary>查看60条节点明细</summary><div class="lat-controls"><div class="lat-filters" role="group" aria-label="按地区筛选暮光延迟记录">{filters}</div><div class="twilight-lat-selects"><label class="lat-sort">状态<select id="twilight-lat-status" aria-label="暮光延迟记录状态"><option value="all">全部记录</option><option value="numeric">有数值</option><option value="timeout">本次超时（0）</option></select></label><label class="lat-sort">排序<select id="twilight-lat-sort" aria-label="暮光节点排序"><option value="source">截图原始顺序</option><option value="ascending">延迟从低到高</option><option value="descending">延迟从高到低</option></select></label></div></div><div class="lat-node-grid">{''.join(nodes)}</div><p class="twilight-lat-empty" hidden>本组在这批记录中没有符合当前筛选条件的节点。</p><div class="lat-pagination"><button type="button" id="twilight-lat-prev">← 上一页</button><p id="twilight-lat-count" role="status" aria-live="polite">共60条记录</p><button type="button" id="twilight-lat-next">下一页 →</button></div></details>
<div class="lat-metadata"><div><span>资料来源</span><b>{e(data['source'])}</b></div><div><span>采样时间</span><b>{time} · 上午</b></div><div><span>所在地 / 运营商</span><b>上海 / 电信</b></div><div><span>测试客户端</span><b>{e(data['client'])}</b></div></div>
<details class="lat-static"><summary>查看可下载的概览图</summary><img src="assets/muguang-latency-overview.svg" alt="暮光网络2026年10月30日10时上海电信节点延迟：60条数值，0条超时，范围{s['min_ms']}至{s['max_ms']}ms" width="1600" height="1120" loading="lazy"></details><p class="twilight-note">原截图只作整理依据，不作为博客图片发布。完整数据保留原名；图表按这批数值重绘，未重新测量。</p><div class="lat-downloads"><a href="assets/muguang-latency-overview.png" download>下载概览图 PNG ↓</a><a href="assets/muguang-latency-overview.svg" download>下载概览图 SVG ↓</a><a href="data/muguang-latency.csv" download>下载60条完整数据 CSV ↓</a><a href="data/muguang-latency.json" download>数据与统计说明 JSON ↓</a></div></section>'''


def latency_markdown(data):
    s=data['summary']
    text='## 上午节点延迟记录\n\n'+data['measured_date']+' '+data['measured_time']+'（北京时间），上海电信，'+data['client']+'。来源：'+data['source']+'。\n\n'
    text+=f"共{s['node_count']}条数值，{s['timeout_count']}条超时；范围{s['min_ms']}—{s['max_ms']}ms，总体中位数{s['median_ms']:g}ms。\n\n"
    text+='| 地区 | 记录数 | 中位数 | 最小—最大值 |\n| --- | --- | --- | --- |\n'
    for g in data['regions']:
        text+=f"| {g['region']} | {g['count']} | {g['median_ms']:g}ms | {g['min_ms']}—{g['max_ms']}ms |\n"
    return text+'\n单次记录不推算下载速度、长期可用率或实时状态；原截图不发布，完整数据保留原名。与2026-10-29 23:00的ChatGPT问答反馈分别记录。\n\n'
