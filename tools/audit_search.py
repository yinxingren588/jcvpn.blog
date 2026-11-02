"""Check search-intent routes, incomplete-brand indexing and release artifacts."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from html import unescape
import json,re

ROOT=Path(__file__).resolve().parents[1]
TARGETS={
    '机场推荐':'recommendations','梯子推荐':'recommendations','VPN':'vpn-choice','VPN推荐':'vpn-choice',
    '节点推荐':'nodes-guide','机场节点':'nodes-guide','机场测评':'reviews-guide','稳定机场':'reviews-guide',
    '性价比机场':'budget-guide','Clash机场':'clash-guide','便宜机场':'budget-guide','便宜机场推荐':'budget-guide'}

class Links(HTMLParser):
    def __init__(self,text):super().__init__();self.links=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a' and d.get('href'):self.links.append(d['href'])

def main():
    pages=json.loads((ROOT/'data/publication-manifest.json').read_text(encoding='utf-8'))['pages']
    intake=json.loads((ROOT/'data/new-brands.json').read_text(encoding='utf-8'))['brands']
    seo=json.loads((ROOT/'data/seo-metadata.json').read_text(encoding='utf-8'))['pages']
    home=(ROOT/'index.html').read_text(encoding='utf-8')
    coverage=[]
    for keyword,topic in TARGETS.items():
        name='topic-'+topic+'.html'; html=(ROOT/name).read_text(encoding='utf-8')
        main=re.search(r'<main\b[^>]*>(.*?)</main>',html,re.S).group(1)
        plain=unescape(re.sub('<[^>]+>',' ',main))
        assert keyword.casefold() in plain.casefold(),(keyword,'missing primary content')
        assert keyword.casefold() in seo[name]['title'].casefold(),(keyword,'missing topic title')
        assert 'href="'+name+'"' in home,(keyword,'missing homepage route')
        coverage.append({'keyword':keyword,'primary_page':'https://jcvpn.blog/'+Path(name).stem,'status':'title_and_visible_topic_content_with_homepage_link'})
    names={info['file'] for info in pages.values()}; reached=set(); queue=['index.html']
    while queue:
        name=queue.pop()
        if name in reached:continue
        reached.add(name)
        for link in Links((ROOT/name).read_text(encoding='utf-8')).links:
            parsed=urlsplit(link)
            if parsed.scheme or parsed.netloc:continue
            target=unquote(parsed.path).lstrip('/') or name
            if target in ('.','./'):target='index.html'
            if target in names and target not in reached:queue.append(target)
    assert names<=reached,sorted(names-reached)
    for b in intake:
        html=(ROOT/b['profile_path']).read_text(encoding='utf-8')
        assert 'name="robots" content="noindex,follow"' in html,b['name']
        assert b['profile_path'] not in names,b['name']
        assert unescape(b['url']) in unescape(html),b['name']
        assert 'rel="sponsored noopener noreferrer"' in html,b['name']
        assert 'href="'+b['profile_path']+'"' in home,b['name']
    assert len(json.loads((ROOT/'data/brands.json').read_text(encoding='utf-8'))['brands'])==8
    assert '/data/*\n  X-Robots-Tag: noindex' in (ROOT/'_headers').read_text(encoding='utf-8')
    assert 'class="search-route-card"' in home and home.count('class="search-route-card"')==6
    for source in ['breezenet-logo-hd','feimaoyun-logo-hd','lingdongyun-logo-hd']:
        assert source+'.png' not in home,source
        assert source+'.webp?v=' not in home,source
    report={'keywords':coverage,'indexable_pages_reachable':len(names),'brand_entries':8,'completed_profiles':5,'incomplete_profiles_noindex':3,'notes':'覆盖检查不代表Bing已收录、排名或权重。'}
    (ROOT/'data/search-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'target_keywords':len(coverage),'reachable_indexable_pages':len(names),'brand_entries':8,'incomplete_noindex':3,'errors':[]}))
if __name__=='__main__':main()
