"""Render FlyV's confirmed periodic rules, technical refund and payment method."""
from html import escape as e


def service_faqs(data):
    return [
        ('飞v普通周期套餐的流量用完后怎样重置？','年付标准轻量版及四款月付方案支持购买与所购套餐同价的流量重置包，购买后立即恢复该套餐完整额度。'),
        ('提前续费飞v会立即补充流量吗？','不会。普通周期套餐提前续费只延长有效期，流量仍按原定刷新日期更新。需要立即恢复额度时，应区分续费与流量重置。'),
        ('飞v升级套餐的费用、周期和流量怎样处理？',data['upgrade']['payment_and_difference_refund']+data['upgrade']['cycle_start']+data['upgrade']['used_traffic_handling']),
        ('飞v什么情况下支持全额退款，多久内申请？','因技术问题，经客服协助后仍完全无法使用时，可在购买后24小时内申请全额退款。申请时登录飞v官网后台联系客服办理。'),
        ('飞v客服从哪里联系？',data['customer_support']['instructions']),
        ('飞v支持什么付款方式？','已确认支持'+'、'.join(data['payment_methods'])+'付款。'),
        ('普通周期套餐的重置、续费和升级规则适用于一次性包吗？','本节已确认的范围为年付标准轻量版和四款月付方案。三款一次性流量包及独享黄金专线的对应处理规则尚未确认，应向客服核对具体方案。')
    ]


def render_service(data):
    assert data['collection_status']=='core_rules_confirmed'
    steps=''.join('<li>'+e(data['upgrade'][key])+'</li>' for key in ('payment_and_difference_refund','cycle_start','used_traffic_handling'))
    return '<section class="section" id="flyv-service" aria-labelledby="flyv-service-title"><span class="overline">PERIODIC PLANS / RESET, RENEWAL & UPGRADE</span><h2 id="flyv-service-title">重置、续费、升级，分别怎样处理？</h2><p class="flyv-section-lead">以下适用于已确认的普通周期套餐：年付标准轻量版、入门、进阶、高端与商业方案。</p><div class="flyv-service-grid"><article class="flyv-service-card"><span class="overline">01 / RESET</span><h3>重置：立即恢复额度</h3><p>流量用完后，可购买与所购套餐同价的流量重置包，购买后立即恢复该套餐的完整流量额度。</p><span class="flyv-rule-tag">同价购买 · 立即恢复</span></article><article class="flyv-service-card"><span class="overline">02 / RENEWAL</span><h3>续费：延长有效期</h3><p>提前续费只延长套餐有效期，不会立即补充流量，仍按原定流量刷新日期更新。</p><span class="flyv-rule-tag">流量仍按原定日期刷新</span></article><article class="flyv-service-card"><span class="overline">03 / UPGRADE</span><h3>升级：核对费用、周期与用量</h3><ol>'+steps+'</ol></article></div><p class="flyv-material-note">同价重置包的优惠适用、对有效期和原定刷新日的影响，以及升级差价的具体算法、退回渠道和到账时间，尚需向平台确认。本节不把普通周期规则扩展到三款一次性包或独享黄金专线。</p><a class="flyv-client-source" href="data/feiv-service-rules.json">查看飞v周期套餐与售后规则 JSON ↓</a></section>'


def render_refund(data,entry_url):
    hours=data['refund']['deadline_hours_after_purchase']
    return '<section class="section" id="flyv-refund" aria-labelledby="flyv-refund-title"><span class="overline">CUSTOMER SUPPORT / TECHNICAL REFUND</span><h2 id="flyv-refund-title">技术问题退款：购买后'+str(hours)+'小时内申请</h2><article class="flyv-refund-panel"><span class="flyv-refund-deadline">申请时限：购买后'+str(hours)+'小时内</span><h3>经客服协助后仍完全无法使用，可申请全额退款。</h3><p>退款条件为因技术问题，经客服协助后仍完全无法使用。请在上述时限内，登录飞v官网后台联系客服办理。</p><ol><li>登录飞v官网后台。</li><li>联系客服，说明问题并配合排查。</li><li>如经协助后仍完全无法使用，在购买后'+str(hours)+'小时内向客服申请全额退款。</li></ol><p class="flyv-refund-note">退款方式与到账时间尚未提供，办理时向客服确认。</p><a class="flyv-refund-entry" href="'+e(entry_url,quote=True)+'" target="_blank" rel="sponsored noopener noreferrer">前往飞v官网入口 <span aria-hidden="true">↗</span></a></article></section>'
