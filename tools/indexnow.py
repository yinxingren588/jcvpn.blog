"""Build a pending URL batch; --submit is explicitly required to send it."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from prepare_site import ROOT, read_json, write_changed, fingerprint

NOTIFIED = ROOT / '.indexnow-state.json'


def pending(config, manifest):
    previous = read_json(NOTIFIED, {'hashes': {}})['hashes']
    current = {url: info['sha256'] for url, info in manifest['pages'].items()}
    changed = [url for url, digest in current.items() if previous.get(url) != digest]
    # Old .html URLs remain working redirects, not deleted resources.
    def normalized(url):
        if url.endswith('/index.html'): return url[:-10]
        return url[:-5] if url.endswith('.html') else url
    deleted = [url for url in previous if url not in current and normalized(url) not in current]
    payload = {'host': urlsplit(config['origin']).netloc,
               'key': config['indexnow_key'],
               'keyLocation': config['origin'].rstrip('/') + '/' + config['indexnow_key'] + '.txt',
               'urlList': sorted(changed + deleted)}
    return payload, current, set(deleted)


def fetch(url):
    request = Request(url, headers={'User-Agent': 'DingdangPublicationCheck/1.0'})
    with urlopen(request, timeout=25) as response:
        return response.status, response.geturl(), response.read().decode('utf-8-sig')


def verify_live(payload, manifest, deleted, check_all=True):
    status, final, text = fetch(payload['keyLocation'])
    if status != 200 or final != payload['keyLocation'] or text.strip() != payload['key']:
        raise RuntimeError('The live IndexNow key file does not match. Upload the release to the confirmed domain root first.')
    urls = payload['urlList'] if check_all else []
    def verify_page(url):
        if url in deleted:
            try:
                fetch(url)
            except HTTPError as error:
                if error.code in (404, 410):
                    return
                raise
            raise RuntimeError('Removed URL is still online: ' + url)
        status, final, text = fetch(url)
        if status != 200 or final != url:
            raise RuntimeError('Unexpected HTTP response or redirect: ' + url)
        if fingerprint(text) != manifest['pages'][url]['sha256']:
            raise RuntimeError('The live page differs from this release: ' + url + '. Upload the changed page and retry.')
    with ThreadPoolExecutor(max_workers=6) as executor:
        list(executor.map(verify_page, urls))
    for filename in ('robots.txt', 'sitemap.xml'):
        url = manifest['origin'] + '/' + filename
        status, final, text = fetch(url)
        if status != 200 or final != url or text.replace('\r\n', '\n') != (ROOT / filename).read_text(encoding='utf-8').replace('\r\n', '\n'):
            raise RuntimeError('The live ' + filename + ' differs from this release.')


def main():
    parser = argparse.ArgumentParser(description='Dry run by default. --submit verifies the live release before sending IndexNow.')
    parser.add_argument('--submit', action='store_true')
    parser.add_argument('--check-live', action='store_true', help='Verify deployment without notifying search engines')
    parser.add_argument('--output', type=Path, default=ROOT / '.release/indexnow-payload.json')
    args = parser.parse_args()
    config = read_json(ROOT / 'site.config.json')
    manifest = read_json(ROOT / 'data/publication-manifest.json')
    if not manifest or not config.get('indexnow_key'):
        raise RuntimeError('Run tools/prepare_site.py first.')
    for url, info in manifest['pages'].items():
        if fingerprint((ROOT / info['file']).read_text(encoding='utf-8')) != info['sha256']:
            raise RuntimeError('Local page changed since preparation. Run tools/prepare_site.py first: ' + info['file'])
    payload, current, deleted = pending(config, manifest)
    write_changed(args.output, json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    print('Pending URLs:', len(payload['urlList']), '(new/updated:', len(payload['urlList']) - len(deleted), ', removed:', len(deleted), ')')
    if not args.submit and not args.check_live:
        print('Dry run only. No network requests. Payload saved to', args.output)
        return
    verify_live(payload, manifest, deleted)
    print('Live key file, changed pages, sitemap and robots match this release.')
    if not args.submit:
        print('Verification only. No URLs submitted.')
        return
    if not payload['urlList']:
        print('Nothing changed since the last successful submission.')
        return
    if len(payload['urlList']) > 10000:
        raise RuntimeError('Batch exceeds 10,000 URLs. Split the batch before sending.')
    body = json.dumps(payload).encode('utf-8')
    request = Request(config['indexnow_endpoint'], data=body,
                      headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'DingdangIndexNow/1.0'}, method='POST')
    with urlopen(request, timeout=30) as response:
        code = response.status
    if code == 200:
        write_changed(NOTIFIED, json.dumps({'submitted_at': datetime.now(timezone.utc).isoformat(), 'hashes': current}, indent=2) + '\n')
        print('HTTP 200: IndexNow received the URLs. This does not mean the pages are indexed.')
    elif code == 202:
        print('HTTP 202: received; key validation pending. Pending URLs retained for a later retry.')
    else:
        raise RuntimeError('Unexpected IndexNow response: ' + str(code))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        print('Stopped:', error, file=sys.stderr)
        sys.exit(1)
