"""Render Flycat's confirmed platforms, identifier and connection workflows."""
from html import escape as e


def client_faqs(data):
    native = data['native_client']
    ios = data['ios_client']
    return [
        ('飞猫云在Windows、macOS和安卓上用什么客户端？', '这三个平台均使用飞猫云品牌自研客户端，操作流程相同：使用官网账号登录，选择节点，再点击连接。'),
        ('飞猫云自研客户端需要导入订阅吗？', '本次确认的自研客户端流程为官网账号直接登录，然后选择节点并点击连接。Windows、macOS和Android均按这个流程使用。'),
        ('飞猫云的iOS客户端叫什么，识别码是什么？', 'iOS使用' + ios['name'] + '，飞猫云识别码为' + ios['identifier'] + '。Windows、macOS和安卓使用飞猫云自研客户端，按各自平台选择对应软件。'),
        ('iOS上的Nextin如何登录并连接飞猫云？', '打开Nextin，先填写飞猫云识别码' + ios['identifier'] + '，再使用自己的飞猫云官网账号登录。登录后选择节点，点击连接。识别码不包含花括号。'),
        ('飞猫云自研客户端在哪里下载？', 'Windows、macOS和Android的飞猫云自研客户端，都可从飞猫云官网首页直接下载。选择与自己设备系统对应的版本；iOS使用Nextin。')
    ]


def render_clients(data):
    native = data['native_client']
    ios = data['ios_client']
    steps = ''.join('<li><span class="flycat-step-number" aria-hidden="true">' + str(index).zfill(2) + '</span><div><h4>' + e(step['title']) + '</h4><p>' + e(step['description']) + '</p></div></li>' for index, step in enumerate(native['steps'], 1))
    ios_steps = ''.join('<li><span class="flycat-step-number" aria-hidden="true">' + str(index).zfill(2) + '</span><div><h4>' + e(step['title']) + '</h4><p>' + e(step['description']) + '</p></div></li>' for index, step in enumerate(ios['connection_steps'], 1))
    systems = ''.join('<span>' + e(platform) + '</span>' for platform in native['platforms'])
    return f'''<section class="section" id="flycat-clients"><div class="flycat-section-title"><span class="overline">CLIENTS & GETTING CONNECTED</span><h2>电脑与安卓使用自研客户端，iOS使用Nextin。</h2><p>按设备选择客户端。自研客户端直接用官网账号登录；iOS先填写识别码，再登录账号并连接。</p></div><div class="flycat-client-grid"><article class="flycat-client-card"><span class="flycat-plan-label">品牌自研客户端</span><h3>{e(native['name'])}</h3><div class="flycat-client-systems">{systems}</div><p class="flycat-client-summary">用官网账号登录，选择节点，再点击连接。</p><ol class="flycat-client-steps">{steps}</ol></article><article class="flycat-client-card is-ios"><span class="flycat-plan-label">iOS客户端</span><h3>{e(ios['name'])}</h3><div class="flycat-client-systems"><span>iPhone / iOS</span></div><div class="flycat-client-code"><span>飞猫云识别码</span><code>{e(ios['identifier'])}</code><p>输入小写字母 <b>{e(ios['identifier'])}</b> 即可，识别码不包含花括号。</p></div><ol class="flycat-client-steps">{ios_steps}</ol></article></div><p class="flycat-note">客户端类型、识别码及各平台登录与连接流程由博客站长于{e(data['confirmed_on'])}确认。具体版本与系统要求请核对对应客户端说明。</p></section>'''


def clients_markdown(data):
    native = data['native_client']
    ios = data['ios_client']
    text = '## 客户端与连接流程\n\n来源：' + data['source'] + '；确认日期：' + data['confirmed_on'] + '。\n\n'
    text += '### Windows、macOS、Android\n\n使用飞猫云自研客户端，三个平台流程相同。\n\n'
    text += ''.join(str(index) + '. ' + step['description'] + '\n' for index, step in enumerate(native['steps'], 1))
    text += '\n### iOS\n\n使用' + ios['name'] + '，飞猫云品牌识别码为`' + ios['identifier'] + '`，不包含花括号。\n\n'
    text += ''.join(str(index) + '. ' + step['description'] + '\n' for index, step in enumerate(ios['connection_steps'], 1)) + '\n'
    return text
