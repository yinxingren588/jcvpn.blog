"""Publish FlyV's supplied prices as readable text, without the source screenshots."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e
from io import StringIO
from pathlib import Path
import csv
import json

from site_chrome import shell, write_changed
from flyv_latency import build_latency_assets, render_latency, latency_faqs
from flyv_clients import render_clients, client_faqs
from flyv_service import render_service, render_refund, service_faqs
from flyv_coupon import discounted_price, validate_coupon, render_coupon, coupon_faqs, coupon_rules, coupon_price_label
from flyv_access import render_access, access_faqs
from flyv_coverage import render_coverage, coverage_faqs


def money(value):
    return format(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'.2f')


def build_flyv_profile(root,brand):
    root=Path(root)
    data=json.loads((root/brand['plans_path']).read_text(encoding='utf-8'))
    latency=json.loads((root/brand['latency_path']).read_text(encoding='utf-8'))
    coverage=json.loads((root/brand['coverage_path']).read_text(encoding='utf-8'))
    clients=json.loads((root/brand['clients_path']).read_text(encoding='utf-8'))
    rules=json.loads((root/brand['service_rules_path']).read_text(encoding='utf-8'))
    coupon=json.loads((root/brand['coupon_path']).read_text(encoding='utf-8'))
    access=json.loads((root/brand['access_records_path']).read_text(encoding='utf-8'))
    validate_coupon(coupon,data['plans'])
    build_latency_assets(root,latency)
    url=e(brand['url'],quote=True)
    kinds={'annual':'轻量年付','monthly':'月付报价','one_time':'不限时总流量','custom':'独享专线'}
    cards=[];rows=[]
    for p in data['plans']:
        after_coupon=discounted_price(p,coupon)
        if p['kind']=='annual':
            billing='券后全年支付 ¥'+money(after_coupon)+'，折合约 ¥'+money(after_coupon/12)+'/月；按年购买'
        elif p['kind']=='monthly':billing='4个付款周期可选，本页只列已提供的月价'
        elif p['kind']=='one_time':billing='一次购买总流量，按累计消耗使用'
        else:billing='独立原生公网IP · 独享带宽'
        features=''.join('<li>'+e(text)+'</li>' for text in p['features'])
        cards.append('<article class="flyv-plan" id="flyv-plan-'+p['id']+'" data-flyv-kind="'+p['kind']+'"><span class="flyv-plan-kind">'+kinds[p['kind']]+'</span><h3>'+e(p['name'])+'</h3><p class="flyv-original-price">资料原价 <s>¥'+money(p['price_cny'])+'/'+e(p['payment_unit'])+'</s></p><span class="flyv-discount-label">'+e(coupon_price_label(coupon))+'</span><p class="flyv-plan-price"><strong>¥'+money(after_coupon)+'</strong><span>/'+e(p['payment_unit'])+'</span></p><p class="flyv-billing-note">'+e(billing)+'</p><dl class="flyv-plan-metrics"><div><dt>'+e(p['quota_scope'])+'</dt><dd>'+e(p['traffic_display'])+'</dd></div><div><dt>速度政策</dt><dd>不限速</dd></div><div><dt>设备数量</dt><dd>不限</dd></div></dl><p class="flyv-plan-audience">'+e(p['audience'])+'</p><ul>'+features+'</ul><p class="flyv-reset">'+e(p['reset_rule'])+'</p><a class="flyv-plan-action" href="'+url+'" target="_blank" rel="sponsored noopener noreferrer">'+('咨询独享方案' if p['kind']=='custom' else '查看官网套餐')+' <span aria-hidden="true">↗</span></a></article>')
        rows.append('<tr><th scope="row"><a href="#flyv-plan-'+p['id']+'">'+e(p['name'])+'</a></th><td>¥'+money(p['price_cny'])+'/'+e(p['payment_unit'])+'</td><td class="flyv-table-discount">¥'+money(after_coupon)+'/'+e(p['payment_unit'])+'</td><td>'+e(p['traffic_display']+' · '+p['quota_scope'])+'</td><td>'+e('、'.join(p['available_cycles']))+'</td><td>'+e(p['reset_rule'])+'</td></tr>')
    questions=[
        ('飞v共有几款套餐，原价分别是多少？','本页整理9款资料原价：年付标准轻量版99元/年；入门25元/月、进阶50元/月、高端110元/月、商业190元/月；三款一次性流量包分别188元、479元与799元；原生IP·独享黄金专线680元/月。9款套餐的用券价格另列在卡片和对照表中；续费订单与流量重置包除外，不能叠加其他优惠。'),
        ('99元年付的65GB是全年总流量吗？','不是。99元是12个月订阅的原价，使用fly20八折后为79.20元/年；65GB是每月额度，每月重置，未用完流量不结转。年费折合每月只作预算换算，仍需全年支付；续费不能使用fly20，续费订单金额需核对后台。'),
        ('四款月付还有哪些付款周期？','入门、进阶、高端和商业均显示月付、季付、半年付、年付选项。本次只提供25、50、110和190元的月价，其他周期金额需核对官网，不按月价乘月份或套折扣推算。'),
        ('一次性流量包会每月自动补流量吗？','不会。130GB、380GB和600GB分别是整包总额度，不按月清零或重新增加，按累计使用消耗，用完为止。资料标注流量永久有效，这里保留的是该流量期限说明。'),
        ('进阶方案和标准流量包都是380GB，有什么区别？','进阶为50元/月、每月380GB；单次标准流量包为479元一次性、380GB总额度。两者付款周期与流量范围不同，不应只按380GB这个数字比较。'),
        ('独享黄金专线的价格和配置是什么？','采用站长补充确认的680元/月，包含每月500GB专属流量、独立原生公网IP和独享带宽。资料列明1对1技术协助，预计约2—3个工作日交付，具体部署要求通过工单沟通。'),
        ('飞v是否所有套餐均为IPLC、IEPL或同一种协议？','不能从本批资料这样推定。进阶列明BGP三网调度搭配IEPL/IPLC传输；高端与商业分别列明多线路调度或冗余专线出口，进阶、高端、商业另列Shadowsocks。其他套餐按各自说明阅读。'),
        ('资料中的平台支持与不限速是否已经实测？','平台支持与不限速来自套餐资料。本页另列2026年11月12日19点上海电信的60个节点延迟记录，以及站长使用新加坡节点完成ChatGPT问答的反馈，两类记录分别注明条件。尚未提供下载速度或连续播放记录，不能由延迟数值或一次问答推断这些任务结果。四端使用流程、周期套餐、技术问题退款规则及fly20八折优惠已由站长逐项确认。')
    ]+coupon_faqs(coupon)+coverage_faqs(coverage)+latency_faqs(latency)+access_faqs(access)+client_faqs(clients)+service_faqs(rules,coupon)
    faq=''.join('<details class="flyv-faq"><summary>'+e(q)+'</summary><p>'+e(answer)+'</p></details>' for q,answer in questions)
    body='''<section class="info-hero flyv-hero" id="flyv-about"><span class="info-kicker">FLYV / PLANS & QUOTAS</span><div class="flyv-brand-heading"><img src="'''+e(brand['logo_path'],quote=True)+'''" width="1024" height="1024" alt="飞vLogo" decoding="async"><div><h1>飞v FlyV</h1><p>从轻量年付，到月度用量与独享部署。</p></div></div><p>按已提供资料整理9款套餐：1款轻量年付、4款月付报价、3款一次性总流量包，以及1款独享黄金专线。先分清付款周期和额度范围，再比较适合自己的方案。</p><div class="contact-buttons"><a class="contact-action" href="#flyv-plans">查看9款套餐 →</a><a class="copy-contact" href="'''+url+'''" target="_blank" rel="sponsored noopener noreferrer">访问飞v推广入口 ↗</a></div><p class="flyv-source-date">资料由博客站长提供 · 整理日期：'''+data['provided_on']+'''</p></section>
<nav class="flyv-jumps" aria-label="飞v页面重点内容"><a href="#flyv-coupon">八折优惠</a><a href="#flyv-plans">套餐文字卡片</a><a href="#flyv-comparison">价格对照表</a><a href="#flyv-guide">如何选择</a><a href="#flyv-coverage">节点覆盖</a><a href="#flyv-latency">晚高峰延迟</a><a href="#flyv-access">ChatGPT反馈</a><a href="#flyv-clients">使用教程</a><a href="#flyv-service">流量规则</a><a href="#flyv-refund">技术问题退款</a><a href="#flyv-faq">常见问题</a><a href="#flyv-sources">资料来源</a></nav>
<section class="section" id="flyv-plans"><span class="overline">9 PLANS / SUPPLIED PRICES</span><h2>九款套餐，价格与额度逐项看清。</h2><p class="flyv-section-lead">下方为文字整理的套餐卡片。年付按年支付、按月刷新；一次性包按总量消耗；独享方案另列资源和交付说明。</p><div class="flyv-plan-grid">'''+''.join(cards)+'''</div><p class="flyv-material-note">卡片中的不限速、设备数量和平台支持取自套餐资料；具体节点、兼容情况与实际使用表现应在相应环境下核对。</p></section>
<section class="section" id="flyv-comparison"><span class="overline">COMPARE BILLING & QUOTAS</span><h2>飞v套餐价格对照表</h2><div class="flyv-table-wrap" role="region" aria-label="飞v9款套餐对比表，可横向滚动" tabindex="0"><table><caption>'''+data['provided_on']+'''资料原价与fly20八折后价格；独享方案原价采用站长确认的680元/月。续费订单和流量重置包不适用该码，不能叠加优惠。</caption><thead><tr><th scope="col">套餐</th><th scope="col">资料原价</th><th scope="col">fly20 八折后</th><th scope="col">流量与范围</th><th scope="col">付款选项</th><th scope="col">刷新或使用规则</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><p class="flyv-material-note">券后价按所列报价×0.8计算，当前在售与结算金额请核对官网。季度、半年与全年价格未提供时保留空缺，不推算。<a href="data/feiv-plans.csv" download>下载含原价和券后价的套餐表 CSV ↓</a></p></section>
<section class="section" id="flyv-guide"><span class="overline">CHOOSE BY YOUR USAGE</span><h2>按用量和付款方式选择</h2><div class="flyv-guide-grid"><article><h3>轻量持续使用</h3><p>年付标准轻量版原价99元/年，fly20八折后79.20元/年，折合约6.60元/月，全年支付，每月65GB。先确认月用量是否在额度内，再看年付安排。</p></article><article><h3>每月固定用量</h3><p>入门、进阶、高端和商业分别提供150GB、380GB、800GB与1.8TB月度额度，八折后月价为20、40、88与152元。以近期实际消耗作参考，比较相应档位。</p></article><article><h3>间歇使用或备用</h3><p>130GB、380GB与600GB一次性包八折后分别为150.40、383.20与639.20元，按累计用量安排。整包额度不随月份自动增加。</p></article><article><h3>独立资源与业务部署</h3><p>独享黄金专线原价680元/月，八折后544元/月，每月500GB。资料列明独立原生公网IP与独享带宽，定制要求通过工单确认，预计约2—3个工作日交付。</p></article></div></section>
<section class="section" id="flyv-faq"><span class="overline">FLYV QUESTIONS & ANSWERS</span><h2>飞v套餐常见问题</h2>'''+faq+'''</section>
<section class="section" id="flyv-sources"><span class="overline">SOURCES & UPDATES</span><h2>资料来源与后续补充</h2><p class="flyv-section-lead">本页依据站长提供的6张套餐截图及独享方案价格确认，整理为文字卡片和对照表。原套餐照片不放入网页；飞v Logo 使用站长另行提供的图片。</p><p class="flyv-section-lead">已列明的线路、协议、流量和使用方向按套餐分别保留。客户端名称与下载流程、节点地区清单、支付方式、优惠及重置、续费、升级和退款规则尚待提供，后续按飞v自身资料补充。</p><div class="flyv-source-links"><a href="data/feiv-plans.json">9款套餐源资料 JSON ↓</a><a href="data/feiv-plans.csv" download>套餐对照表 CSV ↓</a><a href="topic-budget-guide.html">预算与付款周期选择 →</a><a href="topic-recommendations.html">机场推荐与选择方法 →</a><a href="brands.html">返回品牌目录 →</a></div></section>'''
    # Keep bookmarks to the original five sections valid after inserting the chart.
    original_headings=['九款套餐，价格与额度逐项看清。','飞v套餐价格对照表','按用量和付款方式选择','飞v套餐常见问题','资料来源与后续补充']
    for index,title in enumerate(original_headings,1):
        body=body.replace('<h2>'+title+'</h2>','<h2 id="quick-section-'+str(index)+'">'+title+'</h2>',1)
    for grid in ('flyv-plan-grid','flyv-guide-grid'):
        body=body.replace('<div class="'+grid+'">','<p class="flyv-material-note">'+e(coupon_rules(coupon))+'</p><div class="'+grid+'">',1)
    body=body.replace('<section class="section" id="flyv-plans">',render_coupon(coupon)+'\n<section class="section" id="flyv-plans">',1)
    body=body.replace('<section class="section" id="flyv-faq">',render_coverage(coverage)+'\n'+render_latency(latency)+'\n'+render_access(access)+'\n'+render_clients(clients,brand['url'])+'\n'+render_service(rules,coupon)+render_refund(rules,brand['url'])+'\n<section class="section" id="flyv-faq">',1)
    body=body.replace('客户端名称与下载流程、节点地区清单、支付方式、优惠及重置、续费、升级和退款规则尚待提供，后续按飞v自身资料补充。','另按站长提供的6张新截图整理2026年11月12日19点上海电信的节点延迟，重复卡片去重，超时独立保留。ChatGPT记录为站长针对当次新加坡节点问答逐项确认的反馈，本站未独立复测。Windows、macOS与安卓的飞v客户端流程，以及iOS Nextin的flyv识别码、下载与登录连接流程，均由站长逐项确认。普通周期套餐的重置、续费和升级规则，以及购买后24小时内的技术问题退款条件与后台客服入口，均已确认；付款已确认支持支付宝。优惠码fly20八折、9款套餐适用、无到期限制亦已确认；站长于2026年11月3日另确认续费订单及流量重置包不适用，也不能叠加其他优惠。完整节点地区与数量已由站长另行确认，共5个地区、60个节点。具体客户端版本按后续资料补充。',1)
    payment_badge='<span class="flyv-payment-badge" id="flyv-payment">支持'+e('、'.join(rules['payment_methods']))+'付款</span>'
    body=body.replace('访问飞v推广入口 ↗</a></div>','访问飞v推广入口 ↗</a>'+payment_badge+'</div>',1)
    html=shell('飞v FlyV套餐与晚高峰节点延迟','飞v9款套餐及晚高峰上海电信节点延迟记录。',body)
    styles='<link rel="stylesheet" href="assets/flyv.css"><link rel="stylesheet" href="assets/invisible-latency.css"><link rel="stylesheet" href="assets/flyv-latency.css"><link rel="stylesheet" href="assets/flyv-access.css"><link rel="stylesheet" href="assets/flyv-coverage.css">'
    html=html.replace('</head>',styles+'</head>',1)
    html=html.replace('</body>','<script src="assets/flyv-latency.js" defer></script><script src="assets/flyv-coupon.js" defer></script></body>',1)
    write_changed(root/brand['profile_path'],html)
    output=StringIO(newline='');writer=csv.writer(output,lineterminator='\n')
    writer.writerow(['套餐','资料原价（元）','优惠码','折扣','券后价格（元）','付款单位','流量原单位','流量范围','付款周期选项','刷新说明','资料日期','优惠有效期','使用限制','优惠规则更新日期'])
    for p in data['plans']:
        writer.writerow([p['name'],money(p['price_cny']),coupon['coupon']['code'],coupon['coupon']['display_discount'],money(discounted_price(p,coupon)),p['payment_unit'],p['traffic_display'],p['quota_scope'],'/'.join(p['available_cycles']),p['reset_rule'],data['provided_on'],coupon['coupon']['expiry_policy'],coupon_rules(coupon),coupon.get('updated_on',coupon['confirmed_on'])])
    write_changed(root/'data/feiv-plans.csv','\ufeff'+output.getvalue())
