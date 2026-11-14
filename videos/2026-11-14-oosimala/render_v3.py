"""Render Oosimala v3. Run in a folder holding clips/, ov3/, bite.mp4, vH.wav v1.wav v2.wav v3.wav, music_news.mp3.
python3 render_v3.py v|h"""
import subprocess, sys, os
O = sys.argv[1]
W, H = (1080, 1920) if O == 'v' else (1920, 1080)
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30', '-an']
CAPY = 1090 if O == 'v' else 700
LTY = 880 if O == 'v' else 500

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(' '.join(cmd)[:500]); print(r.stderr[-3000:]); sys.exit(1)
    return r.stdout

def dur_of(p): return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

def scene(name, dur, base, overlays, top):
    """base: ('clip', path, ss, dim) | ('map', [(img, d)]). overlays: list of (png, y, start, end, slide)"""
    out = f'sc3_{O}_{name}.mp4'; ins, f = [], ''
    if base[0] == 'map':
        parts = []
        for j, (img, d) in enumerate(base[1]):
            ins += ['-loop', '1', '-framerate', '30', '-t', str(d + 0.4), '-i', img]
            n = int((d + 0.4) * 30)
            f += (f"[{j}:v]scale={W*2}:{H*2},zoompan=z='1+0.08*on/{n}':d=1:s={W}x{H}:fps=30:"
                  f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',setsar=1,trim=duration={d+0.4}[m{j}];")
            parts.append((f'm{j}', d))
        acc, t = parts[0][0], parts[0][1]
        for j in range(1, len(parts)):
            f += f"[{acc}][{parts[j][0]}]xfade=transition=fade:duration=0.4:offset={t:.2f}[x{j}];"; acc = f'x{j}'; t += parts[j][1]
        last, n = acc, len(parts)
    else:
        _, src, ss, dim = base
        L = dur_of(src); ss = max(0, min(ss, L - dur - 0.05))
        ins += ['-ss', str(ss), '-t', str(dur), '-i', src]
        g = ',eq=brightness=-0.10:saturation=0.8' if dim else ''
        if O == 'v':
            f += f"[0:v]scale=-2:{H},crop={W}:{H}:x='(iw-{W})/2-140+280*t/{dur}':y=0,setsar=1,fps=30{g}[b0];"
        else:
            f += f"[0:v]scale={int(W*1.08)}:-2,crop={W}:{H}:x='(iw-{W})*t/{dur}':y='(ih-{H})/2',setsar=1,fps=30{g}[b0];"
        last, n = 'b0', 1
    ins += ['-loop', '1', '-framerate', '30', '-t', str(dur), '-i', top]
    f += f"[{last}][{n}:v]overlay=0:0[t0]"; last = 't0'; k = n + 1
    for i, (png, y, s, e, slide) in enumerate(overlays):
        ins += ['-loop', '1', '-framerate', '30', '-t', str(dur), '-i', png]
        sd = 0.35 if slide == 'big' else 0.22
        x = f"'if(lt(t,{s}),-main_w,min(0,-main_w+(t-{s})*main_w/{sd}))'" if slide == 'big' else f"'min(0,-160+(t-{s})*160/{sd})'"
        f += f";[{last}][{k}:v]overlay=x={x}:y={y}:enable='between(t,{s},{e})'[o{i}]"; last = f'o{i}'; k += 1
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f, '-map', f'[{last}]', '-t', str(dur), *ENC, out + '.tmp.mp4'])
    os.replace(out + '.tmp.mp4', out); return out

def cap(c, s, e): return (f'ov3/{O}_cap_{c}.png', CAPY, s, e, 'cap')
TOP, TOPM = f'ov3/{O}_top.png', f'ov3/{O}_map.png'

# absolute timeline of captions, split across b-roll scenes
S, T = [], 0.0
def broll(items, caps_abs):
    global T
    for c, d, ss in items:
        cs = [cap(k, round(max(s - T, 0), 2), round(min(e - T, d), 2)) for k, s, e in caps_abs if e > T + 0.05 and s < T + d - 0.05]
        S.append(scene(f'{c}_{int(T*10)}', d, ('clip', f'clips/{c}.mp4', ss, False), cs, TOP)); T += d

VH, V1, V2, V3 = 0.8, 8.4, 23.9, 77.8
S.append(scene('open', 8.3, ('clip', 'clips/c04.mp4', 2.0, True),
               [(f'ov3/{O}_head1.png', 0, 0.4, 8.3, 'big'), (f'ov3/{O}_head2.png', 0, VH + 3.85, 8.3, 'big')], TOP)); T = 8.3
S.append(scene('map', 7.0, ('map', [(f'ov3/map_{O}_kerala.jpg', 2.2), (f'ov3/map_{O}_attappadi.jpg', 2.2), (f'ov3/map_{O}_narasi.jpg', 2.6)]),
               [cap('m1', 0.3, 7.0)], TOPM)); T = 15.3
broll([('c11', 4.3, 2.5), ('c03', 4.1, 2.5)], [('m2', V1 + 7.08, 23.7)])
P = [('p1', V2, V2 + 6.7), ('p2', V2 + 7.15, V2 + 9.8), ('p3', V2 + 9.8, V2 + 14.0), ('p4', V2 + 14.26, V2 + 18.9),
     ('p5', V2 + 19.25, V2 + 24.0), ('p6', V2 + 24.0, V2 + 29.6), ('p7', V2 + 30.1, 63.0)]
broll([('c02', 5.0, 2.0), ('c09', 4.6, 3.0), ('c08', 5.0, 2.0), ('c06', 5.0, 2.0), ('c10', 5.4, 2.0), ('c12', 5.0, 2.0), ('c01', 4.4, 2.0), ('c05', 4.9, 2.0)], P)
BITE0 = T  # 63.0
S.append(scene('bite', 14.6, ('clip', 'bite.mp4', 0, False), [(f'ov3/{O}_lt.png', LTY, 0.3, 14.6, 'cap'), cap('bite', 0.8, 14.4)], TOP)); T += 14.6
broll([('c07', 5.6, 2.0), ('c09', 5.3, 0.0), ('c11', 5.3, 0.0)],
      [('q1', V3, V3 + 6.9), ('q2', V3 + 7.26, V3 + 10.9), ('q3', V3 + 11.24, T + 16.2)])
END0 = T; END = 5.0
out = f'sc3_{O}_end.mp4'
run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', f'ov3/{O}_end.png', '-vf', f'scale={W}:{H},format=yuv420p,loop=-1:1,trim=duration={END},fade=in:0:9', *ENC, out + '.tmp.mp4'])
os.replace(out + '.tmp.mp4', out); S.append(out); TOTAL = T + END

open(f'list3_{O}.txt', 'w').write(''.join(f"file '{s}'\n" for s in S))
run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'list3_{O}.txt', '-c', 'copy', f'video3_{O}.mp4'])
def vo(i, t): return f"[{i}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=1.6,adelay={int(t*1000)}|{int(t*1000)}[a{i}];"
vol = (f"if(lt(t,8.3),0.30,if(between(t,{BITE0},{BITE0+14.6}),0.035,if(gt(t,{END0}),0.32,0.11)))")
af = (vo(0, VH) + vo(1, V1) + vo(2, V2) + vo(3, V3) +
      f"[4:a]aresample=48000,atrim=0:14.6,asetpts=PTS-STARTPTS,highpass=f=90,volume=1.9,adelay={int(BITE0*1000)}|{int(BITE0*1000)}[bt];"
      f"[5:a]aresample=48000,aloop=loop=-1:size=2e9,atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume='{vol}':eval=frame,afade=t=out:st={TOTAL-1.8}:d=1.8[mu];"
      f"[a0][a1][a2][a3][bt][mu]amix=inputs=6:duration=longest:normalize=0,alimiter=limit=0.95,atrim=0:{TOTAL}[a]")
run(['ffmpeg', '-v', 'error', '-y', '-i', 'vH.wav', '-i', 'v1.wav', '-i', 'v2.wav', '-i', 'v3.wav', '-i', 'bite.mp4', '-i', 'music_news.mp3',
     '-filter_complex', af, '-map', '[a]', '-c:a', 'aac', '-b:a', '192k', f'audio3_{O}.m4a'])
name = 'NewsAttappadi_Oosimala_v3_' + ('reel' if O == 'v' else '16x9') + '.mp4'
run(['ffmpeg', '-v', 'error', '-y', '-i', f'video3_{O}.mp4', '-i', f'audio3_{O}.m4a', '-map', '0:v', '-map', '1:a', '-c', 'copy', '-shortest', '-movflags', '+faststart', name + '.tmp.mp4'])
os.replace(name + '.tmp.mp4', name)
print(name, round(TOTAL, 2))
