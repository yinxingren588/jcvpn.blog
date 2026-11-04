"""Declare the site's Doraemon tab icon with content-based cache versions."""
from hashlib import sha256
from pathlib import Path
import re

from site_chrome import write_changed


def favicon_links(root):
    root = Path(root)
    ico = root / 'favicon.ico'
    png = root / 'assets/doraemon-favicon-32.png'
    assert ico.is_file() and png.is_file(), 'Missing favicon exports'
    ico_version = sha256(ico.read_bytes()).hexdigest()[:12]
    png_version = sha256(png.read_bytes()).hexdigest()[:12]
    return ('<link rel="icon" href="favicon.ico?v=' + ico_version + '" sizes="any">'
            '<link rel="icon" type="image/png" href="assets/doraemon-favicon-32.png?v='
            + png_version + '" sizes="32x32">')


def apply_site_favicon(root):
    root = Path(root)
    links = favicon_links(root)
    pattern = r'''<link\b(?=[^>]*\brel=["'](?:icon|shortcut\s+icon)["'])[^>]*>'''
    for path in root.glob('*.html'):
        text = path.read_text(encoding='utf-8')
        text = re.sub(pattern, '', text, flags=re.I)
        assert '</head>' in text, path.name
        text = text.replace('</head>', links + '</head>', 1)
        write_changed(path, text)
