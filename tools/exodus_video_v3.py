"""Exodus news video v2: stock footage + real photos + animated maps + TV graphics.
usage: python3 make_v2.py W H out.mp4"""
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
V = H > W
S = W / 1920 if not V else W / 1080
LIB = '/home/claude/media/assets/library/'
AUD = '/home/claude/media/assets/audio/'
FD = '/home/claude/vid/fonts/'
TMP = f'/home/claude/vid2/tmp_{W}x{H}/'; os.makedirs(TMP, exist_ok=True)
NAVY, BLUE, WHITE, TINT, RED = (6, 54, 74), (10, 122, 191), (255, 255, 255), (124, 200, 255), (214, 48, 48)
FPS = 25
INTRO = 1.0
def mj(sz): return ImageFont.truetype(FD + 'manjari-full-700.ttf', int(sz), layout_engine=ImageFont.Layout.RAQM)
def bc(sz): return ImageFont.truetype(FD + 'barlow-condensed-latin-700-normal.ttf', int(sz))
logo = Image.open('/home/claude/na/logo.png').convert('RGBA'); logo = logo.crop(logo.getbbox())

def wrap(d, text, f, maxw):
    out, cur = [], ''
    for w in text.split(' '):
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out

STRAP_H = int(96 * S)
STRAP_Y = H - STRAP_H - int((230 if V else 40) * S)

def chrome_png(tag, name):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    # top gradient for legibility
    for y in range(int(200 * S)):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(110 * (1 - y / (200 * S)))))
    l = logo.copy(); sz = int((150 if V else 130) * S); l.thumbnail((sz, sz), Image.LANCZOS)
    img.alpha_composite(l, (int(36 * S), int((80 if V else 30) * S)))
    d.text((W - int(36 * S), int((100 if V else 44) * S)), '@newsattappadi', font=bc(36 * S), fill=WHITE, anchor='ra')
    if tag:
        d.text((W - int(36 * S), int((150 if V else 90) * S)), tag, font=mj(28 * S), fill=WHITE, anchor='ra', stroke_width=2, stroke_fill=(0, 0, 0))
    # bottom strap
    lab = 'അട്ടപ്പാടി'; lf = mj(44 * S); lw = int(d.textlength(lab, font=lf) + 60 * S)
    d.rectangle([0, STRAP_Y, lw, STRAP_Y + STRAP_H], fill=RED)
    d.text((lw / 2, STRAP_Y + STRAP_H / 2 + 4 * S), lab, font=lf, fill=WHITE, anchor='mm')
    d.rectangle([lw, STRAP_Y, W, STRAP_Y + STRAP_H], fill=WHITE)
    d.rectangle([0, STRAP_Y + STRAP_H, W, STRAP_Y + STRAP_H + int(10 * S)], fill=NAVY)
    hl = 'അട്ടപ്പാടി ഒഴിയുന്നു, പടിഞ്ഞാറൻ മേഖല വിജനമാകുന്നു'; hf = mj((40 if V else 48) * S)
    while d.textlength(hl, font=hf) > W - lw - 50 * S: hf = mj(hf.size - 2)
    d.text((lw + 26 * S, STRAP_Y + STRAP_H / 2 + 4 * S), hl, font=hf, fill=NAVY, anchor='lm')
    p = TMP + name + '.png'; img.save(p); return p

def caption_png(text, hi, name):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = mj((62 if V else 66) * S); maxw = W - int(130 * S)
    lines = wrap(d, text, f, maxw); lh = int(f.size * 1.3)
    bh = lh * len(lines) + int(36 * S); by = STRAP_Y - bh - int(20 * S)
    bw = max(d.textlength(x, font=f) for x in lines) + int(76 * S)
    d.rectangle([int(36 * S), by, int(36 * S) + bw, by + bh], fill=NAVY + (238,))
    d.rectangle([int(36 * S), by, int(48 * S), by + bh], fill=BLUE)
    y = by + int(20 * S)
    for ln in lines:
        x = int(36 * S + 42 * S)
        for wd in ln.split(' '):
            col = TINT if hi and any(h in wd for h in hi) else WHITE
            d.text((x, y), wd, font=f, fill=col); x += d.textlength(wd + ' ', font=f)
        y += lh
    p = TMP + name + '.png'; img.save(p); return p

def headline_png():
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f1 = mj((112 if V else 128) * S); f2 = mj((78 if V else 84) * S)
    l1 = 'അട്ടപ്പാടി ഒഴിയുന്നു'; l2s = ['പടിഞ്ഞാറൻ മേഖല', 'വിജനമാകുന്നു'] if V else ['പടിഞ്ഞാറൻ മേഖല വിജനമാകുന്നു']
    w1 = d.textlength(l1, font=f1); w2 = max(d.textlength(x, font=f2) for x in l2s)
    pw = max(w1, w2) + 120 * S; ph = f1.size * 1.35 + len(l2s) * f2.size * 1.3 + 150 * S
    px = (W - pw) / 2; py = (H - ph) / 2 - (140 if V else 40) * S
    d.rectangle([px, py, px + pw, py + ph], fill=NAVY + (240,))
    tag = 'പ്രധാന വാർത്ത'; tf = mj(42 * S); tw = d.textlength(tag, font=tf) + 50 * S
    d.rectangle([px, py - 70 * S, px + tw, py], fill=RED)
    d.text((px + 25 * S, py - 33 * S), tag, font=tf, fill=WHITE, anchor='lm')
    d.text((W / 2, py + 50 * S), l1, font=f1, fill=WHITE, anchor='ma')
    y = py + 50 * S + f1.size * 1.35
    for x in l2s: d.text((W / 2, y), x, font=f2, fill=TINT, anchor='ma'); y += f2.size * 1.3
    d.rectangle([px, py + ph - 12 * S, px + pw, py + ph], fill=RED)
    p = TMP + 'headline.png'; img.save(p); return p

def big_png(text, sub, name, col=RED):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = mj((84 if V else 92) * S); lines = wrap(d, text, f, W - 200 * S)
    lh = f.size * 1.3; ph = lh * len(lines) + 120 * S
    pw = max(d.textlength(x, font=f) for x in lines) + 120 * S
    px = (W - pw) / 2; py = (H - ph) / 2 - (160 if V else 60) * S
    d.rectangle([px, py, px + pw, py + ph], fill=(0, 0, 0, 200))
    d.rectangle([px, py, px + pw, py + 12 * S], fill=col)
    y = py + 55 * S
    for x in lines: d.text((W / 2, y), x, font=f, fill=WHITE, anchor='ma'); y += lh
    if sub:
        sf = mj(40 * S); sw = d.textlength(sub, font=sf) + 50 * S
        d.rectangle([(W - sw) / 2, py + ph, (W + sw) / 2, py + ph + 64 * S], fill=col)
        d.text((W / 2, py + ph + 34 * S), sub, font=sf, fill=WHITE, anchor='mm')
    p = TMP + name + '.png'; img.save(p); return p

def stat_png(num, text, sub, slot, name):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    pw = W - int(100 * S) if V else int(1080 * S); bh = int(270 * S)
    px = int(50 * S); py = (int(560 * S) if V else int(230 * S)) + slot * (bh + int(36 * S))
    d.rectangle([px, py, px + pw, py + bh], fill=NAVY + (240,)); d.rectangle([px, py, px + int(14 * S), py + bh], fill=RED)
    nf = bc(200 * S); d.text((px + 50 * S, py + 20 * S), num, font=nf, fill=TINT); nw = d.textlength(num, font=nf)
    tf = mj(46 * S); ty = py + int(58 * S)
    for ln in wrap(d, text, tf, pw - nw - 110 * S): d.text((px + 80 * S + nw, ty), ln, font=tf, fill=WHITE); ty += int(60 * S)
    d.text((px + 80 * S + nw, ty + 4 * S), sub, font=mj(32 * S), fill=(190, 215, 230))
    p = TMP + name + '.png'; img.save(p); return p

def esa_stamp_png():
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = mj((84 if V else 96) * S); t = 'പരിസ്ഥിതിലോല പ്രദേശം'; tw = d.textlength(t, font=f)
    cx, cy = W / 2, H * (0.36 if V else 0.38)
    box = Image.new('RGBA', (int(tw + 80 * S), int(130 * S)), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    box = Image.new('RGBA', (int(tw + 90 * S), int(170 * S)), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rectangle([4, 4, box.width - 4, box.height - 4], fill=(255, 255, 255, 215), outline=RED + (255,), width=int(12 * S))
    bd.text((box.width / 2, box.height / 2 + 4 * S), t, font=f, fill=RED + (255,), anchor='mm')
    box = box.rotate(-8, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(box, (int(cx - box.width / 2), int(cy - box.height / 2)))
    p = TMP + 'esa.png'; img.save(p); return p

def end_png():
    img = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(img)
    l = logo.copy(); sz = int(500 * S); l.thumbnail((sz, sz), Image.LANCZOS)
    cy = H // 2 - int((260 if V else 170) * S)
    img.paste(l, ((W - l.width) // 2, cy - l.height // 2), l)
    y = cy + l.height // 2 + int(40 * S)
    d.text((W // 2, y), 'NEWS ATTAPPADI', font=bc(110 * S), fill=WHITE, anchor='ma'); y += int(130 * S)
    d.text((W // 2, y), 'വാർത്തകൾ വിശദമായി', font=mj(56 * S), fill=TINT, anchor='ma'); y += int(110 * S)
    fw = int(620 * S); d.rounded_rectangle([W // 2 - fw // 2, y, W // 2 + fw // 2, y + int(100 * S)], int(50 * S), fill=BLUE)
    d.text((W // 2, y + int(52 * S)), 'Follow @newsattappadi', font=bc(60 * S), fill=WHITE, anchor='mm')
    p = TMP + 'end.png'; img.save(p); return p

def bg_from_photo(fn, name):
    """cover-fit at 1.25x for zoompan; small/odd images get a blurred backdrop with the photo fitted in the centre"""
    im = Image.open(LIB + fn).convert('RGB')
    tw, th = int(W * 1.25), int(H * 1.25)
    cover = max(tw / im.width, th / im.height)
    if cover > 2.2 or abs((im.width / im.height) - (W / H)) > 0.9:
        bg = im.resize((int(im.width * cover) + 1, int(im.height * cover) + 1)).filter(ImageFilter.GaussianBlur(30 * S))
        bg = ImageEnhance.Brightness(bg).enhance(0.55)
        bg = bg.crop(((bg.width - tw) // 2, (bg.height - th) // 2, (bg.width - tw) // 2 + tw, (bg.height - th) // 2 + th))
        fit = min(tw * 0.80 / im.width, th * 0.80 / im.height)
        fg = im.resize((int(im.width * fit), int(im.height * fit)), Image.LANCZOS)
        bg.paste(fg, ((tw - fg.width) // 2, (th - fg.height) // 2))
        im = bg
    else:
        im = im.resize((int(im.width * cover) + 1, int(im.height * cover) + 1), Image.LANCZOS)
        im = im.crop(((im.width - tw) // 2, (im.height - th) // 2, (im.width - tw) // 2 + tw, (im.height - th) // 2 + th))
    p = TMP + 'bg_' + name + '.jpg'; im.save(p, quality=92); return p

def run(args): subprocess.run(['ffmpeg', '-y', '-v', 'error'] + args, check=True)

def layer_filters(n_in, overlays):
    """overlays: list of (input_index, kind, t0) kind: static|slide|slam"""
    fc, last = [], '[base]'
    for k, (idx, kind, t0) in enumerate(overlays):
        o = f'[o{k}]'
        if kind == 'slide':
            fc.append(f"[{idx}:v]format=rgba,setpts=PTS+{t0}/TB[l{k}]")
            fc.append(f"{last}[l{k}]overlay=x='if(lt(t,{t0}),-W,min(0,-W+(t-{t0})*W/0.28))':y=0:eof_action=pass{o}")
        elif kind == 'slam':
            fc.append(f"[{idx}:v]format=rgba,setpts=PTS+{t0}/TB,scale=w='iw*(1+0.35*max(0,1-(t-{t0})/0.3))':h=-1:eval=frame[l{k}]")
            fc.append(f"{last}[l{k}]overlay=x='(W-w)/2':y='(H-h)/2':eof_action=pass:enable='gte(t,{t0})'{o}")
        elif kind == 'fade':
            fc.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,setpts=PTS+{t0}/TB[l{k}]")
            fc.append(f"{last}[l{k}]overlay=0:0:eof_action=pass:enable='gte(t,{t0})'{o}")
        else:
            fc.append(f"{last}[{idx}:v]overlay=0:0{o}")
        last = o
    return fc, last

GRADE = "eq=contrast=1.06:saturation=0.92,vignette=PI/5"

def shot_clip(src, dur, name, overlays, ss=0.6, extra=''):
    """stock video, cover-cropped. overlays: list of (png, kind, t0)"""
    out = TMP + name + '.mp4'
    ins = ['-stream_loop', '-1', '-ss', str(ss), '-i', AUD + src]
    for png, kind, t0 in overlays: ins += ['-loop', '1', '-t', f'{dur:.3f}', '-i', png]
    fc = [f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,{GRADE}{extra}[base]"]
    lf, last = layer_filters(len(overlays), [(i + 1, k, t0) for i, (_, k, t0) in enumerate(overlays)])
    fc += lf
    run(ins + ['-filter_complex', ';'.join(fc) + f";{last}format=yuv420p[v]", '-map', '[v]', '-t', f'{dur:.3f}', '-an', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out])
    return out

def shot_photo(fn, dur, name, overlays, mode=0):
    pp = bg_from_photo(fn, name); N = int(dur * FPS) + 1
    tw, th = int(W * 1.25), int(H * 1.25)
    z, x, y = [(f"1+0.18*on/{N}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"), (f"1.18-0.18*on/{N}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
               ("1.12", f"(iw-iw/zoom)*on/{N}", "ih/2-(ih/zoom/2)"), ("1.12", f"(iw-iw/zoom)*(1-on/{N})", "ih/2-(ih/zoom/2)")][mode]
    out = TMP + name + '.mp4'
    ins = ['-loop', '1', '-i', pp]
    for png, kind, t0 in overlays: ins += ['-loop', '1', '-t', f'{dur:.3f}', '-i', png]
    fc = [f"[0:v]scale={tw*2}:{th*2},zoompan=z='{z}':x='{x}':y='{y}':d={N}:s={W}x{H}:fps={FPS},setsar=1,{GRADE}[base]"]
    lf, last = layer_filters(len(overlays), [(i + 1, k, t0) for i, (_, k, t0) in enumerate(overlays)])
    fc += lf
    run(ins + ['-filter_complex', ';'.join(fc) + f";{last}format=yuv420p[v]", '-map', '[v]', '-t', f'{dur:.3f}', '-an', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out])
    return out

def shot_map(scene, dur, name, overlays):
    raw = TMP + name + '_raw.mp4'
    subprocess.run(['python3', '/home/claude/vid2/maps.py', str(W), str(H), scene, f'{dur:.3f}', raw], check=True, capture_output=True)
    out = TMP + name + '.mp4'
    ins = ['-i', raw]
    for png, kind, t0 in overlays: ins += ['-loop', '1', '-t', f'{dur:.3f}', '-i', png]
    fc = ["[0:v]setsar=1[base]"]
    lf, last = layer_filters(len(overlays), [(i + 1, k, t0) for i, (_, k, t0) in enumerate(overlays)])
    fc += lf
    run(ins + ['-filter_complex', ';'.join(fc) + f";{last}format=yuv420p[v]", '-map', '[v]', '-t', f'{dur:.3f}', '-an', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out])
    return out

# chrome variants
CH_SYM = chrome_png('പ്രതീകാത്മക ദൃശ്യം', 'ch_sym')
CH_FILE = chrome_png('ഫയൽ ചിത്രം', 'ch_file')
CH_OWN = chrome_png('ദൃശ്യം: News Attappadi', 'ch_own')
CH_MAP = chrome_png('', 'ch_map')
def cap(t, hi, n): return caption_png(t, hi, n)

# timeline in voiceover seconds (vo starts at INTRO). (start, end, kind, src, overlays_fn)
T = [
 (0.0, 4.8, 'photo', 'u_mundanpara.jpg', lambda: [(CH_OWN, 'static', 0), (headline_png(), 'slam', 0.15)]),
 (4.8, 10.3, 'map', 'west', lambda: [(CH_MAP, 'static', 0)]),
 (10.3, 13.5, 'photo', 'agali_road.jpg', lambda: [(CH_FILE, 'static', 0), (cap('മുണ്ടൻപാറ ഉൾപ്പെടെയുള്ള പ്രദേശങ്ങൾ ആളൊഴിഞ്ഞു', ['മുണ്ടൻപാറ'], 'c1'), 'slide', 0.1)]),
 (13.5, 17.0, 'photo', 'v_mukkali_sv.jpg', lambda: [(CH_FILE, 'static', 0), (cap('പകൽ പോലും അങ്ങാടികളിൽ ആളില്ല', ['ആളില്ല'], 'c2'), 'slide', 0.1)]),
 (17.0, 25.0, 'map', 'churam', lambda: [(CH_MAP, 'static', 0)]),
 (25.0, 29.2, 'photo', 'u_churam_potholes.jpg', lambda: [(CH_OWN, 'static', 0), (cap('ആനമൂളി മുതൽ മന്ദംപൊട്ടി വരെ കുഴികൾ', ['കുഴികൾ'], 'c3'), 'slide', 0.1)]),
 (29.2, 35.5, 'map', 'bend', lambda: [(CH_MAP, 'static', 0)]),
 (35.5, 38.4, 'photo', 'hairpin.jpg', lambda: [(CH_FILE, 'static', 0), (big_png('ചരക്കുവാഹനങ്ങൾക്ക് നിരോധനം', 'അട്ടപ്പാടി ചുരം', 'b1'), 'slam', 0.1)]),
 (38.4, 43.0, 'photo', 'ghat_road.jpg', lambda: [(CH_FILE, 'static', 0), (big_png('നിർമാണ സാമഗ്രികൾ കിട്ടാനില്ല', 'വില കുതിച്ചുയർന്നു', 'b2'), 'slam', 0.2)]),
 (43.0, 50.4, 'map', 'ambulance', lambda: [(CH_MAP, 'static', 0)]),
 (50.4, 55.2, 'photo', 'r_kottathara_ambulance.jpg', lambda: [(CH_FILE, 'static', 0), (cap('ചികിത്സ വൈകി ആദിവാസി യുവാവ് മരിച്ചു (ജൂലൈ 2026)', ['മരിച്ചു'], 'c6'), 'slide', 0.1)]),
 (55.2, 59.85, 'photo', 'foggy_route.jpg', lambda: [(CH_FILE, 'static', 0), (cap('ഗുരുതര രോഗികൾ ഇപ്പോഴും തൃശൂർ മെഡിക്കൽ കോളേജിലേക്ക്', ['തൃശൂർ'], 'c7'), 'slide', 0.1)]),
 (59.85, 62.34, 'photo', 'jowar.jpg', lambda: [(CH_FILE, 'static', 0), (cap('കാർഷിക വരുമാനം കുത്തനെ ഇടിഞ്ഞു', ['ഇടിഞ്ഞു'], 'c8'), 'slide', 0.1)]),
 (62.34, 66.3, 'photo', 'r_attapady_hills.jpg', lambda: [(CH_FILE, 'static', 0), (cap('അട്ടപ്പാടിയിലേക്ക് വിവാഹം ചെയ്തയയ്ക്കാൻ മടി', ['വിവാഹം'], 'c9'), 'slide', 0.1)]),
 (66.3, 70.87, 'photo', 'school_agali.jpg', lambda: [(CH_FILE, 'static', 0), (cap('പഠിച്ച് പുറത്തുപോകുന്ന പുതുതലമുറ തിരിച്ചുവരുന്നില്ല', ['തിരിച്ചുവരുന്നില്ല'], 'c10'), 'slide', 0.1)]),
 (70.87, 75.6, 'photo', 'v_landscape_a.jpg', lambda: [(CH_FILE, 'static', 0), (esa_stamp_png(), 'slam', 0.4)]),
 (75.6, 80.26, 'photo', 'narasimukk.jpg', lambda: [(CH_FILE, 'static', 0), (cap('കൃഷിയിലും നിർമാണത്തിലും നിയന്ത്രണം വരുമോ എന്ന ആശങ്ക', ['ആശങ്ക'], 'c11'), 'slide', 0.1)]),
 (80.26, 89.23, 'map', 'land', lambda: [(CH_MAP, 'static', 0)]),
 (89.23, 91.84, 'photo', 'v_landscape_b.jpg', lambda: [(CH_FILE, 'static', 0), (cap('നാട്ടുകാരുടെ സ്വൈര്യജീവിതം നഷ്ടമായി', ['സ്വൈര്യജീവിതം'], 'c12'), 'slide', 0.1)]),
 (91.84, 98.99, 'photo', 'r_attapadi_plains.jpg', lambda: [(CH_FILE, 'static', 0), (cap('വന്യമൃഗശല്യവും രൂക്ഷം', ['രൂക്ഷം'], 'c13'), 'slide', 0.1),
     (stat_png('15', 'വന്യമൃഗ ആക്രമണത്തിൽ മരണം', '2022 മുതൽ', 0, 's1'), 'slide', 2.4)]),
 (98.99, 105.29, 'photo', 'hills_mist_2.jpg', lambda: [(CH_FILE, 'static', 0), (stat_png('15', 'വന്യമൃഗ ആക്രമണത്തിൽ മരണം', '2022 മുതൽ', 0, 's1b'), 'static', 0),
     (stat_png('8,000', 'പേർ സുരക്ഷിത സ്ഥലങ്ങളിലേക്ക് മാറി', 'സർക്കാർ സർവേ', 1, 's2'), 'slide', 0.1)]),
 (105.29, 110.22, 'photo', 'v_ghat_a.jpg', lambda: [(CH_FILE, 'static', 0), (cap('ചുരം റോഡ് നന്നാക്കിയാൽ മാറും അട്ടപ്പാടിയുടെ മുഖച്ഛായ', ['ചുരം', 'മുഖച്ഛായ'], 'c14'), 'slide', 0.1)]),
 (110.22, 116.4, 'photo', 'u_churam_potholes.jpg', lambda: [(CH_OWN, 'static', 0), (big_png('അട്ടപ്പാടിക്കാരെ കുടിയൊഴിപ്പിക്കാനോ?', 'ആശങ്ക ഉയരുന്നു', 'b3'), 'slam', 0.3)]),
]
END_EXTRA = 3.0
VO_LEN = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', AUD + 'x3_vo.wav']).decode())

clips = []
for k, (a, b, kind, src, ovf) in enumerate(T):
    dur = b - a + (INTRO if k == 0 else 0)
    ov = ovf()
    if k == 0: ov = [(p, kd, t0 + (INTRO if kd != 'static' else 0)) for p, kd, t0 in ov]
    name = f's{k:02d}'
    if kind == 'clip': clips.append(shot_clip(src, dur, name, ov, ss=0.6 if k != 3 else 5.0, extra=',eq=gamma=1.6:brightness=0.04' if src == 'x2_elephants.mp4' else ''))
    elif kind == 'photo': clips.append(shot_photo(src, dur, name, ov, mode=k % 4))
    else: clips.append(shot_map(src, dur, name, ov))
    print('shot', k, round(dur, 2), flush=True)
end_dur = (VO_LEN - T[-1][1]) + END_EXTRA
ep = end_png(); eo = TMP + 'end.mp4'
run(['-loop', '1', '-i', ep, '-t', f'{end_dur:.3f}', '-vf', 'fade=t=in:st=0:d=0.3,format=yuv420p', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', eo])
clips.append(eo)
with open(TMP + 'list.txt', 'w') as f:
    for c in clips: f.write(f"file '{c}'\n")
run(['-f', 'concat', '-safe', '0', '-i', TMP + 'list.txt', '-c', 'copy', TMP + 'video.mp4'])
total = INTRO + VO_LEN + END_EXTRA
ms = int(INTRO * 1000)
fc = (f"[1:a]aresample=44100,volume=1.5,adelay={ms}|{ms}[vo];"
      f"[0:a]aresample=44100,atrim=0:{total:.2f},volume='if(lt(t,{INTRO}),0.6,if(gt(t,{INTRO+VO_LEN}),0.5,0.09))':eval=frame,afade=t=out:st={total-2.5:.2f}:d=2.5[mu];"
      f"[vo][mu]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
run(['-i', AUD + 'exodus_music.mp3', '-i', AUD + 'x3_vo.wav', '-filter_complex', fc, '-map', '[a]', '-t', f'{total:.2f}', '-c:a', 'aac', '-b:a', '192k', TMP + 'audio.m4a'])
run(['-i', TMP + 'video.mp4', '-i', TMP + 'audio.m4a', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', OUT])
print('done', OUT, round(total, 1))
