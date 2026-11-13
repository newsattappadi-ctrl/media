"""WhatsApp group posters for News Attappadi, in the same brand style as build.py.
Usage: cd tools && python3 wa.py ../posts/whatsapp
"""
import pathlib, subprocess, sys, re

D = pathlib.Path(__file__).resolve().parent
src = (D / 'build.py').read_text(encoding='utf-8')
ns = {}
exec(src.split('def pts(')[0].split('import subprocess, pathlib, json, sys')[1], {'pathlib': pathlib, '__file__': str(D / 'build.py')}, ns)
CSS, PAPER, FOOT = ns['CSS'], ns['PAPER'], ns['FOOT']
CHROME = sys.argv[2] if len(sys.argv) > 2 else 'google-chrome'

CSS += """
.date{font-family:BC,MJ;font-size:36px;padding:8px 22px 4px}
body:not(.tall) .photo.inv{height:400px}
.cta{margin-top:34px;background:var(--blue);color:#fff;border-radius:22px;padding:26px 34px 18px;font-family:MJ;font-weight:700;font-size:38px;line-height:1.35}
.cta small{display:block;font-weight:400;font-size:28px;opacity:.92;margin-top:6px}
.pt.no i{background:#a8322a}
.warn{margin-top:30px;border:4px solid #a8322a;border-radius:22px;padding:22px 30px 16px;font-family:BC,MJ;font-size:32px;line-height:1.45;color:#5c1712;background:rgba(255,255,255,.5)}
.warn b{font-family:MJ;font-weight:700;color:#a8322a}
.lead{font-family:BC,MJ;font-size:36px;line-height:1.45;margin-top:30px;color:var(--ink)}
body.tall{height:1920px}
body.tall .photo{height:760px}
body.tall .head.hp{margin-top:30px;padding:40px 44px 32px}
body.tall h1.hsm{font-size:72px}
body.tall .sub.ssm{font-size:40px;margin-top:34px}
body.tall .cta{font-size:46px;margin-top:50px}
body.tall .cta small{font-size:32px}
"""

LOGO_REL = 'brand/logo.jpg'
PHOTO = '../assets/library/landscape.jpg'
CREDIT = 'Shino jacob koottanad / Wikimedia Commons (CC BY-SA 4.0)'

def points(items, cls=''):
    marks = ['✓'] * len(items) if cls == '' else ['✕'] * len(items)
    return '<div class="pts">' + ''.join(f'<div class="pt {cls}"><i>{m}</i><div>{t}</div></div>' for m, t in zip(marks, items)) + '</div>'

INVITE = (f'<div class="photo inv"><img src="{PHOTO}" style="object-position:center 60%">'
          f'<span class="pcredit">ചിത്രം: {CREDIT}</span></div>'
          '<div class="head hp"><h1 class="hsm">നിങ്ങളുടെ നാട്ടിലെ വാർത്ത ഞങ്ങൾക്ക് അയക്കൂ</h1>'
          '<p>News Attappadi വാർത്താ കൂട്ടായ്മ</p></div>'
          '<div class="sub ssm">അഗളി, ഷോളയൂർ, പുതൂർ പഞ്ചായത്തുകളിലെ സംഭവങ്ങളും ഫോട്ടോകളും അറിയിപ്പുകളും WhatsApp വഴി അയക്കൂ. '
          'നിങ്ങളുടെ പേര് credit ആയി നൽകും.</div>'
          '<div class="cta">ഗ്രൂപ്പിൽ ചേരാൻ താഴെയുള്ള ലിങ്കിൽ ക്ലിക്ക് ചെയ്യൂ<small>നിങ്ങളാണ് അട്ടപ്പാടിയുടെ കണ്ണും കാതും</small></div>')

POSTERS = {
    'wa1-invite': INVITE,
    'wa2-what-to-send': ('<div class="head"><h2>എന്തൊക്കെ വാർത്തകൾ അയക്കാം?</h2><p>നാട്ടിൽ നടക്കുന്ന എല്ലാം</p></div>'
        + points(['<strong>കാട്ടാന, കാട്ടുമൃഗ ശല്യം,</strong> കൃഷിനാശം',
                  '<strong>റോഡ്, കറന്റ്, കുടിവെള്ളം</strong> എന്നിവയുടെ പ്രശ്നങ്ങൾ',
                  '<strong>പഞ്ചായത്ത്, സർക്കാർ അറിയിപ്പുകൾ,</strong> ക്യാമ്പുകൾ, പരിപാടികൾ',
                  '<strong>ഉത്സവം, സ്കൂൾ, കായികം,</strong> നേട്ടങ്ങൾ, മരണ അറിയിപ്പ്'])),
    'wa3-how-to-send': ('<div class="head"><h2>വാർത്ത അയക്കുമ്പോൾ ഇത് കൂടി എഴുതുക</h2><p>4 കാര്യങ്ങൾ മതി</p></div>'
        + '<div class="pts">' + ''.join(f'<div class="pt"><i>{n}</i><div>{t}</div></div>' for n, t in enumerate([
              '<strong>എന്ത് സംഭവിച്ചു?</strong> ചുരുക്കി, സത്യസന്ധമായി',
              '<strong>എവിടെ?</strong> ഊര് / സ്ഥലം / പഞ്ചായത്ത്',
              '<strong>എപ്പോൾ?</strong> തീയതിയും സമയവും',
              '<strong>നിങ്ങളുടെ പേര്</strong> + നിങ്ങൾ എടുത്ത ഫോട്ടോ / വീഡിയോ'], 1)) + '</div>'
        + '<div class="lead">പേര് പുറത്ത് പറയേണ്ടെങ്കിൽ Admin-ന് personal ആയി അയക്കൂ.</div>'),
    'wa4-rules': ('<div class="head"><h2>ഗ്രൂപ്പിൽ അയക്കരുത്</h2><p>എല്ലാ വാർത്തയും പരിശോധിച്ച ശേഷമേ പ്രസിദ്ധീകരിക്കൂ</p></div>'
        + points(['<strong>ഉറപ്പില്ലാത്ത വാർത്ത,</strong> കിംവദന്തി',
                  '<strong>മറ്റ് ചാനലുകളുടെയും പത്രങ്ങളുടെയും</strong> ഫോട്ടോ, വീഡിയോ',
                  '<strong>Forward, Good morning,</strong> പരസ്യം, രാഷ്ട്രീയ-മത തർക്കം',
                  '<strong>ചോര കാണുന്ന ചിത്രങ്ങൾ,</strong> അപകടത്തിൽപ്പെട്ട കുട്ടികളുടെ മുഖം'], 'no')
        + '<div class="warn"><b>സുരക്ഷ ആദ്യം:</b> ആന ഇറങ്ങിയ സ്ഥലത്തോ അപകട സ്ഥലത്തോ ഫോട്ടോ എടുക്കാൻ അടുത്തേക്ക് പോകരുത്.</div>'),
}

LINK = 'chat.whatsapp.com/GfCtDsKvpep3Dk57UGE9PL'
CSS += """
.qrbox{margin:40px auto 0;width:560px;background:#fff;border:4px solid var(--navy);border-radius:28px;padding:26px;text-align:center}
.qrbox img{width:500px;height:500px;display:block}
.qlink{text-align:center;font-family:BC;font-weight:600;font-size:34px;color:var(--navy);margin-top:24px;letter-spacing:.5px}
.qhint{text-align:center;font-family:BC,MJ;font-size:32px;color:var(--grey);margin-top:14px;line-height:1.4}
body.tall .qrbox{width:760px;margin-top:70px}
body.tall .qrbox img{width:700px;height:700px}
body.tall .qlink{font-size:40px;margin-top:34px}
body.tall .qhint{font-size:38px}
"""
QR = ('<div class="head"><h2>സ്കാൻ ചെയ്ത് ഗ്രൂപ്പിൽ ചേരൂ</h2><p>നാട്ടിലെ വാർത്തകൾ ഞങ്ങൾക്ക് അയക്കൂ</p></div>'
      '<div class="qrbox"><img src="../assets/qr/whatsapp-group.png"></div>'
      f'<div class="qlink">{LINK}</div>'
      '<div class="qhint">ഫോണിലെ ക്യാമറ കൊണ്ട് QR code സ്കാൻ ചെയ്യൂ</div>')
POSTERS['wa5-join-qr'] = QR

out = pathlib.Path(sys.argv[1]).resolve(); out.mkdir(parents=True, exist_ok=True)
jobs = [(k, v, 1350, '') for k, v in POSTERS.items()] + [('wa1-invite-status', INVITE, 1920, 'tall'), ('wa5-join-qr-status', QR, 1920, 'tall')]
for name, body, h, cls in jobs:
    html = (f'<!DOCTYPE html><html lang="ml"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body class="{cls}">{PAPER}<div class="wrap"><span class="date">WhatsApp കൂട്ടായ്മ</span>{body}</div>{FOOT}</body></html>')
    f = D / f'_{name}.html'; f.write_text(html, encoding='utf-8')
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--window-size=1080,{h}',
                    '--virtual-time-budget=3000', f'--screenshot={out}/{name}.png', f'file://{f}'], capture_output=True)
    f.unlink()
    print('built', name)
