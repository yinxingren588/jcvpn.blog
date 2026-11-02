"""Maintain the original library and the authored, source-backed keyword expansion."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e
from pathlib import Path
import json
import re

from site_chrome import header, footer, write_changed

DATE='2026-11-02'
BRANDS=[('隐形人机场','brand-yinxingren.html'),('微风网络','brand-breezenet.html'),('飞猫云','brand-feimaoyun.html'),('暮光网络','brand-muguang.html'),('灵动云','brand-lingdongyun.html')]
SOURCES={
 'brand-catalog':['五个品牌的独立资料入口','brands.html'],
 'brand-plans':['套餐来源与各品牌独立说明','brands.html'],
 'brand-clients':['各品牌客户端名称与使用教程','brands.html'],
 'brand-coupons':['优惠范围与例外：进入对应品牌核对','brands.html'],
 'brand-rules':['流量、升级与退款：各品牌规则入口','brands.html'],
 'node-records':['四批节点延迟记录与来源','article-airport-review-records-overview.html'],
 'ai-records':['五条ChatGPT使用反馈与条件','article-vpn-ai-use-records.html'],
 'timeout-guide':['隐形人客服排查资料','data/invisible-support.json'],
 'ipsec':['RFC 4301：IP安全架构','https://www.rfc-editor.org/info/rfc4301/'],
 'aim':['Cloudflare：互联网性能测量指标','https://developers.cloudflare.com/speed/aim/'],
 'mihomo-config':['Mihomo官方文档：配置','https://wiki.metacubex.one/en/config/'],
 'mihomo-providers':['Mihomo官方文档：代理集合','https://wiki.metacubex.one/en/config/proxy-providers/'],
 'mihomo-groups':['Mihomo官方文档：代理组','https://wiki.metacubex.one/en/config/proxy-groups/']}

def load(root,name): return json.loads((root/name).read_text(encoding='utf-8'))
def money(value): return format(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'.2f')

def tables(root):
    # Each row retains its real source file; the figures are supplied snapshots, not live quotations.
    specs=[('invisible-plans.json','starlight-annual','silver-era','price','0.8','0.8','yxr888'),
           ('breezenet-plans.json','breeze-year','riding-month','price','0.9','0.9','weifeng90'),
           ('feimaoyun-plans.json','student','starlight','price_cny','1','0.9','flycat888'),
           ('muguang-plans.json','light-year','basic','price_cny','1','1','未确认优惠码'),
           ('lingdongyun-plans.json','chuanyun-year','fufeng','price_cny','1','0.8','wsj888')]
    annuals=[]; monthly=[]; overview=[]
    for i,(filename,annual_id,monthly_id,price_key,annual_rate,monthly_rate,code) in enumerate(specs):
        data=load(root,'data/'+filename)
        annual=next(p for p in data['plans'] if p['id']==annual_id)
        month=next((p for p in data['plans'] if p['id']==monthly_id),None)
        if month is None:
            month=next(p for p in data['plans'] if p['traffic_gb']=={'breezenet-plans.json':200,'muguang-plans.json':120}.get(filename,144))
        paid=Decimal(str(annual[price_key]))*Decimal(annual_rate)
        annuals.append([BRANDS[i][0],annual['name'],'¥'+money(annual[price_key])+'/年','¥'+money(paid)+'/年','约¥'+money(paid/12)+'/月',str(annual['traffic_gb'])+'GB',annual.get('reset',annual.get('reset_rule','每月刷新；具体日期核对后台'))])
        month_paid=Decimal(str(month[price_key]))*Decimal(monthly_rate)
        monthly.append([BRANDS[i][0],month['name'],'¥'+money(month[price_key])+'/月','¥'+money(month_paid)+'/月',str(month['traffic_gb'])+'GB/月','¥'+money(month_paid/Decimal(str(month['traffic_gb'])))+'/GB（满额算例）'])
        overview.append([BRANDS[i][0],str(len(data['plans']))+'款', ['IEPL专线资料','IPLC与原生IP资料','IPLC与学生年付方案','IPLC与独享定制','BGP资料；穿云另列IPLC'][i],filename])
    batches=[]
    for i,filename in [(0,'invisible-latency.json'),(1,'breezenet-latency.json'),(2,'feimaoyun-latency.json'),(3,'muguang-latency.json')]:
        d=load(root,'data/'+filename); s=d['summary']
        batches.append([BRANDS[i][0],d['measured_date'],d.get('measured_time') or d.get('period','时刻未提供'),str(s['node_count']),str(s['response_count']),str(s['timeout_count']),d['client']])
    ai=[]
    for i,filename in enumerate(['invisible-access-records.json','breezenet-access-records.json','feimaoyun-access-records.json','muguang-access-records.json','lingdongyun-access-records.json']):
        r=load(root,'data/'+filename)['records'][0]
        ai.append([BRANDS[i][0],r['tested_on'],r.get('tested_time') or '时刻未记录',r.get('test_location') or '所在地未记录',r.get('isp') or '运营商未记录',r['node_region'],'已报告能发送问题并收到回答'])
    return {
      'brand-overview':(['品牌','已提供套餐','资料方向','套餐源文件'],overview),
      'annuals':(['品牌','方案','原价','按已确认规则应付','年付折算','每期额度','刷新说明'],annuals),
      'monthly':(['品牌','入门月付','原价','按已确认规则应付','月度额度','名义满额单价'],monthly),
      'latency-batches':(['品牌','日期','时段或时刻','记录数','有数值','超时','客户端'],batches),
      'ai-records':(['品牌','日期','时刻','所在地','网络','节点地区','报告结果'],ai),
      'clients':(['品牌','Windows/macOS/安卓显示名称','已确认连接流程','iOS应用','识别码'],[[b[0],['隐形人','微风网络','飞猫云','暮光加速','灵动云'][i],'官网账号登录→选节点→连接','Nextin',['yxr','wfwl','fmy','mgjs','ldy'][i]] for i,b in enumerate(BRANDS)]),
      'refunds':(['品牌','已确认条件','申请期限','客服入口'],[[b[0],'技术问题经协助仍完全无法使用，全额退款','期限未提供' if i==0 else '购买后24小时内','客服' if i==0 else '登录官网后台联系客服'] for i,b in enumerate(BRANDS)]),
      'coupons':(['品牌','优惠码','力度','范围','期限'],[
        ['隐形人机场','yxr888','八折','全部9款','无到期限制'],['微风网络','weifeng90','九折','全部6款','期限未确认'],['飞猫云','flycat888','九折','学生版除外，其余6款','无到期限制'],['暮光网络','未提供','保留原价','不补造优惠规则','未提供'],['灵动云','wsj888','八折','穿云与至尊私人定制除外，其余7款','无到期限制']]),
      'evidence-gaps':(['记录项目','现有覆盖','尚需补充'],[
        ['套餐与优惠','五个品牌均有单独资料','当前结算与活动变更需核对'],['客户端流程','五品牌四平台说明','具体版本与系统要求'],['节点延迟','四批截图快照','同条件、跨日期与探测方法'],['ChatGPT问答','五条不同条件反馈','部分时刻、客户端和重复样本'],['流媒体与稳定性','品牌支持方向','对应播放与连续观测资料']])}

def layout(title,current,body,script=''):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(title)+'｜叮当观察</title><meta name="description" content="'+e(title,quote=True)+'"><link rel="stylesheet" href="assets/site-base.css"><link rel="stylesheet" href="assets/doraemon-theme.css"><link rel="stylesheet" href="assets/topics.css"><link rel="stylesheet" href="assets/library.css"><link rel="stylesheet" href="assets/expansion.css"><link rel="stylesheet" href="assets/search-library.css"></head><body><div class="shell">'+header(current)+'<main>'+body+'</main>'+footer()+'</div>'+script+'</body></html>'

def hero(label,title,description):
    return '<section class="hub-hero"><div><span class="overline">'+label+'</span><h1>'+e(title)+'</h1><p>'+e(description)+'</p></div></section>'

def ref_links(keys,sources,self_file=''):
    out=[]
    for key in keys:
        title,url=sources[key]
        if url==self_file:
            url='brands.html'
        external=url.startswith('https://')
        out.append('<a class="source" href="'+e(url,quote=True)+'"'+(' target="_blank" rel="noopener noreferrer"' if external else '')+'>'+e(title)+' ↗</a>')
    if 'node-records' in keys:
        out.extend('<a class="source" href="data/'+name+'-latency.json">'+label+'延迟源记录 JSON ↓</a>' for name,label in [('invisible','隐形人'),('breezenet','微风'),('feimaoyun','飞猫'),('muguang','暮光')])
    if 'ai-records' in keys:
        out.extend('<a class="source" href="data/'+name+'-access-records.json">'+label+'问答源记录 JSON ↓</a>' for name,label in [('invisible','隐形人'),('breezenet','微风'),('feimaoyun','飞猫'),('muguang','暮光'),('lingdongyun','灵动')])
    if 'brand-plans' in keys or 'brand-coupons' in keys:
        out.extend('<a class="source" href="data/'+name+'-plans.json">'+label+'套餐与优惠源资料 JSON ↓</a>' for name,label in [('invisible','隐形人'),('breezenet','微风'),('feimaoyun','飞猫'),('muguang','暮光'),('lingdongyun','灵动')])
    return ''.join(out)

def render_table(table,snapshot=False,caption=None):
    if not table:return ''
    heads,rows=table
    def cell(value):
        text=str(value)
        for name,url in BRANDS:
            if text==name:return '<a href="'+url+'">'+e(text)+'</a>'
        if text.endswith('.json') and text in ['invisible-plans.json','breezenet-plans.json','feimaoyun-plans.json','muguang-plans.json','lingdongyun-plans.json']:
            return '<a href="data/'+text+'">资料JSON</a>'
        return e(text)
    caption=caption or ('报价与记录来自2026年10月已提供资料；11月2日整理，未作实时询价。' if snapshot else '文中条件与方法对照；算例不代表品牌实测。')
    return '<div class="data-table" role="region" aria-label="文章资料对照表，可横向滚动" tabindex="0"><table><caption>'+e(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+e(str(x))+'</th>' for x in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+cell(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def row(a,topics):
    return '<a class="article-row" href="'+a['file']+'"><div><span class="overline">'+e(topics[a['category']]['name'])+'</span><h3>'+e(a['title'])+'</h3><p>'+e(a['summary'])+'</p></div><span>阅读全文 ↗</span></a>'

def build_content_library(root):
    root=Path(root)
    (root/'content/faqs').mkdir(parents=True,exist_ok=True)
    data=load(root,'data/library.json'); expansion=load(root,'data/editorial-expansion.json')
    new_ids={t['id'] for t in expansion['topics']}
    articles=[a for a in data['articles'] if a.get('origin')!='search-expansion']
    faqs=[f for f in data['faqs'] if f.get('origin')!='search-expansion']
    old_topics=[t for t in data['topics'] if t['id'] not in new_ids]
    sources={**data['sources'],**SOURCES}; source_tables=tables(root)
    corrected={
      'brands-listed':'本站收录隐形人机场、微风网络、飞猫云、暮光网络和灵动云，均有套餐与客户端资料。隐形人为本站主推，实际反馈与延迟记录按各品牌的日期和条件分别阅读。',
      'price-check':'五个品牌均已整理站长提供的套餐报价与额度。比较时先区分月付、年付和一次性总流量，查看优惠排除项，再到对应官网核对当前结算金额，不推算尚未提供的付款周期。',
      'brand-materials':'品牌页包含套餐、客户端与规则资料；部分另有截图延迟和ChatGPT反馈。品牌说明、用户反馈与独立复测不是同一种证据，记录应分别保留来源与日期。'}
    for f in faqs:
        if f['id'] in corrected:f['answer']=corrected[f['id']]
    revisions_path=root/'data/editorial-revisions.json'
    revisions=load(root,'data/editorial-revisions.json')['articles'] if revisions_path.exists() else []
    original_map={a['slug']:a for a in articles}
    faq_map={f['id']:f for f in faqs}
    for revision in revisions:
        a=original_map[revision['slug']]
        a.update({k:v for k,v in revision.items() if k not in ('slug','faq_answers')})
        for fid,answer in revision.get('faq_answers',{}).items():
            assert faq_map[fid]['article']==a['slug'],fid
            faq_map[fid]['answer']=answer
        for fid in a['faq_ids']:faq_map[fid]['sources']=a['sources']
        a['faqs']=[[faq_map[fid]['question'],faq_map[fid]['answer']] for fid in a['faq_ids']]
        a['chars']=len(a['summary'])+sum(len(h)+len(p) for h,p in a['sections'])+sum(map(len,a['checks']))
    for source in expansion['articles']:
        a={**source,'origin':'search-expansion','file':'article-'+source['slug']+'.html','faq_ids':[]}
        a['table']=source_tables.get(a.get('table_kind'))
        a['chars']=len(a['summary'])+sum(len(h)+len(p) for h,p in a['sections'])+sum(map(len,a['checks']))
        for index,(q,answer,steps) in enumerate(a['faqs'],1):
            fid=a['slug']+'-'+str(index); a['faq_ids'].append(fid)
            faqs.append(dict(id=fid,category=a['category'],question=q,answer=answer,steps=steps,article=a['slug'],type='专题解答与核对步骤',sources=a['sources'],origin='search-expansion',file='faq-'+fid+'.html'))
        articles.append(a)
    topic_list=expansion['topics']+old_topics; topics={t['id']:t for t in topic_list}
    amap={a['slug']:a for a in articles}; fmap={f['id']:f for f in faqs}
    assert len(amap)==84 and len(faqs)==248 and len({f['question'] for f in faqs})==248
    for t in topic_list:
        if t['id'] in new_ids:
            t['steps']={
                'recommendations':['明确设备、用量与售后要求','并排核对五品牌对应方案','验证自己的主要使用任务'],
                'vpn-choice':['分清用途、授权与连接范围','核对问答或播放的具体动作','保留相应环境下的访问记录'],
                'nodes-guide':['先确定任务和节点地区需求','区分延迟探测与实际目标响应','发生异常时做单变量对照'],
                'reviews-guide':['找出数据来源与采样窗口','核对统计口径和失败样本','补充连续记录及关键缺失条件'],
                'budget-guide':['区分月付、年付与一次性总量','核对优惠范围与实际付款','按自己的消耗评估预算'],
                'clash-guide':['确认客户端和实际内核版本','核对协议与订阅格式','分别验证导入、连接和访问']
            }[t['id']]
        aa=[a for a in articles if a['category']==t['id']]
        t['article_paths']=[a['file'] for a in aa]; t['articles']=[a['title'] for a in aa]
        t['faq']=[f['id'] for f in faqs if f['category']==t['id']]
    def faq_link(f): return f.get('file','faq.html#'+f['id'])
    for a in articles:
        t=topics[a['category']]; date=a.get('published_on','2026-10-28')
        toc=''.join('<a href="#section-'+str(i)+'">'+e(h)+'</a>' for i,(h,p) in enumerate(a['sections'],1))
        sections=''.join('<section class="prose-section" id="section-'+str(i)+'"><h2>'+e(h)+'</h2><p>'+e(p)+'</p></section>' for i,(h,p) in enumerate(a['sections'],1))
        category_articles=[x for x in articles if x['category']==a['category']]
        position=next(i for i,x in enumerate(category_articles) if x['slug']==a['slug'])
        related=(category_articles[position+1:]+category_articles[:position])[:3]
        inline=''.join('<details class="inline-faq"><summary>'+e(fmap[fid]['question'])+'</summary><p>'+e(fmap[fid]['answer'])+'</p><a href="'+faq_link(fmap[fid])+'">查看完整解答 →</a></details>' for fid in a['faq_ids'])
        table=render_table(a.get('table'),bool(a.get('origin')),a.get('table_caption'))
        if a.get('table_after_section'):
            sections=''.join('<section class="prose-section" id="section-'+str(i)+'"><h2>'+e(h)+'</h2><p>'+e(p)+'</p></section>'+(table if i==a['table_after_section'] else '') for i,(h,p) in enumerate(a['sections'],1))
            table=''
        quick='<section class="article-quick-answer" aria-label="阅读要点"><strong>先看结论</strong><p>'+e(a['quick_answer'])+'</p></section>' if a.get('quick_answer') else ''
        revision_note='<details class="article-revision"><summary>本次修订说明 · '+a['reviewed_on']+'</summary><p>'+e(a['revision_note'])+'</p></details>' if a.get('reviewed_on') else ''
        display_date='初稿 <time datetime="'+date+'">'+date+'</time>'
        if a.get('reviewed_on'):display_date+=' · 修订 <time datetime="'+a['reviewed_on']+'">'+a['reviewed_on']+'</time>'
        note='本文为资料型选择指南；套餐与截图记录按来源日期列明。隐形人是本站主推，展示位置不作为独立测速排名。' if a.get('origin') else 'AI辅助撰写与资料整理；技术解释、方法和算例不作为本站完成的品牌实测。'
        body='<div class="article-breadcrumb"><a href="topics.html">专题</a> / <a href="topic-'+t['id']+'.html">'+e(t['name'])+'</a></div><article class="article-panel"><header class="article-header"><span class="overline">'+e(t['name'])+'</span><h1>'+e(a['title'])+'</h1><p class="article-lead">'+e(a['summary'])+'</p><div class="article-meta">'+display_date+' · 叮当观察</div><p class="authorship">'+note+'</p></header><div class="article-layout"><aside class="article-toc" aria-label="文章目录"><strong>本文目录</strong>'+toc+'</aside><div class="article-prose">'+quick+sections+table+'<section class="takeaway"><h2>选择与核对清单</h2><ul>'+''.join('<li>'+e(c)+'</li>' for c in a['checks'])+'</ul></section><section class="prose-section"><h2>相关问题</h2>'+inline+'</section><section class="reference-box"><h2>资料与参考</h2>'+ref_links(a['sources'],sources,a['file'])+'<p>品牌报价与记录来自已提供材料。本文的比较步骤为本站整理方法，具体产品条件应在购买前核对。</p>'+revision_note+'</section><section class="prose-section"><h2>继续阅读</h2>'+''.join(row(x,topics) for x in related)+'</section></div></div></article>'
        write_changed(root/a['file'],layout(a['title'],'blog',body))
        md='# '+a['title']+'\n\n'+a['summary']+'\n\n初稿日期：'+date+'。'+('修订日期：'+a['reviewed_on']+'。' if a.get('reviewed_on') else '')+'\n\n'
        if a.get('quick_answer'):md+='## 先看结论\n\n'+a['quick_answer']+'\n\n'
        md+=''.join('## '+h+'\n\n'+p+'\n\n' for h,p in a['sections'])
        if a.get('table'):
            heads,rows=a['table']; md+='| '+' | '.join(heads)+' |\n| '+' | '.join(['---']*len(heads))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)+'\n'
        md+='## 核对清单\n\n'+''.join('- '+c+'\n' for c in a['checks'])+'\n## 相关FAQ\n\n'+''.join('### '+fmap[fid]['question']+'\n\n'+fmap[fid]['answer']+'\n\n' for fid in a['faq_ids'])+'## 来源\n\n'+''.join('- ['+sources[k][0]+']('+sources[k][1]+')\n' for k in a['sources'])
        markdown_path=root/'content/articles'/(a['slug']+'.md')
        if a.get('origin') or a.get('reviewed_on') or not markdown_path.exists():
            write_changed(markdown_path,md.rstrip()+'\n')
    for f in faqs:
        if f.get('origin')!='search-expansion':continue
        a=amap[f['article']]; t=topics[f['category']]
        related=[x for x in faqs if x['category']==f['category'] and x['id']!=f['id'] and x.get('file')][:3]
        body='<div class="article-breadcrumb"><a href="faq.html">FAQ专题</a> / <a href="topic-'+t['id']+'.html">'+e(t['name'])+'</a></div><article class="article-panel faq-detail"><header class="article-header"><span class="overline">'+e(t['name'])+' / FAQ</span><h1>'+e(f['question'])+'</h1><p class="article-lead">'+e(f['answer'])+'</p><div class="article-meta">叮当观察 · '+DATE+'整理</div></header><section class="prose-section"><h2>怎样继续核对</h2><ol>'+''.join('<li>'+e(s)+'</li>' for s in f['steps'])+'</ol></section><section class="prose-section"><h2>适用范围与完整说明</h2><p>'+e(a['summary'])+'</p>'+row(a,topics)+'</section><section class="reference-box"><h2>资料出处</h2>'+ref_links(f['sources'],sources,f['file'])+'</section><section class="prose-section"><h2>相关问题</h2>'+''.join('<a class="faq-short" href="'+x['file']+'">'+e(x['question'])+'<span>→</span></a>' for x in related)+'</section></article>'
        write_changed(root/f['file'],layout(f['question'],'faq',body))
        write_changed(root/'content/faqs'/(f['id']+'.md'),'# '+f['question']+'\n\n'+f['answer']+'\n\n## 核对步骤\n\n'+''.join(str(i)+'. '+s+'\n' for i,s in enumerate(f['steps'],1))+'\n[完整指南]('+a['file']+')\n')
    topic_cards=''
    for t in topic_list:
        aa=[a for a in articles if a['category']==t['id']]; ff=[f for f in faqs if f['category']==t['id']]
        topic_cards+='<a class="topic-card" href="topic-'+t['id']+'.html"><span class="topic-icon">'+e(t['icon'])+'</span><span class="overline">'+('选择与使用专题' if t['id'] in new_ids else '基础阅读路线')+'</span><h2>'+e(t['name'])+'</h2><p>'+e(t['intro'])+'</p><span class="topic-card-foot">'+str(len(aa))+'篇文章 · '+str(len(ff))+'条FAQ <b>↗</b></span></a>'
        steps=t.get('steps',['先明确当前使用需求','对照对应资料与条件','完成实际任务后保留记录'])
        topic_body=hero('READ BY PURPOSE',t['name'],t['intro'])+'<div class="breadcrumb"><a href="topics.html">全部专题</a> / '+e(t['name'])+'</div><section class="section"><h2>按这个顺序阅读</h2><p>'+e(t['audience'])+'。先明确问题，再沿文章核对资料，实际使用结果按日期与环境分别记录。</p><ol class="route-list">'+''.join('<li><b>'+str(i).zfill(2)+'</b>'+e(s)+'</li>' for i,s in enumerate(steps,1))+'</ol></section><section class="section"><div class="sectionhead"><h2>专题文章</h2><span>'+str(len(aa))+'篇独立正文</span></div>'+''.join(row(a,topics) for a in aa)+'</section><section class="section"><h2>专题FAQ</h2>'+''.join('<a class="faq-short" href="'+faq_link(f)+'">'+e(f['question'])+'<span>→</span></a>' for f in ff[:8])+'</section>'
        write_changed(root/('topic-'+t['id']+'.html'),layout(t['name'],'topics',topic_body))
    write_changed(root/'topics.html',layout('机场推荐、VPN与节点专题','topics',hero('GUIDES BY SEARCH INTENT','机场推荐、VPN与节点专题','12条阅读路线：先按需求选择专题，再进入完整文章和具体问题。')+'<section class="topic-grid">'+topic_cards+'</section><section class="section"><h2>84篇文章与248条FAQ怎样衔接</h2><p>选择指南负责解释条件、展示资料表和提供下一步；FAQ集中回答一个明确问题。新增48条FAQ均有独立页面，其余问题保留原来的锚点入口与延伸阅读。</p><a class="inline-link" href="blog.html">查看全部文章 →</a></section>'))
    ordered=[a for a in articles if a.get('origin')]+[a for a in articles if not a.get('origin')]
    filters='<button type="button" data-category="all" aria-pressed="true">全部内容</button>'+''.join('<button type="button" data-category="'+t['id']+'" aria-pressed="false">'+e(t['name'])+'</button>' for t in topic_list)
    cards=''.join('<article class="catalog-card" data-library-card data-category="'+a['category']+'"><a href="'+a['file']+'"><span class="overline">'+e(topics[a['category']]['name'])+'</span><h2>'+e(a['title'])+'</h2><p>'+e(a['summary'])+'</p><span class="catalog-foot">'+('修订于 '+a['reviewed_on'] if a.get('reviewed_on') else '独立正文 · '+a.get('published_on','2026-10-28'))+'<b>阅读全文 ↗</b></span></a></article>' for a in ordered)
    controls='<section class="section library-controls"><label class="faq-search">⌕ <input type="search" aria-label="搜索文章" placeholder="搜索主题，例如机场推荐、年付、节点、Clash"></label><div class="faq-filters" role="group" aria-label="文章分类">'+filters+'</div><p id="library-count" aria-live="polite">84篇文章</p></section>'
    pager='<div class="pagination"><button type="button" id="library-previous">← 上一页</button><span id="library-page" aria-live="polite"></span><button type="button" id="library-next">下一页 →</button></div>'
    write_changed(root/'blog.html',layout('机场推荐与VPN使用指南','blog',hero('ARTICLE LIBRARY','机场推荐与VPN使用指南','84篇独立文章，覆盖机场推荐、VPN、节点选择、机场测评、性价比与Clash配置。')+controls+'<div class="catalog-grid">'+cards+'</div><p class="section" id="library-empty" hidden>没有匹配文章，请调整关键词或分类。</p>'+pager,'<script src="assets/content-library.js" defer></script>'))
    groups=''
    for t in topic_list:
        entries=''
        for f in [f for f in faqs if f['category']==t['id']]:
            a=amap[f['article']]
            entries+='<details class="faq-item" id="'+f['id']+'" data-category="'+f['category']+'"><summary>'+e(f['question'])+'</summary><div class="answer"><span class="answer-kind">'+e(f['type'])+'</span><p>'+e(f['answer'])+'</p>'+('<a class="answer-topic" href="'+f['file']+'">打开这个问题的独立页面 →</a>' if f.get('file') else '')+'<a class="answer-topic" href="'+a['file']+'">完整指南：'+e(a['title'])+' →</a></div></details>'
        groups+='<section class="faq-group section" data-group="'+t['id']+'"><h2>'+e(t['name'])+'</h2>'+entries+'</section>'
    faq_controls='<section class="section faq-controls"><label class="faq-search">⌕ <input type="search" aria-label="搜索FAQ" placeholder="搜索机场推荐、优惠、节点、Clash或具体问题"></label><div class="faq-filters" role="group" aria-label="FAQ分类">'+filters+'</div><div class="faq-tools"><p id="faq-count" aria-live="polite">248个问题</p><div><button type="button" id="expand-all">展开本页</button><button type="button" id="collapse-all">收起全部</button></div></div></section>'
    faq_pager='<div class="pagination faq-pagination"><button type="button" id="faq-previous">← 上一页</button><span id="faq-page" aria-live="polite"></span><button type="button" id="faq-next">下一页 →</button></div>'
    write_changed(root/'faq.html',layout('机场推荐与VPN常见问题','faq',hero('QUESTIONS WITH CONTEXT','机场推荐与VPN常见问题','248条FAQ，按12类任务查找。新增问题可进入独立页面，查看核对步骤、资料来源与完整指南。')+faq_controls+'<p class="section" id="faq-empty" hidden>没有匹配问题，请清空关键词或切换分类。</p>'+groups+faq_pager,'<script src="assets/content-library.js" defer></script>'))
    home=(root/'index.html').read_text(encoding='utf-8')
    home=home.replace('60篇完整文章 · 六条阅读路线','84篇独立文章 · 12条阅读路线').replace('200个常见问题，按专题查找与搜索','248个常见问题，含48个独立解答页')
    home=home.replace('60篇资料型文章与200条FAQ','84篇资料型文章与248条FAQ')
    featured=[next(a for a in ordered if a['category']==t['id']) for t in expansion['topics']]
    reading='<section class="section" id="reading"><div class="sectionhead"><div><span class="overline">PRACTICAL READING PATHS</span><h2>从需求出发，读懂推荐与测评。</h2><p>六个选择与使用专题，各从一篇具体指南开始。</p></div><a href="blog.html">查看全部84篇 ↗</a></div><div class="search-featured-grid">'+''.join(row(a,topics) for a in featured)+'</div></section>'
    home=re.sub(r'<section class="section" id="reading">.*?</section>',lambda _:reading,home,count=1,flags=re.S)
    home=re.sub(r'<link rel="stylesheet" href="assets/search-library\.css">','',home)
    home=home.replace('</head>','<link rel="stylesheet" href="assets/search-library.css"></head>',1)
    write_changed(root/'index.html',home)
    data.update(topics=topic_list,sources=sources,articles=articles,faqs=faqs,updated_on=DATE,
                authorship='AI辅助撰写与资料整理；品牌说明、使用反馈与独立测试分开记录')
    write_changed(root/'data/library.json',json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    write_changed(root/'data/topics.json',json.dumps(dict(topics=topic_list,faqs=faqs,article_catalog='library.json'),ensure_ascii=False,indent=2)+'\n')
