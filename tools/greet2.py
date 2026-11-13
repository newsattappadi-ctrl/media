"""News Attappadi greeting posters, photo style (single page, 1080x1350).
Usage: cd tools && npm install && python3 greet2.py greetings2.json ../posts/greetings
greetings2.json: list of {"date","slug","day":"14","month":"NOV","year":"2026","kicker","title","story",
  "photo":"../assets/greetings/children.jpg","credit":"Name / Pexels","pos":"center","accent":"#e9c46a"}
"""
import json, pathlib, subprocess, sys
D = pathlib.Path(__file__).resolve().parent
F = 'node_modules/@fontsource'
CSS = f'''
@font-face{{font-family:NS;font-weight:400;src:url({F}/noto-serif-malayalam/files/noto-serif-malayalam-malayalam-400-normal.woff2) format("woff2")}}
@font-face{{font-family:NS;font-weight:600;src:url({F}/noto-serif-malayalam/files/noto-serif-malayalam-malayalam-600-normal.woff2) format("woff2")}}
@font-face{{font-family:NS;font-weight:700;src:url({F}/noto-serif-malayalam/files/noto-serif-malayalam-malayalam-700-normal.woff2) format("woff2")}}
@font-face{{font-family:MJ;font-weight:400;src:url({F}/manjari/files/manjari-malayalam-400-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:400;src:url({F}/barlow-condensed/files/barlow-condensed-latin-500-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:600;src:url({F}/barlow-condensed/files/barlow-condensed-latin-600-normal.woff2) format("woff2")}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#0b1e27;color:#fff;font-family:BC,MJ,sans-serif}}
.ph{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.sh{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,22,30,.55) 0%,rgba(6,22,30,0) 22%,rgba(6,22,30,0) 38%,rgba(6,22,30,.78) 66%,rgba(6,22,30,.96) 100%)}}
.frame{{position:absolute;inset:34px;border:1.5px solid rgba(255,255,255,.55);border-radius:6px}}
.date{{position:absolute;left:78px;top:74px;display:flex;align-items:center;gap:16px;font-weight:600;letter-spacing:6px;font-size:30px}}
.date b{{font-size:74px;font-weight:600;letter-spacing:0;line-height:.8;color:var(--ac)}}
.date span{{display:block;line-height:1.25}}
.brand{{position:absolute;right:78px;top:70px;display:flex;align-items:center;gap:14px;font-weight:600;font-size:24px;letter-spacing:5px;text-align:right;line-height:1.3}}
.brand .lg{{width:84px;height:84px;border-radius:50%;background:#fff;overflow:hidden;display:flex;align-items:center;justify-content:center}}
.brand .lg img{{width:96px;height:96px}}
.txt{{position:absolute;left:96px;right:96px;bottom:150px;text-align:center}}
.kick{{font-family:BC,MJ;font-size:30px;letter-spacing:3px;color:var(--ac);margin-bottom:18px}}
h1{{font-family:NS,BC;font-weight:600;font-size:var(--fs);line-height:1.32;text-shadow:0 2px 24px rgba(0,0,0,.45)}}
.orn{{display:flex;align-items:center;justify-content:center;gap:16px;margin:26px 0 24px}}
.orn i{{width:120px;height:1.5px;background:var(--ac)}}
.orn u{{width:10px;height:10px;background:var(--ac);transform:rotate(45deg)}}
.story{{font-family:BC,MJ;font-size:34px;line-height:1.6;color:#e6eef1}}
.bot{{position:absolute;left:78px;right:78px;bottom:66px;display:flex;justify-content:space-between;font-size:22px;letter-spacing:3px;color:rgba(255,255,255,.75)}}
.bot b{{font-weight:600;color:#fff}}
'''
items = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
out = pathlib.Path(sys.argv[2]).resolve()
for g in items:
    n = len(g['title'])
    fs = 92 if n <= 16 else (78 if n <= 24 else 66)
    w = max(len(x) for x in g['title'].split())
    if w >= 14: fs = min(fs, 70)
    elif w >= 11: fs = min(fs, 80)
    kick = f'<div class="kick">{g["kicker"]}</div>' if g.get('kicker') else ''
    html = (f'<!DOCTYPE html><html lang="ml"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body style="--ac:{g.get("accent","#e9c46a")};--fs:{fs}px"><img class="ph" src="{g["photo"]}" style="object-position:{g.get("pos","center")}">'
            '<div class="sh"></div><div class="frame"></div>'
            f'<div class="date"><b>{g["day"]}</b><span>{g["month"]}<br>{g["year"]}</span></div>'
            '<div class="brand"><div>NEWS<br>ATTAPPADI</div><div class="lg"><img src="brand/logo.jpg"></div></div>'
            f'<div class="txt">{kick}<h1>{g["title"]}</h1><div class="orn"><i></i><u></u><i></i></div><div class="story">{g["story"]}</div></div>'
            f'<div class="bot"><b>@NEWSATTAPPADI</b><span>PHOTO: {g["credit"]}</span></div></body></html>')
    d = out / f'{g["date"]}-{g["slug"]}'; d.mkdir(parents=True, exist_ok=True)
    h = D / '_greet.html'; h.write_text(html, encoding='utf-8')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1350', '--virtual-time-budget=3000', f'--screenshot={d}/slide1.png', f'file://{h}'], capture_output=True)
    h.unlink()
print('built', len(items))
