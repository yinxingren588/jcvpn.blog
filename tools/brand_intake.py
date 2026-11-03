"""Publish confirmed brand entrances without inventing service facts."""
import json
import re
from html import escape as e
from pathlib import Path
from site_chrome import shell,write_changed

def brand_mark(brand):
    if brand.get('logo_path'):
        return '<span class="intake-mark intake-logo"><img src="'+e(brand['logo_path'],quote=True)+'" width="'+str(brand['logo_width'])+'" height="'+str(brand['logo_height'])+'" alt="'+e(brand['name'],quote=True)+'Logo" decoding="async"></span>'
    return '<span class="intake-mark" aria-hidden="true">'+e(brand['mark'])+'</span>'

def intake_copy(brand):
    if brand['id']=='feiv' and brand.get('coupon_path'):
        return '9款套餐 · 八折优惠','fly20八折；续费及重置包除外，不叠加','查看套餐资料'
    if brand['id']=='tiziyun' and brand.get('coupon_path'):
        return '9款套餐 · 5款享八五折','2hy85；年付保活、3款买断除外，不叠加','查看套餐与优惠'
    if brand['id']=='langwang' and brand.get('coupon_path'):
        return '9款套餐 · 全部享八折','lw888；周期续费与普通周期重置包可用，不叠加','查看套餐与优惠'
    if brand['id']=='langwang' and brand.get('node_profile_ready'):
        return '9款套餐 · 60个节点','BGP / 年付IPLC · SS · 12点节点记录','查看套餐与节点'
    if brand.get('node_profile_ready'):
        return '9款套餐 · 50个节点','BGP / 高阶IEPL · SS · 套餐与下午记录','查看套餐与节点'
    if brand.get('plans_path'):
        return '9款套餐已整理','年付、月付与一次性总流量','查看套餐资料'
    return '入口已收录','套餐与介绍陆续补充','查看品牌页面'

def build_brand_intake(root):
    root=Path(root)
    source=json.loads((root/'data/new-brands.json').read_text(encoding='utf-8'))
    brands=source['brands']
    pending=[b for b in brands if not b.get('plans_path') and not b.get('node_profile_ready')]
    catalog=json.loads((root/'data/brands.json').read_text(encoding='utf-8'))
    by_id={b['id']:b for b in catalog['brands']}
    for b in brands:
        material_status=b.get('profile_status','entry_provided_details_pending')
        by_id[b['id']]={**by_id.get(b['id'],{}),**b,'source_type':b.get('materials_source',source['source']),'source_date':b.get('materials_updated_on',source['confirmed_on']),'verification_status':material_status,'commercial_relationship':'推广入口；具体合作条件未提供'}
        if b.get('node_profile_ready'):
            if b['id']=='tiziyun':
                from tiziyun_profile import build_tiziyun_profile
                build_tiziyun_profile(root,b)
            elif b['id']=='langwang':
                from langwang_profile import build_langwang_profile
                build_langwang_profile(root,b)
            else:
                raise AssertionError('A node profile builder is required for this brand.')
            continue
        if b.get('plans_path'):
            from flyv_profile import build_flyv_profile
            assert b['id']=='feiv','A profile builder is required for this brand.'
            build_flyv_profile(root,b)
            continue
        name=b['name']+(' '+b['english_name'] if b['english_name'] else '')
        body='<section class="info-hero intake-hero"><span class="info-kicker">BRAND PROFILE / IN PROGRESS</span><span class="intake-status">入口已收录 · 资料补充中</span><h1>'+e(name)+'</h1><p>本站已收录站长确认的'+e(b['name'])+'推广入口。套餐价格、流量规则、客户端与使用记录将按后续提供的资料逐项整理。</p><div class="contact-buttons"><a class="contact-action" href="'+e(b['url'],quote=True)+'" target="_blank" rel="sponsored noopener noreferrer">访问'+e(b['name'])+'推广入口 ↗</a><a class="copy-contact" href="brands.html">查看全部品牌 →</a></div></section><nav class="info-breadcrumb" aria-label="当前位置"><a href="index.html">首页</a><span>/</span><a href="brands.html">品牌介绍</a><span>/</span><span>'+e(b['name'])+'</span></nav><section class="info-section"><h2>目前已确认的资料</h2><dl class="intake-facts"><div><dt>品牌名称</dt><dd>'+e(name)+'</dd></div><div><dt>入口来源</dt><dd>博客站长提供，2026-11-02收录；此链接为推广入口。</dd></div><div><dt>套餐与价格</dt><dd>待提供，不沿用其他品牌的金额或优惠。</dd></div><div><dt>客户端与节点</dt><dd>待提供，不预填线路、识别码或节点数量。</dd></div></dl></section><section class="info-section"><h2>选择前先核对什么</h2><p>先确认付款周期、流量额度、刷新方式、设备要求与售后条件，再对照自己的使用任务。当前页面仅提供已确认入口，尚未形成性能评价。</p><p><a href="topic-recommendations.html">阅读机场推荐与梯子推荐指南 →</a>　<a href="article-plan-comparison-sheet.html">查看套餐比较方法 →</a></p></section>'
        if b.get('logo_path'):
            heading='<h1>'+e(name)+'</h1>'
            body=body.replace(heading,'<div class="intake-brand-heading">'+brand_mark(b)+heading+'</div>',1)
        html=shell(name+'品牌入口与资料',name+'品牌推广入口已收录；套餐、客户端和节点资料正在补充。',body)
        html=html.replace('</head>','<link rel="stylesheet" href="assets/brand-intake.css"></head>',1)
        write_changed(root/b['profile_path'],html)
    catalog['brands']=list(by_id.values())
    catalog['updated_on']=max([source['confirmed_on']]+[b.get('materials_updated_on',source['confirmed_on']) for b in brands])
    write_changed(root/'data/brands.json',json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    policy={'noindex_pages':{b['profile_path']:'仅确认品牌名与入口；补齐实质资料后再开放索引' for b in pending}}
    write_changed(root/'data/indexing-policy.json',json.dumps(policy,ensure_ascii=False,indent=2)+'\n')
    cards=[]
    for b in brands:
        status,description,action=intake_copy(b)
        cards.append('<a class="intake-card" href="'+b['profile_path']+'" aria-label="查看'+e(b['name'],quote=True)+'品牌资料">'+brand_mark(b)+'<span class="intake-status">'+e(status)+'</span><h3>'+e(b['name'])+'</h3><p>'+e((b['english_name'] or '品牌资料')+' · '+description)+'</p><span class="intake-cta">'+e(action)+' <span>→</span></span></a>')
    section='<section class="section brand-intake-section" id="brand-intake"><div class="sectionhead"><div><span class="overline">NEW BRAND ENTRANCES</span><h2>新增品牌，逐步补全资料。</h2><p>飞v已补充9款套餐、fly20八折优惠（续费、重置包除外，不叠加）与晚高峰延迟记录；梯子云已整理9款套餐、2hy85八五折优惠（年付保活、3款买断除外，不叠加），并列明客户端、流量规则、技术问题退款条件与50节点下午截图。浪网已整理9款套餐、lw888八折优惠、BGP与年付IPLC说明及60节点午间记录，并列明四端教程、支付宝、流量规则与24小时技术问题退款条件；周期续费与五款普通周期重置包可用该码，不能叠加其他优惠。另有11月3日19点上海电信、新加坡节点的ChatGPT问答反馈。</p></div></div><div class="intake-grid">'+''.join(cards)+'</div></section>'
    for filename in ['index.html','brands.html']:
        p=root/filename; html=p.read_text(encoding='utf-8')
        html=re.sub(r'<section class="section brand-intake-section".*?</section>','',html,flags=re.S)
        html=html.replace('</main>',section+'</main>',1)
        if 'href="assets/brand-intake.css"' not in html:html=html.replace('</head>','<link rel="stylesheet" href="assets/brand-intake.css"></head>',1)
        write_changed(p,html)
