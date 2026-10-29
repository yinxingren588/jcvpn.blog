"""Render the Breezenet plan profile from attributed third-party materials."""
import csv
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e
from hashlib import sha256
import io
import json
from pathlib import Path
import re

from site_chrome import header, footer, write_changed


def coupon_price(plan, coupon):
    if not coupon or not (coupon.get('all_plans_applicable') or plan['id'] in coupon.get('confirmed_plan_ids', [])):
        return None
    return (Decimal(str(plan['price'])) * Decimal(coupon['pay_multiplier'])).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def faqs(data, latency=None, coupon=None, profile=None):
    questions = [
        ('微风网络的这批套餐分别多少钱？', '清风137元/年、乘风25元/月、破风55元/月、御风125元/月；信风·不限时为200元一次性、270GB总流量，长风·不限时为370元一次性、570GB总流量。价格来自本次第三方套餐资料，实际在售及结算金额以微风后台为准。'),
        ('清风年付的100GB，是全年总量还是每月额度？', '是每月100GB。截图写明年付价格137元、每月流量100GB，并注明从购买日起自动重置。年付是付款周期，月流量是额度周期，两者需要分开理解。'),
        ('清风折算约11.42元/月，是否可以每月只付11.42元？', '11.42元是137元除以12后得到的月均成本，便于比较；这份资料给出的实际支付方式是年付137元，不是11.42元的月付报价。'),
        ('乘风、破风和御风的主要区别是什么？', '已提供的月付价格及额度分别为：乘风25元、200GB；破风55元、500GB；御风125元、1,200GB。三款均在截图中标注全IPLC专线、不限设备同时接入及不限速；没有据此推断不同档位的实测速率或优先级。'),
        ('信风和长风的一次性流量会按月恢复吗？', '它们是一次性总额度：信风270GB、长风570GB，使用时按实际消耗扣减。截图写明不限时、用完为止，不能将其理解为每月新增或重置同样的流量。'),
        ('“不限时、流量不过期”应该怎样理解？', '按这批套餐资料，信风和长风没有固定的流量使用期限，额度消耗完即用完。这个表述说明流量包的有效期口径，不额外承诺服务本身会永久持续；具体服务条款以购买时页面为准。'),
        ('微风网络的套餐采用什么线路？', '本次两张第三方截图中的6款套餐均标注“全IPLC专线”。本页按原资料保留IPLC线路表述，没有将其他品牌的线路类型套用到微风，也不把线路名称当作实测速率证明。'),
        ('这些套餐限制设备同时接入数量吗？', '本次6款套餐的详情均写明“不限制设备同时接入”。该资料没有进一步提供账号共享、转售或其他使用条款，不将不限设备数扩写成允许任意共享账号。'),
        ('套餐写“不限速”，能否理解为固定速度？', '不能。“不限速”是原套餐的速率政策表述；实际连接体验仍需在具体设备、网络、节点和时段下验证。流量额度、线路类型与单次下载速度属于不同信息。'),
        ('为什么没有列出季付、半年付或其他周期价格？', '截图顶部虽出现按季、按半年等筛选项，但本次没有提供这些周期对应的套餐报价。本页只展示清晰可读的年付、月付与一次性价格，不用月付金额直接推算其他周期的实际售价。')
    ]
    if latency:
        questions += [
            ('微风网络有节点延迟记录吗？', '本页新增一批第三方截图记录：用户说明采样时间为2026-10-29 12:00（北京时间），上海电信，Windows版“微风网络”客户端。共52个节点，39条数值、13条超时；图表依据截图重绘，本站没有重新测量。'),
            ('为什么日本节点同时有超时和可用数值？', '截图中的日本01—10本次均为超时；名称明确带“直连”的日本01—04显示57、64、58、58ms。本页将两组分开，不把直连记录用来代替前10个节点，也不凭截图推断具体网络故障原因。'),
            ('为什么明细里没有香港13？', '这批资料展示香港01—12及香港14，没有展示香港13。本页只记录可见节点；未展示不等于已确认超时、下线或不存在。'),
            ('图表中的ms能否换算为下载速度？', '不能直接换算。ms是这次客户端显示的延迟单位，下载或上传速度需要另行测量。每节点只有一条记录，也不能据此计算全天可用率或持续稳定性。')
        ]
    if coupon:
        plan = next(item for item in data['plans'] if item['id'] == 'breeze-year')
        annual = coupon_price(plan, coupon)
        monthly = (annual / Decimal(12)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        questions += [
            (f'清风套餐券后折算约{monthly}元/月，怎样计算？', f'清风是年付套餐，原价{plan["price"]}元/年，每月{plan["traffic_gb"]}GB。使用优惠码{coupon["code"]}{coupon["discount_label"]}后，按该原价计算为{annual}元/年；除以12折算约{monthly}元/月。这是年付月均成本，实际按年支付，不是同价的月付套餐。'),
            ('微风网络的优惠码是什么，如何使用？', f'本页优惠码为{coupon["code"]}，优惠力度为{coupon["discount_label"]}。清风套餐的适用情况已由站长确认；在微风后台购买时填写优惠码，核对结算金额后再支付。' + ('站长确认全部套餐适用。' if coupon.get('all_plans_applicable') else '其他套餐适用范围尚未确认。') + ('该优惠没有固定到期限制。' if coupon.get('expiry_rule') == 'no_fixed_expiry' else '有效期以购买时的活动规则为准。'))
        ]
    if profile:
        questions.append(('微风网络是否提供原生IP节点？', '根据博客站长于2026-10-29补充的资料，微风提供原生IP节点选择，面向关注IP属性的用户。本站尚未逐节点核验，不将原生IP扩写为独享IP、住宅IP或特定平台永久可用。'))
    return questions


def build_breezenet_profile(root):
    root = Path(root)
    data = json.loads((root / 'data/breezenet-plans.json').read_text(encoding='utf-8'))
    latency_path = root / 'data/breezenet-latency.json'
    latency_data = json.loads(latency_path.read_text(encoding='utf-8')) if latency_path.exists() else None
    profile_path = root / 'data/breezenet-profile.json'
    profile = json.loads(profile_path.read_text(encoding='utf-8')) if profile_path.exists() else None
    coupon_path = root / 'data/breezenet-coupon.json'
    coupon = json.loads(coupon_path.read_text(encoding='utf-8')) if coupon_path.exists() else None
    plans = data['plans']
    url = e(data['entry_url'], quote=True)
    labels = {'year': '年付 · 每月流量', 'month': '月付 · 每月流量', 'once': '一次性 · 总流量'}
    cards = []
    rows = []
    for plan in plans:
        kind = plan['billing']
        annual = (Decimal(str(plan['price'])) / Decimal(12)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        price_note = f'年付折算约{annual}元/月，实际年付{plan["price"]}元' if kind == 'year' else ('一次购买，按总额度逐步消耗' if kind == 'once' else '按月支付，按月提供对应额度')
        discounted = coupon_price(plan, coupon)
        if discounted is not None:
            price_note += f'；优惠码{coupon["code"]}{coupon["discount_label"]}后¥{discounted}/{plan["price_unit"]}'
        period = '一次性总流量' if kind == 'once' else '每月流量额度'
        english = e(plan['english_name'] or 'TRAFFIC PACK')
        cards.append(f'''<article class="breeze-plan" data-billing="{kind}" id="breeze-plan-{plan['id']}"><span class="breeze-plan-kind">{labels[kind]}</span><h3>{e(plan['name'])}</h3><span class="breeze-plan-english">{english}</span><p class="breeze-plan-tagline">{e(plan['tagline'])}</p><div class="breeze-price"><span>¥</span><strong>{plan['price']}</strong><small>/{e(plan['price_unit'])}</small></div><p class="breeze-price-note">{e(price_note)}</p><div class="breeze-quota"><div><strong>{plan['traffic_gb']:,}</strong><span>GB</span></div><small>{period}</small></div><p class="breeze-reset">{e(plan['reset_rule'])}</p><p class="breeze-plan-copy">{e(plan['description'])}</p><a class="breeze-plan-action" href="{url}" target="_blank" rel="sponsored noopener noreferrer" aria-label="前往微风入口查看{e(plan['name'], quote=True)}套餐">前往查看套餐 <span aria-hidden="true">↗</span></a></article>''')
        rows.append(f'''<tr><th scope="row">{e(plan['name'])}</th><td>¥{plan['price']} / {e(plan['price_unit'])}</td><td>{plan['traffic_gb']:,}GB<br>{period}</td><td>{e(plan['reset_rule'])}</td></tr>''')
    faq_items = ''.join('<details class="breeze-faq"><summary>' + e(question) + '</summary><p>' + e(answer) + '</p></details>' for question, answer in faqs(data, latency_data, coupon, profile))
    body = f'''<section class="breeze-hero"><div class="breeze-intro"><span class="overline">BREEZENET / PLANS & CONNECTION</span><div class="breeze-heading"><span class="breeze-mark" aria-hidden="true">B</span><div><h1>微风网络 Breezenet</h1><span class="breeze-english">选择流量，也选择适合自己的使用节奏</span></div></div><p>本页整理微风网络的6款套餐，覆盖年付、月付和一次性流量。周期套餐每月100GB至1,200GB，一次性套餐按270GB或570GB总量使用，方便按实际用量和付费方式选择。</p><div class="breeze-hero-actions"><a class="btn" href="#breeze-plans">查看6款套餐 <span aria-hidden="true">↓</span></a><a class="textlink" href="{url}" target="_blank" rel="sponsored noopener noreferrer">访问微风入口 ↗</a></div></div><aside class="breeze-spotlight" aria-label="清风套餐计费与流量示例"><span class="overline">PAYMENT ≠ TRAFFIC CYCLE</span><h2>年付金额与每月额度，<br>分开看更清楚。</h2><div class="breeze-sample"><div><small>清风 · 全年支付</small><strong>137<span>元 / 年</span></strong><small>折算约11.42元 / 月</small></div><div><small>清风 · 每月额度</small><strong>100<span>GB / 月</span></strong><small>购买日起按月重置</small></div></div><p>137元是年付金额，100GB是每月额度；一次性流量包则按整包总量扣减。</p></aside></section>
<nav class="breeze-jumps" aria-label="微风页面目录"><a href="#breeze-plans">套餐价格</a><a href="#breeze-comparison">快速对比</a><a href="#breeze-plan-guide">如何选择</a><a href="#breeze-faq">常见问题</a><a href="#breeze-sources">资料来源</a></nav>
<section class="section" id="breeze-plans" aria-labelledby="breeze-plans-title"><div class="breeze-section-title"><span class="overline">SIX PLANS / THREE BILLING OPTIONS</span><h2 id="breeze-plans-title">微风网络套餐价格与流量</h2><p>先选付费方式，再看每月额度或一次性总量。</p></div><p class="breeze-source-line">资料来源：第三方提供的2张套餐截图，经站长转交整理 · 整理日期：{data['updated_on']}</p><div class="breeze-shared-features"><span>IPLC专线 · 资料标注</span><span>不限设备同时接入</span><span>套餐标注不限速</span></div><div class="breeze-filters" role="group" aria-label="微风套餐类型"><button type="button" data-breeze-filter="all" aria-pressed="true">全部套餐 <span>6</span></button><button type="button" data-breeze-filter="year" aria-pressed="false">年付套餐 <span>1</span></button><button type="button" data-breeze-filter="month" aria-pressed="false">月付套餐 <span>3</span></button><button type="button" data-breeze-filter="once" aria-pressed="false">一次性流量 <span>2</span></button></div><p class="breeze-count" id="breeze-plan-count" aria-live="polite">全部套餐 · 共6款</p><div class="breeze-pricing-grid">{''.join(cards)}</div></section>
<section class="section" id="breeze-comparison"><div class="breeze-section-title"><span class="overline">COMPARE THE RIGHT NUMBERS</span><h2>把价格、额度和刷新规则放在一起看</h2><p>相同的GB数字，可能分别代表每月额度或整包总量。</p></div><div class="breeze-table-wrap" role="region" aria-label="微风6款套餐对比表" tabindex="0"><table class="breeze-table"><thead><tr><th scope="col">套餐</th><th scope="col">资料价格</th><th scope="col">流量口径</th><th scope="col">刷新或使用规则</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="breeze-reading-note">截图还出现按季、按半年等筛选项，但未提供对应报价。本页不据此补算未展示周期的售价；具体在售周期与金额以微风结算页为准。</p></section>
<section class="section" id="breeze-plan-guide"><div class="breeze-section-title"><span class="overline">MATCH YOUR USAGE</span><h2>按使用节奏，缩小选择范围</h2><p>以下是根据套餐额度整理的选择思路，不是速度排名。</p></div><div class="breeze-guide-grid"><article><h3>持续使用，每月用量较低</h3><p>可先看清风：137元年付、每月100GB。适合能接受年付周期，并预计自己的月度消耗在该额度内的情况。</p><a href="#breeze-plan-breeze-year">了解清风年付 →</a></article><article><h3>按月付费，按用量选择档位</h3><p>乘风、破风、御风分别提供每月200GB、500GB和1,200GB。先看自己已有的用量记录，再决定是否需要增加额度。</p><a href="#breeze-plan-riding-month">查看月付方案 →</a></article><article><h3>低频连接，或准备备用流量</h3><p>信风270GB和长风570GB按一次性总量消耗，资料写明不限时、用完为止。需要区分总额度与每月自动刷新的额度。</p><a href="#breeze-plan-trade-wind-once">了解一次性流量 →</a></article></div><p class="breeze-reading-note">流量额度不直接等于观看时长或下载速度；具体消耗受应用任务、清晰度、同步和后台流量等因素影响，可结合实际用量记录判断。</p></section>
<section class="section" id="breeze-faq"><div class="breeze-section-title"><span class="overline">BREEZENET QUESTIONS & ANSWERS</span><h2>微风网络套餐常见问题</h2><p>付款周期、流量周期与套餐表述，分别说明。</p></div><div class="breeze-faqs">{faq_items}</div></section>
<section class="section" id="breeze-sources"><div class="breeze-section-title"><span class="overline">SOURCES & REVISIONS</span><h2>资料来源与本次整理范围</h2></div><div class="breeze-source-grid"><div><h3>第三方套餐资料</h3><p>站长于{data['updated_on']}转交2张第三方截图，本页据其可见内容整理6款套餐价格、流量、IPLC线路及同时接入规则，未放入原照片。截图拍摄时间和提供者名称未单独提供。</p></div><div><h3>本站如何处理</h3><p>叮当观察负责文字编排、套餐对比与选择说明，未登录后台独立核价。实际在售、续费及服务条款以购买时页面为准；“不限速”不作为固定带宽或实测速度保证。</p></div></div><p class="breeze-reading-note">本次未提供微风的节点地区、客户端、优惠码及售后规则，本页没有使用其他品牌资料代填。外部入口保留站长提供的推广参数，访问会打开新窗口。</p><div class="breeze-source-links"><a href="data/breezenet-plans.json">查看套餐数据 JSON ↓</a><a href="data/breezenet-plans.csv" download>下载套餐对比 CSV ↓</a><a href="{url}" target="_blank" rel="sponsored noopener noreferrer">访问微风入口 ↗</a></div><div class="breeze-followup"><a href="brands.html">返回品牌目录 →</a><a href="topic-plans.html">阅读套餐与选择专题 →</a><a href="contact.html">反馈资料更新 →</a></div></section>'''
    description = '了解微风网络Breezenet的6款机场套餐，按年付、月付与一次性流量比较价格和额度。本文依据第三方资料整理IPLC专线、周期流量、设备同时接入与不限时方案，并说明年付100GB月流量及270GB、570GB一次性总额度的区别。'
    if latency_data:
        from breeze_latency import build_module as latency_html
        body = body.replace('<section class="section" id="breeze-plans"', latency_html(root) + '<section class="section" id="breeze-plans"', 1)
        body = body.replace('<nav class="breeze-jumps" aria-label="微风页面目录">', '<nav class="breeze-jumps" aria-label="微风页面目录"><a href="#peak-latency">延迟记录</a>', 1)
        body = body.replace('方便按实际用量和付费方式选择。</p>', '方便按实际用量和付费方式选择。另附10月29日12:00上海电信的第三方节点延迟记录，数值与超时分别展示。</p>', 1)
        body = body.replace('本次未提供微风的节点地区、客户端、优惠码及售后规则，本页没有使用其他品牌资料代填。', '套餐与延迟记录按各自资料来源分别整理；客户端使用方式、优惠活动和售后规则请以微风后台现行指引为准。')
        description = '查看微风网络Breezenet的6款套餐、IPLC线路资料及第三方节点延迟记录。2026年10月29日12:00，上海电信、Windows版微风网络客户端共记录52个节点，39条数值和13条超时，日本直连单列，并提供完整明细与图表下载。'
    if profile:
        introduction = e(profile['intro'])
        body = re.sub(r'(<div class="breeze-intro">.*?<p>).*?(</p>)', lambda match: match[1] + introduction + match[2], body, count=1, flags=re.S)
        audience_cards = ''.join('<article><h3>' + e(item['title']) + '</h3><p>' + e(item['description']) + '</p></article>' for item in profile['audiences'])
        about = '<section class="section" id="breeze-about"><div class="breeze-section-title"><span class="overline">BUILT AROUND YOUR USAGE</span><h2>大流量与性价比，面向更具体的连接需求。</h2><p>从使用量、节点IP需求和视频场景出发，了解微风网络的服务定位。</p></div><div class="breeze-guide-grid">' + audience_cards + '</div></section>'
        body = body.replace('<nav class="breeze-jumps" aria-label="微风页面目录">', '<nav class="breeze-jumps" aria-label="微风页面目录"><a href="#breeze-about">品牌介绍</a>', 1)
        body = body.replace('</nav>', '</nav>' + about, 1)
        body = body.replace('<div class="breeze-source-grid">', '<p class="breeze-source-line">品牌定位由博客站长于' + e(profile['updated_on']) + '补充；套餐和延迟记录按各自第三方资料整理，分别注明来源。</p><div class="breeze-source-grid">', 1)
        description = '微风网络Breezenet以大流量与性价比为定位，面向关注节点IP属性和4K视频使用需求的用户。页面整理IPLC专线、6款套餐价格与流量，以及上海电信Windows客户端的第三方延迟记录，便于按用量与场景了解服务。'
    if coupon:
        recommended = next(item for item in plans if item['id'] == 'breeze-year')
        annual_paid = coupon_price(recommended, coupon)
        monthly_paid = (annual_paid / Decimal(12)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        scope = '全部套餐适用' if coupon.get('all_plans_applicable') else '已确认清风套餐适用'
        expiry = '无固定到期限制' if coupon.get('expiry_rule') == 'no_fixed_expiry' else '使用时核对后台活动规则'
        spotlight = f'''<aside class="breeze-spotlight breeze-offer" aria-label="清风年付推荐与优惠码"><span class="breeze-offer-badge">清风 · 年付推荐</span><h2>每月100GB，<br>年付券后约{monthly_paid}元/月。</h2><div class="breeze-offer-price"><span>¥</span><strong>{monthly_paid}</strong><small>/月 · 年付折算</small></div><p class="breeze-offer-total">原价 <s>¥{recommended['price']}/年</s><span>{e(coupon['discount_label'])}</span>券后年付 <b>¥{annual_paid}</b></p><div class="breeze-coupon"><div><small>优惠码 · {e(coupon['discount_label'])}</small><code>{e(coupon['code'])}</code></div><button type="button" data-breeze-copy="{e(coupon['code'], quote=True)}" aria-label="复制微风优惠码">复制</button></div><p class="breeze-coupon-status" role="status" aria-live="polite"></p><p>{scope} · {expiry}。<br>每月100GB，购买日起按月重置；实际按年支付。</p><a class="breeze-plan-action" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往微风使用优惠码 <span aria-hidden="true">↗</span></a></aside>'''
        body = re.sub(r'<aside class="breeze-spotlight".*?</aside>', lambda _: spotlight, body, count=1, flags=re.S)
        body = body.replace('先选付费方式，再看每月额度或一次性总量。', '先选付费方式，再看每月额度或一次性总量。以下保留套餐原价，已确认的券后价格另行注明。', 1)
        body = body.replace('客户端使用方式、优惠活动和售后规则请以微风后台现行指引为准。', '优惠码由站长补充，结算金额以后台为准；客户端使用方式和售后规则请以微风后台现行指引为准。')
    page = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>微风网络 Breezenet｜套餐价格、IPLC线路与流量说明｜叮当观察</title><meta name="description" content="' + e(description, quote=True) + '"><link rel="stylesheet" href="assets/site-base.css"><link rel="stylesheet" href="assets/doraemon-theme.css"><link rel="stylesheet" href="assets/topics.css"><link rel="stylesheet" href="assets/breezenet.css"><script src="assets/breezenet.js" defer></script></head><body><div class="shell">' + header('brands') + '<main>' + body + '</main>' + footer() + '</div></body></html>'
    if latency_data:
        page = page.replace('套餐价格、IPLC线路与流量说明', '套餐价格、IPLC资料与节点延迟', 1)
        page = page.replace('<link rel="stylesheet" href="assets/breezenet.css">', '<link rel="stylesheet" href="assets/invisible-latency.css"><link rel="stylesheet" href="assets/breezenet.css"><script src="assets/invisible-latency.js" defer></script>', 1)
    for asset in ('breezenet.css', 'breezenet.js'):
        revision = sha256((root / 'assets' / asset).read_bytes()).hexdigest()[:12]
        page = page.replace(f'assets/{asset}"', f'assets/{asset}?v={revision}"')
    write_changed(root / 'brand-breezenet.html', page)
    # Keep card summaries in the home and directory consistent with the profile.
    for name in ('index.html', 'brands.html'):
        path = root / name
        text = path.read_text(encoding='utf-8')
        def update_card(match):
            return re.sub(r'<p>.*?</p>', '<p>IPLC资料 · 6款套餐</p>', match[0], count=1, flags=re.S)
        text = re.sub(r'<a\b[^>]*href="brand-breezenet\.html"[^>]*>.*?</a>', update_card, text, flags=re.S)
        write_changed(path, text)
    brands_path = root / 'data/brands.json'
    catalog = json.loads(brands_path.read_text(encoding='utf-8'))
    brand = next(item for item in catalog['brands'] if item['id'] == 'breezenet')
    brand.update(profile_status='third_party_plan_catalog', verification_status='third_party_materials_not_independently_verified', source_type='第三方套餐截图，经站长转交', source_date=data['updated_on'], plan_count=len(plans), line_type_from_materials='IPLC专线', page_checked_on=data['updated_on'], page_observation='入口经线路检测后可跳转微风网络注册页，并保留邀请码；套餐数据来自第三方截图，未登录后台独立核价。')
    if latency_data:
        brand.update(source_type='第三方套餐及延迟截图，经站长转交', latency_node_count=52, latency_recorded_at='2026-10-29 12:00（北京时间）')
    write_changed(brands_path, json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    # Keep the existing general FAQ accurate as a second brand gains prices.
    old_status = '其他四个品牌的现行价格仍待提供，非月付周期报价不自行推算。'
    new_status = '微风网络的6款套餐已按第三方资料整理；其余三个品牌的现行价格仍待补充。未提供的付费周期报价不自行推算。'
    for name in ('faq.html', 'data/library.json', 'data/topics.json'):
        path = root / name
        if path.exists():
            text = path.read_text(encoding='utf-8')
            if old_status in text:
                write_changed(path, text.replace(old_status, new_status))
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['套餐', '价格_元', '付费周期', '流量_GB', '额度口径', '规则', '线路_资料标注', '设备同时接入_资料标注'])
    for plan in plans:
        writer.writerow([plan['name'], plan['price'], plan['price_unit'], plan['traffic_gb'], '一次性总量' if plan['billing'] == 'once' else '每月额度', plan['reset_rule'], 'IPLC专线', '不限'])
    write_changed(root / 'data/breezenet-plans.csv', '\ufeff' + output.getvalue())
    markdown = '# 微风网络 Breezenet\n\n' + f'整理日期：{data["updated_on"]}。来源：{data["source"]["description"]}。未发布原截图，未登录后台独立核价。\n\n'
    if profile:
        markdown += '## 品牌介绍\n\n' + profile['intro'] + '\n\n定位来源：' + profile['source'] + '，日期：' + profile['updated_on'] + '。\n\n' + ''.join('### ' + item['title'] + '\n\n' + item['description'] + '\n\n' for item in profile['audiences'])
    markdown += '## 套餐与流量\n\n| 套餐 | 价格 | 流量口径 | 规则 |\n| --- | --- | --- | --- |\n'
    for plan in plans:
        period = '一次性总量' if plan['billing'] == 'once' else '每月额度'
        markdown += f'| {plan["name"]} | {plan["price"]}元/{plan["price_unit"]} | {plan["traffic_gb"]}GB，{period} | {plan["reset_rule"]} |\n'
    markdown += '\n清风137元年付折算约11.42元/月，实际仍按年支付。6款套餐资料均标注IPLC专线、不限制设备同时接入及不限速；不把这些表述当作实测结果或速度保证。\n\n'
    markdown += '## 套餐说明\n\n' + ''.join('### ' + plan['name'] + '\n\n' + plan['description'] + '\n\n' for plan in plans)
    if coupon:
        markdown += f'## 清风年付优惠\n\n优惠码：{coupon["code"]}，{coupon["discount_label"]}。清风原价137元/年、每月100GB，券后按原价计算为{annual_paid}元/年，折算约{monthly_paid}元/月，实际按年支付。{scope}；{expiry}。来源：{coupon["source"]}。\n\n'
    markdown += '## 常见问题\n\n' + ''.join('### ' + question + '\n\n' + answer + '\n\n' for question, answer in faqs(data, latency_data, coupon, profile))
    if latency_data:
        from breeze_latency import markdown as latency_markdown
        markdown += latency_markdown(root)
    markdown += '## 入口与资料边界\n\n[微风访问入口](' + data['entry_url'] + ')。入口保留原推广参数。套餐截图与延迟截图分别注明来源；未提供的其他周期价格、客户端使用方式及售后规则不自行填写。\n'
    folder = root / 'content/brands'
    folder.mkdir(parents=True, exist_ok=True)
    write_changed(folder / 'breezenet.md', markdown)


if __name__ == '__main__':
    build_breezenet_profile(Path(__file__).resolve().parents[1])
