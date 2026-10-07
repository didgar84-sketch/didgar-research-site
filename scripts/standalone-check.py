"""Check offline packaging, hash-route coverage and executable JS syntax.

This is an artifact check, not a substitute for a browser rendering test.
"""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import base64
import io
import json
import re
import subprocess
import sys
import hashlib
import zipfile
from lxml import html, etree
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
FILE=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'deliverables/didgar-preview.html'
SOURCE=ROOT/'dist' if (ROOT/'dist/index.html').is_file() else ROOT
doc=html.parse(str(FILE));templates=doc.xpath('//template[@data-route]')
routes=json.loads((ROOT/'content/routes.json').read_text())
by_route={t.get('data-route'):t for t in templates}
assert len(templates)==len(by_route)==len(routes) and set(by_route)==set(routes)
assert doc.xpath('string(//head/meta[@name="robots"]/@content)')=='noindex, follow'
assert not doc.xpath('//script[@src]') and not doc.xpath('//link[@rel="stylesheet"]')
assert '@import' not in doc.xpath('string(//head/style)')
css=doc.xpath('string(//head/style)')
fonts=[base64.b64decode(x) for x in re.findall(r'data:font/woff2;base64,([A-Za-z0-9+/=]+)',css)]
assert len(fonts)==2
for family in ('Vazirmatn','Cairo'):
    assert (ROOT/'assets/fonts'/f'{family}-Variable.woff2').read_bytes() in fonts
assert not doc.xpath('//picture/source[@srcset]')
assets=json.loads(doc.xpath('string(//script[@id="offline-assets"])'))
for value in assets.values():
    with Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))) as im:
        im.verify()
def image_key(src):
    return re.sub(r'-(480|800)\.webp$', '-1200.webp', src.lstrip('/'))
image_count=0
picture_count=0
download_count=0
for route,t in by_route.items():
    lang='fa' if route=='/' else route.split('/')[1]
    assert t.get('data-lang')==lang and t.get('data-dir')==('ltr' if lang=='en' else 'rtl')
    assert len(t.xpath('.//main'))==len(t.xpath('.//h1'))==1
    ids=t.xpath('.//@id');assert len(ids)==len(set(ids))
    source=html.parse(str(SOURCE/route.lstrip('/')/'index.html'))
    expected=[image_key(e.get('src')) for e in source.xpath('//body//img')]
    actual=[e.get('data-image') for e in t.xpath('.//img')]
    assert actual==expected, f'{route}: displayed image elements lost or reordered; expected {len(expected)}, got {len(actual)}'
    pictures=t.xpath('.//picture')
    assert len(pictures)==len(source.xpath('//body//picture')), f'{route}: picture containers lost'
    assert all(len(p.xpath('./img'))==1 for p in pictures), f'{route}: empty picture container'
    assert not t.xpath('.//picture/source'), f'{route}: unnecessary responsive source left in offline edition'
    source_downloads=source.xpath('//body//a[@download]')
    offline_downloads=t.xpath('.//a[@download]')
    assert len(source_downloads)==len(offline_downloads), f'{route}: missing offline downloads'
    for original,offline in zip(source_downloads,offline_downloads):
        target=SOURCE/original.get('href').lstrip('/')
        href=offline.get('href')
        assert href.startswith('data:') and ';base64,' in href
        payload=base64.b64decode(href.split(',',1)[1])
        assert payload==target.read_bytes(), f'{route}: changed download bytes'
        if target.suffix=='.zip':
            assert href.startswith('data:application/zip;base64,')
            with zipfile.ZipFile(io.BytesIO(payload)) as archive: assert archive.testzip() is None
        download_count+=1
    image_count+=len(actual)
    picture_count+=len(pictures)
    for e in t.xpath('.//img'):
        assert e.get('data-image') in assets
        assert not e.get('srcset')
    for href in t.xpath('.//a/@href'):
        target=urlsplit(href)
        if target.scheme or target.netloc:continue
        assert href.startswith('#/'),href
        local=urlsplit(href[1:]);assert local.path in by_route,href
        section=parse_qs(local.query).get('section',[None])[0]
        if section:assert section=='top' or section in by_route[local.path].xpath('.//@id'),href
home=doc.xpath('//div[@id="standalone-content"]')
assert len(home)==1
home=home[0]
assert [e.get('data-image') for e in home.xpath('.//img')]==[e.get('data-image') for e in by_route['/'].xpath('.//img')]
for image in home.xpath('.//img'):
    assert image.get('src')==assets[image.get('data-image')], 'Initial home image must be embedded directly, without JavaScript or network'
assert all(len(p.xpath('./img'))==1 for p in home.xpath('.//picture')), 'Initial home contains an empty picture'
for script in doc.xpath('//script[not(@type)]'):
    result=subprocess.run(['node','--check','--input-type=commonjs'],input=script.text,encoding='utf8',capture_output=True)
    assert result.returncode==0,result.stderr
report={'passed':True,'pages':len(routes),'images':image_count,'pictures':picture_count,'embeddedHomeImages':len(home.xpath('.//img')),'exactDownloadLinks':download_count,'fonts':2,'javascriptSyntax':True,'sha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),'browserRendering':False}
(ROOT/'reference/qa').mkdir(parents=True,exist_ok=True)
(ROOT/'reference/qa/standalone-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(routes)} offline templates, {image_count} preserved images, {download_count} exact embedded downloads, initial home images, routes/fragments, fonts and JavaScript syntax.')
