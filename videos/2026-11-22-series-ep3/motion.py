# Motion graphics for series videos: animated cards and animated maps, drawn frame by frame with PIL.
# Logo palette only: navy, blue, grey, white, tint.
import json, math, re
from PIL import Image, ImageDraw, ImageFont

NAVY, BLUE, GREY, WHITE, TINT = (6,54,74), (10,122,191), (77,77,77), (255,255,255), (124,200,255)
DEEP = (4,30,42)

def ease(x): x = max(0.0, min(1.0, x)); return x*x*(3-2*x)
def eout(x): x = max(0.0, min(1.0, x)); return 1-(1-x)**3
def back(x):  # overshoot pop
    x = max(0.0, min(1.0, x)); c = 1.6; return 1 + (c+1)*(x-1)**3 + c*(x-1)**2

class Motion:
    def __init__(self, W, H, mj, bc, s, wrap, fit, geo_dir):
        self.W, self.H, self.mj, self.bc, self.s, self.wrap, self.fit = W, H, mj, bc, s, wrap, fit
        self.V = H > W
        self.geo = []
        for st in ('kerala', 'tamil-nadu', 'karnataka'):
            for f in json.load(open(f'{geo_dir}/{st}.geojson'))['features']:
                g = f['geometry']; rings = [g['coordinates'][0]] if g['type'] == 'Polygon' else [p[0] for p in g['coordinates']]
                self.geo.append((f['properties']['st_nm'], f['properties']['district'], rings))

    # ---------- shared ----------
    def panel(self, t):
        W, H, s = self.W, self.H, self.s
        im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
        off = int((t*40) % s(70))
        for i in range(-s(70), W+H+s(70), s(70)): d.line([(i+off, 0), (i+off-H, H)], fill=(10,64,88), width=s(3))
        return im

    def layer_text(self, text, font, fill):
        d0 = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
        b = d0.textbbox((0, 0), text, font=font)
        w, h = b[2]-b[0]+20, b[3]-b[1]+20
        L = Image.new('RGBA', (w, h), (0,0,0,0)); ImageDraw.Draw(L).text((10-b[0], 10-b[1]), text, font=font, fill=fill)
        return L

    def put(self, im, L, cx, cy, alpha=1.0, scale=1.0, dy=0):
        if alpha <= 0.01: return
        if abs(scale-1) > 0.005:
            L = L.resize((max(1, int(L.width*scale)), max(1, int(L.height*scale))), Image.BICUBIC)
        if alpha < 0.999:
            a = L.split()[3].point(lambda v: int(v*alpha)); L = L.copy(); L.putalpha(a)
        im.paste(L, (int(cx-L.width/2), int(cy-L.height/2+dy)), L)

    # ---------- cards ----------
    def card(self, kind, data, dur):
        """returns frame(t)->RGB image"""
        W, H, s, mj, bc = self.W, self.H, self.s, self.mj, self.bc
        cx, cy = W/2, H/2 - s(60 if self.V else 20)
        d0 = ImageDraw.Draw(Image.new('RGB', (8, 8)))
        if kind == 'stat':
            big, lab = data
            num = re.match(r'^(₹?)([\d,]+(?:\.\d+)?)(.*)$', big)
            countable = bool(num) and not re.fullmatch(r'(19|20)\d\d', num.group(2).replace(',', '')) and '–' not in big
            fn = bc if re.fullmatch(r'[0-9,.\-–%+? ]+', big) else mj
            f = self.fit(d0, big, s(300 if self.V else 280), W-s(120), fn)
            labs = [self.layer_text(ln, mj(s(60)), TINT) for ln in self.wrap(d0, lab, mj(s(60)), W-s(140))]
            static_big = self.layer_text(big, f, WHITE)
            def frame(t):
                im = self.panel(t)
                if countable:
                    p = eout(t/1.1); raw = num.group(2).replace(',', ''); dec = len(raw.split('.')[1]) if '.' in raw else 0
                    v = float(raw)*p; txt = f'{v:,.{dec}f}' if ',' in num.group(2) or dec else f'{int(round(v))}'
                    if dec: txt = f'{v:.{dec}f}'
                    L = self.layer_text(num.group(1)+txt+num.group(3), f, WHITE)
                else:
                    L = static_big
                self.put(im, L, cx, cy-s(40), alpha=ease(t/0.35), scale=0.82+0.18*back(t/0.55))
                dd = ImageDraw.Draw(im); bw = s(420)*eout((t-0.25)/0.5)
                if bw > 1: dd.rectangle([cx-bw/2, cy+s(105), cx+bw/2, cy+s(113)], fill=BLUE)
                for i, Lb in enumerate(labs):
                    tt = (t-0.45-0.15*i)/0.45
                    self.put(im, Lb, cx, cy+s(180)+i*s(80), alpha=ease(tt), dy=s(30)*(1-eout(tt)))
                return im
            return frame
        if kind == 'route':
            a, b, lab = data
            La = self.layer_text(a, self.fit(d0, a, s(80), W-s(120)), WHITE)
            Lb = self.layer_text(b, self.fit(d0, b, s(100), W-s(120)), TINT)
            labs = [self.layer_text(ln, mj(s(50)), WHITE) for ln in self.wrap(d0, lab, mj(s(50)), W-s(160))]
            def frame(t):
                im = self.panel(t); dd = ImageDraw.Draw(im)
                self.put(im, La, cx, cy-s(330), alpha=ease(t/0.35), dy=-s(30)*(1-eout(t/0.4)))
                p = eout((t-0.3)/0.6); y1 = cy-s(250); y2 = y1+(s(310))*p
                if p > 0: dd.line([(cx, y1), (cx, y2)], fill=TINT, width=s(10))
                if p >= 0.98: dd.polygon([(cx-s(40), cy+s(40)), (cx+s(40), cy+s(40)), (cx, cy+s(110))], fill=TINT)
                tb = (t-0.85)/0.45
                if tb > 0: self.put(im, Lb, cx, cy+s(190), alpha=ease(tb), scale=0.7+0.3*back(tb))
                for i, L in enumerate(labs):
                    tt = (t-1.2-0.15*i)/0.4; self.put(im, L, cx, cy+s(360)+i*s(70), alpha=ease(tt), dy=s(20)*(1-eout(tt)))
                return im
            return frame
        if kind == 'quote':
            q, who = data
            lines = [self.layer_text(ln, mj(s(66)), WHITE) for ln in self.wrap(d0, q, mj(s(66)), W-s(180))]
            whos = [self.layer_text(ln, mj(s(42)), TINT) for ln in self.wrap(d0, who, mj(s(42)), W-s(200))]
            Q = self.layer_text('“', bc(s(260)), BLUE)
            def frame(t):
                im = self.panel(t); dd = ImageDraw.Draw(im)
                self.put(im, Q, s(80)+Q.width/2, cy-s(380)+Q.height/2, alpha=ease(t/0.3), scale=0.6+0.4*back(t/0.45))
                y = cy-s(200)
                for i, L in enumerate(lines):
                    tt = (t-0.3-0.28*i)/0.4
                    self.put(im, L, s(100)+L.width/2, y+L.height/2, alpha=ease(tt), dy=s(18)*(1-eout(tt))); y += s(92)
                tw = (t-0.3-0.28*len(lines))/0.4
                bw = s(60)*eout(tw)
                if bw > 1: dd.rectangle([s(100), y+s(30), s(100)+bw, y+s(36)], fill=TINT)
                for L in whos:
                    self.put(im, L, s(100)+L.width/2, y+s(60)+L.height/2, alpha=ease(tw)); y += s(56)
                return im
            return frame
        if kind == 'next':
            ep = data
            items = [(self.layer_text('സ്വന്തം മണ്ണിലെ അഭയാർത്ഥികൾ', self.fit(d0, 'സ്വന്തം മണ്ണിലെ അഭയാർത്ഥികൾ', s(80), W-s(120)), TINT), cy-s(200)),
                     (self.layer_text(ep['next_part'], mj(s(130)), WHITE), cy-s(40)),
                     (self.layer_text(ep['next_title'], self.fit(d0, ep['next_title'], s(80), W-s(100)), WHITE), cy+s(110))]
            U = self.layer_text('ഉടൻ', mj(s(52)), WHITE)
            def frame(t):
                im = self.panel(t); dd = ImageDraw.Draw(im)
                for i, (L, y) in enumerate(items):
                    tt = (t-0.2*i)/0.45; self.put(im, L, cx, y, alpha=ease(tt), scale=0.85+0.15*eout(tt))
                tt = (t-0.8)/0.4
                if tt > 0:
                    k = back(tt); dd.rectangle([cx-s(140)*k, cy+s(200), cx+s(140)*k, cy+s(270)], fill=BLUE)
                    self.put(im, U, cx, cy+s(238), alpha=ease(tt))
                return im
            return frame
        raise ValueError(kind)

    # ---------- maps ----------
    def map(self, data, dur):
        """data: {'view': 'kerala'|'zoom', 'pins': [(name, lon, lat, main)], 'title': str, 'sub': str}"""
        W, H, s, mj = self.W, self.H, self.s, self.mj
        ATT = (76.64, 11.10)
        K = dict(lon=76.25, lat=10.45, span=5.6)       # all of Kerala
        A = dict(lon=76.66, lat=11.10, span=0.75)      # Attappadi
        zoom = data.get('view') == 'zoom'
        d0 = ImageDraw.Draw(Image.new('RGB', (8, 8)))
        title = self.layer_text(data['title'], self.fit(d0, data['title'], s(64), W-s(140)), WHITE)
        subs = [self.layer_text(ln, mj(s(44)), TINT) for ln in self.wrap(d0, data.get('sub', ''), mj(s(44)), W-s(160))] if data.get('sub') else []
        def cam(t):
            if not zoom: return K
            p = ease((t-0.4)/2.0)
            # geometric interpolation of span for a smooth zoom
            sp = math.exp(math.log(K['span'])+(math.log(A['span'])-math.log(K['span']))*p)
            return dict(lon=K['lon']+(A['lon']-K['lon'])*p, lat=K['lat']+(A['lat']-K['lat'])*p, span=sp)
        def px(c, lon, lat):
            k = W/c['span']; return (W/2+(lon-c['lon'])*k*math.cos(math.radians(c['lat'])), H*0.47-(lat-c['lat'])*k)
        def frame(t):
            c = cam(t)
            im = Image.new('RGB', (W, H), DEEP); d = ImageDraw.Draw(im, 'RGBA')
            g = s(80)
            for i in range(0, W, g): d.line([(i, 0), (i, H)], fill=(255,255,255,10))
            for j in range(0, H, g): d.line([(0, j), (W, j)], fill=(255,255,255,10))
            for st, dist, rings in self.geo:
                if st == 'Kerala':
                    fill, line = ((16,96,140,255), TINT+(255,)) if dist == 'Palakkad' else ((14,70,96,255), (60,140,180,255))
                else:
                    fill, line = (8,36,50,255), (30,70,90,255)
                for r in rings:
                    pts = [px(c, x, y) for x, y in r[::2]]
                    if len(pts) > 2: d.polygon(pts, fill=fill, outline=line)
            # Attappadi glow region
            ax, ay = px(c, *ATT); rr = min(0.17*W/c['span'], s(120))
            pulse = 0.5+0.5*math.sin(t*4)
            for k in range(6, 0, -1):
                r = rr*(1+0.12*k) + s(6)*pulse
                d.ellipse([ax-r, ay-r, ax+r, ay+r], fill=(124,200,255, int(10+4*k*ease(t/0.6))))
            d.ellipse([ax-rr, ay-rr, ax+rr, ay+rr], outline=TINT+(int(255*ease(t/0.6)),), width=s(5))
            # state labels
            if not zoom or t < 1.2:
                for nm, lon, lat in [('കേരളം', 76.3, 9.6), ('തമിഴ്നാട്', 77.8, 10.6), ('കർണാടക', 76.6, 12.6)]:
                    x, y = px(c, lon, lat); d.text((x, y), nm, font=mj(s(44)), fill=(255,255,255,140), anchor='mm')
            if not zoom:
                lx, ly = ax+s(40), ay-s(40); d.line([(ax+rr*0.7, ay-rr*0.7), (lx, ly)], fill=WHITE+(255,), width=s(4))
                f = mj(s(50)); tw = d.textlength('അട്ടപ്പാടി', font=f)
                d.rectangle([lx, ly-s(40), lx+tw+s(40), ly+s(36)], fill=BLUE+(255,)); d.text((lx+s(20), ly), 'അട്ടപ്പാടി', font=f, fill=WHITE, anchor='lm')
            # pins
            for i, (nm, lon, lat, main) in enumerate(data.get('pins', [])):
                tp = (t-(2.4 if zoom else 0.8)-0.35*i)/0.4
                if tp <= 0: continue
                x, y = px(c, lon, lat); k = back(tp); r = s(16 if main else 11)*k
                if main:
                    rp = s(16)+s(40)*((t*1.2) % 1); d.ellipse([x-rp, y-rp, x+rp, y+rp], outline=TINT+(int(255*(1-((t*1.2) % 1))),), width=s(4))
                d.ellipse([x-r, y-r, x+r, y+r], fill=WHITE+(255,), outline=BLUE+(255,), width=s(5))
                f = mj(s(46 if main else 38)); tw = d.textlength(nm, font=f); a = int(255*ease(tp))
                bx = x+s(28); d.rectangle([bx, y-s(32), bx+tw+s(32), y+s(30)], fill=(NAVY if not main else BLUE)+(int(a*0.92),))
                d.text((bx+s(16), y), nm, font=f, fill=WHITE+(a,), anchor='lm')
            # title box (top area, below the logo row)
            tt = ease((t-0.2)/0.4)
            if tt > 0:
                by = s(250); bh = title.height+s(30)+len(subs)*s(58)
                d.rectangle([s(36), by, W-s(36), by+bh], fill=NAVY+(int(235*tt),)); d.rectangle([s(36), by, s(48), by+bh], fill=BLUE+(int(255*tt),))
                self.put(im, title, s(76)+title.width/2, by+s(14)+title.height/2, alpha=tt)
                for i, L in enumerate(subs):
                    self.put(im, L, s(76)+L.width/2, by+s(18)+title.height+i*s(58)+L.height/2, alpha=ease((t-0.5-0.15*i)/0.4))
            return im
        return frame
