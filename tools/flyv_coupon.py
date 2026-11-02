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


def coupon_faqs(data):
    coupon = data['coupon']
    return [
        ('飞v优惠码是什么，折扣和适用范围如何？',
         '优惠码为'+coupon['code']+'，八折，适用于全部9款套餐，包括年付标准轻量版、四款月付、三款一次性流量包和原生IP·独享黄金专线，无到期限制。'),
        ('飞v年付轻量版八折后多少钱，可以按月付款吗？',
         '99元年付报价使用fly20八折后为79.20元/年，全年支付，折合约6.60元/月；每月流量仍为65GB。6.60元是年费除以12的预算换算，不是单月购买价。'),
        ('fly20是否也适用于续费、重置包或叠加其他优惠？',
         '目前确认的是全部9款套餐的八折优惠。续费、流量重置包是否可用，以及是否可叠加其他优惠，尚未提供明确规则，需在相应订单或向后台客服核对。')
    ]


def render_coupon(data):
    coupon = data['coupon']
    code = e(coupon['code'], quote=True)
    return '''<section class="section flyv-coupon-section" id="flyv-coupon" aria-labelledby="flyv-coupon-title">
<div class="flyv-coupon-panel"><div><span class="overline">FLYV COUPON / 20% OFF</span><h2 id="flyv-coupon-title">全部9款套餐，使用 fly20 享八折。</h2><p>年付轻量版、四款月付、三款一次性流量包及独享黄金专线均适用，无到期限制。</p><p class="flyv-coupon-example">年付标准轻量版 <s>¥99.00/年</s> <strong>¥79.20/年</strong><span>全年支付 · 折合约 ¥6.60/月 · 每月65GB</span></p></div>
<div class="flyv-coupon-copy" data-flyv-coupon-box><label for="flyv-coupon-code">八折优惠码</label><div><input id="flyv-coupon-code" type="text" value="'''+code+'''" readonly spellcheck="false" autocomplete="off"><button type="button" aria-describedby="flyv-coupon-copy-status">复制优惠码</button></div><p id="flyv-coupon-copy-status" class="flyv-copy-status" role="status" aria-live="polite"></p></div></div>
<p class="flyv-material-note">优惠由站长于'''+e(data['confirmed_on'])+'''逐项确认。下列券后价按所列报价×0.8计算，实际订单请核对结算页面；尚未提供的其他付款周期金额不推算。续费、重置包及优惠叠加规则待确认。<a href="data/feiv-coupon.json">查看优惠源资料 JSON ↓</a></p></section>'''
