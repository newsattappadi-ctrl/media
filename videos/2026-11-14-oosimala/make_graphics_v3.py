"""v3 graphics — News Attappadi brand colours only (logo navy/blue/grey/white). Run: python3 make_graphics_v3.py <chrome>"""
import subprocess, pathlib, sys
from PIL import Image, ImageDraw, ImageEnhance
D = pathlib.Path(__file__).resolve().parent
CHROME = sys.argv[1] if len(sys.argv) > 1 else 'google-chrome'
OV = D / 'ov3'; OV.mkdir(exist_ok=True)
FT = (D / 'fonts').as_uri(); LOGO = (D / 'logo.jpg').as_uri()
NAVY, BLUE, GREY, TINT = '#06364a', '#0a7abf', '#4d4d4d', '#7cc8ff'

CSS = f'''
@font-face{{font-family:MJ;font-weight:400;src:url({FT}/manjari-malayalam-400-normal.woff2)}}
@font-face{{font-family:MJ;font-weight:700;src:url({FT}/manjari-malayalam-700-normal.woff2)}}
@font-face{{font-family:BC;font-weight:600;src:url({FT}/barlow-condensed-latin-600-normal.woff2)}}
@font-face{{font-family:BC;font-weight:700;src:url({FT}/barlow-condensed-latin-700-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{background:transparent}}
body{{position:relative;overflow:hidden;font-family:BC,MJ,sans-serif;color:#fff}}
em{{font-style:normal;color:{TINT}}}
.sh{{box-shadow:0 8px 30px rgba(0,0,0,.55)}} .ts{{text-shadow:0 2px 10px rgba(0,0,0,.8)}}
.bug{{display:flex;align-items:center;gap:14px}}
.bug img{{border-radius:50%;border:3px solid #fff;background:#fff;object-fit:cover}}
.bug b{{display:block;font:700 40px/.95 BC;letter-spacing:1px}} .bug span{{display:block;font:600 24px/1 BC;color:#bfe3fb;letter-spacing:3px}}
.strap{{display:flex;align-items:stretch}}
.strap .k{{background:{BLUE};font:700 34px/1 MJ;padding:22px 26px 14px;display:flex;align-items:center;white-space:nowrap}}
.strap .t{{background:#fff;color:{NAVY};font:700 40px/1.3 MJ;padding:18px 28px 10px;flex:1;border-bottom:8px solid {NAVY}}}
.cap{{display:inline-block;background:rgba(6,54,74,.93);border-left:12px solid {BLUE};font:700 50px/1.42 MJ;padding:22px 32px 12px}}
.lt .n{{display:inline-block;background:{BLUE};font:700 48px/1 MJ;padding:18px 30px 10px}}
.lt .r{{display:inline-block;background:{NAVY};font:700 34px/1 MJ;padding:16px 30px 10px;border-bottom:6px solid {BLUE}}}
'''

def shot(name, w, h, body):
    f = OV / f'_{name}.html'
    f.write_text(f'<!DOCTYPE html><html lang="ml"><head><meta charset="utf-8"><style>{CSS}</style></head><body style="width:{w}px;height:{h}px">{body}</body></html>', encoding='utf-8')
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--default-background-color=00000000',
                    f'--window-size={w},{h}', '--virtual-time-budget=3000', f'--screenshot={OV}/{name}.png', f.as_uri()], capture_output=True)
    f.unlink()

STRAP_K = 'അട്ടപ്പാടി'
STRAP_T = 'ഊശിമലയിൽ വൻതോതിൽ അനധികൃത ഖനനമെന്ന് പരാതി'
H1 = 'അട്ടപ്പാടിയിൽ വൻതോതിൽ<br>അനധികൃത ഖനനം'
H2 = 'പരിസ്ഥിതിക്ക് വൻ ആഘാതമുണ്ടാകുമെന്ന് നിരീക്ഷണം'
CREDIT = 'ദൃശ്യങ്ങൾ: കുമാർ അട്ടപ്പാടി'
CAPS = {
 'm1': 'ഊശിമലയിൽ <em>വൻതോതിൽ അനധികൃത ഖനനം</em>',
 'm2': 'ഭൂമാഫിയ <em>റോഡ് വെട്ടുന്നു</em>, <em>മണ്ണും കല്ലും</em> ഖനനം ചെയ്യുന്നുവെന്ന് പരാതി',
 'p1': 'ഭവാനിപ്പുഴയുടെ കരയിൽ, <em>45 ഡിഗ്രിയിലേറെ ചരിവ്</em>',
 'p2': '<em>ഇടിച്ചിൽ ഭീഷണി</em>യുള്ള പ്രദേശം',
 'p3': 'മലയുടെ <em>അടിവാരം തുരന്ന്</em> കരിങ്കല്ല് പൊട്ടിക്കുന്നു',
 'p4': 'രാത്രി: <em>പടക്കം പൊട്ടിച്ച്</em> പാറ തകർക്കുന്നു',
 'p5': 'പകൽ: കല്ല് <em>ടിപ്പർ ലോറികളിൽ</em> കടത്തുന്നു',
 'p6': 'പലയിടത്തും <em>ഭൂമാഫിയ ഭൂമി കൈയേറുന്നു</em> എന്നും പരാതി',
 'p7': '<em>ഭൂമാഫിയ കൈയേറ്റവും അനധികൃത ക്വാറിയും</em> വ്യാപകം',
 'bite': 'അട്ടപ്പാടിയിൽ വ്യാപകമായി <em>ഭൂമാഫിയ കൈയേറ്റവും അനധികൃത ക്വാറിയും</em>',
 'q1': 'ഖനനം തുടർന്നാൽ <em>മണ്ണിടിച്ചിൽ, പരിസ്ഥിതി നാശം</em>: ആശങ്ക',
 'q2': 'ഒറ്റപ്പെട്ട പ്രദേശം; <em>പുറംലോകം അറിഞ്ഞില്ല</em>',
 'q3': 'റവന്യൂ, പൊലീസ്, വനം വകുപ്പുകൾ <em>മൗനം പാലിക്കുന്നുവെന്ന്</em> ആരോപണം',
}

for o, (W, H) in {'v': (1080, 1920), 'h': (1920, 1080)}.items():
    v = o == 'v'
    grad = (f'<div style="position:absolute;left:0;right:0;top:0;height:{420 if v else 240}px;background:linear-gradient(rgba(6,54,74,.85),rgba(6,54,74,0))"></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;height:{820 if v else 420}px;background:linear-gradient(rgba(6,54,74,0),rgba(6,54,74,.75))"></div>')
    bug = (f'<div class="bug ts" style="position:absolute;left:{56 if v else 48}px;top:{70 if v else 36}px"><img src="{LOGO}" style="width:{88 if v else 80}px;height:{88 if v else 80}px"><div><b>NEWS</b><span>ATTAPPADI</span></div></div>')
    sb = 330 if v else 34  # strap bottom
    strap = (f'<div class="strap sh" style="position:absolute;left:{0 if v else 48}px;right:{0 if v else 48}px;bottom:{sb}px">'
             f'<div class="k">{STRAP_K}</div><div class="t" style="{"font-size:38px" if v else ""}">{STRAP_T}</div></div>')
    for kind, note in (('top', CREDIT), ('map', 'Map: Esri, Maxar · ഏകദേശ സ്ഥാനം')):
        meta = (f'<div class="ts" style="position:absolute;{"left:56px;top:178px" if v else "right:48px;top:44px"};font:700 26px/1.2 MJ;opacity:.95">{note}</div>'
                f'<div class="ts" style="position:absolute;{"right:56px;top:96px" if v else "right:48px;top:84px"};font:700 30px/1 BC">@newsattappadi</div>')
        shot(f'{o}_{kind}', W, H, grad + bug + meta + strap)
    # opening headline card (full frame, slides in)
    hs = 1 if v else 1
    shot(f'{o}_head1', W, H, f'''<div style="position:absolute;left:{56 if v else 120}px;right:{56 if v else 120}px;top:{620 if v else 250}px">
<div style="display:inline-block;background:{BLUE};font:700 {40 if v else 38}px/1 MJ;padding:18px 28px 10px">പ്രധാന വാർത്ത</div>
<div class="sh" style="background:{NAVY};border-left:16px solid {BLUE};padding:34px 44px 22px;font:700 {86 if v else 92}px/1.28 MJ">{H1}</div></div>''')
    shot(f'{o}_head2', W, H, f'''<div style="position:absolute;left:{56 if v else 120}px;right:{56 if v else 120}px;top:{1080 if v else 610}px">
<div class="sh" style="display:inline-block;background:#fff;color:{NAVY};border-left:16px solid {GREY};padding:24px 36px 14px;font:700 {50 if v else 52}px/1.35 MJ">{H2}</div></div>''')
    for k, t in CAPS.items():
        shot(f'{o}_cap_{k}', W, 340 if v else 230, f'<div class="ts" style="position:absolute;left:{40 if v else 48}px;right:{40 if v else 520}px;bottom:0"><div class="cap sh">{t}</div></div>')
    shot(f'{o}_lt', W, 200, '<div class="lt" style="position:absolute;left:48px;bottom:0"><div class="n sh">പ്രതാപ്</div><br><div class="r sh">സാമൂഹിക പ്രവർത്തകൻ</div></div>')
    s = 1 if v else .78
    shot(f'{o}_end', W, H, f'''<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 40%,#0b4a63,{NAVY} 70%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{38*s}px">
<img src="{LOGO}" style="width:{340*s}px;height:{340*s}px;border-radius:50%;border:8px solid #fff;background:#fff;object-fit:cover">
<div style="font:700 {100*s}px/1 BC;letter-spacing:2px">NEWS ATTAPPADI</div>
<div style="font:700 {58*s}px/1.3 MJ;color:{TINT}">വാർത്തകൾ വിശദമായി</div>
<div style="font:700 {58*s}px/1 BC;background:{BLUE};padding:{18*s}px {44*s}px {12*s}px;border-radius:{50*s}px">Follow @newsattappadi</div></div>''')

# ---- map scenes, brand-blue pins ----
PINS = {
 'kerala': [('അട്ടപ്പാടി', 1287, 941, True, 'R', -40), ('പാലക്കാട്', 1291, 1059, False, 'R', 10), ('കൊച്ചി', 1153, 1374, False, 'R', 0), ('കോഴിക്കോട്', 974, 885, False, 'L', 0)],
 'attappadi': [('ഊശിമല · നരസിമുക്ക്', 1235, 1191, True, 'L', -80), ('മുക്കാലി', 1076, 1245, False, 'L', 20), ('ഷോളയൂർ', 1331, 1155, False, 'R', -10), ('മണ്ണാർക്കാട്', 967, 1363, False, 'L', 0), ('പുതൂർ', 1171, 1259, False, 'R', 40)],
 'narasi': [('ഊശിമല · നരസിമുക്ക്', 1200, 1200, True, 'L', -80), ('അഗളി', 1452, 1207, False, 'R', 0)],
}
CENTER = {'kerala': (1287, 941), 'attappadi': (1200, 1210), 'narasi': (1290, 1200)}

def label_png(text, main):
    name = f'lbl_{abs(hash(text)) % 10**8}_{int(main)}'
    p = OV / f'{name}.png'
    if not p.exists():
        bg = BLUE if main else NAVY
        shot(name, 900, 120, f'<div style="position:absolute;left:0;top:20px;display:inline-block;background:{bg};color:#fff;font:700 {46 if main else 34}px/1 MJ;padding:16px 22px 8px;border:3px solid #fff;box-shadow:0 4px 16px rgba(0,0,0,.6)">{text}</div>')
    im = Image.open(p); return im.crop(im.getbbox())

for m, pins in PINS.items():
    base = Image.open(D / 'map' / f'{m}.jpg').convert('RGB')
    base = ImageEnhance.Color(base).enhance(1.1); base = ImageEnhance.Contrast(base).enhance(1.1)
    base = Image.blend(base, Image.new('RGB', base.size, (6, 54, 74)), .28)
    d = ImageDraw.Draw(base)
    for t, x, y, main, side, dy in pins:
        r = 22 if main else 13
        if main:
            for rr, a in ((72, 70), (50, 130)):
                ring = Image.new('RGBA', base.size, (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((x-rr, y-rr, x+rr, y+rr), outline=(10, 122, 191, a + 60), width=7)
                base.paste(ring, (0, 0), ring)
        d.ellipse((x-r, y-r, x+r, y+r), fill=(10, 122, 191) if main else (255, 255, 255), outline=(255, 255, 255) if main else (6, 54, 74), width=5)
        lb = label_png(t, main); lx = x + r + 14 if side == 'R' else x - r - 14 - lb.width; base.paste(lb, (lx, y - lb.height // 2 + dy), lb)
    cx, cy = CENTER[m]
    for o, (W, H) in {'v': (1242, 2208), 'h': (2208, 1242)}.items():
        x0 = min(max(cx - W // 2, 0), base.width - W); y0 = min(max(cy - H // 2, 0), base.height - H)
        base.crop((x0, y0, x0 + W, y0 + H)).save(OV / f'map_{o}_{m}.jpg', quality=92)
print('done', len(list(OV.glob('*'))))
