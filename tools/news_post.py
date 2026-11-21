# News Attappadi - "bold news" post template (stacked headline blocks + cut-out subject)
# Style reference: stacked white/blue headline boxes, big outline quote mark, dot grids,
# round logo top-right, summary + @newsattappadi at the bottom. Colours: logo palette only.
#
# Usage: python3 news_post.py post.json out.png
# post.json: {
#   "subject": "cutout.png"   (transparent PNG of the person/subject)  OR  "photo": "photo.jpg",
#   "kicker": "അഗളി",              small blue tag above the headline
#   "lines": ["ശിശുമരണം", "രാഷ്ട്രീയ", "ആയുധമാക്കരുത്"],   headline lines (alternate plain/boxed)
#   "quote": true,              big quote mark (for a statement by a person)
#   "name": "കെ.എ. തുളസി", "role": "പട്ടികജാതി-പട്ടികവർഗ വികസന വകുപ്പ് മന്ത്രി",
#   "summary": "...", "credit": "ദൃശ്യങ്ങൾ: കുമാർ അട്ടപ്പാടി"
# }
# Fonts: fonts/Manjari-Bold.ttf, fonts/BarlowCondensed-Bold.ttf ; logo: logo.jpg (next to the script's cwd)
import sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
NAVY, BLUE, GREY, WHITE, TINT = (6,54,74), (10,122,191), (77,77,77), (255,255,255), (124,200,255)
DEEP = (4,38,52)
def mj(z): return ImageFont.truetype('fonts/Manjari-Bold.ttf', int(z), layout_engine=ImageFont.Layout.RAQM)
def bc(z): return ImageFont.truetype('fonts/BarlowCondensed-Bold.ttf', int(z))

def round_logo():
    src = Image.open('logo.jpg').convert('RGB'); w, h = src.size
    key = src.copy()
    for c in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]: ImageDraw.floodfill(key, c, (255,0,255), thresh=40)
    px = key.load(); m = Image.new('L', (w, h), 255); mp = m.load()
    for y in range(h):
        for x in range(w):
            if px[x,y] == (255,0,255): mp[x,y] = 0
    badge = src.convert('RGBA'); badge.putalpha(m)
    out = Image.new('RGBA', (w, h), (0,0,0,0))
    ImageDraw.Draw(out).ellipse([662-566, 652-566, 662+566, 652+566], fill=(255,255,255,255))
    out.alpha_composite(badge)
    return out.crop(out.getbbox())

def dots(d, x, y, cols, rows, gap=18, r=3, fill=TINT):
    for i in range(cols):
        for j in range(rows):
            d.ellipse([x+i*gap-r, y+j*gap-r, x+i*gap+r, y+j*gap+r], fill=fill)

def wrap(d, t, f, mw):
    o, c = [], ''
    for w in t.split(' '):
        x = (c+' '+w).strip()
        if d.textlength(x, font=f) <= mw or not c: c = x
        else: o.append(c); c = w
    if c: o.append(c)
    return o

def build(p, out):
    im = Image.new('RGBA', (W, H), NAVY+(255,)); d = ImageDraw.Draw(im)
    # background shapes: deep navy lower band, blue bar, grey sliver
    d.rectangle([0, 900, W, H], fill=DEEP)
    d.rectangle([0, 860, 560, 900], fill=BLUE)
    d.rectangle([560, 880, W, 900], fill=GREY)
    dots(d, 980, 440, 4, 6); dots(d, 40, 1000, 6, 3, fill=(40,90,112))
    # big outline quote mark behind the subject
    if p.get('quote'):
        d.text((40, 130), '“', font=bc(520), fill=None, stroke_width=6, stroke_fill=BLUE)
    # subject: cut-out (preferred) or framed photo, on the left, standing on the blue bar
    if p.get('subject'):
        s = Image.open(p['subject']).convert('RGBA'); s = s.crop(s.getbbox())
        sh = 780; s = s.resize((int(s.width*sh/s.height), sh), Image.LANCZOS)
        if s.width > 540:   # keep the headline column clean; soften the cut edge
            s = s.crop((0, 0, 540, sh)); a = s.split()[3]
            fade = Image.linear_gradient('L').rotate(90).resize((70, sh))
            a.paste(Image.composite(Image.new('L', (70, sh), 0), a.crop((470, 0, 540, sh)), fade), (470, 0)); s.putalpha(a)
        shadow = Image.new('RGBA', s.size, (0,0,0,0)); shadow.putalpha(s.split()[3].point(lambda a: a*0.45))
        im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)), (34, 900-sh+16))
        im.alpha_composite(s, (20, 900-sh))
    elif p.get('photo'):
        ph = Image.open(p['photo']).convert('RGB'); tw, th = 520, 680
        r = max(tw/ph.width, th/ph.height); ph = ph.resize((int(ph.width*r), int(ph.height*r)), Image.LANCZOS)
        ph = ph.crop(((ph.width-tw)//2, (ph.height-th)//2, (ph.width-tw)//2+tw, (ph.height-th)//2+th))
        d.rectangle([28, 176, 28+tw+16, 176+th+16], fill=BLUE); im.paste(ph, (36, 184))
    # logo top-right + handle top-left
    l = round_logo(); l.thumbnail((150,150), Image.LANCZOS); im.alpha_composite(l, (W-40-l.width, 40))
    d.text((44, 64), 'NEWS ATTAPPADI', font=bc(40), fill=WHITE)
    d.text((44, 108), 'വാർത്തകൾ വിശദമായി', font=mj(28), fill=TINT)
    # headline stack on the right: kicker, then alternating plain / white-boxed lines
    x0 = 580; maxw = W-40-x0
    y = 300
    if p.get('kicker'):
        kf = mj(34); kw = d.textlength(p['kicker'], font=kf)+40
        d.rectangle([x0, y, x0+kw, y+54], fill=BLUE); d.text((x0+20, y+29), p['kicker'], font=kf, fill=WHITE, anchor='lm'); y += 74
    lines = p['lines']
    size = 74; f = mj(size)
    while max(d.textlength(t, font=f) for t in lines)+36 > maxw and size > 40: size -= 2; f = mj(size)
    lh = int(size*1.42)
    for i, t in enumerate(lines):
        boxed = i % 2 == 1
        tw = d.textlength(t, font=f)
        if boxed:
            d.rectangle([x0, y, x0+tw+36, y+lh-8], fill=WHITE); d.text((x0+18, y+lh/2-2), t, font=f, fill=NAVY, anchor='lm')
        else:
            d.text((x0, y+lh/2-2), t, font=f, fill=WHITE, anchor='lm')
        y += lh
    # name / role tag under the headline
    if p.get('name'):
        y += 16
        nf, rf = mj(40), mj(26)
        d.rectangle([x0, y, x0+8, y+92], fill=BLUE)
        d.text((x0+24, y+24), p['name'], font=nf, fill=WHITE, anchor='lm')
        for k, ln in enumerate(wrap(d, p.get('role',''), rf, maxw-30)[:2]):
            d.text((x0+24, y+60+k*32), ln, font=rf, fill=TINT, anchor='lm')
    # summary + footer
    sf = mj(42); sy = 960
    for ln in wrap(d, p.get('summary',''), sf, W-100)[:5]:
        d.text((50, sy), ln, font=sf, fill=WHITE); sy += 62
    d.rectangle([0, H-70, W, H], fill=BLUE)
    d.text((50, H-35), '@newsattappadi', font=bc(38), fill=WHITE, anchor='lm')
    if p.get('credit'): d.text((W-50, H-35), p['credit'], font=mj(26), fill=WHITE, anchor='rm')
    im.convert('RGB').save(out, quality=95)

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
