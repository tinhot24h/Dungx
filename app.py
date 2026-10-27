"""Local TikTok review video composer. Python 3.11+, FFmpeg, no pip packages."""
import base64
import json
import os
import re
import subprocess
import threading
import struct
import shutil
import unicodedata
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from design import settings, layout, artwork, frame_box, video_box
from fonts import FONTS
import ai_translate

ROOT = Path(__file__).resolve().parent
DATA = ROOT / '.local'
DATA.mkdir(exist_ok=True)
FRAMES = DATA / 'frames'
FRAMES.mkdir(exist_ok=True)
JOBS = {}
LOCK = threading.Lock()
RENDER_LOCK = threading.Lock()
AI_SLOTS = threading.BoundedSemaphore(2)


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                             'format=duration:stream=codec_type', '-of', 'json', str(path)],
                            capture_output=True, text=True, timeout=20, check=True)
    info = json.loads(result.stdout)
    if not any(s['codec_type'] == 'video' for s in info['streams']):
        raise ValueError('Tệp không có hình ảnh video.')
    duration = float(info['format']['duration'])
    if not 0 < duration <= 180:
        raise ValueError('Chọn clip dài tối đa 180 giây.')
    return duration


def validate_options(opts):
    opts = settings(opts)
    for field, limit in [('title', 160), ('body', 600)]:
        value = opts.get(field)
        if not isinstance(value, str) or len(value) > limit or not value.strip():
            raise ValueError(f'Nội dung {field} không hợp lệ (tối đa {limit} ký tự).')
        opts[field] = unicodedata.normalize('NFC', '\n'.join(' '.join(line.split()) for line in value.splitlines()))
    if opts['frame_style'] == 'custom' and not (FRAMES / (opts['frame_id']+'.png')).is_file():
        raise ValueError('Khung PNG không còn trong ứng dụng này. Hãy tải lại khung.')
    layout(opts)
    return opts


def compose(folder, options):
    (folder / 'overlay.png').write_bytes(artwork(options))
    filters = []
    for item in layout(options):
        font = '../../assets/' + FONTS[item['font']][0]
        for line_number, line in enumerate(item['lines']):
            if not line.strip():
                continue
            filename = f"{item['key']}-{line_number}.txt"
            (folder / filename).write_text(line, encoding='utf-8')
            y = item['y'] + line_number*(item['size']+item['gap'])
            filters.append(f"drawtext=fontfile={font}:textfile={filename}:expansion=none:"
                           f"fontsize={item['size']}:fontcolor={item['color'].replace('#','0x')}:"
                           f"x={item['line_x'][line_number]}:y={y}:"
                           f"borderw={item['outline']}:bordercolor={item['outline_color'].replace('#','0x')}")
    video = video_box(options)
    width,height,x,y = (video[k] for k in ('width','height','x','y'))
    color = options['color'].replace('#','0x')
    graph = (f"[0:v]split[src][bg];[bg]scale=720:1280,setsar=1,"
             f"drawbox=color={color}:t=fill[base];"
             f"[src]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=rgba,"
             f"scale={width}:{height},setsar=1[clip];"
             f"[base][clip]overlay={x}:{y}:shortest=1[placed];"
             "[placed][1:v]overlay=0:0:format=auto[design];")
    extra = []
    if options['frame_style'] == 'custom':
        shutil.copyfile(FRAMES / (options['frame_id']+'.png'),folder/'frame.png')
        box = frame_box(options)
        w,h = box['width'],box['height']
        extra = ['-i','frame.png']
        graph += (f"[2:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
                  f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x00000000,format=rgba,"
                  f"colorchannelmixer=aa={options['frame_opacity']/100}[custom];"
                  f"[design][custom]overlay={box['x']}:{box['y']}:format=auto[framed];")
        top = 'framed'
    else:
        top = 'design'
    graph += f"[{top}]" + ','.join(filters) + '[out]'
    return ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
            '-i', 'source', '-i', 'overlay.png', *extra, '-filter_complex_threads', '1',
            '-filter_complex', graph, '-map', '[out]', '-map', '0:a:0?',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-threads', '2',
            '-r', '30', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart', 'review.mp4']


def render(job_id, command):
    with RENDER_LOCK:
        with LOCK:
            JOBS[job_id] = {'state': 'rendering'}
        try:
            subprocess.run(command, cwd=DATA / job_id, capture_output=True,
                           timeout=600, check=True)
            result = {'state': 'done', 'url': f'/download/{job_id}'}
        except (subprocess.SubprocessError, OSError):
            result = {'state': 'error', 'error': 'Xuất video thất bại. Hãy thử clip MP4 H.264 khác hoặc clip ngắn hơn.'}
        with LOCK:
            JOBS[job_id] = result


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, content, mime='application/json; charset=utf-8'):
        if not isinstance(content, bytes):
            content = json.dumps(content, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(content)

    def allowed(self):
        port = self.server.server_port
        hosts = (f'127.0.0.1:{port}',f'localhost:{port}')
        origin = self.headers.get('Origin')
        if self.headers.get('Host') not in hosts or (origin and origin not in ('http://'+host for host in hosts)):
            self.respond(403, {'error':'Chỉ chấp nhận truy cập từ ứng dụng cục bộ.'})
            return False
        return True

    def do_GET(self):
        if not self.allowed():
            return
        path = urlparse(self.path).path
        if path == '/':
            return self.respond(200, (ROOT / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if path in ('/studio.css','/studio.js','/ai_ui.js'):
            mime = 'text/css' if path.endswith('.css') else 'text/javascript'
            return self.respond(200, (ROOT/path.lstrip('/')).read_bytes(), mime+'; charset=utf-8')
        if path in ('/assets/'+font[0] for font in FONTS.values()):
            return self.respond(200, (ROOT / path.lstrip('/')).read_bytes(), 'font/ttf')
        match = re.fullmatch(r'/frames/([a-f0-9]{32})', path)
        if match and (FRAMES / (match[1]+'.png')).is_file():
            return self.respond(200, (FRAMES / (match[1]+'.png')).read_bytes(), 'image/png')
        if path == '/ai-status':
            return self.respond(200, {'configured':ai_translate.configured(),'model':ai_translate.default_model(),
                                     'providers':{name:dict(configured=ai_translate.configured(name),model=ai_translate.default_model(name))
                                                  for name in ('openai','gemini')}})
        if path == '/health':
            return self.respond(200, {'status': 'ok'})
        match = re.fullmatch(r'/(jobs|download)/([a-f0-9]{32})', path)
        if match:
            kind, key = match.groups()
            with LOCK:
                job = JOBS.get(key)
            if kind == 'jobs' and job:
                return self.respond(200, job)
            output = DATA / key / 'review.mp4'
            if kind == 'download' and job and job['state'] == 'done' and output.is_file():
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Content-Disposition', 'attachment; filename="tiktok-review.mp4"')
                self.send_header('Content-Length', str(output.stat().st_size))
                self.end_headers()
                with output.open('rb') as source:
                    while chunk := source.read(1024 * 1024):
                        self.wfile.write(chunk)
                return
        self.respond(404, {'error': 'Không tìm thấy.'})

    def do_POST(self):
        if not self.allowed():
            return
        path = urlparse(self.path).path
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if path in ('/translation-prompt','/translation-import'):
                if not 0 < size <= 196608:
                    raise ValueError('Yêu cầu quá lớn.')
                raw = json.loads(self.rfile.read(size))
                result = {'prompt':ai_translate.manual_prompt(raw)} if path.endswith('prompt') else ai_translate.import_manual(raw)
                return self.respond(200,result)
            if path == '/translate':
                if not 0 < size <= 65536:
                    raise ValueError('Yêu cầu dịch quá lớn.')
                raw = json.loads(self.rfile.read(size))
                if not AI_SLOTS.acquire(blocking=False):
                    return self.respond(429, {'error':'Đang xử lý các bản dịch khác. Hãy chờ rồi thử lại.'})
                try:
                    result = ai_translate.translate(raw)
                finally:
                    AI_SLOTS.release()
                return self.respond(200,result)
            if path == '/frame-upload':
                if not 0 < size <= 5*1024*1024:
                    return self.respond(413, {'error': 'Khung PNG tối đa 5 MB.'})
                data = self.rfile.read(size)
                if len(data) != size or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR' or len(data)<33:
                    raise ValueError('Tệp không phải PNG hợp lệ.')
                width, height = struct.unpack('!II',data[16:24])
                if not 0 < width <= 4096 or not 0 < height <= 4096 or width*height>8000000:
                    raise ValueError('PNG tối đa 4096 px mỗi cạnh và 8 triệu điểm ảnh.')
                key = uuid.uuid4().hex
                source, target = FRAMES/(key+'-upload.png'), FRAMES/(key+'.png')
                source.write_bytes(data)
                try:
                    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
                                    '-f','image2','-c:v','png','-i',str(source),'-frames:v','1',
                                    '-vf','format=rgba',str(target)],capture_output=True,check=True,timeout=25)
                except subprocess.SubprocessError:
                    target.unlink(missing_ok=True)
                    raise ValueError('Không đọc được PNG. Hãy xuất lại dưới dạng PNG tĩnh.')
                finally:
                    source.unlink(missing_ok=True)
                return self.respond(200, {'id': key,'url':'/frames/'+key,'width':width,'height':height})
            if path == '/upload':
                if not 0 < size <= 100 * 1024 * 1024:
                    return self.respond(413, {'error': 'Chọn video có dung lượng tối đa 100 MB.'})
                key = uuid.uuid4().hex
                folder = DATA / key
                folder.mkdir()
                remaining = size
                with (folder / 'source').open('wb') as output:
                    while remaining:
                        chunk = self.rfile.read(min(1024 * 1024, remaining))
                        if not chunk:
                            raise ValueError('Tải lên bị gián đoạn.')
                        output.write(chunk)
                        remaining -= len(chunk)
                duration = probe(folder / 'source')
                return self.respond(200, {'id': key, 'duration': round(duration, 1)})
            if path == '/design':
                if not 0 < size <= 8192:
                    raise ValueError('Yêu cầu không hợp lệ.')
                opts = validate_options(json.loads(self.rfile.read(size)))
                custom = None
                if opts['frame_style'] == 'custom':
                    custom = dict(url='/frames/'+opts['frame_id'],**frame_box(opts),opacity=opts['frame_opacity']/100)
                return self.respond(200, {'image':'data:image/png;base64,'+
                                         base64.b64encode(artwork(opts)).decode(),
                                         'text':layout(opts),'custom':custom,'frame':frame_box(opts),'video':video_box(opts)})
            if path == '/render':
                if not 0 < size <= 8192:
                    raise ValueError('Yêu cầu không hợp lệ.')
                opts = validate_options(json.loads(self.rfile.read(size)))
                key = opts.get('id', '')
                if not isinstance(key, str) or not re.fullmatch('[a-f0-9]{32}', key):
                    raise ValueError('Hãy tải clip lên trước.')
                folder = DATA / key
                if not (folder / 'source').is_file():
                    raise ValueError('Không tìm thấy clip.')
                with LOCK:
                    if JOBS.get(key, {}).get('state') in ('queued', 'rendering'):
                        return self.respond(409, {'error': 'Clip đang được xử lý.'})
                    JOBS[key] = {'state': 'queued'}
                try:
                    command = compose(folder, opts)
                except ValueError:
                    with LOCK:
                        JOBS.pop(key, None)
                    raise
                threading.Thread(target=render, args=(key, command), daemon=True).start()
                return self.respond(202, {'id': key})
            self.respond(404, {'error': 'Không tìm thấy.'})
        except ai_translate.AIError as error:
            self.respond(error.status, {'error':str(error)})
        except ValueError as error:
            self.respond(400, {'error': str(error)})
        except (KeyError, TypeError, subprocess.SubprocessError):
            self.respond(400, {'error': 'Dữ liệu không hợp lệ. Dùng clip video tối đa 180 giây.'})


if __name__ == '__main__':
    address = ('127.0.0.1', int(os.environ.get('PORT', '8000')))
    print(f'Review Studio running on port {address[1]}', flush=True)
    ThreadingHTTPServer(address, Handler).serve_forever()
