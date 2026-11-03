"""Render only the prices and terms visible in the owner's LadderCloud plan images."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e
from io import StringIO
from pathlib import Path
import csv

from site_chrome import write_changed
from tiziyun_coupon import discounted_price


def money(value):
    return format(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'.2f')


def validate_plans(data):
    plans=data['plans']
    assert data['brand_id']=='tiziyun' and data['catalog_complete_confirmed'] is True
    assert len(plans)==len({p['id'] for p in plans})==9
    assert sum(p['kind']=='annual' for p in plans)==1
    assert sum(p['kind']=='monthly' for p in plans)==4
    assert sum(p['kind']=='one_time' for p in plans)==3
    assert sum(p['kind']=='custom' for p in plans)==1
    assert all(p['price_cny']>0 and p['traffic_display'] and p['available_cycles'] for p in plans)
    assert all(p['device_limit_display']=='不限' for p in plans)


def plan_faqs(data,coupon=None):
    validate_plans(data)
    return [
        ('梯子云9款套餐的报价分别是多少？','本次提供的原始报价为：天梯随行89元/年；初阶25元/月、中阶60元/月、高阶110元/月、顶阶商业190元/月；三款一次性包169元、449元与849元；私人定制680元/月。'+('适用2hy85的5款套餐另列八五折价格，年付保活和三款买断不适用。' if coupon else '优惠信息尚未提供，这里展示截图报价。')),
        ('89元年付的60GB是每月还是全年总量？','截图写明每个月60GB自动刷新，89元是年付金额。全年支付89元，折合约7.42元/月；这一数字只是年度预算换算，不能按7.42元单独购买一个月。具体刷新日期与未用额度处理尚未提供。'),
        ('月付套餐还有哪些周期，其他周期多少钱？','初阶、中阶、高阶和顶阶商业均显示月付、季付、半年付、年付。本次只提供25、60、110和190元的月价，其他周期总额待提供，不按月价乘月份推算。'),
        ('350GB中阶与350GB标准买断包有什么区别？','中阶原价60元/月，每月350GB；标准买断包为449元一次性，整包350GB总流量，不限时、用完即止。'+('中阶使用2hy85后为51元/月，标准买断不适用该码。' if coupon else '')+'流量数字相同，付款周期与额度范围不同。'),
        ('高阶套餐为何单独列出IEPL？','品牌介绍提供的是BGP智能多线入口与专线中继说明，高阶套餐详情另写核心骨干网IEPL专线与专线级网络出口。本页按各套餐的可见说明分别记录，其他套餐未明确相同传输类别时不代填。'),
        ('顶阶商业的1.6TB换算成多少GB？','本页保留截图中的1.6TB原单位。资料未确认TB到GB的换算口径，因此不另填1600GB或其他换算结果。'),
        ('私人定制包含什么资源，多久交付？','资料报价680元/月，每月500GB专属流量，列明独享带宽与独享公网IP、1对1技术维护，预计约2—3个工作日交付。特殊定制或多节点集群可通过工单咨询。原生或住宅IP属性未提供，不据独享公网IP推定。'),
        ('三款买断包会每月自动增加流量吗？','三款分别是120GB、350GB、700GB整包总流量，一次性购买；资料标注不限时、流量用完即止。它们按累计消耗使用，不按月自动补充。')
    ]


def build_plan_csv(root,data,coupon=None):
    validate_plans(data)
    stream=StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    headers=['套餐','报价（元）','付款单位','流量原单位','流量范围','付款周期选项','设备限制','线路说明','速度政策原文范围','刷新或使用说明','来源截图编号','资料接收日期']
    if coupon:
        headers+=['优惠码','优惠适用','优惠后报价（元）','优惠力度','续费使用','重置包使用','优惠到期规则','优惠叠加','优惠确认日期']
    writer.writerow(headers)
    for p in data['plans']:
        row=[p['name'],money(p['price_cny']),p['payment_unit'],p['traffic_display'],p['quota_scope'],
                         '/'.join(p['available_cycles']),p['device_limit_display'],p['line_in_materials'] or '未提供',
                         p['speed_policy_in_materials'] or '未提供',p['reset_rule'],'/'.join(map(str,p['source_screenshots'])),data['provided_on']]
        if coupon:
            c=coupon['coupon'];price=discounted_price(p,coupon);eligible=price is not None
            reset=('可使用' if p['id'] in c['traffic_reset_applies_to_plan_ids'] else '重置包服务未确认') if eligible else '不适用该码'
            row+=[c['code'],'适用' if eligible else '不适用',money(price) if eligible else '',
                  c['display_discount'] if eligible else '', '可使用' if eligible else '不适用该码',
                  reset,c['expiry_policy'],'不能叠加其他优惠',coupon['updated_on']]
        writer.writerow(row)
    write_changed(Path(root)/'data/tiziyun-plans.csv','\ufeff'+stream.getvalue())


def render_plans(data,entry_url,coupon=None):
    validate_plans(data)
    kinds={'annual':'轻量年付','monthly':'月付报价','one_time':'不限时总流量','custom':'独享专线'}
    cards=[];rows=[];entry=e(entry_url,quote=True)
    for p in data['plans']:
        if p['kind']=='annual':
            billing='全年支付 ¥'+money(p['price_cny'])+'，折合约 ¥'+money(Decimal(str(p['price_cny']))/12)+'/月；按年购买'
        elif p['kind']=='monthly':
            billing='月付、季付、半年付、年付可选；本页只列已提供月价'
        elif p['kind']=='one_time':
            billing='一次购买整包总流量；不限时，流量用完即止'
        else:
            billing='独享带宽与独享公网IP；预计约2—3个工作日交付'
        features=''.join('<li>'+e(text)+'</li>' for text in p['features'])
        line='<p class="tiziyun-plan-line"><b>线路说明</b>'+e(p['line_in_materials'])+'</p>' if p['line_in_materials'] else ''
        cycles=''.join('<span>'+e(cycle)+'</span>' for cycle in p['available_cycles'])
        discount_html='';discount_cell=''
        if coupon:
            price=discounted_price(p,coupon)
            if price is not None:
                price_text='¥'+money(price)+'/'+p['payment_unit']
                discount_html='<p class="tiziyun-plan-discount">2hy85八五折后 <strong>'+e(price_text)+'</strong></p>'
                discount_cell='<td class="tiziyun-table-discount">'+e(price_text)+'</td>'
            else:
                discount_html='<p class="tiziyun-plan-excluded">不适用2hy85，按原报价展示。</p>'
                discount_cell='<td>不适用2hy85</td>'
        cards.append('<article class="tiziyun-plan" id="tiziyun-plan-'+p['id']+'" data-plan-kind="'+p['kind']+'"><span class="tiziyun-plan-kind">'+kinds[p['kind']]+'</span><h3>'+e(p['name'])+'</h3><p class="tiziyun-plan-price"><strong>¥'+money(p['price_cny'])+'</strong><span>/'+e(p['payment_unit'])+'</span></p><p class="tiziyun-plan-billing">'+e(billing)+'</p><div class="tiziyun-plan-cycles" aria-label="截图列出的付款选项">'+cycles+'</div><dl class="tiziyun-plan-metrics"><div><dt>'+e(p['quota_scope'])+'</dt><dd>'+e(p['traffic_display'])+'</dd></div><div><dt>设备限制</dt><dd>'+e(p['device_limit_display'])+'</dd></div></dl>'+line+'<ul>'+features+'</ul><p class="tiziyun-plan-reset">'+e(p['reset_rule'])+'</p><a class="tiziyun-plan-action" href="'+entry+'" target="_blank" rel="sponsored noopener noreferrer">'+('咨询私人定制' if p['kind']=='custom' else '查看官网套餐')+' <span aria-hidden="true">↗</span></a></article>')
        if discount_html:
            cards[-1]=cards[-1].replace('<p class="tiziyun-plan-billing">',discount_html+'<p class="tiziyun-plan-billing">',1)
        rows.append('<tr><th scope="row"><a href="#tiziyun-plan-'+p['id']+'">'+e(p['name'])+'</a></th><td>¥'+money(p['price_cny'])+'/'+e(p['payment_unit'])+'</td>'+discount_cell+'<td>'+e(p['traffic_display']+' · '+p['quota_scope'])+'</td><td>'+e('、'.join(p['available_cycles']))+'</td><td>'+e(p['reset_rule'])+'</td></tr>')
    result='''<section class="section" id="tiziyun-plans" aria-labelledby="tiziyun-plans-title"><span class="overline">9 PLANS / SUPPLIED QUOTATIONS</span><h2 id="tiziyun-plans-title">9款套餐，先看付款周期与额度范围。</h2><p class="tiziyun-lead">按站长于'''+e(data['provided_on'])+'''提供的3张套餐图整理，站长已确认共9款。下列为截图报价，优惠与结算规则继续补充；其他付款周期未给出的金额不推算。</p><div class="tiziyun-plan-grid">'''+''.join(cards)+'''</div><p class="tiziyun-note">设备限制、线路、速度政策和平台使用方向按各套餐可见说明整理。部分详情被截图截断，仅保留画面内的内容。顶阶商业保留1.6TB原单位，私人定制仅明确独享公网IP。</p></section>
<section class="section" id="tiziyun-plan-comparison"><span class="overline">BILLING & QUOTA COMPARISON</span><h2 id="tiziyun-plan-comparison-title">梯子云套餐价格对照表</h2><div class="tiziyun-table-wrap" role="region" aria-label="梯子云9款套餐报价对照，可横向滚动" tabindex="0"><table><caption>站长提供的截图报价；年付按年支付，买断包按整包总量消耗。</caption><thead><tr><th scope="col">套餐</th><th scope="col">已提供报价</th><th scope="col">流量与范围</th><th scope="col">付款选项</th><th scope="col">刷新或使用说明</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><div class="tiziyun-source-links"><a href="data/tiziyun-plans.csv" download>下载9款套餐对照表 CSV ↓</a><a href="data/tiziyun-plans.json">查看套餐源资料 JSON ↓</a></div></section>'''
    if coupon:
        result=result.replace('下列为截图报价，优惠与结算规则继续补充；','原始报价与适用2hy85的八五折价格分别列出；',1)
        result=result.replace('<th scope="col">流量与范围</th>','<th scope="col">2hy85八五折后</th><th scope="col">流量与范围</th>',1)
        result=result.replace('站长提供的截图报价；年付按年支付，买断包按整包总量消耗。','原始报价与适用优惠分列；年付保活、三款买断不适用2hy85。年付按年支付，买断包按整包总量消耗。',1)
    return result
