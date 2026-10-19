#!/usr/bin/env python3
"""Local code-video toolkit. Editorial research is performed by the invoking agent."""
import argparse
import base64
import contextlib
import hashlib
import http.server
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import wave

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / 'engine'

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def ffmpeg():
    if os.environ.get('VIBE_FFMPEG'):
        return os.environ['VIBE_FFMPEG']
    if shutil.which('ffmpeg'):
        return shutil.which('ffmpeg')
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def chrome():
    explicit = os.environ.get('VIBE_CHROME')
    if explicit:
        return explicit
    for x in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
              shutil.which('google-chrome'), shutil.which('chromium')]:
        if x and Path(x).exists():
            return x
    return None

def load(project):
    project = Path(project).resolve()
    p = json.loads((project/'project.json').read_text(encoding='utf-8'))
    errors=[]
    for k in ['title','duration','fps','width','height','scenes','subtitles','sources','claims','assets']:
        if k not in p:
            errors.append('missing '+k)
    if errors:
        raise ValueError('; '.join(errors))
    for k in ['duration','fps','width','height']:
        if not isinstance(p[k], (int,float)) or not math.isfinite(p[k]) or p[k]<=0:
            errors.append('invalid '+k)
    for k in ['width','height']:
        if not isinstance(p[k],int) or p[k]%2:
            errors.append(k+' must be an even integer')
    if errors:
        raise ValueError('; '.join(errors))
    if not p['scenes'] or not p['subtitles']:
        errors.append('scenes and subtitles must be nonempty')
    for key in ['scenes','subtitles']:
        cursor=0
        for row in p[key]:
            if not isinstance(row.get('start'),(int,float)) or not isinstance(row.get('end'),(int,float)):
                errors.append('invalid time in '+key);continue
            if not (math.isfinite(row['start']) and math.isfinite(row['end']) and 0<=row['start']<row['end']<=p['duration']):
                errors.append('out of range time in '+key)
            if row['start']<cursor-1e-6:
                errors.append('overlap or unsorted '+key)
            if key=='scenes' and abs(row['start']-cursor)>1e-6:
                errors.append('gap in scenes')
            cursor=row['end']
        if key=='scenes' and abs(cursor-p['duration'])>1e-6:
            errors.append('scenes do not cover duration')
    ids={x['id'] for x in p['scenes']}
    if len(ids)!=len(p['scenes']): errors.append('duplicate scene id')
    sources={x['id']:x for x in p['sources']}
    for c in p['claims']:
        if not c.get('sources') or any(v not in sources for v in c['sources']):
            errors.append('claim missing source: '+c.get('id','?'))
        if c.get('status')!='verified' or not c.get('evidence'):
            errors.append('claim not verified: '+c.get('id','?'))
    claim_ids={x['id'] for x in p['claims']}
    for sub in p['subtitles']:
        if not sub.get('text') or any(x not in claim_ids for x in sub.get('claims',[])):
            errors.append('invalid subtitle/claim reference')
        if sub.get('kind')=='fact' and not sub.get('claims'):
            errors.append('factual subtitle missing claim')
    for s in p['sources']:
        if not s.get('url','').startswith(('https://','http://')) or not s.get('checked_at'):
            errors.append('incomplete source '+s['id'])
    for asset in p['assets']:
        if not asset.get('license') or not asset.get('origin'):
            errors.append('asset missing rights information')
    if errors:
        raise ValueError('\n'.join(errors))
    return project,p

def reading_warnings(p):
    warnings=[]
    for s in p['subtitles']:
        rate=len(s['text'].replace('\n',''))/(s['end']-s['start'])
        if rate>7:
            warnings.append({'text':s['text'],'characters_per_second':round(rate,2)})
    return warnings

def prepare(project):
    project,p=load(project)
    for file in ['runtime.js']:
        shutil.copyfile(ENGINE/file,project/file)
    shutil.copyfile(ENGINE/'player.html',project/'index.html')
    return project,p

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

@contextlib.contextmanager
def server(project, port=0):
    import functools
    handler=functools.partial(QuietHandler,directory=str(project))
    srv=http.server.ThreadingHTTPServer(('127.0.0.1',port),handler)
    thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
    try: yield f'http://127.0.0.1:{srv.server_port}/'
    finally: srv.shutdown();srv.server_close();thread.join()

@contextlib.contextmanager
def browser_page(project,p):
    from playwright.sync_api import sync_playwright
    with server(project) as url, sync_playwright() as pw:
        opts={'headless':True}
        if chrome(): opts['executable_path']=chrome()
        browser=pw.chromium.launch(**opts)
        try:
            page=browser.new_page(viewport={'width':p['width'],'height':p['height']},device_scale_factor=1)
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(url+'?export=1',wait_until='networkidle')
            page.evaluate('window.ready')
            page.evaluate('document.fonts.ready')
            yield page,errors
        finally: browser.close()

def png(page,t):
    return base64.b64decode(page.evaluate('(t)=>{window.seek(t);return Vibe.canvas.toDataURL("image/png").split(",")[1]}',t))

def review(project):
    from PIL import Image,ImageDraw
    project,p=prepare(project)
    out=project/'review';out.mkdir(exist_ok=True)
    times=sorted(set(round(min(p['duration']-.001,max(0,t)),4) for s in p['scenes']
        for t in [s['start'],s['start']+.2,(s['start']+s['end'])/2,s['end']-.05]))
    thumbs=[];issues=[];hashes={}
    with browser_page(project,p) as (page,errors):
        # Out-of-order repeat catches hidden state in scene renderers.
        for t in times:
            data=png(page,t);hashes[t]=hashlib.sha256(data).hexdigest()
            issues.extend(page.evaluate('(t)=>Vibe.render(t).issues',t))
            im=Image.open(io.BytesIO(data)).convert('RGB');im.thumbnail((480,270))
            tile=Image.new('RGB',(480,300),'#080d19');tile.paste(im,(0,0));ImageDraw.Draw(tile).text((12,278),f'{t:.2f} s',fill='white');thumbs.append(tile)
        for t in reversed(times):
            if hashlib.sha256(png(page,t)).hexdigest()!=hashes[t]:
                issues.append({'kind':'nondeterministic','time':t})
        page.evaluate('window.seek(1)');page.screenshot(path=str(out/'player.png'))
        (out/'cover.png').write_bytes(png(page,p.get('cover_time',times[len(times)//2])))
    sheet=Image.new('RGB',(480*3,300*math.ceil(len(thumbs)/3)),'#080d19')
    for i,tile in enumerate(thumbs):sheet.paste(tile,((i%3)*480,(i//3)*300))
    sheet.save(out/'contact-sheet.jpg',quality=90)
    report={'sample_count':len(times),'deterministic_samples':not any(x['kind']=='nondeterministic' for x in issues),
            'browser_errors':errors,'layout_issues':issues,'reading_warnings':reading_warnings(p),
            'facts':'Source records validated structurally; truth still needs editorial review.',
            'visual_review':'Contact sheet requires human/agent inspection; not a frame-complete visual audit.'}
    write_json(out/'qa.json',report)
    print(json.dumps(report,ensure_ascii=False))
    if errors or issues:raise RuntimeError('QA failed; inspect review/qa.json')

def synth(project,p):
    import numpy as np
    sr=48000;n=math.ceil(p['duration']*sr);mix=np.zeros(n,dtype=np.float64)
    bpm=p.get('audio',{}).get('bpm',80);beat=60/bpm
    def tone(start,duration,freq,gain):
        start=round(start*sr);count=min(round(duration*sr),n-start)
        if count<=0:return
        t=np.arange(count)/sr
        env=(1-np.exp(-t*45))*np.exp(-t*2.4)*np.minimum(1,(count/sr-t)*8)
        mix[start:start+count]+=gain*env*(np.sin(2*np.pi*freq*t)+.22*np.sin(4*np.pi*freq*t))
    notes=[220,261.6256,329.6276,391.9954,329.6276,261.6256,196,261.6256]
    for i in range(math.ceil(p['duration']/beat)):
        tone(i*beat,2.1,notes[i%len(notes)],.12)
        if i%4==0:tone(i*beat,2.8,110 if (i//8)%2==0 else 130.8128,.10)
    for s in p['scenes']:tone(s['start'],.28,880,.08)
    fade=np.minimum(1,np.arange(n)/sr)*np.minimum(1,(n-1-np.arange(n))/sr/1.5)
    mix*=fade;peak=float(np.max(np.abs(mix)))
    if peak>.75:mix*=.75/peak
    path=project/'audio.wav'
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes((mix*32767).astype('<i2').tobytes())
    return path

def audio(project):
    project,p=load(project);a=p.get('audio',{})
    if a.get('file'):
        src=(project/a['file']).resolve()
        if not src.is_file():raise ValueError('Missing audio '+str(src))
        subprocess.run([ffmpeg(),'-v','error','-y','-i',str(src),'-t',str(p['duration']),'-ac','1','-ar','48000',str(project/'audio.wav')],check=True)
    else:synth(project,p)
    import numpy as np
    with wave.open(str(project/'audio.wav'),'rb') as f:
        sr=f.getframerate();samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
    duration=len(samples)/sr
    if duration<p['duration']-.03:raise ValueError('Audio shorter than video; supply a longer track')
    energies=[float(np.sqrt(np.mean(samples[i:i+sr]**2))) for i in range(0,len(samples),sr)]
    report={'duration':duration,'peak_dbfs':round(20*math.log10(max(float(np.max(np.abs(samples))),1e-9)),2),'rms_per_second':energies,
            'bpm':a.get('bpm'),'beat_origin':a.get('beat_origin',0),'beat_method':'User supplied BPM/grid; no automatic BPM detection.',
            'loudness':'Sample peak and RMS only; not a LUFS/true-peak certification.'}
    if a.get('bpm'):
        report['beats']=[round(a.get('beat_origin',0)+i*60/a['bpm'],4) for i in range(math.ceil(p['duration']*a['bpm']/60)) if 0<=a.get('beat_origin',0)+i*60/a['bpm']<p['duration']]
    write_json(project/'audio-analysis.json',report)
    p.setdefault('audio',{})['preview']='audio.wav';write_json(project/'project.json',p)
    print(json.dumps({k:v for k,v in report.items() if k not in ['rms_per_second','beats']},ensure_ascii=False))

def render(project,start=0,end=None,width=None):
    project,p=prepare(project);end=p['duration'] if end is None else end
    if not 0<=start<end<=p['duration']:raise ValueError('Invalid render range')
    if width:
        if width%2 or width<2:raise ValueError('width must be a positive even integer')
        p['height']=round(p['height']*width/p['width']/2)*2;p['width']=width
    if not (project/'audio.wav').exists():audio(project)
    out=project/'renders';out.mkdir(exist_ok=True)
    label='final' if start==0 and end==p['duration'] and not width else f'clip-{start:g}-{end:g}-{p["width"]}'
    dest=out/(label+'.mp4');temporary=out/(label+'.partial.mp4');log=out/(label+'.log')
    count=math.ceil((end-start)*p['fps']-1e-8);length=count/p['fps']
    cmd=[ffmpeg(),'-v','warning','-y','-f','image2pipe','-vcodec','png','-framerate',str(p['fps']),'-i','pipe:0',
         '-ss',str(start),'-i',str(project/'audio.wav'),'-map','0:v:0','-map','1:a:0','-t',str(length),
         '-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(temporary)]
    with log.open('wb') as logfile, browser_page(project,p) as (page,errors):
        # Canvas dimensions can be overridden without rewriting the source project.
        page.evaluate('(p)=>Vibe.init(p)',p)
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=logfile)
        try:
            for i in range(count):
                proc.stdin.write(png(page,min(end-1e-6,start+i/p['fps'])))
                if i%p['fps']==0:print(f'{i}/{count} frames',flush=True)
            proc.stdin.close();code=proc.wait()
            if code or errors:raise RuntimeError(f'Render failed: {code}, {errors}; see {log}')
        except BaseException:
            if proc.poll() is None:proc.kill()
            proc.wait();temporary.unlink(missing_ok=True);raise
    # Decode both streams: do not call a successful encode sufficient evidence.
    checked=subprocess.run([ffmpeg(),'-v','error','-i',str(temporary),'-map','0:v:0','-map','0:a:0',
                            '-progress','pipe:1','-nostats','-f','null','-'],capture_output=True,text=True)
    if checked.returncode or checked.stderr:
        temporary.unlink(missing_ok=True);raise RuntimeError(checked.stderr)
    decoded_frames=[int(line.split('=',1)[1]) for line in checked.stdout.splitlines() if line.startswith('frame=')]
    if not decoded_frames or decoded_frames[-1]!=count:
        temporary.unlink(missing_ok=True);raise RuntimeError(f'Frame count mismatch: requested {count}, decoded {decoded_frames}')
    import imageio_ffmpeg
    reader=imageio_ffmpeg.read_frames(str(temporary));meta=next(reader);reader.close()
    if tuple(meta['size'])!=(p['width'],p['height']) or abs(meta['fps']-p['fps'])>.02:
        temporary.unlink(missing_ok=True);raise RuntimeError('Encoded dimensions/fps mismatch')
    temporary.replace(dest)
    write_json(out/(label+'.json'),{'file':dest.name,'width':p['width'],'height':p['height'],'fps':p['fps'],
        'frames_requested':count,'frames_decoded':decoded_frames[-1],'start':start,'duration_requested':length,
        'encoded_metadata':meta,'decode_passed':True,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    print(dest)

def docs(project):
    project,p=load(project)
    def stamp(t):
        ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
        return f'{h:02}:{m:02}:{s:02},{ms:03}'
    (project/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(s["start"])} --> {stamp(s["end"])}\n{s["text"]}' for i,s in enumerate(p['subtitles']))+'\n',encoding='utf-8')
    rows=['# '+p['title'],'','| 时间 | 分镜 | 视觉实现 | 字幕 |','|---|---|---|---|']
    for s in p['scenes']:
        subs=' / '.join(x['text'].replace('\n',' ') for x in p['subtitles'] if x['start']<s['end'] and x['end']>s['start'])
        rows.append(f'| {s["start"]}–{s["end"]}s | {s["title"]} | {s.get("description",s["visual"])} | {subs} |')
    (project/'storyboard.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    rows=['# 来源与主张','','说明：verified 是编辑核查状态，不代表程序自动判断事实真伪。','']
    for s in p['sources']:rows.extend([f'## {s["id"]} · {s["title"]}',s['url'],f'核查日期：{s["checked_at"]}',''])
    for c in p['claims']:rows.extend([f'### {c["id"]} · {c["text"]}',f'出处：{", ".join(c["sources"])}',c['evidence'],''])
    (project/'research.md').write_text('\n'.join(rows),encoding='utf-8')
    (project/'publish.md').write_text(f'# {p["title"]}\n\n{p.get("description",p["title"])}\n\n代码动画演示 · 无旁白 · AI 辅助制作\n\n素材与来源见 research.md 和 project.json。\n',encoding='utf-8')
    print('Wrote storyboard.md, research.md, subtitles.srt, publish.md')

def new(path,title,duration):
    path=Path(path).resolve()
    if path.exists() and any(path.iterdir()):raise ValueError('Destination must be empty')
    path.mkdir(parents=True,exist_ok=True)
    p={'title':title,'description':'待编写','duration':duration,'width':1920,'height':1080,'fps':30,'series':'知识短片',
       'audio':{'bpm':80},'sources':[],'claims':[],
       'assets':[{'name':'code graphics and synthesized sound','origin':'original code','license':'original project assets'}],
       'scenes':[{'id':'opening','start':0,'end':duration,'title':title,'visual':'cards','items':['待设计画面']}],
       'subtitles':[{'start':0,'end':duration,'text':'请先完成资料核查和分镜。','kind':'editorial','claims':[]}]}
    write_json(path/'project.json',p)
    (path/'scenes.js').write_text('// Register scene renderers with Vibe.register(name, ({ctx,t,lt,s,p,...helpers})=>{}).\n',encoding='utf-8')
    prepare(path);docs(path);print(path)

def doctor():
    import importlib.util
    modules={name:bool(importlib.util.find_spec(name)) for name in ['playwright','PIL','numpy','imageio_ffmpeg']}
    binary=ffmpeg();result=subprocess.run([binary,'-version'],capture_output=True,text=True,check=True)
    print(json.dumps({'python':sys.executable,'modules':modules,'ffmpeg':binary,'ffmpeg_version':result.stdout.splitlines()[0],
                      'browser':chrome() or 'Playwright managed Chromium required'},ensure_ascii=False,indent=2))
    if not all(modules.values()):raise RuntimeError('Missing dependencies')

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    x=sub.add_parser('new');x.add_argument('project');x.add_argument('--title',required=True);x.add_argument('--duration',type=float,default=120)
    for name in ['validate','docs','audio','review','preview','render']:
        x=sub.add_parser(name);x.add_argument('project')
        if name=='preview':x.add_argument('--port',type=int,default=8765)
        if name=='render':
            x.add_argument('--start',type=float,default=0);x.add_argument('--end',type=float);x.add_argument('--width',type=int)
    a=parser.parse_args()
    if a.command=='doctor':doctor()
    elif a.command=='new':new(a.project,a.title,a.duration)
    elif a.command=='validate':
        _,p=load(a.project);print(json.dumps({'structural_validation':'passed','reading_warnings':reading_warnings(p)},ensure_ascii=False))
    elif a.command=='docs':docs(a.project)
    elif a.command=='audio':audio(a.project)
    elif a.command=='review':review(a.project)
    elif a.command=='render':render(a.project,a.start,a.end,a.width)
    elif a.command=='preview':
        project,_=prepare(a.project)
        with server(project,a.port) as url:
            print(url,flush=True)
            try:threading.Event().wait()
            except KeyboardInterrupt:pass

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(f'ERROR: {exc}',file=sys.stderr);sys.exit(1)
