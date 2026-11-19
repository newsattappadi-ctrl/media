import sys, os, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0,'/home/claude/ep1'); from shots import S, L
W,H=int(sys.argv[1]),int(sys.argv[2]); OUT=sys.argv[3]; V=H>W
S_=W/1920 if not V else W/1080
T=f'/home/claude/ep1/tmp_{W}x{H}/'; os.makedirs(T,exist_ok=True)
AUD='/home/claude/media/assets/audio/'
NAVY,BLUE,GREY,WHITE,TINT=(6,54,74),(10,122,191),(77,77,77),(255,255,255),(124,200,255)
FPS=25; GAP=0.45
FD='/home/claude/vid/fonts/'
def mj(z): return ImageFont.truetype(FD+'manjari-full-700.ttf',int(z),layout_engine=ImageFont.Layout.RAQM)
def bc(z): return ImageFont.truetype(FD+'barlow-condensed-latin-700-normal.ttf',int(z))
logo=Image.open('/home/claude/na/logo.png').convert('RGBA'); logo=logo.crop(logo.getbbox())
cred=json.load(open(L+'credits.json'))
def s(v): return int(v*S_)
def wrap(d,t,f,mw):
    o,c=[], ''
    for w in t.split(' '):
        x=(c+' '+w).strip()
        if d.textlength(x,font=f)<=mw or not c: c=x
        else: o.append(c); c=w
    if c:o.append(c)
    return o
def fit(d,t,size,mw,fn=mj):
    f=fn(size)
    while d.textlength(t,font=f)>mw and size>10: size-=2; f=fn(size)
    return f
STRAP_H=s(96); STRAP_Y=H-STRAP_H-s(250 if V else 40)
def chrome(credit):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for y in range(s(190)): d.line([(0,y),(W,y)],fill=(0,0,0,int(120*(1-y/s(190)))))
    l=logo.copy(); z=s(150 if V else 130); l.thumbnail((z,z),Image.LANCZOS); im.alpha_composite(l,(s(36),s(90 if V else 28)))
    d.text((W-s(36),s(100 if V else 40)),'@newsattappadi',font=bc(s(38)),fill=WHITE,anchor='ra')
    d.text((W-s(36),s(150 if V else 88)),'അന്വേഷണ പരമ്പര · ഭാഗം 1',font=mj(s(30)),fill=TINT,anchor='ra',stroke_width=2,stroke_fill=(0,0,0))
    lab='സ്വന്തം മണ്ണിലെ അഭയാർത്ഥികൾ' if not V else 'അന്വേഷണ പരമ്പര'
    lf=mj(s(40 if not V else 40)); lw=int(d.textlength(lab,font=lf)+s(56))
    d.rectangle([0,STRAP_Y,lw,STRAP_Y+STRAP_H],fill=BLUE); d.text((lw/2,STRAP_Y+STRAP_H/2+s(4)),lab,font=lf,fill=WHITE,anchor='mm')
    d.rectangle([lw,STRAP_Y,W,STRAP_Y+STRAP_H],fill=WHITE); d.rectangle([0,STRAP_Y+STRAP_H,W,STRAP_Y+STRAP_H+s(10)],fill=NAVY)
    hl='കാട് പോയി, പുഴ വറ്റി'; hf=fit(d,hl,s(52),W-lw-s(50))
    d.text((lw+s(26),STRAP_Y+STRAP_H/2+s(4)),hl,font=hf,fill=NAVY,anchor='lm')
    if credit:
        cf=mj(s(24)); y=STRAP_Y+STRAP_H+s(16)
        for ln in wrap(d,credit,cf,W-s(72))[:2]:
            d.text((W-s(36),y),ln,font=cf,fill=WHITE,anchor='ra',stroke_width=2,stroke_fill=(0,0,0)); y+=s(30)
    return im
def caption(text):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    f=mj(s(64 if V else 66)); mw=W-s(150); lines=wrap(d,text,f,mw); lh=int(f.size*1.3)
    bh=lh*len(lines)+s(34); by=STRAP_Y-bh-s(22); bw=max(d.textlength(x,font=f) for x in lines)+s(78)
    d.rectangle([s(36),by,s(36)+bw,by+bh],fill=NAVY+(238,)); d.rectangle([s(36),by,s(48),by+bh],fill=BLUE)
    y=by+s(20)
    for ln in lines: d.text((s(80),y),ln,font=f,fill=WHITE); y+=lh
    return im
def bgpanel():
    im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
    for i in range(0,W+H,s(70)): d.line([(i,0),(i-H,H)],fill=(10,64,88),width=s(3))
    return im
def card(kind,data):
    im=bgpanel(); d=ImageDraw.Draw(im); cx,cy=W/2,H/2-s(60 if V else 20)
    def ctext(t,y,f,col=WHITE): d.text((cx,y),t,font=f,fill=col,anchor='mm')
    if kind=='title':
        l=logo.copy(); z=s(260); l.thumbnail((z,z)); im.paste(l,(int(cx-l.width/2),int(cy-s(210)-l.height)),l)
        ctext('ന്യൂസ് അട്ടപ്പാടി അന്വേഷണ പരമ്പര',cy-s(130),fit(d,'ന്യൂസ് അട്ടപ്പാടി അന്വേഷണ പരമ്പര',s(52),W-s(120)),TINT)
        t='സ്വന്തം മണ്ണിലെ അഭയാർത്ഥികൾ'
        if V:
            ctext('സ്വന്തം മണ്ണിലെ',cy+s(10),mj(s(120))); ctext('അഭയാർത്ഥികൾ',cy+s(160),mj(s(120)))
        else: ctext(t,cy+s(30),fit(d,t,s(130),W-s(160)))
        d.rectangle([cx-s(200),cy+s(260 if V else 140),cx+s(200),cy+s(268 if V else 148)],fill=BLUE)
        ctext('ഇന്ന് തുടങ്ങുന്നു',cy+s(330 if V else 210),mj(s(50)),WHITE)
    elif kind=='parts':
        parts=[('1','കാട്'),('2','മണ്ണ്'),('3','ശരീരം'),('4','സ്വത്വം')]
        ctext('നാല് ഭാഗങ്ങൾ',cy-s(330 if V else 250),mj(s(60)),TINT)
        for i,(n,t) in enumerate(parts):
            if V: x,y=cx,cy-s(170)+i*s(170)
            else: x,y=W*(i+1)/5,cy+s(20)
            bw,bh=s(360 if V else 300),s(140 if V else 200)
            d.rectangle([x-bw/2,y-bh/2,x+bw/2,y+bh/2],fill=BLUE if i==0 else (10,64,88),outline=WHITE if i==0 else TINT,width=s(4))
            if V:
                d.text((x-bw/2+s(40),y),n,font=bc(s(90)),fill=WHITE,anchor='lm'); d.text((x-bw/2+s(120),y+s(6)),t,font=mj(s(60)),fill=WHITE,anchor='lm')
            else:
                d.text((x,y-s(40)),n,font=bc(s(100)),fill=WHITE,anchor='mm'); d.text((x,y+s(55)),t,font=mj(s(56)),fill=WHITE,anchor='mm')
        ctext('ഭാഗം 1: കാട് പോയി, പുഴ വറ്റി',cy+s(560 if V else 260),fit(d,'ഭാഗം 1: കാട് പോയി, പുഴ വറ്റി',s(58),W-s(100)))
    elif kind=='stat':
        big,lab=data; f=fit(d,big,s(300 if V else 280),W-s(120),bc)
        ctext(big,cy-s(40),f,WHITE)
        for i,ln in enumerate(wrap(d,lab,mj(s(60)),W-s(140))): ctext(ln,cy+s(170)+i*s(80),mj(s(60)),TINT)
    elif kind=='timeline':
        ev=[('18-ാം നൂറ്റാണ്ട്','സാമൂതിരി'),('','മൂപ്പിൽ നായർ · പാലാട്ട് · ഏറാൾപ്പാട്'),('','മൈസൂർ'),('1792','ബ്രിട്ടീഷ്')]
        if V:
            x0=s(160); d.line([(x0,cy-s(420)),(x0,cy+s(420))],fill=TINT,width=s(6))
            for i,(a,b) in enumerate(ev):
                y=cy-s(360)+i*s(240); d.ellipse([x0-s(22),y-s(22),x0+s(22),y+s(22)],fill=BLUE,outline=WHITE,width=s(4))
                if a: d.text((x0+s(60),y-s(40)),a,font=mj(s(40)),fill=TINT,anchor='lm')
                for j,ln in enumerate(wrap(d,b,mj(s(54)),W-x0-s(120))): d.text((x0+s(60),y+s(20)+j*s(66)),ln,font=mj(s(54)),fill=WHITE,anchor='lm')
        else:
            y0=cy; d.line([(s(140),y0),(W-s(140),y0)],fill=TINT,width=s(6))
            for i,(a,b) in enumerate(ev):
                x=s(240)+i*(W-s(480))/3; d.ellipse([x-s(22),y0-s(22),x+s(22),y0+s(22)],fill=BLUE,outline=WHITE,width=s(4))
                if a: d.text((x,y0-s(80)),a,font=mj(s(40)),fill=TINT,anchor='mm')
                for j,ln in enumerate(wrap(d,b,mj(s(46)),s(380))): d.text((x,y0+s(80)+j*s(58)),ln,font=mj(s(46)),fill=WHITE,anchor='mm')
        ctext('ഭരണം മാറി, കൊള്ള മാറിയില്ല',H-s(560 if V else 230),fit(d,'ഭരണം മാറി, കൊള്ള മാറിയില്ല',s(60),W-s(100)),WHITE)
    elif kind=='bar':
        ctext('അട്ടപ്പാടിയിലെ വനം',cy-s(330 if V else 260),mj(s(64)),TINT)
        bw=W-s(240); x0=s(120)
        for i,(lab,val,col) in enumerate([('അന്ന്',82,BLUE),('ഇന്ന്',20,GREY)]):
            y=cy-s(120)+i*s(240); d.rectangle([x0,y,x0+bw,y+s(120)],outline=(30,90,120),width=s(3))
            d.rectangle([x0,y,x0+bw*val/100,y+s(120)],fill=col)
            d.text((x0,y-s(46)),lab,font=mj(s(48)),fill=WHITE,anchor='lm')
            d.text((x0+bw*val/100+s(20),y+s(60)),f'{val}%',font=bc(s(110)),fill=WHITE,anchor='lm')
        ctext('ഏകദേശ കണക്ക്',cy+s(330),mj(s(36)),TINT)
    elif kind=='ahads':
        ctext('അഹാഡ്സ്',cy-s(300 if V else 250),mj(s(110)),WHITE)
        items=[('1996–2009','13 വർഷം'),('₹219 കോടി','ജപ്പാൻ സഹായം'),('നീർത്തടം','മരം, മണ്ണ്, വെള്ളം')]
        for i,(a,b) in enumerate(items):
            if V: x,y=cx,cy-s(80)+i*s(230)
            else: x,y=W*(i+1)/4,cy+s(40)
            d.text((x,y),a,font=fit(d,a,s(96),s(460),bc) if a[0].isdigit() else mj(s(80)),fill=TINT,anchor='mm'); d.text((x,y+s(90)),b,font=mj(s(46)),fill=WHITE,anchor='mm')
    elif kind=='rivers':
        ctext('അട്ടപ്പാടിയുടെ പുഴകൾ',cy-s(330 if V else 260),mj(s(64)),TINT)
        rv=['ഭവാനി','ശിരുവാണി','വരഗാർ','കൊടുങ്ങരപ്പള്ളം']
        for i,r in enumerate(rv):
            y=cy-s(150)+i*s(130 if not V else 150); col=TINT if i==3 else WHITE
            d.line([(cx-s(330),y),(cx-s(230),y)],fill=BLUE,width=s(10)); d.text((cx-s(200),y),r,font=mj(s(66)),fill=col,anchor='lm')
        ctext('38 കി.മീ. — വീണ്ടും ഒഴുകി',cy+s(450 if V else 400),mj(s(52)),TINT)
    elif kind=='end2009':
        for i,(a,b) in enumerate([('2009','അഹാഡ്സ് അവസാനിച്ചു'),('310','സ്ഥാപനങ്ങൾ നിശ്ചലം')]):
            if V: x,y=cx,cy-s(220)+i*s(440)
            else: x,y=W*(i+1)/3,cy
            d.text((x,y-s(40)),a,font=bc(s(230)),fill=WHITE,anchor='mm'); d.text((x,y+s(130)),b,font=mj(s(54)),fill=TINT,anchor='mm')
    elif kind=='next':
        ctext('സ്വന്തം മണ്ണിലെ അഭയാർത്ഥികൾ',cy-s(200),fit(d,'സ്വന്തം മണ്ണിലെ അഭയാർത്ഥികൾ',s(80),W-s(120)),TINT)
        ctext('ഭാഗം 2',cy-s(40),mj(s(130)),WHITE)
        ctext('ഭൂമി പോയ വഴി',cy+s(110),mj(s(80)),WHITE)
        d.rectangle([cx-s(140),cy+s(200),cx+s(140),cy+s(270)],fill=BLUE); ctext('ഉടൻ',cy+s(238),mj(s(52)),WHITE)
    return im
def cover(path):
    im=Image.open(path).convert('RGB'); 
    if 'irula_men' in path or 'irula_women' in path: im=im.crop((int(im.width*0.08),int(im.height*0.12),int(im.width*0.78),int(im.height*0.70)))
    # blurred fill + fitted image if aspect differs a lot
    r=max(W/im.width,H/im.height); bg=im.resize((int(im.width*r)+2,int(im.height*r)+2)).crop((0,0,W,H)).filter(ImageFilter.GaussianBlur(s(30))); bg=ImageEnhance.Brightness(bg).enhance(0.55)
    ar_i=im.width/im.height; ar_f=W/H
    if abs(ar_i-ar_f)/ar_f<0.35:
        bg2=im.resize((int(im.width*r)+2,int(im.height*r)+2)); x=(bg2.width-W)//2; y=(bg2.height-H)//2; return bg2.crop((x,y,x+W,y+H))
    r2=min(W/im.width,H*0.82/im.height); fg=im.resize((int(im.width*r2),int(im.height*r2))); bg.paste(fg,((W-fg.width)//2,(H-fg.height)//2 - s(40 if V else 0))); return bg
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# build segments
segs=[]; n=0
creds=set()
for sec,shots in S:
    d=dur(AUD+f'ep1_{sec}.wav')+GAP; per=d/len(shots)
    for sh in shots:
        n+=1; base=T+f'b{n:02d}.png'; ov=T+f'o{n:02d}.png'; vid=T+f'v{n:02d}.mp4'
        if sh[0]=='img':
            _,f,cap,lab=sh; c=cred.get(f,{}).get('credit','')
            creds.add(c); cr=(lab+' · ' if lab else '')+'ചിത്രം: '+c
            cover(L+f).save(base); o=chrome(cr); o.alpha_composite(caption(cap)); o.save(ov); kb=True
        else:
            card(sh[1],sh[2]).save(base); chrome(None).save(ov) if sh[1] not in('title','parts','next') else Image.new('RGBA',(W,H),(0,0,0,0)).save(ov); kb=False
        fr=int(round(per*FPS))
        z="min(1.0+0.0007*on,1.15)" if kb else "1.0+0.00012*on"
        vf=f"scale={int(W*1.2)}:{int(H*1.2)},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s={W}x{H}:fps={FPS}[bg];[1:v]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1[ov];[bg][ov]overlay=0:0,fade=t=in:st=0:d=0.25,format=yuv420p"
        subprocess.run(['ffmpeg','-y','-v','error','-loop','1','-i',base,'-loop','1','-i',ov,'-filter_complex',vf,'-frames:v',str(fr),'-c:v','libx264','-preset','veryfast','-crf','20','-r',str(FPS),vid],check=True)
        segs.append(vid)
# end card
n+=1; endp=T+'end.png'; im=bgpanel(); d=ImageDraw.Draw(im); l=logo.copy(); l.thumbnail((s(300),s(300))); im.paste(l,(int(W/2-l.width/2),int(H/2-s(130)-l.height)),l)
d.text((W/2,H/2-s(40)),'NEWS ATTAPPADI',font=bc(s(110)),fill=WHITE,anchor='mm'); d.text((W/2,H/2+s(60)),'വാർത്തകൾ വിശദമായി',font=mj(s(52)),fill=TINT,anchor='mm'); d.text((W/2,H/2+s(140)),'Follow @newsattappadi',font=bc(s(60)),fill=WHITE,anchor='mm')
y=H/2+s(240); cf=mj(s(22))
for ln in wrap(d,'ചിത്രങ്ങൾ: '+' | '.join(sorted(c for c in creds if c)),cf,W-s(120)): d.text((W/2,y),ln,font=cf,fill=TINT,anchor='mm'); y+=s(30)
im.save(endp); ev=T+'v_end.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-loop','1','-i',endp,'-t','6','-vf','fade=t=in:d=0.4,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','20','-r',str(FPS),ev],check=True); segs.append(ev)
open(T+'list.txt','w').write(''.join(f"file '{x}'\n" for x in segs))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',T+'list.txt','-c','copy',T+'video.mp4'],check=True)
# audio: VO sections each followed by GAP silence
parts=[]; 
for sec,_ in S: parts.append(AUD+f'ep1_{sec}.wav')
inp=[]; fc=''
for i,p in enumerate(parts): inp+=['-i',p]; fc+=f'[{i}:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur={GAP}[a{i}];'
fc+=''.join(f'[a{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=0:a=1[vo]'
subprocess.run(['ffmpeg','-y','-v','error']+inp+['-filter_complex',fc,'-map','[vo]',T+'vo.wav'],check=True)
tv=dur(T+'video.mp4'); vd=dur(T+'vo.wav')
mus=AUD+'exodus_music.mp3'
fc=(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.6[v];"
    f"[2:a]aresample=48000,aformat=channel_layouts=stereo,aloop=loop=-1:size=2e9,atrim=0:{tv},volume='if(lt(t,2.0),0.35,if(gt(t,{vd}),0.30,0.08))':eval=frame,afade=t=out:st={tv-2.5}:d=2.5[m];"
    f"[v][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]")
subprocess.run(['ffmpeg','-y','-v','error','-i',T+'video.mp4','-i',T+'vo.wav','-i',mus,'-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(tv),OUT],check=True)
print('done',OUT,tv,vd)
