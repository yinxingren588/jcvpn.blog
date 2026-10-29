"""Export an attributed, shareable latency chart with true timeout handling."""
from pathlib import Path
import json
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderSVG
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from breeze_latency import COLORS, MAX_MS

root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/breezenet-latency.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
chart = Drawing(1400, 1060)


def box(x, y, width, height, fill, stroke=None, radius=0):
    chart.add(Rect(x, y, width, height, fillColor=HexColor(fill), strokeColor=HexColor(stroke) if stroke else None, rx=radius, ry=radius))


def text(x, y, value, size=16, color='#315c76', font='STSong-Light', anchor='start'):
    chart.add(String(x, y, value, fontName=font, fontSize=size, fillColor=HexColor(color), textAnchor=anchor))


box(0, 0, 1400, 1060, '#f2f7fc')
box(30, 30, 1340, 1000, '#ffffff', '#dce8f2', 22)
text(74, 987, 'BREEZENET  /  MIDDAY NODE LATENCY', 13, '#468993', 'Helvetica')
text(74, 934, '微风网络 · 午间节点延迟记录', 37, '#163d5b')
text(74, 898, '第三方截图数据重绘  |  2026-10-29 12:00（北京时间）  |  单位 ms', 17, '#66879e')
stats = data['summary']
cards = [('记录节点', str(stats['node_count'])), ('有延迟数值', str(stats['response_count'])), ('超时记录', str(stats['timeout_count'])), ('最低延迟', str(stats['min_ms']) + ' ms')]
for index, (label, value) in enumerate(cards):
    x = 74 + index * 316
    box(x, 765, 298, 101, '#fff6e8' if index == 2 else '#f2f8ff', radius=14)
    text(x + 22, 830, label, 15, '#66869c')
    text(x + 22, 790, value, 29, '#ca7d23' if index == 2 else '#226da1', 'Helvetica-Bold')
text(74, 722, '各分组延迟中位数', 23, '#244e6c')
text(1324, 723, '仅统计有数值记录；日本直连单列', 13, '#7a94a7', anchor='end')
left, right, top, step = 230, 1070, 665, 46
for tick in range(0, MAX_MS + 1, 20):
    x = left + (right - left) * tick / MAX_MS
    chart.add(Line(x, 392, x, 687, strokeColor=HexColor('#e7f0f6'), strokeWidth=1))
    text(x, 374, str(tick), 11, '#8ca2b3', 'Helvetica', anchor='middle')
text(1132, 695, '数值 / 总数', 11, '#7290a4')
text(1267, 695, '超时', 11, '#7290a4', anchor='middle')
for index, region in enumerate(data['regions']):
    y = top - index * step
    text(74, y - 5, region['region'], 17)
    median = region['median_ms']
    if median is None:
        box(left, y - 12, right - left, 24, '#fff6e9', radius=5)
        text(left + 18, y - 5, '无数值 · 全部超时', 14, '#b18a56')
    else:
        width = (right - left) * median / MAX_MS
        box(left, y - 10, width, 21, COLORS[region['region']], radius=4)
        text(left + width + 12, y - 5, f'{median:g} ms', 14, '#376d8c', 'Helvetica-Bold')
    text(1165, y - 5, f'{region["response_count"]} / {region["count"]}', 15, '#426c89', 'Helvetica', anchor='middle')
    text(1267, y - 5, str(region['timeout_count']), 15, '#cf7b21' if region['timeout_count'] else '#83a1b7', 'Helvetica-Bold', anchor='middle')
box(74, 185, 1250, 150, '#f6f9fd', radius=14)
text(96, 301, '采样条件与统计口径', 18, '#355f7d')
text(96, 271, '上海 / 电信 · Windows版“微风网络”客户端 · 39条数值范围11—111ms。', 15, '#64839b')
text(96, 243, '日本01—10本次均超时，日本01—04-直连另列；香港13未在资料中展示。', 15, '#64839b')
text(96, 215, '超时不作0ms；单次延迟不代表下载速度、长期可用率或实时监测。', 15, '#64839b')
text(74, 146, '依据第三方提供的5张截图整理，未重新测量，未发布原照片。', 13, '#7893a7')
text(74, 110, '叮当观察  /  jcvpn.blog', 15, '#416e8d')
text(1324, 110, '2026-10-29 12:00（北京时间） · 上海电信', 12, '#7e97a9', anchor='end')
path = root / 'assets/breezenet-latency.svg'
renderSVG.drawToFile(chart, str(path))
svg = path.read_text(encoding='utf-8')
svg = svg.replace('<svg ', '<svg role="img" aria-label="微风网络午间节点延迟记录" ', 1)
svg = svg.replace('<title>...</title>', '<title>微风网络2026年10月29日午间延迟记录</title><style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif!important}</style>', 1)
svg = svg.replace('<desc>...</desc>', '<desc>2026年10月29日12:00北京时间，上海电信，Windows版微风网络客户端，第三方截图记录52个节点，39条数值、13条超时；日本直连单列。不是实时监测。</desc>', 1)
path.write_text(svg, encoding='utf-8')
print('Breezenet standalone SVG chart exported: 1400 x 1060.')
