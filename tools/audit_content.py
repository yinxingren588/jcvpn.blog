"""Validate content coverage, distinct bodies, independent pages and metadata invariants."""
from collections import Counter
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.ids=Counter(); self.metas={}; self.feed(text)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get('id'):self.ids[d['id']]+=1
        if tag=='meta' and d.get('name'):self.metas.setdefault(d['name'],[]).append(d.get('content',''))

def audit():
    data=json.loads((ROOT/'data/library.json').read_text(encoding='utf-8'))
    seo=json.loads((ROOT/'data/seo-metadata.json').read_text(encoding='utf-8'))['pages']
    articles=data['articles']; faqs=data['faqs']; new=[a for a in articles if a.get('origin')=='search-expansion']
    independent=[f for f in faqs if f.get('file')]
    assert (len(articles),len(faqs),len(data['topics']),len(new),len(independent))==(84,248,12,24,48)
    assert len({a['slug'] for a in articles})==84
    assert len({f['id'] for f in faqs})==248
    assert len({f['question'] for f in faqs})==248
    assert all((ROOT/a['file']).is_file() for a in articles)
    assert all((ROOT/f['file']).is_file() for f in independent)
    bodies={a['slug']:''.join(p for _,p in a['sections']) for a in articles}
    assert len(set(bodies.values()))==84
    assert min(len(bodies[a['slug']]) for a in new)>450
    revised=[a for a in articles if a.get('reviewed_on')]
    if (ROOT/'data/editorial-revisions.json').exists():
        assert len(revised)==60
        assert len({a['quick_answer'] for a in revised})==60
        assert len({json.dumps(a['table'],ensure_ascii=False) for a in revised})==60
        faqmap={f['id']:f for f in faqs}
        for a in revised:
            assert len(bodies[a['slug']])>=550,a['slug']
            assert len(a['sections'])==6 and len(a['table'][1])>=2,a['slug']
            text=(ROOT/a['file']).read_text(encoding='utf-8')
            assert 'class="article-quick-answer"' in text,a['slug']
            assert '本次修订说明' in text,a['slug']
            structured=json.loads(re.search(r'<script type="application/ld\+json" id="site-seo-structured-data">(.*?)</script>',text,re.S).group(1))
            assert structured['datePublished']=='2026-10-28' and structured['dateModified']==a['reviewed_on'],a['slug']
            assert all('id="section-'+str(i)+'"' in text for i in range(1,7)),a['slug']
            assert a['faqs']==[[faqmap[fid]['question'],faqmap[fid]['answer']] for fid in a['faq_ids']],a['slug']
    similarities=[]
    for i,a in enumerate(new):
        for b in new[i+1:]:
            ratio=SequenceMatcher(None,bodies[a['slug']],bodies[b['slug']],autojunk=False).ratio()
            similarities.append((round(ratio,3),a['slug'],b['slug']))
            assert ratio<.65, ('Near duplicate articles',a['slug'],b['slug'])
    for path in ROOT.glob('*.html'):
        if path.name=='01-首页框架.html':continue
        text=path.read_text(encoding='utf-8'); page=Page(text); m=seo[path.name]
        assert len(page.metas.get('description',[]))==1,path.name
        assert len(page.metas.get('keywords',[]))==1,path.name
        assert page.metas['description'][0]==m['description'],path.name
        assert '<title>'+m['title'].replace('&','&amp;')+'</title>' in text,path.name
        assert 20<=len(m['description'])<=145,path.name
        assert page.ids['home-directory-root']==1,path.name
        assert not [key for key,n in page.ids.items() if n>1],path.name
        assert 'class="site-directory-feature" href="brand-yinxingren.html"' in text,path.name
        for script in re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',text,re.S):json.loads(script)
    for path in (ROOT/'assets').glob('*.js'):
        result=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
        assert result.returncode==0,(path.name,result.stderr)
    assert len({m['title'] for m in seo.values()})==len(seo)
    assert len({m['description'] for m in seo.values()})==len(seo)
    targets=['机场推荐','梯子推荐','vpn','vpn推荐','节点推荐','机场节点','机场测评','性价比机场','稳定机场','clash机场','便宜机场','便宜机场推荐']
    titles=' '.join(a['title'] for a in new).casefold()
    assert all(k.casefold() in titles for k in targets)
    report=dict(articles=84,new_articles=24,revised_original_articles=len(revised),faqs=248,new_independent_faqs=48,topics=12,seo_pages=len(seo),
                new_article_shortest_prose=min(len(bodies[a['slug']]) for a in new),highest_new_pair_similarity=sorted(similarities,reverse=True)[:3],errors=[])
    print(json.dumps(report,ensure_ascii=True))
    return report

if __name__=='__main__':audit()
