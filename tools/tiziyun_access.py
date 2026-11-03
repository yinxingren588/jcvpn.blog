"""Publish LadderCloud's separately confirmed ChatGPT task feedback."""
from datetime import date, time
from html import escape as e


def access_record(data):
    assert data['brand_id'] == 'tiziyun' and data['collection_status'] == 'core_conditions_confirmed'
    assert len(data['records']) == 1
    record = data['records'][0]
    for key in ('tested_on', 'tested_time', 'test_location', 'isp', 'node_region',
                'client', 'client_name', 'client_platform', 'result'):
        assert record[key], key
    date.fromisoformat(record['tested_on'])
    time.fromisoformat(record['tested_time'])
    assert record['reported_time_precision'] == 'hour'
    assert record['platform'] == 'ChatGPT' and record['status'] == 'reported_success'
    assert data['independently_retested'] is False and record['independently_retested'] is False
    return record


def access_faqs(data):
    record = access_record(data)
    return [
        ('梯子云有ChatGPT的实际问答反馈吗？',
         record['scope'] + '这是站长提供的实际使用反馈，本站未独立复测。'),
        ('这条问答反馈能说明梯子云所有节点和AI功能都可用吗？',
         '本条记录覆盖所列日期、时段、网络、客户端和新加坡节点下的发送问题与接收回答动作。其他节点、模型、API、文件上传或其他时段的表现需分别记录。')
    ]


def render_access(data):
    record = access_record(data)
    facts = [
        ('测试时间', record['tested_on'] + ' ' + record['tested_time'] + '（北京时间，按小时提供）'),
        ('所在地 / 运营商', record['test_location'] + ' / ' + record['isp']),
        ('节点地区', record['node_region'] + '；具体编号未提供'),
        ('连接客户端', record['client'] + '；具体版本未提供')
    ]
    details = ''.join('<div><dt>' + e(label) + '</dt><dd>' + e(value) + '</dd></div>' for label, value in facts)
    return ('<section class="section" id="tiziyun-access" aria-labelledby="tiziyun-access-title">'
            '<span class="overline">CHATGPT / REPORTED USE</span>'
            '<h2 id="tiziyun-access-title">新加坡节点，ChatGPT问答反馈。</h2>'
            '<article class="tiziyun-access-card"><p class="tiziyun-access-label">站长实际使用反馈 · 未独立复测</p>'
            '<p class="tiziyun-access-result">' + e(record['result']) + '。</p>'
            '<dl class="tiziyun-access-facts">' + details + '</dl>'
            '<p class="tiziyun-note">记录操作：' + e(record['task'])
            + '。日期、时刻、网络、节点地区和客户端均针对这次问答逐项确认。'
            '记录覆盖当次问答；其他节点、时段、模型、API和文件上传需分别验证。</p></article>'
            '<div class="tiziyun-source-links"><a href="data/tiziyun-access-records.json">问答反馈与测试条件 JSON ↓</a>'
            '<a href="topic-reviews-guide.html#chatgpt-feedback-scope">阅读ChatGPT反馈适用范围 →</a></div></section>')
