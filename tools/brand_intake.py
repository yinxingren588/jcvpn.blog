"""Publish confirmed brand entrances without inventing service facts."""
import json
import re
from html import escape as e
from pathlib import Path
from site_chrome import shell,write_changed

def build_brand_intake(root):
    root=Path(root)
    source=json.loads((root/'data/new-brands.json').read_text(encoding='utf-8'))
    pending=source['brands']
    catalog=json.loads((root/'data/brands.json').read_text(encoding='utf-8'))
    by_id={b['id']:b for b in catalog['brands']}
    for b in pending:
        by_id[b['id']]={**by_id.get(b['id'],{}),**b,'source_type':source['source'],'source_date':source['confirmed_on'],'verification_status':'entry_provided_details_pending','commercial_relationship':'推广入口；具体合作条件未提供'}
        name=b['name']+(' '+b['english_name'] if b['english_name'] else '')
        body='<section class="info-hero intake-hero"><span class="info-kicker">BRAND PROFILE / IN PROGRESS</span><span class="intake-status">入口已收录 · 资料补充中</span><h1>'+e(name)+'</h1><p>本站已收录站长确认的'+e(b['name'])+'推广入口。套餐价格、流量规则、客户端与使用记录将按后续提供的资料逐项整理。</p><div class="contact-buttons"><a class="contact-action" href="'+e(b['url'],quote=True)+'" target="_blank" rel="sponsored noopener noreferrer">访问'+e(b['name'])+'推广入口 ↗</a><a class="copy-contact" href="brands.html">查看全部品牌 →</a></div></section><nav class="info-breadcrumb" aria-label="当前位置"><a href="index.html">首页</a><span>/</span><a href="brands.html">品牌介绍</a><span>/</span><span>'+e(b['name'])+'</span></nav><section class="info-section"><h2>目前已确认的资料</h2><dl class="intake-facts"><div><dt>品牌名称</dt><dd>'+e(name)+'</dd></div><div><dt>入口来源</dt><dd>博客站长提供，2026-11-02收录；此链接为推广入口。</dd></div><div><dt>套餐与价格</dt><dd>待提供，不沿用其他品牌的金额或优惠。</dd></div><div><dt>客户端与节点</dt><dd>待提供，不预填线路、识别码或节点数量。</dd></div></dl></section><section class="info-section"><h2>选择前先核对什么</h2><p>先确认付款周期、流量额度、刷新方式、设备要求与售后条件，再对照自己的使用任务。当前页面仅提供已确认入口，尚未形成性能评价。</p><p><a href="topic-recommendations.html">阅读机场推荐与梯子推荐指南 →</a>　<a href="article-plan-comparison-sheet.html">查看套餐比较方法 →</a></p></section>'
        html=shell(name+'品牌入口与资料',name+'品牌推广入口已收录；套餐、客户端和节点资料正在补充。',body)
        html=html.replace('</head>','<link rel="stylesheet" href="assets/brand-intake.css"></head>',1)
        write_changed(root/b['profile_path'],html)
    catalog['brands']=list(by_id.values())
    catalog['updated_on']=source['confirmed_on']
    write_changed(root/'data/brands.json',json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    policy={'noindex_pages':{b['profile_path']:'仅确认品牌名与入口；补齐实质资料后再开放索引' for b in pending}}
    write_changed(root/'data/indexing-policy.json',json.dumps(policy,ensure_ascii=False,indent=2)+'\n')
    cards=''.join('<a class="intake-card" href="'+b['profile_path']+'"><span class="intake-mark" aria-hidden="true">'+e(b['mark'])+'</span><span class="intake-status">入口已收录</span><h3>'+e(b['name'])+'</h3><p>'+e(b['english_name'] or '品牌资料')+' · 套餐与介绍陆续补充</p><span class="intake-cta">查看品牌页面 <span>→</span></span></a>' for b in pending)
    section='<section class="section brand-intake-section" id="brand-intake"><div class="sectionhead"><div><span class="overline">NEW BRAND ENTRANCES</span><h2>新增品牌，逐步补全资料。</h2><p>飞v、梯子云、浪网已收录推广入口；服务详情待逐项确认。</p></div></div><div class="intake-grid">'+cards+'</div></section>'
    for filename in ['index.html','brands.html']:
        p=root/filename; html=p.read_text(encoding='utf-8')
        html=re.sub(r'<section class="section brand-intake-section".*?</section>','',html,flags=re.S)
        html=html.replace('</main>',section+'</main>',1)
        if 'href="assets/brand-intake.css"' not in html:html=html.replace('</head>','<link rel="stylesheet" href="assets/brand-intake.css"></head>',1)
        write_changed(p,html)
