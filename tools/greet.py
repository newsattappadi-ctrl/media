"""News Attappadi greeting poster builder (single page, 1080x1350).
Usage: cd tools && npm install && python3 greet.py greetings.json ../posts/greetings
greetings.json: list of {"date":"2026-11-14","slug":"children","pill":"നവംബർ 14","kicker":"..","title":"..","story":"..","icons":["balloon","teddy-bear","kite"],"accent":"#f2b705"}
icons are names from @iconify-json/fluent-emoji-flat (MIT); "flag-india" is drawn in CSS.
"""
import json, pathlib, subprocess, sys
D = pathlib.Path(__file__).resolve().parent
F = 'node_modules/@fontsource'
IC = json.load(open(D / 'node_modules/@iconify-json/fluent-emoji-flat/icons.json'))['icons']

def icon(name, size):
    if name == 'flag-india':
        return (f'<div style="width:{size}px;height:{int(size*.68)}px;border-radius:14px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.35);display:flex;flex-direction:column">'
                '<div style="flex:1;background:#ff9933"></div><div style="flex:1;background:#fff;display:flex;align-items:center;justify-content:center">'
                f'<div style="width:{int(size*.17)}px;height:{int(size*.17)}px;border-radius:50%;border:{max(3,int(size*.014))}px solid #000080;background:repeating-conic-gradient(#000080 0 2deg,transparent 2deg 15deg)"></div></div>'
                '<div style="flex:1;background:#138808"></div></div>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="{size}" height="{size}">{IC[name]["body"]}</svg>'

CSS = f'''
@font-face{{font-family:MJ;font-weight:400;src:url({F}/manjari/files/manjari-malayalam-400-normal.woff2) format("woff2")}}
@font-face{{font-family:MJ;font-weight:700;src:url({F}/manjari/files/manjari-malayalam-700-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:400;src:url({F}/barlow-condensed/files/barlow-condensed-latin-500-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:600;src:url({F}/barlow-condensed/files/barlow-condensed-latin-600-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:700;src:url({F}/barlow-condensed/files/barlow-condensed-latin-700-normal.woff2) format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:BC,MJ,sans-serif;color:#fff;background:radial-gradient(circle at 50% 30%,#1f6a89 0%,#0f3a4d 46%,#08232f 100%)}}
.ring{{position:absolute;left:50%;top:372px;border-radius:50%;transform:translate(-50%,-50%);border:3px solid rgba(255,255,255,.13)}}
.r1{{width:560px;height:560px;background:rgba(255,255,255,.06)}}
.r2{{width:720px;height:720px;border-style:dashed;border-color:rgba(255,255,255,.12)}}
.r3{{width:900px;height:900px;border-color:rgba(255,255,255,.06)}}
.pill{{position:absolute;left:64px;top:56px;background:var(--ac);color:#0f3a4d;font-weight:700;font-size:38px;border-radius:16px;padding:10px 24px 5px}}
.main{{position:absolute;left:50%;top:372px;transform:translate(-50%,-50%);filter:drop-shadow(0 18px 30px rgba(0,0,0,.35))}}
.s1{{position:absolute;left:92px;top:470px;transform:rotate(-14deg);filter:drop-shadow(0 10px 18px rgba(0,0,0,.3))}}
.s2{{position:absolute;right:92px;top:180px;transform:rotate(12deg);filter:drop-shadow(0 10px 18px rgba(0,0,0,.3))}}
.txt{{position:absolute;left:64px;right:64px;top:690px;text-align:center}}
.kick{{display:inline-block;font-weight:700;font-size:34px;color:var(--ac);letter-spacing:.5px;margin-bottom:14px}}
h1{{font-family:BC,MJ;font-weight:700;font-size:var(--fs);line-height:1.2}}
.bar{{width:150px;height:8px;border-radius:4px;background:var(--ac);margin:22px auto 26px}}
.story{{font-size:37px;line-height:1.5;color:#d9e8ef;max-width:900px;margin:0 auto}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:140px;background:#f6f6f4;display:flex;align-items:center;justify-content:space-between;padding:0 64px;color:#16242b}}
.logo{{display:flex;align-items:center;gap:18px}}
.logo img{{height:108px;mix-blend-mode:multiply}}
.logo .b{{width:4px;height:84px;background:#0f3a4d}}
.logo .nm{{font-weight:700;font-size:54px;line-height:.82;color:#4d4f50}}
.logo .nm span{{display:block;font-size:27px;font-weight:600;letter-spacing:1.5px;margin-top:6px}}
.contact{{text-align:right;font-weight:600;font-size:28px;line-height:1.25}}
.contact b{{font-size:34px;color:#0f3a4d}}
'''
items = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
out = pathlib.Path(sys.argv[2]).resolve()
for g in items:
    fs = 104 if len(g['title']) <= 16 else (88 if len(g['title']) <= 24 else 74)
    kick = f'<div class="kick">{g["kicker"]}</div><br>' if g.get('kicker') else ''
    m, a, b = g['icons']
    html = (f'<!DOCTYPE html><html lang="ml"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body style="--ac:{g.get("accent","#f2b705")};--fs:{fs}px"><div class="ring r3"></div><div class="ring r2"></div><div class="ring r1"></div>'
            f'<div class="pill">{g["pill"]}</div><div class="s1">{icon(a,150)}</div><div class="s2">{icon(b,150)}</div><div class="main">{icon(m,380)}</div>'
            f'<div class="txt">{kick}<h1>{g["title"]}</h1><div class="bar"></div><div class="story">{g["story"]}</div></div>'
            '<div class="foot"><div class="logo"><img src="brand/logo.jpg"><div class="b"></div><div class="nm">NEWS<span>ATTAPPADI</span></div></div>'
            '<div class="contact"><b>@newsattappadi</b><br>newsattappadi@gmail.com</div></div></body></html>')
    d = out / f'{g["date"]}-{g["slug"]}'; d.mkdir(parents=True, exist_ok=True)
    h = D / '_greet.html'; h.write_text(html, encoding='utf-8')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1350', '--virtual-time-budget=3000', f'--screenshot={d}/slide1.png', f'file://{h}'], capture_output=True)
    h.unlink()
print('built', len(items))
