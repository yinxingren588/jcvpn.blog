"""Render WaveNet's confirmed traffic, payment and conditional refund rules."""
from html import escape as e
from langwang_coupon import coupon_rules


def validate_service(data, plans, coupon):
    assert data['brand_id'] == 'langwang' and data['collection_status'] == 'core_rules_confirmed'
    periodic = {p['id'] for p in plans if p['kind'] in ('annual', 'monthly')}
    assert len(periodic) == 5
    for key in ('periodic_traffic_reset', 'early_renewal', 'upgrade'):
        assert set(data[key]['applies_to_plan_ids']) == periodic
    reset = data['periodic_traffic_reset']
    assert reset['supported'] and reset['effective_immediately'] and reset['restores_full_plan_quota']
    assert reset['discount_applicability']['coupon_code'] == coupon['coupon']['code']
    assert set(reset['discount_applicability']['applies_to_plan_ids']) == periodic
    assert set(coupon['coupon']['traffic_reset_applies_to_plan_ids']) == periodic
    assert data['early_renewal']['extends_validity'] and data['early_renewal']['refreshes_traffic_immediately'] is False
    assert all(data['upgrade'][key] for key in
               ('payment_and_difference_refund', 'cycle_start', 'used_traffic_handling'))
    refund = data['refund']
    assert refund['supported'] and refund['full_refund'] and refund['deadline_hours_after_purchase'] == 24
    assert refund['conditions'] == ['因技术问题', '经客服协助后仍完全无法使用']
    assert refund['application_login_required'] is True
    assert data['one_time_traffic_reset'] is None and data['custom_plan_traffic_reset'] is None


def service_faqs(data, coupon):
    return [
        ('浪网普通周期套餐的流量用完后能立即重置吗？',
         '年付标准及四款月付支持购买同价重置包，购买后立即恢复所购套餐完整流量额度。这五款套餐的重置包可使用lw888享八折。'),
        ('提前续费浪网会立即补充流量吗？',
         '普通周期套餐提前续费只延长有效期，不立即补充流量，仍按原定日期刷新。周期套餐续费可使用lw888享八折。'),
        ('浪网升级时费用、周期与流量如何处理？',
         ''.join(data['upgrade'][key] for key in
                 ('payment_and_difference_refund', 'cycle_start', 'used_traffic_handling'))),
        ('浪网什么情况下支持全额退款，怎样申请？',
         '因技术问题，经客服协助后仍完全无法使用时，可在购买后24小时内申请全额退款。登录浪网官网后台联系客服办理；退款方式与到账时间尚未提供。'),
        ('浪网支持什么付款方式？', '已确认支持' + '、'.join(data['payment_methods']) + '付款。'),
        ('普通周期流量规则是否也适用于买断包和定制线路包？',
         '本节重置、提前续费与升级的确认范围为年付标准及四款月付。三款一次性包与定制线路包的对应规则未提供；优惠码可用范围另行列明。')
    ]


def render_service(data, coupon):
    upgrade = ''.join('<li>' + e(data['upgrade'][key]) + '</li>' for key in
                      ('payment_and_difference_refund', 'cycle_start', 'used_traffic_handling'))
    return ('<section class="section" id="langwang-service" aria-labelledby="langwang-service-title">'
            '<span class="overline">RESET, RENEWAL & UPGRADE</span>'
            '<h2 id="langwang-service-title">重置、续费和升级，分别怎样处理？</h2>'
            '<p class="langwang-lead">以下流量规则适用于普通周期套餐：年付标准，以及入门、进阶、高端、商业四款月付。</p>'
            '<div class="langwang-service-grid"><article><span class="overline">01 / RESET</span>'
            '<h3>重置：立即恢复完整额度</h3><p>购买与所购套餐同价的流量重置包后，立即恢复完整流量额度。</p>'
            '<p>年付标准及四款月付的重置包均可使用lw888享八折。</p></article>'
            '<article><span class="overline">02 / RENEWAL</span><h3>续费：延长有效期</h3>'
            '<p>提前续费只延长有效期，不立即补充流量，仍按原定刷新日期更新。</p>'
            '<p>周期套餐续费可使用lw888。定制线路包的具体流量处理规则需另行核对。</p></article>'
            '<article><span class="overline">03 / UPGRADE</span><h3>升级：重算周期与可用流量</h3><ol>'
            + upgrade + '</ol></article></div><p class="langwang-note">重置对有效期与原定刷新日的影响，以及升级差价算法、退回渠道和处理时间尚未提供。'
            '三款一次性包和定制线路包的流量规则需分别核对。</p>'
            '<p class="langwang-payment"><strong>付款方式：</strong>已确认支持' + e('、'.join(data['payment_methods']))
            + '。' + e(coupon_rules(coupon)) + '</p><div class="langwang-source-links">'
            '<a href="data/langwang-service-rules.json">流量、付款与售后规则 JSON ↓</a>'
            '<a href="#langwang-coupon">核对优惠使用规则 →</a></div></section>')


def render_refund(data, entry_url):
    refund = data['refund']
    hours = str(refund['deadline_hours_after_purchase'])
    return ('<section class="section" id="langwang-refund" aria-labelledby="langwang-refund-title">'
            '<span class="overline">TECHNICAL-ISSUE REFUND</span>'
            '<h2 id="langwang-refund-title">技术问题退款：购买后' + hours + '小时内申请</h2>'
            '<div class="langwang-refund-panel"><h3>经客服协助后仍完全无法使用，可申请全额退款。</h3>'
            '<p>适用条件为因技术问题，经客服协助后仍完全无法使用。须在购买后' + hours
            + '小时内，登录浪网官网后台联系客服办理。</p>'
            '<p class="langwang-note">这是申请时限，退款方式和到账时间尚未提供，请在办理时向客服确认。</p>'
            '<a class="langwang-client-entry" href="' + e(entry_url, quote=True)
            + '" target="_blank" rel="sponsored noopener noreferrer">前往浪网官网入口 ↗</a></div></section>')
