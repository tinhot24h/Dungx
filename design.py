"""Shared template geometry and RGBA artwork, generated without extra packages."""
import math
import struct
import textwrap
import zlib

W, H = 720, 1280


def settings(raw):
    if not isinstance(raw, dict):
        raise ValueError('Yêu cầu không hợp lệ.')
    out = dict(raw)
    out.setdefault('template', 'pink')
    if out['template'] not in ('pink', 'blue'):
        raise ValueError('Mẫu không hợp lệ.')
    defaults = dict(fade_start=44, fade_height=18, opacity=100,
                    card_y=62, gloss=65, zoom=100, focus=50)
    bounds = dict(fade_start=(20, 65), fade_height=(5, 30), opacity=(60, 100),
                  card_y=(58, 70), gloss=(0, 100), zoom=(100, 160), focus=(0, 100))
    for key, default in defaults.items():
        value = out.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError('Thông số không hợp lệ: ' + key)
        if not bounds[key][0] <= value <= bounds[key][1]:
            raise ValueError('Thông số ngoài giới hạn: ' + key)
        out[key] = round(value)
    return out


def layout(opts):
    pink = opts['template'] == 'pink'
    y = round(H * opts['card_y'] / 100)
    title = textwrap.fill(opts['title'], 27 if pink else 31)
    body = textwrap.fill(opts['body'], 40 if pink else 44)
    if len(title.splitlines()) > 3 or len(body.splitlines()) > 6:
        raise ValueError('Chữ quá dài: tối đa 3 dòng tiêu đề và 6 dòng nội dung.')
    return [
        dict(key='title', text=title, y=y+25, size=30 if pink else 28,
             color='#fff36a' if pink else '#ffffff', bold=True, outline=1 if pink else 2),
        dict(key='body', text=body, y=y+25+len(title.splitlines())*((30 if pink else 28)+3)+22, size=22,
             color='#ffffff' if pink else '#ffed59', bold=False, outline=1),
        dict(key='cta', text=opts['cta'], y=y+342, size=22,
             color='#943956' if pink else '#ffffff', bold=True, outline=0 if pink else 1),
    ]


def artwork(opts):
    color = bytes.fromhex(opts['color'][1:])
    start = H * opts['fade_start'] / 100
    height = H * opts['fade_height'] / 100
    pixels = []
    for y in range(H):
        t = min(1, max(0, (y-start)/height))
        # Smoothstep: transparent at the top, opaque toward the background.
        alpha = round(255 * opts['opacity']/100 * t*t*(3-2*t))
        pixels.append(bytearray((color + bytes([alpha])) * W))

    def span(y, x1, x2, rgba):
        if not 0 <= y < H:
            return
        row = pixels[y]
        r, g, b, a = rgba
        for x in range(max(0, x1), min(W, x2)):
            i = 4*x
            old = row[i+3] / 255
            a0 = a/255
            combined = a0 + old*(1-a0)
            if combined:
                row[i:i+4] = bytes((round((r*a0+row[i]*old*(1-a0))/combined),
                                   round((g*a0+row[i+1]*old*(1-a0))/combined),
                                   round((b*a0+row[i+2]*old*(1-a0))/combined),
                                   round(combined*255)))

    def rounded(x, y, w, h, radius, fill):
        for yy in range(y, min(H, y+h)):
            edge = max(radius-(yy-y)-.5, (yy-(y+h-radius))+.5, 0)
            inset = radius-math.sqrt(max(0, radius*radius-edge*edge)) if edge else 0
            rgba = fill(yy-y) if callable(fill) else fill
            span(yy, math.ceil(x+inset), math.floor(x+w-inset), rgba)

    if opts['template'] == 'pink':
        y = round(H * opts['card_y']/100)
        rounded(39, y+55, 642, 282, 45, (128, 49, 85, 35))
        rounded(35, y+44, 650, 285, 45, (249, 171, 200, 255))
        rounded(39, y+46, 642, 278, 42, (255, 241, 234, 255))
        rounded(61, y+4, 598, 300, 40, (212, 85, 133, 255))
        rounded(65, y, 590, 297, 38, (255, 228, 240, 255))
        rounded(71, y+6, 578, 285, 33, (242, 122, 166, 255))
        rounded(76, y+11, 568, 275, 29,
                lambda yy: (250, 158, 190, 255) if yy > 85 else
                (250, 158+round((1-yy/85)*opts['gloss']*.5),
                 190+round((1-yy/85)*opts['gloss']*.35), 255))
        # Four-point star decorations, independent of the readable text area.
        for cx, cy, size in [(47,y+3,21),(672,y+18,24),(48,y+288,17),(670,y+306,17)]:
            for dy in range(-size, size+1):
                half = max(1, round((1-abs(dy)/size)**2*size*.45))
                span(cy+dy, cx-half, cx+half+1, (255, 247, 188, 255))
    else:
        # Subtle repeating diagonal grain, away from the live footage.
        for y in range(math.ceil(start+height), H):
            for x in range((y % 18), W, 18):
                span(y, x, x+1, (255, 255, 255, 4))
    raw = b''.join(b'\0' + row for row in pixels)

    def chunk(kind, data):
        return struct.pack('!I', len(data))+kind+data+struct.pack('!I', zlib.crc32(kind+data)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', W,H,8,6,0,0,0))
            + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))
