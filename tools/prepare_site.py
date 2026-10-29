"""Prepare a static release without publishing or notifying search engines."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import zipfile
from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path
from urllib.parse import quote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.release' / 'manifest.json'
NAMESPACE = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ALIAS = '01-首页框架.html'
DOCS = ('03-可信内容与SEO规范.md', '04-首批品牌档案.md')


def write_changed(path: Path, value: str) -> None:
    if path.exists() and path.read_text(encoding='utf-8') == value:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8', newline='\n')


def read_json(path: Path, default=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def page_url(name: str, origin: str) -> str:
    # Cloudflare Pages redirects *.html to the extensionless URL.
    return origin + '/' if name == 'index.html' else origin + '/' + quote(name.removesuffix('.html'))


def fingerprint(content: str) -> str:
    return hashlib.sha256(content.replace('\r\n', '\n').encode('utf-8')).hexdigest()


def prepare() -> dict:
    if (ROOT / 'data/breezenet-plans.json').exists():
        from breeze_profile import build_breezenet_profile
        build_breezenet_profile(ROOT)
    if (ROOT / 'data/feimaoyun-profile.json').exists():
        from flycat_profile import build_flycat_profile
        build_flycat_profile(ROOT)
    if (ROOT / 'data/site-contact.json').exists():
        from site_chrome import apply_site_chrome
        apply_site_chrome(ROOT)
    config_path = ROOT / 'site.config.json'
    config = read_json(config_path)
    origin = config['origin'].rstrip('/')
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or parsed.netloc != 'jcvpn.blog' or parsed.path:
        raise ValueError('Expected the confirmed origin https://jcvpn.blog')
    if not config.get('indexnow_key'):
        config['indexnow_key'] = secrets.token_hex(16)
    key = config['indexnow_key']
    if not re.fullmatch(r'[a-f0-9]{32}', key):
        raise ValueError('Invalid IndexNow verification key')
    write_changed(config_path, json.dumps(config, ensure_ascii=False, indent=2) + '\n')
    write_changed(ROOT / (key + '.txt'), key)
    write_changed(ROOT / '.nojekyll', '')

    old = read_json(STATE, {'pages': {}})
    descriptions = read_json(ROOT / 'data/page-descriptions.json', {})
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    pages = {}
    for path in sorted(ROOT.glob('*.html')):
        if path.name == ALIAS:
            continue
        content = path.read_text(encoding='utf-8')
        if path.name in descriptions:
            description_tag = '<meta name="description" content="' + escape(descriptions[path.name], quote=True) + '">'
            content, count = re.subn(r'<meta\b(?=[^>]*\bname=[\"\']description[\"\'])[^>]*>', lambda match: description_tag, content, count=1, flags=re.I)
            if not count:
                content = content.replace('</head>', description_tag + '</head>', 1)
        # Remove preview indexing rules and stale canonical tags, then add one copy.
        content = re.sub(r'<meta\b(?=[^>]*\bname=[\"\'](?:robots|bingbot)[\"\'])[^>]*>', '', content, flags=re.I)
        content = re.sub(r'<link\b(?=[^>]*\brel=[\"\']canonical[\"\'])[^>]*>', '', content, flags=re.I)
        canonical = page_url(path.name, origin)
        robots_rule = 'noindex,follow' if path.name == '404.html' else 'index,follow'
        tags = '<meta name="robots" content="' + robots_rule + '"><link rel="canonical" href="' + escape(canonical, quote=True) + '">'
        content = re.sub(r'</head>', lambda match: tags + match.group(), content, count=1, flags=re.I)
        # Remove only the local-preview label, retaining source and authorship notes.
        content = content.replace('本地内容预览 · ', '').replace('本地预览 · ', '').replace(' · 本地预览', '')
        content = content.replace(' · 本地内容预览', '')
        write_changed(path, content)
        if path.name == '404.html':
            continue
        digest = fingerprint(content)
        previous = old.get('pages', {}).get(canonical, {})
        modified = previous['lastmod'] if previous.get('sha256') == digest else now
        pages[canonical] = {'file': path.name, 'sha256': digest, 'lastmod': modified}

    # Preserve the old bookmark as a small alias; it is not a second indexable home.
    alias = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>叮当观察</title><meta name="robots" content="noindex,follow"><link rel="canonical" href="' + origin + '/"><meta http-equiv="refresh" content="0;url=./"></head><body><h1>叮当观察</h1><p><a href="index.html">前往首页</a></p></body></html>\n'
    write_changed(ROOT / ALIAS, alias)
    robots = 'User-agent: *\nAllow: /\n\nSitemap: ' + origin + '/sitemap.xml\n'
    write_changed(ROOT / 'robots.txt', robots)
    ET.register_namespace('', NAMESPACE)
    urlset = ET.Element('{' + NAMESPACE + '}urlset')
    for url, info in pages.items():
        item = ET.SubElement(urlset, '{' + NAMESPACE + '}url')
        ET.SubElement(item, '{' + NAMESPACE + '}loc').text = url
        ET.SubElement(item, '{' + NAMESPACE + '}lastmod').text = info['lastmod']
    ET.indent(urlset, space='  ')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(urlset, encoding='unicode') + '\n'
    write_changed(ROOT / 'sitemap.xml', xml)
    manifest = {'origin': origin, 'pages': pages}
    write_changed(STATE, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    # Keep timestamps across fresh clones and file-copy uploads; file mtimes alone
    # would incorrectly claim every page changed on every build.
    write_changed(ROOT / 'data' / 'publication-manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


def archive(path: Path, key: str) -> int:
    files = list(ROOT.glob('*.html'))
    files += [ROOT / name for name in (*DOCS, 'robots.txt', 'sitemap.xml', '.nojekyll', key + '.txt')]
    for directory in ('assets', 'data'):
        files.extend(p for p in (ROOT / directory).rglob('*') if p.is_file())
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as package:
        for file in sorted(set(files)):
            if file.is_file():
                package.write(file, file.relative_to(ROOT).as_posix())
    return len(set(files))


def main():
    parser = argparse.ArgumentParser(description='Prepare canonical URLs, sitemap, robots and IndexNow verification. No network requests.')
    parser.add_argument('--zip', type=Path, help='Optional public-files-only upload archive')
    args = parser.parse_args()
    # An ignored working manifest may be absent after cloning the repository.
    if not STATE.exists() and (ROOT / 'data/publication-manifest.json').exists():
        write_changed(STATE, (ROOT / 'data/publication-manifest.json').read_text(encoding='utf-8'))
    manifest = prepare()
    print('Prepared', len(manifest['pages']), 'canonical pages. No URLs submitted.')
    if args.zip:
        count = archive(args.zip.resolve(), read_json(ROOT / 'site.config.json')['indexnow_key'])
        print('Packaged', count, 'public files:', args.zip.resolve())


if __name__ == '__main__':
    main()
