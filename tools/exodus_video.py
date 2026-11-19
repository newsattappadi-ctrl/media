"""News Attappadi exodus video: graphics (PIL) + Ken Burns shots + audio mix (ffmpeg).
usage: python3 make_video.py 1920 1080 out169.mp4   |   python3 make_video.py 1080 1920 out916.mp4"""
import sys, subprocess, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
V = W < H  # vertical reel
LIB = '/home/claude/media/assets/library/'
AUD = '/home/claude/media/assets/audio/'
FD = '/home/claude/vid/fonts/'
TMP = f'/home/claude/vid/tmp_{W}x{H}/'
os.makedirs(TMP, exist_ok=True)
NAVY, BLUE, GREY, WHITE, TINT = (6, 54, 74), (10, 122, 191), (77, 77, 77), (255, 255, 255), (124, 200, 255)
FPS = 25
S = W / 1920 if not V else W / 1080  # scale unit

def mj(sz, b=True): return ImageFont.truetype(FD + ('manjari-full-700.ttf' if b else 'manjari-full-400.ttf'), int(sz), layout_engine=ImageFont.Layout.RAQM)
def bc(sz): return ImageFont.truetype(FD + 'barlow-condensed-latin-700-normal.ttf', int(sz))
def ml(sz):  # Malayalam + digits mixed: use Noto (has latin digits)
    return ImageFont.truetype('/home/claude/na/fonts/NotoSansMalayalam-Black.ttf', int(sz), layout_engine=ImageFont.Layout.RAQM)

logo = Image.open('/home/claude/na/logo.png').convert('RGBA'); logo = logo.crop(logo.getbbox())

def wrap(d, text, f, maxw):
    out, cur = [], ''
    for w in text.split(' '):
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out

def chrome(img, file_photo=True, label='ഫയൽ ചിത്രം'):
    """top bug + handle + bottom strap"""
    d = ImageDraw.Draw(img)
    l = logo.copy(); sz = int((150 if V else 130) * S); l.thumbnail((sz, sz), Image.LANCZOS)
    img.alpha_composite(l, (int(36 * S), int((70 if V else 30) * S)))
    hf = bc(34 * S)
    d.text((W - int(36 * S), int((90 if V else 44) * S)), '@newsattappadi', font=hf, fill=WHITE, anchor='ra', stroke_width=2, stroke_fill=(0, 0, 0))
    if file_photo:
        d.text((W - int(36 * S), int((140 if V else 88) * S)), label, font=mj(26 * S), fill=WHITE, anchor='ra', stroke_width=2, stroke_fill=(0, 0, 0))
    # bottom strap
    sh = int(96 * S); y0 = H - sh - int((210 if V else 40) * S)
    lab = 'അട്ടപ്പാടി'; lf = mj(44 * S)
    lw = int(d.textlength(lab, font=lf) + 60 * S)
    d.rectangle([0, y0, lw, y0 + sh], fill=BLUE)
    d.text((lw / 2, y0 + sh / 2 + 4 * S), lab, font=lf, fill=WHITE, anchor='mm')
    d.rectangle([lw, y0, W, y0 + sh], fill=WHITE)
    d.rectangle([0, y0 + sh, W, y0 + sh + int(8 * S)], fill=NAVY)
    hl = 'അട്ടപ്പാടി ഒഴിയുന്നു, പടിഞ്ഞാറൻ മേഖല വിജനമാകുന്നു'
    hf2 = mj((40 if V else 48) * S)
    while d.textlength(hl, font=hf2) > W - lw - 50 * S: hf2 = mj(hf2.size - 2)
    d.text((lw + 26 * S, y0 + sh / 2 + 4 * S), hl, font=hf2, fill=NAVY, anchor='lm')
    return y0

def caption_png(text, hi=None, name='c'):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    y0 = chrome(img)
    if text:
        d = ImageDraw.Draw(img)
        f = mj((62 if V else 68) * S)
        maxw = W - int(120 * S)
        lines = wrap(d, text, f, maxw)
        lh = int(f.size * 1.32)
        bh = lh * len(lines) + int(40 * S)
        by = y0 - bh - int(22 * S)
        bw = max(d.textlength(x, font=f) for x in lines) + int(70 * S)
        d.rectangle([int(36 * S), by, int(36 * S) + bw, by + bh], fill=NAVY + (235,))
        d.rectangle([int(36 * S), by, int(36 * S) + int(10 * S), by + bh], fill=BLUE)
        y = by + int(22 * S)
        for ln in lines:
            x = int(36 * S + 40 * S)
            for wd in ln.split(' '):
                col = TINT if hi and any(h in wd for h in hi) else WHITE
                d.text((x, y), wd, font=f, fill=col)
                x += d.textlength(wd + ' ', font=f)
            y += lh
    p = TMP + name + '.png'; img.save(p); return p

def headline_png(name='hl'):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    chrome(img)
    d = ImageDraw.Draw(img)
    pw = W - int(100 * S) if V else int(1500 * S)
    f = mj((92 if V else 96) * S)
    lines = ['അട്ടപ്പാടി ഒഴിയുന്നു,', 'പടിഞ്ഞാറൻ മേഖല', 'വിജനമാകുന്നു'] if V else ['അട്ടപ്പാടി ഒഴിയുന്നു,', 'പടിഞ്ഞാറൻ മേഖല വിജനമാകുന്നു']
    lh = int(f.size * 1.3)
    ph = lh * len(lines) + int(170 * S)
    px, py = int(50 * S), (H - ph) // 2 - int((120 if V else 40) * S)
    d.rectangle([px, py, px + pw, py + ph], fill=NAVY + (242,))
    tf = mj(40 * S); tag = 'പ്രധാന വാർത്ത'
    tw = d.textlength(tag, font=tf) + 50 * S
    d.rectangle([px, py, px + tw, py + int(70 * S)], fill=BLUE)
    d.text((px + 25 * S, py + int(39 * S)), tag, font=tf, fill=WHITE, anchor='lm')
    y = py + int(110 * S)
    for i, ln in enumerate(lines):
        d.text((px + 45 * S, y), ln, font=f, fill=WHITE if i == 0 else TINT); y += lh
    d.rectangle([px, py + ph - int(10 * S), px + pw, py + ph], fill=BLUE)
    p = TMP + name + '.png'; img.save(p); return p

def stats_png(show2, name):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    chrome(img, file_photo=True, label='പ്രതീകാത്മക ചിത്രം')
    d = ImageDraw.Draw(img)
    pw = W - int(100 * S) if V else int(1100 * S)
    items = [('15', 'വന്യമൃഗ ആക്രമണത്തിൽ മരണം', '2022 മുതൽ')] + ([('8,000', 'പേർ സുരക്ഷിത സ്ഥലങ്ങളിലേക്ക് മാറി', 'സർക്കാർ സർവേ')] if show2 else [])
    bh = int(300 * S)
    total = bh * 2 + int(40 * S)
    px = int(50 * S); py = (H - total) // 2 - int((160 if V else 60) * S)
    for i, (n, t, s2) in enumerate(items):
        y = py + i * (bh + int(40 * S))
        d.rectangle([px, y, px + pw, y + bh], fill=NAVY + (240,))
        d.rectangle([px, y, px + int(14 * S), y + bh], fill=BLUE)
        d.text((px + 50 * S, y + 20 * S), n, font=bc(190 * S), fill=TINT)
        nw = d.textlength(n, font=bc(190 * S))
        tf = mj(46 * S)
        tl = wrap(d, t, tf, pw - nw - 110 * S)
        ty = y + int(60 * S)
        for ln in tl:
            d.text((px + 80 * S + nw, ty), ln, font=tf, fill=WHITE); ty += int(62 * S)
        d.text((px + 80 * S + nw, ty + 6 * S), s2, font=mj(32 * S, False), fill=(190, 215, 230))
    p = TMP + name + '.png'; img.save(p); return p

def end_png():
    img = Image.new('RGBA', (W, H), NAVY + (255,))
    d = ImageDraw.Draw(img)
    l = logo.copy(); sz = int(520 * S); l.thumbnail((sz, sz), Image.LANCZOS)
    cy = H // 2 - int((260 if V else 170) * S)
    img.alpha_composite(l, ((W - l.width) // 2, cy - l.height // 2))
    y = cy + l.height // 2 + int(40 * S)
    d.text((W // 2, y), 'NEWS ATTAPPADI', font=bc(110 * S), fill=WHITE, anchor='ma'); y += int(130 * S)
    d.text((W // 2, y), 'വാർത്തകൾ വിശദമായി', font=mj(56 * S), fill=TINT, anchor='ma'); y += int(110 * S)
    fw = int(620 * S)
    d.rounded_rectangle([W // 2 - fw // 2, y, W // 2 + fw // 2, y + int(100 * S)], int(50 * S), fill=BLUE)
    d.text((W // 2, y + int(52 * S)), 'Follow @newsattappadi', font=bc(60 * S), fill=WHITE, anchor='mm')
    p = TMP + 'end.png'; img.convert('RGB').save(p); return p

def photo_prep(fn):
    """cover-fit photo at 1.25x output, for slow zoom/pan"""
    im = Image.open(LIB + fn).convert('RGB')
    tw, th = int(W * 1.25), int(H * 1.25)
    r = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x = (im.width - tw) // 2; y = (im.height - th) // 2
    im = im.crop((x, y, x + tw, y + th))
    p = TMP + 'p_' + fn; im.save(p, quality=92); return p

def shot(photo, ov, dur, name, mode=0, ov_fade=True):
    """mode 0 zoom in, 1 zoom out, 2 pan right, 3 pan left"""
    pp = photo_prep(photo)
    N = int(dur * FPS) + 1
    tw, th = int(W * 1.25), int(H * 1.25)
    if mode == 0: z = f"1+0.2*on/{N}"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 1: z = f"1.2-0.2*on/{N}"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif mode == 2: z = "1.12"; x = f"(iw-iw/zoom)*on/{N}"; y = "ih/2-(ih/zoom/2)"
    else: z = "1.12"; x = f"(iw-iw/zoom)*(1-on/{N})"; y = "ih/2-(ih/zoom/2)"
    fade = ",fade=t=in:st=0:d=0.35:alpha=1" if ov_fade else ""
    fc = (f"[0:v]scale={tw*2}:{th*2},zoompan=z='{z}':x='{x}':y='{y}':d={N}:s={W}x{H}:fps={FPS},setsar=1[bg];"
          f"[1:v]format=rgba{fade}[ov];[bg][ov]overlay=0:0:shortest=1,format=yuv420p[v]")
    out = TMP + name + '.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', pp, '-loop', '1', '-t', f'{dur:.3f}', '-i', ov,
                    '-filter_complex', fc, '-map', '[v]', '-t', f'{dur:.3f}', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out], check=True)
    return out

def still(png, dur, name):
    out = TMP + name + '.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', png, '-t', f'{dur:.3f}', '-vf', 'fade=t=in:st=0:d=0.4,format=yuv420p',
                    '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out], check=True)
    return out

# ---- timeline: (section audio, [(start_in_section, photo, caption, highlights, mode)]) ----
INTRO = 1.2
plan = [
 ('s1', [(0.0, 'v_mukkali_sv.jpg', 'ആളും ആരവവുമായിരുന്ന അങ്ങാടികൾ', ['അങ്ങാടികൾ'], 0),
         (3.6, 'v_ghat_d.jpg', 'ഇന്ന് പകൽ പോലും ആളില്ല', ['ആളില്ല'], 2),
         (6.1, 'agali_road.jpg', 'മുണ്ടൻപാറ പോലുള്ള നാടുകൾ ഓർമ്മ മാത്രമാകുന്നു', ['മുണ്ടൻപാറ'], 1),
         (9.6, 'v_hills_c.jpg', 'HEADLINE', None, 0)]),
 ('s2', [(0.0, 'v_landscape_a.jpg', 'പടിഞ്ഞാറൻ മേഖലയിൽ നിന്ന് കർഷക കുടുംബങ്ങൾ കുടിയിറങ്ങുന്നു', ['കുടിയിറങ്ങുന്നു'], 2),
         (6.2, 'v_landscape_b.jpg', 'അട്ടപ്പാടി ഇന്നും 1980-കളിൽ തന്നെ', ['1980-കളിൽ'], 3)]),
 ('s3', [(0.0, 'v_ghat_a.jpg', 'ചുരം റോഡിന് 25 വർഷമായി ഒരു മാറ്റവുമില്ല', ['25', 'ചുരം'], 0),
         (3.3, 'hairpin.jpg', 'റോഡ് നിറയെ കുഴികൾ', ['കുഴികൾ'], 2),
         (6.0, 'v_ghat_b.jpg', 'യാത്ര ദുരിതം', ['ദുരിതം'], 1)]),
 ('s4', [(0.0, 'v_cowpea.jpg', 'കൃഷിയിൽ നിന്ന് വരുമാനമില്ല', ['വരുമാനമില്ല'], 0),
         (2.4, 'v_ghat_e.jpg', 'നിർമാണ സാമഗ്രികൾക്ക് തീവില, കിട്ടാനുമില്ല', ['തീവില'], 2),
         (6.0, 'v_view_a.jpg', 'അട്ടപ്പാടിയിലേക്ക് വിവാഹം ചെയ്തയയ്ക്കാൻ പോലും മടി', ['വിവാഹം'], 3),
         (11.2, 'school_agali.jpg', 'പഠിച്ച് പുറത്തുപോകുന്നവർ തിരിച്ചുവരുന്നില്ല', ['തിരിച്ചുവരുന്നില്ല'], 1)]),
 ('s5', [(0.0, 'v_view_b.jpg', 'തമിഴ്നാട്ടിൽ നിന്നുള്ളവർ വൻതോതിൽ ഭൂമി വാങ്ങുന്നു, റിസോർട്ട് മാഫിയ: ആരോപണം', ['ഭൂമി', 'റിസോർട്ട്'], 2),
         (9.4, 'v_ghat_c.jpg', 'നാട്ടുകാരുടെ സ്വൈര്യജീവിതം നഷ്ടമായി', ['സ്വൈര്യജീവിതം'], 0)]),
 ('s6', [(0.0, 'elephant.jpg', 'STATS1', None, 0),
         (5.3, 'elephant.jpg', 'STATS2', None, 0)]),
 ('s7', [(0.0, 'v_landscape_b.jpg', 'റോഡ് നന്നായാൽ മാറും അട്ടപ്പാടിയുടെ മുഖച്ഛായ', ['റോഡ്', 'മുഖച്ഛായ'], 1),
         (3.7, 'v_hills_c.jpg', 'അട്ടപ്പാടിക്കാരെ കുടിയൊഴിപ്പിക്കാനോ? സംശയം ഉയരുന്നു', ['കുടിയൊഴിപ്പിക്കാനോ?'], 2),
         (10.2, None, 'END', None, 0)]),
]
GAP = 0.5
dur = {k: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', AUD + f'exodus_{k}.wav']).decode()) for k, _ in plan}

clips, t, vo = [], INTRO, []
k = 0
for si, (sec, shots) in enumerate(plan):
    secdur = dur[sec] + GAP
    vo.append((sec, t))
    for j, (st, ph, cap, hi, mode) in enumerate(shots):
        en = shots[j + 1][0] if j + 1 < len(shots) else secdur
        d = en - st + (INTRO if k == 0 else 0)
        if cap == 'END':
            d += 3.0
            clips.append(still(end_png(), d, f'c{k:02d}'))
        else:
            if cap == 'HEADLINE': ov = headline_png()
            elif cap.startswith('STATS'): ov = stats_png(cap == 'STATS2', f'st{k}')
            else: ov = caption_png(cap, hi, f'cap{k}')
            clips.append(shot(ph, ov, d, f'c{k:02d}', mode, ov_fade=(cap != 'STATS2')))
        k += 1
    t += secdur
total = t + 3.0
with open(TMP + 'list.txt', 'w') as f:
    for c in clips: f.write(f"file '{c}'\n")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', TMP + 'list.txt', '-c', 'copy', TMP + 'video.mp4'], check=True)

# audio: music loud in intro, ducked under voice, fade out
inputs = ['-i', AUD + 'exodus_music.mp3']
fl = []
for i, (sec, st) in enumerate(vo):
    inputs += ['-i', AUD + f'exodus_{sec}.wav']
    ms = int(st * 1000)
    fl.append(f"[{i+1}:a]aresample=44100,volume=1.6,adelay={ms}|{ms}[v{i}]")
vmix = ''.join(f'[v{i}]' for i in range(len(vo)))
vstart = vo[0][1]
fc = ';'.join(fl) + f";{vmix}amix=inputs={len(vo)}:normalize=0[vo];" \
     f"[0:a]aresample=44100,atrim=0:{total:.2f},volume='if(lt(t,{vstart}),0.55,0.10)':eval=frame,afade=t=out:st={total-2.5:.2f}:d=2.5[mu];" \
     f"[vo][mu]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]"
subprocess.run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', fc, '-map', '[a]', '-t', f'{total:.2f}', '-c:a', 'aac', '-b:a', '192k', TMP + 'audio.m4a'], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', TMP + 'video.mp4', '-i', TMP + 'audio.m4a', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', OUT], check=True)
print('done', OUT, round(total, 1), 's')
