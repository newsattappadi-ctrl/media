"""Graphics for the Oosimala news video (News Attappadi). Run: python3 make_graphics.py <chrome>"""
import subprocess, pathlib, sys
from PIL import Image, ImageDraw, ImageFilter
D = pathlib.Path(__file__).resolve().parent
CHROME = sys.argv[1] if len(sys.argv) > 1 else 'google-chrome'
OV = D / 'ov'; OV.mkdir(exist_ok=True)
FT = (D / 'fonts').as_uri(); LOGO = (D / 'logo.jpg').as_uri()
GOLD = '#ffc83d'

CSS = f'''
@font-face{{font-family:MJ;font-weight:400;src:url({FT}/manjari-malayalam-400-normal.woff2)}}
@font-face{{font-family:MJ;font-weight:700;src:url({FT}/manjari-malayalam-700-normal.woff2)}}
@font-face{{font-family:BC;font-weight:600;src:url({FT}/barlow-condensed-latin-600-normal.woff2)}}
@font-face{{font-family:BC;font-weight:700;src:url({FT}/barlow-condensed-latin-700-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{background:transparent}}
body{{position:relative;overflow:hidden;font-family:BC,MJ,sans-serif;color:#fff}}
.sh{{text-shadow:0 3px 14px rgba(0,0,0,.75),0 1px 3px rgba(0,0,0,.9)}}
em{{font-style:normal;color:{GOLD}}}
.brand{{display:flex;align-items:center;gap:14px}}
.brand img{{border-radius:50%;border:3px solid #fff;background:#fff;object-fit:cover}}
.brand b{{display:block;font:700 40px/.95 BC;letter-spacing:1px}} .brand span{{display:block;font:600 24px/1 BC;color:#9fd6f5;letter-spacing:3px}}
.title{{font:700 62px/1.28 MJ}} .subt{{font:700 34px/1.3 MJ;color:{GOLD};margin-top:10px;letter-spacing:.5px}}
.cap{{font:700 54px/1.42 MJ;text-align:center}}
.lt .n{{display:inline-block;background:{GOLD};color:#10232c;font:700 46px/1 MJ;padding:16px 28px 8px;border-radius:10px 10px 0 0}}
.lt .r{{background:rgba(9,30,40,.92);font:700 34px/1 MJ;padding:16px 28px 10px;border-radius:0 10px 10px 10px;display:inline-block}}
.small{{font:700 26px/1 BC,MJ;opacity:.92}} .handle{{font:700 34px/1 BC}}
'''

def shot(name, w, h, body):
    f = OV / f'_{name}.html'
    f.write_text(f'<!DOCTYPE html><html lang="ml"><head><meta charset="utf-8"><style>{CSS}</style></head><body style="width:{w}px;height:{h}px">{body}</body></html>', encoding='utf-8')
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--default-background-color=00000000',
                    f'--window-size={w},{h}', '--virtual-time-budget=3000', f'--screenshot={OV}/{name}.png', f.as_uri()], capture_output=True)
    f.unlink()

TITLE = 'ഊശിമലയിൽ അനധികൃത ഖനനമെന്ന് പരാതി'
SUB = 'അഗളി · നരസിമുക്ക് · അട്ടപ്പാടി'
CREDIT = 'ദൃശ്യങ്ങൾ: കുമാർ അട്ടപ്പാടി'
CAPS = {
 'a1': 'അട്ടപ്പാടി, അഗളിക്കടുത്ത് <em>നരസിമുക്ക്</em>',
 'a2': 'ഇവിടെയാണ് <em>ഊശിമല</em>',
 'a3': 'ജൈവവൈവിധ്യം നിറഞ്ഞ മലയിൽ <em>അനധികൃത റോഡും കരിങ്കൽ ഖനനവും</em>',
 'a4': 'ഭവാനിപ്പുഴയുടെ കരയിൽ <em>സൂചിമുന</em> പോലെ ഒരു മല',
 'a5': '<em>45 ഡിഗ്രിയിലേറെ</em> ചരിവ്, <em>ഇടിച്ചിൽ ഭീഷണി</em>',
 'a6': 'രാത്രി: ആനയെ ഓടിക്കാനെന്ന പേരിൽ <em>പടക്കം പൊട്ടിച്ച് പാറ തകർക്കുന്നു</em>',
 'a7': 'പകൽ: യന്ത്രങ്ങൾ ഉപയോഗിച്ച് <em>കല്ല് ടിപ്പറുകളിൽ കടത്തുന്നു</em>',
 'bite': 'അട്ടപ്പാടിയിൽ വ്യാപകമായി <em>ഭൂമാഫിയ കൈയേറ്റവും അനധികൃത ക്വാറിയും</em>',
 'b1': 'ഒറ്റപ്പെട്ട പ്രദേശം; <em>പുറംലോകം അറിഞ്ഞില്ല</em>',
 'b2': 'റവന്യൂ, പൊലീസ്, വനം വകുപ്പുകൾ <em>മൗനം പാലിക്കുന്നുവെന്ന്</em> ആരോപണം',
}

for o, (W, H) in {'v': (1080, 1920), 'h': (1920, 1080)}.items():
    v = o == 'v'
    grad = (f'<div style="position:absolute;left:0;right:0;top:0;height:{620 if v else 330}px;background:linear-gradient(rgba(6,18,26,.88),rgba(6,18,26,0))"></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;height:{720 if v else 380}px;background:linear-gradient(rgba(6,18,26,0),rgba(6,18,26,.9))"></div>')
    logo = (f'<div class="brand sh" style="position:absolute;{"left:56px;top:70px" if v else "right:48px;top:40px"}"><img src="{LOGO}" style="width:{84 if v else 76}px;height:{84 if v else 76}px"><div><b>NEWS</b><span>ATTAPPADI</span></div></div>')
    title = (f'<div class="sh" style="position:absolute;left:56px;right:56px;top:{190 if v else 40}px;{"" if v else "right:420px"}"><div class="title" style="{"" if v else "font-size:54px"}">{TITLE}</div><div class="subt">{SUB}</div></div>')
    for kind, foot in (('top', CREDIT), ('map', 'Map: Esri, Maxar · ഏകദേശ സ്ഥാനം')):
        shot(f'{o}_{kind}', W, H, grad + logo + title +
             f'<div class="sh" style="position:absolute;left:56px;right:56px;bottom:{70 if v else 34}px;display:flex;justify-content:space-between;align-items:center"><span class="small">{foot}</span><span class="handle">@newsattappadi</span></div>')
    for k, t in CAPS.items():
        shot(f'{o}_cap_{k}', W, 360 if v else 220, f'<div class="cap sh" style="position:absolute;left:{60 if v else 260}px;right:{60 if v else 260}px;bottom:0;{"" if v else "font-size:48px"}">{t}</div>')
    shot(f'{o}_lt', W, 260, '<div class="lt sh" style="position:absolute;left:56px;bottom:0"><div class="n">പ്രതാപ്</div><br><div class="r">സാമൂഹിക പ്രവർത്തകൻ</div></div>')
    s = 1 if v else .78
    shot(f'{o}_end', W, H, f'''<div style="position:absolute;inset:0;background:#0b2a38;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{38*s}px">
<img src="{LOGO}" style="width:{340*s}px;height:{340*s}px;border-radius:50%;border:8px solid #fff;background:#fff;object-fit:cover">
<div style="font:700 {100*s}px/1 BC;letter-spacing:2px">NEWS ATTAPPADI</div>
<div style="font:700 {56*s}px/1.3 MJ;color:{GOLD}">വാർത്തകൾ വിശദമായി</div>
<div style="font:700 {58*s}px/1 BC;background:#0a7abf;padding:{18*s}px {44*s}px {12*s}px;border-radius:{50*s}px">Follow @newsattappadi</div></div>''')

# ---- map scenes with pins (baked), 1.15x output size for slow zoom ----
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
        bg = GOLD if main else 'rgba(9,30,40,.9)'; fg = '#10232c' if main else '#fff'
        shot(name, 900, 120, f'<div style="position:absolute;left:0;top:20px;display:inline-block;background:{bg};color:{fg};font:700 {44 if main else 34}px/1 MJ;padding:16px 22px 8px;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,.6)">{text}</div>')
    im = Image.open(p); return im.crop(im.getbbox())

for m, pins in PINS.items():
    base = Image.open(D / 'map' / f'{m}.jpg').convert('RGB')
    from PIL import ImageEnhance
    base = ImageEnhance.Color(base).enhance(1.15); base = ImageEnhance.Contrast(base).enhance(1.1)
    dark = Image.new('RGB', base.size, (6, 18, 26)); base = Image.blend(base, dark, .25)
    d = ImageDraw.Draw(base)
    for t, x, y, main, side, dy in pins:
        r = 22 if main else 13
        if main:
            for rr, a in ((70, 60), (48, 110)):
                ring = Image.new('RGBA', base.size, (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((x-rr, y-rr, x+rr, y+rr), outline=(255, 200, 61, a), width=6)
                base.paste(ring, (0, 0), ring)
        d.ellipse((x-r, y-r, x+r, y+r), fill=(255, 200, 61) if main else (255, 255, 255), outline=(16, 35, 44), width=5)
        lb = label_png(t, main); lx = x + r + 14 if side == 'R' else x - r - 14 - lb.width; base.paste(lb, (lx, y - lb.height // 2 + dy), lb)
    cx, cy = CENTER[m]
    for o, (W, H) in {'v': (1242, 2208), 'h': (2208, 1242)}.items():
        x0 = min(max(cx - W // 2, 0), base.width - W); y0 = min(max(cy - H // 2, 0), base.height - H)
        base.crop((x0, y0, x0 + W, y0 + H)).save(OV / f'map_{o}_{m}.jpg', quality=92)
print('done', len(list(OV.glob('*'))))
