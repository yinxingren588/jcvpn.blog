"""Render substantial topic guides from editorial copy and existing source records."""
from html import escape as e
from pathlib import Path
import json


HUB_FILES = {
    'recommendations': 'recommendations-hub.json',
    'budget-guide': 'budget-hub.json',
    'reviews-guide': 'reviews-hub.json',
}


def load_hubs(root):
    return {key: json.loads((Path(root)/'data'/name).read_text(encoding='utf-8'))
            for key, name in HUB_FILES.items()}


def hub_tables(root, source_tables, brands):
    candidates=[]
    lines=['IEPL', 'IPLC', 'IPLC', 'IPLC', 'BGP；穿云另列IPLC']
    for i, (annual, monthly) in enumerate(zip(source_tables['annuals'][1], source_tables['monthly'][1])):
        candidates.append([brands[i][0], lines[i], monthly[3]+' · '+monthly[4],
                           annual[3]+' · '+annual[5]+' / '+(
                               '每30天' if i in (0,3,4) else '按月'),
                           ['yxr888八折全部9款','weifeng90九折全部6款',
                            'flycat888九折，学生版除外','暂无已确认优惠码',
                            'wsj888八折，穿云与私人定制除外'][i]])
    latency=[]
    for i, name in enumerate(['invisible','breezenet','feimaoyun','muguang']):
        d=json.loads((Path(root)/'data'/(name+'-latency.json')).read_text(encoding='utf-8'))
        s=d['summary']
        latency.append([brands[i][0], d['measured_date']+' '+d['measured_time'],
                        d['location']+d['isp']+' · '+d['client'], str(s['node_count']),
                        str(s['response_count'])+' / '+str(s['timeout_count']),
                        str(s['min_ms'])+' / '+format(s['median_ms'],'g')+' / '+str(s['max_ms'])])
    latency.append([brands[4][0],'尚未提供','尚未提供','—','—','—'])
    return {**source_tables,
            'hub-candidates': (['品牌','线路资料','入门月付应付与额度','轻量年付应付与每期额度','优惠范围'], candidates),
            'hub-latency': (['品牌','采样时刻（北京时间）','环境与客户端','记录数','有数值 / 超时','最小 / 中位 / 最大（ms）'], latency)}


def render_hub(hub, tables, render_table, source_links):
    paragraphs=lambda items: ''.join('<p>'+e(text)+'</p>' for text in items)
    out='<div class="topic-hub" data-topic-hub="'+e(hub['id'],quote=True)+'">'
    out+='<section class="section topic-hub-summary" aria-label="专题阅读要点"><span class="overline">先看选择要点</span>'
    out+=paragraphs([hub['lead']])+'<p class="topic-hub-scope">'+e(hub['scope'])+'</p>'
    out+='<p class="topic-hub-date">内容整理 <time datetime="'+hub['reviewed_on']+'">'+hub['reviewed_on']+'</time> · 叮当观察</p>'
    out+='<nav class="topic-hub-jumps" aria-label="专题重点内容">'+''.join(
        '<a href="#'+e(s['id'],quote=True)+'">'+e(s['title'])+'</a>' for s in hub['sections'])+'</nav></section>'
    for s in hub['sections']:
        out+='<section class="section topic-hub-section"><h2 id="'+e(s['id'],quote=True)+'">'+e(s['title'])+'</h2>'
        out+=paragraphs(s.get('paragraphs',[]))
        if s.get('table_key'):
            out+=render_table(tables[s['table_key']],True,s.get('caption'))
        if s.get('cards'):
            out+='<div class="topic-choice-grid">'+''.join(
                '<article class="topic-choice-card"><h3>'+e(c['title'])+'</h3><p>'+e(c['text'])+'</p><a href="'+
                e(c['href'],quote=True)+'">'+e(c['label'])+' →</a></article>' for c in s['cards'])+'</div>'
        if s.get('bullets'):
            out+='<ul>'+''.join('<li>'+e(text)+'</li>' for text in s['bullets'])+'</ul>'
        if s.get('links'):
            out+='<div class="topic-hub-related">'+''.join('<a href="'+e(url,quote=True)+'">'+e(label)+' →</a>' for url,label in s['links'])+'</div>'
        out+='</section>'
    out+='<section class="section topic-hub-section topic-hub-sources"><h2 id="'+e(hub['id'])+'-sources">资料来源与更新依据</h2>'
    out+='<p>套餐、业务规则与使用反馈按提供日期分别保存。下面链接可追溯到品牌说明与源资料；新增材料或确认更正后，再更新对应比较和结论。</p>'
    out+=source_links(hub['sources'])+'</section></div>'
    return out
