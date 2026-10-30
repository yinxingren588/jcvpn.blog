"""Render Lingdong's supplied application feedback with its own conditions."""
from html import escape as e


def access_summary(data):
    r = data['records'][0]
    return ('根据博客站长提供的实际使用反馈，' + r['tested_on'] + ' ' + r['tested_time'] +
            '（北京时间），在' + r['test_location'] + '使用' + r['isp'] + '网络，连接灵动云' +
            r['node_region'] + '节点，ChatGPT' + r['result'] + '。')


def access_faqs(data):
    return [('灵动云有ChatGPT实际使用记录吗？', access_summary(data) + '本次记录对应上述条件下的问答操作。')]


def render_access(data):
    cards = []
    for r in data['records']:
        facts = [('记录时间', r['tested_on'] + ' ' + r['tested_time'] + '（北京时间）'),
                 ('使用所在地', r['test_location']), ('网络运营商', r['isp']),
                 ('节点地区', r['node_region']), ('验证操作', r['task'])]
        fields = ''.join('<div><dt>' + e(k) + '</dt><dd>' + e(v) + '</dd></div>' for k, v in facts)
        cards.append('<article class="access-record"><div class="access-record-head"><span class="access-record-source">' +
                     e(data['source']) + '</span><span class="access-record-status">本次问答正常</span></div><h3>' +
                     e(r['platform']) + ' · ' + e(r['node_region']) + '节点</h3><dl class="access-record-facts">' +
                     fields + '</dl><div class="access-record-result"><span>使用结果</span><p>' + e(r['result']) +
                     '。</p></div><p class="access-record-note">本次反馈对应上述条件下的ChatGPT问答；其他节点、时段和功能应分别记录。</p></article>')
    return ('<section class="section" id="lingdong-access-records"><div class="lingdong-section-title">' +
            '<span class="overline">CHATGPT / RECORDED USE</span><h2>12:00的ChatGPT问答记录。</h2>' +
            '<p>上海电信网络，连接新加坡节点。按站长提供的实际使用反馈整理。</p></div>' +
            '<div class="lingdong-access-cards">' + ''.join(cards) + '</div><div class="lingdong-source-links">' +
            '<a href="data/lingdongyun-access-records.json">查看ChatGPT使用记录 JSON ↓</a></div></section>')


def access_markdown(data):
    text = '## ChatGPT实际使用记录\n\n来源：' + data['source'] + '。\n\n'
    for r in data['records']:
        for k, v in [('时间', r['tested_on'] + ' ' + r['tested_time'] + '（北京时间）'),
                     ('所在地', r['test_location']), ('运营商', r['isp']), ('节点地区', r['node_region']),
                     ('操作', r['task']), ('结果', r['result'])]:
            text += '- ' + k + '：' + v + '\n'
        text += '\n'
    return text + '本次反馈仅覆盖上述条件下的ChatGPT问答，其他节点、时段及功能应分别记录。\n\n'
