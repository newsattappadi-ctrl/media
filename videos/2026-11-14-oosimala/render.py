"""Render the Oosimala news video. Run from a folder holding clips/, ov/, bite.mp4, voA.wav, voB.wav, music.mp3.
python3 render.py v|h"""
import subprocess, sys, os
O = sys.argv[1]
W, H = (1080, 1920) if O == 'v' else (1920, 1080)
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30', '-an']
CAPY = 1300 if O == 'v' else 760
LTY = 1030 if O == 'v' else 520
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)

def caps_filter(base, inputs_offset, caps):
    f, last = '', base
    for i, (s, e) in enumerate(caps):
        f += f";[{last}][{inputs_offset+i}:v]overlay=0:{CAPY}:enable='between(t,{s},{e})'[k{i}]"; last = f'k{i}'
    return f, last

def scene(name, dur, src, kind, caps, extra=None, ss=0):
    """kind: map (image list) | clip"""
    out = f'sc_{O}_{name}.mp4'; tmp = out + '.tmp.mp4'
    ins, f = [], ''
    if kind == 'map':
        # three maps, each with slow zoom, crossfaded
        parts = []
        for j, (img, d) in enumerate(src):
            ins += ['-loop', '1', '-framerate', '30', '-t', str(d + 0.4), '-i', img]
            n = int((d + 0.4) * 30)
            f += (f"[{j}:v]scale={W*2}:{H*2},zoompan=z='1+0.07*on/{n}':d=1:s={W}x{H}:fps=30:"
                  f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',setsar=1,trim=duration={d+0.4}[m{j}];")
            parts.append((f'm{j}', d))
        acc, t = parts[0][0], parts[0][1]
        for j in range(1, len(parts)):
            f += f"[{acc}][{parts[j][0]}]xfade=transition=fade:duration=0.4:offset={t-0.0:.2f}[x{j}];"; acc = f'x{j}'; t += parts[j][1]
        base = acc; nimg = len(src); top = 'ov/%s_map.png' % O
    else:
        ins += ['-ss', str(ss), '-t', str(dur), '-i', src]
        if O == 'v':
            f += (f"[0:v]scale=-2:{H},crop={W}:{H}:x='(iw-{W})/2-140+280*t/{dur}':y=0,setsar=1,fps=30[b0];")
        else:
            f += f"[0:v]scale={int(W*1.08)}:-2,crop={W}:{H}:x='(iw-{W})*t/{dur}':y='(ih-{H})/2',setsar=1,fps=30[b0];"
        base = 'b0'; nimg = 1; top = 'ov/%s_top.png' % O
    ins += ['-i', top]; f += f"[{base}][{nimg}:v]overlay=0:0[t0]"; last = 't0'; off = nimg + 1
    if extra:
        ins += ['-i', extra]; f += f";[t0][{off}:v]overlay=0:{LTY}[t1]"; last = 't1'; off += 1
    for c, _, _ in caps: ins += ['-i', f'ov/{O}_cap_{c}.png']
    cf, last = caps_filter(last, off, [(s, e) for _, s, e in caps]); f += cf
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f, '-map', f'[{last}]', '-t', str(dur), *ENC, tmp])
    os.replace(tmp, out); return out

def still(name, img, dur):
    out = f'sc_{O}_{name}.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', img, '-vf', f'scale={W}:{H},format=yuv420p,loop=-1:1,trim=duration={dur},fade=in:0:9', *ENC, out + '.tmp.mp4'])
    os.replace(out + '.tmp.mp4', out); return out

S = []
S.append(scene('map', 7.5, [(f'ov/map_{O}_kerala.jpg', 2.6), (f'ov/map_{O}_attappadi.jpg', 2.1), (f'ov/map_{O}_narasi.jpg', 2.8)], 'map',
               [('a1', 0.2, 2.4), ('a2', 2.9, 4.4), ('a3', 4.6, 7.5)]))
T = 7.5
BROLL = [('c04', 3.8, 2.0), ('c11', 3.8, 2.5), ('c03', 3.6, 2.5), ('c09', 2.2, 3.0), ('c02', 3.8, 2.0), ('c08', 3.9, 2.0)]
VOCAPS = [('a3', 4.6, 11.9), ('a4', 11.93, 15.6), ('a5', 15.7, 21.0), ('a6', 21.1, 24.7), ('a7', 24.78, 28.8)]
for c, d, ss in BROLL:
    caps = [(k, max(s - T, 0), min(e - T, d)) for k, s, e in VOCAPS if e > T and s < T + d]
    S.append(scene(f'{c}', d, f'clips/{c}.mp4', 'clip', caps, ss=ss)); T += d
BITE0 = T  # 28.8
S.append(scene('bite', 14.6, 'bite.mp4', 'clip', [('bite', 0.6, 14.4)], extra=f'ov/{O}_lt.png'))
T += 14.6
VOB = T + 0.2
B2 = [('c06', 4.0, 2.0), ('c07', 5.2, 2.5)]
VBCAPS = [('b1', VOB + 0.0, VOB + 3.45), ('b2', VOB + 3.85, VOB + 8.4)]
for c, d, ss in B2:
    caps = [(k, max(s - T, 0), min(e - T, d)) for k, s, e in VBCAPS if e > T and s < T + d]
    S.append(scene(f'{c}', d, f'clips/{c}.mp4', 'clip', caps, ss=ss)); T += d
END = 4.8
S.append(still('end', f'ov/{O}_end.png', END)); TOTAL = T + END

open(f'list_{O}.txt', 'w').write(''.join(f"file '{s}'\n" for s in S))
run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'list_{O}.txt', '-c', 'copy', f'video_{O}.mp4'])
# audio: VO A at 0, bite at BITE0, VO B at VOB, music bed ducked under bite
af = (f"[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=1.5[va];"
      f"[1:a]aresample=48000,atrim=0:14.6,asetpts=PTS-STARTPTS,highpass=f=90,volume=1.9,adelay={int(BITE0*1000)}|{int(BITE0*1000)}[bt];"
      f"[2:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=1.5,adelay={int(VOB*1000)}|{int(VOB*1000)}[vb];"
      f"[3:a]aresample=48000,aloop=loop=-1:size=2e9,atrim=0:{TOTAL},asetpts=PTS-STARTPTS,"
      f"volume='if(between(t,{BITE0},{BITE0+14.6}),0.05,0.16)':eval=frame,afade=t=out:st={TOTAL-1.5}:d=1.5[mu];"
      f"[va][bt][vb][mu]amix=inputs=4:duration=longest:normalize=0,alimiter=limit=0.95,atrim=0:{TOTAL}[a]")
run(['ffmpeg', '-v', 'error', '-y', '-i', 'voA.wav', '-i', 'bite.mp4', '-i', 'voB.wav', '-i', 'music.mp3', '-filter_complex', af,
     '-map', '[a]', '-c:a', 'aac', '-b:a', '192k', f'audio_{O}.m4a'])
name = 'NewsAttappadi_Oosimala_v2_' + ('reel' if O == 'v' else '16x9') + '.mp4'
run(['ffmpeg', '-v', 'error', '-y', '-i', f'video_{O}.mp4', '-i', f'audio_{O}.m4a', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', name + '.tmp.mp4'])
os.replace(name + '.tmp.mp4', name)
print(name, round(TOTAL, 2))
