"""Apply shared header/footer and maintain real site-information pages."""
from datetime import datetime, timezone, timedelta
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, quote


def write_changed(path, text):
    if not path.exists() or path.read_text(encoding='utf-8') != text:
        path.write_text(text, encoding='utf-8', newline='\n')


def read_contact(root):
    data = json.loads((root / 'data/site-contact.json').read_text(encoding='utf-8'))
    if not data.get('contacts'):
        raise ValueError('A confirmed public blog contact is required before adding the contact page.')
    for contact in data['contacts']:
        kind = contact['type']
        if kind == 'email':
            if not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', contact['value']):
                raise ValueError('Invalid public email address')
        elif kind == 'telegram':
            url = urlsplit(contact['url'])
            if url.scheme != 'https' or url.hostname != 't.me' or url.username or url.password:
                raise ValueError('Expected a confirmed HTTPS Telegram contact URL')
        else:
            raise ValueError('Unsupported contact type')
    return data


def header(current):
    routes = [('index.html', '首页', 'home'), ('brands.html', '品牌介绍', 'brands'),
              ('topics.html', '博客专题', 'topics'), ('blog.html', '文章目录', 'blog'),
              ('faq.html', 'FAQ专题', 'faq'), ('about.html', '关于本站', 'about')]
    links = ''.join('<a href="' + url + '"' + (' aria-current="page"' if current == key else '') + '>' + label + '</a>' for url, label, key in routes)
    return '<header class="header site-header" id="top"><a class="logo" href="index.html" aria-label="叮当观察首页"><span class="topic-logo" aria-hidden="true">叮</span><span>叮当观察<small>JCVPN.BLOG</small></span></a><nav class="site-primary-nav" id="site-primary-nav" aria-label="主导航">' + links + '</nav><a class="contact-nav-link" href="contact.html"' + (' aria-current="page"' if current == 'contact' else '') + '>联系我们 <span aria-hidden="true">↗</span></a><button class="site-menu" type="button" aria-expanded="false" aria-controls="site-primary-nav" aria-label="展开或收起导航菜单">菜单 <span aria-hidden="true">☰</span></button></header>'


def footer():
    groups = [
        ('探索内容', [('topics.html', '博客专题'), ('blog.html', '全部文章'), ('faq.html', '常见问题 FAQ'), ('topic-basics.html', 'VPN 入门指南')]),
        ('品牌与记录', [('brands.html', '全部品牌介绍'), ('brand-yinxingren.html', '隐形人机场'), ('brand-yinxingren.html#invisible-plans', '套餐与流量选择'), ('brand-yinxingren.html#peak-latency', '晚高峰延迟记录')]),
        ('认识本站', [('about.html', '关于叮当观察'), ('contact.html', '联系我们'), ('about.html#editorial-principles', '内容来源与编辑原则'), ('article-promotion-disclosure.html', '推广关系怎么看')])
    ]
    columns = ''.join('<nav class="footer-column" aria-label="' + title + '"><h3>' + title + '</h3><ul>' + ''.join('<li><a href="' + url + '">' + label + '</a></li>' for url, label in links) + '</ul></nav>' for title, links in groups)
    year = datetime.now(timezone(timedelta(hours=8))).year
    return f'''<footer class="site-footer" aria-label="网站页脚"><div class="footer-invite"><div><span class="footer-invite-label">KEEP THE CONVERSATION GOING</span><h2>还有没找到的答案？</h2><p>先查常见问题，也欢迎把内容疑问与纠错建议告诉我们。</p></div><div class="footer-actions"><a class="footer-faq-button" href="faq.html">查找常见问题 <span aria-hidden="true">→</span></a><a class="footer-contact-button" href="contact.html">联系我们 <span aria-hidden="true">↗</span></a></div></div><div class="footer-grid"><div class="footer-identity"><a class="logo" href="index.html"><span class="topic-logo" aria-hidden="true">叮</span><span>叮当观察</span></a><p>从 VPN 与机场VPN 的基础概念，到套餐、客户端和连接排查，把复杂的问题讲清楚。</p><span class="footer-mini-label">连接知识 · 品牌资料 · 使用指南</span></div>{columns}</div><div class="footer-bottom"><span>© {year} 叮当观察 · jcvpn.blog<br>资料会随产品与服务变化持续修订。</span><a href="#top">返回顶部 ↑</a></div></footer>'''


def shell(title, description, content):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + escape(title) + '｜叮当观察</title><meta name="description" content="' + escape(description, quote=True) + '"><link rel="stylesheet" href="assets/site-base.css"><link rel="stylesheet" href="assets/doraemon-theme.css"><link rel="stylesheet" href="assets/topics.css"><link rel="stylesheet" href="assets/site-chrome.css"><script src="assets/site-chrome.js" defer></script></head><body><div class="shell">' + header('') + '<main class="site-info-main">' + content + '</main>' + footer() + '</div></body></html>'


def about_page():
    intro = '''<section class="info-hero"><span class="info-kicker">ABOUT DINGDANG OBSERVATION</span><h1>认识叮当观察</h1><p>一份关于连接的好奇心。从读懂 VPN 与机场VPN，到看清套餐、客户端与实际记录，帮助你找到判断问题的具体依据。</p></section><nav class="info-breadcrumb" aria-label="当前位置"><a href="index.html">首页</a><span aria-hidden="true">/</span><span>关于本站</span></nav>'''
    cards = '''<div class="info-grid"><article class="info-card"><span class="info-card-index">01 / UNDERSTAND</span><h2>先弄清原理</h2><p>分清服务、客户端与连接概念，理解一个“已连接”图标可以说明什么。</p><a href="topic-basics.html">从入门专题开始 →</a></article><article class="info-card"><span class="info-card-index">02 / COMPARE</span><h2>再核对选择</h2><p>把套餐价格、流量规则、使用需求放在一起看，读懂条件再做选择。</p><a href="topic-plans.html">查看套餐与规则专题 →</a></article><article class="info-card"><span class="info-card-index">03 / TROUBLESHOOT</span><h2>把问题说清楚</h2><p>按设备、网络和错误现象整理排查路径，让每一步都能说明一个问题。</p><a href="topic-diagnostics.html">进入连接排查专题 →</a></article></div>'''
    principles = '''<section class="info-section" id="editorial-principles"><h2>内容从哪里来，如何整理</h2><ul><li>概念与技术说明参考相应文档；品牌套餐、规则与客户端信息注明其资料来源。</li><li>第三方使用反馈、品牌说明与本站整理分开呈现。延迟记录只说明对应条件下的数值，不推导下载速度或长期可用率。</li><li>部分正文由 AI 辅助撰写与整理。产品价格、客户端行为与服务规则会变化，使用前应核对当前说明。</li><li>品牌介绍包含推广入口。本站主推展示不作为独立测速排名，引用资料也不等于为所有服务表现背书。</li></ul><p><a href="article-evidence-levels.html">了解不同资料来源能支持哪些判断 →</a></p></section><section class="info-section"><h2>一起把资料补得更准确</h2><p>如果你发现链接失效、价格或规则变化，或某条说明不够清楚，欢迎附上对应页面与具体问题联系站方。真实的补充材料，比一句笼统的“好用”更有帮助。</p><p><a href="contact.html">联系我们 →</a>　<a href="faq.html">先查看常见问题 →</a></p></section>'''
    return shell('关于本站', '认识叮当观察的内容方向、资料来源、编辑原则与联系入口。', intro + cards + principles)


def contact_page(data):
    methods = []
    for item in data['contacts']:
        value = item['value']
        if item['type'] == 'email':
            title, icon, description, action = '联系邮箱', '@', '适合内容纠错、资料补充与合作咨询。', '打开邮件应用'
            url = 'mailto:' + quote(value, safe='@.+-_') + '?subject=' + quote('叮当观察｜网站咨询')
            extra = ''
        else:
            title, icon, description, action = 'Telegram 联系', '↗', '通过以下账号或入口联系博客站方。', '前往 Telegram'
            url = item['url']
            extra = ' target="_blank" rel="noopener noreferrer"'
        methods.append('<article class="contact-method"><span class="contact-method-icon" aria-hidden="true">' + icon + '</span><h2>' + title + '</h2><p>' + description + '</p><a class="contact-address" href="' + escape(url, quote=True) + '"' + extra + '>' + escape(value) + '</a><div class="contact-buttons"><a class="contact-action" href="' + escape(url, quote=True) + '"' + extra + '>' + action + ' <span aria-hidden="true">↗</span></a><button class="copy-contact" type="button" data-copy-contact="' + escape(value, quote=True) + '">复制联系方式</button></div><p class="contact-feedback" role="status" aria-live="polite"></p></article>')
    intro = '''<section class="info-hero"><span class="info-kicker">CONTACT THE BLOG</span><h1>联系我们</h1><p>关于内容、链接、资料或合作，把具体问题告诉我们。你提供的页面地址与说明，能帮助站方更快理解需要核对的内容。</p></section><nav class="info-breadcrumb" aria-label="当前位置"><a href="index.html">首页</a><span aria-hidden="true">/</span><span>联系我们</span></nav>'''
    body = '<div class="contact-grid' + (' single-contact' if len(methods) == 1 else '') + '">' + ''.join(methods) + '</div>'
    body += '''<section class="info-section"><h2>哪些事情可以联系站方？</h2><div class="contact-purpose-grid"><article><h3>内容纠错</h3><p>请附页面地址、需要修改的位置，以及你发现的问题或参考来源。</p></article><article><h3>资料补充</h3><p>欢迎提供品牌当前资料或实际使用记录，说明来源、日期及适用范围。</p></article><article><h3>合作咨询</h3><p>请说明品牌名称、合作内容与可公开核对的信息，便于站方了解需求。</p></article></div><p class="contact-note">账号登录、订单、退款及节点故障，请优先通过所购品牌后台的客服入口处理。博客联系方式用于站点沟通；请勿发送密码、私有订阅链接或支付凭据。</p></section><section class="info-section"><h2>发送前，可以先找找答案</h2><p><a href="faq.html">查找常见问题 →</a>　<a href="topic-diagnostics.html">查看连接排查专题 →</a>　<a href="about.html#editorial-principles">了解资料与编辑原则 →</a></p></section>'''
    return shell('联系我们', '叮当观察的公开联系入口，用于内容纠错、资料补充与合作咨询。', intro + body)


def apply_site_chrome(root):
    root = Path(root)
    data = read_contact(root)
    write_changed(root / 'about.html', about_page())
    write_changed(root / 'contact.html', contact_page(data))
    write_changed(root / '404.html', shell('页面未找到', '这个页面不存在，可以返回首页、浏览专题或联系站方。', '<section class="info-hero"><span class="info-kicker">404 / PAGE NOT FOUND</span><h1>这页暂时找不到了</h1><p>链接可能已经变化，或地址输入有误。你可以返回首页，从专题重新查找内容；如果是站内链接的问题，也欢迎告诉站方。</p><div class="contact-buttons"><a class="contact-action" href="index.html">返回首页 →</a><a class="copy-contact" href="topics.html">浏览博客专题</a><a class="copy-contact" href="contact.html">反馈失效链接</a></div></section>'))
    for page in root.glob('*.html'):
        if page.name in ('01-首页框架.html', '404.html'):
            continue
        name = page.name
        if name == 'index.html': current = 'home'
        elif name.startswith('brand'): current = 'brands'
        elif name == 'blog.html' or name.startswith('article-'): current = 'blog'
        elif name == 'faq.html': current = 'faq'
        elif name.startswith('topic'): current = 'topics'
        else: current = page.stem
        text = page.read_text(encoding='utf-8')
        text = re.sub(r'<header\b.*?</header>', lambda match: header(current), text, count=1, flags=re.S)
        text = re.sub(r'<footer\b.*?</footer>', lambda match: footer(), text, count=1, flags=re.S)
        # Remove only the previous homepage menu handler, keeping content filters.
        text = re.sub(r'<script>const menu=document\.querySelector\(\x27\.menu\x27\).*?</script>', '', text, flags=re.S)
        text = text.replace('<link rel="stylesheet" href="assets/site-chrome.css">', '')
        text = text.replace('<script src="assets/site-chrome.js" defer></script>', '')
        text = text.replace('</head>', '<link rel="stylesheet" href="assets/site-chrome.css"><script src="assets/site-chrome.js" defer></script></head>', 1)
        write_changed(page, text)


if __name__ == '__main__':
    apply_site_chrome(Path(__file__).resolve().parents[1])
