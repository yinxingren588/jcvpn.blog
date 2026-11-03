"""Keep WaveNet's confirmed coupon separate from its original plan quotes."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e


def discounted_price(plan, data):
    coupon = data['coupon']
    if plan['id'] not in coupon['applies_to_plan_ids']:
        return None
    return (Decimal(str(plan['price_cny'])) * Decimal(coupon['pay_multiplier'])).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP)


def validate_coupon(data, plans):
    c = data['coupon']
    assert data['brand_id'] == 'langwang' and data['collection_status'] == 'confirmed'
    assert c['code'] == 'lw888' and Decimal(c['pay_multiplier']) == Decimal('0.8')
    assert set(c['applies_to_plan_ids']) == {p['id'] for p in plans}
    assert len(c['applies_to_plan_ids']) == len(plans) == 9 and c['excluded_plan_ids'] == []
    assert set(c['traffic_reset_applies_to_plan_ids']) == {
        p['id'] for p in plans if p['kind'] in ('annual', 'monthly')}
    assert c['expires_on'] is None and c['expiry_policy'] == '无到期限制'
    assert c['renewal_applicability'] is True and c['traffic_reset_applicability'] is True
    assert c['stackability'] is False


def coupon_rules(data):
    c = data['coupon']
    assert c['renewal_applicability'] and c['traffic_reset_applicability'] and not c['stackability']
    return '全部9款套餐可用；周期套餐续费可用；年付标准及四款月付的流量重置包可用；不能叠加其他优惠。'


def coupon_faqs(data):
    c = data['coupon']
    return [
        ('浪网优惠码是什么，哪些套餐可用？',
         '优惠码' + c['code'] + '，输入时不含大括号，为八折，无到期限制。' + c['scope'] + '。'),
        ('lw888可以用于续费、流量重置包或叠加优惠吗？', coupon_rules(data)),
        ('浪网年付标准使用八折码后多少钱？',
         '原价119元/年，使用lw888后全年支付95.20元，折合约7.93元/月，只作年度预算换算。每30天刷新80GB，仍按年购买。')
    ]


def render_coupon(data):
    c = data['coupon']
    code = e(c['code'], quote=True)
    return ('<section class="section" id="langwang-coupon" aria-labelledby="langwang-coupon-title">'
            '<span class="overline">WAVENET COUPON / 20% OFF</span>'
            '<h2 id="langwang-coupon-title">9款套餐，使用 lw888 享八折。</h2>'
            '<div class="langwang-coupon-panel"><div><p class="langwang-lead">' + e(c['scope'])
            + '。</p><p>优惠码 <strong>' + code + '</strong> · ' + e(c['expiry_policy'])
            + '</p><p>' + e(coupon_rules(data)) + '</p></div>'
            '<div class="langwang-coupon-copy" data-langwang-coupon-box>'
            '<label for="langwang-coupon-code">八折优惠码</label><div>'
            '<input id="langwang-coupon-code" type="text" value="' + code
            + '" readonly spellcheck="false" autocomplete="off">'
            '<button type="button" aria-describedby="langwang-coupon-copy-status">复制优惠码</button></div>'
            '<p id="langwang-coupon-copy-status" role="status" aria-live="polite"></p></div></div>'
            '<p class="langwang-note">优惠条款由站长于' + e(data['updated_on'])
            + '逐项确认。优惠价按已提供报价×0.8计算，请核对官网结算页面。定制线路包是否提供流量重置服务尚未确认。</p>'
            '<div class="langwang-source-links"><a href="data/langwang-coupon.json">优惠范围与使用条款 JSON ↓</a></div></section>')
