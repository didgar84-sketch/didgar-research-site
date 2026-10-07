"""Check release requirements across every public page and the offline edition.

This validates source structure and assets, not browser rendering or live ranks.
"""
from pathlib import Path
from lxml import html, etree
import json

ROOT = Path(__file__).resolve().parents[1]
routes = json.loads((ROOT / 'content/routes.json').read_text())
eitaa_url = json.loads((ROOT / 'content/site-content.json').read_text())['contacts']['eitaa_url']
checks = {'canonical_pages': 0, 'contact_channels': 0, 'embedded_offline_fonts': 0}
for route in routes:
    page = ROOT / 'dist' / route.lstrip('/') / 'index.html'
    dom = html.parse(str(page))
    assert not dom.xpath('//footer | //figcaption'), route
    assert not dom.xpath('//*[@class="topline" or @class="ribbon"]'), route
    assert 'پژوهش دقیق. مسیر روشن.' not in dom.xpath('string(//body)'), route
    assert dom.xpath('//header//nav[@class="languages"]/a[@lang="ar" and @dir="rtl"]'), route
    assert dom.xpath('//header//nav[@class="languages"]/a[@lang="fa" and @dir="rtl"]'), route
    assert dom.xpath('//header//img[@class="brandmark" and @alt="" and @aria-hidden="true"]'), route
    assert dom.xpath('//header//a[@class="brand"]//strong'), route
    assert dom.xpath('//button[@class="menu" and @type="button" and @aria-controls="navigation"]'), route
    for a in dom.xpath('//a[@target="_blank"]'):
        assert {'noopener', 'noreferrer'}.issubset(set(a.get('rel', '').split())), route
    for image in dom.xpath('//img[@fetchpriority="high"]'):
        assert image.get('loading') == 'eager', route
    checks['canonical_pages'] += 1
    if route in ('/', '/en/', '/ar/'):
        channels = dom.xpath('//nav[@class="contactlinks"]/a')
        assert len(channels) == 5, route
        expected = ['https://wa.me/989124067596', 'https://t.me/bestprojeh',
                    'tel:+989124067596', 'https://www.instagram.com/dr.mohsen.didgar',
                    eitaa_url]
        assert [a.get('href') for a in channels] == expected, route
        for a in channels:
            assert a.get('aria-label'), route
            assert a[0].get('class') == 'channel-label', route
            assert a[1].get('class') == 'channel-icon', route
            assert a.xpath('.//*[local-name()="svg"]'), route
            checks['contact_channels'] += 1
        assert dom.xpath('//nav[@class="contactpolicies"]/a'), route
        assert dom.xpath('//form[@id="consultation" and @method="post" and @action="/api/consultation"]'), route
        assert dom.xpath('//form[@id="consultation"]//noscript//a'), route
        if eitaa_url == 'https://eitaa.com/':
            assert channels[-1].xpath('./small'), 'Unconfirmed Eitaa destination must be clear'

css = (ROOT / 'dist/style.css').read_text()
for family in ('Vazirmatn', 'Cairo'):
    assert f"font-family:'{family}'" in css
    font = ROOT / 'dist/assets/fonts' / f'{family}-Variable.woff2'
    assert font.read_bytes()[:4] == b'wOF2'
    assert (font.parent / f'OFL-{family}.txt').is_file()
assert 'html:lang(fa),[lang="fa"]' in css
assert 'html:lang(ar),[lang="ar"]' in css
svg = etree.parse(str(ROOT / 'assets/icons/eitaa.svg'))
assert not svg.xpath('//*[local-name()="script" or local-name()="foreignObject"]')
assert not any(k.lower().startswith('on') for node in svg.iter() for k in node.attrib)

preview = ROOT.parent / 'deliverables/didgar-preview.html'
offline = preview.read_text()
assert offline.count('data:font/woff2;base64,') == 2
checks['embedded_offline_fonts'] = 2
doc = html.fromstring(offline)
assert not doc.xpath('//footer | //figcaption')
assert len(doc.xpath('//template[@data-route]')) == len(routes)
assert not doc.xpath('//script[@src] | //link[@rel="stylesheet"]')
assert doc.xpath('//meta[@name="robots" and @content="noindex, follow"]')
assert not (ROOT / 'dist/reference').exists()
assert not (ROOT / 'dist/content').exists()
assert not (ROOT / 'dist/scripts').exists()
report = {'passed': True, 'scope': 'Static source and offline release requirements', **checks}
(ROOT / 'reference/qa/release-check.json').write_text(json.dumps(report, indent=2))
print('PASS: ' + json.dumps(checks))
