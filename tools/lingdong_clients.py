"""Render the confirmed Lingdong client acquisition and connection steps."""
from html import escape as e


def client_faqs(data):
    ios=next(p for p in data['platforms'] if p['os']=='iOS')
    return [
        ('灵动云Windows、macOS和安卓客户端怎样下载和连接？','三个系统都使用名为灵动云的客户端。从官网首页下载对应系统的软件，打开后使用官网账号登录，再选择节点、点击连接。'),
        ('灵动云iOS使用什么应用，怎样登录？','iOS使用Nextin。使用海外Apple ID在App Store下载，打开后填写品牌识别码'+ios['brand_identifier']+'，再用官网账号登录，选择节点并点击连接。'),
        ('ldy是灵动云的优惠码吗？','ldy在本页指Nextin的品牌识别码，登录前用于识别灵动云。已确认的套餐优惠码为wsj888，与登录用的品牌识别码ldy分别填写，优惠适用范围见本页说明。')
    ]


def render_clients(data,url):
    ios=next(p for p in data['platforms'] if p['os']=='iOS')
    code=e(ios['brand_identifier'])
    return f'''<section class="section" id="lingdong-clients"><div class="lingdong-section-title"><span class="overline">CLIENTS / DOWNLOAD & CONNECT</span><h2>电脑与安卓用灵动云，iOS用Nextin。</h2><p>按系统选择客户端，再按对应方式登录和连接。</p></div><div class="lingdong-client-grid"><article class="lingdong-client-card"><span class="lingdong-index">WINDOWS / MACOS / ANDROID</span><h3>灵动云</h3><p>三个系统的下载与连接流程相同。</p><ol class="lingdong-client-steps"><li>从灵动云官网首页下载对应系统的客户端。</li><li>打开客户端，使用官网账号登录。</li><li>选择需要的节点，再点击“连接”。</li></ol><a class="lingdong-client-link" href="{url}" target="_blank" rel="sponsored noopener noreferrer">前往官网首页获取客户端 <span aria-hidden="true">↗</span></a></article><article class="lingdong-client-card is-ios" id="lingdong-ios"><span class="lingdong-index">IOS / NEXTIN</span><h3>Nextin</h3><div class="lingdong-client-code"><span>品牌识别码</span><code>{code}</code></div><ol class="lingdong-client-steps"><li>使用海外Apple ID，在App Store下载Nextin。</li><li>打开应用，先填写品牌识别码 <strong>{code}</strong>。</li><li>使用灵动云官网账号登录。</li><li>选择节点，再点击“连接”。</li></ol></article></div><div class="lingdong-source-links"><a href="data/lingdongyun-clients.json">查看客户端流程 JSON ↓</a></div></section>'''


def clients_markdown(data):
    ios=next(p for p in data['platforms'] if p['os']=='iOS')
    text='## 客户端下载与连接\n\n来源：'+data['source']+'。确认日期：'+data['updated_on']+'。\n\n'
    text+='### Windows、macOS与安卓\n\n三个系统均使用灵动云客户端。\n\n1. 官网首页下载对应系统客户端。\n2. 用官网账号登录。\n3. 选择节点。\n4. 点击连接。\n\n'
    text+='### iOS · Nextin\n\n1. 使用海外Apple ID在App Store下载Nextin。\n2. 填写品牌识别码'+ios['brand_identifier']+'。\n3. 用官网账号登录。\n4. 选择节点并点击连接。\n\n'
    return text
