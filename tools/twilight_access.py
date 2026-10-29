"""Render supplied Twilight application feedback with its actual test conditions."""
from html import escape as e


def access_summary(data):
    record=data['records'][0]
    return ('根据站长提供的实际使用反馈，'+record['tested_on']+' '+record['tested_time']+
            '（北京时间），在'+record['test_location']+'使用'+record['isp']+'网络，连接暮光网络'+
            record['node_region']+'节点，'+record['platform']+record['result']+'。')


def access_faqs(data):
    return [('暮光网络有ChatGPT实际使用记录吗？',access_summary(data)+'本次记录对应上述条件下的问答操作。')]


def render_access(data):
    cards=[]
    for record in data['records']:
        facts=[('记录时间',record['tested_on']+' '+record['tested_time']+'（北京时间）'),
               ('使用所在地',record['test_location']),('网络运营商',record['isp']),
               ('节点地区',record['node_region']),('验证操作',record['task'])]
        fields=''.join('<div><dt>'+e(label)+'</dt><dd>'+e(value)+'</dd></div>' for label,value in facts)
        cards.append('<article class="access-record"><div class="access-record-head"><span class="access-record-source">'+
                     e(data['source'])+'</span><span class="access-record-status">本次问答正常</span></div><h3>'+e(record['platform'])+
                     ' · '+e(record['node_region'])+'节点</h3><dl class="access-record-facts">'+fields+
                     '</dl><div class="access-record-result"><span>使用结果</span><p>'+e(record['result'])+
                     '。</p></div><p class="access-record-note">本次反馈仅覆盖上述条件下的ChatGPT问答；其他节点、时段和功能应分别记录。</p></article>')
    return ('<section class="section" id="twilight-access-records"><div class="twilight-section-title"><span class="overline">CHATGPT / RECORDED USE</span>'+
            '<h2>23:00的ChatGPT问答记录。</h2><p>上海电信网络，连接新加坡节点。按站长提供的实际使用反馈整理。</p></div>'+
            '<div class="twilight-access-cards">'+''.join(cards)+'</div><div class="twilight-source-links">'+
            '<a href="data/muguang-access-records.json">查看ChatGPT使用记录 JSON ↓</a></div></section>')


def access_markdown(data):
    text='## ChatGPT实际使用记录\n\n来源：'+data['source']+'。\n\n'
    for record in data['records']:
        for label,value in [('时间',record['tested_on']+' '+record['tested_time']+'（北京时间）'),
                            ('所在地',record['test_location']),('运营商',record['isp']),('节点地区',record['node_region']),
                            ('操作',record['task']),('结果',record['result'])]:
            text+='- '+label+'：'+value+'\n'
        text+='\n'
    return text+'本次反馈仅覆盖上述条件下的ChatGPT问答，其他节点、时段及功能应分别记录。\n\n'
