"""Keep LadderCloud's confirmed discount separate from the supplied list prices."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e


def discounted_price(plan, data):
    coupon = data['coupon']
    if plan['id'] not in coupon['applies_to_plan_ids']:
        return None
    return (Decimal(str(plan['price_cny'])) * Decimal(coupon['pay_multiplier'])).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP)


def validate_coupon(data, plans):
    coupon = data['coupon']
    assert data['brand_id'] == 'tiziyun' and data['collection_status'] == 'confirmed'
    assert coupon['code'] == '2hy85' and Decimal(coupon['pay_multiplier']) == Decimal('0.85')
    allowed, excluded = set(coupon['applies_to_plan_ids']), set(coupon['excluded_plan_ids'])
    assert allowed == {p['id'] for p in plans if p['kind'] in ('monthly', 'custom')}
    assert excluded == {p['id'] for p in plans if p['kind'] in ('annual', 'one_time')}
    assert len(allowed) == 5 and len(excluded) == 4 and allowed.isdisjoint(excluded)
    assert len(allowed | excluded) == len(plans) == 9
    assert set(coupon['traffic_reset_applies_to_plan_ids']) == {p['id'] for p in plans if p['kind'] == 'monthly'}
    assert coupon['expires_on'] is None and coupon['expiry_policy'] == '无到期限制'
    assert coupon['renewal_applicability'] is True and coupon['traffic_reset_applicability'] is True
    assert coupon['stackability'] is False


def coupon_rules(data):
    coupon = data['coupon']
    renewal = '适用套餐的新购与续费可用' if coupon['renewal_applicability'] else '续费不适用'
    reset = '四款月付方案的流量重置包可用' if coupon['traffic_reset_applicability'] else '流量重置包不适用'
    stacking = '不能叠加其他优惠' if not coupon['stackability'] else '可叠加其他优惠'
    return renewal + '；' + reset + '；' + stacking + '。'


def coupon_faqs(data):
    coupon = data['coupon']
    return [
        ('梯子云优惠码是什么，哪些套餐可以使用？',
         '优惠码' + coupon['code'] + '为八五折，无到期限制。' + coupon['scope'] + '。'),
        ('2hy85可以用于续费、流量重置包或叠加其他优惠吗？', coupon_rules(data)),
        ('梯子云89元年付和三款买断包的券后价是多少？',
         '这四款套餐不适用2hy85，不生成八五折券后价。年付保活为89元/年；三款买断包按已提供报价分别为169元、449元和849元一次性。')
    ]


def render_coupon(data):
    coupon = data['coupon']
    code = e(coupon['code'], quote=True)
    return ('<section class="section" id="tiziyun-coupon" aria-labelledby="tiziyun-coupon-title">'
            '<span class="overline">LADDERCLOUD COUPON / 15% OFF</span>'
            '<h2 id="tiziyun-coupon-title">5款套餐享八五折，4款套餐不适用。</h2>'
            '<div class="tiziyun-coupon-panel"><div><p class="tiziyun-lead">' + e(coupon['scope'])
            + '。</p><p>优惠码<strong>' + code + '</strong> · ' + e(coupon['expiry_policy'])
            + '</p><p>' + e(coupon_rules(data)) + '</p></div>'
            '<div class="tiziyun-coupon-copy" data-tiziyun-coupon-box>'
            '<label for="tiziyun-coupon-code">八五折优惠码</label><div>'
            '<input id="tiziyun-coupon-code" type="text" value="' + code
            + '" readonly spellcheck="false" autocomplete="off">'
            '<button type="button" aria-describedby="tiziyun-coupon-copy-status">复制优惠码</button></div>'
            '<p id="tiziyun-coupon-copy-status" role="status" aria-live="polite"></p></div></div>'
            '<p class="tiziyun-note">优惠条款由站长于' + e(data['updated_on'])
            + '逐项确认。券后价按已提供报价×0.85计算；其他付款周期未提供的总额不推算，请核对官网结算页面。</p>'
            '<div class="tiziyun-source-links"><a href="data/tiziyun-coupon.json">优惠范围与使用条款 JSON ↓</a></div></section>')
