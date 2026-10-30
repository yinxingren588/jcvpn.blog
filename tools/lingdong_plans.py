"""Render Lingdong's supplied plans without importing another brand's service rules."""
import csv
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e
from io import StringIO
from lingdong_coupon import discounted, coupon_box


def money(value):
    return format(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP),'.2f')


def plan_faqs(data):
    return [
        ('灵动云目前有哪些套餐，原价是多少？','本页整理9款原价：拂风20元/月、100GB；驭浪50元/月、300GB；破晓100元/月、700GB；凌霄180元/月、1500GB；穿云99元/年、70GB每30天刷新。另有闲云199元/150GB、惊云499元/400GB、飞云899元/800GB一次性流量包，以及680元/月、500GB的至尊私人定制。'),
        ('穿云99元年付，折合每月多少钱？70GB是全年总量吗？','99元除以12，折合约8.25元/月，但实际按年支付99元。70GB不是全年总量，截图明确从购买日起每30天自动刷新。'),
        ('拂风、驭浪、破晓、凌霄还有哪些付款周期？','截图提供月付、季付、半年付、年付4个周期选项。本次只提供20、50、100、180元的月价，其他周期的实际价格需到后台核对，不按月价直接推算。'),
        ('闲云、惊云、飞云会每月自动补流量吗？','不会。150GB、400GB、800GB是一次购买获得的总额度，无固定流量使用期限，用完为止；不是每月新增相同额度。这里说明流量使用规则，不额外承诺服务永久持续。'),
        ('灵动云私人定制包含什么配置？','图示680元/月，包含每月500GB专线独享流量、独立带宽与独立公网IP，资源不与他人共享。面向独立站、TikTok直播及跨境定制业务，不扩写为住宅IP。'),
        ('至尊私人定制需要多久交付，怎样沟通需求？','资料列明下单后约2—3个工作日交付，配有专人技术维护，特殊需求通过工单沟通。具体部署配置和进度以双方确认内容为准。'),
        ('穿云的IPLC与品牌BGP线路说明怎样看？','品牌介绍保留BGP多网专线；穿云已由站长确认采用IPLC专线，截图列明单节点峰值最高2.5Gbps。本页按对应资料分别记录，不把单款套餐规格扩展至全品牌，也不将峰值当作每名用户持续获得的下载速度。'),
        ('灵动云周期套餐什么时候刷新流量？','穿云明确从购买日起每30天自动刷新70GB。其余四款按每月额度列明，本次截图没有提供具体刷新日期；定制方案的刷新与部署配置通过工单确认。')
    ]


def render_plans(data,url,coupon):
    cards=[]
    rows=[]
    for p in data['plans']:
        annual=p['id']=='chuanyun-year'
        once=p['kind']=='one_time'
        custom=p['kind']=='custom'
        label='轻量年付' if annual else ('不限时总流量' if once else ('独享定制' if custom else '周期订阅'))
        extra='年付折合约 <b>¥'+money(Decimal(str(p['price_cny']))/12)+'/月</b>' if annual else ('一次购买 · 用完为止' if once else ('独立公网IP · 独立带宽' if custom else '月付报价 · 4个周期可选'))
        refresh='购买日起每30天刷新' if annual else ('不按月自动补充' if once else ('刷新与部署配置通过工单确认' if custom else '具体刷新日期请核对后台'))
        delivery='<p class="lingdong-delivery">'+e(p['delivery_note'])+'</p>' if custom else ''
        sale=discounted(p,coupon)
        coupon_html=('<p class="lingdong-plan-coupon-excluded">本套餐不适用'+e(coupon['code'])+'八折码</p>' if sale is None else '<p class="lingdong-plan-coupon-price"><span>'+e(coupon['code'])+' 八折后</span><strong>¥'+money(sale)+'<small>/'+e(p['payment_unit'])+'</small></strong></p>')
        sale_cell=('<span class="lingdong-coupon-excluded-cell">不适用</span>' if sale is None else '¥'+money(sale)+'/'+e(p['payment_unit']))
        classes=(' is-annual' if annual else '')+(' is-once' if once else '')+(' is-custom' if custom else '')
        cards.append(f'<article class="lingdong-plan{classes}" id="lingdong-plan-{p["id"]}" data-lingdong-kind="{p["kind"]}"><span class="lingdong-plan-label">{label}</span><h3>{e(p["name"])}</h3><p class="lingdong-plan-price"><span>原价</span><strong>¥{money(p["price_cny"])}</strong><span>/{e(p["payment_unit"])}</span></p><p class="lingdong-plan-extra">{extra}</p>{coupon_html}<div class="lingdong-plan-quota"><span>{e(p["quota_scope"])}</span><strong>{p["traffic_gb"]:,}<small>GB</small></strong></div><p class="lingdong-plan-reset">{refresh}</p><p class="lingdong-plan-audience">{e(p["audience"])}</p><p class="lingdong-plan-detail">{e(p["detail"])}</p>{delivery}<a class="lingdong-plan-action" href="{url}" target="_blank" rel="sponsored noopener noreferrer">'+('了解定制方案' if custom else '查看套餐入口')+' <span aria-hidden="true">↗</span></a></article>')
        rows.append(f'<tr><th scope="row"><a href="#lingdong-plan-{p["id"]}">{e(p["name"])}</a></th><td>¥{money(p["price_cny"])}/{e(p["payment_unit"])}</td><td>{sale_cell}</td><td>{p["traffic_gb"]:,}GB · {e(p["quota_scope"])}</td><td>{e(p["reset_rule"])}</td></tr>')
    return f'''<section class="section" id="lingdong-plans"><div class="lingdong-section-title"><span class="overline">9 PLANS / QUOTA & BILLING</span><h2>按用量与周期，选择灵动套餐。</h2><p>4款月付报价、1款轻量年付、3款一次性流量包与1款私人定制，分别列明付款周期和流量范围。</p></div><div class="lingdong-plan-filters" role="group" aria-label="按灵动套餐类型筛选"><button type="button" data-lingdong-filter="all" aria-pressed="true">全部 <span>9</span></button><button type="button" data-lingdong-filter="periodic" aria-pressed="false">周期套餐 <span>5</span></button><button type="button" data-lingdong-filter="one_time" aria-pressed="false">不限时流量 <span>3</span></button><button type="button" data-lingdong-filter="custom" aria-pressed="false">私人定制 <span>1</span></button></div><p class="lingdong-plan-count" id="lingdong-plan-count" role="status" aria-live="polite">全部套餐 · 共9款</p><div class="lingdong-plan-grid">{''.join(cards)}</div><div class="lingdong-plan-notes"><h3>付款周期与流量额度，分开比较。</h3><p>拂风、驭浪、破晓、凌霄分别提供100GB、300GB、700GB、1500GB月度额度；图片有4个付款周期选项，本页列出已提供的月价。穿云按年支付99元，70GB从购买日起每30天刷新。</p><p>闲云、惊云、飞云分别是150GB、400GB、800GB一次性总流量，按累计使用消耗。至尊私人定制另行列明每月500GB独享流量、独立公网IP和独立带宽。</p></div></section>
<section class="section" id="lingdong-plan-comparison"><div class="lingdong-section-title"><span class="overline">COMPARE PRICE, QUOTA & RESET</span><h2>9款套餐，放在同一张表中比较。</h2><p>月度额度、每30天额度和一次性总流量分别标注。</p></div><div class="lingdong-table-wrap" tabindex="0" role="region" aria-label="灵动云9款套餐对比，可横向滚动"><table class="lingdong-plan-table"><caption>灵动云9款套餐 · {data['provided_on']}整理</caption><thead><tr><th scope="col">套餐</th><th scope="col">原价</th><th scope="col">八折码后</th><th scope="col">流量范围</th><th scope="col">刷新说明</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="lingdong-note">价格与额度依据站长提供的套餐图片整理，实际在售与配置请核对官网。<a href="data/lingdongyun-plans.csv" download>下载完整套餐表 CSV ↓</a></p></section>
<section class="section" id="lingdong-plan-guide"><div class="lingdong-section-title"><span class="overline">FIND YOUR OWN USAGE PATTERN</span><h2>先看实际用量，再决定付款方式。</h2></div><div class="lingdong-plan-guide"><article><span>每月持续使用</span><h3>从100GB到1500GB，比较月度用量。</h3><p>以最近一个月的实际用量为参考，再比较拂风、驭浪、破晓和凌霄。偏好轻量年付时，可比较穿云70GB每30天、99元/年的安排。</p></article><article><span>使用频率不固定</span><h3>比较一次购买的总额度。</h3><p>闲云、惊云和飞云适合按累计消耗安排预算。150GB、400GB、800GB不会因为月份增加而自动补充，需要结合长期总用量选择。</p></article><article><span>独立部署需求</span><h3>通过工单确认定制配置。</h3><p>至尊私人定制列明独立公网IP、独立带宽与每月500GB独享流量。独立站、直播等业务可先沟通部署需求与交付进度。</p></article></div></section>'''


def render_floating(data,url,coupon,logo_image):
    p=next(x for x in data['plans'] if x['id']=='chuanyun-year')
    monthly=money(Decimal(str(p['price_cny']))/12)
    return f'''<aside class="floating-promo" id="lingdong-floating-promo" data-open="auto" aria-label="灵动云套餐推荐"><section class="fp-panel" id="lingdong-floating-panel" aria-label="灵动云穿云年付推荐"><div class="fp-handle" title="拖动移动推荐卡"><span class="fp-grip" aria-hidden="true">⠿</span><span class="fp-label">轻量年付</span><div class="fp-window-actions"><button type="button" class="fp-reset" aria-label="恢复灵动推荐卡默认位置" title="恢复默认位置">↺</button><button type="button" class="fp-close" aria-label="收起灵动推荐卡" title="收起">×</button></div></div><div class="fp-content"><a class="fp-brand" href="#lingdong-about">{logo_image}<span><strong>灵动云</strong><small>日常连接方案</small></span></a><div class="fp-plan"><span class="fp-eyebrow">推荐套餐 · 轻量年付</span><h2>灵动·穿云</h2><div class="fp-traffic"><strong>{p['traffic_gb']}<small>GB</small></strong><span>每30天刷新</span></div></div><div class="fp-pricing"><div><small>年付折算约</small><strong>¥{monthly}</strong><span>/月</span></div><p class="fp-annual-total">实际按年支付 ¥{money(p['price_cny'])}/年</p></div><p class="lingdong-floating-exclusion">穿云不适用八折码，保持原价</p>{coupon_box(coupon,floating=True)}<a class="lingdong-float-details" href="#lingdong-plans" data-lingdong-show-all>对比全部9款套餐 →</a><a class="fp-cta" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往灵动云查看 <span aria-hidden="true">↗</span></a><p class="fp-note">购买日起每30天刷新70GB，实际按年付款。</p></div></section><button type="button" class="fp-launcher" aria-controls="lingdong-floating-panel" aria-expanded="false" aria-label="展开灵动套餐推荐">{logo_image}<span>灵动套餐</span><span aria-hidden="true">＋</span></button></aside>'''


def plans_csv(data,coupon):
    stream=StringIO(newline='')
    writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['套餐','原价（元）','付款单位','八折码后价格（元）','优惠码适用','流量（GB）','流量范围','付款周期选项','刷新说明','交付说明','资料日期'])
    for p in data['plans']:
        sale=discounted(p,coupon)
        writer.writerow([p['name'],p['price_cny'],p['payment_unit'],money(sale) if sale is not None else '',coupon['code']+'八折' if sale is not None else '不适用',p['traffic_gb'],p['quota_scope'],'/'.join(p['available_cycles']),p['reset_rule'],p.get('delivery_note',''),data['provided_on']])
    return '\ufeff'+stream.getvalue()


def plans_markdown(data,coupon):
    text='## 套餐与流量\n\n来源：'+data['source']+'。整理日期：'+data['provided_on']+'。原图片只作整理来源。\n\n'
    for p in data['plans']:
        text+='### '+p['name']+'\n\n¥'+money(p['price_cny'])+'/'+p['payment_unit']+'；'+str(p['traffic_gb'])+'GB · '+p['quota_scope']+'。\n\n'+p['detail']+'\n\n'+p['reset_rule']+'\n\n'
        sale=discounted(p,coupon)
        text+=('不适用'+coupon['code']+'，保持原价。' if sale is None else coupon['code']+'八折后：¥'+money(sale)+'/'+p['payment_unit']+'。')+'\n\n'
        if p.get('delivery_note'):
            text+=p['delivery_note']+'\n\n'
    return text+'不推算未提供报价的其他付款周期售价或优惠价。穿云不适用八折码，保持99元/年，折合8.25元/月。\n\n'
