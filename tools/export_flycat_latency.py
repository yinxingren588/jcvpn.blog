"""Draw a new data chart (PNG and SVG); source screenshots are never embedded."""
from pathlib import Path
from html import escape
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/feimaoyun-latency.json').read_text(encoding='utf-8'))
W,H=1600,1500
image=Image.new('RGB',(W,H),'#f2f7fc')
draw=ImageDraw.Draw(image)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">飞猫云晚高峰节点延迟记录</title><desc id="desc">2026年10月29日20时，上海电信，Windows版飞猫云客户端，69条截图记录，63条数值，6条超时，延迟29至345ms。</desc>']
fonts={}


def box(x,y,w,h,fill,stroke=None,radius=0):
    draw.rounded_rectangle((x,y,x+w,y+h),radius=radius,fill=fill,outline=stroke,width=1)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>')


def text(x,y,value,size=18,color='#3a627b',bold=False,anchor='start'):
    key=(size,bold)
    if key not in fonts:
        fonts[key]=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc',size)
    draw.text((x,y),value,font=fonts[key],fill=color,anchor={'start':'ls','middle':'ms','end':'rs'}[anchor])
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(value)}</text>')


def line(x1,y1,x2,y2,color='#e5eef5',width=1):
    draw.line((x1,y1,x2,y2),fill=color,width=width)
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')


box(36,36,1528,1428,'#ffffff','#d9e7f2',24)
text(90,99,'FLYCAT / PEAK-HOUR NODE LATENCY',17,'#a17b3e',True)
text(90,163,'飞猫云 · 晚高峰节点延迟记录',42,'#1e506f',True)
text(90,205,'2026-10-29 20:00（北京时间）  |  上海电信  |  Windows版飞猫云客户端',19,'#708c9e')
s=data['summary']
stats=[('截图记录',str(s['node_count'])+' 条'),('有延迟数值',str(s['response_count'])+' 条'),('本次超时',str(s['timeout_count'])+' 条'),('最低延迟',str(s['min_ms'])+' ms')]
for i,(label,value) in enumerate(stats):
    x=90+i*361
    box(x,245,337,120,'#fff6e7' if i==2 else '#eff6fc',None,15)
    text(x+24,282,label,17,'#738d9f')
    text(x+24,335,value,37,'#bc8537' if i==2 else '#28769f',True)
text(90,421,'各分组延迟中位数',25,'#315e79',True)
text(1510,421,'单位 ms · 超时单独计数',15,'#8098a8',anchor='end')
left,right=470,1220
for tick in range(0,401,100):
    x=left+(right-left)*tick/400
    line(x,464,x,1060)
    text(x,1090,str(tick),14,'#829bab',anchor='middle')
text(1270,454,'中位数 / 最小—最大值',14,'#7a93a3')
for i,group in enumerate(data['regions']):
    y=495+i*54
    text(90,y-2,group['region'],18,'#466b82',True)
    text(90,y+20,f"{group['response_count']}条数值 / {group['timeout_count']}条超时",13,'#8198a7')
    if group['median_ms'] is None:
        box(left,y-17,right-left,25,'#fff6e8',None,5)
        text(left+14,y+2,'本组无延迟数值',14,'#b48d53')
        text(1270,y+2,'仅超时记录',15,'#b48d53')
    else:
        box(left,y-15,right-left,20,'#f1f6fa',None,4)
        box(left,y-15,(right-left)*group['median_ms']/400,20,group['color'],None,4)
        text(1270,y+2,f"{group['median_ms']:g} / {group['min_ms']}—{group['max_ms']}",16,'#4d748a',True)
box(90,1130,1420,230,'#f5f9fc',None,16)
text(116,1168,'采样与统计说明',21,'#456f88',True)
text(116,1207,'63条数值范围29—345ms，总体中位数80ms；6条超时保留，不作0ms。',18,'#718b9c')
text(116,1243,'两组直连代码与中文地区矛盾，按截图原名分组；香港09未出现，不补记录。',18,'#718b9c')
text(116,1279,'截图名称含IEPL字样，品牌介绍仍按站长确认保留IPLC；原始名称见完整数据。',18,'#718b9c')
text(116,1315,'本图依据6张客户端截图重绘，未重新测量；单次延迟不推断下载速度或长期可用率。',18,'#718b9c')
text(90,1415,'叮当观察  /  jcvpn.blog',19,'#47748c',True)
text(1510,1415,'2026-10-29 20:00 · 上海电信 · 晚高峰快照',16,'#8199a8',anchor='end')
svg.append('</svg>')
(ROOT/'assets/feimaoyun-latency-overview.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
image.save(ROOT/'assets/feimaoyun-latency-overview.png',optimize=True)
print(f'Exported Flycat latency PNG and SVG: {W}x{H}.')
