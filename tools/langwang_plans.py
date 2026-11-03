"""Render WaveNet's supplied plan quotes and the owner's explicit corrections."""
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e
from io import StringIO
from pathlib import Path
import csv

from site_chrome import write_changed


def money(value):
    return format(Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP), '.2f')


def validate_plans(data):
    assert data['brand_id'] == 'langwang' and data['catalog_complete_confirmed'] is True
    assert data['collection_status'] == 'core_plan_quotes_and_terms_confirmed'
    assert not data['pending_confirmations']
    plans = data['plans']
    assert len(plans) == len({p['id'] for p in plans}) == 9
    assert Counter(p['kind'] for p in plans) == {'annual': 1, 'monthly': 4, 'one_time': 3, 'custom': 1}
    assert all(p['price_cny'] > 0 and p['traffic_display'] and p['available_cycles'] for p in plans)
    by_id = {p['id']: p for p in plans}
    assert by_id['annual-standard']['traffic_gb'] == 80
    assert by_id['annual-standard']['line_type'] == 'IPLC'
    assert by_id['custom-line']['price_cny'] == 680
    for p in plans:
        if p['kind'] == 'one_time':
            assert p['quota_scope'] == '整包总流量' and p['refreshes_monthly'] is False
            assert p['expiry_policy'] == '不限时，用完即止'


def plan_faqs(data):
    validate_plans(data)
    return [
        ('浪网9款套餐的价格和流量分别是多少？', '年付标准119元/年，每30天80GB；入门30元/月150GB、进阶70元/月400GB、高端120元/月800GB、商业200元/月2.0TB。三款买断包分别为239元180GB、569元450GB、1099元900GB；定制线路680元/月500GB。'),
        ('浪网年付标准能按月购买吗，流量怎样刷新？', '年付报价119元，全年支付，折合约9.92元/月，仅作预算换算。购买日起算，每30天刷新80GB；9.92元不是单月购买价格。年付标准的IPLC说明已由站长单独确认。'),
        ('浪网三款一次性流量包会每月补充吗？', '不会。180GB、450GB和900GB均已由站长确认为不限时整包总流量，用完即止，按累计消耗使用。原图的统一流量字段标签不作为按月增加额度的依据。'),
        ('浪网每款套餐的设备数量都一样吗？', '已提供的说明为：年付标准与入门不限；180GB小流量包限1台设备；450GB标准包可2台同时在线。进阶、高端、商业、900GB精英包及定制线路的具体数量未提供。'),
        ('浪网整体BGP介绍与年付标准IPLC怎样阅读？', 'BGP智能多线入口与专线中继互联来自品牌介绍；年付标准的全IPLC说明另由站长确认。其余套餐的出口与线路描述按各自材料保留。'),
        ('月付还有季付、半年付或年付报价吗？', '截图只提供四档月价及对应每月额度，其他付款周期选项和总额未提供，不按月价乘月份推算。119元年付标准是另一款已明确的套餐。'),
        ('商业套餐的2.0TB是否被改写为GB？', '页面保留顶部2.0TB原单位；该卡详情另明确写2000GB，下载表同时保留材料明示的GB数字，不以其他套餐的换算规则代填。'),
        ('定制线路包包含什么，多久交付？', '价格已由站长确认为680元/月，每月500GB独享流量。资料列独立公网IP、独占带宽、专人技术维护及约2—3个工作日交付。原生IP、住宅IP及固定设备数未提供。')
    ]


def build_plan_csv(root, data):
    validate_plans(data)
    stream = StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['套餐', '采用报价（元）', '付款单位', '流量原单位', '流量GB（材料明示）', '额度范围', '已提供付款选项', '设备说明', '线路说明', '速度政策原文范围', '流量倍率', '刷新或使用说明', '来源截图编号', '资料接收日期'])
    for p in data['plans']:
        writer.writerow([p['name'], money(p['price_cny']), p['payment_unit'], p['traffic_display'], p['traffic_gb'],
                         p['quota_scope'], '/'.join(p['available_cycles']), p['device_limit_display'] or '未提供',
                         p['line_in_materials'] or '未提供', p['speed_policy_in_materials'] or '未提供',
                         p['traffic_multiplier'] if p['traffic_multiplier'] is not None else '未提供',
                         p['reset_rule'], '/'.join(map(str, p['source_screenshots'])), data['provided_on']])
    write_changed(Path(root)/'data/langwang-plans.csv', '\ufeff'+stream.getvalue())


def render_plans(data, entry_url):
    validate_plans(data)
    kinds = {'annual': '年付标准', 'monthly': '月付报价', 'one_time': '不限时总流量', 'custom': '独享定制'}
    cards, rows = [], []
    for p in data['plans']:
        if p['kind'] == 'annual':
            billing = '全年支付 ¥'+money(p['price_cny'])+'，折合约 ¥'+money(Decimal(str(p['price_cny']))/12)+'/月；按年购买'
        elif p['kind'] == 'monthly':
            billing = '已提供月付报价；其他付款周期选项与总额未提供'
        elif p['kind'] == 'one_time':
            billing = '一次购买整包总流量；不限时、用完即止，不按月补充'
        else:
            billing = '独占带宽与独立公网IP；预计约2—3个工作日交付'
        device = p['device_limit_display'] or '未提供'
        cycles = ''.join('<span>'+e(cycle)+'</span>' for cycle in p['available_cycles'])
        line = '<p class="langwang-plan-line"><b>线路说明</b>'+e(p['line_in_materials'])+'</p>' if p['line_in_materials'] else ''
        speed = '<p class="langwang-plan-policy">速度说明：'+e(p['speed_policy_in_materials'])+'</p>' if p['speed_policy_in_materials'] else ''
        features = ''.join('<li>'+e(text)+'</li>' for text in p['features'])
        cards.append('<article class="langwang-plan" id="langwang-plan-'+p['id']+'" data-plan-kind="'+p['kind']+'">'
                     '<span class="langwang-plan-kind">'+kinds[p['kind']]+'</span><h3>'+e(p['name'])+'</h3>'
                     '<p class="langwang-plan-price"><strong>¥'+money(p['price_cny'])+'</strong><span>/'+e(p['payment_unit'])+'</span></p>'
                     '<p class="langwang-plan-billing">'+e(billing)+'</p><div class="langwang-plan-cycles" aria-label="已提供的付款选项">'+cycles+'</div>'
                     '<dl class="langwang-plan-metrics"><div><dt>'+e(p['quota_scope'])+'</dt><dd>'+e(p['traffic_display'])+'</dd></div>'
                     '<div><dt>设备说明</dt><dd>'+e(device)+'</dd></div></dl>'+line+speed+'<ul>'+features+'</ul>'
                     '<p class="langwang-plan-reset">'+e(p['reset_rule'])+'</p><a class="langwang-plan-action" href="'+e(entry_url, quote=True)
                     +'" target="_blank" rel="sponsored noopener noreferrer">'+('咨询定制线路' if p['kind']=='custom' else '查看官网套餐')
                     +' <span aria-hidden="true">↗</span></a></article>')
        rows.append('<tr><th scope="row"><a href="#langwang-plan-'+p['id']+'">'+e(p['name'])+'</a></th><td>¥'
                    +money(p['price_cny'])+'/'+e(p['payment_unit'])+'</td><td>'+e(p['traffic_display']+' · '+p['quota_scope'])
                    +'</td><td>'+e(device)+'</td><td>'+e('、'.join(p['available_cycles']))+'</td><td>'+e(p['reset_rule'])+'</td></tr>')
    return ('<section class="section" id="langwang-plans" aria-labelledby="langwang-plans-title"><span class="overline">9 PLANS / PRICES & QUOTAS</span>'
            '<h2 id="langwang-plans-title">9款套餐，分清付款周期与流量范围。</h2>'
            '<p class="langwang-lead">按站长于'+e(data['provided_on'])+'提供的两张套餐图及后续确认整理，共9款。'
            '年付标准采用80GB，定制采用680元/月，三款买断按不限时总流量列出。优惠与其他使用规则继续逐项补充。</p>'
            '<div class="langwang-plan-grid">'+''.join(cards)+'</div>'
            '<p class="langwang-note">设备、线路、速度与平台方向按各套餐资料分别列明；未提供的设备数量、付款周期与服务条件需在官网核对。平台方向与2.5Gbps峰值说明均不是本页独立测试结果。</p></section>'
            '<section class="section" id="langwang-plan-comparison"><span class="overline">BILLING & QUOTA COMPARISON</span>'
            '<h2 id="langwang-plan-comparison-title">浪网套餐价格对照表</h2>'
            '<div class="langwang-table-wrap" role="region" aria-label="浪网9款套餐价格对照，可横向滚动" tabindex="0">'
            '<table><caption>采用站长确认的当前报价与额度；年付按年支付，买断包按整包总量消耗。</caption>'
            '<thead><tr><th scope="col">套餐</th><th scope="col">已提供报价</th><th scope="col">流量与范围</th><th scope="col">设备说明</th>'
            '<th scope="col">已提供付款选项</th><th scope="col">刷新或使用说明</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
            '<div class="langwang-source-links"><a href="data/langwang-plans.csv" download>下载9款套餐对照表 CSV ↓</a>'
            '<a href="data/langwang-plans.json">套餐源资料及补充确认 JSON ↓</a></div></section>')
