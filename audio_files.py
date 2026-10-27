"""Download provider-returned media without API keys, validate and cache as MP3."""
import hashlib
import ipaddress
import json
import math
from pathlib import Path
import socket
import subprocess
import threading
import time
from urllib import request, error, parse
import ai33_audio as api

LIMIT=100*1024*1024
_LOCKS={}
_MUTEX=threading.Lock()


def asset_id(task):
    return hashlib.sha256(task.encode('utf-8')).hexdigest()[:32]


def public_url(url):
    api.https_url(url)
    host=parse.urlsplit(url).hostname
    try:
        addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    except OSError:
        raise api.AudioError('Không phân giải được máy chủ audio. Kiểm tra DNS/mạng trước khi tải lại.') from None
    if not addresses or any(not ipaddress.ip_address(item[4][0].split('%')[0]).is_global for item in addresses):
        raise api.AudioError('Từ chối tải audio từ địa chỉ mạng nội bộ.')
    return url


class PublicRedirect(request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        public_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def download(url,target):
    public_url(url)
    # Default ProxyHandler/HTTPSHandler retain the session proxy and TLS trust.
    opener=request.build_opener(PublicRedirect())
    deadline=time.monotonic()+120
    try:
        # No xi-api-key, Authorization or cookies go to the media/CDN host.
        with opener.open(request.Request(url,headers={'Accept':'audio/*,application/octet-stream'}),timeout=45) as response:
            declared=response.headers.get('Content-Length')
            if declared and declared.isdigit() and int(declared)>LIMIT:
                raise api.AudioError('File audio vượt giới hạn tải 100 MB.')
            total=0
            with target.open('wb') as output:
                while True:
                    if time.monotonic()>deadline:
                        raise api.AudioError('Tải audio quá lâu. Kiểm tra mạng rồi tải lại tác vụ này.')
                    chunk=response.read(256*1024)
                    if not chunk:
                        break
                    total+=len(chunk)
                    if total>LIMIT:
                        raise api.AudioError('File audio vượt giới hạn tải 100 MB.')
                    output.write(chunk)
        if not total:
            raise api.AudioError('ai33.pro trả file audio trống.')
    except (error.URLError,TimeoutError,OSError):
        raise api.AudioError('Không tải được file audio. Kiểm tra lại tác vụ để lấy link mới, không cần tạo audio lại.',504) from None


def media_format(path):
    with path.open('rb') as source:
        head=source.read(64)
    if head.startswith(b'ID3') or (len(head)>1 and head[0]==255 and head[1]&224==224):
        return 'mp3'
    if head.startswith(b'RIFF') and head[8:12]==b'WAVE':
        return 'wav'
    if head.startswith(b'fLaC'):
        return 'flac'
    if head.startswith(b'OggS'):
        return 'ogg'
    if head[4:8]==b'ftyp':
        return 'mov'
    raise api.AudioError('File nhận về không phải MP3/WAV/FLAC/Ogg/M4A được hỗ trợ.')


def info(path):
    try:
        result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type','-of','json',str(path)],capture_output=True,text=True,check=True,timeout=25)
        data=json.loads(result.stdout)
        duration=float(data['format']['duration'])
        if not math.isfinite(duration) or duration<=0 or not any(s.get('codec_type')=='audio' for s in data['streams']):
            raise ValueError()
        return dict(duration=round(duration,3),bytes=path.stat().st_size)
    except (subprocess.SubprocessError,OSError,ValueError,KeyError,TypeError):
        raise api.AudioError('Không xác minh được file âm thanh. Kiểm tra tác vụ rồi tải lại.') from None


def cache(raw,directory):
    task=api.task_id(raw)
    aid=asset_id(task)
    directory=Path(directory)
    directory.mkdir(exist_ok=True)
    with _MUTEX:
        lock=_LOCKS.setdefault(aid,threading.Lock())
    with lock:
        target=directory/(aid+'.mp3')
        if target.is_file():
            try:
                metadata=info(target)
                return dict(task_id=task,asset_id=aid,url='/audio/file/'+aid,**metadata)
            except api.AudioError:
                target.unlink(missing_ok=True)
        detail=api.get_task(raw)
        if detail['status']!='done' or not detail['audio_url']:
            raise api.AudioError('Tác vụ chưa có audio hoàn tất để tải. Tiếp tục kiểm tra tiến độ.',409)
        source=directory/(aid+'.download')
        encoded=directory/(aid+'.encoding.mp3')
        try:
            download(detail['audio_url'],source)
            fmt=media_format(source)
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
                            '-protocol_whitelist','file,pipe','-f',fmt,'-i',str(source),
                            '-map','0:a:0','-vn','-c:a','libmp3lame','-b:a','192k',str(encoded)],
                           capture_output=True,check=True,timeout=180)
            metadata=info(encoded)
            encoded.replace(target)
            return dict(task_id=task,asset_id=aid,url='/audio/file/'+aid,**metadata)
        except (subprocess.SubprocessError,OSError):
            raise api.AudioError('Không chuyển được audio sang MP3. Cần FFmpeg có libmp3lame; không cần tạo lại tác vụ.') from None
        finally:
            source.unlink(missing_ok=True)
            encoded.unlink(missing_ok=True)
