"""Render Lingdong's confirmed coupon and calculate only eligible quoted prices."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e


def eligible(plan,coupon):
    return plan['id'] in coupon['applies_to_plan_ids'] and plan['id'] not in coupon['excluded_plan_ids']


def discounted(plan,coupon):
    if not eligible(plan,coupon):
        return None
    return (Decimal(str(plan['price_cny']))*Decimal(coupon['pay_multiplier'])).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)


def coupon_box(coupon,floating=False):
    prefix='lingdong-floating' if floating else 'lingdong-main'
    outer='fp-coupon' if floating else 'lingdong-coupon-box'
    return f'''<div class="{outer}" data-lingdong-coupon-box><label for="{prefix}-coupon-code">优惠码 · {e(coupon['discount_label'])}</label><div><input id="{prefix}-coupon-code" type="text" value="{e(coupon['code'],quote=True)}" readonly aria-label="灵动云优惠码" spellcheck="false"><button class="{'fp-copy' if floating else 'lingdong-coupon-copy'}" type="button" aria-label="{'复制浮窗灵动云优惠码' if floating else '复制灵动云优惠码'}">复制</button></div><p>穿云、至尊私人定制除外 · 其余7款八折 · 无到期限制</p><span class="lingdong-copy-status" role="status" aria-live="polite"></span></div>'''


def render_coupon(coupon,url):
    return f'''<section class="section" id="lingdong-coupon"><div class="lingdong-section-title"><span class="overline">LINGDONG / COUPON & ELIGIBILITY</span><h2>优惠码 {e(coupon['code'])}，7款套餐享八折。</h2><p>穿云与至尊私人定制不适用；其余7款套餐按原价的80%计算，无到期限制。</p></div><div class="lingdong-coupon-layout">{coupon_box(coupon)}<div class="lingdong-coupon-scope"><span class="lingdong-index">CHECK YOUR PLAN BEFORE PAYING</span><h3>先核对套餐，再填写优惠码。</h3><p>适用：拂风、驭浪、破晓、凌霄、闲云、惊云、飞云。</p><p>穿云保持99元/年，至尊私人定制保持680元/月。</p><a href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往灵动云使用优惠码 ↗</a></div></div><p class="lingdong-note">券后金额按本页已提供的报价计算，具体结算金额请核对官网。重置包、升级订单与其他优惠叠加条件需分别确认。</p></section>'''


def coupon_faqs(coupon):
    return [
        ('灵动云优惠码是什么，可以优惠多少？','优惠码为'+coupon['code']+'，享八折，即按原价的80%支付。穿云、至尊私人定制除外，其余7款适用，无到期限制。'),
        ('穿云和至尊私人定制可以使用wsj888吗？','不可以。穿云保持99元/年、年付折算8.25元/月；至尊私人定制保持680元/月，不计算这两款的八折价。'),
        ('wsj888八折后的套餐价格是多少？','按已提供报价计算：拂风16元/月、驭浪40元/月、破晓80元/月、凌霄144元/月；闲云159.20元、惊云399.20元、飞云719.20元一次性。其他付款周期金额需核对对应报价，不用月价推算。')
    ]


def coupon_markdown(coupon):
    return ('## 八折优惠码\n\n优惠码：`'+coupon['code']+'`。穿云、至尊私人定制不适用，其余7款套餐享八折，无到期限制。\n\n'+
            '重置包、升级订单和其他优惠叠加条件未确认，单独核对。\n\n')
