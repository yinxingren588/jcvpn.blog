"""Render nine Twilight packages from the supplied screenshots and confirmation."""
import csv
from decimal import Decimal, ROUND_HALF_UP
from html import escape as e
from io import StringIO


def money(value):
    return format(Decimal(str(value)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP),'.2f')


def plan_faqs(data):
    return [
        ('暮光网络目前有哪些套餐，价格是多少？', '本页整理9款：年付轻量版109元/年、70GB/30天；基础版20元/月、120GB；标准版40元/月、240GB；旗舰版100元/月、700GB；至尊版180元/月、1500GB。另有219元/150GB、529元/400GB、959元/800GB的一次性不限时流量包，以及680元/月、500GB的独享私人定制节点。'),
        ('年付轻量版的70GB是全年总流量吗？', '不是。资料写明购买日起算，每30天自动刷新70GB。109元是年付金额，折合约9.08元/月；月均成本用于比较，实际按年支付。'),
        ('暮光标准版的流量是240GB还是300GB？', '图片上方标240GB、详情文字标300GB，站长已明确确认采用240GB/月，本页与价格表均按240GB整理。'),
        ('暮光不限时流量包会每月自动补充吗？', '不会。三款分别是150GB、400GB和800GB一次性总流量，无流量到期限制，用完为止，不按周期自动重置。'),
        ('暮光周期套餐每个月哪天刷新？', '年付轻量版明确写明购买日起每30天自动刷新。其余四款按每月额度介绍，截图未列具体刷新日期，使用前请核对后台。'),
        ('暮光周期套餐流量用完后怎么办，重置包多少钱？', data['periodic_reset_policy']['description']),
        ('暮光周期套餐提前续费，会立即补充流量吗？', data['periodic_early_renewal_policy']['description']),
        ('暮光周期套餐升级如何收费，周期与流量怎样计算？', data['periodic_upgrade_policy']['description']),
        ('暮光独享私人定制节点提供什么配置？', '图示680元/月、每月500GB独享流量，提供独立带宽资源与独立公网IP，不与他人共享。面向独立部署、TikTok直播及跨境业务，定制需求通过工单沟通。'),
        ('独享私人定制节点需要多久交付？', '资料列明下单后2—3个工作日完成交付，由专人技术维护。具体部署内容与进度通过暮光工单系统确认。'),
        ('套餐里的Shadowsocks是客户端名称吗？', 'Shadowsocks是协议或连接方案名称，不能直接当作软件名称。基础、标准、旗舰、至尊四款的截图提到该方案，各平台客户端及具体使用流程需要对应指引。'),
        ('资料中的4K、8K和AI平台支持是否已经实测？', '这些属于本次套餐资料中的使用方向，本页尚未提供暮光网络的实际播放、AI操作或速度测试记录。实际使用反馈将注明日期、网络、节点和完成的任务。')
    ]


def render_usage_rules(data):
    policy=data['periodic_reset_policy']
    renewal=data['periodic_early_renewal_policy']
    upgrade=data['periodic_upgrade_policy']
    return '<section class="section" id="twilight-traffic"><div class="twilight-section-title"><span class="overline">PERIODIC PLAN / RESET, RENEWAL & UPGRADE</span><h2>看清重置、续费与升级的区别。</h2><p>按需要补充流量、延长有效期或调整套餐，分别核对金额、起算日和可用额度。</p></div><article class="twilight-plan-notes"><h3>购买重置包 · 立即恢复流量</h3><p>'+e(policy['description'])+'</p></article><article class="twilight-plan-notes"><h3>提前续费 · 延长有效期</h3><p>'+e(renewal['description'])+'</p></article><article class="twilight-plan-notes"><h3>升级套餐 · 先付全价，再退差价</h3><p>'+e(upgrade['description'])+'</p></article></section>'


def render_plans(data,url):
    labels={'periodic':'周期订阅','one_time':'不限时总流量','custom':'独享定制'}
    cards=[]
    rows=[]
    for plan in data['plans']:
        annual=plan['id']=='light-year'
        custom=plan['kind']=='custom'
        badge='轻量年付' if annual else labels[plan['kind']]
        extra='年付折合约 <b>¥'+money(Decimal(str(plan['price_cny']))/12)+'/月</b>' if annual else ('独立公网IP · 独立带宽' if custom else ('一次购买 · 用完为止' if plan['kind']=='one_time' else '每月额度 · 按图示月价'))
        refresh='购买日起每30天刷新' if annual else ('不按周期自动重置' if plan['kind']=='one_time' else ('部署与刷新方式通过工单确认' if custom else '具体刷新日期请核对后台'))
        delivery='<p class="twilight-delivery">'+e(plan['delivery_note'])+'</p>' if custom else ''
        cards.append(f'''<article class="twilight-plan{' is-annual' if annual else ''}{' is-once' if plan['kind']=='one_time' else ''}{' is-custom' if custom else ''}" id="twilight-plan-{plan['id']}" data-twilight-kind="{plan['kind']}"><span class="twilight-plan-label">{badge}</span><h3>{e(plan['name'])}</h3><p class="twilight-plan-price"><strong>¥{money(plan['price_cny'])}</strong><span>/{e(plan['payment_unit'])}</span></p><p class="twilight-plan-extra">{extra}</p><div class="twilight-plan-quota"><span>{e(plan['quota_scope'])}</span><strong>{plan['traffic_gb']:,}<small>GB</small></strong></div><p class="twilight-plan-reset">{refresh}</p><p class="twilight-plan-audience">{e(plan['audience'])}</p><p class="twilight-plan-detail">{e(plan['detail'])}</p>{delivery}<a href="{url}" target="_blank" rel="sponsored noopener noreferrer" class="twilight-plan-action">{'前往了解定制方案' if custom else '查看套餐入口'} <span aria-hidden="true">↗</span></a></article>''')
        row_refresh='购买日起每30天' if annual else ('不自动重置' if plan['kind']=='one_time' else ('工单确认' if custom else '具体日期核对后台'))
        rows.append(f'''<tr><th scope="row"><a href="#twilight-plan-{plan['id']}">{e(plan['name'])}</a></th><td>¥{money(plan['price_cny'])}/{e(plan['payment_unit'])}</td><td>{plan['traffic_gb']:,}GB · {e(plan['quota_scope'])}</td><td>{row_refresh}</td></tr>''')
    return f'''<section class="section" id="twilight-plans"><div class="twilight-section-title"><span class="overline">9 PLANS / CHOOSE BY USAGE</span><h2>按用量与付款方式，选择暮光套餐。</h2><p>5款周期套餐、3款不限时流量包与1款独享定制，分别看清每期额度和一次性总额度。</p></div><div class="twilight-plan-filters" role="group" aria-label="按暮光套餐类型筛选"><button type="button" data-twilight-filter="all" aria-pressed="true">全部 <span>9</span></button><button type="button" data-twilight-filter="periodic" aria-pressed="false">周期套餐 <span>5</span></button><button type="button" data-twilight-filter="one_time" aria-pressed="false">不限时流量 <span>3</span></button><button type="button" data-twilight-filter="custom" aria-pressed="false">独享定制 <span>1</span></button></div><p class="twilight-plan-count" id="twilight-plan-count" role="status" aria-live="polite">全部套餐 · 共9款</p><div class="twilight-plan-grid">{''.join(cards)}</div><div class="twilight-plan-notes"><h3>这些套餐怎样区分？</h3><p>年付轻量版109元按年支付，从购买日起每30天刷新70GB；四款月付分别对应120GB、240GB、700GB和1500GB。标准版额度已由站长确认采用240GB。</p><p>三款不限时流量包按累计消耗扣减，分别为150GB、400GB和800GB总额度，不自动按月补充。独享定制提供独立带宽与独立公网IP，图示每月500GB，资料列明2—3个工作日交付。</p><p>四款月付资料提到BGP优化、Shadowsocks方案及流媒体与AI工具使用方向；年付、一次性和定制方案按各自说明整理。实际速率和平台访问结果需要对应条件下的记录。</p></div></section>
<section class="section" id="twilight-plan-comparison"><div class="twilight-section-title"><span class="overline">PRICE, QUOTA & RENEWAL</span><h2>把价格、流量和刷新方式放在同一张表。</h2><p>周期额度与不限时总额度分开列明，避免只比较GB数字。</p></div><div class="twilight-table-wrap" tabindex="0" role="region" aria-label="暮光网络9款套餐对比，可横向滚动"><table class="twilight-plan-table"><caption>暮光网络9款套餐 · {data['provided_on']}整理</caption><thead><tr><th scope="col">套餐</th><th scope="col">图示价格</th><th scope="col">流量额度</th><th scope="col">刷新方式</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="twilight-note">价格与额度依据站长提供的套餐截图和确认记录整理，实际在售与配置请核对官网。<a href="data/muguang-plans.csv" download>下载完整套餐表 CSV ↓</a></p></section>
<section class="section" id="twilight-plan-guide"><div class="twilight-section-title"><span class="overline">START WITH YOUR OWN PATTERN</span><h2>用量、周期和IP需求，决定选择方向。</h2></div><div class="twilight-plan-guide"><article><span>轻量与日常使用</span><h3>先看每期用量，再看付款周期。</h3><p>每30天用量较少，可比较年付轻量版；偏好月付或需要更多额度时，再比较120GB至1500GB四个档位。9.08元是年付月均成本，实际一次支付109元。</p></article><article><span>用量随阶段变化</span><h3>按累计消耗评估不限时流量。</h3><p>不限时流量包适合按实际总消耗安排预算。150GB、400GB、800GB都是单次购买获得的总量，月份增加不会自动补充流量。</p></article><article><span>独立部署与业务使用</span><h3>先确认公网IP和带宽配置。</h3><p>有独立公网IP、独立带宽或部署需求，可通过工单了解私人定制节点，并确认交付配置与进度。普通套餐与独享定制分别核对。</p></article></div></section>'''


def floating_recommendation(data,url):
    plan=next(plan for plan in data['plans'] if plan['id']=='light-year')
    monthly=money(Decimal(str(plan['price_cny']))/12)
    return f'''<aside class="floating-promo" id="twilight-floating-promo" data-open="auto" aria-label="暮光网络套餐推荐"><section class="fp-panel" id="twilight-floating-panel" aria-label="暮光网络年付轻量版推荐"><div class="fp-handle" title="拖动移动推荐卡"><span class="fp-grip" aria-hidden="true">⠿</span><span class="fp-label">轻量年付</span><div class="fp-window-actions"><button type="button" class="fp-reset" aria-label="恢复暮光推荐卡默认位置" title="恢复默认位置">↺</button><button type="button" class="fp-close" aria-label="收起暮光推荐卡" title="收起">×</button></div></div><div class="fp-content"><a class="fp-brand" href="#twilight-about"><span class="twilight-float-mark" aria-hidden="true">暮</span><span><strong>暮光网络</strong><small>IPLC专线</small></span></a><div class="fp-plan"><span class="fp-eyebrow">推荐套餐 · 轻量使用</span><h2>{e(plan['name'])}</h2><div class="fp-traffic"><strong>{plan['traffic_gb']}<small>GB</small></strong><span>每30天刷新</span></div></div><div class="fp-pricing"><div><small>年付折算约</small><strong>¥{monthly}</strong><span>/月</span></div><p class="fp-annual-total">实际按年支付 ¥{money(plan['price_cny'])}/年</p></div><a class="twilight-float-details" href="#twilight-plans" data-twilight-show-all>对比全部9款套餐 →</a><a class="fp-cta" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往暮光网络查看 <span aria-hidden="true">↗</span></a><p class="fp-note">购买日起每30天刷新70GB，实际按年付款。</p></div></section><button type="button" class="fp-launcher" aria-controls="twilight-floating-panel" aria-expanded="false" aria-label="展开暮光套餐推荐"><span class="twilight-launcher-mark" aria-hidden="true">暮</span><span>暮光套餐</span><span aria-hidden="true">＋</span></button></aside>'''


def plans_csv(data):
    stream=StringIO(newline='')
    writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['套餐','价格（元）','付款单位','流量（GB）','流量范围','刷新方式','交付说明','资料日期'])
    for plan in data['plans']:
        writer.writerow([plan['name'],plan['price_cny'],plan['payment_unit'],plan['traffic_gb'],plan['quota_scope'],plan['reset_rule'],plan.get('delivery_note',''),data['provided_on']])
    return '\ufeff'+stream.getvalue()


def plans_markdown(data):
    text='## 套餐与流量\n\n来源：'+data['source']+'。整理日期：'+data['provided_on']+'。原套餐照片不作为博客图片发布。\n\n'
    for plan in data['plans']:
        text+='### '+plan['name']+'\n\n¥'+money(plan['price_cny'])+'/'+plan['payment_unit']+'；'+str(plan['traffic_gb'])+'GB · '+plan['quota_scope']+'。\n\n'+plan['detail']+'\n\n'+plan['reset_rule']+'\n\n'+plan['audience']+'\n\n'
        if plan.get('delivery_note'):
            text+=plan['delivery_note']+'\n\n'
    text+='标准版流量冲突已由站长确认采用240GB/月。不推算其他付款周期或优惠价；具体套餐范围和使用规则按对应资料说明。\n\n'
    text+='## 周期套餐流量重置\n\n'+data['periodic_reset_policy']['description']+'\n\n'
    text+='## 周期套餐提前续费\n\n'+data['periodic_early_renewal_policy']['description']+'\n\n'
    text+='## 周期套餐升级\n\n'+data['periodic_upgrade_policy']['description']+'\n\n'
    return text
