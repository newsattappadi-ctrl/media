"""Runs on GitHub Actions. Reads tools/photo-requests.json:
{"queries":[{"out":"name","url":"https://commons.wikimedia.org/w/api.php?..."}],
 "downloads":[{"file":"name.jpg","url":"https://upload.wikimedia.org/..."}]}
Queries are saved to tools/photo-cache/<out>.json. Downloads are resized (longest side 1600px)
and saved to assets/library/<file>. Only the hosts in ALLOWED are contacted.
Credits are recorded separately in assets/library/credits.json."""
import json, pathlib, re, sys, time, io, urllib.request, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED = ('.wikimedia.org', '.wikipedia.org', '.pexels.com', '.pixabay.com', '.cdnpk.net', '.gettyimages.com', 'villagesquare.in', 'thesouthfirst.com', '.assettype.com', 'organikos.net', '.keralatourism.org', '.onmanorama.com', '.magnific.com')
UA = 'NewsAttappadiBot/1.0 (https://github.com/newsattappadi-ctrl/media; newsattappadi@gmail.com)'

def get(url):
    host = urllib.parse.urlparse(url).hostname or ''
    if urllib.parse.urlparse(url).scheme != 'https' or not any(host == a[1:] or host.endswith(a) for a in ALLOWED):
        raise ValueError('host not allowed: ' + host)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            err = e
            time.sleep(5 * (attempt + 1))
    raise err

req = json.loads((ROOT / 'tools/photo-requests.json').read_text(encoding='utf-8'))
cache = ROOT / 'tools/photo-cache'; cache.mkdir(exist_ok=True)
lib = ROOT / 'assets/library'
log = []
for q in req.get('queries', []):
    name = re.sub(r'[^a-z0-9_-]', '', q['out'].lower())
    try:
        (cache / (name + '.json')).write_bytes(get(q['url']))
        log.append('query ok ' + name)
    except Exception as e:
        log.append('query FAILED %s: %s' % (name, e))
    time.sleep(1)
for d in req.get('downloads', []):
    fn = re.sub(r'[^a-z0-9_.-]', '', d['file'].lower())
    if not fn.endswith('.jpg') or (lib / fn).exists():
        log.append('skip ' + fn); continue
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(get(d['url']))).convert('RGB')
        im.thumbnail((1600, 1600))
        im.save(lib / fn, 'JPEG', quality=86, optimize=True)
        log.append('download ok %s %dx%d' % (fn, im.width, im.height))
    except Exception as e:
        log.append('download FAILED %s: %s' % (fn, e))
    time.sleep(1)
aud = ROOT / 'assets/audio'; aud.mkdir(exist_ok=True)
for d in req.get('files', []):
    fn = re.sub(r'[^a-z0-9_.-]', '', d['file'].lower())
    try:
        (aud / fn).write_bytes(get(d['url'])); log.append('file ok ' + fn)
    except Exception as e:
        log.append('file FAILED %s: %s' % (fn, e))
(cache / '_last_run.txt').write_text('\n'.join(log) + '\n', encoding='utf-8')
print('\n'.join(log))
