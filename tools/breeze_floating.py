"""Render the Breezenet floating recommendation from confirmed plan data."""
from html import escape as e


def render(plan, coupon, annual_paid, monthly_paid, url, logo_image, scope, expiry):
    launcher_logo = logo_image.replace('alt="微风网络 Breezenet Logo"', 'alt=""') if logo_image else ''
    return f'''<aside class="floating-promo" id="breezenet-floating-promo" data-open="auto" aria-label="微风网络套餐与优惠推荐">
<section class="fp-panel" id="breeze-floating-panel" aria-label="微风推荐套餐和优惠码">
<div class="fp-handle" title="拖动移动推荐卡"><span class="fp-grip" aria-hidden="true">⠿</span><span class="fp-label">套餐推荐</span><div class="fp-window-actions"><button type="button" class="fp-reset" aria-label="恢复微风推荐卡默认位置" title="恢复默认位置">↺</button><button type="button" class="fp-close" aria-label="收起微风推荐卡" title="收起">×</button></div></div>
<div class="fp-content"><a class="fp-brand" href="#top">{logo_image or ''}<span><strong>微风网络</strong><small>Breezenet · IPLC专线</small></span></a>
<div class="fp-plan"><span class="fp-eyebrow">推荐套餐 · 年付</span><h2>{e(plan['name'])}</h2><div class="fp-traffic"><strong>{plan['traffic_gb']}<small>GB</small></strong><span>每月刷新</span></div></div>
<div class="fp-pricing"><p>原价 <s>¥{plan['price']}/年</s><span>{e(coupon['discount_label'])}</span></p><div><small>年付折算约</small><strong>¥{monthly_paid}</strong><span>/月</span></div><p class="fp-annual-total">券后年付合计 ¥{annual_paid}</p></div>
<div class="fp-coupon"><label for="breeze-floating-coupon-code">优惠码 · {e(coupon['discount_label'])}</label><div><input id="breeze-floating-coupon-code" type="text" readonly value="{e(coupon['code'], quote=True)}" aria-label="微风优惠码"><button class="fp-copy" type="button" aria-label="复制微风优惠码">复制</button></div><p>{e(scope)} · {e(expiry)}</p></div>
<a class="fp-cta" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往官网使用 <span aria-hidden="true">↗</span></a>
<p class="fp-note">实际按年支付，结算金额以官网为准。</p><p class="fp-copy-status" role="status" aria-live="polite"></p></div>
</section>
<button type="button" class="fp-launcher" aria-controls="breeze-floating-panel" aria-expanded="false" aria-label="展开微风套餐推荐">{launcher_logo}<span>微风优惠</span><span aria-hidden="true">＋</span></button>
</aside>'''
