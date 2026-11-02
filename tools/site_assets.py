"""Use smaller encodings of existing artwork without changing the site design."""
from pathlib import Path
from hashlib import sha256
from urllib.parse import urlsplit
import re

from site_chrome import write_changed


OPTIMIZED_ASSETS = {
    'doraemon-sky.png': 'doraemon-sky.webp',
    'breezenet-logo-hd.png': 'breezenet-logo-hd.webp',
    'feimaoyun-logo-hd.png': 'feimaoyun-logo-hd.webp',
    'lingdongyun-logo-hd.png': 'lingdongyun-logo-hd.webp',
}


def apply_site_assets(root):
    """Rewrite generated page/style/script URLs; retain all source PNG files.

    Only the known sidebar images are deferred. Above-the-fold brand artwork,
    background and other content images retain their original loading behavior.
    Running this pass repeatedly produces the same output.
    """
    root = Path(root)
    for source, target in OPTIMIZED_ASSETS.items():
        assert (root / 'assets' / source).is_file(), source
        assert (root / 'assets' / target).is_file(), target

    paths = list(root.glob('*.html'))
    for suffix in ('*.css', '*.js'):
        paths.extend((root / 'assets').glob(suffix))

    changed = 0
    for path in paths:
        original = path.read_text(encoding='utf-8')
        content = original
        for source, target in OPTIMIZED_ASSETS.items():
            content = content.replace(source, target)
            # Generated hero logos used a cache-busting hash while directory
            # logos did not. Keep one URL for each exact WebP resource so both
            # locations share a single browser request. Other query parameters
            # and other assets keep their original URLs.
            content = re.sub(
                r'(?<![\w.-])' + re.escape(target) +
                r'\?v=[0-9a-fA-F]+(?=["\'\s)<>#]|$)',
                target, content)
        if path.suffix == '.html':
            def defer_sidebar(match):
                def image_tag(image):
                    tag = image.group(0)
                    if not re.search(r'\bloading\s*=', tag, re.I):
                        tag = tag[:-1] + ' loading="lazy">'
                    return tag
                return re.sub(r'<img\b[^>]*>', image_tag, match.group(0), flags=re.I)
            content = re.sub(
                r'<aside\b[^>]*\bid=["\']home-directory-root["\'][^>]*>.*?</aside>',
                defer_sidebar, content, flags=re.S | re.I)
        if content != original:
            write_changed(path, content)
            changed += 1
    # Rendering may change a shared stylesheet without changing its filename.
    # Hash the final bytes after optimization, so returning visitors receive it.
    for path in root.glob('*.html'):
        original=path.read_text(encoding='utf-8')
        def version(match):
            attr,quote,url=match.groups()
            parsed=urlsplit(url)
            asset=root/parsed.path
            if parsed.scheme or not parsed.path.startswith('assets/') or asset.suffix not in ('.css','.js') or not asset.is_file():return match[0]
            return attr+'='+quote+parsed.path+'?v='+sha256(asset.read_bytes()).hexdigest()[:12]+quote
        content=re.sub(r'\b(href|src)=(["\'])([^"\']+)\2',version,original)
        seen=set()
        def unique_tag(match):
            tag=match[0]
            found=re.search(r'\b(?:href|src)=["\']([^"\']+)',tag)
            if not found:return tag
            parsed=urlsplit(found[1])
            if not parsed.path.startswith('assets/') or Path(parsed.path).suffix not in ('.css','.js'):return tag
            if parsed.path in seen:return ''
            seen.add(parsed.path)
            return tag
        content=re.sub(r'<link\b[^>]*>|<script\b[^>]*\bsrc=["\'][^"\']+["\'][^>]*>\s*</script>',unique_tag,content,flags=re.I)
        if content!=original:
            write_changed(path,content)
            changed+=1
    return changed
