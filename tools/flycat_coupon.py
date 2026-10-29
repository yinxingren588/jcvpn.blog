"""Render confirmed Flycat coupon facts and prices only for eligible plans."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e


def eligible(coupon, plan):
    return coupon['applies_to_all_plans'] is True or plan['id'] in (coupon['applies_to_plan_ids'] or [])


def discounted(coupon, price):
    return (Decimal(str(price)) * Decimal(str(coupon['payable_ratio']))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def scope_text(coupon):
    if coupon['applies_to_all_plans'] is True:
        return '全部7款套餐适用'
    if coupon['applies_to_plan_ids'] == ['starlight', 'starring', 'galaxy', 'universe', 'timeless', 'custom']:
        return '学生版不适用，其余6款套餐适用'
    return '适用范围以官网结算页为准'


def expiry_text(coupon):
    if coupon['no_expiry_confirmed']:
        return '无到期限制'
    if coupon['expiry_date']:
        return '有效期至' + coupon['expiry_date']
    return '有效期请核对官网'


def floating_coupon(coupon):
    return '<div class="fp-coupon"><label for="flycat-floating-coupon-code">优惠码 · ' + e(coupon['discount_label']) + '</label><div><input id="flycat-floating-coupon-code" type="text" readonly value="' + e(coupon['code'], quote=True) + '" aria-label="飞猫云优惠码"><button class="fp-copy" type="button" aria-label="复制飞猫云优惠码">复制</button></div><p>' + e(scope_text(coupon)) + ' · ' + e(expiry_text(coupon)) + '</p></div>'


def coupon_faqs(coupon):
    return [
        ('飞猫云优惠码是什么，能优惠多少？', '站长确认的优惠码为' + coupon['code'] + '，享' + coupon['discount_label'] + '优惠，即按原价的90%支付。' + scope_text(coupon) + '；' + expiry_text(coupon) + '，实际金额以结算页为准。'),
        ('飞猫云学生版可以使用flycat888吗？', '学生版不适用。学生版保持84元/年、每月50GB，折合7元/月；优惠码适用于星耀、星环、银河、宇宙、不限时和定制套餐。')
    ]


def render_coupon(coupon, url):
    return f'''<section class="section" id="flycat-coupon"><div class="flycat-section-title"><span class="overline">FLYCAT / COUPON</span><h2>飞猫云优惠码：{e(coupon['code'])}，享九折。</h2><p>九折按原价的90%计算。{e(scope_text(coupon))}，实际结算金额请核对官网。</p></div><div class="flycat-coupon-bar"><div><span>优惠码</span><code>{e(coupon['code'])}</code></div><div><strong>{e(coupon['discount_label'])}</strong><p>{e(expiry_text(coupon))}</p></div><a class="btn" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往官网使用 ↗</a></div><p class="flycat-note">可在左侧推荐卡中复制优惠码。流量重置包与升级订单是否适用，请另行核对。</p></section>'''


def coupon_markdown(coupon):
    return '## 优惠码\n\n优惠码：`' + coupon['code'] + '`；优惠：' + coupon['discount_label'] + '，按原价的90%支付。\n\n' + scope_text(coupon) + '；' + expiry_text(coupon) + '。流量重置包与升级订单是否适用需另行核对。\n\n'
