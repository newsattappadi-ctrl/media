# 3D stone title for ആദിരക്തം: extruded, bevel-lit, perspective rise, light sweep, embers, fog.
import numpy as np, subprocess, sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W,H=1080,1920; FPS=25
FD='/home/claude/fonts2/'
def font(name,size,var=None):
    f=ImageFont.truetype(FD+name,size,layout_engine=ImageFont.Layout.RAQM)
    if var: f.set_variation_by_name(var)
    return f
TINT=(124,200,255); BLUE=(10,122,191)
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def eout(x): x=max(0,min(1,x)); return 1-(1-x)**3

def stone_text(text, size, tex_path, depth=44, maxw=900):
    f=font('NotoSerifMalayalam.ttf',size,'Black')
    d0=ImageDraw.Draw(Image.new('L',(8,8))); b=d0.textbbox((0,0),text,font=f)
    while b[2]-b[0]>maxw:
        size=int(size*0.95); f=font('NotoSerifMalayalam.ttf',size,'Black'); b=d0.textbbox((0,0),text,font=f)
    tw,th=b[2]-b[0],b[3]-b[1]; pad=60
    w,h=tw+2*pad+depth,th+2*pad+depth
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).text((pad-b[0],pad-b[1]),text,font=f,fill=255)
    M=np.asarray(m).astype(np.float32)/255
    # bevel normals from blurred mask
    hb=np.asarray(m.filter(ImageFilter.GaussianBlur(7))).astype(np.float32)/255
    gy,gx=np.gradient(hb)
    nx,ny,nz=-gx*9,-gy*9,np.ones_like(gx); n=np.sqrt(nx**2+ny**2+nz**2); nx,ny,nz=nx/n,ny/n,nz/n
    L=np.array([-0.45,-0.6,0.66]); L/=np.linalg.norm(L)
    lam=np.clip(nx*L[0]+ny*L[1]+nz*L[2],0,1)
    tex=Image.open(tex_path).convert('RGB'); tex=tex.resize((max(w,tex.width*w//tex.width),max(h,int(tex.height*w/tex.width)))).crop((0,0,w,h))
    T=np.asarray(tex).astype(np.float32)/255
    T=0.55*T+0.45*T.mean(axis=2,keepdims=True)  # desaturate a bit
    warm=np.array([1.08,0.92,0.78])
    spec=np.clip(lam,0,1)**12
    face=T*warm*(0.25+1.15*lam[...,None])+spec[...,None]*np.array([1.0,0.85,0.6])*0.5
    edge=np.clip(np.asarray(m.filter(ImageFilter.FIND_EDGES)).astype(np.float32)/255,0,1)
    face=face+edge[...,None]*np.array([1.0,0.75,0.4])*0.35
    # extrusion: darker copies shifted down
    out=np.zeros((h,w,4),np.float32)
    for k in range(depth,0,-1):
        sh=np.roll(np.roll(M,k,axis=0),k//2,axis=1); sh[:k]=0; sh[:,:k//2]=0
        c=np.array([0.42,0.27,0.14])*(1-0.75*k/depth)
        a=sh[...,None]
        out[...,:3]=out[...,:3]*(1-a)+c*a; out[...,3:]=np.maximum(out[...,3:],a)
    a=M[...,None]; out[...,:3]=out[...,:3]*(1-a)+face*a; out[...,3:]=np.maximum(out[...,3:],a)
    return out, M  # float rgba, face mask

def persp(img, ang, scale, cx, cy):
    """rotateX by ang (deg, positive = top tilted away), project onto canvas centre (cx,cy)."""
    h,w=img.shape[:2]; f=1400.0; a=math.radians(ang)
    def P(x,y):
        X=(x-w/2)*scale; Y=(y-h/2)*scale
        y3=Y*math.cos(a); z3=Y*math.sin(a)
        k=f/(f+z3); return (cx+X*k, cy+y3*k)
    dst=[P(0,0),P(w,0),P(w,h),P(0,h)]; src=[(0,0),(w,0),(w,h),(0,h)]
    # solve coefficients mapping dst->src
    A=[];B=[]
    for (X,Y),(x,y) in zip(dst,src):
        A.append([X,Y,1,0,0,0,-x*X,-x*Y]); B.append(x)
        A.append([0,0,0,X,Y,1,-y*X,-y*Y]); B.append(y)
    co=np.linalg.solve(np.array(A,float),np.array(B,float))
    im=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8),'RGBA')
    return im.transform((W,H),Image.PERSPECTIVE,tuple(co),Image.BICUBIC)

def embers(n,seed=3):
    r=random.Random(seed); return [(r.uniform(0,W),r.uniform(0,H),r.uniform(30,110),r.uniform(1.5,4.5),r.uniform(0,6.28)) for _ in range(n)]

def render_title(out, dur, bg_video, tex, sub1, sub2, logo_path, big='ആദിരക്തം', mode='title'):
    title,_=stone_text(big,260,tex,maxw=900 if mode=='title' else 760)
    fr=int(round(dur*FPS)); E=embers(90)
    logo=Image.open(logo_path).convert('RGBA'); logo=logo.crop(logo.getbbox()); logo.thumbnail((150,150))
    f1=font('AnekMalayalam.ttf',44,'SemiBold'); f2=font('AnekMalayalam.ttf',58,'Bold'); f3=font('AnekMalayalam.ttf',40,'Medium')
    dec=subprocess.Popen(['ffmpeg','-v','error','-i',bg_video,'-vf',f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=brightness=-0.18:saturation=0.55,gblur=sigma=2','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    last=None
    for i in range(fr):
        t=i/FPS
        raw=dec.stdout.read(W*H*3)
        if len(raw)==W*H*3: last=raw
        bg=Image.frombytes('RGB',(W,H),last).convert('RGBA')
        # warm ember glow from below
        glow=Image.new('RGBA',(W,H),(0,0,0,0)); g=ImageDraw.Draw(glow)
        pulse=0.85+0.15*math.sin(t*5)
        g.ellipse([W*0.05,H*0.42,W*0.95,H*0.78],fill=(255,120,40,int(70*pulse*ease(t/1.5))))
        glow=glow.filter(ImageFilter.GaussianBlur(120)); bg.alpha_composite(glow)
        # embers
        e=Image.new('RGBA',(W,H),(0,0,0,0)); ed=ImageDraw.Draw(e)
        for (x,y,v,r,ph) in E:
            yy=(y-v*t)%H; xx=x+18*math.sin(t*1.3+ph); a=int(200*(0.5+0.5*math.sin(t*3+ph)))
            ed.ellipse([xx-r,yy-r,xx+r,yy+r],fill=(255,170,80,a))
        e2=e.filter(ImageFilter.GaussianBlur(2)); bg.alpha_composite(e2); bg.alpha_composite(e)
        cy=H*0.5
        if mode=='title':
            # logo + presenter line
            la=ease(t/0.8)*(1-ease((t-6.2)/0.6))
            L=logo.copy(); L.putalpha(L.split()[3].point(lambda v:int(v*la))); bg.alpha_composite(L,(int(W/2-L.width/2),int(H*0.25)))
            d=ImageDraw.Draw(bg)
            if t>0.4:
                a=int(255*ease((t-0.4)/0.6)); d.text((W/2,H*0.25+190),'ന്യൂസ് അട്ടപ്പാടി അവതരിപ്പിക്കുന്നു',font=f1,fill=TINT+(a,),anchor='mm')
            tt=(t-1.6)/1.6
        else:
            tt=t/1.4
        if tt>0:
            p=eout(tt); ang=75*(1-p); sc=0.72+0.28*p+0.02*max(0,t-3)
            img=title.copy()
            # light sweep across the face
            sw=(t-(3.0 if mode=='title' else 1.4))/1.2
            if 0<sw<1:
                h_,w_=img.shape[:2]; xs=np.arange(w_)[None,:]; band=np.exp(-((xs-(sw*1.4-0.2)*w_)/60.0)**2)
                img[...,:3]=np.clip(img[...,:3]+band[...,None]*0.55*img[...,3:],0,1)
            ti=persp(img,ang,sc,W/2,cy)
            # shadow
            shd=Image.new('RGBA',(W,H),(0,0,0,0)); shd.putalpha(ti.split()[3].point(lambda v:int(v*0.7))); shd=shd.filter(ImageFilter.GaussianBlur(18))
            al=ease(tt*1.6)
            if al<1:
                ti.putalpha(ti.split()[3].point(lambda v:int(v*al))); shd.putalpha(shd.split()[3].point(lambda v:int(v*al)))
            bg.alpha_composite(shd,(0,24)); bg.alpha_composite(ti)
        d=ImageDraw.Draw(bg)
        t2=t-(4.0 if mode=='title' else 1.6)
        if t2>0:
            lw=int(360*eout(t2/0.6)); d.rectangle([W/2-lw,cy+175,W/2+lw,cy+180],fill=BLUE+(255,))
            a=int(255*ease((t2-0.2)/0.5));
            if a>0: d.text((W/2,cy+250+12*(1-ease((t2-0.2)/0.5))),sub1,font=f2,fill=(255,255,255,a),anchor='mm')
            a=int(255*ease((t2-0.6)/0.5))
            if a>0 and sub2: d.text((W/2,cy+330),sub2,font=f3,fill=TINT+(a,),anchor='mm')
        fo=1-ease((t-(dur-0.5))/0.5)
        fr_=bg.convert('RGB')
        if fo<1: fr_=Image.eval(fr_,lambda v:int(v*fo))
        enc.stdin.write(fr_.tobytes())
    dec.stdout.close(); dec.wait(); enc.stdin.close(); enc.wait()

if __name__=='__main__':
    A='/home/claude/media/assets/audio/'; Lb='/home/claude/media/assets/library/'
    render_title('/home/claude/adi1/c2/title.mp4',7.3,A+'adi1_v_peak.mp4',Lb+'a1_dolmen.jpg','ഭാഗം 1  ·  മണ്ണ് മറന്ന കഥ','ശിലായുഗം മുതൽ ഇന്നുവരെ','/home/claude/na/logo.png')
