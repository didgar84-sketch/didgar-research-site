"""Create an offline, single-file preview of all canonical pages.

The deployable SEO site remains the multi-page Vercel package. The preview is
deliberately noindex; fragment navigation cannot replace crawlable page URLs.
"""
from pathlib import Path
from urllib.parse import urlsplit, urlencode
from copy import deepcopy
import base64
import json
import re
import sys
import mimetypes
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'dist' if (ROOT / 'dist/index.html').is_file() else ROOT
OUTPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / 'deliverables/didgar-preview.html'
routes = json.loads((ROOT / 'content/routes.json').read_text())
assert len(routes) == len(set(routes)) and len(routes) > 0

assets = {}
templates = []
home = None
home_doc = None
for route in routes:
    file = SOURCE / route.lstrip('/') / 'index.html'
    doc = html.parse(str(file))
    body = doc.find('body')
    for e in body.xpath('.//a[@href]'):
        url = urlsplit(e.get('href'))
        if url.scheme or url.netloc:
            continue
        dest = url.path or route
        if dest.startswith('/assets/downloads/'):
            asset=(SOURCE/dest.lstrip('/')).resolve()
            assert asset.is_relative_to((SOURCE/'assets/downloads').resolve()) and asset.is_file(), dest
            mime='text/markdown;charset=utf-8' if asset.suffix=='.md' else mimetypes.guess_type(asset.name)[0] or 'application/octet-stream'
            e.set('href','data:'+mime+';base64,'+base64.b64encode(asset.read_bytes()).decode())
            continue
        if dest == '/fa/': dest = '/'
        if dest in routes:
            e.set('href', '#' + dest + ('?' + urlencode({'section': url.fragment}) if url.fragment else ''))
    for image in body.xpath('.//img[@src]'):
        filename = image.get('src').lstrip('/')
        if filename.startswith('assets/images/'):
            filename=re.sub(r'-(480|800)\.webp$','-1200.webp',filename)
            image.set('width','1200'); image.set('height','800')
        if filename not in assets:
            extension = Path(filename).suffix.lstrip('.')
            assets[filename] = 'data:image/' + extension + ';base64,' + base64.b64encode((SOURCE / filename).read_bytes()).decode()
        image.set('data-image', filename)
        image.attrib.pop('src')
        image.attrib.pop('srcset',None); image.attrib.pop('sizes',None)
    # One full-size WebP per subject is sufficient for the offline edition.
    for source in body.xpath('.//picture/source'):
        # source is void in HTML5, but lxml's HTML parser can place the
        # following img inside it. Removing the whole subtree deletes the
        # photograph. Unwrap only the source tag and preserve its children.
        source.drop_tag()
    assert all(len(p.xpath('./img')) == 1 for p in body.xpath('.//picture')), f'{route}: offline picture lost its img'
    template = etree.Element('template', {
        'data-route': route,
        'data-lang': doc.getroot().get('lang'),
        'data-dir': doc.getroot().get('dir'),
        'data-title': doc.xpath('string(//head/title)'),
        'data-description': doc.xpath('string(//head/meta[@name="description"]/@content)'),
        'data-canonical': doc.xpath('string(//head/link[@rel="canonical"]/@href)'),
    })
    for child in body:
        template.append(deepcopy(child))
    templates.append(etree.tostring(template, encoding='unicode', method='html'))
    if route == '/':
        home = deepcopy(body)
        home_doc = doc
        for image in home.xpath('.//img[@data-image]'):
            image.set('src', assets[image.get('data-image')])
        # Keep native in-page anchors available on the initial page without JS.
        for link in home.xpath('.//a[starts-with(@href,"#/?section=")]'):
            from urllib.parse import parse_qs
            link.set('href', '#' + parse_qs(urlsplit(link.get('href')[1:]).query)['section'][0])

css = (SOURCE / 'style.css').read_text()
# Embed the actual webfonts, so the chosen Persian/Arabic faces work offline.
def embed_font(match):
    filename = match.group(1)
    data = base64.b64encode((SOURCE / filename.lstrip('/')).read_bytes()).decode()
    return "url('data:font/woff2;base64," + data + "')"
css = re.sub(r"url\(['\"](/assets/fonts/[^'\"]+\.woff2)['\"]\)", embed_font, css)
font_licenses = [
    {'family': family, 'license': (SOURCE / 'assets/fonts' / ('OFL-' + family + '.txt')).read_text()}
    for family in ('Vazirmatn', 'Cairo')
]
app = (SOURCE / 'app.js').read_text()
favicon = 'data:image/svg+xml;base64,' + base64.b64encode((SOURCE / 'favicon.svg').read_bytes()).decode()
head = etree.Element('head')
for attrs in [
    {'charset': 'utf-8'},
    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'},
    {'name': 'description', 'content': home_doc.xpath('string(//meta[@name="description"]/@content)')},
    {'name': 'robots', 'content': 'noindex, follow'},
    {'name': 'theme-color', 'content': '#071c2c'},
]:
    etree.SubElement(head, 'meta', attrs)
etree.SubElement(head, 'title').text = home_doc.xpath('string(//title)')
etree.SubElement(head, 'link', rel='icon', href=favicon)
etree.SubElement(head, 'link', rel='canonical', href=home_doc.xpath('string(//link[@rel="canonical"]/@href)'))
etree.SubElement(head, 'style').text = css
nojs=etree.SubElement(head, 'noscript')
etree.SubElement(nojs, 'style').text=(SOURCE / 'nojs.css').read_text()
serialized_head = etree.tostring(head, encoding='unicode', method='html')
home_markup = ''.join(etree.tostring(child, encoding='unicode', method='html') for child in home)
router = r'''
(function(){
  'use strict';
  const host=document.getElementById('standalone-content');
  const assets=JSON.parse(document.getElementById('offline-assets').textContent);
  const templates=new Map(Array.from(document.querySelectorAll('template[data-route]'),t=>[t.dataset.route,t]));
  let current='/';
  function render(){
    if(location.hash && !location.hash.startsWith('#/'))return;
    const target=new URL(location.hash.slice(1)||'/', 'https://offline.invalid');
    const route=templates.has(target.pathname)?target.pathname:'/';
    const template=templates.get(route);
    const changed=route!==current;
    if(changed){
      host.replaceChildren(template.content.cloneNode(true));
      current=route;
      document.documentElement.lang=template.dataset.lang;
      document.documentElement.dir=template.dataset.dir;
      document.title=template.dataset.title;
      document.querySelector('meta[name="description"]').content=template.dataset.description;
      document.querySelector('link[rel="canonical"]').href=template.dataset.canonical;
      host.querySelectorAll('img[data-image]').forEach(im=>{im.src=assets[im.dataset.image];});
      window.DidgarApp.init();
    }
    requestAnimationFrame(()=>{
      const section=target.searchParams.get('section');
      const element=section?document.getElementById(section):null;
      if(element)element.scrollIntoView();
      else if(changed){
        window.scrollTo(0,0);
        const main=host.querySelector('main');
        main.setAttribute('tabindex','-1');main.focus({preventScroll:true});
      }
    });
  }
  window.addEventListener('hashchange',render);
  render();
})();
'''
output = '<!doctype html><html lang="fa" dir="rtl" data-standalone>' + serialized_head + '<body id="top">'
output += '<noscript><p class="wrap"><span lang="fa">برای مشاهده صفحات دیگر، JavaScript مرورگر را فعال کنید.</span> <span lang="en">Enable JavaScript to explore the other pages.</span></p></noscript>'
output += '<div id="standalone-content">' + home_markup + '</div>' + ''.join(templates)
output += '<script type="application/json" id="offline-assets">' + json.dumps(assets, ensure_ascii=False).replace('</', '<\\/') + '</script>'
output += '<script type="application/json" id="font-licenses">' + json.dumps(font_licenses, ensure_ascii=False).replace('</', '<\\/') + '</script>'
output += '<script>' + app + '</script><script>' + router + '</script></body></html>'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(output)
print(f'Created {OUTPUT.name}: {len(routes)} pages, embedded CSS/JS and {len(assets)} images ({OUTPUT.stat().st_size:,} bytes).')
