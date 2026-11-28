# News Attappadi - Kumar 2026-11-26 (Kallamala excise liquor seizure C)
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

def round_logo():
    # drop the square white background (flood fill from corners), then sit the badge on a white disc like earlier reels
    from PIL import ImageDraw as _D
    src = Image.open('logo.jpg').convert('RGB'); w, h = src.size
    key = src.copy()
    for c in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]: _D.floodfill(key, c, (255,0,255), thresh=40)
    px = key.load(); m = Image.new('L', (w, h), 255); mp = m.load()
    for y in range(h):
        for x in range(w):
            if px[x,y] == (255,0,255): mp[x,y] = 0
    badge = src.convert('RGBA'); badge.putalpha(m)
    cx, cy, r = 662, 652, 566
    out = Image.new('RGBA', (w, h), (0,0,0,0)); _D.Draw(out).ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255,255,255,255))
    out.alpha_composite(badge)
    return out.crop(out.getbbox())
logo = round_logo()
CREDIT = 'ദൃശ്യങ്ങൾ: കുമാർ അട്ടപ്പാടി'
PLACE = 'അട്ടപ്പാടി'
STRAP_H = 96; STRAP_Y = 1580
VID_Y, VID_H = 330, 760   # foreground video band

def base(headline, label='പ്രധാന വാർത്ത'):
    im = Image.new('RGBA', (W, H), (0,0,0,0)); d = ImageDraw.Draw(im)
    for y in range(260): d.line([(0,y),(W,y)], fill=(0,0,0,int(130*(1-y/260))))
    l = logo.copy(); l.thumbnail((150,150), Image.LANCZOS); im.alpha_composite(l, (36, 90))
    d.text((W-36, 100), '@newsattappadi', font=bc(38), fill=WHITE, anchor='ra')
    d.text((W-36, 150), PLACE, font=mj(30), fill=TINT, anchor='ra', stroke_width=2, stroke_fill=(0,0,0))
    lf = mj(40); lw = int(d.textlength(label, font=lf)+56)
    size = 52; hf = mj(size)
    while d.textlength(headline, font=hf) > W-lw-50 and size > 30: size -= 2; hf = mj(size)
    d.rectangle([0, STRAP_Y, lw, STRAP_Y+STRAP_H], fill=BLUE)
    d.text((lw/2, STRAP_Y+STRAP_H/2+4), label, font=lf, fill=WHITE, anchor='mm')
    d.rectangle([lw, STRAP_Y, W, STRAP_Y+STRAP_H], fill=WHITE)
    d.rectangle([0, STRAP_Y+STRAP_H, W, STRAP_Y+STRAP_H+10], fill=NAVY)
    d.text((lw+26, STRAP_Y+STRAP_H/2+4), headline, font=hf, fill=NAVY, anchor='lm')
    d.text((W-36, STRAP_Y+STRAP_H+18), CREDIT, font=mj(26), fill=WHITE, anchor='ra', stroke_width=2, stroke_fill=(0,0,0))
    return im

def caption(im, text):
    d = ImageDraw.Draw(im); f = mj(58); lines = wrap(d, text, f, W-160); lh = int(f.size*1.32)
    bh = lh*len(lines)+34; by = STRAP_Y-bh-22; bw = max(d.textlength(x, font=f) for x in lines)+80
    d.rectangle([40, by, 40+bw, by+bh], fill=NAVY+(240,)); d.rectangle([40, by, 52, by+bh], fill=BLUE)
    y = by+20
    for ln in lines: d.text((84, y), ln, font=f, fill=WHITE); y += lh
    return im

def lower_third(im, name, role):
    d = ImageDraw.Draw(im); by = STRAP_Y-150-22
    nf, rf = mj(58), mj(38)
    nw = d.textlength(name, font=nf)+80; rw = d.textlength(role, font=rf)+80
    d.rectangle([40, by, 40+nw, by+88], fill=BLUE); d.text((80, by+46), name, font=nf, fill=WHITE, anchor='lm')
    d.rectangle([40, by+88, 40+max(nw, rw), by+150], fill=WHITE); d.text((80, by+121), role, font=rf, fill=NAVY, anchor='lm')
    return im

def opener(im, kicker, lines):
    d = ImageDraw.Draw(im); size = 76; f = mj(size)
    while max(d.textlength(x, font=f) for x in lines) > W-150 and size > 40: size -= 2; f = mj(size)
    lh = int(size*1.37)
    top = STRAP_Y - 22 - len(lines)*lh - 70
    kf = mj(42); kw = d.textlength(kicker, font=kf)+56
    d.rectangle([36, top, 36+kw, top+66], fill=BLUE); d.text((64, top+35), kicker, font=kf, fill=WHITE, anchor='lm')
    y = top+70
    bw = max(d.textlength(x, font=f) for x in lines)+70
    d.rectangle([36, y, 36+bw, y+lh*len(lines)+10], fill=NAVY+(240,)); d.rectangle([36, y, 48, y+lh*len(lines)+10], fill=BLUE)
    for i, ln in enumerate(lines):
        d.text((76, y+8+i*lh+lh/2), ln, font=f, fill=TINT if i == len(lines)-1 else WHITE, anchor='lm')
    return im

def endcard(path):
    im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
    for i in range(0, W+H, 70): d.line([(i,0),(i-H,H)], fill=(10,64,88), width=3)
    l = logo.copy(); l.thumbnail((420,420), Image.LANCZOS); im.paste(l, (int(W/2-l.width/2), 560), l)
    d.text((W/2, 1070), 'NEWS ATTAPPADI', font=bc(110), fill=WHITE, anchor='mm')
    d.text((W/2, 1180), 'വാർത്തകൾ വിശദമായി', font=mj(64), fill=TINT, anchor='mm')
    d.rectangle([W/2-260, 1260, W/2+260, 1268], fill=BLUE)
    d.text((W/2, 1340), 'Follow @newsattappadi', font=bc(70), fill=WHITE, anchor='mm')
    im.save(path)

# ---------------- 2026-11-25 stories ----------------
from story import STORIES

def base2(st):
    global CREDIT, PLACE
    CREDIT = st['credit']; PLACE = st['place']
    im = base(st['headline'], st.get('label','പ്രധാന വാർത്ത'))
    d = ImageDraw.Draw(im)
    # replace place label (base() draws the Kottathara one) -> redraw region
    return im

def vchain(inp, ss, d, label):
    # blurred fill background + zoomed 16:9 band in the middle
    return (f"[{inp}:v]trim=start={ss}:duration={d},setpts=PTS-STARTPTS,fps={FPS},split[{label}a][{label}b];"
            f"[{label}a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,eq=brightness=-0.18[{label}bg];"
            f"[{label}b]scale=-2:{VID_H},crop={W}:{VID_H}[{label}fg];"
            f"[{label}bg][{label}fg]overlay=0:{VID_Y},setsar=1[{label}]")

def is_vert(src):
    if src.endswith('.jpg'): return False
    o=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',src]).decode().split(',')
    return int(o[1])>int(o[0])

def vchain2(inp, src, ss, d, label, full, zoom=1.0):
    if src.endswith('.jpg'):
        # still photo: blurred fill + fitted photo with slow push-in
        nfr = int(d*FPS)+2
        iw, ih = Image.open(src).size
        ph = 1100; pw = int(iw*ph/ih)//2*2
        if pw > W-80: pw = (W-80)//2*2; ph = int(ih*pw/iw)//2*2
        return (f"[{inp}:v]split[{label}s1][{label}s2];[{label}s1]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.2,setsar=1,fps={FPS},trim=duration={d},setpts=PTS-STARTPTS[{label}bg];"
                f"[{label}s2]scale={pw}:{ph},setsar=1,zoompan=z='1+0.0012*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nfr}:s={pw}x{ph}:fps={FPS},trim=duration={d},setpts=PTS-STARTPTS[{label}fg];"
                f"[{label}bg][{label}fg]overlay=(W-w)/2:300[{label}]")
    if full or is_vert(src):
        zw = int(W*zoom)//2*2; zh = int(H*zoom)//2*2
        return (f"[{inp}:v]trim=start={ss}:duration={d},setpts=PTS-STARTPTS,fps={FPS},"
                f"scale={zw}:{zh}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[{label}]")
    return vchain(inp, ss, d, label)

def render_seg2(i, seg, st, tmp):
    out = f'{tmp}/seg{i:02d}.mp4'; png = f'{tmp}/ov{i:02d}.png'
    im = base2(st)
    lead = seg.get('lead', 0.0); vd = dur(seg['vo']); d = lead+vd+0.02
    if seg.get('open'): opener(im, *st['opener'])
    if seg.get('cap'): caption(im, seg['cap'])
    if seg.get('lt'): lower_third(im, *seg['lt'])
    im.save(png)
    n = len(seg['vis']); part = d/n; fc = []; ins = []
    for k, v in enumerate(seg['vis']):
        clip, ss = v[0], v[1]; zoom = v[2] if len(v) > 2 else 1.0
        if clip.endswith('.jpg'): ins += ['-loop', '1', '-t', str(part+0.2), '-i', clip]
        else: ins += ['-i', clip]
        fc.append(vchain2(k, clip, ss, part+0.05, f'p{k}', st.get('full'), zoom))
    fc.append(''.join(f'[p{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[v]')
    fc.append(f'[v][{n}:v]overlay=0:0[o]')
    fc.append(f"[{n+1}:a]adelay={int(lead*1000)}|{int(lead*1000)},apad,atrim=duration={d},loudnorm=I=-16:TP=-1.5,aresample=48000[a]")
    cmd = ['ffmpeg','-v','error','-y'] + ins + ['-loop','1','-i',png,'-i',seg['vo'],'-filter_complex',';'.join(fc),'-map','[o]','-map','[a]','-t',str(d),
           '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-ar','48000','-ac','2',out]
    subprocess.run(cmd, check=True)
    return out, dur(out), 'vo'

def main2(key, OUT):
    st = STORIES[key]; tmp = f'tmp_{key}'; os.makedirs(tmp, exist_ok=True)
    parts = [render_seg2(i, s, st, tmp) for i, s in enumerate(st['segs'])]
    endcard(f'{tmp}/end.png')
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',f'{tmp}/end.png','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','3','-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-ar','48000','-ac','2',f'{tmp}/end.mp4'], check=True)
    parts.append((f'{tmp}/end.mp4', 3.0, 'end'))
    with open(f'{tmp}/list.txt', 'w') as f:
        for p, _, _ in parts: f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{tmp}/list.txt','-c','copy',f'{tmp}/joined.mp4'], check=True)
    t = 0.0; terms = []
    for i, (_, d, kind) in enumerate(parts):
        v = 0.35 if kind == 'end' else 0.08
        terms.append(f"between(t,{t:.3f},{t+d:.3f})*{v}"); t += d
    total = t
    vol = '+'.join(terms) + "+lt(t,0.6)*0.2"
    fc = (f"[1:a]atrim=duration={total},volume='{vol}':eval=frame,afade=t=out:st={total-1.5}:d=1.5[m];"
          f"[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'{tmp}/joined.mp4','-stream_loop','-1','-i',st.get('music','music.mp3'),'-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT], check=True)
    print(OUT, round(total, 2))

if __name__ == '__main__':
    main2(sys.argv[1], sys.argv[2])
