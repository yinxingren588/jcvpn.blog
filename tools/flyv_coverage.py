"""Render the owner's confirmed FlyV coverage separately from latency observations."""
from html import escape as e


def validate_coverage(data):
    regions=data['regions']
    assert data['collection_status']=='regions_and_counts_confirmed'
    assert len(regions)==len({r['id'] for r in regions})==data['region_count']
    assert all(isinstance(r['node_count'],int) and r['node_count']>0 for r in regions)
    assert sum(r['node_count'] for r in regions)==data['total_node_count']


def coverage_faqs(data):
    validate_coverage(data)
    counts='、'.join(r['name']+str(r['node_count'])+'个' for r in data['regions'])
    return [('飞v覆盖哪些节点地区，有多少个节点？',
             '根据站长于'+data['confirmed_on']+'对完整覆盖范围及数量的确认，飞v覆盖'+
             str(data['region_count'])+'个地区，共'+str(data['total_node_count'])+'个节点：'+counts+
             '。节点延迟见本页晚高峰记录，数值与超时按当次日期和条件分别保留。')]


def render_coverage(data):
    validate_coverage(data)
    cards=''.join('<li><h3>'+e(r['name'])+'</h3><p><strong>'+str(r['node_count'])+'</strong><span>个节点</span></p></li>' for r in data['regions'])
    return '''<section class="section flyv-coverage-section" id="flyv-coverage" aria-labelledby="flyv-coverage-title">
<span class="overline">FLYV / REGIONS & NODES</span><h2 id="flyv-coverage-title">'''+str(data['region_count'])+'''个地区，'''+str(data['total_node_count'])+'''个节点。</h2>
<p class="flyv-section-lead">香港、台湾、日本、新加坡与美国。完整地区范围与各地区数量，均由站长于'''+e(data['confirmed_on'])+'''逐项确认。</p>
<ul class="flyv-coverage-grid">'''+cards+'''</ul><p class="flyv-material-note">以上为该日期确认的节点覆盖资料。下方晚高峰记录另列节点数值与超时，并保留采样条件。<a href="data/feiv-coverage.json">查看节点覆盖源资料 JSON ↓</a></p></section>'''
