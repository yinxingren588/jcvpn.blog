"""Render attributed application-access feedback without inferring other tests."""
from html import escape as e


def render(data):
    cards = []
    for record in data['records']:
        cards.append('<article class="access-record" id="breeze-access-' + e(record['id'], quote=True) + '"><div class="access-record-head"><span class="access-record-source">' + e(data['source']) + '</span><span class="access-record-status">本次问答正常</span></div><h3>' + e(record['platform']) + ' · ' + e(record['node_region']) + '节点</h3><dl class="access-record-facts"><div><dt>记录日期</dt><dd>' + e(record['tested_on']) + '</dd></div><div><dt>测试所在地</dt><dd>' + e(record['test_location']) + '</dd></div><div><dt>节点地区</dt><dd>' + e(record['node_region']) + '</dd></div></dl><div class="access-record-result"><span>问答操作与结果</span><p>' + e(record['result']) + '。</p></div><p class="access-record-note">本记录仅说明上述日期、所在地和节点地区下的ChatGPT问答操作；其他节点、时段与功能需分别验证。</p></article>')
    return '<section class="section access-records-panel" id="breeze-access-records" aria-labelledby="breeze-access-title"><div class="breeze-section-title"><span class="overline">APPLICATION ACCESS / CHATGPT</span><h2 id="breeze-access-title">ChatGPT访问记录：日期、节点与结果。</h2><p>按站长提供的实际使用反馈，记录具体完成的访问操作。</p></div><div class="access-records-subtitle"></div>' + ''.join(cards) + '<div class="breeze-source-links"><a href="data/breezenet-access-records.json">查看访问记录 JSON ↓</a></div></section>'


def markdown(data):
    output = '## ChatGPT实际使用记录\n\n资料来源：' + data['source'] + '。\n\n'
    for record in data['records']:
        output += '### ' + record['platform'] + ' · ' + record['node_region'] + '节点\n\n- 日期：' + record['tested_on'] + '\n- 测试所在地：' + record['test_location'] + '\n- 节点地区：' + record['node_region'] + '\n- 操作：' + record['task'] + '\n- 结果：' + record['result'] + '。\n\n'
    return output + '本记录只说明对应条件下的ChatGPT问答操作，其他节点、时段与功能应分别验证。\n\n'
