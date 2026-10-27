"""Local TikTok review video composer. Python 3.11+, FFmpeg, no pip packages."""
import base64
import json
import os
import re
import subprocess
import threading
import textwrap
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from design import settings, layout, artwork

ROOT = Path(__file__).resolve().parent
DATA = ROOT / '.local'
DATA.mkdir(exist_ok=True)
JOBS = {}
LOCK = threading.Lock()
RENDER_LOCK = threading.Lock()
# Relative to .local/<job-id>/; forward slashes also work in FFmpeg on Windows.
FONT = '../../assets/DejaVuSans.ttf'
BOLD = '../../assets/DejaVuSans-Bold.ttf'


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
    for field, limit in [('title', 72), ('body', 210), ('cta', 38)]:
        value = opts.get(field)
        if not isinstance(value, str) or len(value) > limit or (field != 'cta' and not value.strip()):
            raise ValueError(f'Nội dung {field} không hợp lệ (tối đa {limit} ký tự).')
        opts[field] = ' '.join(value.split())
    if not isinstance(opts.get('color'), str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', opts['color']):
        raise ValueError('Màu không hợp lệ.')
    layout(opts)
    return opts


def compose(folder, options):
    (folder / 'overlay.png').write_bytes(artwork(options))
    filters = []
    for item in layout(options):
        font = BOLD if item['bold'] else FONT
        for line_number, line in enumerate(item['text'].splitlines()):
            filename = f"{item['key']}-{line_number}.txt"
            (folder / filename).write_text(line, encoding='utf-8')
            y = item['y'] + line_number*(item['size']+3)
            filters.append(f"drawtext=fontfile={font}:textfile={filename}:expansion=none:"
                           f"fontsize={item['size']}:fontcolor={item['color'].replace('#','0x')}:"
                           f"x=(w-tw)/2:y={y}:"
                           f"borderw={item['outline']}:bordercolor=0x342333@0.8")
    zoom = options['zoom']/100
    width = round(720*zoom/2)*2
    height = round(1280*zoom/2)*2
    focus = options['focus']/100
    vf = (f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
          f"crop=720:1280:(iw-720)/2:(ih-1280)*{focus},setsar=1[clip];"
          "[clip][1:v]overlay=0:0:format=auto," + ','.join(filters) + '[out]')
    return ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
            '-i', 'source', '-i', 'overlay.png', '-filter_complex_threads', '1',
            '-filter_complex', vf, '-map', '[out]', '-map', '0:a:0?',
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

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            return self.respond(200, (ROOT / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if path in ('/assets/DejaVuSans.ttf', '/assets/DejaVuSans-Bold.ttf'):
            return self.respond(200, (ROOT / path.lstrip('/')).read_bytes(), 'font/ttf')
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
        path = urlparse(self.path).path
        try:
            size = int(self.headers.get('Content-Length', '0'))
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
                return self.respond(200, {'image': 'data:image/png;base64,' +
                                         base64.b64encode(artwork(opts)).decode(), 'text': layout(opts)})
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
        except ValueError as error:
            self.respond(400, {'error': str(error)})
        except (KeyError, TypeError, subprocess.SubprocessError):
            self.respond(400, {'error': 'Dữ liệu không hợp lệ. Dùng clip video tối đa 180 giây.'})


if __name__ == '__main__':
    address = ('127.0.0.1', int(os.environ.get('PORT', '8000')))
    print(f'Review Studio running on port {address[1]}', flush=True)
    ThreadingHTTPServer(address, Handler).serve_forever()
