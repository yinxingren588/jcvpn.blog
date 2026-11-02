"""Render only the platform names and connection flows confirmed for FlyV."""
from html import escape as e


def client_faqs(data):
    identifier=data['platforms']['ios']['identifier']
    return [
        ('飞v在Windows、macOS和安卓使用哪个客户端？','这三个平台均使用名为“飞v”的客户端，从官网首页下载对应版本，用飞v官网账号登录，选择节点后点击连接。'),
        ('飞v的iOS客户端和品牌识别码是什么？','iOS使用Nextin，品牌识别码为'+identifier+'。使用海外Apple ID在App Store下载Nextin，填写识别码后用飞v官网账号登录，再选择节点、点击连接。'),
        ('飞v客户端的版本和系统要求在哪里核对？','目前已确认四个平台的名称与基本流程，具体版本和最低系统要求尚未提供。下载时请查看对应下载页或应用页面的说明。')
    ]


def render_clients(data,entry_url):
    assert data['collection_status']=='basic_flows_confirmed'
    labels={'windows':'Windows','macos':'macOS','android':'安卓 Android','ios':'iPhone / iPad · iOS'}
    cards=[]
    for key,label in labels.items():
        platform=data['platforms'][key]
        steps=''.join('<li><span class="flyv-client-step-number" aria-hidden="true">'+str(i)+'</span><div><strong>'+e(step['title'])+'</strong><p>'+e(step['description'])+'</p></div></li>' for i,step in enumerate(platform['connection_steps'],1))
        identifier='<div class="flyv-client-identifier"><span>Nextin品牌识别码</span><code id="flyv-ios-identifier">'+e(platform['identifier'])+'</code></div>' if key=='ios' else ''
        action='<p class="flyv-client-store">在App Store中搜索并下载 Nextin。</p>' if key=='ios' else '<a class="flyv-client-entry" href="'+e(entry_url,quote=True)+'" target="_blank" rel="sponsored noopener noreferrer">前往飞v官网入口 <span aria-hidden="true">↗</span></a>'
        cards.append('<article class="flyv-client" id="flyv-client-'+key+'"><span class="overline">'+e(label)+'</span><h3>'+e(platform['name'])+' 客户端</h3>'+identifier+'<ol class="flyv-client-steps">'+steps+'</ol>'+action+'</article>')
    return '<section class="section" id="flyv-clients" aria-labelledby="flyv-clients-title"><span class="overline">DOWNLOAD, SIGN IN & CONNECT</span><h2 id="flyv-clients-title">飞v各平台下载与连接教程</h2><p class="flyv-section-lead">Windows、macOS和安卓均使用“飞v”；iOS使用Nextin，品牌识别码为 <code>flyv</code>。按自己的设备查看对应步骤。</p><div class="flyv-client-grid">'+''.join(cards)+'</div><p class="flyv-material-note">这些使用流程由站长逐项确认；具体版本和最低系统要求以对应下载页或应用页面说明为准。测速所使用的客户端条件，在对应记录中分别列明。</p><a class="flyv-client-source" href="data/feiv-clients.json">查看四个平台的客户端资料 JSON ↓</a></section>'
