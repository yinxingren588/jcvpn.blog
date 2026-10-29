"""Render Flycat application feedback separately from service claims and speed tests."""
from html import escape as e


def access_faqs(data):
    record = data['records'][0]
    return [
        ('飞猫云有没有ChatGPT实际使用记录？', '有。根据站长提供的反馈，' + record['tested_on'] + '在' + record['test_location'] + '使用' + record['isp'] + '网络，连接飞猫云' + record['node_region'] + '节点，可以正常发送问题并收到回答。这条记录对应当时的ChatGPT问答操作。')
    ]


def render_access(data):
    cards = []
    for record in data['records']:
        facts = [('记录日期', record['tested_on']), ('使用所在地', record['test_location']), ('网络运营商', record['isp']), ('节点地区', record['node_region'])]
        facts_html = ''.join('<div><dt>' + e(label) + '</dt><dd>' + e(value) + '</dd></div>' for label, value in facts)
        cards.append('<article class="access-record" id="flycat-access-' + e(record['id'], quote=True) + '"><div class="access-record-head"><span class="access-record-source">' + e(data['source']) + '</span><span class="access-record-status">本次问答正常</span></div><h3>' + e(record['platform']) + ' · ' + e(record['node_region']) + '节点</h3><dl class="access-record-facts">' + facts_html + '</dl><div class="flycat-access-task"><span>验证操作</span><p>' + e(record['task']) + '</p></div><div class="access-record-result"><span>使用结果</span><p>' + e(record['result']) + '。</p></div><p class="access-record-note">本次反馈仅覆盖上述条件下的ChatGPT问答；其他节点、时段及功能应分别记录。</p></article>')
    return '<section class="section access-records-panel" id="flycat-access-records" aria-labelledby="flycat-access-title"><div class="flycat-section-title"><span class="overline">CHATGPT / RECORDED USE</span><h2 id="flycat-access-title">ChatGPT使用记录：上海电信，新加坡节点。</h2><p>按站长提供的实际使用反馈，列出日期、网络环境、节点地区和具体结果。</p></div><div class="flycat-access-cards">' + ''.join(cards) + '</div><div class="flycat-source-links"><a href="data/feimaoyun-access-records.json">查看ChatGPT使用记录 JSON ↓</a></div></section>'


def access_markdown(data):
    text = '## ChatGPT实际使用记录\n\n来源：' + data['source'] + '。\n\n'
    for record in data['records']:
        text += '### ' + record['platform'] + ' · ' + record['node_region'] + '节点\n\n'
        for label, value in [('日期', record['tested_on']), ('使用所在地', record['test_location']), ('网络运营商', record['isp']), ('节点地区', record['node_region']), ('操作', record['task']), ('结果', record['result'])]:
            text += '- ' + label + '：' + value + '\n'
        text += '\n'
    return text + '本次反馈仅覆盖上述条件下的ChatGPT问答；其他节点、时段及功能应分别记录。\n\n'
