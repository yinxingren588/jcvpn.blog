"""Validate the publishable static site, including local references and SEO files."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

from prepare_site import ROOT, ALIAS, NAMESPACE, fingerprint, page_url, read_json


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set(); self.refs = []; self.canonicals = []; self.robots = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get('id'):
            self.ids.add(data['id'])
        if tag == 'a' and data.get('href'):
            self.refs.append(data['href'])
        if tag in ('script', 'img') and data.get('src'):
            self.refs.append(data['src'])
        if tag == 'link' and data.get('href'):
            if data.get('rel') == 'canonical': self.canonicals.append(data['href'])
            else: self.refs.append(data['href'])
        if tag == 'meta' and data.get('name', '').lower() in ('robots', 'bingbot'):
            self.robots.append(data.get('content', ''))


def validate():
    config = read_json(ROOT / 'site.config.json')
    manifest = read_json(ROOT / 'data/publication-manifest.json')
    documents = {p.name: Document(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')}
    errors = []
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    urls = [node.text for node in sitemap.findall('.//{' + NAMESPACE + '}loc')]
    if len(urls) != len(set(urls)) or set(urls) != set(manifest['pages']): errors.append('Sitemap URL set mismatch')
    if page_url(ALIAS, config['origin']) in urls: errors.append('Duplicate home in sitemap')
    if page_url('404.html', config['origin']) in urls: errors.append('404 page in sitemap')
    for name, doc in documents.items():
        content = (ROOT / name).read_text(encoding='utf-8')
        expected = config['origin'] + '/' if name == ALIAS else page_url(name, config['origin'])
        if doc.canonicals != [expected]: errors.append(name + ': canonical mismatch')
        expected_robots = 'noindex,follow' if name in (ALIAS, '404.html') else 'index,follow'
        if doc.robots != [expected_robots]: errors.append(name + ': indexing rule mismatch')
        if len(re.findall(r'<h1(?:>|\s)', content)) != 1: errors.append(name + ': H1 count')
        for ref in doc.refs:
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc: continue
            path = unquote(parsed.path) or name
            if path in ('./', '/'): path = 'index.html'
            target = ROOT / path
            if not target.is_file(): errors.append(name + ': missing ' + ref)
            elif parsed.fragment and path in documents and unquote(parsed.fragment) not in documents[path].ids:
                errors.append(name + ': missing anchor ' + ref)
    for url, info in manifest['pages'].items():
        if fingerprint((ROOT / info['file']).read_text(encoding='utf-8')) != info['sha256']: errors.append('Stale hash: ' + url)
    key = config['indexnow_key']
    if (ROOT / (key + '.txt')).read_text(encoding='utf-8') != key: errors.append('IndexNow key file mismatch')
    if 'Sitemap: ' + config['origin'] + '/sitemap.xml' not in (ROOT / 'robots.txt').read_text(encoding='utf-8'): errors.append('robots sitemap missing')
    for css in (ROOT / 'assets').glob('*.css'):
        for ref in re.findall(r'url\([\"\']?([^\)\"\']+)', css.read_text(encoding='utf-8')):
            if not urlsplit(ref).scheme and not (css.parent / ref).is_file(): errors.append(css.name + ': missing CSS asset ' + ref)
    report = {'html_pages': len(documents), 'canonical_urls': len(urls), 'errors': errors}
    print(json.dumps(report, ensure_ascii=True))
    if errors: raise SystemExit(1)
    return report


if __name__ == '__main__':
    validate()
