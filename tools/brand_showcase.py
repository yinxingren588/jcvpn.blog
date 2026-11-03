"""Keep Invisible's featured presentation separate from the four other brands."""
from hashlib import sha256
from pathlib import Path
import re

from site_chrome import write_changed


FEATURE = '''<section class="brand-showcase-feature" id="invisible-brand-showcase" aria-labelledby="invisible-showcase-title"><div class="brand-showcase-main"><span class="brand-showcase-label">本站主推</span><div class="brand-showcase-identity"><span class="brand-showcase-logo invisible-brand-logo"><img class="invisible-logo-image" src="assets/invisible-network-logo.jpg" width="512" height="512" alt="隐形人Logo" decoding="async"></span><div><span class="brand-showcase-en">INVISIBLE NETWORK</span><h2 id="invisible-showcase-title">隐形人</h2><p>IEPL专线，面向日常连接与多端使用。</p></div></div><div class="brand-showcase-tags"><span>IEPL专线</span><span>9款套餐</span><span>多设备接入</span></div></div><div class="brand-showcase-action"><p>套餐、客户端、使用记录与常见问题，在品牌页集中查看。</p><a class="btn" href="brand-yinxingren.html">进入隐形人品牌页 <span aria-hidden="true">→</span></a><a class="brand-showcase-plan-link" href="brand-yinxingren.html#invisible-plans">查看套餐与流量 →</a></div></section>'''


def build_brand_showcase(root):
    root = Path(root)
    revision = sha256((root / 'assets/brand-showcase.css').read_bytes()).hexdigest()[:12]
    for name in ('index.html', 'brands.html'):
        path = root / name
        html = path.read_text(encoding='utf-8')
        # The homepage already has a large Invisible promotion in its hero.
        html = re.sub(r'<a\b(?=[^>]*class="[^"]*\bowner-card\b)[^>]*>.*?</a>', '', html, flags=re.S)
        html = html.replace('<div class="brands">', '<div class="brands separated-brand-grid">')
        if name == 'brands.html':
            if 'id="invisible-brand-showcase"' in html:
                html = re.sub(r'<section class="brand-showcase-feature".*?</section>', lambda _: FEATURE, html, count=1, flags=re.S)
            else:
                html = html.replace('<section class="section profile-hub">', FEATURE + '<section class="section profile-hub">', 1)
            marker = '<div class="brand-showcase-other-title"><span class="overline">MORE BRAND PROFILES</span><h2>其他品牌</h2><p>分别查看微风网络、飞猫云、暮光网络与灵动云的资料。</p></div>'
            if 'class="brand-showcase-other-title"' not in html:
                html = html.replace('<section class="section profile-hub">', '<section class="section profile-hub">' + marker, 1)
        else:
            html = html.replace('从这里，认识一个品牌。', '继续了解其他品牌。')
        html = re.sub(r'<link rel="stylesheet" href="assets/brand-showcase\.css(?:\?[^"]*)?">', '', html)
        html = html.replace('</head>', '<link rel="stylesheet" href="assets/brand-showcase.css?v=' + revision + '"></head>', 1)
        write_changed(path, html)
