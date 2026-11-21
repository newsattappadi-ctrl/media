# News Attappadi - Kumar clips 2026-11-21 (Agali mobile medical units + minister's remarks)
# Usage (in ~/mm with clips c1..c8, VO a*.wav b*.wav, music.mp3, logo.jpg, fonts/):
#   python3 render.py A out_A.mp4   |   python3 render.py B out_B.mp4
import sys, os, subprocess, json
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 25
NAVY, BLUE, GREY, WHITE, TINT = (6,54,74), (10,122,191), (77,77,77), (255,255,255), (124,200,255)
FD = 'fonts/'
def mj(z): return ImageFont.truetype(FD+'Manjari-Bold.ttf', int(z), layout_engine=ImageFont.Layout.RAQM)
def bc(z): return ImageFont.truetype(FD+'BarlowCondensed-Bold.ttf', int(z))
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
def wrap(d, t, f, mw):
    o, c = [], ''
    for w in t.split(' '):
        x = (c+' '+w).strip()
        if d.textlength(x, font=f) <= mw or not c: c = x
        else: o.append(c); c = w
    if c: o.append(c)
    return o

logo = Image.open('logo.jpg').convert('RGBA')
CREDIT = 'ദൃശ്യങ്ങൾ: കുമാർ അട്ടപ്പാടി'
STRAP_H = 112; STRAP_Y = 1460
VID_Y, VID_H = 470, 760   # foreground video band

def base(headline, label='അഗളി'):
    im = Image.new('RGBA', (W, H), (0,0,0,0)); d = ImageDraw.Draw(im)
    for y in range(260): d.line([(0,y),(W,y)], fill=(0,0,0,int(150*(1-y/260))))
    l = logo.copy(); l.thumbnail((170,170), Image.LANCZOS); im.alpha_composite(l, (40, 70))
    d.text((W-40, 84), '@newsattappadi', font=bc(46), fill=WHITE, anchor='ra')
    d.text((W-40, 146), CREDIT, font=mj(30), fill=TINT, anchor='ra', stroke_width=2, stroke_fill=(0,0,0))
    # TV strap: blue label + white headline bar (2 lines allowed)
    lf = mj(42); lw = int(d.textlength(label, font=lf)+56)
    hf = mj(44); lines = wrap(d, headline, hf, W-lw-50)
    if len(lines) > 2:
        hf = mj(38); lines = wrap(d, headline, hf, W-lw-50)
    bh = max(STRAP_H, 58*len(lines)+30)
    d.rectangle([0, STRAP_Y, lw, STRAP_Y+bh], fill=BLUE)
    d.text((lw/2, STRAP_Y+bh/2+4), label, font=lf, fill=WHITE, anchor='mm')
    d.rectangle([lw, STRAP_Y, W, STRAP_Y+bh], fill=WHITE)
    d.rectangle([0, STRAP_Y+bh, W, STRAP_Y+bh+12], fill=NAVY)
    y = STRAP_Y + bh/2 - (len(lines)-1)*29
    for ln in lines:
        d.text((lw+24, y+4), ln, font=hf, fill=NAVY, anchor='lm'); y += 58
    return im

def caption(im, text):
    d = ImageDraw.Draw(im); f = mj(58); lines = wrap(d, text, f, W-160); lh = int(f.size*1.32)
    bh = lh*len(lines)+34; by = VID_Y+VID_H+20; bw = max(d.textlength(x, font=f) for x in lines)+80
    d.rectangle([40, by, 40+bw, by+bh], fill=NAVY+(240,)); d.rectangle([40, by, 52, by+bh], fill=BLUE)
    y = by+20
    for ln in lines: d.text((84, y), ln, font=f, fill=WHITE); y += lh
    return im

def lower_third(im, name, role):
    d = ImageDraw.Draw(im); by = VID_Y+VID_H+20
    nf, rf = mj(60), mj(36)
    nw = d.textlength(name, font=nf)+80; rw = d.textlength(role, font=rf)+80
    d.rectangle([40, by, 40+nw, by+88], fill=BLUE); d.text((80, by+46), name, font=nf, fill=WHITE, anchor='lm')
    d.rectangle([40, by+88, 40+max(nw, rw), by+150], fill=WHITE); d.text((80, by+121), role, font=rf, fill=NAVY, anchor='lm')
    return im

def opener(im, kicker, lines):
    d = ImageDraw.Draw(im); top = 300
    kf = mj(50); kw = d.textlength(kicker, font=kf)+60
    d.rectangle([40, top, 40+kw, top+80], fill=BLUE); d.text((70, top+42), kicker, font=kf, fill=WHITE, anchor='lm')
    f = mj(84); y = top+100
    for ln in lines:
        lw_ = d.textlength(ln, font=f)+60
        d.rectangle([40, y, 40+lw_, y+118], fill=NAVY+(235,)); d.text((70, y+62), ln, font=f, fill=WHITE if ln != lines[-1] else TINT, anchor='lm'); y += 128
    return im

def endcard(path):
    im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
    for i in range(0, W+H, 70): d.line([(i,0),(i-H,H)], fill=(10,64,88), width=3)
    l = logo.copy(); l.thumbnail((420,420), Image.LANCZOS); im.paste(l.convert('RGB'), (int(W/2-l.width/2), 560))
    d.text((W/2, 1070), 'NEWS ATTAPPADI', font=bc(110), fill=WHITE, anchor='mm')
    d.text((W/2, 1180), 'വാർത്തകൾ വിശദമായി', font=mj(64), fill=TINT, anchor='mm')
    d.rectangle([W/2-260, 1260, W/2+260, 1268], fill=BLUE)
    d.text((W/2, 1340), 'Follow @newsattappadi', font=bc(70), fill=WHITE, anchor='mm')
    im.save(path)

# ---------------- stories ----------------
NAME, ROLE = 'കെ.എ. തുളസി', 'പട്ടികജാതി-പട്ടികവർഗ വികസന വകുപ്പ് മന്ത്രി'
STORIES = {
 'A': dict(
   headline='അട്ടപ്പാടിയിൽ മൊബൈൽ മെഡിക്കൽ യൂണിറ്റുകൾ, മന്ത്രി ഫ്ലാഗ് ഓഫ് ചെയ്തു',
   opener=('പ്രധാന വാർത്ത', ['മൊബൈൽ മെഡിക്കൽ', 'യൂണിറ്റുകൾ', 'വീണ്ടും നിരത്തിൽ']),
   segs=[
     dict(vo='a0.wav', lead=0.8, open=True, vis=[('c2.mp4', 0.0)]),
     dict(vo='a1.wav', cap='മന്ത്രി കെ.എ. തുളസി ഫ്ലാഗ് ഓഫ് ചെയ്തു', vis=[('c4.mp4', 0.0), ('c6.mp4', 0.0)]),
     dict(vo='a2.wav', cap='3 വർഷമായി നിർത്തിവെച്ച സേവനം വീണ്ടും', vis=[('c5.mp4', 0.0), ('c8.mp4', 0.0), ('c7.mp4', 0.0)]),
     dict(vo='a3.wav', cap='അടച്ചിട്ട കമ്മ്യൂണിറ്റി കിച്ചണുകൾ തുറക്കും', vis=[('c1.mp4', 0.0), ('c3.mp4', 160.0)]),
   ]),
 'B': dict(
   headline='ശിശുമരണം രാഷ്ട്രീയ ആയുധമാക്കരുത്, പിണറായിക്കെതിരെ മന്ത്രി',
   opener=('പ്രധാന വാർത്ത', ['ശിശുമരണം', 'രാഷ്ട്രീയ', 'ആയുധമാക്കരുത്']),
   segs=[
     dict(vo='b0.wav', lead=0.8, open=True, vis=[('c3.mp4', 28.0)]),
     dict(vo='b1.wav', cap='"കുട്ടികളുടെ മരണം രാഷ്ട്രീയ നേട്ടത്തിന് ഉപയോഗിക്കരുത്"', vis=[('c6.mp4', 0.5), ('c1.mp4', 0.5)]),
     dict(bite=(11.15, 25.35)),
     dict(vo='b2.wav', cap='"തിരിഞ്ഞുനോക്കിയില്ല" വിമർശനത്തിന് മറുപടി', vis=[('c4.mp4', 4.0)]),
     dict(bite=(52.7, 69.15)),
     dict(vo='b3.wav', cap='"10 വർഷം വന്നത് കെട്ടിട ഉദ്ഘാടനത്തിന് മാത്രം"', vis=[('c2.mp4', 2.0), ('c3.mp4', 120.0)]),
     dict(bite=(77.4, 86.75)),
     dict(vo='b4.wav', cap='"ശിശുമരണം ആഴത്തിൽ പഠിക്കേണ്ട വിഷയം"', vis=[('c3.mp4', 140.0), ('c7.mp4', 1.0)]),
   ]),
}

def vchain(inp, ss, d, label):
    # blurred fill background + zoomed 16:9 band in the middle
    return (f"[{inp}:v]trim=start={ss}:duration={d},setpts=PTS-STARTPTS,fps={FPS},split[{label}a][{label}b];"
            f"[{label}a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,eq=brightness=-0.18[{label}bg];"
            f"[{label}b]scale=-2:{VID_H},crop={W}:{VID_H}[{label}fg];"
            f"[{label}bg][{label}fg]overlay=0:{VID_Y}[{label}]")

def render_seg(i, seg, st, tmp):
    out = f'{tmp}/seg{i:02d}.mp4'; png = f'{tmp}/ov{i:02d}.png'
    im = base(st['headline'])
    if 'bite' in seg:
        s0, s1 = seg['bite']; d = s1-s0
        lower_third(im, NAME, ROLE); im.save(png)
        fc = vchain(0, s0, d, 'v') + f";[v][1:v]overlay=0:0[o];[0:a]atrim=start={s0}:duration={d},asetpts=PTS-STARTPTS,afade=t=in:d=0.15,afade=t=out:st={d-0.2}:d=0.2,loudnorm=I=-16:TP=-1.5,aresample=48000[a]"
        cmd = ['ffmpeg','-v','error','-y','-i','c3.mp4','-loop','1','-i',png,'-filter_complex',fc,'-map','[o]','-map','[a]','-t',str(d)]
    else:
        lead = seg.get('lead', 0.0); vd = dur(seg['vo']); d = lead+vd+0.35
        if seg.get('open'): opener(im, *st['opener'])
        if seg.get('cap'): caption(im, seg['cap'])
        im.save(png)
        n = len(seg['vis']); part = d/n; fc = []; ins = []
        for k, (clip, ss) in enumerate(seg['vis']):
            ins += ['-i', clip]; fc.append(vchain(k, ss, part+0.05, f'p{k}'))
        cat = ''.join(f'[p{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[v]'
        fc.append(cat)
        fc.append(f'[v][{n}:v]overlay=0:0[o]')
        fc.append(f"[{n+1}:a]adelay={int(lead*1000)}|{int(lead*1000)},apad,atrim=duration={d},loudnorm=I=-16:TP=-1.5,aresample=48000[a]")
        cmd = ['ffmpeg','-v','error','-y'] + ins + ['-loop','1','-i',png,'-i',seg['vo'],'-filter_complex',';'.join(fc),'-map','[o]','-map','[a]','-t',str(d)]
    cmd += ['-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-ar','48000','-ac','2',out]
    subprocess.run(cmd, check=True)
    return out, dur(out), ('bite' if 'bite' in seg else 'vo')

def main(key, OUT):
    st = STORIES[key]; tmp = f'tmp_{key}'; os.makedirs(tmp, exist_ok=True)
    parts = [render_seg(i, s, st, tmp) for i, s in enumerate(st['segs'])]
    endcard(f'{tmp}/end.png')
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',f'{tmp}/end.png','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','3','-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-ar','48000','-ac','2',f'{tmp}/end.mp4'], check=True)
    parts.append((f'{tmp}/end.mp4', 3.0, 'end'))
    with open(f'{tmp}/list.txt', 'w') as f:
        for p, _, _ in parts: f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{tmp}/list.txt','-c','copy',f'{tmp}/joined.mp4'], check=True)
    # music bed: loud on opener lead, 0.11 under VO, 0.03 under bites, 0.35 on end card, fade out
    t = 0.0; terms = []
    for i, (_, d, kind) in enumerate(parts):
        if kind == 'bite': v = 0.03
        elif kind == 'end': v = 0.35
        else: v = 0.11
        terms.append(f"between(t,{t:.3f},{t+d:.3f})*{v}"); t += d
    total = t
    vol = '+'.join(terms) + f"+lt(t,0.8)*0.4"
    fc = (f"[1:a]atrim=duration={total},volume='{vol}':eval=frame,afade=t=out:st={total-1.5}:d=1.5[m];"
          f"[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'{tmp}/joined.mp4','-stream_loop','-1','-i','music.mp3','-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT], check=True)
    print(OUT, round(total, 2))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
