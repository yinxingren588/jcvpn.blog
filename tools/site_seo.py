"""Apply page-specific titles, descriptions, keywords and matching structured metadata."""
from html import escape as e
from pathlib import Path
from urllib.parse import quote
import csv
import io
import json
import re

from site_chrome import write_changed

DATE='2026-11-02'
SUFFIX='｜叮当观察'
KEYS={
 'recommendations':['机场推荐','梯子推荐'], 'vpn-choice':['VPN','VPN推荐'],
 'nodes-guide':['节点推荐','机场节点'], 'reviews-guide':['机场测评','稳定机场'],
 'budget-guide':['性价比机场','便宜机场','便宜机场推荐'], 'clash-guide':['Clash机场'],
 'basics':['VPN','机场VPN','VPN入门'], 'diagnostics':['机场节点','VPN连接排查'],
 'plans':['性价比机场','机场套餐','便宜机场'], 'testing':['机场测评','节点延迟','稳定机场'],
 'privacy':['VPN','隐私与配置'], 'brands':['机场推荐','机场测评','品牌资料']}
PREFIX={'basics':'VPN入门：','diagnostics':'机场节点排查：','plans':'性价比机场选择：',
        'testing':'机场测评：','privacy':'VPN隐私配置：','brands':'机场推荐资料：'}

def shorten(text,limit=145):
    text=re.sub(r'\s+',' ',text).strip()
    if len(text)<=limit:return text
    part=text[:limit-1]
    # Finish at a natural clause boundary if it does not discard most of the summary.
    cut=max(part.rfind('。'),part.rfind('；'))
    return part[:cut+1] if cut>limit*.65 else part.rstrip('，、；：。 ')+'。'

def apply_site_seo(root):
    root=Path(root); data=json.loads((root/'data/library.json').read_text(encoding='utf-8'))
    metadata={}
    def put(file,title,description,keywords,kind='WebPage',published=None):
        metadata[file]=dict(title=title if title.endswith(SUFFIX) else title+SUFFIX,
                            description=shorten(description),keywords=list(dict.fromkeys(keywords)),kind=kind,published_on=published)
    put('index.html','机场推荐与VPN推荐｜套餐对比、节点记录与Clash指南',
        '叮当观察提供机场推荐、梯子推荐、VPN推荐与节点选择指南，整理隐形人等五品牌的套餐、优惠和使用资料，并收录飞v、梯子云、浪网入口。通过性价比机场、便宜机场推荐、Clash机场和稳定性专题，核对预算、客户端、售后条件及实际记录。',
        ['机场推荐','梯子推荐','VPN推荐','机场测评','性价比机场','机场节点','Clash机场','稳定机场'],'WebSite')
    put('blog.html','机场推荐与VPN文章｜节点、测评、性价比及Clash指南',
        '浏览叮当观察84篇独立文章，围绕机场推荐、梯子推荐、VPN推荐、机场节点、机场测评、性价比与Clash机场开展阅读。支持关键词搜索和12类专题筛选，查看五品牌报价表、优惠例外、退款条件与真实记录的适用范围。',
        ['机场推荐','梯子推荐','VPN推荐','机场测评','便宜机场推荐','Clash机场'],'CollectionPage')
    put('topics.html','机场推荐专题｜VPN、节点推荐、稳定性与便宜机场',
        '叮当观察提供12个阅读专题，涵盖机场推荐与梯子选择、VPN使用、节点推荐、机场测评、稳定性、性价比和Clash机场。专题串联84篇完整文章与248条FAQ，帮助读者按实际任务核对价格、客户端、资料来源和使用条件。',
        ['机场推荐','VPN','节点推荐','稳定机场','便宜机场','Clash机场'],'CollectionPage')
    put('faq.html','机场与VPN常见问题｜推荐、套餐、节点及Clash FAQ',
        '查询248个机场与VPN常见问题，涵盖机场推荐、VPN推荐、节点选择、便宜机场、优惠范围、流量规则、退款条件和Clash客户端。支持搜索与专题筛选，新增48个问题可打开独立页面，继续查看核对步骤、来源和完整指南。',
        ['机场推荐','VPN推荐','机场节点','便宜机场','Clash机场','机场FAQ'],'CollectionPage')
    put('brands.html','机场品牌目录｜8个品牌入口与套餐资料',
        '浏览叮当观察8个品牌入口：隐形人独立主推，微风网络、飞猫云、暮光网络和灵动云分别提供套餐、客户端及已有记录；飞v、梯子云LadderCloud、浪网WaveNet资料陆续补充。主推展示不作为同条件测速排名。',
        ['机场推荐','机场品牌','隐形人机场','性价比机场','机场测评资料'],'CollectionPage')
    brand_specs=[
      ('yinxingren','隐形人机场怎么样｜IEPL套餐、优惠码与节点记录','隐形人机场品牌页整理IEPL专线、9款套餐与yxr888八折优惠，包括109元年付、80GB每30天刷新方案。查看Windows、macOS、安卓及iOS使用流程、流量重置、退款条件、晚高峰延迟与ChatGPT使用反馈。',['隐形人机场','机场推荐','IEPL专线','机场节点','机场套餐']),
      ('breezenet','微风网络机场资料｜套餐价格、节点与使用教程','微风网络Breezenet资料汇总6款套餐、IPLC与原生IP说明、weifeng90九折优惠及客户端教程。查看清风100GB年付方案、月付与一次性总流量、上海电信午间节点记录、ChatGPT反馈和技术问题退款条件。',['微风网络','机场推荐','性价比机场','机场节点']),
      ('feimaoyun','飞猫云机场测评资料｜学生年付、套餐与节点记录','飞猫云页面整理IPLC线路、7款套餐与flycat888九折规则，学生版84元年付不参与该优惠。核对月度和一次性流量、Windows与移动端教程、晚高峰节点延迟、ChatGPT反馈及购买后24小时内技术问题退款条件。',['飞猫云','机场测评','便宜机场','机场节点']),
      ('muguang','暮光网络机场｜IPLC套餐、节点记录与客户端教程','暮光网络介绍汇总9款套餐、IPLC专线、节点地区与暮光加速客户端教程，iOS使用Nextin识别码mgjs。查看年付轻量版、月付和不限时流量包、上海电信上午节点记录、ChatGPT反馈与技术问题退款条件。',['暮光网络','机场推荐','IPLC专线','机场节点']),
      ('lingdongyun','灵动云机场｜八折套餐、节点地区与使用教程','灵动云页面整理9款套餐、BGP线路资料、SS协议及各平台客户端，iOS使用Nextin识别码ldy。八折码wsj888适用7款，穿云和至尊私人定制除外；另列新加坡节点ChatGPT反馈、流量规则与技术问题退款条件。',['灵动云','性价比机场','便宜机场','机场节点'])]
    for slug,title,description,keys in brand_specs:put('brand-'+slug+'.html',title,description,keys)
    intake=json.loads((root/'data/new-brands.json').read_text(encoding='utf-8'))['brands']
    for b in intake:
        put(b['profile_path'],b['name']+(' '+b['english_name'] if b['english_name'] else '')+'品牌入口｜套餐与资料陆续补充',
            '叮当观察已收录'+b['name']+'的站长确认推广入口。当前套餐价格、额度、客户端、节点与售后资料尚待提供；本页展示已知来源和选择前核对步骤，详情会按真实材料逐项补充。',[b['name'],b['english_name']] if b['english_name'] else [b['name']])
    for t in data['topics']:
        count=len(t['article_paths']); n=len(t['faq']); keys=t.get('keywords') or KEYS[t['id']]
        desc='叮当观察的'+t['name']+'专题，整理'+str(count)+'篇独立文章与'+str(n)+'条常见问题。'+t['intro']+'从具体需求进入对应指南，查看条件对照、核对步骤和资料出处，区分品牌说明、使用反馈与尚待验证的结果。'
        put('topic-'+t['id']+'.html',t.get('seo_title',t['name']+'专题｜选择方法、资料与FAQ'),t.get('seo_description',desc),keys,'CollectionPage')
    articlemap={a['slug']:a for a in data['articles']}
    for a in data['articles']:
        title=a['title']
        if not a.get('origin'):
            prefix=PREFIX[a['category']]
            if not (a['category']=='basics' and 'VPN' in title.upper()):title=prefix+title
        desc=a['summary']+'本文说明'+ '、'.join(a['checks'])+'，结合适用条件、资料出处和相关问题继续核对，帮助读者按自己的任务判断。'
        put(a['file'],title,desc,KEYS[a['category']],'Article',a.get('published_on','2026-10-28'))
    for f in data['faqs']:
        if not f.get('file'):continue
        a=articlemap[f['article']]
        put(f['file'],f['question'],f['answer']+'本页提供具体核对步骤、资料出处与'+a['title']+'的延伸阅读，便于结合实际条件理解。',KEYS[f['category']],'FAQPage',DATE)
    put('about.html','关于叮当观察｜机场与VPN内容来源、编辑原则',
        '认识叮当观察的机场与VPN内容方向、资料来源及编辑原则。了解品牌说明、第三方使用反馈、本站整理方法和独立测试的区别，查看主推展示与推广入口说明，并通过联系入口提交具体页面的纠错与资料补充。',['叮当观察','机场资料来源','VPN指南'])
    put('contact.html','联系叮当观察｜内容纠错、资料补充与合作咨询',
        '通过叮当观察公开邮箱或Telegram联系站方，提交机场与VPN文章的内容纠错、失效链接、资料补充或合作咨询。请附具体页面和问题说明；品牌账号、订单、节点故障及退款申请优先通过所购品牌官方客服处理。',['叮当观察联系','机场内容纠错','VPN资料补充'])
    put('404.html','页面未找到｜返回机场与VPN内容导航',
        '当前页面不存在或链接已经变化。可返回叮当观察首页，浏览机场推荐、VPN使用、节点选择与FAQ专题，也可以通过联系我们反馈失效链接。',[])
    descriptions={}
    for path in root.glob('*.html'):
        if path.name=='01-首页框架.html':continue
        assert path.name in metadata, 'Unmapped SEO page: '+path.name
        m=metadata[path.name]; text=path.read_text(encoding='utf-8')
        text=re.sub(r'<title>.*?</title>','<title>'+e(m['title'])+'</title>',text,count=1,flags=re.S)
        for attr,name in [('name','description'),('name','keywords'),('property','og:title'),('property','og:description'),('property','og:url'),('property','og:type'),('name','twitter:card'),('name','twitter:title'),('name','twitter:description')]:
            text=re.sub(r'<meta\b(?=[^>]*\b'+attr+r'=["\']'+re.escape(name)+r'["\'])[^>]*>','',text,flags=re.I)
        url='https://jcvpn.blog/' if path.name=='index.html' else 'https://jcvpn.blog/'+quote(path.stem)
        tags='<meta name="description" content="'+e(m['description'],quote=True)+'"><meta name="keywords" content="'+e(','.join(m['keywords']),quote=True)+'">'
        for attr,name,value in [('property','og:title',m['title']),('property','og:description',m['description']),('property','og:url',url),('property','og:type','article' if m['kind']=='Article' else 'website'),('name','twitter:card','summary'),('name','twitter:title',m['title']),('name','twitter:description',m['description'])]:
            tags+='<meta '+attr+'="'+name+'" content="'+e(value,quote=True)+'">'
        structured={'@context':'https://schema.org','@type':m['kind'],'name':m['title'],'description':m['description'],'url':url,'inLanguage':'zh-CN'}
        if m['kind']=='Article':
            article=articlemap[path.stem.removeprefix('article-')]
            structured.update(headline=article['title'],datePublished=m['published_on'],author={'@type':'Organization','name':'叮当观察'},mainEntityOfPage=url)
            if article.get('reviewed_on'):structured['dateModified']=article['reviewed_on']
        if m['kind']=='FAQPage':
            f=next(f for f in data['faqs'] if f.get('file')==path.name)
            structured['mainEntity']=[{'@type':'Question','name':f['question'],'acceptedAnswer':{'@type':'Answer','text':f['answer']}}]
        text=re.sub(r'<script type="application/ld\+json" id="site-seo-structured-data">.*?</script>','',text,flags=re.S)
        tags+='<script type="application/ld+json" id="site-seo-structured-data">'+json.dumps(structured,ensure_ascii=False).replace('</',r'<\/')+'</script>'
        if path.name=='index.html':
            text=re.sub(r'<h1>.*?</h1>','<h1>机场推荐与VPN推荐，<br><em>先看套餐与节点，<br>再做适合自己的选择。</em></h1>',text,count=1,flags=re.S)
            text=text.replace('关于 VPN 与机场VPN，我们从原理、使用问题和真实依据出发，把复杂的连接，讲得清楚一点。','从机场套餐、节点记录到Clash客户端与常见问题，按预算和真实使用需求，找到值得继续核对的方案。')
        text=text.replace('</head>',tags+'</head>',1)
        write_changed(path,text)
        descriptions[path.name]=m['description']
    assert len({m['title'] for m in metadata.values()})==len(metadata),'Duplicate page titles'
    write_changed(root/'data/page-descriptions.json',json.dumps(descriptions,ensure_ascii=False,indent=2)+'\n')
    write_changed(root/'data/seo-metadata.json',json.dumps(dict(updated_on=DATE,pages=metadata),ensure_ascii=False,indent=2)+'\n')
    out=io.StringIO(newline=''); writer=csv.writer(out,lineterminator='\n')
    writer.writerow(['页面','标题Title','描述Description','关键词Keywords'])
    for name,m in metadata.items():writer.writerow([name,m['title'],m['description'],'、'.join(m['keywords'])])
    write_changed(root/'data/seo-metadata.csv','\ufeff'+out.getvalue())
