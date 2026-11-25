# ആദിരക്തം — cinematic documentary renderer (no news chrome)
import sys, os, json, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; FPS=25; BAR=150
OUT=sys.argv[1]
T='/home/claude/adi1/cine_tmp/'; os.makedirs(T,exist_ok=True)
L='/home/claude/media/assets/library/'; A='/home/claude/media/assets/audio/'
FD='/home/claude/vid/fonts/'
def mj(z): return ImageFont.truetype(FD+'manjari-full-700.ttf',int(z),layout_engine=ImageFont.Layout.RAQM)
def bc(z): return ImageFont.truetype(FD+'barlow-condensed-latin-700-normal.ttf',int(z))
logo=Image.open('/home/claude/na/logo.png').convert('RGBA'); logo=logo.crop(logo.getbbox())
cred=json.load(open(L+'credits.json')); cred.update(json.load(open('/home/claude/adi1/newcred.json')))
AI='AI ചിത്രീകരണം'
# (start, end, kind, src, opts)  kind: vid|img|card ; opts: grade, ss (clip start), sub, subt (sub start rel), tag
S0,S1,S2,S3,S4,S5,S6,S7=0,17.34,32.96,39.9,54.68,93.66,100.92,113.86
TV=119.24
SEG=[
 (0,6.0,'vid','adi1_v_peak.mp4',dict(g='film',sub='ആദിവാസി.',sub2=('ഈ ഒറ്റ വാക്ക് കേൾക്കുമ്പോൾ, പലരുടെയും ചുണ്ടിൽ ഒരു പുച്ഛച്ചിരി വിടരും.',1.8),tag=AI)),
 (6.0,10.4,'img','malleswaran_mudi_2.jpg',dict(g='film',sub=('പക്ഷേ, ആ ചിരി മായും.',1.5),tag='മല്ലീശ്വരൻ മുടി, അട്ടപ്പാടി')),
 (10.4,S1,'vid','adi1_v_valley.mp4',dict(g='film',sub='അട്ടപ്പാടിയുടെ മണ്ണ് പതിനായിരം വർഷമായി ഒളിപ്പിച്ചുവച്ച ആ രഹസ്യം…',tag=AI)),
 (S1,S1+2.9,'vid','adi1_v_knap.mp4',dict(g='film',sub='ശിലായുഗം മുതൽ ഇന്നുവരെ.',tag=AI)),
 (S1+2.9,S1+5.2,'vid','adi1_v_family.mp4',dict(g='film',sub='ഇന്ത്യയുടെ ആദ്യത്തെ രക്തം.',tag=AI)),
 (S1+5.2,S1+7.8,'img','monsoon_clouds.jpg',dict(g='film',sub='കടൽ കടന്ന് നീളുന്ന വേരുകൾ.',tag='പശ്ചിമഘട്ടം')),
 (S1+7.8,S1+10.8,'img','a1_dolmen.jpg',dict(g='film',sub='നഗരങ്ങൾക്ക് പേര് നൽകിയ തലവന്മാർ.',tag='മുനിയറ, മറയൂർ — പ്രതീകാത്മക ചിത്രം')),
 (S1+10.8,S2,'img','muduga_women.jpg',dict(g='warm',sub='നാം പുച്ഛിച്ചുതള്ളിയ ഒരു ജനതയുടെ, ആരും പറയാത്ത ചരിത്രം.',tag='അട്ടപ്പാടി')),
 (S2,S3,'card','title',{}),
 (S3,S3+6.4,'vid','adi1_v_dig.mp4',dict(g='film',sub='മുക്കാലിയുടെ മണ്ണിനടിയിൽ, പ്രാചീന ശിലായുഗത്തിന്റെ കാൽപ്പാടുകൾ.',tag=AI,place='മുക്കാലി')),
 (S3+6.4,S3+11.4,'img','a1_attirampakkam.jpg',dict(g='film',sub='അഗളിയിലും ചേരക്കൽപ്പാടിയിലും, മധ്യശിലായുഗ മനുഷ്യൻ ഉപേക്ഷിച്ചുപോയ കല്ലായുധങ്ങൾ.',tag='ശിലായുധങ്ങൾ — പ്രതീകാത്മക ചിത്രം',place='അഗളി · ചേരക്കൽപ്പാടി')),
 (S3+11.4,S4,'img','a_river_1.jpg',dict(g='dusk',sub='കാലം മായ്ക്കാൻ മറന്നുപോയ തെളിവുകൾ.',tag='അട്ടപ്പാടി')),
 (S4,S4+1.6,'card','year',{}),
 (S4+1.6,S4+4.3,'img','a1_pyramid2.jpg',dict(g='bw',sub='അന്ന് ഈജിപ്തിൽ പിരമിഡുകൾ ഇല്ല.',tag='ഗിസ, ഈജിപ്ത്')),
 (S4+4.3,S4+7.9,'img','a1_pyramid.jpg',dict(g='bw',sub='അവ ഉയരാൻ ഇനിയും അയ്യായിരം വർഷം കാത്തിരിക്കണം.',tag='ഗിസ, ഈജിപ്ത്')),
 (S4+7.9,S4+9.9,'img','a1_stonehenge.jpg',dict(g='bw',sub='ഇംഗ്ലണ്ടിൽ സ്റ്റോൺഹെഞ്ച് ഇല്ല.',tag='സ്റ്റോൺഹെഞ്ച്, ഇംഗ്ലണ്ട്')),
 (S4+9.9,S4+15.2,'img','a1_stonehenge2.jpg',dict(g='bw',sub='ബ്രിട്ടൻ ഒരു ദ്വീപ് പോലും ആയിട്ടില്ല; യൂറോപ്പുമായി കര ചേർന്നുകിടക്കുന്നു.',tag='ബ്രിട്ടൻ')),
 (S4+15.2,S4+16.6,'img','a1_harappa1.jpg',dict(g='bw',sub='ഹാരപ്പയില്ല.',tag='ഹാരപ്പ')),
 (S4+16.6,S4+18.1,'img','a1_mohenjo.jpg',dict(g='bw',sub='മോഹൻജൊദാരോയില്ല.',tag='മോഹൻജൊദാരോ')),
 (S4+18.1,S4+19.75,'img','a1_keeladi03.jpg',dict(g='bw',sub='കീഴടിയില്ല.',tag='കീഴടി, തമിഴ്നാട്')),
 (S4+19.75,S4+22.95,'card','nocity',{}),
 (S4+22.95,S4+29.1,'vid','adi1_v_family.mp4',dict(g='film',ss=0,sub='അപ്പോഴും, ഈ മലഞ്ചെരിവുകളിൽ മനുഷ്യൻ ഉണ്ടായിരുന്നു.',sub2=('അവൻ കല്ലുരച്ച് തീ കൊളുത്തി.',4.3),tag=AI)),
 (S4+29.1,S4+31.9,'vid','adi1_v_knap.mp4',dict(g='film',ss=2.2,sub='കല്ലുരുട്ടി ആയുധം തീർത്തു.',tag=AI)),
 (S4+31.9,S5,'vid','adi1_v_hunters.mp4',dict(g='film',sub='കാടിനോട് പൊരുതി ജീവിച്ചു.',sub2=('ലോകം ചരിത്രം എഴുതിത്തുടങ്ങും മുമ്പേ, അട്ടപ്പാടി ജീവിച്ചുതുടങ്ങിയിരുന്നു.',1.9),tag=AI)),
 (S5,S6,'img','sv_tower_view.jpg',dict(g='color',sub='അട്ടപ്പാടി ഒരു മലയോര ഗ്രാമമല്ല.',sub2=('മനുഷ്യചരിത്രത്തിന്റെ ആദ്യ താളുകളിൽ ഒന്നാണ്.',3.3),tag='അട്ടപ്പാടി')),
 (S6,S6+6.0,'vid','adi1_v_river.mp4',dict(g='film',sub='അവർ ആരായിരുന്നു?',sub2=('ഇന്ന് ഈ മലകളിൽ ജീവിക്കുന്നവർ, അവരുടെ പിൻമുറക്കാരോ?',2.0),tag=AI)),
 (S6+6.0,S7,'vid','adi1_v_elder.mp4',dict(g='film',sub='ഉത്തരം കല്ലിലല്ല.',sub2=('ഇന്നും തുടിക്കുന്ന ഒരു രക്തത്തിലാണ്.',2.8),tag=AI)),
 (S7,TV,'card','next',{}),
 (TV,TV+6,'card','end',{}),
]
def shadow_text(im,xy,txt,f,fill=(255,255,255),anchor='mm',blur=6):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).text(xy,txt,font=f,fill=(0,0,0,230),anchor=anchor)
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); im.alpha_composite(sh); im.alpha_composite(sh)
    ImageDraw.Draw(im).text(xy,txt,font=f,fill=fill,anchor=anchor)
def wrap(d,t,f,mw):
    o,c=[],''
    for w in t.split(' '):
        x=(c+' '+w).strip()
        if d.textlength(x,font=f)<=mw or not c: c=x
        else: o.append(c); c=w
    if c:o.append(c)
    return o
def frame_png(path,tag=None,credit=None,place=None):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,BAR],fill=(0,0,0,255)); d.rectangle([0,H-BAR,W,H],fill=(0,0,0,255))
    l=logo.copy(); l.thumbnail((96,96)); a=l.split()[3].point(lambda v:int(v*0.8)); l.putalpha(a); im.alpha_composite(l,(36,(BAR-l.height)//2+8))
    d.text((W-40,BAR/2+10),'ആദിരക്തം · ഭാഗം 1',font=mj(30),fill=(200,200,200),anchor='rm')
    y=H-BAR+40
    if tag: d.text((W-40,y),tag,font=mj(26),fill=(190,190,190),anchor='rm')
    if credit: d.text((W-40,y+40),credit,font=mj(20),fill=(140,140,140),anchor='rm')
    if place:
        f=mj(40); shadow_text(im,(60,BAR+70),place,f,fill=(255,255,255),anchor='lm',blur=4)
        d=ImageDraw.Draw(im); tw=d.textlength(place,font=f); d.rectangle([60,BAR+100,60+min(tw,200),BAR+104],fill=(124,200,255,255))
    im.save(path)
def sub_png(path,txt):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); f=mj(56)
    lines=wrap(d,txt,f,W-140); y=H-BAR-60-(len(lines)-1)*76
    for ln in lines: shadow_text(im,(W/2,y),ln,f); y+=76
    im.save(path)
def grade_vf(g):
    if g=='bw': return "hue=s=0,eq=contrast=1.25:brightness=-0.03,curves=preset=darker"
    if g=='film': return "eq=saturation=0.78:contrast=1.08,colorbalance=rs=0.04:bs=-0.03:rh=0.03:bh=-0.04"
    if g=='warm': return "eq=saturation=0.85:contrast=1.05,colorbalance=rm=0.04:bm=-0.03"
    if g=='dusk': return "eq=saturation=0.45:brightness=-0.12:contrast=1.1,colorbalance=bs=0.06"
    return "eq=saturation=1.0"
FIN="noise=alls=9:allf=t,vignette=PI/4.5"
def card_png(kind):
    im=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(im)
    return im,d
segs=[]
for i,(a,b,kind,src,o) in enumerate(SEG):
    dur=b-a; fr=int(round(dur*FPS)); out=T+f's{i:02d}.mp4'
    if kind in('vid','img'):
        c=cred.get(src,{}).get('credit','') if kind=='img' else ''
        fp=T+f'f{i:02d}.png'; frame_png(fp,o.get('tag'),('ചിത്രം: '+c) if c else None,o.get('place'))
        subs=[]
        s1=o.get('sub')
        if s1: subs.append((s1,0.15) if isinstance(s1,str) else s1)
        if o.get('sub2'): subs.append(o['sub2'])
        inputs=[];
        if kind=='vid':
            ss=o.get('ss',0); clip=A+src; cd=5.04-ss; sp=min(1.0,cd/dur)
            inputs=['-ss',str(ss),'-i',clip]
            base=f"[0:v]setpts=PTS/{sp:.4f},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{grade_vf(o['g'])},{FIN},trim=0:{dur:.3f},setpts=PTS-STARTPTS[bg]"
        else:
            inputs=['-loop','1','-i',L+src]
            zi=i%2
            z=f"1.0+0.10*on/{fr}" if zi==0 else f"1.10-0.10*on/{fr}"
            base=f"[0:v]scale={int(W*1.25)}:{int(H*1.25)}:force_original_aspect_ratio=increase,crop={int(W*1.25)}:{int(H*1.25)},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s={W}x{H}:fps={FPS},{grade_vf(o['g'])},{FIN}[bg]"
        inputs+=['-loop','1','-i',fp]
        fc=base+";[bg][1:v]overlay=0:0[v0]"
        last='v0'
        # subtitle timing: each sub shows from its start to next sub start (or end)
        for k,(txt,st) in enumerate(subs):
            en=subs[k+1][1] if k+1<len(subs) else dur
            sp_=T+f'sub{i:02d}_{k}.png'; sub_png(sp_,txt); inputs+=['-loop','1','-i',sp_]
            idx=2+k
            fc+=f";[{idx}:v]format=rgba,fade=t=in:st={st:.2f}:d=0.35:alpha=1,fade=t=out:st={max(st,en-0.3):.2f}:d=0.3:alpha=1[t{k}];[{last}][t{k}]overlay=0:0[v{k+1}]"
            last=f'v{k+1}'
        fc+=f";[{last}]format=yuv420p,fade=t=in:d=0.25,fade=t=out:st={dur-0.25:.2f}:d=0.25[out]"
        subprocess.run(['ffmpeg','-y','-v','error']+inputs+['-filter_complex',fc,'-map','[out]','-frames:v',str(fr),'-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','19',out],check=True)
    else:
        # text cards on black, frame by frame
        def F(t):
            im=Image.new('RGBA',(W,H),(0,0,0,255));
            def put(txt,y,f,col,t0,t1=99):
                a=max(0,min(1,(t-t0)/0.6))*max(0,min(1,(t1-t)/0.4))
                if a<=0: return
                L_=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(L_).text((W/2,y),txt,font=f,fill=col+(int(255*a),),anchor='mm'); im.alpha_composite(L_)
            if src=='title':
                l=logo.copy(); l.thumbnail((170,170)); a=max(0,min(1,t/0.6)); l.putalpha(l.split()[3].point(lambda v:int(v*a))); im.alpha_composite(l,(int(W/2-l.width/2),560))
                put('ന്യൂസ് അട്ടപ്പാടി അവതരിപ്പിക്കുന്നു',800,mj(46),(170,170,170),0.2)
                s=1.0+0.04*t
                put('ആദിരക്തം',960,mj(int(190*s)),(255,255,255),2.5)
                put('ഭാഗം 1  ·  മണ്ണ് മറന്ന കഥ',1130,mj(60),(124,200,255),3.9)
                put('ശിലായുഗം മുതൽ ഇന്നുവരെ',1220,mj(40),(170,170,170),4.3)
            elif src=='year':
                v=int(10000*min(1,(t/1.2)**0.6)); put(f'{v:,}',900,bc(220),(255,255,255),0)
                put('വർഷം മുമ്പ്',1060,mj(64),(200,200,200),0.3)
            elif src=='nocity':
                put('ലോകത്ത്',860,mj(70),(220,220,220),0.0)
                put('ഒരൊറ്റ നഗരം പോലുമില്ല.',960,mj(70),(255,255,255),1.0)
            elif src=='next':
                put('ആദിരക്തം',820,mj(150),(255,255,255),0.0)
                put('അടുത്ത ഭാഗം',990,mj(48),(170,170,170),1.4)
                put('ജീനുകളിലെ രഹസ്യം',1090,mj(78),(124,200,255),2.0)
                put('ഉടൻ',1200,mj(44),(200,200,200),2.6)
            elif src=='end':
                l=logo.copy(); l.thumbnail((240,240)); im.alpha_composite(l,(int(W/2-l.width/2),560))
                put('NEWS ATTAPPADI',880,bc(100),(255,255,255),0)
                put('Follow @newsattappadi',980,bc(56),(124,200,255),0.2)
                cs=sorted({cred.get(x[3],{}).get('credit','') for x in SEG if x[2]=='img'}-{''})
                dd=ImageDraw.Draw(im); y=1110; f=mj(24)
                for ln in wrap(dd,'ചിത്രങ്ങൾ: '+' | '.join(cs),f,W-140)+['AI ചിത്രീകരണങ്ങളും ദൃശ്യങ്ങളും: Magnific','അവലംബം: Historical Geography of Valluvanad, കാലിക്കറ്റ് സർവകലാശാല (2008)']:
                    dd.text((W/2,y),ln,font=f,fill=(150,150,150),anchor='mm'); y+=34
            return im.convert('RGB')
        p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-vf',f'{FIN},format=yuv420p','-frames:v',str(fr),'-c:v','libx264','-preset','veryfast','-crf','19',out],stdin=subprocess.PIPE)
        for k in range(fr): p.stdin.write(F(k/FPS).tobytes())
        p.stdin.close(); p.wait()
    segs.append(out)
open(T+'list.txt','w').write(''.join(f"file '{x}'\n" for x in segs))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',T+'list.txt','-c','copy',T+'video.mp4'],check=True)
print('video ok')

sys.path.insert(0,'/home/claude/adi1'); from shots import S, SFX
AUD=A; GAP=0.3
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# audio: VO sections each followed by GAP silence, scored music bed, sound effects
parts=[AUD+f'{sec}.wav' for sec,_,_ in S]
st={}; t0=0.0
for sec,_,_ in S: st[sec]=t0; t0+=dur(AUD+f'{sec}.wav')+GAP
inp=[]; fc=''
for i,p in enumerate(parts): inp+=['-i',p]; fc+=f'[{i}:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur={GAP}[a{i}];'
fc+=''.join(f'[a{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=0:a=1[vo]'
subprocess.run(['ffmpeg','-y','-v','error']+inp+['-filter_complex',fc,'-map','[vo]',T+'vo.wav'],check=True)
tv=dur(T+'video.mp4'); vd=dur(T+'vo.wav')
A0,A1,A2,A3,A4,A5,A6,A7=[st[f'adi1_a{i}'] for i in range(8)]
HUSH0,HUSH1=A4+19.75,A4+22.95
# (video start, video end, music start, lowpass Hz or 0)
P=[(0,A3,0,0),(A3,A4,38,2200),(A4,HUSH0,52.8,0),(HUSH1,A6,41,0),(A6,A7,70.2,900),(A7,tv,70.2+(A7-A6),0)]
MUS=AUD+'adi1_music.mp3'
# volume envelope over absolute time
env=[(0,A0+7.4,0.24),(A0+7.4,A0+8.6,0.03),(A0+8.6,A1,0.2),(A1,A2,0.2),(A2,A2+2.6,0.6),(A2+2.6,A3,0.32),(A3,A4,0.2),
     (A4,HUSH0,0.15),(HUSH0,HUSH1,0.0),(HUSH1,HUSH1+2.2,0.55),(HUSH1+2.2,A5,0.17),(A5,A6,0.22),(A6,A7,0.32),(A7,tv,0.45)]
ex='0'
for a,b,v in reversed(env): ex=f'if(between(t,{a:.2f},{b:.2f}),{v},{ex})'
inp=['-i',T+'vo.wav']; fc='[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.6[v];'; mix=['[v]']
k=1
for a,b,m,lp in P:
    L_=b-a+0.3
    inp+=['-i',MUS]; f=f'[{k}:a]atrim={m}:{m+L_},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,'
    if lp: f+=f'lowpass=f={lp},'
    f+=f'afade=t=in:d=0.3,afade=t=out:st={L_-0.35:.2f}:d=0.35,adelay={int(a*1000)}|{int(a*1000)}[p{k}];'
    fc+=f; k+=1
fc+=''.join(f'[p{i}]' for i in range(1,k))+f"amix=inputs={k-1}:normalize=0,volume='{ex}':eval=frame,afade=t=out:st={tv-2.5:.2f}:d=2.5[m];"
mix.append('[m]')
for sec,off,f,vol in SFX:
    a=st[sec]+off; inp+=['-i',AUD+f]
    fc+=f'[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={int(a*1000)}|{int(a*1000)}[s{k}];'; mix.append(f'[s{k}]'); k+=1
fc+=''.join(mix)+f'amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{tv},alimiter=limit=0.95[a]'
subprocess.run(['ffmpeg','-y','-v','error']+inp+['-i',T+'video.mp4','-filter_complex',fc,'-map',f'{k}:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(tv),OUT],check=True)
print('done',OUT,tv,vd,{k:round(v,2) for k,v in st.items()})
