# overlay pass: letterbox + brand, word-reveal subtitles, place tags, year chips, light leaks, grain
import sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0,'/home/claude/adi1')
from c2 import *
OUT=sys.argv[1]
TOT=END
# static bars
bars=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(bars)
d.rectangle([0,0,W,BAR],fill=(0,0,0,255)); d.rectangle([0,H-BAR,W,H],fill=(0,0,0,255))
d.rectangle([0,BAR,W,BAR+3],fill=BLUE+(255,)); d.rectangle([0,H-BAR-3,W,H-BAR],fill=BLUE+(180,))
l=logo.copy(); l.thumbnail((92,92)); bars.alpha_composite(l,(34,(BAR-l.height)//2+12))
d.text((140,BAR/2+12),'ന്യൂസ് അട്ടപ്പാടി',font=ANEK(32,'Bold'),fill=(235,235,235),anchor='lm')
d.text((W-36,BAR/2+12),'ആദിരക്തം · ഭാഗം 1',font=SERIFB(30),fill=TINT,anchor='rm')
BARS=np.asarray(bars).astype(np.float32)
def tagimg(s):
    im=Image.new('RGBA',(W,60),(0,0,0,0)); ImageDraw.Draw(im).text((W-36,30),s,font=ANEK(26,'Medium'),fill=(185,185,185,255),anchor='rm'); return im
SHOT_TAG=[]
for (a,b,kind,src,g,o) in SHOTS:
    if kind=='card' and src!='title': SHOT_TAG.append((a,b,None)); continue
    if kind=='card': SHOT_TAG.append((a,b,None)); continue
    c=cred.get(src,{}).get('credit','') if kind=='img' else ''
    s=o.get('tag','')+((' · ചിത്രം: '+c) if c else '')
    SHOT_TAG.append((a,b,tagimg(s)))
SUBF=ANEK(54,'SemiBold')
def words_layer(text,t0,t1,t):
    """word-by-word reveal; returns RGBA layer for subtitle region"""
    im=Image.new('RGBA',(W,330),(0,0,0,0)); d=ImageDraw.Draw(im)
    ws=text.split(' ')
    # wrap into lines
    lines=[];cur=[]
    for w in ws:
        if d.textlength(' '.join(cur+[w]),font=SUBF)>W-150 and cur: lines.append(cur); cur=[w]
        else: cur.append(w)
    if cur: lines.append(cur)
    n=sum(len(x) for x in ws); span=min(t1-t0-0.15,max(0.5,0.075*n)); acc=0
    out_a=1-ease((t-(t1-0.25))/0.25)
    y=330-60-(len(lines)-1)*76
    sh=Image.new('RGBA',im.size,(0,0,0,0)); sd=ImageDraw.Draw(sh)
    for ln in lines:
        lw=d.textlength(' '.join(ln),font=SUBF); x=W/2-lw/2
        for w in ln:
            st=t0+span*acc/n; acc+=len(w)
            a=ease((t-st)/0.28)*out_a
            if a>0:
                dy=10*(1-eout((t-st)/0.35))
                sd.text((x+2,y+4+dy),w,font=SUBF,fill=(0,0,0,int(220*a)),anchor='lm')
                d.text((x,y+dy),w,font=SUBF,fill=(255,250,240,int(255*a)),anchor='lm')
            x+=d.textlength(w+' ',font=SUBF)
        y+=76
    sh=sh.filter(ImageFilter.GaussianBlur(5)); sh.alpha_composite(im); return sh
def place_layer(name,t):
    im=Image.new('RGBA',(W,170),(0,0,0,0)); d=ImageDraw.Draw(im); f=BALOO(46)
    p=eout(t/0.6); x0=-500+536*p; tw=d.textlength(name,font=f)
    d.rounded_rectangle([x0,40,x0+tw+120,120],radius=14,fill=NAVY+(215,)); d.rectangle([x0,40,x0+10,120],fill=BLUE+(255,))
    # pin
    cx=x0+52; d.ellipse([cx-16,58,cx+16,90],fill=(255,255,255,255)); d.polygon([(cx-13,82),(cx+13,82),(cx,106)],fill=(255,255,255,255)); d.ellipse([cx-6,68,cx+6,80],fill=BLUE+(255,))
    d.text((x0+90,82),name,font=f,fill=(255,255,255,255),anchor='lm')
    return im
def chip_layer(yr,lab,t):
    im=Image.new('RGBA',(W,230),(0,0,0,0)); d=ImageDraw.Draw(im)
    a=ease(t/0.35); p=eout(t/0.9)
    num=int(yr.replace(',',''))*p; s='~'+f'{int(round(num/100)*100):,}'
    d.rounded_rectangle([36,30,560,190],radius=10,fill=(236,222,196,int(232*a)),outline=(90,60,30,int(255*a)),width=3)
    d.text((66,92),s,font=CINZEL(76),fill=(60,35,15,int(255*a)),anchor='lm')
    d.text((66,158),'വർഷം മുമ്പ് · '+lab,font=ANEK(34,'Bold'),fill=(90,55,25,int(255*a)),anchor='lm')
    return im
# grain tiles
rng=np.random.default_rng(1)
GR=[(rng.normal(0,1,(H//2,W//2,1))*9).astype(np.float32) for _ in range(6)]
GR=[np.repeat(np.repeat(g,2,0),2,1) for g in GR]
yy,xx=np.mgrid[0:H,0:W]; VIG=(1-0.42*(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.7))**2)).clip(0.45,1)[...,None].astype(np.float32)
def leak(t):
    best=None
    for s in LEAKS:
        if s-0.1<t<s+1.0: best=s
    if best is None: return None
    p=(t-best)/1.0; a=math.sin(math.pi*max(0,min(1,p)))
    return a
LEAKIMG=None
def leak_arr():
    global LEAKIMG
    if LEAKIMG is None:
        im=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(im)
        d.ellipse([-300,-200,700,900],fill=(255,140,50)); d.ellipse([500,1100,1400,2200],fill=(255,90,40))
        LEAKIMG=np.asarray(im.filter(ImageFilter.GaussianBlur(220))).astype(np.float32)
    return LEAKIMG
dec=subprocess.Popen(['ffmpeg','-v','error','-i',T+'bg.mp4','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',T+'ov.mp4'],stdin=subprocess.PIPE)
N=int(round(TOT*FPS)); last=None
for i in range(N):
    t=i/FPS
    raw=dec.stdout.read(W*H*3)
    if len(raw)==W*H*3: last=raw
    f=np.frombuffer(last,np.uint8).reshape(H,W,3).astype(np.float32)
    # gate weave
    if i%2==0:
        dx=int(round(math.sin(t*7.3)*1.2)); dy=int(round(math.sin(t*5.1)*1.5))
        f=np.roll(f,(dy,dx),(0,1))
    la=leak(t)
    if la: f=255-(255-f)*(255-leak_arr()*la*0.55)/255
    f=f*VIG+GR[i%6]
    # flicker
    f*=1+0.012*math.sin(t*23.0)
    img=Image.fromarray(np.clip(f,0,255).astype(np.uint8)).convert('RGBA')
    end_card=t>=TV
    if not end_card:
        img.alpha_composite(bars)
        for (a,b,tg) in SHOT_TAG:
            if tg is not None and a<=t<b:
                al=ease((t-a)/0.4)*(1-ease((t-(b-0.2))/0.2)); tl=tg.copy(); tl.putalpha(tl.split()[3].point(lambda v:int(v*al))); img.alpha_composite(tl,(0,H-BAR+20))
        for (a,b,kind,src,g,o) in SHOTS:
            if a<=t<b and o and 'place' in o:
                nm,st=o['place']
                if t>=a+st:
                    pl=place_layer(nm,t-a-st); al=1-ease((t-(b-0.35))/0.35)
                    if al<1: pl.putalpha(pl.split()[3].point(lambda v:int(v*al)))
                    img.alpha_composite(pl,(0,BAR+40))
            if a<=t<b and o and 'chip' in o:
                yr,lab=o['chip']; ch=chip_layer(yr,lab,t-a-0.1); img.alpha_composite(ch,(0,BAR+30))
        for (a,b,s) in SUBS:
            if a<=t<b+0.05:
                img.alpha_composite(words_layer(s,a,b,t),(0,H-BAR-330-30))
    enc.stdin.write(img.convert('RGB').tobytes())
    if i%250==0: print('ov',i,N,flush=True)
dec.stdout.close(); enc.stdin.close(); enc.wait()
# audio
sys.path.insert(0,'/home/claude/adi1'); from shots import S, SFX
AUD=A; GAP=0.3
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
import shutil; shutil.copy(T+'ov.mp4',T+'video.mp4')
exec(open('/home/claude/adi1/audio_part.py').read().replace("T+'video.mp4'","T+'video.mp4'"))
