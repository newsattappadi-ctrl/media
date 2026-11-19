"""Animated vector map scenes for the exodus video. Each scene renders RGB frames piped to ffmpeg.
usage: python3 maps.py W H scene dur out.mp4"""
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, SCENE, DUR, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], float(sys.argv[4]), sys.argv[5]
V = H > W
S = (W / 1920) if not V else (W / 1080)
FPS = 25
NAVY, BLUE, TINT, WHITE, RED = (6, 54, 74), (10, 122, 191), (124, 200, 255), (255, 255, 255), (226, 59, 59)
BG = (4, 26, 38)
FD = '/home/claude/vid/fonts/'
def mj(sz): return ImageFont.truetype(FD + 'manjari-full-700.ttf', int(sz), layout_engine=ImageFont.Layout.RAQM)

G = json.load(open('/home/claude/vid2/geo/south_s.geojson'))['features']
def rings(geom):
    if geom['type'] == 'Polygon': return [geom['coordinates'][0]]
    return [p[0] for p in geom['coordinates']]
FEAT = [(f['properties']['st'], f['properties']['d'], rings(f['geometry'])) for f in G]

P = {  # approximate coordinates (lon, lat)
 'മണ്ണാർക്കാട്': (76.462, 10.993), 'ആനമൂളി': (76.495, 11.027), 'മന്ദംപൊട്ടി': (76.515, 11.048),
 'മുക്കാലി': (76.535, 11.066), 'അഗളി': (76.648, 11.098), 'കോട്ടത്തറ': (76.684, 11.106),
 'ആനക്കട്ടി': (76.772, 11.104), 'തൃശൂർ മെഡി. കോളേജ്': (76.206, 10.592), 'കോയമ്പത്തൂർ': (76.955, 11.017),
 'പാലക്കാട്': (76.65, 10.775),
}
ATT = (76.63, 11.10)  # Attappadi centre
CHURAM = ['മണ്ണാർക്കാട്', 'ആനമൂളി', 'മന്ദംപൊട്ടി', 'മുക്കാലി', 'അഗളി']

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

class Cam:
    def __init__(s, lon, lat, span): s.lon, s.lat, s.span = lon, lat, span
    def px(s, lon, lat):
        k = (W if not V else W * 1.0) / s.span
        x = W / 2 + (lon - s.lon) * k * math.cos(math.radians(s.lat))
        y = H / 2 - (lat - s.lat) * k
        return x, y

def base(cam, hl_dist=None, dim_others=True):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    # grid lines
    for i in range(0, W, int(80 * S)): d.line([(i, 0), (i, H)], fill=(255, 255, 255, 10))
    for j in range(0, H, int(80 * S)): d.line([(0, j), (W, j)], fill=(255, 255, 255, 10))
    for st, dist, rs in FEAT:
        if st == 'Kerala': fill = (14, 70, 96, 255); line = (60, 140, 180, 255)
        else: fill = (10, 40, 56, 255); line = (40, 80, 100, 255)
        if hl_dist and dist == hl_dist: fill = (16, 96, 140, 255); line = TINT + (255,)
        for r in rs:
            pts = [cam.px(x, y) for x, y in r]
            if len(pts) > 2: d.polygon(pts, fill=fill, outline=line)
    return img, d

def label(d, xy, text, size=34, color=WHITE, dot=True, anchor='l', box=True):
    x, y = xy; f = mj(size * S)
    if dot:
        d.ellipse([x - 9 * S, y - 9 * S, x + 9 * S, y + 9 * S], fill=WHITE, outline=BLUE, width=int(4 * S))
    tw = d.textlength(text, font=f)
    tx = x + 18 * S if anchor == 'l' else x - 18 * S - tw
    if box:
        d.rounded_rectangle([tx - 10 * S, y - size * S * 0.75, tx + tw + 10 * S, y + size * S * 0.65], int(8 * S), fill=(0, 0, 0, 150))
    d.text((tx, y + 3 * S), text, font=f, fill=color, anchor='lm')

def title(d, text, sub=None):
    f = mj((54 if V else 52) * S)
    y0 = int((270 if V else 175) * S)
    tw = d.textlength(text, font=f)
    d.rectangle([0, y0, tw + 90 * S, y0 + 90 * S], fill=NAVY + (240,))
    d.rectangle([0, y0, 14 * S, y0 + 90 * S], fill=BLUE)
    d.text((45 * S, y0 + 48 * S), text, font=f, fill=WHITE, anchor='lm')
    if sub:
        sf = mj(32 * S); sw = d.textlength(sub, font=sf)
        d.rectangle([0, y0 + 90 * S, sw + 90 * S, y0 + 145 * S], fill=BLUE + (235,))
        d.text((45 * S, y0 + 118 * S), sub, font=sf, fill=WHITE, anchor='lm')

def glow_circle(img, xy, r, col, alpha):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    x, y = xy
    dd.ellipse([x - r, y - r, x + r, y + r], fill=col + (alpha,))
    lay = lay.filter(ImageFilter.GaussianBlur(r * 0.25))
    img.paste(lay, (0, 0), lay)

def polyline(d, pts, t, col, width):
    """draw first fraction t of the polyline; return the head point"""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(seg) * t; acc = 0; out = [pts[0]]
    for i, s_ in enumerate(seg):
        if acc + s_ >= L:
            f = (L - acc) / s_ if s_ else 0
            out.append((lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f))); break
        out.append(pts[i + 1]); acc += s_
    if len(out) > 1: d.line(out, fill=col, width=width, joint='curve')
    return out[-1]

def arrow(d, a, b, t, col, w):
    x = lerp(a[0], b[0], t); y = lerp(a[1], b[1], t)
    d.line([a, (x, y)], fill=col, width=w)
    ang = math.atan2(y - a[1], x - a[0]); L = 26 * S
    d.polygon([(x, y), (x - L * math.cos(ang - 0.45), y - L * math.sin(ang - 0.45)), (x - L * math.cos(ang + 0.45), y - L * math.sin(ang + 0.45))], fill=col)

def frame(i):
    t = i / FPS; u = t / DUR
    if SCENE == 'west':
        z = ease(t / 2.5)
        cam = Cam(lerp(76.3, 76.62, z), lerp(10.4, 11.08, z), lerp(5.5 if not V else 3.6, 0.75 if not V else 0.5, z))
        img, d = base(cam, hl_dist='Palakkad')
        a = cam.px(*ATT)
        glow_circle(img, a, 150 * S * (1 + 0.05 * math.sin(t * 4)), TINT, int(90 * ease((t - 1.5) / 1)))
        d = ImageDraw.Draw(img, 'RGBA')
        # western region highlight (red)
        if t > 2.4:
            w = cam.px(76.56, 11.08)
            glow_circle(img, w, 95 * S, RED, int(170 * ease((t - 2.4) / 0.8)))
            d = ImageDraw.Draw(img, 'RGBA')
            for k, (dx, dy) in enumerate([(-1, 0.25), (-1, -0.15), (-0.8, 0.6)]):
                tt = ease((t - 3.0 - k * 0.25) / 1.2)
                if tt > 0:
                    arrow(d, (w[0] - 30 * S, w[1]), (w[0] + dx * 260 * S, w[1] + dy * 260 * S), tt, (255, 220, 220, 255), int(7 * S))
            label(d, (w[0], w[1] + 120 * S), 'പടിഞ്ഞാറൻ മേഖല', 38, (255, 200, 200), dot=False)
        if t > 1.6: label(d, cam.px(76.66, 11.14), 'അട്ടപ്പാടി', 46, TINT, dot=False)
        label(d, cam.px(*P['പാലക്കാട്']), 'പാലക്കാട്', 32)
        title(d, 'കുടിയിറങ്ങുന്ന കർഷകർ', 'പടിഞ്ഞാറൻ അട്ടപ്പാടി')
        return img
    if SCENE == 'churam':
        cam = Cam(76.56, 11.045, 0.42 if not V else 0.30)
        img, d = base(cam)
        pts = [cam.px(*P[n]) for n in CHURAM]
        d.line(pts, fill=(255, 255, 255, 40), width=int(18 * S), joint='curve')
        head = polyline(d, pts, ease(t / 3.0), (255, 200, 60, 255), int(10 * S))
        d.ellipse([head[0] - 12 * S, head[1] - 12 * S, head[0] + 12 * S, head[1] + 12 * S], fill=(255, 200, 60))
        for j, n in enumerate(CHURAM):
            if t > j * 0.6: label(d, cam.px(*P[n]), n, 34, anchor='r' if n in ('ആനമൂളി', 'മന്ദംപൊട്ടി') else 'l')
        # pothole stretch Anamooli - Mandampotti
        if t > 3.2:
            a, b = cam.px(*P['ആനമൂളി']), cam.px(*P['മന്ദംപൊട്ടി'])
            pulse = int(150 + 100 * math.sin(t * 6))
            d.line([a, b], fill=RED + (pulse,), width=int(14 * S))
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            label(d, (mx - 40 * S, my + 45 * S), 'കുഴികൾ', 34, (255, 200, 200), dot=False, anchor='r')
        if t > 4.6:  # 10th bend X
            x, y = cam.px(76.505, 11.038)
            r = 26 * S * ease((t - 4.6) / 0.4)
            d.line([(x - r, y - r), (x + r, y + r)], fill=RED, width=int(10 * S)); d.line([(x - r, y + r), (x + r, y - r)], fill=RED, width=int(10 * S))
            label(d, (x + 40 * S, y + 10 * S), 'പത്താം വളവ്: ചരക്കുവാഹന നിരോധനം', 32, (255, 210, 210), dot=False)
        title(d, 'ഏക വഴി: അട്ടപ്പാടി ചുരം', '25 വർഷമായി മാറ്റമില്ല')
        return img
    if SCENE == 'bend':
        z = ease(t / 1.6)
        cam = Cam(lerp(76.56, 76.505, z), lerp(11.045, 11.038, z), lerp(0.42 if not V else 0.30, 0.09 if not V else 0.07, z))
        img, d = base(cam)
        pts = [cam.px(*P[n]) for n in CHURAM]
        d.line(pts, fill=(255, 200, 60, 255), width=int(14 * S), joint='curve')
        for n in ['ആനമൂളി', 'മന്ദംപൊട്ടി']: label(d, cam.px(*P[n]), n, 36, anchor='r')
        x, y = cam.px(76.505, 11.038)
        if t > 1.4:
            ph = (t - 1.4) % 1.0
            r = (30 + 90 * ph) * S
            d.ellipse([x - r, y - r, x + r, y + r], outline=RED + (int(255 * (1 - ph)),), width=int(8 * S))
            r2 = 34 * S
            d.line([(x - r2, y - r2), (x + r2, y + r2)], fill=RED, width=int(14 * S)); d.line([(x - r2, y + r2), (x + r2, y - r2)], fill=RED, width=int(14 * S))
        if t > 2.0: label(d, (x + 50 * S, y - 60 * S) if not V else (x - 330 * S, y + 120 * S), 'പത്താം വളവ്: സ്ലാബ് തകർന്ന് ഗർത്തം', 40, (255, 215, 215), dot=False)
        if t > 3.2: label(d, (x + 50 * S, y + 30 * S) if not V else (x - 330 * S, y + 200 * S), 'ചരക്കുവാഹനങ്ങൾക്ക് നിരോധനം', 40, (255, 215, 215), dot=False)
        title(d, 'പത്താം വളവിൽ ഗർത്തം', 'സെപ്റ്റംബർ 2026')
        return img
    if SCENE == 'ambulance':
        z = ease(t / 1.5)
        cam = Cam(lerp(76.6, 76.42, z), lerp(11.05, 10.78, z), lerp(0.5, 1.05, z) if not V else lerp(0.36, 0.75, z))
        img, d = base(cam)
        route = [P['കോട്ടത്തറ'], P['അഗളി'], P['മുക്കാലി'], P['മന്ദംപൊട്ടി'], P['ആനമൂളി'], P['മണ്ണാർക്കാട്'], (76.35, 10.80), P['തൃശൂർ മെഡി. കോളേജ്']]
        pts = [cam.px(*p) for p in route]
        d.line(pts, fill=(255, 255, 255, 40), width=int(16 * S), joint='curve')
        # ambulance stops at Mandampotti between 2.5-4.5s
        prog = ease(t / 2.4) * 0.42 if t < 4.4 else 0.42 + ease((t - 4.4) / 2.0) * 0.58
        head = polyline(d, pts, prog, (255, 80, 80, 255), int(9 * S))
        blink = (255, 60, 60) if int(t * 4) % 2 else (60, 140, 255)
        d.ellipse([head[0] - 15 * S, head[1] - 15 * S, head[0] + 15 * S, head[1] + 15 * S], fill=blink, outline=WHITE, width=int(3 * S))
        for n in ['കോട്ടത്തറ', 'മന്ദംപൊട്ടി', 'തൃശൂർ മെഡി. കോളേജ്']:
            label(d, cam.px(*P[n]), n, 32, anchor='r' if (n == 'മന്ദംപൊട്ടി' or (V and n == 'കോട്ടത്തറ')) else 'l')
        if 2.3 < t:
            x, y = cam.px(*P['മന്ദംപൊട്ടി'])
            label(d, (x + 20 * S, y + 60 * S) if not V else (x - 10 * S, y + 120 * S), 'മരം വീണു: 1 മണിക്കൂർ കുരുക്ക്', 32, (255, 210, 210), dot=False, anchor='l' if not V else 'r')
        title(d, 'ചികിത്സയ്ക്ക് ചുരം കടക്കണം', 'കോട്ടത്തറ മുതൽ തൃശൂർ മെഡിക്കൽ കോളേജ് വരെ')
        return img
    if SCENE == 'land':
        cam = Cam(76.78 if not V else 76.80, 11.06, 0.75 if not V else 0.80)
        img, d = base(cam)
        a = cam.px(*ATT)
        glow_circle(img, a, 140 * S, TINT, 70)
        d = ImageDraw.Draw(img, 'RGBA')
        label(d, cam.px(76.50, 11.19), 'അട്ടപ്പാടി', 44, TINT, dot=False)
        label(d, cam.px(77.02, 10.93), 'തമിഴ്നാട്', 36, dot=False)
        for k, (s0, e0) in enumerate([((77.08, 11.20), (76.71, 11.14)), ((77.12, 11.08), (76.73, 11.09)), ((77.08, 10.97), (76.71, 11.04))]):
            tt = ease((t - 0.6 - k * 0.35) / 1.4)
            if tt > 0: arrow(d, cam.px(*s0), cam.px(*e0), tt, (255, 190, 70, 255), int(8 * S))
        for k, (dx, dy) in enumerate([(-0.07, 0.03), (0.04, -0.04), (-0.02, -0.07), (0.08, 0.05)]):
            if t > 2.2 + k * 0.3:
                x, y = cam.px(ATT[0] + dx, ATT[1] + dy)
                f = mj(26 * S); tw = d.textlength('വിറ്റു', font=f)
                d.rounded_rectangle([x - tw / 2 - 12 * S, y - 20 * S, x + tw / 2 + 12 * S, y + 22 * S], int(6 * S), fill=RED + (230,))
                d.text((x, y + 2 * S), 'വിറ്റു', font=f, fill=WHITE, anchor='mm')
        title(d, 'ഭൂമി വാങ്ങിക്കൂട്ടൽ, റിസോർട്ട് മാഫിയ', 'ആരോപണം')
        return img
    raise SystemExit('scene?')

N = int(DUR * FPS)
p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
for i in range(N):
    p.stdin.write(frame(i).convert('RGB').tobytes())
p.stdin.close(); p.wait()
print('ok', OUT)
