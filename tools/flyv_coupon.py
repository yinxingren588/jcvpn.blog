"""Render FlyV's confirmed coupon separately from the original plan quotes."""
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
    plan_ids = {p['id'] for p in plans}
    eligible = coupon['applies_to_plan_ids']
    excluded = coupon['excluded_plan_ids']
    assert data['collection_status'] == 'confirmed'
    assert coupon['code'] == 'fly20' and Decimal(coupon['pay_multiplier']) == Decimal('0.80')
    assert len(eligible) == len(set(eligible)) == len(plan_ids) == 9
    assert set(eligible) == plan_ids and not excluded
    assert coupon['expires_on'] is None and coupon['expiry_policy'] == '无到期限制'
    assert all(coupon[key] is None or isinstance(coupon[key], bool) for key in
               ('renewal_applicability', 'traffic_reset_applicability', 'stackability'))


def coupon_rules(data):
    coupon = data['coupon']
    rules = []
    for key, label in [('renewal_applicability', '续费订单'), ('traffic_reset_applicability', '流量重置包')]:
        value = coupon[key]
        rules.append(label+('可使用该码' if value is True else '不能使用该码' if value is False else '适用性待确认'))
    value = coupon['stackability']
    rules.append('可叠加其他优惠' if value is True else '不能叠加其他优惠' if value is False else '优惠叠加规则待确认')
    return '；'.join(rules)+'。'


def excluded_orders(data):
    return [label for key, label in [('renewal_applicability', '续费订单'),
                                   ('traffic_reset_applicability', '流量重置包')]
            if data['coupon'][key] is False]


def coupon_price_label(data):
    excluded = excluded_orders(data)
    return 'fly20 八折后'+('（'+'、'.join(excluded)+'除外）' if excluded else '')


def coupon_faqs(data):
    coupon = data['coupon']
    return [
        ('飞v优惠码是什么，折扣和适用范围如何？',
         '优惠码为'+coupon['code']+'，八折，适用于全部9款套餐，包括年付标准轻量版、四款月付、三款一次性流量包和原生IP·独享黄金专线，无到期限制。'+coupon_rules(data)),
        ('飞v年付轻量版八折后多少钱，可以按月付款吗？',
         '99元年付报价使用fly20八折后为79.20元/年，全年支付，折合约6.60元/月；每月流量仍为65GB。6.60元是年费除以12的预算换算，不是单月购买价。'+('续费不能使用fly20，续费订单金额需核对后台。' if coupon['renewal_applicability'] is False else '')),
        ('fly20是否也适用于续费、重置包或叠加其他优惠？',
         coupon_rules(data)+'具体订单金额请在后台核对。')
    ]


def render_coupon(data):
    coupon = data['coupon']
    code = e(coupon['code'], quote=True)
    rules = e(coupon_rules(data))
    excluded = excluded_orders(data)
    heading = '9款套餐享八折'+('，'+'、'.join(excluded)+'除外。' if excluded else '。')
    exclusion_note = '、'.join(excluded)+'不能使用该码。' if excluded else ''
    return '''<section class="section flyv-coupon-section" id="flyv-coupon" aria-labelledby="flyv-coupon-title">
<div class="flyv-coupon-panel"><div><span class="overline">FLYV COUPON / 20% OFF</span><h2 id="flyv-coupon-title">'''+e(heading)+'''</h2><p>优惠码 fly20 适用于年付轻量版、四款月付、三款一次性流量包及独享黄金专线，无到期限制。<strong>'''+e(exclusion_note)+'''</strong></p><p class="flyv-coupon-example">年付标准轻量版 <s>¥99.00/年</s> <strong>¥79.20/年</strong><span>全年支付 · 折合约 ¥6.60/月 · 每月65GB · 续费不能使用该码</span></p></div>
<div class="flyv-coupon-copy" data-flyv-coupon-box><label for="flyv-coupon-code">八折优惠码</label><div><input id="flyv-coupon-code" type="text" value="'''+code+'''" readonly spellcheck="false" autocomplete="off"><button type="button" aria-describedby="flyv-coupon-copy-status">复制优惠码</button></div><p id="flyv-coupon-copy-status" class="flyv-copy-status" role="status" aria-live="polite"></p></div></div>
<p class="flyv-material-note">优惠与适用限制由站长逐项确认，最近更新：'''+e(data.get('updated_on',data['confirmed_on']))+'''。下列券后价按所列报价×0.8计算，实际订单请核对结算页面；尚未提供的其他付款周期金额不推算。'''+rules+'''<a href="data/feiv-coupon.json">查看优惠源资料 JSON ↓</a></p></section>'''
