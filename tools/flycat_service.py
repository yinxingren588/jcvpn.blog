"""Render only confirmed Flycat service rules with separate package scopes."""
from html import escape as e


def service_faqs(data):
    return [
        ('飞猫云周期套餐的流量用完了怎么办？', '可以购买流量重置包，或选择升级套餐。周期套餐重置包的价格与所购套餐一致，购买后立即恢复该套餐的完整流量额度。'),
        ('飞猫云所有套餐的流量重置都是612元吗？', '不是。612元是不限时套餐截图列明的手动重置价格，按680元原价的90%计算。周期套餐采用与所购套餐同价的重置包，购买后立即恢复对应套餐完整流量。'),
        ('飞猫云周期套餐可以升级吗？', '支持升级套餐。需要更多流量时，可以先对照本页套餐表选择额度；升级前核对后台订单列出的费用、流量和有效期。')
    ]


def render_service(data):
    reset = data['periodic_traffic_reset']
    once = data['one_time_traffic_reset']
    return f'''<section class="section" id="flycat-service"><div class="flycat-section-title"><span class="overline">TRAFFIC RESET & PLAN UPGRADES</span><h2>周期套餐流量用完，可重置或升级。</h2><p>继续使用当前额度，或根据用量调整套餐，先了解两种处理方式。</p></div><div class="flycat-feature-grid flycat-rules-grid"><article><h3>购买流量重置包</h3><p>重置包价格{e(reset['price_basis'])}，购买后立即恢复该套餐的完整流量额度。适合希望继续使用当前套餐、补充本次可用流量的情况。</p><div class="flycat-rule-tags"><span>与所购套餐同价</span><span>立即恢复完整流量</span></div></article><article><h3>升级套餐</h3><p>支持升级套餐。若现有额度经常不够用，可以先对照月度流量选择更适合的套餐，升级前核对后台订单中的费用、流量与有效期。</p><a class="flycat-rule-link" href="#flycat-compare">对照套餐额度与价格 →</a></article></div><div class="flycat-service-scope"><h3>不限时套餐采用单独规则</h3><p>不限时套餐为一次性1000GB总额度，不按月自动刷新。截图列明手动重置费用为{once['price_cny']}元，即680元原价的90%；与周期套餐的同价重置包分别计算。</p></div><p class="flycat-note">周期套餐重置与升级支持由博客站长于{e(data['confirmed_on'])}确认；不限时套餐的手动重置金额来自已提供的套餐资料。</p></section>'''


def service_markdown(data):
    text = '## 流量重置与套餐升级\n\n来源：' + data['source'] + '；确认日期：' + data['confirmed_on'] + '。\n\n'
    text += '### 周期套餐\n\n流量用完后可购买重置包或升级套餐。重置包与所购套餐价格一致，购买后立即恢复该套餐完整流量额度。升级前核对后台订单列出的费用、流量和有效期。\n\n'
    text += '### 不限时套餐\n\n一次性1000GB总额度，不按月自动刷新。按截图列明的规则，手动重置费用为680元原价的90%，即612元，与周期套餐分别计算。\n\n'
    return text
