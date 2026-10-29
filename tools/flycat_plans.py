"""Render Flycat prices using supplied package materials and explicit confirmations."""
import csv
from decimal import Decimal
from html import escape as e
from io import StringIO
from flycat_coupon import eligible, discounted, floating_coupon


def money(value):
    return format(Decimal(str(value)), '.2f')


def plan_faqs(data):
    return [
        ('飞猫云有几款套餐，价格是多少？', '本页整理7款：学生版84元/年、每月50GB；星耀版25元/月、150GB；星环版45元/月、300GB；银河版85元/月、600GB；宇宙版150元/月、1000GB；不限时套餐680元一次性、1000GB总额度；定制套餐图示550元/月、500GB。'),
        ('学生版84元/年还要再打年付8折吗？', '不再叠加。站长已确认84元就是最终年付价，一次支付84元，折合7元/月；每月自动刷新50GB。7元/月是年付折算，不能按7元单独购买一个月。'),
        ('其他周期套餐的年付、两年付和三年付价格是多少？', '本次按站长确认保留四款套餐的图示月价，不按月价推算长周期总价。选择季度、半年、年付或更长周期时，请先查看官网对应订单的实际金额与规则。'),
        ('飞猫云周期套餐什么时候刷新流量？', '学生版资料写明每月自动刷新。星耀、星环、银河、宇宙的截图写明季付及以上从购买日起每30天自动刷新；月付具体刷新日期以后台显示为准。'),
        ('不限时套餐是每个月都有1000GB吗？', '不是。680元购买的是一次性1000GB总流量，无使用时间限制，用完为止；购买后不按月自动重置，也不参加周期套餐的长期折扣。'),
        ('不限时套餐手动重置多少钱？', '截图列明手动重置费用为原价的90%，即680×0.9＝612元。这是单独的付费重置规则；首次购买金额按套餐与优惠码规则核对，不能由此推定重置包还能叠加优惠。'),
        ('飞猫云定制套餐适合什么需求？', '定制方案提供专属节点、独享原生IP及独立带宽，面向跨境电商、TikTok直播、社媒推广、远程办公等需求。图示550元/月、500GB；流量、带宽和地区可以调整，实际配置及报价向客服确认。'),
        ('套餐里的最高2.5Gbps是实际测速结果吗？', '这是常规套餐截图中的最高网络规格，未提供对应测速记录，不能直接换算成每位用户持续可获得的下载速度。定制套餐按单独确认的带宽配置介绍。'),
        ('为什么不同资料中的韩国节点数量不一样？', '品牌介绍和周期套餐列明韩国3个节点，不限时套餐截图列明韩国2个。本页分别保留对应资料，购买某款套餐时以该套餐后台当前可选节点为准。')
    ]


def render_plans(data, url, coupon):
    cards = []
    labels = {'periodic': '周期订阅', 'one_time': '一次性流量', 'custom': '专属定制'}
    for plan in data['plans']:
        if plan['kind'] == 'custom':
            continue
        student = plan['id'] == 'student'
        badge = '轻量年付' if student else labels[plan['kind']]
        extra = '<p class="flycat-plan-equivalent">年付折合 <b>¥7.00/月</b> · 实付¥84/年</p>' if student else '<p class="flycat-plan-equivalent">' + ('付费手动重置 ¥612' if plan['kind'] == 'one_time' else '当前展示已确认的月付报价') + '</p>'
        if eligible(coupon, plan):
            extra = '<p class="flycat-plan-equivalent flycat-coupon-price">九折券后 <b>¥' + money(discounted(coupon, plan['price_cny'])) + '/' + e(plan['payment_unit']) + '</b></p>'
        refresh = '每月自动刷新' if student else ('总额度，用完为止' if plan['kind'] == 'one_time' else '季付及以上：购买日起每30天刷新')
        cards.append(f'''<article class="flycat-plan-card{' is-student' if student else ''}{' is-timeless' if plan['kind'] == 'one_time' else ''}" id="flycat-plan-{plan['id']}"><span class="flycat-plan-label">{badge}</span><h3>{e(plan['name'])}</h3><p class="flycat-plan-price"><strong>¥{money(plan['price_cny'])}</strong><span>/{e(plan['payment_unit'])}</span></p>{extra}<div class="flycat-plan-quota"><span>{e(plan['traffic_scope'])}流量</span><strong>{plan['traffic_gb']:,}<small>GB</small></strong></div><p class="flycat-plan-refresh">{refresh}</p><p class="flycat-plan-audience">{e(plan['audience'])}</p><p class="flycat-plan-detail">{e(plan['detail'])}</p><a class="flycat-plan-link" href="{url}" target="_blank" rel="sponsored noopener noreferrer">查看该套餐 <span aria-hidden="true">↗</span></a></article>''')
    custom = next(plan for plan in data['plans'] if plan['kind'] == 'custom')
    rows = ''
    for plan in data['plans']:
        coupon_price = '¥' + money(discounted(coupon, plan['price_cny'])) + '/' + e(plan['payment_unit']) if eligible(coupon, plan) else '学生版不适用'
        refresh = '每月自动刷新' if plan['id'] == 'student' else ('季付及以上每30天刷新' if plan['kind'] == 'periodic' else ('不自动刷新；手动重置¥612' if plan['kind'] == 'one_time' else '配置及规则向客服确认'))
        rows += f'''<tr><th scope="row"><a href="#flycat-plan-{plan['id']}">{e(plan['name'])}</a></th><td>¥{money(plan['price_cny'])}/{e(plan['payment_unit'])}</td><td class="flycat-table-discount">{coupon_price}</td><td>{plan['traffic_gb']:,}GB · {e(plan['traffic_scope'])}</td><td>{refresh}</td></tr>'''
    return f'''<section class="section" id="flycat-plans"><div class="flycat-section-title"><span class="overline">7 PLANS / DIFFERENT WAYS TO USE</span><h2>按用量与周期，选择飞猫云套餐。</h2><p>从每月50GB的轻量年付，到一次性流量与专属定制。先看额度，再看付款方式。</p></div><div class="flycat-plan-grid">{''.join(cards)}</div><article class="flycat-custom" id="flycat-plan-custom"><div><span class="flycat-plan-label">专属定制 · 按需求确认</span><h3>{e(custom['name'])}</h3><p class="flycat-custom-price">图示配置 <strong>¥550/月</strong><span>500GB</span></p><p class="flycat-coupon-price">图示配置九折后 <b>¥{money(discounted(coupon, custom['price_cny']))}/月</b></p><p>{e(custom['audience'])}</p></div><div><h4>独享原生IP与独立带宽</h4><p>支持按需求调整流量、带宽和节点地区；资料列明香港、日本、美国、新加坡等地区，以及一对一技术支持与优先客服通道。</p><p class="flycat-note">以上为截图所示配置。具体部署方案、价格与刷新规则向客服确认。</p><a class="flycat-plan-link" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往官网了解定制方案 ↗</a></div></article><div class="flycat-plan-common"><h3>常规套餐共同列明的服务</h3><div><span>IPLC专线</span><span>节点1×计费</span><span>不限设备连接</span><span>原生IP线路</span><span>智能路由优化</span></div><p>套餐资料列明Netflix、Disney+、ChatGPT、TikTok支持方向，以及最高2.5Gbps网络规格。规格说明按资料展示，实际连接表现取决于使用环境与当时线路状态。</p></div><details class="flycat-cycle-notes"><summary>查看流量刷新与价格说明</summary><p>学生版每月自动刷新50GB，84元为最终年付价，不另叠加年付折扣。四款月付报价分别对应150GB、300GB、600GB和1000GB；资料中的“从购买日起每30天刷新”明确针对季付及以上，月付刷新日期请核对后台。</p><p>其他周期套餐仅列已确认月价，不推算长周期总价。不限时套餐的1000GB是一次性总额度，不参加周期套餐的长期折扣，手动重置费用为612元。节点地区可能因套餐而异，具体以后台为准。</p></details></section>
<section class="section" id="flycat-compare"><div class="flycat-section-title"><span class="overline">PRICES & TRAFFIC AT A GLANCE</span><h2>价格、额度与刷新方式，一起对照。</h2><p>“每月额度”和“一次性总额度”分开列示，便于按实际使用习惯比较。</p></div><div class="flycat-table-wrap" tabindex="0" role="region" aria-label="飞猫云套餐价格对比，可横向滚动"><table class="flycat-plan-table"><caption>飞猫云7款套餐对比 · 2026年10月29日整理</caption><thead><tr><th scope="col">套餐</th><th scope="col">基础价格</th><th scope="col">九折码券后价格</th><th scope="col">流量额度</th><th scope="col">刷新方式</th></tr></thead><tbody>{rows}</tbody></table></div><p class="flycat-note">报价依据站长提供的套餐资料及确认记录，实际在售价格与配置请核对官网。<a href="data/feimaoyun-plans.csv" download>下载套餐表 CSV ↓</a></p></section>
<section class="section" id="flycat-choose"><div class="flycat-section-title"><span class="overline">START WITH YOUR ACTUAL USAGE</span><h2>先了解自己的用量，再决定买多少。</h2></div><div class="flycat-choice-grid"><article><span>01 / 轻量、稳定使用</span><h3>看月度额度，也看全年预算。</h3><p>如果每月用量在50GB以内，可先比较学生版；希望保留月付灵活性、需要更大额度时，再从150GB、300GB往上选择。年付意味着一次支付全年金额。</p></article><article><span>02 / 用量不固定</span><h3>比较月度刷新与总流量。</h3><p>偶尔集中使用、平时用量少，可以对比不限时套餐。它不随月份增加流量，适合按累计消耗评估预算；用完后手动重置需另付612元。</p></article><article><span>03 / 有专门业务需求</span><h3>把IP与带宽需求告诉客服。</h3><p>定制方案适合有独享IP、独立带宽或特定地区需求的用户。先确认部署地区、流量和带宽，再核对报价；普通套餐不直接等同于独享IP方案。</p></article></div></section>'''


def render_floating(url, coupon, logo_image):
    launcher_logo = logo_image.replace('alt="飞猫云Logo"', 'alt=""')
    return f'''<aside class="floating-promo" id="flycat-floating-promo" data-open="auto" aria-label="飞猫云套餐推荐"><section class="fp-panel" id="flycat-floating-panel" aria-label="飞猫云学生版推荐"><div class="fp-handle" title="拖动移动推荐卡"><span class="fp-grip" aria-hidden="true">⠿</span><span class="fp-label">轻量年付</span><div class="fp-window-actions"><button type="button" class="fp-reset" aria-label="恢复飞猫推荐卡默认位置" title="恢复默认位置">↺</button><button type="button" class="fp-close" aria-label="收起飞猫推荐卡" title="收起">×</button></div></div><div class="fp-content"><a class="fp-brand" href="#flycat-about">{logo_image}<span><strong>飞猫云</strong><small>FLYCAT · IPLC专线</small></span></a><div class="fp-plan"><span class="fp-eyebrow">推荐套餐 · 低流量用户</span><h2>飞猫·学生版</h2><div class="fp-traffic"><strong>50<small>GB</small></strong><span>每月刷新</span></div></div><div class="fp-pricing"><div><small>年付折算</small><strong>¥7.00</strong><span>/月</span></div><p class="fp-annual-total">实付 ¥84.00/年 · 已确认最终价</p></div><a class="flycat-float-details" href="#flycat-plans">比较全部7款套餐 →</a>{floating_coupon(coupon)}<a class="fp-cta" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往官网查看 <span aria-hidden="true">↗</span></a><p class="fp-note">学生版不适用优惠码；按年支付，每月50GB。</p><p class="fp-copy-status" role="status" aria-live="polite"></p></div></section><button type="button" class="fp-launcher" aria-controls="flycat-floating-panel" aria-expanded="false" aria-label="展开飞猫套餐推荐">{launcher_logo}<span>飞猫套餐</span><span aria-hidden="true">＋</span></button></aside>'''


def plans_csv(data, coupon):
    stream = StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['套餐', '基础价格（元）', '付款单位', '流量（GB）', '流量范围', '刷新规则', '资料整理日期', 'flycat888券后价格（元）'])
    for plan in data['plans']:
        writer.writerow([plan['name'], plan['price_cny'], plan['payment_unit'], plan['traffic_gb'], plan['traffic_scope'], plan['reset_rule'], data['provided_on'], money(discounted(coupon, plan['price_cny'])) if eligible(coupon, plan) else '学生版不适用'])
    return '\ufeff' + stream.getvalue()


def plans_markdown(data, coupon):
    text = '## 套餐价格与流量\n\n来源：' + data['source'] + '。整理日期：' + data['provided_on'] + '。原截图不作为页面图片发布。\n\n'
    for plan in data['plans']:
        text += '### ' + plan['name'] + '\n\n¥' + money(plan['price_cny']) + '/' + plan['payment_unit'] + '；' + str(plan['traffic_gb']) + 'GB · ' + plan['traffic_scope'] + '。\n\n' + plan['detail'] + '\n\n' + plan['reset_rule'] + '\n\n' + plan['audience'] + '\n\n'
        if eligible(coupon, plan):
            text += '使用优惠码' + coupon['code'] + '，九折后¥' + money(discounted(coupon, plan['price_cny'])) + '/' + plan['payment_unit'] + '。\n\n'
    text += '常规套餐资料列明IPLC、原生IP、节点1×及不限设备连接，最高2.5Gbps为规格说明。定制方案的独享IP与独立带宽单独向客服确认。其他四款周期套餐仅展示图示月价，不推算长周期金额。\n\n'
    return text
