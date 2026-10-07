"""Validate the delivered static site's SEO relationships, rather than tag presence.

Requires Python + lxml + Pillow for local maintenance. Vercel builds use Node only.
Run `python3 scripts/seo-check.py` or pass `dist` to inspect the built site.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter, deque
from datetime import date
import json
import sys
from lxml import html, etree
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / (sys.argv[1] if len(sys.argv) > 1 else '.')
LANGS = ('fa', 'en', 'ar')
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
sitemap = etree.parse(str(ROOT / 'sitemap.xml'))
urls = sitemap.xpath('//s:url/s:loc/text()', namespaces=NS)
expected_routes = json.loads((PROJECT / 'content/routes.json').read_text())
assert len(urls) == len(set(urls)) == len(expected_routes), 'Sitemap must list every unique canonical page'
origin = urlsplit(urls[0]).scheme + '://' + urlsplit(urls[0]).netloc
assert origin.startswith('https://')
routes = {urlsplit(u).path for u in urls}
assert '/' in routes and '/fa/' not in routes
assert all(r == '/' or r.endswith('/') for r in routes)

def physical(route):
    return ROOT / route.lstrip('/') / 'index.html' if route.endswith('/') else ROOT / route.lstrip('/')

docs = {route: html.parse(str(physical(route))) for route in routes}
titles = set()
descriptions = set()
edges = {r: set() for r in routes}
checks = Counter()

def asset(url):
    parts = urlsplit(url)
    assert not parts.netloc or parts.scheme + '://' + parts.netloc == origin, url
    p = ROOT / unquote(parts.path.lstrip('/'))
    assert p.is_file(), f'Missing asset: {url}'
    return p

for route, dom in docs.items():
    lang = 'fa' if route == '/' else route.split('/')[1]
    assert dom.xpath('string(/html/@lang)') == lang
    assert dom.xpath('string(/html/@dir)') == ('ltr' if lang == 'en' else 'rtl')
    assert len(dom.xpath('//main')) == len(dom.xpath('//h1')) == 1, route
    assert dom.xpath('//main[@id="main"]//h1'), route
    assert len(dom.xpath('//head/title')) == 1
    title = dom.xpath('string(//head/title)')
    desc = dom.xpath('string(//head/meta[@name="description"]/@content)')
    assert title and title not in titles, f'Duplicate title: {route}'
    assert desc and desc not in descriptions, f'Duplicate description: {route}'
    assert desc == ' '.join(desc.split()) and desc.endswith('.'), f'Unfinished description: {route}'
    assert len(desc) >= 60, f'Description too vague: {route}'
    titles.add(title); descriptions.add(desc)
    canonical = origin + route
    assert dom.xpath('//head/link[@rel="canonical"]/@href') == [canonical]
    robots = dom.xpath('string(//head/meta[@name="robots"]/@content)')
    assert ('noindex' in robots) or ('index' in robots and 'max-image-preview:large' in robots)
    path = '' if route == '/' else route.split('/', 2)[2].strip('/')
    expected = {l: (origin + '/' if l == 'fa' and not path else origin + '/' + l + '/' + (path + '/' if path else '')) for l in LANGS}
    expected['x-default'] = expected['fa']
    alts = {e.get('hreflang'): e.get('href') for e in dom.xpath('//head/link[@rel="alternate"]')}
    assert alts == expected, f'Incorrect hreflang targets: {route}'
    for l in LANGS:
        peer = docs[urlsplit(alts[l]).path]
        assert peer.xpath(f'//head/link[@hreflang="{lang}"]/@href') == [canonical], f'Missing return link: {route}'
    entry = sitemap.xpath('//s:url[s:loc=$url]', url=canonical, namespaces=NS)[0]
    assert {e.get('hreflang'): e.get('href') for e in entry.findall('x:link', namespaces=NS)} == alts
    modified = entry.findtext('s:lastmod', namespaces=NS)
    assert date.fromisoformat(modified) <= date.today()
    ids = dom.xpath('//@id'); assert len(ids) == len(set(ids)), f'Duplicate DOM IDs: {route}'
    for e in dom.xpath('//*[@href or @src]'):
        for attr in ('href', 'src'):
            value = e.get(attr)
            if not value: continue
            target = urlsplit(value)
            if target.scheme in ('tel', 'mailto') or (target.netloc and target.scheme + '://' + target.netloc != origin): continue
            dest = target.path or route
            if dest.startswith('/api/'): continue
            if dest in docs:
                if attr == 'href': edges[route].add(dest)
                if target.fragment:
                    assert unquote(target.fragment) in docs[dest].xpath('//@id'), f'Broken fragment: {route} -> {value}'
            else:
                asset(value)
            checks['internal_links_and_assets'] += 1
    for image in dom.xpath('//img'):
        assert image.get('alt') is not None, f'Missing alt: {route}'
        assert image.get('alt') or image.get('aria-hidden') == 'true', f'Empty alt on nondecorative image: {route}'
        with Image.open(asset(image.get('src'))) as im:
            assert (int(image.get('width')), int(image.get('height'))) == im.size, f'Incorrect image dimensions: {route}'
        if image.get('fetchpriority') == 'high':
            assert image.get('fetchpriority') == 'high' and image.get('loading') != 'lazy'
        checks['visible_images'] += 1
    og = {e.get('property'): e.get('content') for e in dom.xpath('//meta[@property]')}
    assert og['og:url'] == canonical and og['og:description'] == desc
    assert og['og:title'] == title and og['og:site_name'] and og['og:image:alt']
    with Image.open(asset(og['og:image'])) as im:
        assert im.size == (int(og['og:image:width']), int(og['og:image:height'])) == (1200, 630)
    assert dom.xpath('string(//meta[@name="twitter:card"]/@content)') == 'summary_large_image'
    assert dom.xpath('string(//meta[@name="twitter:image"]/@content)') == og['og:image']
    assert '&amp;amp;' not in physical(route).read_text(), f'Double-escaped entity: {route}'
    graph = json.loads(dom.xpath('//script[@type="application/ld+json"]/text()')[0])['@graph']
    nodes = {n['@id']: n for n in graph}
    assert len(nodes) == len(graph), f'Duplicate schema IDs: {route}'
    def refs(value):
        if isinstance(value, dict):
            if set(value) == {'@id'}: assert value['@id'] in nodes, f'Unresolved schema node: {route}'
            for v in value.values(): refs(v)
        elif isinstance(value, list):
            for v in value: refs(v)
    refs(graph)
    page = nodes[canonical + '#page']
    assert page['@type'] in ('WebPage', 'CollectionPage') and page['url'] == canonical
    org = nodes[origin + '/#organization']
    with Image.open(asset(org['logo']['url'])) as im:
        assert im.size == (512, 512)
    assert nodes[origin + '/#website']['url'] == origin + '/'
    if path:
        crumb = nodes[canonical + '#breadcrumb']['itemListElement']
        visible = dom.xpath('//nav[@class="crumb"]/*[self::a or @aria-current="page"]')
        assert [n['name'] for n in crumb] == [''.join(e.itertext()) for e in visible]
        assert [n['position'] for n in crumb] == list(range(1, len(crumb) + 1))
        assert crumb[-1]['item'] == canonical
    if path.startswith('services/'):
        service = nodes[canonical + '#service']
        assert service['@type'] == 'Service' and service['provider']['@id'] == org['@id']
        assert 'inLanguage' not in service and 'isPartOf' not in service
        checks['service_entities'] += 1
    if path.startswith('guides/'):
        article = nodes[canonical + '#article']
        assert article['mainEntityOfPage']['@id'] == page['@id']
        assert article['author']['@id'] == org['@id'] and article['publisher']['@id'] == org['@id']
        assert article['headline'] == dom.xpath('string(//main//h1)')
        assert article['dateModified'] == dom.xpath('string(//time/@datetime)') == modified
        assert urlsplit(article['image']['url']).path in dom.xpath('//main//img/@src'), f'Article image must be visible: {route}'
        assert dom.xpath('//nav[@class="toc"]//a')
        checks['article_entities'] += 1
    assert dom.xpath('//main//img'), f'Page lacks a topic image: {route}'
    for srcset in dom.xpath('//@srcset'):
        for candidate in srcset.split(','):
            asset(candidate.strip().split()[0])
            checks['responsive_image_candidates'] += 1
    image_locations=entry.xpath('i:image/i:loc/text()', namespaces={'i':'http://www.google.com/schemas/sitemap-image/1.1'})
    assert len(image_locations)==1
    asset(image_locations[0])
    checks['canonical_pages'] += 1

visited = {'/'}; pending = deque(['/'])
while pending:
    for dest in edges[pending.popleft()] - visited:
        visited.add(dest); pending.append(dest)
assert visited == routes, f'Orphan pages: {routes - visited}'
redirects = {r['source']: r for r in json.loads((PROJECT / 'vercel.json').read_text())['redirects']}
assert redirects['/fa/']['destination'] == '/' and redirects['/fa/']['permanent']
assert (ROOT / 'fa/index.html').read_bytes() == (ROOT / 'index.html').read_bytes()
assert 'noindex' in (ROOT / '404.html').read_text()
assert '@import' not in (ROOT / 'style.css').read_text()
assert not (ROOT / 'reference').exists() if ROOT.name == 'dist' else True
checks['reachable_pages'] = len(visited)
print('PASS: ' + json.dumps(dict(checks), ensure_ascii=False))
