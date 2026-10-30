"""Maintain the homepage's compact left-hand shortcut directory."""
from hashlib import sha256
from pathlib import Path
import re

from site_chrome import write_changed


def build_home_directory(root):
    root = Path(root)
    path = root / 'index.html'
    html = path.read_text(encoding='utf-8')
    html = html.replace('<section class="hero home-feature-hero">', '<section class="hero home-feature-hero" id="home-overview">', 1)
    directory = '''<aside class="home-directory-root" id="home-directory-root" data-open="auto" aria-label="首页快捷目录">
<section class="home-directory-panel" id="home-directory-panel" aria-labelledby="home-directory-title">
<div class="home-directory-head"><div><span>QUICK NAVIGATION</span><h2 id="home-directory-title">快捷目录</h2></div><button type="button" class="home-directory-close" aria-label="收起首页快捷目录" title="收起目录">×</button></div>
<nav class="home-directory-links" aria-label="首页快捷导航">
<div class="home-directory-group"><h3>本页导航</h3><a href="#home-overview" data-home-section="home-overview"><span class="home-dir-number">01</span><span>首页介绍</span></a><a href="#home-invisible-feature" data-home-section="home-invisible-feature"><span class="home-dir-number">02</span><span>隐形人主推</span><small>推荐</small></a><a href="#brands" data-home-section="brands"><span class="home-dir-number">03</span><span>品牌档案</span></a><a href="#reading" data-home-section="reading"><span class="home-dir-number">04</span><span>精选文章</span></a></div>
<div class="home-directory-group"><h3>品牌直达</h3><a href="brand-yinxingren.html"><span class="home-dir-brand"><img src="assets/invisible-network-logo.jpg" width="512" height="512" alt="" decoding="async"></span><span>隐形人机场</span><small>主推</small></a><a href="brand-breezenet.html"><span class="home-dir-brand"><img src="assets/breezenet-logo-hd.png" width="1254" height="1254" alt="" decoding="async"></span><span>微风网络</span></a><a href="brand-feimaoyun.html"><span class="home-dir-brand"><img src="assets/feimaoyun-logo-hd.png" width="1254" height="1254" alt="" decoding="async"></span><span>飞猫云</span></a><a href="brand-muguang.html"><span class="home-dir-brand"><img src="assets/feimaoyun-logo-hd.png" width="1254" height="1254" alt="" decoding="async"></span><span>暮光网络</span></a><a href="brand-lingdongyun.html"><span class="home-dir-brand"><img src="assets/lingdongyun-logo-hd.png" width="1254" height="1254" alt="" decoding="async"></span><span>灵动云</span></a></div>
<div class="home-directory-group"><h3>内容与帮助</h3><a href="topics.html"><span class="home-dir-symbol" aria-hidden="true">▤</span><span>博客专题</span><span class="home-dir-arrow" aria-hidden="true">↗</span></a><a href="faq.html"><span class="home-dir-symbol" aria-hidden="true">?</span><span>FAQ专题</span><span class="home-dir-arrow" aria-hidden="true">↗</span></a><a href="about.html"><span class="home-dir-symbol" aria-hidden="true">i</span><span>关于本站</span><span class="home-dir-arrow" aria-hidden="true">↗</span></a><a href="contact.html"><span class="home-dir-symbol" aria-hidden="true">✉</span><span>联系我们</span><span class="home-dir-arrow" aria-hidden="true">↗</span></a></div>
</nav><p class="home-directory-foot">点击目录，快速找到你想看的内容。</p></section>
<button class="home-directory-launcher" type="button" aria-controls="home-directory-panel" aria-expanded="false" aria-label="展开首页快捷目录"><span aria-hidden="true">☷</span>快捷目录</button></aside>'''
    if 'id="home-directory-root"' in html:
        html, count = re.subn(r'<aside\b[^>]*id="home-directory-root"[^>]*>.*?</aside>', lambda _: directory, html, count=1, flags=re.S)
    else:
        html, count = re.subn(r'<body([^>]*)>', lambda m: m[0] + directory, html, count=1)
    assert count == 1, 'Expected one homepage directory insertion point.'
    html = re.sub(r'<link rel="stylesheet" href="assets/home-directory\.css(?:\?[^"]*)?">', '', html)
    html = re.sub(r'<script src="assets/home-directory\.js(?:\?[^"]*)?" defer></script>', '', html)
    css_rev = sha256((root / 'assets/home-directory.css').read_bytes()).hexdigest()[:12]
    js_rev = sha256((root / 'assets/home-directory.js').read_bytes()).hexdigest()[:12]
    html = html.replace('</head>', '<link rel="stylesheet" href="assets/home-directory.css?v=' + css_rev + '"></head>', 1)
    html = html.replace('</body>', '<script src="assets/home-directory.js?v=' + js_rev + '" defer></script></body>', 1)
    write_changed(path, html)
