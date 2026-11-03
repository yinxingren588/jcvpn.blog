"""Check topic evidence, legacy anchors and comparisons against retained sources."""
from collections import Counter
from decimal import Decimal
from html import unescape
from pathlib import Path
from statistics import median
import json
import re

from content_library import BRANDS, SOURCES, tables
from topic_hubs import load_hubs, hub_tables

ROOT=Path(__file__).resolve().parents[1]


def audit():
    hubs=load_hubs(ROOT)
    library=json.loads((ROOT/'data/library.json').read_text(encoding='utf-8'))
    seo=json.loads((ROOT/'data/seo-metadata.json').read_text(encoding='utf-8'))['pages']
    topic_map={t['id']:t for t in library['topics']}
    source_tables=tables(ROOT)
    rendered_tables=hub_tables(ROOT,source_tables,BRANDS)
    total_sections=0
    for key,hub in hubs.items():
        assert key==hub['id']
        assert len(hub['sections'])>=5
        assert all(source in {**library['sources'],**SOURCES} for source in hub['sources'])
        text=(ROOT/('topic-'+key+'.html')).read_text(encoding='utf-8')
        main=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.S)[1]
        ids=Counter(re.findall(r'\bid="([^"]+)"',text))
        assert all(count==1 for count in ids.values()),key
        # These anchors existed before the richer guide and remain valid bookmarks.
        for index,label in [(1,'按这个顺序阅读'),(2,'专题文章'),(3,'专题FAQ')]:
            assert '<h2 id="quick-section-'+str(index)+'">'+label+'</h2>' in main,key
        for section in hub['sections']:
            assert ids[section['id']]==1,(key,section['id'])
            assert 'href="#'+section['id']+'"' in main,(key,section['id'])
            if section.get('table_key'):
                assert section['table_key'] in rendered_tables
                assert section.get('caption'),(key,section['id'])
        for href in re.findall(r'\bhref="([^"]+)"',main):
            href=unescape(href)
            if href.startswith(('https://','mailto:')):continue
            file,_,fragment=href.partition('#')
            target=ROOT/file if file else ROOT/('topic-'+key+'.html')
            assert target.is_file(),(key,href)
            if fragment and target.suffix=='.html':
                target_ids=re.findall(r'\bid="([^"]+)"',target.read_text(encoding='utf-8'))
                assert fragment in target_ids,(key,href)
        for path in topic_map[key]['article_paths']:
            assert 'href="'+path+'"' in main,(key,path)
        assert len(topic_map[key]['article_paths'])==4
        assert len(topic_map[key]['faq'])==8
        assert seo['topic-'+key+'.html']['title'].startswith(hub['seo_title'])
        assert seo['topic-'+key+'.html']['description']==hub['seo_description']
        structured=json.loads(re.search(r'<script type="application/ld\+json" id="site-seo-structured-data">(.*?)</script>',text,re.S)[1])
        assert structured['@type']=='CollectionPage'
        total_sections+=len(hub['sections'])
    # Validate that failure entries were not turned into zeroes or silently omitted.
    verified_records=0
    for name in ('invisible','breezenet','feimaoyun','muguang','feiv','tiziyun','langwang'):
        data=json.loads((ROOT/'data'/(name+'-latency.json')).read_text(encoding='utf-8'))
        records=data['records']
        verified_records+=len(records)
        numeric=[r['latency_ms'] for r in records if r['latency_ms'] is not None]
        summary=data['summary']
        assert len(records)==summary['node_count']
        assert len(numeric)==summary['response_count']
        assert len(records)-len(numeric)==summary['timeout_count']
        assert (min(numeric),median(numeric),max(numeric))==(summary['min_ms'],summary['median_ms'],summary['max_ms'])
    # Cross-check annual and monthly arithmetic, including the three excluded annual offers.
    annual_expected=[('87.20','7.27'),('123.30','10.28'),('84.00','7.00'),('109.00','9.08'),('99.00','8.25')]
    monthly_expected=['19.20','22.50','22.50','20.00','16.00']
    for row,(annual,monthly) in zip(source_tables['annuals'][1],annual_expected):
        assert row[3]=='¥'+annual+'/年' and row[4]=='约¥'+monthly+'/月',row
    for row,amount in zip(source_tables['monthly'][1],monthly_expected):
        assert row[3]=='¥'+amount+'/月',row
    assert Decimal('199')*Decimal('.8')==Decimal('159.20')
    assert len(rendered_tables['hub-candidates'][1])==5
    assert rendered_tables['hub-latency'][1][-1][1]=='尚未提供'
    assert len(rendered_tables['hub-latency'][1])==8
    wave_latency=next(row for row in rendered_tables['hub-latency'][1] if row[0]=='浪网')
    assert wave_latency[3:]==['60','59 / 1','50 / 169 / 1028']
    assert '2026-11-03 12:00' in wave_latency[1] and '上海电信' in wave_latency[2]
    ai_rows=rendered_tables['hub-ai-records'][1]
    assert len(ai_rows)==8
    ladder_ai=next(row for row in ai_rows if row[0]=='梯子云')
    assert ladder_ai[1:6]==['2026-11-03','12:00','上海','电信','新加坡']
    wave_ai=next(row for row in ai_rows if row[0]=='浪网')
    assert wave_ai[1:6]==['2026-11-03','19:00','上海','电信','新加坡']
    report=dict(substantive_hubs=len(hubs),authored_sections=total_sections,legacy_anchors_preserved=9,
                verified_latency_records=verified_records,verified_ai_records=len(ai_rows),errors=[])
    print(json.dumps(report,ensure_ascii=True))
    return report


if __name__=='__main__':audit()
