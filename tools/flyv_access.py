"""Publish the separately confirmed FlyV ChatGPT feedback with its own context."""
from datetime import date, time
from html import escape as e


def access_record(data):
    assert data['collection_status'] == 'core_conditions_confirmed'
    assert len(data['records']) == 1
    record = data['records'][0]
    for key in ('tested_on', 'tested_time', 'test_location', 'isp', 'node_region',
                'client_name', 'client_platform', 'result'):
        assert record[key], key
    date.fromisoformat(record['tested_on'])
    time.fromisoformat(record['tested_time'])
    assert record['platform'] == 'ChatGPT' and record['status'] == 'reported_success'
    assert not data['independently_retested'] and not record['independently_retested']
    return record


def access_faqs(data):
    r = access_record(data)
    answer = (r['tested_on']+' '+r['tested_time']+'（北京时间，按小时提供），站长在'+
              r['test_location']+'使用'+r['isp']+'网络，通过'+r['client']+'连接'+
              r['node_region']+'节点，已报告ChatGPT能够正常发送问题并收到回答。'+
              '这是站长的实际使用反馈，本站未独立复测；不据此推断其他节点、所有模型、API或其他功能的表现。')
    return [('飞v有ChatGPT的实际问答反馈吗？', answer)]


def render_access(data):
    r = access_record(data)
    facts = [
        ('测试时间', r['tested_on']+' '+r['tested_time']+'（北京时间，按小时提供）'),
        ('所在地 / 运营商', r['test_location']+' / '+r['isp']),
        ('节点地区', r['node_region']+'；具体编号未提供'),
        ('连接客户端', r['client']+'；具体版本未提供'),
    ]
    details = ''.join('<div><dt>'+e(label)+'</dt><dd>'+e(value)+'</dd></div>' for label, value in facts)
    return '''<section class="section flyv-access-section" id="flyv-access" aria-labelledby="flyv-access-title">
<span class="overline">CHATGPT / REPORTED USE</span><h2 id="flyv-access-title">新加坡节点，ChatGPT问答反馈。</h2>
<article class="flyv-access-card"><div class="flyv-access-head"><span>站长实际使用反馈 · 未独立复测</span><span class="flyv-access-status">本次问答正常</span></div>
<p class="flyv-access-result">'''+e(r['result'])+'''。</p><dl class="flyv-access-facts">'''+details+'''</dl>
<p class="flyv-access-scope">记录操作：'''+e(r['task'])+'''。本条日期、时刻、网络、节点地区和客户端均针对这次问答逐项确认。记录覆盖当次问答，其他节点、时段、模型、API与文件上传需分别验证。</p>
</article><div class="flyv-source-links"><a href="data/feiv-access-records.json">查看问答反馈源资料 JSON ↓</a><a href="topic-reviews-guide.html#chatgpt-feedback-scope">阅读ChatGPT反馈的适用范围 →</a></div></section>'''
