"""Draw a data-only Twilight latency overview as PNG and SVG."""
from pathlib import Path
from html import escape
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/muguang-latency.json').read_text(encoding='utf-8'))
W,H=1600,1120
canvas=Image.new('RGB',(W,H),'#f5f2fa')
draw=ImageDraw.Draw(canvas)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">暮光网络上午节点延迟记录</title><desc id="desc">2026年10月30日10时，上海电信，Windows版暮光加速客户端，60条数值，0条超时。</desc>']
fonts={}


def box(x,y,w,h,fill,stroke=None,radius=0):
    draw.rounded_rectangle((x,y,x+w,y+h),radius=radius,fill=fill,outline=stroke,width=1)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>')


def text(x,y,value,size=18,color='#6e6281',bold=False,anchor='start'):
    key=(size,bold)
    if key not in fonts:
        fonts[key]=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc',size)
    draw.text((x,y),value,font=fonts[key],fill=color,anchor={'start':'ls','middle':'ms','end':'rs'}[anchor])
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(value)}</text>')


def line(x1,y1,x2,y2,color='#e9e2f0'):
    draw.line((x1,y1,x2,y2),fill=color,width=1)
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"/>')


s=data['summary']
box(36,36,1528,1048,'#fff','#e3d9ed',24)
text(90,99,'TWILIGHT / MORNING NODE LATENCY',17,'#9782b1',True)
text(90,160,'暮光网络 · 上午节点延迟记录',42,'#53406f',True)
text(90,204,'2026-10-30 10:00（北京时间）  |  上海电信  |  Windows版暮光加速客户端',19,'#8b8199')
stats=[('截图记录',str(s['node_count'])+' 条'),('有延迟数值',str(s['response_count'])+' 条'),('本次超时','0 条'),('最低延迟',str(s['min_ms'])+' ms')]
for i,(label,value) in enumerate(stats):
    x=90+i*361
    box(x,244,337,120,'#f6f1fb',None,15)
    text(x+24,282,label,17,'#9385a2')
    text(x+24,335,value,37,'#8161a4',True)
text(90,420,'各地区延迟中位数',25,'#69547f',True)
text(1510,420,'单位 ms · 右侧为中位数与范围',16,'#93899e',anchor='end')
left,right=360,1200
for tick in (0,50,100,150):
    x=left+(right-left)*tick/150
    line(x,460,x,760)
    text(x,790,str(tick),15,'#9a90a5',anchor='middle')
for i,g in enumerate(data['regions']):
    y=490+i*60
    text(90,y,g['region'],21,'#6b5a7e',True)
    text(90,y+23,str(g['count'])+'条数值 · 0条超时',14,'#9b90a7')
    box(left,y-16,right-left,22,'#f2edf7',None,4)
    box(left,y-16,(right-left)*g['median_ms']/150,22,g['color'],None,4)
    text(1260,y+2,f"{g['median_ms']:g} / {g['min_ms']}—{g['max_ms']}",19,'#75618d',True)
box(90,833,1420,165,'#f8f5fc',None,16)
text(116,870,'采样与统计说明',21,'#766189',True)
text(116,909,f"60条数值范围{s['min_ms']}—{s['max_ms']}ms，总体中位数{s['median_ms']:g}ms；本次截图未出现超时。",18,'#8e819a')
text(116,945,'每节点仅一条记录，不推算下载速度、长期可用率或实时状态。',18,'#8e819a')
text(116,977,'根据6张客户端截图重绘，未重新测量；原截图不在博客发布。',18,'#8e819a')
text(90,1047,'叮当观察 / jcvpn.blog',18,'#857197',True)
text(1510,1047,'2026-10-30 10:00 · 上海电信 · 上午记录',16,'#9b90a7',anchor='end')
svg.append('</svg>')
(ROOT/'assets/muguang-latency-overview.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
canvas.save(ROOT/'assets/muguang-latency-overview.png',optimize=True)
print(f'Exported Twilight latency PNG and SVG: {W}x{H}.')
