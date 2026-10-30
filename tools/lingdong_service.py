"""Render Lingdong's confirmed periodic service rules with their own package scope."""
from html import escape as e


def upgrade_text(data):
    return ''.join(data['upgrade'][key] for key in ('payment_rule','cycle_rule','traffic_rule'))


def service_faqs(data):
    return [
        ('灵动云周期套餐的流量用完后怎样重置？',data['reset']['description']),
        ('提前续费灵动云周期套餐，会立即补充流量吗？',data['early_renewal']['description']),
        ('灵动云升级套餐的费用、周期和流量怎样处理？',upgrade_text(data)),
        ('灵动云什么情况下可以全额退款，多久内申请？',data['refund']['description']),
        ('灵动云客服在哪里联系？',data['customer_support']['instructions']),
        ('灵动云支持什么付款方式？','已确认支持'+ '、'.join(data['payment_methods'])+'付款，可通过灵动云官网选择套餐并付款。')
    ]


def render_service(data):
    steps=''.join('<li>'+e(data['upgrade'][key])+'</li>' for key in ('payment_rule','cycle_rule','traffic_rule'))
    return f'''<section class="section" id="lingdong-service"><div class="lingdong-section-title"><span class="overline">PERIODIC PLANS / RESET, RENEWAL & UPGRADE</span><h2>重置、续费、升级，各自怎样处理？</h2><p>把费用、流量和起算日分开看清。以下适用于已确认的周期套餐。</p></div><div class="lingdong-service-grid"><article class="lingdong-service-card"><span class="lingdong-index">01 / RESET</span><h3>重置：立即恢复流量</h3><p>{e(data['reset']['description'])}</p><span class="lingdong-rule-tag">与所购套餐同价</span></article><article class="lingdong-service-card"><span class="lingdong-index">02 / RENEWAL</span><h3>续费：延长有效期</h3><p>{e(data['early_renewal']['description'])}</p><span class="lingdong-rule-tag">仍按原时间刷新</span></article><article class="lingdong-service-card is-upgrade"><span class="lingdong-index">03 / UPGRADE</span><h3>升级：分清三项处理</h3><ol>{steps}</ol></article></div><div class="lingdong-source-links"><a href="data/lingdongyun-service-rules.json">查看周期套餐规则 JSON ↓</a></div></section>'''


def service_markdown(data):
    return ('## 周期套餐流量规则\n\n来源：'+data['source']+'。确认日期：'+data['updated_on']+'。\n\n'+
            '### 流量重置\n\n'+data['reset']['description']+'\n\n'+
            '### 提前续费\n\n'+data['early_renewal']['description']+'\n\n'+
            '### 套餐升级\n\n'+upgrade_text(data)+'\n\n'+
            '## 技术问题退款与客服\n\n'+data['refund']['description']+'\n\n'+data['customer_support']['instructions']+'\n\n'+
            '## 付款方式\n\n已确认支持'+ '、'.join(data['payment_methods'])+'付款。\n\n')


def render_refund(data,url):
    return f'''<section class="section" id="lingdong-refund"><div class="lingdong-section-title"><span class="overline">SUPPORT / TECHNICAL REFUND</span><h2>技术问题退款：购买后24小时内申请。</h2><p>先联系官网后台客服协助排查，再按实际情况申请。</p></div><article class="lingdong-refund-card"><h3>经客服协助后仍完全无法使用，可申请全额退款。</h3><p>{e(data['refund']['description'])}</p><a class="lingdong-refund-link" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往官网后台联系客服 <span aria-hidden="true">↗</span></a></article></section>'''
