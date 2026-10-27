"""Shared geometry, editable text layout and portable RGBA frame artwork."""
import math
import re
import struct
import zlib
from fonts import FONTS, width, wrap

W, H = 720, 1280
FRAMES = ('pink','glass','gold','minimal','neon','ribbon','none','custom')


def settings(raw):
    if not isinstance(raw, dict):
        raise ValueError('Yêu cầu không hợp lệ.')
    out = dict(raw)
    out.setdefault('units','percent')
    if out['units'] not in ('px','percent'):
        raise ValueError('Đơn vị không hợp lệ.')
    px = out['units'] == 'px'
    out.setdefault('template','pink')
    if out['template'] not in ('pink','blue'):
        raise ValueError('Mẫu không hợp lệ.')
    out.setdefault('frame_style','pink' if out['template']=='pink' else 'none')
    if out['frame_style'] not in FRAMES:
        raise ValueError('Khung không hợp lệ.')
    out.setdefault('background','solid')
    if out['background'] not in ('solid','gradient'):
        raise ValueError('Kiểu nền không hợp lệ.')
    for key,default in dict(color='#fad9e9',color2='#cbb9ef',frame_color='#f69fbe',border_color='#fff3e7',
                            title_color='#fff36a',body_color='#ffffff',title_outline_color='#342333',
                            body_outline_color='#342333').items():
        out.setdefault(key,default)
        if not isinstance(out[key],str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',out[key]):
            raise ValueError('Mã màu không hợp lệ: '+key)
    spec = dict(fade_start=(44,0,90),fade_height=(18,2,60),opacity=(100,0,100),
                frame_x=(50,0,100),frame_y=(62,0,95),frame_width=(90,20,100),
                frame_height=(26,8,60),frame_opacity=(100,0,100),gloss=(65,0,100),
                zoom=(100,50,200),video_x=(0,-80,80),video_y=(0,-80,80))
    if px:
        spec.update(fade_start=(563,0,1152),fade_height=(230,16,768),
                    frame_x=(36,-720,720),frame_y=(794,-1280,1280),
                    frame_width=(648,80,720),frame_height=(333,60,1000),
                    video_x=(0,-2160,720),video_y=(0,-3840,1280),
                    video_width=(720,180,2160),video_height=(1280,320,3840))
    for name in ('title','body'):
        spec.update({name+'_size':(30 if name=='title' else 22,12,144),
                     name+'_x':(50,0,100),name+'_y':(64 if name=='title' else 73,0,98),
                     name+'_width':(76,20,100),name+'_outline':(1,0,5),name+'_gap':(4,0,24)})
        if px:
            spec.update({name+'_x':(86,0,719),name+'_y':(819 if name=='title' else 934,0,1270),
                         name+'_width':(548,60,720)})
        out.setdefault(name+'_font','sans-bold' if name=='title' else 'sans')
        out.setdefault(name+'_align','center')
        if out[name+'_font'] not in FONTS or out[name+'_align'] not in ('left','center','right'):
            raise ValueError('Font hoặc căn chữ không hợp lệ.')
    for key,(default,low,high) in spec.items():
        value=out.get(key,default)
        if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not low<=value<=high:
            raise ValueError('Thông số ngoài giới hạn: '+key)
        out[key]=round(value,1)
    if out['frame_style']=='custom':
        if not isinstance(out.get('frame_id'),str) or not re.fullmatch('[a-f0-9]{32}',out['frame_id']):
            raise ValueError('Hãy tải khung PNG từ máy trước.')
    return out


def video_box(opts):
    if opts.get('units') == 'px':
        return {key:round(opts['video_'+key]) for key in ('x','y','width','height')}
    zoom = opts['zoom']/100
    w,h = round(720*zoom/2)*2,round(1280*zoom/2)*2
    return dict(width=w,height=h,x=round((720-w)/2+720*opts['video_x']/100),
                y=round((1280-h)/2+1280*opts['video_y']/100))


def frame_box(opts):
    if opts.get('units') == 'px':
        return {key:round(opts['frame_'+key]) for key in ('x','y','width','height')}
    w=round(W*opts['frame_width']/100)
    h=round(H*opts['frame_height']/100)
    x=round(max(0,min(W-w,W*opts['frame_x']/100-w/2)))
    y=round(min(H-h,H*opts['frame_y']/100))
    return dict(x=x,y=y,width=w,height=h)


def layout(opts):
    result=[]
    for key in ('title','body'):
        text=opts.get(key,'')
        if not text.strip():
            continue
        font,size=opts[key+'_font'],opts[key+'_size']
        px = opts.get('units') == 'px'
        box_width=round(opts[key+'_width'] if px else W*opts[key+'_width']/100)
        lines=wrap(text,font,size,box_width-2*opts[key+'_outline']-4)
        step=size+opts[key+'_gap']
        y=round(opts[key+'_y'] if px else H*opts[key+'_y']/100)
        if len(lines)>16 or y+len(lines)*step>H-4:
            raise ValueError(('Tiêu đề' if key=='title' else 'Nội dung')+' vượt khung hình. Giảm cỡ chữ, tăng độ rộng hoặc kéo lên.')
        x=round(opts[key+'_x'] if px else max(2,min(W-box_width-2,W*opts[key+'_x']/100-box_width/2)))
        if x+box_width>W:
            raise ValueError('Hộp chữ vượt cạnh phải. Giảm X hoặc độ rộng hộp chữ.')
        offsets=[]
        for line in lines:
            line_width=width(line,font,size)
            factor={'left':0,'center':.5,'right':1}[opts[key+'_align']]
            offsets.append(round(x+(box_width-line_width)*factor,2))
        result.append(dict(key=key,text='\n'.join(lines),lines=lines,line_x=offsets,
                           x=x,y=y,width=box_width,size=size,gap=opts[key+'_gap'],
                           font=font,family=FONTS[font][1],align=opts[key+'_align'],
                           color=opts[key+'_color'],outline=opts[key+'_outline'],
                           outline_color=opts[key+'_outline_color']))
    return result


def artwork(opts):
    color=tuple(bytes.fromhex(opts['color'][1:]))
    other=tuple(bytes.fromhex(opts['color2'][1:])) if opts['background']=='gradient' else color
    start=opts['fade_start'] if opts.get('units')=='px' else H*opts['fade_start']/100
    height=opts['fade_height'] if opts.get('units')=='px' else H*opts['fade_height']/100
    pixels=[]
    for y in range(H):
        t=min(1,max(0,(y-start)/height))
        mix=min(1,max(0,(y-start)/max(1,H-start)))
        rgb=bytes(round(a+(b-a)*mix) for a,b in zip(color,other))
        alpha=round(255*opts['opacity']/100*t*t*(3-2*t))
        pixels.append(bytearray((rgb+bytes([alpha]))*W))

    original = [bytes(row) for row in pixels] if 0 < opts['frame_opacity'] < 100 else None

    def span(y,x1,x2,rgba):
        if not 0<=y<H:
            return
        row=pixels[y]
        r,g,b,a=rgba
        a0=a/255
        for x in range(max(0,x1),min(W,x2)):
            i=4*x
            old=row[i+3]/255
            combined=a0+old*(1-a0)
            if combined:
                row[i:i+4]=bytes((round((r*a0+row[i]*old*(1-a0))/combined),
                                  round((g*a0+row[i+1]*old*(1-a0))/combined),
                                  round((b*a0+row[i+2]*old*(1-a0))/combined),round(combined*255)))

    def rounded(x,y,w,h,radius,fill):
        x,y,w,h,radius=map(round,(x,y,w,h,min(radius,w/2,h/2)))
        for yy in range(max(0,y),min(H,y+h)):
            edge=max(radius-(yy-y)-.5,(yy-(y+h-radius))+.5,0)
            inset=radius-math.sqrt(max(0,radius*radius-edge*edge)) if edge else 0
            span(yy,math.ceil(x+inset),math.floor(x+w-inset),fill(yy-y) if callable(fill) else fill)

    box=frame_box(opts)
    x,y,w,h=[box[k] for k in ('x','y','width','height')]
    fill=tuple(bytes.fromhex(opts['frame_color'][1:]))
    border=tuple(bytes.fromhex(opts['border_color'][1:]))
    style=opts['frame_style']
    r=min(40,h*.12)
    if style not in ('none','custom') and opts['frame_opacity'] > 0:
        if style=='pink':
            rounded(x,y+6,w,h-6,r,(*border,255))
            rounded(x+6,y,w-12,h-12,r,(*border,255))
            rounded(x+12,y+6,w-24,h-24,r-5,(*fill,255))
            rounded(x+17,y+11,w-34,h-34,r-8,
                    lambda yy: tuple(round(c+(255-c)*max(0,1-yy/max(1,h*.35))*opts['gloss']/180) for c in fill)+(255,))
            for cx,cy,size in [(x+8,y+8,18),(x+w-8,y+12,20),(x+8,y+h-12,15),(x+w-8,y+h-16,15)]:
                for dy in range(-size,size+1):
                    half=max(1,round((1-abs(dy)/size)**2*size*.45))
                    span(cy+dy,cx-half,cx+half+1,(*border,255))
        elif style=='glass':
            rounded(x,y,w,h,r,(*border,200))
            rounded(x+2,y+2,w-4,h-4,r-2,(*fill,125))
            rounded(x+9,y+7,w-18,h*.22,r/2,(255,255,255,40))
        elif style=='gold':
            rounded(x,y,w,h,r,(*border,255))
            rounded(x+4,y+4,w-8,h-8,r-2,(*fill,255))
            rounded(x+10,y+10,w-20,h-20,r-5,(*border,255))
            rounded(x+12,y+12,w-24,h-24,r-7,(*fill,255))
        elif style=='minimal':
            rounded(x,y,w,h,r*.6,(*fill,245))
            rounded(x,y+16,5,h-32,2,(*border,255))
        elif style=='neon':
            for spread,alpha in [(10,15),(7,25),(4,50)]:
                rounded(x-spread,y-spread,w+2*spread,h+2*spread,r+spread,(*border,alpha))
            rounded(x,y,w,h,r,(*border,255))
            rounded(x+3,y+3,w-6,h-6,r-3,(*fill,250))
        elif style=='ribbon':
            rounded(x,y,w,h,5,(*border,255))
            rounded(x+3,y+3,w-6,h-6,4,(*fill,255))
            rounded(x+12,y+12,w-24,7,3,(*border,220))
            rounded(x+12,y+h-19,w-24,7,3,(*border,220))
    if original is not None and style not in ('none','custom'):
        factor = opts['frame_opacity']/100
        for yy in range(max(0,y-30),min(H,y+h+30)):
            before,after = original[yy],pixels[yy]
            for xx in range(max(0,x-30),min(W,x+w+30)):
                at = xx*4
                a,b = before[at+3]/255,after[at+3]/255
                alpha = a*(1-factor)+b*factor
                if alpha:
                    for c in range(3):
                        after[at+c] = round((before[at+c]*a*(1-factor)+after[at+c]*b*factor)/alpha)
                    after[at+3] = round(alpha*255)
    raw=b''.join(b'\0'+row for row in pixels)
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',W,H,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b'')
