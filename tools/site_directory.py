"""Apply a consistent site directory and per-page chapter links to every content page."""
from hashlib import sha256
from html import escape, unescape
from pathlib import Path
import json
import re

from site_chrome import write_changed


def plain_text(markup):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', '', markup))).strip()


def add_chapters(html, name):
    if name == 'index.html':
        return html, [('home-overview', '首页介绍'), ('home-invisible-feature', '隐形人主推'),
                      ('search-guides', '按需求选专题'), ('brands', '品牌档案'), ('reading', '精选文章'), ('brand-intake', '新增品牌')]
    main = re.search(r'<main\b[^>]*>(.*?)</main>', html, re.S)
    if not main:
        return html, [('top', '返回页首')]
    body = main[1]
    ids = set(re.findall(r'\bid=["\']([^"\']+)', html))
    chapters = []
    def add_heading(match):
        # Catalog card titles are links to articles, rather than chapters of this page.
        before = body[:match.start()]
        if before.rfind('<a ') > before.rfind('</a>'):
            return match[0]
        label = plain_text(match['text'])
        if name == 'faq.html':
            label = re.sub(r'^\d{2}\s+', '', label)
        if not label:
            return match[0]
        found = re.search(r'\bid=["\']([^"\']+)', match['attrs'])
        anchor = found[1] if found else 'quick-section-' + str(len(chapters) + 1)
        while not found and anchor in ids:
            anchor += '-page'
        ids.add(anchor)
        chapters.append((anchor, label))
        if found:
            return match[0]
        return '<h2' + match['attrs'] + ' id="' + anchor + '">' + match['text'] + '</h2>'
    body = re.sub(r'<h2\b(?P<attrs>[^>]*)>(?P<text>.*?)</h2>', add_heading, body, flags=re.S)
    html = html[:main.start(1)] + body + html[main.end(1):]
    return html, chapters or [('top', '返回页首')]


def render_directory(name, chapters):
    toc = ''.join('<a href="#' + escape(anchor, quote=True) + '" data-home-section="' + escape(anchor, quote=True) +
                  '" title="' + escape(label, quote=True) + '"><span class="home-dir-number">' + f'{index:02}' +
                  '</span><span>' + escape(label) + '</span></a>' for index, (anchor, label) in enumerate(chapters, 1))
    routes = [('index.html', '首页'), ('brands.html', '品牌介绍'), ('topics.html', '博客专题'),
              ('blog.html', '文章目录'), ('faq.html', 'FAQ专题'), ('about.html', '关于本站'), ('contact.html', '联系我们')]
    route_links = ''.join('<a href="' + url + '"' + (' aria-current="page"' if name == url else '') +
                          '><span>' + label + '</span><span class="home-dir-arrow" aria-hidden="true">↗</span></a>' for url, label in routes)
    brands = [('brand-breezenet.html', '微风网络', 'breezenet-logo-hd.png'),
              ('brand-feimaoyun.html', '飞猫云', 'feimaoyun-logo-hd.png'),
              ('brand-muguang.html', '暮光网络', 'feimaoyun-logo-hd.png'),
              ('brand-lingdongyun.html', '灵动云', 'lingdongyun-logo-hd.png')]
    brand_links = ''.join('<a href="' + url + '" aria-label="查看'+escape(label,quote=True)+'品牌资料"' + (' aria-current="page"' if name == url else '') +
                          '><span class="home-dir-brand"><img src="assets/' + logo + '" width="1254" height="1254" alt="'+escape(label,quote=True)+'Logo" decoding="async"></span><span>' +
                          label + '</span></a>' for url, label, logo in brands)
    for b in json.loads((Path(__file__).resolve().parents[1]/'data/new-brands.json').read_text(encoding='utf-8'))['brands']:
        mark='<span class="home-dir-monogram" aria-hidden="true">'+escape(b['mark'])+'</span>'
        if b.get('logo_path'):
            mark='<span class="home-dir-brand"><img src="'+escape(b['logo_path'],quote=True)+'" width="'+str(b['logo_width'])+'" height="'+str(b['logo_height'])+'" alt="'+escape(b['name'],quote=True)+'Logo" decoding="async"></span>'
        brand_links+='<a href="'+b['profile_path']+'" aria-label="查看'+escape(b['name'],quote=True)+'品牌资料"'+(' aria-current="page"' if name==b['profile_path'] else '')+'>'+mark+'<span>'+escape(b['name'])+' <small>资料待补</small></span></a>'
    current = ' aria-current="page"' if name == 'brand-yinxingren.html' else ''
    return '''<aside class="home-directory-root" id="home-directory-root" data-open="auto" aria-label="页面快捷目录">
<section class="home-directory-panel" id="home-directory-panel" aria-labelledby="home-directory-title">
<div class="home-directory-head"><div><span>QUICK NAVIGATION</span><h2 id="home-directory-title">快捷目录</h2></div><button type="button" class="home-directory-close" aria-label="收起快捷目录" title="收起目录">×</button></div>
<a class="site-directory-feature" href="brand-yinxingren.html" aria-label="查看隐形人品牌资料"''' + current + '''><img src="assets/invisible-network-logo.jpg" width="512" height="512" alt="隐形人Logo" decoding="async"><span><small>本站主推</small><strong>隐形人</strong></span><span aria-hidden="true">→</span></a>
<nav class="home-directory-links" aria-label="页面快捷导航"><div class="home-directory-group"><h3>本页目录</h3>''' + toc + '''</div><div class="home-directory-group"><h3>网站导航</h3>''' + route_links + '''</div><div class="home-directory-group"><h3>其他品牌</h3>''' + brand_links + '''</div></nav>
<p class="home-directory-foot">点击目录，快速找到你想看的内容。</p></section><button class="home-directory-launcher" type="button" aria-controls="home-directory-panel" aria-expanded="false" aria-label="展开快捷目录"><span aria-hidden="true">☷</span>快捷目录</button></aside>'''


def apply_site_directory(root):
    root = Path(root)
    css_rev = sha256((root / 'assets/home-directory.css').read_bytes()).hexdigest()[:12]
    js_rev = sha256((root / 'assets/home-directory.js').read_bytes()).hexdigest()[:12]
    for path in root.glob('*.html'):
        # This legacy entry immediately redirects to the homepage, which carries the directory.
        if path.name == '01-首页框架.html':
            continue
        html = path.read_text(encoding='utf-8')
        html = re.sub(r'<aside\b[^>]*id="home-directory-root"[^>]*>.*?</aside>', '', html, flags=re.S)
        html, chapters = add_chapters(html, path.name)
        directory = render_directory(path.name, chapters)
        def body_tag(match):
            attrs = match[1]
            if 'has-site-directory' not in attrs:
                if re.search(r'\bclass="', attrs):
                    attrs = re.sub(r'\bclass="', 'class="has-site-directory ', attrs, count=1)
                else:
                    attrs += ' class="has-site-directory"'
            return '<body' + attrs + '>' + directory
        html, count = re.subn(r'<body([^>]*)>', body_tag, html, count=1)
        assert count == 1, path.name + ': expected one body element'
        html = re.sub(r'<link rel="stylesheet" href="assets/home-directory\.css(?:\?[^"]*)?">', '', html)
        html = re.sub(r'<script src="assets/home-directory\.js(?:\?[^"]*)?" defer></script>', '', html)
        html = html.replace('</head>', '<link rel="stylesheet" href="assets/home-directory.css?v=' + css_rev + '"></head>', 1)
        html = html.replace('</body>', '<script src="assets/home-directory.js?v=' + js_rev + '" defer></script></body>', 1)
        write_changed(path, html)
