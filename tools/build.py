"""News Attappadi carousel builder.
Usage:  cd tools && npm install && python3 build.py content.json ../posts/YYYY-MM-DD
content.json: {"date_label":"12 NOV 2026","slides":[
  {"type":"cover","title":"..","kicker":"..","summary":"..","source":"..",
   "photo":"../assets/library/pepper.jpg","credit":"Name / Wikimedia Commons (CC BY 4.0)","photo_tag":"ഫയൽ ചിത്രം","photo_pos":"center"},
  {"type":"weather","title":"..","photo":"..","credit":"..","weather":{"high":28,"low":19,"rain":10},"note":".."}  (single-slide weather post),
  {"type":"points","title":"..","points":["<strong>label:</strong> text", "..."]},
  {"type":"data","title":"..","weather":{"place":"അഗളി","high":28,"low":19,"rain":30},
   "prices_label":"വിപണി വില · നവംബർ 11","prices":[{"name":"ഏലയ്ക്ക","note":"ലേല ശരാശരി","value":"₹3,086"}]},
  {"type":"follow"}]}
Max 4 points per slide, each under ~110 characters. Text is Malayalam; <strong> and <b> allowed.
"""
import subprocess, pathlib, json, sys
D = pathlib.Path(__file__).resolve().parent
F = 'node_modules/@fontsource'
CSS = f'''
@font-face{{font-family:MJ;font-weight:400;src:url({F}/manjari/files/manjari-malayalam-400-normal.woff2) format("woff2")}}
@font-face{{font-family:MJ;font-weight:700;src:url({F}/manjari/files/manjari-malayalam-700-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:400;src:url({F}/barlow-condensed/files/barlow-condensed-latin-500-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:600;src:url({F}/barlow-condensed/files/barlow-condensed-latin-600-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:700;src:url({F}/barlow-condensed/files/barlow-condensed-latin-700-normal.woff2) format("woff2")}}
@font-face{{font-family:BC;font-weight:700;unicode-range:U+20B9;src:url({F}/barlow-condensed/files/barlow-condensed-latin-ext-700-normal.woff2) format("woff2")}}
:root{{--navy:#0f3a4d;--blue:#0a7abf;--grey:#4d4f50;--ink:#16242b}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:BC,MJ,sans-serif;color:var(--ink);position:relative;overflow:hidden;background:#f3f3f1}}
svg.paper{{position:absolute;inset:0;width:100%;height:100%}}
.wrap{{position:absolute;inset:0;padding:56px 64px 0}}
.date{{display:inline-block;border:4px solid var(--grey);border-radius:16px;padding:6px 22px 4px;font-weight:700;font-size:40px;color:var(--grey);letter-spacing:1px;background:#f6f6f4}}
.tag{{float:right;font-weight:700;font-size:40px;color:var(--blue);padding-top:10px}}
.head{{background:var(--navy);border-radius:22px;margin-top:26px;padding:38px 44px 30px}}
h1{{font-family:MJ;font-weight:700;font-size:70px;line-height:1.22;color:#fff;transform:scaleX(.86);transform-origin:left;width:116.3%}}
h2{{font-family:MJ;font-weight:700;font-size:58px;line-height:1.2;color:#fff;transform:scaleX(.88);transform-origin:left;width:113.6%}}
.head p{{font-family:MJ;font-weight:700;font-size:33px;line-height:1.4;color:#6fc0ee;margin-top:14px;transform:scaleX(.9);transform-origin:left;width:111%}}
.sub{{font-size:38px;line-height:1.5;margin-top:34px}}
.sub b,.pt b{{font-family:BC;font-size:1.2em;color:var(--navy);line-height:1}}
.src{{font-size:24px;color:#6c7275;margin-top:12px}}
.swipe{{position:absolute;right:64px;bottom:190px;background:var(--blue);color:#fff;font-family:MJ;font-weight:700;font-size:32px;border-radius:40px;padding:14px 30px 9px}}
.pts{{margin-top:40px}}
.pt{{display:flex;gap:26px;align-items:flex-start;font-size:38px;line-height:1.42;padding:24px 0 20px;border-bottom:2px solid #c9cdce}}
.pt:last-child{{border:0}}
.pt i{{flex:none;width:64px;height:64px;border-radius:16px;background:var(--navy);color:#fff;font:700 40px/64px BC;text-align:center;font-style:normal;margin-top:2px}}
.pt strong{{font-family:MJ;font-weight:700;color:var(--navy)}}
.grid{{display:flex;flex-direction:column;gap:56px;margin-top:64px}}
.card{{border:4px solid var(--grey);border-radius:24px;padding:0 36px 28px;background:rgba(255,255,255,.45)}}
.pill{{display:inline-block;background:var(--navy);color:#fff;font-weight:700;font-size:32px;border-radius:14px;padding:10px 24px 6px;margin-top:-28px}}
.pill,.line,.note,.row span{{font-family:BC,MJ}}
.wx{{display:flex;align-items:flex-end;justify-content:space-between}}
.big{{font-weight:700;font-size:150px;line-height:1;color:var(--navy);margin-top:18px}}
.big small{{font-size:80px;font-weight:600;color:var(--blue)}}
.line{{font-size:36px;padding-bottom:16px;text-align:right;line-height:1.4}}
.row{{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:38px;padding:18px 0 12px;border-bottom:2px solid #c9cdce}}
.row:first-of-type{{margin-top:12px}}
.row b{{font-family:BC;font-size:64px;font-weight:700;color:var(--navy);line-height:1}}
.row em{{font-style:normal;font-weight:400;font-size:26px;color:#6c7275;display:block}}
.note{{font-size:24px;color:#6c7275;margin-top:12px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:140px;border-top:3px solid var(--navy);display:flex;align-items:center;justify-content:space-between;padding:0 64px}}
.logo{{display:flex;align-items:center;gap:18px}}
.logo img{{height:108px;mix-blend-mode:multiply}}
.logo .bar{{width:4px;height:84px;background:var(--navy)}}
.logo .nm{{font-weight:700;font-size:54px;line-height:.82;color:var(--grey)}}
.logo .nm span{{display:block;font-size:27px;font-weight:600;letter-spacing:1.5px;margin-top:6px}}
.contact{{text-align:right;font-weight:600;font-size:28px;line-height:1.25}}
.contact b{{font-size:34px;color:var(--navy)}}
'''
PAPER = '''<svg class="paper" xmlns="http://www.w3.org/2000/svg"><filter id="p" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.006 0.009" numOctaves="4" seed="11" result="n"/>
<feDiffuseLighting in="n" lighting-color="#ffffff" surfaceScale="9" diffuseConstant="1.05"><feDistantLight azimuth="225" elevation="62"/></feDiffuseLighting>
</filter><rect width="100%" height="100%" filter="url(#p)"/></svg>'''
FOOT = '''<div class="foot"><div class="logo"><img src="brand/logo.jpg"><div class="bar"></div><div class="nm">NEWS<span>ATTAPPADI</span></div></div>
<div class="contact"><b>@newsattappadi</b><br>newsattappadi@gmail.com</div></div>'''


CSS += """
.photo{position:relative;margin-top:22px;height:500px;border-radius:22px;overflow:hidden;border:4px solid var(--grey)}
.photo img{width:100%;height:100%;object-fit:cover;display:block}
.pcredit{position:absolute;right:0;bottom:0;background:rgba(15,58,77,.82);color:#fff;font-family:BC,MJ;font-size:20px;padding:6px 14px 3px;border-top-left-radius:12px}
.ptag{position:absolute;left:0;top:0;background:var(--blue);color:#fff;font-family:MJ;font-weight:700;font-size:24px;padding:9px 18px 5px;border-bottom-right-radius:14px}
.head.hp{margin-top:20px;padding:28px 40px 22px}
h1.hsm{font-size:58px;line-height:1.2}
.head.hp p{font-size:30px;margin-top:8px}
.sub.ssm{font-size:33px;line-height:1.45;margin-top:22px}
.wxrow{display:flex;align-items:flex-end;justify-content:space-between;margin-top:30px;padding:0 10px}
.wxrow .big{font-size:190px}
.wxrow .big small{font-size:100px}
.wxrow .line{font-size:42px;padding-bottom:26px}
h1,h2,.head p,.pt strong{font-family:BC,MJ}
.follow{text-align:center;margin-top:150px}
.follow img{height:420px;mix-blend-mode:multiply}
.follow .f1{font-family:MJ;font-weight:700;font-size:64px;color:var(--navy);margin-top:30px;line-height:1.3}
.follow .f2{display:inline-block;margin-top:34px;background:var(--navy);color:#fff;font:700 62px BC;border-radius:22px;padding:16px 44px 12px}
.follow .f3{font-family:MJ;font-size:34px;margin-top:34px;color:var(--grey)}
"""

def pts(items):
    return '<div class="pts">' + ''.join(f'<div class="pt"><i>{n}</i><div>{t}</div></div>' for n, t in enumerate(items, 1)) + '</div>'

def render(s):
    t = s['type']
    if t == 'cover':
        if s.get('photo'):
            tagp = f'<span class="ptag">{s["photo_tag"]}</span>' if s.get('photo_tag') else ''
            return (f'<div class="photo"><img src="{s["photo"]}" style="object-position:{s.get("photo_pos","center")}">{tagp}'
                    f'<span class="pcredit">ചിത്രം: {s["credit"]}</span></div>'
                    f'<div class="head hp"><h1 class="hsm">{s["title"]}</h1><p>{s.get("kicker","")}</p></div>'
                    f'<div class="sub ssm">{s["summary"]}</div><div class="src">അവലംബം: {s["source"]}</div>'
                    + ('' if s.get('single') else '<div class="swipe">വിശദാംശങ്ങൾ ➜</div>'))
        return (f'<div class="head"><h1>{s["title"]}</h1><p>{s.get("kicker","")}</p></div>'
                f'<div class="sub">{s["summary"]}</div><div class="src">അവലംബം: {s["source"]}</div>'
                '<div class="swipe">വിശദാംശങ്ങൾ ➜</div>')
    if t == 'weather':
        w = s['weather']
        return (f'<div class="photo"><img src="{s["photo"]}" style="object-position:{s.get("photo_pos","center")}">'
                f'<span class="pcredit">ചിത്രം: {s["credit"]}</span></div>'
                f'<div class="head hp"><h2>{s["title"]}</h2></div>'
                f'<div class="wxrow"><div class="big">{w["high"]}° <small>/ {w["low"]}°</small></div>'
                f'<div class="line">കൂടിയത് / കുറഞ്ഞത്<br>മഴ സാധ്യത {w["rain"]}%</div></div>'
                f'<div class="src">{s.get("note","")}</div>')
    if t == 'points':
        return f'<div class="head"><h2>{s["title"]}</h2></div>' + pts(s['points'])
    if t == 'data':
        w = s['weather']
        rows = ''.join(f'<div class="row"><span>{p["name"]}<em>{p.get("note","")}</em></span><b>{p["value"]}</b></div>' for p in s['prices'])
        return (f'<div class="head"><h2>{s["title"]}</h2></div><div class="grid"><div class="card">'
                f'<span class="pill">ഇന്നത്തെ കാലാവസ്ഥ · {w["place"]}</span><div class="wx"><div class="big">{w["high"]}° <small>/ {w["low"]}°</small></div>'
                f'<div class="line">കൂടിയത് / കുറഞ്ഞത്<br>മഴ സാധ്യത {w["rain"]}%</div></div></div>'
                f'<div class="card"><span class="pill">{s["prices_label"]}</span>{rows}<div class="note">വില കിലോയ്ക്ക്</div></div></div>')
    if t == 'follow':
        return ('<div class="follow"><img src="brand/logo.jpg"><div class="f1">അട്ടപ്പാടിയുടെ വാർത്തകൾ<br>ആദ്യം അറിയാൻ</div>'
                '<div class="f2">Follow @newsattappadi</div><div class="f3">വാർത്ത · കാലാവസ്ഥ · വിപണി വില</div></div>')
    raise SystemExit('unknown slide type ' + t)

c = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
out = pathlib.Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
n = len(c['slides'])
for i, s in enumerate(c['slides'], 1):
    tag = '' if n == 1 else f'<span class="tag">{i}/{n}</span>'
    html = f'<!DOCTYPE html><html lang="ml"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{PAPER}<div class="wrap"><span class="date">{c["date_label"]}</span>{tag}{render(s)}</div>{FOOT}</body></html>'
    h = D / f'_slide{i}.html'; h.write_text(html, encoding='utf-8')
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1350', '--virtual-time-budget=3000', f'--screenshot={out}/slide{i}.png', f'file://{h}'], capture_output=True)
    h.unlink()
print('built', n, 'slides in', out)
