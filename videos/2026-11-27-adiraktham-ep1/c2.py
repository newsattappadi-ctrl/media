# ആദിരക്തം ഭാഗം 1 — cinematic documentary v2
import sys, os, json, subprocess, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0,'/home/claude/adi1')
import title3d
W,H=1080,1920; FPS=25; BAR=150; XF=0.45
T='/home/claude/adi1/c2/'; os.makedirs(T,exist_ok=True)
L='/home/claude/media/assets/library/'; A='/home/claude/media/assets/audio/'
FD='/home/claude/fonts2/'
NAVY,BLUE,TINT=(6,54,74),(10,122,191),(124,200,255)
INK=(52,30,14)
def font(n,s,v=None):
    f=ImageFont.truetype(FD+n,int(s),layout_engine=ImageFont.Layout.RAQM)
    if v: f.set_variation_by_name(v)
    return f
SERIF=lambda s:font('NotoSerifMalayalam.ttf',s,'Black')
SERIFB=lambda s:font('NotoSerifMalayalam.ttf',s,'Bold')
ANEK=lambda s,v='SemiBold':font('AnekMalayalam.ttf',s,v)
BALOO=lambda s:font('BalooChettan2.ttf',s,'ExtraBold')
CINZEL=lambda s:font('Cinzel.ttf',s,'Bold')
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
def eout(x): x=max(0.,min(1.,x)); return 1-(1-x)**3
logo=Image.open('/home/claude/na/logo.png').convert('RGBA'); logo=logo.crop(logo.getbbox())
cred=json.load(open(L+'credits.json')); cred.update(json.load(open('/home/claude/adi1/newcred.json')))
PARCH=Image.open(L+'adi1_parchment.jpg').convert('RGB').resize((W,H))
AI='AI ചിത്രീകരണം'
S0,S1,S2,S3,S4,S5,S6,S7=0,17.34,32.96,39.9,54.68,93.66,100.92,113.86
TV=119.24; END=TV+6
# ---------------- shot list ----------------
# (start,end,kind,src,grade,opts)
SHOTS=[
 (0,6.0,'vid','adi1_v_peak.mp4','film',dict(tag=AI)),
 (6.0,10.4,'img','malleswaran_mudi_2.jpg','dark',dict(tag='മല്ലീശ്വരൻ മുടി, അട്ടപ്പാടി')),
 (10.4,S1,'vid','adi1_v_valley.mp4','film',dict(tag=AI)),
 (S1,S1+2.86,'vid','adi1_w_knap.mp4','film',dict(tag=AI)),
 (S1+2.86,S1+5.16,'vid','adi1_w_family.mp4','film',dict(tag=AI,ss=2.6)),
 (S1+5.16,S1+7.76,'vid','adi1_w_canoe.mp4','film',dict(tag=AI)),
 (S1+7.76,S1+10.76,'vid','adi1_w_chief.mp4','film',dict(tag=AI)),
 (S1+10.76,S2,'img','muduga_women.jpg','warm',dict(tag='മുഡുഗ സ്ത്രീകൾ, അട്ടപ്പാടി')),
 (S2,S3,'card','title',None,{}),
 (S3,S3+5.1,'vid','adi1_v_dig.mp4','film',dict(tag=AI,place=('മുക്കാലി',0.3))),
 (S3+5.1,S3+8.4,'vid','adi1_w_palm.mp4','film',dict(tag=AI,place=('അഗളി · ചേരക്കൽപ്പാടി',0.3))),
 (S3+8.4,S3+11.5,'img','a1_attirampakkam.jpg','film',dict(tag='ശിലായുധങ്ങൾ — പ്രതീകാത്മക ചിത്രം')),
 (S3+11.5,S4,'img','sv_karuvara.jpg','film',dict(tag='സൈലന്റ് വാലി, മുക്കാലി')),
 (S4,S4+1.62,'card','year',None,{}),
 (S4+1.62,S4+4.32,'img','a1_pyramid2.jpg','bw',dict(tag='ഗിസ, ഈജിപ്ത്',chip=('4,500','പിരമിഡ്'))),
 (S4+4.32,S4+7.92,'img','a1_pyramid.jpg','bw',dict(tag='ഗിസ, ഈജിപ്ത്')),
 (S4+7.92,S4+9.92,'img','a1_stonehenge.jpg','bw',dict(tag='സ്റ്റോൺഹെഞ്ച്, ഇംഗ്ലണ്ട്',chip=('5,000','സ്റ്റോൺഹെഞ്ച്'))),
 (S4+9.92,S4+15.22,'img','a1_stonehenge2.jpg','bw',dict(tag='ബ്രിട്ടൻ',chip=('8,000','ബ്രിട്ടൻ ദ്വീപായത്'))),
 (S4+15.22,S4+16.62,'img','a1_harappa1.jpg','bw',dict(tag='ഹാരപ്പ',chip=('4,500','ഹാരപ്പ'))),
 (S4+16.62,S4+18.12,'img','a1_mohenjo.jpg','bw',dict(tag='മോഹൻജൊദാരോ',chip=('4,500','മോഹൻജൊദാരോ'))),
 (S4+18.12,S4+19.75,'img','a1_keeladi03.jpg','bw',dict(tag='കീഴടി, തമിഴ്നാട്',chip=('2,600','കീഴടി'))),
 (S4+19.75,S4+22.95,'card','nocity',None,{}),
 (S4+22.95,S4+29.2,'vid','adi1_w_family.mp4','fire',dict(tag=AI)),
 (S4+29.2,S4+31.4,'vid','adi1_w_knap.mp4','film',dict(tag=AI,ss=2.4)),
 (S4+31.4,S4+33.9,'vid','adi1_w_women.mp4','film',dict(tag=AI)),
 (S4+33.9,S5,'vid','adi1_w_hunters.mp4','film',dict(tag=AI)),
 (S5,S6,'card','timeline',None,{}),
 (S6,S6+5.98,'vid','adi1_w_river.mp4','film',dict(tag=AI)),
 (S6+5.98,S7,'vid','adi1_w_elder.mp4','film',dict(tag=AI)),
 (S7,TV,'card','next',None,{}),
 (TV,END,'card','end',None,{}),
]
QUICK={i for i,s in enumerate(SHOTS) if S4+1<=s[0]<=S4+19}  # hard-ish cuts in world montage
# subtitles: (start,end,text)
def R(base,lst): return [(base+a,base+b,t) for a,b,t in lst]
SUBS=R(S0,[(0.28,1.6,'ആദിവാസി.'),(1.88,3.6,'ഈ ഒറ്റ വാക്ക് കേൾക്കുമ്പോൾ,'),(3.8,7.4,'പലരുടെയും ചുണ്ടിൽ ഒരു പുച്ഛച്ചിരി വിടരും.'),
  (7.66,8.45,'പക്ഷേ,'),(8.56,10.3,'ആ ചിരി മായും.'),(10.5,11.9,'അട്ടപ്പാടിയുടെ മണ്ണ്'),(11.98,14.9,'പതിനായിരം വർഷമായി ഒളിപ്പിച്ചുവച്ച'),(14.98,17.2,'ആ രഹസ്യം അറിയുമ്പോൾ.')])+\
 R(S1,[(0.36,2.86,'ശിലായുഗം മുതൽ ഇന്നുവരെ.'),(3.06,5.16,'ഇന്ത്യയുടെ ആദ്യത്തെ രക്തം.'),(5.38,7.76,'കടൽ കടന്ന് നീളുന്ന വേരുകൾ.'),
  (7.94,10.76,'നഗരങ്ങൾക്ക് പേര് നൽകിയ തലവന്മാർ.'),(10.92,13.2,'നാം പുച്ഛിച്ചുതള്ളിയ ഒരു ജനതയുടെ,'),(13.38,15.5,'ആരും പറയാത്ത ചരിത്രം.')])+\
 R(S3,[(0.38,2.15,'മുക്കാലിയുടെ മണ്ണിനടിയിൽ,'),(2.28,5.2,'പ്രാചീന ശിലായുഗത്തിന്റെ കാൽപ്പാടുകൾ.'),(5.4,7.45,'അഗളിയിലും ചേരക്കൽപ്പാടിയിലും,'),
  (7.58,11.4,'മധ്യശിലായുഗ മനുഷ്യൻ ഉപേക്ഷിച്ചുപോയ കല്ലായുധങ്ങൾ.'),(11.56,14.6,'കാലം മായ്ക്കാൻ മറന്നുപോയ തെളിവുകൾ.')])+\
 R(S4,[(0.42,1.6,'ഒന്ന് ഓർത്തുനോക്കൂ.'),(1.78,4.3,'അന്ന് ഈജിപ്തിൽ പിരമിഡുകൾ ഇല്ല.'),(4.46,7.9,'അവ ഉയരാൻ ഇനിയും അയ്യായിരം വർഷം കാത്തിരിക്കണം.'),
  (8.04,9.9,'ഇംഗ്ലണ്ടിൽ സ്റ്റോൺഹെഞ്ച് ഇല്ല.'),(10.1,12.5,'ബ്രിട്ടൻ ഒരു ദ്വീപ് പോലും ആയിട്ടില്ല,'),(12.62,15.1,'യൂറോപ്പുമായി കര ചേർന്നുകിടക്കുന്നു.'),
  (15.36,16.6,'ഹാരപ്പയില്ല.'),(16.74,18.1,'മോഹൻജൊദാരോയില്ല.'),(18.28,19.7,'കീഴടിയില്ല.'),
  (23.18,23.95,'അപ്പോഴും,'),(24.04,26.9,'ഈ മലഞ്ചെരിവുകളിൽ മനുഷ്യൻ ഉണ്ടായിരുന്നു.'),(27.02,29.15,'അവൻ കല്ലുരച്ച് തീ കൊളുത്തി.'),
  (29.3,31.35,'കല്ലുരുട്ടി ആയുധം തീർത്തു.'),(31.44,33.75,'കാടിനോട് പൊരുതി ജീവിച്ചു.'),(33.86,36.2,'ലോകം ചരിത്രം എഴുതിത്തുടങ്ങും മുമ്പേ,'),(36.3,38.8,'അട്ടപ്പാടി ജീവിച്ചുതുടങ്ങിയിരുന്നു.')])+\
 R(S6,[(0.34,2.1,'അവർ ആരായിരുന്നു?'),(2.28,4.1,'ഇന്ന് ഈ മലകളിൽ ജീവിക്കുന്നവർ,'),(4.18,6.3,'അവരുടെ പിൻമുറക്കാരോ?'),(6.44,8.95,'ഉത്തരം കല്ലിലല്ല.'),(9.18,12.8,'ഇന്നും തുടിക്കുന്ന ഒരു രക്തത്തിലാണ്.')])
LEAKS=[S1-0.2,S3-0.2,S4+22.85,S6-0.2]
GRADE={'film':"eq=saturation=0.8:contrast=1.1:gamma=0.95,colorbalance=rs=0.05:bs=-0.04:rm=0.03:bm=-0.02:rh=0.04:bh=-0.05",
       'fire':"eq=saturation=0.95:contrast=1.12,colorbalance=rs=0.06:rm=0.05:bm=-0.04",
       'warm':"eq=saturation=0.8:contrast=1.05,colorbalance=rm=0.05:bm=-0.04",
       'dark':"eq=saturation=0.6:brightness=-0.08:contrast=1.15,colorbalance=bs=0.04",
       'bw':"hue=s=0,eq=contrast=1.3:brightness=-0.02,colorchannelmixer=rr=1.06:gg=0.98:bb=0.86"}
# ---------------- cards ----------------
def pipe_enc(out):
    return subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
def parch(dark=0.0,t=0):
    z=1.0+0.03*t/8; im=PARCH.resize((int(W*z),int(H*z))); x=(im.width-W)//2; y=(im.height-H)//2; im=im.crop((x,y,x+W,y+H))
    if dark: im=Image.eval(im,lambda v:int(v*(1-dark)))
    return im.convert('RGBA')
def txt(im,xy,s,f,fill,a=1.0,anchor='mm',shadow=0):
    if a<=0: return
    L_=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(L_)
    if shadow:
        d.text((xy[0]+3,xy[1]+4),s,font=f,fill=(0,0,0,int(160*a)),anchor=anchor); L_=L_.filter(ImageFilter.GaussianBlur(shadow)); d=ImageDraw.Draw(L_)
    d.text(xy,s,font=f,fill=fill[:3]+(int(255*a),),anchor=anchor); im.alpha_composite(L_)
def card(kind,dur,out):
    fr=int(round(dur*FPS)); enc=pipe_enc(out); rnd=random.Random(5)
    dust=[(rnd.uniform(0,W),rnd.uniform(0,H),rnd.uniform(5,25),rnd.uniform(1,2.5)) for _ in range(70)]
    for i in range(fr):
        t=i/FPS
        if kind=='year':
            im=parch(0.55,t); p=eout(t/1.3); v=int(round(10000*p/50)*50) if p<1 else 10000
            jit=(0 if p>=1 else rnd.uniform(-3,3))
            txt(im,(W/2,H*0.44+jit),f'{v:,}',CINZEL(230),(255,236,200),shadow=8)
            txt(im,(W/2,H*0.44+170),'വർഷം മുമ്പ്',SERIFB(70),(240,220,190),a=ease((t-0.25)/0.5),shadow=6)
            lw=int(320*eout((t-0.4)/0.6)); d=ImageDraw.Draw(im); d.rectangle([W/2-lw,H*0.44+235,W/2+lw,H*0.44+240],fill=BLUE)
        elif kind=='nocity':
            im=Image.new('RGBA',(W,H),(8,6,4,255)); pa=parch(0.85,t); im=Image.blend(im,pa,0.35)
            txt(im,(W/2,H*0.44),'ലോകത്ത്',SERIFB(74),(220,205,185),a=ease(t/0.6))
            txt(im,(W/2,H*0.44+120),'ഒരൊറ്റ നഗരം',SERIF(104),(255,245,230),a=ease((t-0.7)/0.6),shadow=6)
            txt(im,(W/2,H*0.44+250),'പോലുമില്ല.',SERIF(104),(255,245,230),a=ease((t-1.2)/0.6),shadow=6)
        elif kind=='timeline':
            im=parch(0.0,t); d=ImageDraw.Draw(im)
            hl=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(hl).rounded_rectangle([170,1365,1000,1520],radius=20,fill=NAVY+(int(200*ease((t-2.7)/0.5)),)); im.alpha_composite(hl); d=ImageDraw.Draw(im)
            txt(im,(W/2,310),'മനുഷ്യചരിത്രത്തിന്റെ',SERIFB(56),INK,a=ease(t/0.5))
            txt(im,(W/2,390),'താളുകൾ',SERIF(96),INK,a=ease((t-0.2)/0.5))
            ev=[('2,600','കീഴടി'),('4,500','പിരമിഡ് · ഹാരപ്പ'),('5,000','സ്റ്റോൺഹെഞ്ച്'),('8,000','ബ്രിട്ടൻ ദ്വീപായി'),('10,000','അട്ടപ്പാടി')]
            x0=230; y0=560; gap=215
            ln=eout((t-0.4)/2.6); d.line([(x0,y0-30),(x0,y0-30+(gap*4+60)*ln)],fill=INK+(255,),width=6)
            for k,(yr,lab) in enumerate(ev):
                tk=(t-0.6-0.55*k)/0.5
                if tk<=0: continue
                y=y0+gap*k; last=k==4
                r=(26 if last else 16)*eout(tk); col=NAVY if last else INK
                d.ellipse([x0-r,y-r,x0+r,y+r],fill=col+(255,),outline=(250,240,220,255),width=4)
                if last:
                    pr=26+60*((t*1.2)%1); d.ellipse([x0-pr,y-pr,x0+pr,y+pr],outline=BLUE+(int(220*(1-(t*1.2)%1)),),width=4)
                txt(im,(x0+60,y-34),yr+' വർഷം മുമ്പ്',ANEK(44,'Bold'),TINT if last else (40,22,8),a=ease(tk),anchor='lm')
                txt(im,(x0+60,y+30),lab,SERIF(76 if last else 50),(255,248,235) if last else (30,15,5),a=ease(tk),anchor='lm',shadow=(6 if last else 0))
                d=ImageDraw.Draw(im)
            ts=(t-3.6)/0.5
            if ts>0:
                s=1.6-0.6*eout(ts); f=SERIF(int(44*s))
                stamp=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(stamp)
                sd.rounded_rectangle([W/2-260*s,1680-50*s,W/2+260*s,1680+50*s],radius=12,outline=(120,20,20,int(255*ease(ts))),width=7)
                sd.text((W/2,1680),'ആദ്യ താൾ',font=f,fill=(120,20,20,int(255*ease(ts))),anchor='mm')
                stamp=stamp.rotate(-6,center=(W/2,1680),resample=Image.BICUBIC); im.alpha_composite(stamp)
        elif kind=='end':
            im=parch(0.45,t)
            l=logo.copy(); l.thumbnail((250,250)); im.alpha_composite(l,(int(W/2-l.width/2),480))
            txt(im,(W/2,820),'NEWS ATTAPPADI',CINZEL(84),(255,240,215),shadow=6)
            txt(im,(W/2,910),'Follow @newsattappadi',ANEK(54,'Bold'),TINT,shadow=4)
            txt(im,(W/2,1000),'ആദിരക്തം — ശിലായുഗം മുതൽ ഇന്നുവരെ',SERIFB(40),(240,225,200))
            cs=sorted({cred.get(s[3],{}).get('credit','') for s in SHOTS if s[2]=='img'}-{''})
            d=ImageDraw.Draw(im); y=1110; f=ANEK(25,'Medium')
            def wrap(t_,f_,mw):
                o,c=[],''
                for w in t_.split(' '):
                    x=(c+' '+w).strip()
                    if d.textlength(x,font=f_)<=mw or not c: c=x
                    else: o.append(c); c=w
                if c:o.append(c)
                return o
            for ln_ in wrap('ചിത്രങ്ങൾ: '+' | '.join(cs),f,W-160)+['പ്രാചീന ജീവിത ദൃശ്യങ്ങൾ: AI ചിത്രീകരണം (Magnific), പഴയ ആർക്കൈവ് ചിത്രങ്ങൾ ആധാരമാക്കി','അവലംബം: Historical Geography of Valluvanad, കാലിക്കറ്റ് സർവകലാശാല (2008)']:
                d.text((W/2,y),ln_,font=f,fill=(225,210,185),anchor='mm'); y+=36
        # dust motes on cards
        dl=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(dl)
        for (x,y,v,r) in dust:
            yy=(y-v*t)%H; dd.ellipse([x-r,yy-r,x+r,yy+r],fill=(255,235,200,90))
        im.alpha_composite(dl)
        enc.stdin.write(im.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait()
def build_bg():
    # ---------------- bg segments ----------------
    segs=[]
    for i,(a,b,kind,src,g,o) in enumerate(SHOTS):
        xf=0 if i==len(SHOTS)-1 else (0.15 if (i in QUICK or i+1 in QUICK) else XF)
        dur=b-a+xf; out=T+f'b{i:02d}.mp4'; fr=int(round(dur*FPS))
        if os.environ.get('REDO') and str(i) not in os.environ['REDO'].split(',') and os.path.exists(out):
            segs.append((out,a,xf)); continue
        if kind=='card':
            if src=='title':
                title3d.render_title(out,dur,A+'adi1_v_peak.mp4',L+'a1_dolmen.jpg','ഭാഗം 1  ·  മണ്ണ് മറന്ന കഥ','ശിലായുഗം മുതൽ ഇന്നുവരെ','/home/claude/na/logo.png')
            elif src=='next':
                title3d.render_title(out,dur,A+'adi1_w_chief.mp4',L+'a1_dolmen.jpg','അടുത്ത ഭാഗം: ജീനുകളിലെ രഹസ്യം','ഉടൻ','/home/claude/na/logo.png',mode='next')
            else: card(src,dur,out)
        elif kind=='vid':
            ss=o.get('ss',0); cd=5.04-ss; sp=min(1.0,cd/dur)
            vf=f"setpts=PTS/{sp:.4f},fps={FPS},crop=iw*0.96:ih*0.96,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{GRADE[g]}"
            subprocess.run(['ffmpeg','-y','-v','error','-ss',str(ss),'-i',A+src,'-vf',vf,'-frames:v',str(fr),'-an','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',out],check=True)
        else:
            z=f"1.0+0.12*on/{fr}" if i%2==0 else f"1.12-0.12*on/{fr}"
            xm="iw/2-(iw/zoom/2)+(iw*0.02)*on/%d"%fr if i%3==0 else "iw/2-(iw/zoom/2)"
            vf=f"scale={int(W*1.3)}:{int(H*1.3)}:force_original_aspect_ratio=increase,crop={int(W*1.3)}:{int(H*1.3)},zoompan=z='{z}':x='{xm}':y='ih/2-(ih/zoom/2)':d={fr}:s={W}x{H}:fps={FPS},{GRADE[g]}"
            subprocess.run(['ffmpeg','-y','-v','error','-loop','1','-i',L+src,'-vf',vf,'-frames:v',str(fr),'-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',out],check=True)
        segs.append((out,a,xf))
        print('seg',i,src,round(dur,2),flush=True)
    # xfade chain
    inp=[]; fc=''; prev='0:v'
    for k,(p,a,xf) in enumerate(segs): inp+=['-i',p]
    for k in range(1,len(segs)):
        off=segs[k][1]; xf=segs[k-1][2]
        tr='fade' if xf<0.3 else 'dissolve'
        fc+=f"[{prev}][{k}:v]xfade=transition={tr}:duration={xf}:offset={off:.3f}[x{k}];"; prev=f'x{k}'
    fc=fc.rstrip(';')
    subprocess.run(['ffmpeg','-y','-v','error']+inp+['-filter_complex',fc,'-map',f'[{prev}]','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',T+'bg.mp4'],check=True)
    print('bg ok',flush=True)

if __name__=='__main__': build_bg()
