"""Build the homepage hero promotion from the confirmed Invisible offer."""
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from html import escape as e
from pathlib import Path
import json
import re

from site_chrome import write_changed


def build_home_feature(root):
    root = Path(root)
    promo = json.loads((root / 'data/invisible-promo.json').read_text(encoding='utf-8'))
    plans = json.loads((root / 'data/invisible-plans.json').read_text(encoding='utf-8'))
    plan = next(p for p in plans['plans'] if p['id'] == promo['recommended_plan_id'])
    coupon = promo['coupon']
    annual = (Decimal(str(plan['price'])) * Decimal(coupon['pay_rate'])).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    monthly = (annual / 12).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    assert plan['billing'] == 'year' and coupon['applies_to'] == 'all_plans'
    entry = 'https://varnexa.invisibleaff.com/#/?code=JF4seZUy'
    card = f'''<aside class="home-invisible-feature" id="home-invisible-feature" aria-labelledby="home-invisible-title">
<div class="home-feature-top" id="featured-brand"><span class="featured-label">本站主推</span><span>INVISIBLE NETWORK</span></div>
<a class="home-feature-brand" href="brand-yinxingren.html"><span class="home-feature-logo invisible-brand-logo"><img class="invisible-logo-image" src="assets/invisible-network-logo.jpg" width="512" height="512" alt="隐形人机场Logo" decoding="async"></span><div><h2 id="home-invisible-title">隐形人机场</h2><p>IEPL专线 · 多设备连接</p></div></a>
<div class="home-feature-plan"><p class="home-feature-plan-label">推荐年付套餐</p><h3>{e(plan['name'])}</h3><div class="home-feature-offer"><div class="home-feature-quota"><strong>{plan['traffic_gb']}<small>GB</small></strong><span>每30天刷新</span></div><div class="home-feature-price"><span>八折后 · 年付折算</span><div><small>¥</small><strong>{monthly:.2f}</strong><span>/月</span></div></div></div><p class="home-feature-annual"><span>原价 <s>¥{plan['price']}/年</s></span><span>券后实付 <b>¥{annual:.2f}/年</b></span></p></div>
<div class="home-feature-coupon" data-home-coupon><div class="home-feature-coupon-row"><div><label for="home-invisible-coupon">八折优惠码</label><input id="home-invisible-coupon" value="{e(coupon['code'],quote=True)}" readonly aria-label="隐形人八折优惠码"></div><button type="button" aria-label="复制首页隐形人优惠码">复制</button></div><p>全部套餐适用 · 无到期限制</p><span class="home-feature-copy-status" role="status" aria-live="polite"></span></div>
<div class="home-feature-actions"><a class="btn" href="brand-yinxingren.html">了解隐形人机场 <span aria-hidden="true">→</span></a><a href="{entry}" target="_blank" rel="sponsored noopener noreferrer">前往官网 <span aria-hidden="true">↗</span></a></div>
<p class="home-feature-note">按年付款，每月金额为折算值；结算时填写优惠码。</p>
</aside>'''
    path = root / 'index.html'
    html = path.read_text(encoding='utf-8')
    html = re.sub(r'<section class="invisible-feature" id="featured-brand">.*?</section>', '', html, count=1, flags=re.S)
    if 'id="home-invisible-feature"' in html:
        html, count = re.subn(r'<aside\b[^>]*id="home-invisible-feature"[^>]*>.*?</aside>', lambda _: card, html, count=1, flags=re.S)
    else:
        html, count = re.subn(r'<div class="orbital"[^>]*>.*?</div></section>', lambda _: card + '</section>', html, count=1, flags=re.S)
    assert count == 1, 'Expected one homepage hero promotion target.'
    html = html.replace('<section class="hero">', '<section class="hero home-feature-hero">', 1)
    html = re.sub(r'<link rel="stylesheet" href="assets/home-feature\.css(?:\?[^"]*)?">', '', html)
    html = re.sub(r'<script src="assets/home-feature\.js(?:\?[^"]*)?" defer></script>', '', html)
    css_rev = sha256((root / 'assets/home-feature.css').read_bytes()).hexdigest()[:12]
    js_rev = sha256((root / 'assets/home-feature.js').read_bytes()).hexdigest()[:12]
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/home-feature.css?v=' + css_rev + '"></head>', 1)
    html = html.replace('</body>', '<script src="assets/home-feature.js?v=' + js_rev + '" defer></script></body>', 1)
    write_changed(path, html)
