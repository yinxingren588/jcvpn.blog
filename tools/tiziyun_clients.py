"""Render the platform flows confirmed by the site owner for LadderCloud."""
from html import escape as e


def client_faqs(data):
    identifier = data['platforms']['ios']['identifier']
    return [
        ('梯子云在Windows、macOS和安卓使用哪个客户端？',
         '三个平台均使用名为“梯子云”的客户端。从官网首页下载对应版本，使用梯子云官网注册的账号登录，选择节点后点击连接。'),
        ('梯子云的iOS客户端和品牌识别码是什么？',
         'iOS使用Nextin，品牌识别码为' + identifier + '。使用海外Apple ID从App Store下载Nextin，打开后填写识别码，用梯子云官网账号登录，再选择节点、点击连接。'),
        ('梯子云客户端的版本和系统要求在哪里核对？',
         '四个平台的客户端名称与基本流程由站长逐项确认。具体版本与最低系统要求尚未提供，请在对应下载页或应用页面核对。')
    ]


def render_clients(data, entry_url):
    assert data['brand_id'] == 'tiziyun'
    assert data['collection_status'] == 'basic_flows_confirmed'
    labels = {'windows': 'Windows', 'macos': 'macOS',
              'android': '安卓 Android', 'ios': 'iPhone / iPad · iOS'}
    identifier = data['platforms']['ios']['identifier']
    cards = []
    for key, label in labels.items():
        platform = data['platforms'][key]
        assert platform['connection_confirmed_on'] and platform['connection_steps']
        steps = ''.join('<li><strong>' + e(step['title']) + '</strong><p>'
                        + e(step['description']) + '</p></li>'
                        for step in platform['connection_steps'])
        code = ('<p class="tiziyun-client-identifier">Nextin品牌识别码：<code>'
                + e(identifier) + '</code></p>') if key == 'ios' else ''
        action = ('<p class="tiziyun-note">在App Store中搜索并下载 Nextin。</p>' if key == 'ios'
                  else '<a class="tiziyun-client-entry" href="' + e(entry_url, quote=True)
                  + '" target="_blank" rel="sponsored noopener noreferrer">前往梯子云官网入口 ↗</a>')
        cards.append('<article class="tiziyun-client" id="tiziyun-client-' + key
                     + '"><span class="overline">' + e(label) + '</span><h3>'
                     + e(platform['name']) + ' 客户端</h3>' + code
                     + '<ol class="tiziyun-client-steps">' + steps + '</ol>' + action + '</article>')
    return ('<section class="section" id="tiziyun-clients" aria-labelledby="tiziyun-clients-title">'
            '<span class="overline">DOWNLOAD, SIGN IN & CONNECT</span>'
            '<h2 id="tiziyun-clients-title">梯子云各平台下载与连接教程</h2>'
            '<p class="tiziyun-lead">Windows、macOS和安卓使用“梯子云”客户端；iPhone与iPad使用Nextin，'
            '品牌识别码为 <code>' + e(identifier) + '</code>。按设备查看对应步骤。</p>'
            '<div class="tiziyun-client-grid">' + ''.join(cards) + '</div>'
            '<p class="tiziyun-note">基础流程由站长于' + e(data['confirmed_on'])
            + '逐项确认，未在本站独立复测。具体版本与最低系统要求以对应下载页或应用页面说明为准。'
            '本页节点截图的采样客户端条件另行列明。</p>'
            '<div class="tiziyun-source-links"><a href="data/tiziyun-clients.json">四个平台客户端资料 JSON ↓</a></div></section>')
