"""Generate the canonical, fully rendered trilingual research website.

Edit content/site-content.json; run npm run generate, then npm run build.
There are no client-only article bodies, invented authors or fabricated reviews.
"""
from pathlib import Path
from lxml import html, etree
from urllib.parse import urlsplit
import html as H, json, math, re
from template_content import template_prompts
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'content/site-content.json').read_text())
T=D['translations']; LANGS=('fa','en','ar'); ORIGIN='https://dr17.vercel.app'
UPDATED=D['revision']; ROUTES=[]; PAGE_IMAGES={}; LASTMOD={}
CONTACTS=D.get('contacts', {'eitaa_url':'https://eitaa.com/'})
eitaa_address=urlsplit(CONTACTS['eitaa_url'])
if eitaa_address.scheme!='https' or eitaa_address.netloc not in ('eitaa.com','web.eitaa.com') or eitaa_address.fragment:
    raise ValueError('Eitaa URL must be an HTTPS address on eitaa.com or web.eitaa.com')
SHORT={'fa':'دکتر دیدگر','en':'Dr. Didgar','ar':'الدكتور ديدگر'}
LOCALES={'fa':'fa_IR','en':'en_US','ar':'ar_AR'}

def esc(s): return H.escape(str(s),quote=True)
def pick(lang,fa,en,ar): return {'fa':fa,'en':en,'ar':ar}[lang]
def text(e): return ' '.join(e.text_content().split())
def serialize(e): return etree.tostring(e,encoding='unicode',method='html')
def url(lang,path=''):
    path=path.strip('/')
    return '/' if lang=='fa' and not path else '/'+lang+'/'+(path+'/' if path else '')
def crumbs(lang,path,title):
    items=[(T[lang]['home'],url(lang))]
    if path.startswith('guides/'): items.append((T[lang]['nav'][1],url(lang,'guides')))
    if path.startswith('services/'): items.append((T[lang]['nav'][0],url(lang)+'#services'))
    if path: items.append((title,url(lang,path)))
    return items

def picture(lang,subject,css='',priority=False,card=False):
    width=480 if card else 1200; height=320 if card else 800
    sizes='(max-width: 520px) calc(100vw - 36px), (max-width: 820px) calc((100vw - 58px)/2), (max-width: 1240px) calc((100vw - 108px)/3), 380px' if card else '(max-width: 820px) calc(100vw - 36px), 760px'
    if css=='herophoto': sizes='(max-width: 820px) calc(100vw - 36px), (max-width: 1300px) 45vw, 540px'
    src=lambda ext:', '.join(f'/assets/images/{subject}-{w}.{ext} {w}w' for w in (480,800,1200))
    attrs='fetchpriority="high" loading="eager"' if priority else 'loading="lazy"'
    return f'<picture class="{css}"><source type="image/avif" srcset="{src("avif")}" sizes="{sizes}"><img src="/assets/images/{subject}-{width}.webp" srcset="{src("webp")}" sizes="{sizes}" width="{width}" height="{height}" {attrs} decoding="async" alt="{esc(D["photo_alts"][lang][subject])}"></picture>'

def head(lang,path,kind='WebPage',subject='library',article=None):
    title,desc=D['meta'][lang][path]; full=title+' | '+SHORT[lang]; canonical=ORIGIN+url(lang,path)
    orgid=ORIGIN+'/#organization'; siteid=ORIGIN+'/#website'; pageid=canonical+'#page'
    org={'@type':'Organization','@id':orgid,'name':T['fa']['brand'],'alternateName':[T['en']['brand'],T['ar']['brand']],'url':ORIGIN+'/','logo':{'@type':'ImageObject','url':ORIGIN+'/assets/logo.png','width':512,'height':512},'telephone':'+989124067596','sameAs':['https://t.me/bestprojeh','https://www.instagram.com/dr.mohsen.didgar'],'contactPoint':{'@type':'ContactPoint','telephone':'+989124067596','contactType':'customer support','availableLanguage':list(LANGS)}}
    website={'@type':'WebSite','@id':siteid,'url':ORIGIN+'/','name':T['fa']['brand'],'alternateName':[T['en']['brand'],T['ar']['brand'],SHORT['fa']],'inLanguage':list(LANGS),'publisher':{'@id':orgid}}
    page={'@type':'CollectionPage' if path in ('guides','resources','toolkit','learning-paths','glossary') else 'WebPage','@id':pageid,'url':canonical,'name':title,'description':desc,'inLanguage':lang,'dateModified':article['revised'] if article else UPDATED,'isPartOf':{'@id':siteid},'primaryImageOfPage':{'@type':'ImageObject','url':ORIGIN+f'/assets/images/{subject}-1200.webp','width':1200,'height':800}}
    graph=[org,website,page]
    if path:
        cid=canonical+'#breadcrumb'; page['breadcrumb']={'@id':cid}
        graph.append({'@type':'BreadcrumbList','@id':cid,'itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':ORIGIN+href} for i,(name,href) in enumerate(crumbs(lang,path,title))]})
    if kind=='Article':
        aid=canonical+'#article'; page['mainEntity']={'@id':aid}
        graph.append({'@type':'Article','@id':aid,'url':canonical,'headline':title,'description':desc,'inLanguage':lang,'mainEntityOfPage':{'@id':pageid},'author':{'@type':'Organization','@id':orgid,'name':T['fa']['brand'],'url':ORIGIN+'/#about'},'publisher':{'@id':orgid},'isAccessibleForFree':True,'dateModified':article['revised'],'image':{'@type':'ImageObject','url':ORIGIN+f'/assets/images/{subject}-1200.webp','width':1200,'height':800},'articleSection':D['categories'][lang][article['category']],'citation':[D['source_registry'][k]['url'] for k in article['sources']]})
        graph[-1]['wordCount']=len(text(html.fragment_fromstring(article['body'],create_parent='div')).split())
        if article.get('created'): graph[-1]['dateCreated']=article['created']
    if kind=='Service':
        sid=canonical+'#service'; page['mainEntity']={'@id':sid}
        graph.append({'@type':'Service','@id':sid,'url':canonical,'name':title,'description':desc,'serviceType':title,'provider':{'@id':orgid},'mainEntityOfPage':{'@id':pageid}})
    if path=='guides':
        lid=canonical+'#guides'; page['mainEntity']={'@id':lid}
        graph.append({'@type':'ItemList','@id':lid,'numberOfItems':len(D['articles'][lang]),'itemListElement':[{'@type':'ListItem','position':i+1,'name':a['title'],'url':ORIGIN+url(lang,'guides/'+a['slug'])} for i,a in enumerate(D['articles'][lang])]})
    alt=''.join(f'<link rel="alternate" hreflang="{l}" href="{ORIGIN+url(l,path)}">' for l in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+url("fa",path)}">'
    font='' if lang=='en' else f'<link rel="preload" href="/assets/fonts/{"Vazirmatn" if lang=="fa" else "Cairo"}-Variable.woff2" as="font" type="font/woff2" crossorigin>'
    social=f'{ORIGIN}/assets/images/{subject}-social.jpg' if path else f'{ORIGIN}/assets/social-{lang}.jpg'
    jsonld=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('</','<\\/')
    modified=f'<meta property="article:modified_time" content="{article["revised"]}">' if article else ''
    ogalts=''.join(f'<meta property="og:locale:alternate" content="{LOCALES[l]}">' for l in LANGS if l!=lang)
    return f'''<!doctype html><html lang="{lang}" dir="{'ltr' if lang=='en' else 'rtl'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(full)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index, follow, max-image-preview:large"><meta name="theme-color" content="#071c2c"><link rel="canonical" href="{canonical}">{alt}<meta property="og:title" content="{esc(full)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="{esc(T[lang]['brand'])}"><meta property="og:locale" content="{LOCALES[lang]}">{ogalts}<meta property="og:image" content="{social}"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{esc(D['photo_alts'][lang][subject])}">{modified}<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(full)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{social}"><meta name="twitter:image:alt" content="{esc(D['photo_alts'][lang][subject])}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/assets/favicon-96.png" sizes="96x96" type="image/png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">{font}<link rel="stylesheet" href="/style.css"><script type="application/ld+json">{jsonld}</script><script src="/app.js" defer></script><noscript><link rel="stylesheet" href="/nojs.css"></noscript></head><body id="top">'''

def header(lang,path):
    t=T[lang]
    items=[(url(lang,'guides'),t['nav'][1]),(url(lang,'learning-paths'),t['learningpaths']),(url(lang,'resources'),t['resources']),(url(lang,'toolkit'),t['toolkit']),(url(lang)+'#services',t['nav'][0])]
    links=''.join(f'<a href="{href}"'+(' aria-current="page"' if href==url(lang,path) else '')+f'>{esc(label)}</a>' for href,label in items)
    langs=''.join(f'<a lang="{l}" dir="{"ltr" if l=="en" else "rtl"}" href="{url(l,path)}"'+(' aria-current="page"' if l==lang else '')+f'>{label}</a>' for l,label in [('fa','فارسی'),('en','EN'),('ar','العربية')])
    return f'''<a class="skip" href="#main">{t['skip']}</a><header class="header"><div class="wrap nav"><a class="brand" href="{url(lang)}"><img class="brandmark" src="/assets/logo.png" width="512" height="512" alt="" aria-hidden="true"><span><strong>{t['brand']}</strong><small lang="en">RESEARCH &amp; INSIGHT</small></span></a><nav class="navlinks" id="navigation" aria-label="{t['menu']}">{links}</nav><nav class="languages" aria-label="{pick(lang,'انتخاب زبان','Choose language','اختيار اللغة')}">{langs}</nav><a class="btn" href="{url(lang)}#contact">{t['cta']}</a><button class="menu" type="button" aria-expanded="false" aria-controls="navigation">{t['menu']}</button></div></header>'''

def footer(lang):
    t=T[lang]
    return f'<a class="top" href="#top">{t["back"]}</a></body></html>'

def contactlinks(lang):
    # Visible label first, recognizable icon underneath; one accessible link.
    icons={
      'whatsapp':'<path fill="currentColor" d="M20.5 3.5A11.9 11.9 0 0 0 1.8 17.8L.2 23.7l6-1.6A11.9 11.9 0 0 0 24 11.9c0-3.2-1.2-6.2-3.5-8.4ZM12 21.8a9.8 9.8 0 0 1-5-1.4l-.4-.2-3.5.9.9-3.4-.2-.4a9.8 9.8 0 1 1 8.2 4.5Zm5.4-7.3c-.3-.1-1.8-.9-2-1s-.5-.1-.7.2-.8 1-1 1.2-.3.2-.6.1a8 8 0 0 1-2.4-1.5 9.1 9.1 0 0 1-1.7-2.1c-.2-.3 0-.5.1-.6l.5-.5.3-.5c.1-.2 0-.4 0-.6l-.9-2.1c-.2-.5-.4-.5-.6-.5H8c-.2 0-.5.1-.7.3s-1 1-1 2.4 1 2.8 1.2 3c.1.2 2 3.1 4.9 4.3.7.3 1.2.5 1.6.6.7.2 1.3.1 1.8.1.5-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4s-.3-.2-.6-.4Z"/>',
      'telegram':'<path fill="currentColor" d="m21.6 3.5-3.1 17c-.2 1.2-.8 1.5-1.7 1l-4.7-3.5-2.3 2.2c-.2.3-.4.5-.9.5l.3-4.8L18 7.8c.4-.3-.1-.5-.5-.2L6.6 14.4l-4.7-1.5c-1-.3-1.1-1 .2-1.5L20.3 3c.9-.3 1.5.2 1.3.5Z"/>',
      'phone':'<path d="M5.5 3h3l2 5-2.5 2a15 15 0 0 0 6 6l2-2.5 5 2v3c0 1.4-1 2.5-2.5 2.5C10.4 21 3 13.6 3 5.5 3 4 4.1 3 5.5 3Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>',
      'instagram':'<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="17.5" cy="6.5" r="1.1" fill="currentColor"/>',
      'eitaa': (ROOT/'assets/icons/eitaa.svg').read_text()
    }
    telephone=pick(lang,'تماس تلفنی','Telephone call','اتصال هاتفي')
    eitaa=pick(lang,'ایتا','Eitaa','إيتا')
    official=pick(lang,'وب‌سایت رسمی ایتا','Official Eitaa website','موقع إيتا الرسمي')
    eitaa_url=CONTACTS['eitaa_url']
    items=[('whatsapp','WhatsApp','https://wa.me/989124067596','WhatsApp'),('telegram','Telegram','https://t.me/bestprojeh','Telegram'),('phone','+98 912 406 7596','tel:+989124067596',telephone+' +98 912 406 7596'),('instagram','Instagram','https://www.instagram.com/dr.mohsen.didgar','Instagram'),('eitaa',eitaa,eitaa_url,official if eitaa_url=='https://eitaa.com/' else eitaa)]
    cards=[]
    for key,label,href,accessible in items:
        external='' if key=='phone' else ' target="_blank" rel="noopener noreferrer"'
        content=icons[key]
        icon=content if content.startswith('<svg') else f'<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false">{content}</svg>'
        subtitle=f'<small>{official}</small>' if key=='eitaa' and eitaa_url=='https://eitaa.com/' else ''
        label_lang=lang if key=='eitaa' else 'en'
        cards.append(f'<a class="contactchannel channel-{key}" href="{esc(href)}" aria-label="{esc(accessible)}"{external}><span class="channel-label" lang="{label_lang}" dir="{"rtl" if label_lang in ("fa","ar") else "ltr"}">{esc(label)}</span><span class="channel-icon" aria-hidden="true">{icon}</span>{subtitle}</a>')
    return '<nav class="contactlinks" aria-label="'+pick(lang,'راه‌های ارتباط','Contact channels','قنوات التواصل')+'">'+''.join(cards)+'</nav>'

def policylinks(lang):
    return '<nav class="contactpolicies" aria-label="'+pick(lang,'سیاست‌ها و شرایط','Policies and terms','السياسات والشروط')+'">'+''.join(f'<a href="{url(lang,p)}">{T[lang][p]}</a>' for p in ('privacy','terms','editorial'))+'</nav>'

def nojs_tool(lang):
    return '<noscript><p class="note">'+pick(lang,'برای استفاده از این ابزار، JavaScript مرورگر را فعال کنید.','Enable JavaScript in your browser to use this tool.','فعّل JavaScript في المتصفح لاستخدام هذه الأداة.')+'</p></noscript>'

def hero(lang,path,subject):
    t=T[lang]; title,desc=D['meta'][lang][path]
    trail=''.join((f'<a href="{esc(href)}">{esc(name)}</a>' if i<len(crumbs(lang,path,title))-1 else f'<span aria-current="page">{esc(name)}</span>')+('<span aria-hidden="true">/</span>' if i<len(crumbs(lang,path,title))-1 else '') for i,(name,href) in enumerate(crumbs(lang,path,title)))
    return f'<section class="pagehero"><div class="wrap pageherogrid"><div><nav class="crumb" aria-label="{pick(lang,"مسیر صفحه","Breadcrumb","مسار الصفحة")}">{trail}</nav><span class="eyebrow">{t["guide"] if path.startswith("guides/") else t["brand"]}</span><h1>{esc(title)}</h1><p>{esc(desc)}</p></div><figure class="pageheroimage">{picture(lang,subject,"pagephoto",True)}</figure></div></section>'

def save(lang,path,body,kind='WebPage',subject='library',article=None):
    file=ROOT/lang/path/'index.html'; file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(head(lang,path,kind,subject,article)+header(lang,path)+body+footer(lang))
    route=url(lang,path); ROUTES.append(route); PAGE_IMAGES[route]=subject; LASTMOD[route]=article['revised'] if article else UPDATED

def guidecards(lang,limit=None):
    cards=[]
    selected=D['articles'][lang]
    if limit:
        featured=['research-proposal','literature-search','research-design','statistical-software','computational-thesis-quarto','registered-reports']
        selected=[next(a for a in selected if a['slug']==s) for s in featured][:limit]
    for i,a in enumerate(selected):
        cards.append(f'<article class="card articlecard photocard" data-searchable data-category="{a["category"]}" data-search-terms="{esc(a.get("search_terms",""))}">{picture(lang,a["image"],"cardphoto",card=True)}<div class="cardbody"><span class="label">{D["categories"][lang][a["category"]]} · {i+1:02}</span><h3><a href="{url(lang,"guides/"+a["slug"])}">{a["title"]}</a></h3><p>{esc(a["desc"])}</p><a class="cardlink" href="{url(lang,"guides/"+a["slug"])}">{T[lang]["read"]}</a></div></article>')
    return ''.join(cards)

def searchcontrols(lang,label):
    t=T[lang]
    return f'<div class="filterbar"><label class="searchbox">{label}<input data-search type="search" autocomplete="off" aria-label="{label}"></label><label class="categorybox">{t["filter"]}<select data-category-filter>{"".join(f"<option value={esc(k)}>{esc(v)}</option>" for k,v in D["categories"][lang].items())}</select></label></div>'

def form(lang):
    t=T[lang]; degrees=pick(lang,['کارشناسی','کارشناسی ارشد','دکتری','پژوهشگر مستقل'],['Undergraduate','Master’s','Doctoral','Independent researcher'],['بكالوريوس','ماجستير','دكتوراه','باحث مستقل'])
    return f'''<form id="consultation" class="form" method="post" action="/api/consultation"><div class="fields"><label class="field">{t['name']}<input name="name" autocomplete="name" required minlength="2" maxlength="100"></label><label class="field">{t['contactfield']}<input name="contact" autocomplete="email" required minlength="5" maxlength="150" dir="auto"></label><label class="field">{t['servicefield']}<select name="service">{''.join('<option>'+esc(s['title'])+'</option>' for s in D['services'][lang])}</select></label><label class="field">{t['degree']}<select name="degree">{''.join('<option>'+d+'</option>' for d in degrees)}</select></label><label class="field full">{t['deadline']}<input type="date" name="deadline"></label><label class="field full">{t['topic']}<textarea name="topic" rows="4" required minlength="10" maxlength="2000"></textarea></label></div><div class="honey" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div><label class="consent"><input type="checkbox" name="consent" required><span>{t['consent']} <a href="{url(lang,'privacy')}">{t['privacy']}</a></span></label><button class="btn" type="submit">{t['submit']}</button><small>{t['formnote']}</small>{policylinks(lang)}<div role="status" aria-live="polite"></div><noscript><p>{pick(lang,"برای درخواست مشاوره، از لینک مستقیم واتساپ استفاده کنید.","Use the direct WhatsApp link to request a consultation.","استخدم رابط واتساب المباشر لطلب الاستشارة.")}</p><a class="btn" href="https://wa.me/989124067596" target="_blank" rel="noopener noreferrer">WhatsApp: +98 912 406 7596</a></noscript></form>'''

def articlepage(lang,a):
    t=T[lang]
    fragment=html.fragment_fromstring(a['body'],create_parent='div')
    for i,h in enumerate(fragment.xpath('.//h2 | .//h3 | .//h4'),1): h.set('id',f'section-{i}')
    toc='<nav class="toc" aria-label="'+pick(lang,'فهرست راهنما','Guide contents','محتويات الدليل')+'"><h2>'+pick(lang,'در این راهنما','In this guide','في هذا الدليل')+'</h2><ul>'+''.join(f'<li><a href="#{h.get("id")}">{esc(text(h))}</a></li>' for h in fragment.xpath('.//h2 | .//h3'))+'<li><a href="#sources">'+t['sources']+'</a></li></ul></nav>'
    prose=''.join(serialize(c) for c in fragment)
    for table in fragment.xpath('.//table'):
        if not table.xpath('./caption'):
            cap=etree.Element('caption');cap.text=pick(lang,'جدول آموزشی مرتبط با این راهنما','Teaching table for this guide','جدول تعليمي لهذا الدليل');table.insert(0,cap)
        for th in table.xpath('.//th'): th.set('scope','col')
    prose=''.join(serialize(c) for c in fragment)
    minutes=max(2,math.ceil(len(text(fragment).split())/180))
    sourcehtml='<section class="sources" aria-labelledby="sources"><h2 id="sources">'+t['sources']+'</h2><p>'+t['sourcechecked']+'</p><ul>'+''.join(f'<li><a href="{D["source_registry"][k]["url"]}" lang="en" dir="ltr" target="_blank" rel="noopener noreferrer">{esc(D["source_registry"][k]["name"])}</a>'+(' <small class="source-date">'+pick(lang,'تطبیق منبع: ','Source verification: ','فحص المصدر: ')+esc(D['source_registry'][k]['checked'])+'</small>' if D['source_registry'][k].get('checked') else '')+'</li>' for k in a['sources'])+'</ul></section>'
    byslug={x['slug']:x for x in D['articles'][lang]}
    related=''.join(f'<a href="{url(lang,"guides/"+s)}">{byslug[s]["title"]}</a>' for s in a['related'])
    sid=a['service']; service=next(s for s in D['services'][lang] if s['slug']==sid)
    meta=pick(lang,'تهیه‌کننده: ','Prepared by: ','إعداد: ')+f'<a href="{url(lang)}#about">{t["brand"]}</a> · '+pick(lang,'آخرین ویرایش: ','Last revised: ','آخر تعديل: ')+f'<time datetime="{a["revised"]}">{a["revised"]}</time> · {minutes} {t["reading"]}'
    if a.get('created'): meta+=' · '+pick(lang,'ایجاد راهنما: ','Guide created: ','إنشاء الدليل: ')+f'<time datetime="{a["created"]}">{a["created"]}</time>'
    outcomes='<section class="learning-outcomes" aria-label="'+t['deliver']+'"><strong>'+t['deliver']+'</strong><ul>'+''.join('<li>'+esc(s)+'</li>' for s in a.get('outcomes',[]))+'</ul></section>'
    downloads=''.join(f'<a class="cardlink" href="/assets/downloads/{esc(d["file"])}" download="{esc(d["file"].split("/")[-1])}">{esc(d["label"])}</a>' for d in a.get('downloads',[]))
    paths=''.join(f'<a href="{url(lang,"learning-paths")}#{p["id"]}">{esc(p["title"][lang])}</a>' for p in D['learning_paths'] if p['id'] in a.get('paths',[]))
    note=pick(lang,'این راهنما برای آموزش و برنامه‌ریزی پژوهش است؛ اجرای روش را با طراحی واقعی و شیوه‌نامه مؤسسه تطبیق دهید.','This guide supports research learning and planning; align implementation with the actual design and institutional requirements.','يدعم الدليل تعلم البحث وتخطيطه؛ وائم التنفيذ مع التصميم الفعلي وتعليمات المؤسسة.')
    return '<main id="main">'+hero(lang,'guides/'+a['slug'],a['image'])+f'<section class="block"><div class="wrap reading"><article class="prose"><div class="meta">{meta}</div>{outcomes}{downloads}{toc}{prose}{sourcehtml}<div class="note">{note} <a href="{url(lang,"editorial")}">{t["editorial"]}</a></div></article><aside class="aside"><h2>{t["related"]}</h2>{related}<h3>{t["learningpaths"]}</h3>{paths}<a href="{url(lang,"glossary")}">{t["glossary"]}</a><h3>{t["nav"][0]}</h3><a href="{url(lang,"services/"+sid)}">{service["title"]}</a><a href="{url(lang,"toolkit")}">{t["toolkit"]}</a><a class="btn" href="{url(lang)}#contact">{t["cta"]}</a></aside></div></section></main>'

def workbook(lang,a):
    def md(s): return str(s).replace('|','\\|').replace('\n',' ')
    heading=pick(lang,'دفتر تصمیم و مثال آموزشی','Decision workbook and teaching example','دفتر القرارات والمثال التعليمي')
    warning=pick(lang,'مثال تکمیل‌شده فرضی است. اعداد و تصمیم‌ها نتیجۀ واقعی پژوهش نیستند؛ پرونده خود را با مجوز، روش و شیوه‌نامه مرتبط تکمیل کنید.','The completed case is fictional. Its values and decisions are not actual findings; complete your project using relevant permissions, methods and requirements.','المثال افتراضي وليس نتائج فعلية؛ أكمل مشروعك وفق الأذونات والمنهج والتعليمات.')
    labels=pick(lang,['پروژه','پژوهشگر و نقش','تاریخ و نسخه','داده‌ای که پیش از تصمیم دیده‌اید','هدف و دامنه'],['Project','Researcher and role','Date and version','Data seen before the decision','Aim and scope'],['المشروع','الباحث والدور','التاريخ والنسخة','البيانات المرئية قبل القرار','الهدف والنطاق'])
    result='# '+a['title']+'\n\n'+heading+' · '+a['revised']+'\n\n'+warning+'\n\n'
    result+='\n'.join('- '+s+': ____________________' for s in labels)+'\n\n'
    result+='## '+pick(lang,'مثال تکمیل‌شده','Completed example','مثال مكتمل')+'\n\n'
    headers=pick(lang,['مرحله/تصمیم','مثال','کنترل یا اقدام'],['Stage/decision','Example','Check or action'],['المرحلة/القرار','المثال','الفحص أو الإجراء'])
    result+='| '+' | '.join(headers)+' |\n| --- | --- | --- |\n'
    result+=''.join('| '+' | '.join(md(v) for v in row)+' |\n' for row in a['worksheet'])
    result+='\n## '+pick(lang,'پروندۀ خود را تکمیل کنید','Complete your own record','أكمل سجلك')+'\n\n'
    result+='| '+pick(lang,'موضوع | تصمیم واقعی و دلیل | پیوند شاهد و وضعیت','Topic | Actual decision and reason | Evidence link and status','الموضوع | القرار الفعلي وسببه | رابط الدليل وحالته')+' |\n| --- | --- | --- |\n'
    result+=''.join('| '+md(row[0])+' | __________ | __________ |\n' for row in a['worksheet'])
    result+='\n## '+pick(lang,'معیار پایان کار','Completion checks','فحص الاكتمال')+'\n\n'+''.join('- [ ] '+s+'\n' for s in a['outcomes'])
    result+='\n## '+pick(lang,'دفتر تغییر و محدودیت','Changes and limitations','سجل التغير والحدود')+'\n\n'
    result+='| '+pick(lang,'تاریخ | تغییر | شناخت داده در زمان تصمیم | دلیل | اثر بر ادعا | بازبین','Date | Change | Data known at decision time | Reason | Consequence for claim | Reviewer','التاريخ | التغير | البيانات المعروفة | السبب | أثره على الادعاء | المراجع')+' |\n| --- | --- | --- | --- | --- | --- |\n| __________ | __________ | __________ | __________ | __________ | __________ |\n'
    result+='\n## '+T[lang]['sources']+'\n\n'+''.join('- ['+s['name']+']('+s['url']+')\n' for k in a['sources'] for s in [D['source_registry'][k]])
    result+='\n'+pick(lang,'راهنمای مرتبط: ','Related guide: ','الدليل: ')+ORIGIN+url(lang,'guides/'+a['slug'])+'\n'
    return result

def pathcards(lang):
    return ''.join('<article class="card pathcard"><span class="number">'+str(i+1).zfill(2)+'</span><h3><a href="'+url(lang,'learning-paths')+'#'+p['id']+'">'+esc(p['title'][lang])+'</a></h3><p>'+esc(p['desc'][lang])+'</p><small>'+pick(lang,'خروجی: ','Output: ','المخرج: ')+esc(p['output'][lang])+'</small></article>' for i,p in enumerate(D['learning_paths']))

for lang in LANGS:
    t=T[lang]
    services=''.join(f'<article class="card photocard">{picture(lang,s["slug"],"cardphoto",card=True)}<div class="cardbody"><span class="number">0{i+1}</span><h3><a href="{url(lang,"services/"+s["slug"])}">{s["title"]}</a></h3><p>{esc(s["desc"])}</p><a class="cardlink" href="{url(lang,"services/"+s["slug"])}">{t["more"]}</a></div></article>' for i,s in enumerate(D['services'][lang]))
    steps=''.join(f'<div class="step"><b>0{i+1}</b><h3>{name}</h3><p>{t["steptext"][i]}</p></div>' for i,name in enumerate(t['stepnames']))
    faq=''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in D['faq'][lang])
    herofigure=picture(lang,'library','herophoto',True)
    home=f'''<main id="main"><section class="hero"><div class="wrap herogrid"><div><span class="eyebrow">{t['eyebrow']}</span><h1>{t['hero']}</h1><p>{t['intro']}</p><div class="actions"><a class="btn" href="#contact">{t['cta']}</a><a class="btn ghost" href="{url(lang,'guides')}">{t['all']}</a></div><div class="herofoot">{''.join('<span>'+v+'</span>' for v in t['pill'])}</div></div><figure class="herofigure">{herofigure}</figure></div></section><section class="block" id="services"><div class="wrap"><div class="heading"><div><span class="eyebrow">01 / {t['nav'][0]}</span><h2>{t['services']}</h2></div><p>{t['servicedesc']}</p></div><div class="grid">{services}</div></div></section><section class="block dark" id="about"><div class="wrap split"><div><span class="eyebrow">02 / {t['nav'][3]}</span><h2>{t['about']}</h2><p>{t['abouttext']}</p><ul class="checklist">{''.join('<li>'+esc(v)+'</li>' for v in t['values'])}</ul><a class="cardlink" href="{url(lang,'editorial')}">{t['editorial']}</a></div><figure class="sectionfigure">{picture(lang,'team','sectionphoto')}</figure></div></section><section class="block" id="process"><div class="wrap"><div class="heading"><div><span class="eyebrow">03 / {t['nav'][2]}</span><h2>{t['workflow']}</h2></div><a class="cardlink" href="{url(lang,'planner')}">{t['planner']}</a></div>{picture(lang,'proposal','widephoto')}<div class="steps">{steps}</div></div></section><section class="block knowledge" id="knowledge"><div class="wrap"><div class="heading"><div><span class="eyebrow">04 / {t['nav'][1]}</span><h2>{t['knowledge']}</h2></div><a class="cardlink" href="{url(lang,'guides')}">{t['all']}</a></div><p>{t['knowdesc']}</p><div class="grid">{guidecards(lang,6)}</div></div></section><section class="block resourceshome" id="resources"><div class="wrap split"><div><span class="eyebrow">05 / {t['resources']}</span><h2>{t['resources']}</h2><p>{D['meta'][lang]['resources'][1]}</p><div class="resourcecounts"><strong>28</strong><span>{t['guide']}</span><strong>34</strong><span>{t['resources']}</span></div><div class="actions"><a class="btn" href="{url(lang,'resources')}">{t['allresources']}</a><a class="btn ghost" href="{url(lang,'toolkit')}">{t['toolkit']}</a></div></div>{picture(lang,'desk','sectionphoto')}</div></section><section class="block" id="faq"><div class="wrap"><div class="heading"><h2>{t['faq']}</h2></div><div class="faqgrid">{picture(lang,'originality','faqphoto')}<div class="faq">{faq}</div></div></div></section><section class="block contact" id="contact"><div class="wrap split"><div><span class="eyebrow">06 / {t['cta']}</span><h2>{t['contact']}</h2><p>{t['contacttext']}</p>{picture(lang,'proposal','contactphoto')}{contactlinks(lang)}</div>{form(lang)}</div></section></main>'''
    # Lead with learning while retaining all service, process and contact sections.
    home_root=html.fragment_fromstring(home)
    hero_actions=home_root.xpath('./section[contains(@class,"hero")]//div[@class="actions"]/a')
    hero_actions[0].set('href',url(lang,'guides')); hero_actions[0].text=t['all']
    hero_actions[1].set('href',url(lang,'learning-paths')); hero_actions[1].text=t['learningpaths']
    path_section=html.fragment_fromstring('<section class="block learninghome" id="learning"><div class="wrap"><div class="heading"><div><span class="eyebrow">'+t['learningpaths']+'</span><h2>'+pick(lang,'از کجا شروع کنید؟','Where should you start?','من أين تبدأ؟')+'</h2></div><a class="cardlink" href="'+url(lang,'glossary')+'">'+t['glossary']+'</a></div><p>'+esc(D['meta'][lang]['learning-paths'][1])+'</p><div class="grid pathgrid">'+pathcards(lang)+'</div></div></section>')
    home_root.insert(1,path_section)
    ordered=[home_root[0]]+[home_root.xpath('./section[@id="'+key+'"]')[0] for key in ('learning','knowledge','resources','services','about','process','faq','contact')]
    for node in ordered: home_root.append(node)
    for i,node in enumerate(ordered[1:],1):
        for eyebrow in node.xpath('.//span[@class="eyebrow"]'):
            eyebrow.text=f'{i:02} / '+(eyebrow.text or '').split(' / ')[-1]
    counts=home_root.xpath('.//div[@class="resourcecounts"]/strong')
    counts[0].text=str(len(D['articles'][lang]));counts[1].text=str(len(D['resources']))
    home=serialize(home_root)
    save(lang,'',home)
    jump=f'<nav class="guide-jumps" aria-label="{t["nav"][1]}"><a href="{url(lang,"learning-paths")}">{t["learningpaths"]}</a><a href="{url(lang,"glossary")}">{t["glossary"]}</a><a href="{url(lang,"toolkit")}">{t["toolkit"]}</a></nav>'
    body='<main id="main">'+hero(lang,'guides','library')+f'<section class="block"><div class="wrap">{jump}{searchcontrols(lang,t["search"])}<p class="searchcount" role="status" aria-live="polite">{len(D["articles"][lang])}</p><div class="grid">{guidecards(lang)}</div><noscript><p>{pick(lang,"همه راهنماها بدون JavaScript نیز از پیوندهای بالا قابل مطالعه‌اند.","All guides remain readable through their links without JavaScript.","جميع الأدلة متاحة عبر روابطها دون JavaScript.")}</p></noscript></div></section></main>'
    save(lang,'guides',body,subject='library')
    for s in D['services'][lang]:
        sid=s['slug']; guides=D['service_guides'][sid]
        extra=[a['slug'] for a in D['articles'][lang] if a['service']==sid and a['slug'] not in guides][:3]
        by={a['slug']:a for a in D['articles'][lang]}
        deliver=pick(lang,['دامنه و برنامۀ کار توافق‌شده','فایل‌های قابل ویرایش یا کد متناسب با خدمت','مستندات روش، فرض‌ها و تصمیم‌ها','گزارش بازبینی و راهنمای استفاده'],['Agreed scope and work plan','Editable files or code appropriate to the service','Methods, assumptions and decision documentation','Review notes and usage guidance'],['نطاق وخطة متفق عليهما','ملفات قابلة للتحرير أو شفرة ملائمة','توثيق الطرق والافتراضات والقرارات','ملاحظات المراجعة ودليل الاستخدام'])
        prepare=pick(lang,['پرسش، رشته و مرحله فعلی پژوهش','شیوه‌نامه و مهلت مؤسسه یا نشریه','نسخه موجود متن یا داده مجاز بدون هویت اشخاص','خروجی مورد انتظار و نظرهای استاد راهنما'],['Question, discipline and current research stage','Institutional or journal requirements and deadline','Existing manuscript or permitted de-identified data','Expected deliverables and supervisor comments'],['السؤال والتخصص ومرحلة البحث','تعليمات المؤسسة أو المجلة والموعد','النص الحالي أو بيانات مسموحة منزوعة الهوية','المخرجات المطلوبة وتعليقات المشرف'])
        note=pick(lang,'دامنه، هزینه، ابزار، زمان، بازبینی و پشتیبانی در توافق کتبی مشخص می‌شوند. پژوهشگر مسئول فهم و تأیید روش و متن نهایی است.','Scope, fees, tools, timing, revisions and support are agreed in writing. Researchers retain responsibility for understanding and approving the work.','يُحدد النطاق والتكلفة والأدوات والوقت والمراجعات والدعم كتابةً، ويبقى الباحث مسؤولاً عن فهم العمل واعتماده.')
        lists=lambda items:'<ul>'+''.join('<li>'+esc(i)+'</li>' for i in items)+'</ul>'
        body='<main id="main">'+hero(lang,'services/'+sid,sid)+f'<section class="block"><div class="wrap reading"><article class="prose"><h2>{t["nav"][0]}</h2>{lists(s["items"])}<h2>{t["deliver"]}</h2>{lists(deliver)}<h2>{t["prepare"]}</h2>{lists(prepare)}<div class="note">{note}</div><h2>{t["nav"][2]}</h2><ol>{"".join("<li>"+esc(x)+"</li>" for x in t["steptext"])}</ol><h2>{t["related"]}</h2><ul>{"".join(f"<li><a href='{url(lang,'guides/'+g)}'>{esc(by[g]['title'])}</a></li>" for g in guides+extra)}</ul></article><aside class="aside"><h2>{t["cta"]}</h2><p>{t["contacttext"]}</p><a class="btn" href="{url(lang)}#contact">{t["cta"]}</a></aside></div></section></main>'
        save(lang,'services/'+sid,body,'Service',sid)
    for a in D['articles'][lang]: save(lang,'guides/'+a['slug'],articlepage(lang,a),'Article',a['image'],a)
    planner='<main id="main">'+hero(lang,'planner','proposal')+f'<section class="block"><div class="wrap"><div class="toolbox"><form id="planner"><label class="field">{t["days"]}<input type="number" name="days" min="14" max="730" step="1" value="90" required></label><div class="actions"><button class="btn" type="submit">{t["planbtn"]}</button></div></form>{nojs_tool(lang)}<div id="planresult" class="toolresult" role="status" hidden></div></div><div class="note">{t["plandesc"]}</div><a class="cardlink" href="{url(lang,'toolkit')}">{t['toolkit']}</a></div></section></main>'
    save(lang,'planner',planner,subject='proposal')
    for path in ('privacy','terms'):
        parts=D['legal'][lang][path]
        # All fonts are local; avoid an obsolete Google Fonts privacy claim.
        if path=='privacy':
            parts=[(h,p.replace('قلم‌های Google Fonts ممکن است درخواست شبکه شامل IP مرورگر ایجاد کنند.','فونت‌های فارسی و عربی در خود سایت میزبانی می‌شوند.').replace('Google Fonts may receive network requests including your browser IP.','Persian and Arabic fonts are hosted on this website.').replace('قد تُرسل Google Fonts طلبات شبكة تشمل عنوان IP للمتصفح.','تُستضاف الخطوط الفارسية والعربية داخل الموقع.')) for h,p in parts]
        body='<main id="main">'+hero(lang,path,'originality')+'<section class="block"><div class="wrap prose legal">'+''.join('<h2>'+esc(h)+'</h2><p>'+esc(p)+'</p>' for h,p in parts)+'</div></section></main>'
        save(lang,path,body,subject='originality')
    resourcecards=[]
    accesslabel=pick(lang,'راهنما یا رکورد عمومی؛ دسترسی کامل تابع شرایط منبع است.','Public guide or records; full access follows the source’s terms.','دليل أو سجلات عامة؛ يخضع الوصول الكامل لشروط المصدر.')
    for r in D['resources']:
        source=D['source_registry'][r['source']]
        resourcecards.append(f'<article class="card resourcecard" data-searchable data-category="{r["category"]}"><span class="label">{D["categories"][lang][r["category"]]}</span><h2><a href="{source["url"]}" lang="en" dir="ltr" target="_blank" rel="noopener noreferrer">{esc(source["name"])}</a></h2><p>{esc(r["desc"][lang])}</p><p class="accessnote"><strong>{t["access"]}:</strong> {accesslabel}</p><small lang="en" dir="ltr">{esc(r['access_en'])}</small></article>')
    body='<main id="main">'+hero(lang,'resources','library')+f'<section class="block"><div class="wrap"><div class="note">{t["resourcesnote"]}</div>{searchcontrols(lang,t["searchresources"])}<p class="searchcount" role="status" aria-live="polite">{len(D["resources"])}</p><div class="grid">{"".join(resourcecards)}</div></div></section></main>'
    save(lang,'resources',body,subject='library')
    # Toolkit templates use Markdown for transparent editing in any text editor.
    templates=[
      ('search-log',pick(lang,'دفتر جست‌وجوی منابع','Literature search log','سجل البحث عن المصادر'),pick(lang,['پرسش و دامنه','پایگاه و رابط','تاریخ و رشته کامل','محدودیت‌ها و تعداد','فایل خروجی و حذف تکرار'],['Question and scope','Database and interface','Date and full query','Limits and count','Export and deduplication'],['السؤال والنطاق','القاعدة والواجهة','التاريخ والاستراتيجية','القيود والعدد','التصدير وإزالة التكرار'])),
      ('data-management-plan',pick(lang,'برنامه مدیریت داده','Data management plan','خطة إدارة البيانات'),pick(lang,['نوع داده و روش تولید','مستندات و فرهنگ داده','دسترسی و حفاظت','نسخه پشتیبان و مسئول','مجوز، مخزن و حفظ بلندمدت'],['Data types and production','Documentation and dictionary','Access and protection','Backup and responsibility','License, repository and preservation'],['أنواع البيانات وإنتاجها','التوثيق والقاموس','الوصول والحماية','النسخ والمسؤولية','الترخيص والمستودع والحفظ'])),
      ('data-dictionary',pick(lang,'فرهنگ داده','Data dictionary','قاموس البيانات'),pick(lang,['نام متغیر','تعریف و زمان سنجش','نوع و واحد','دامنه و کدهای مجاز','گمشدگی و منشأ'],['Variable name','Definition and measurement time','Type and units','Range and permitted codes','Missingness and provenance'],['اسم المتغير','التعريف ووقت القياس','النوع والوحدة','المدى والرموز','الفقد والمصدر'])),
      ('preregistration-plan',pick(lang,'برنامۀ پیش‌ثبت و تحلیل','Preregistration and analysis plan','خطة التسجيل المسبق والتحليل'),pick(lang,['پرسش و فرضیه','پیامد و نمونه','حجم نمونه و توقف','حذف و گمشدگی','مدل و تحلیل اکتشافی','نسخه و دلیل تغییر'],['Questions and hypotheses','Outcomes and sample','Sample size and stopping','Exclusions and missingness','Models and exploratory work','Version and change rationale'],['الأسئلة والفرضيات','النتائج والعينة','الحجم والتوقف','الاستبعاد والفقد','النماذج والاستكشاف','النسخة وسبب التغيير'])),
      ('reviewer-response',pick(lang,'پاسخ بندبه‌بند به داور','Point-by-point reviewer response','رد تفصيلي على المراجع'),pick(lang,['شماره داور و نظر','پاسخ علمی','اقدام یا دلیل عدم اجرا','محل اصلاح و نسخه','کنترل نهایی نویسندگان'],['Reviewer and comment','Scientific response','Action or reason not implemented','Location and version','Final author check'],['المراجع والتعليق','الرد العلمي','الإجراء أو سبب عدم التنفيذ','الموضع والنسخة','فحص المؤلفين'])),
      ('research-readme',pick(lang,'README پروژه پژوهشی','Research project README','README للمشروع البحثي'),pick(lang,['هدف و نسخه پروژه','منشأ داده و مجوز','محیط و وابستگی‌ها','دستور اجرای مرتب','خروجی و کنترل‌ها','محدودیت و راه تماس'],['Purpose and version','Data origin and rights','Environment and dependencies','Ordered execution instructions','Outputs and checks','Limitations and contact'],['الهدف والنسخة','مصدر البيانات والحقوق','البيئة والاعتماديات','تعليمات التنفيذ','المخرجات والفحوص','القيود والتواصل']))]
    downloadcards=[]
    template_guides={'search-log':'literature-search','data-management-plan':'research-data','data-dictionary':'research-data','preregistration-plan':'preregistration','reviewer-response':'open-peer-review','research-readme':'research-programming'}
    byslug={a['slug']:a for a in D['articles'][lang]}
    for filename,title,sections in templates:
        target=ROOT/'assets/downloads'/lang/(filename+'.md');target.parent.mkdir(parents=True,exist_ok=True)
        prompts=template_prompts(lang,filename)
        mapped=byslug[template_guides[filename]]
        target.write_text('# '+title+'\n\n'+t['toolintro']+'\n\n'+''.join('## '+s+'\n\n'+prompts[i]+'\n\n'+pick(lang,'تصمیم واقعی، دلیل و محل شاهد: ','Actual decision, rationale and evidence location: ','القرار الفعلي وسببه وموضع دليله: ')+'____________________\n\n' for i,s in enumerate(sections))+'---\n\n'+workbook(lang,mapped).replace('# '+mapped['title'],'## '+pick(lang,'مثال مرتبط و دفتر تصمیم','Related example and decision record','مثال مرتبط وسجل قرار'),1))
        downloadcards.append(f'<article class="card"><h2>{title}</h2><p>{esc(" · ".join(sections))}</p><a class="cardlink" href="/assets/downloads/{lang}/{filename}.md" download="{filename}-{lang}.md">{t["download"]} · Markdown</a></article>')
    workbookcards=[]
    for a in D['articles'][lang]:
        target=ROOT/'assets/downloads'/lang/(a['slug']+'-workbook.md')
        target.write_text(workbook(lang,a))
        workbookcards.append(f'<article class="card workbookcard" data-searchable data-category="{a["category"]}" data-search-terms="{esc(a.get("search_terms",""))}"><span class="label">{D["categories"][lang][a["category"]]}</span><h3><a href="{url(lang,"guides/"+a["slug"])}">{esc(a["title"])}</a></h3><p>{esc(a["outcomes"][0])}</p><a class="cardlink" href="/assets/downloads/{lang}/{a["slug"]}-workbook.md" download="{a["slug"]}-{lang}.md">{t["download"]} · Markdown</a></article>')
    examples='<article class="toolbox examplebox"><h2>'+pick(lang,'پروژۀ اجرایی: داده و کد آموزشی','Executable project: teaching data and code','مشروع تنفيذي: بيانات وكود تعليميان')+'</h2><p>'+pick(lang,'۱۲ رکورد ساختگی، فرهنگ داده، کنترل ورودی، شش مسیر تحلیل، مثال TOST، سند Quarto و آزمون‌های با جواب معلوم. محاسبۀ Python از کتابخانۀ استاندارد استفاده می‌کند؛ ساخت سند Quarto نیازهای جدا دارد که در README آمده‌اند.','12 synthetic records, a dictionary, validation, six analysis paths, a TOST example, a Quarto document and known-answer tests. Python calculations use the standard library; separate Quarto requirements are documented in the README.','١٢ سجلاً اصطناعياً وقاموس وفحص وستة مسارات ومثال TOST ووثيقة Quarto واختبارات. يستخدم الحساب مكتبة Python القياسية وتوثق متطلبات Quarto منفصلة.')+'</p><a class="btn" href="/assets/downloads/common/research-examples.zip" download="research-examples.zip">'+pick(lang,'دانلود بستۀ مثال‌ها','Download the examples package','تنزيل حزمة الأمثلة')+' · ZIP</a><a class="cardlink" href="'+url(lang,'guides/computational-thesis-quarto')+'">'+byslug['computational-thesis-quarto']['title']+'</a></article>'
    doi=f'<div class="toolbox" data-doi-tool data-invalid="{esc(t["doifail"])}" data-ready="{esc(t["doiready"])}" data-copy="{esc(t["doicopy"])}" data-copied="{esc(t["copied"])}" data-copy-failed="{esc(t["copyfail"])}"><h2>{t["doi"]}</h2><p>{t["doinote"]}</p>{nojs_tool(lang)}<form data-doi-form><label class="field">{t["doilabel"]}<input name="doi" type="text" dir="ltr" maxlength="300" placeholder="10.1038/sdata.2016.18" required autocomplete="off" spellcheck="false"></label><button class="btn" type="submit">{t["doibutton"]}</button></form><div data-doi-result role="status" aria-live="polite"></div></div>'
    body='<main id="main">'+hero(lang,'toolkit','programming')+f'<section class="block"><div class="wrap"><p>{t["toolintro"]}</p>{examples}<h2>{pick(lang,"الگوهای پایه با مثال","Foundation templates with examples","قوالب أساسية مع أمثلة")}</h2><div class="grid toolkitgrid">{"".join(downloadcards)}</div><h2>{pick(lang,"کاربرگ‌های راهنماها","Guide workbooks","دفاتر الأدلة")}</h2>{searchcontrols(lang,t["search"])}<p class="searchcount" role="status" aria-live="polite">{len(workbookcards)}</p><div class="grid toolkitgrid">{"".join(workbookcards)}</div>{doi}<div class="actions"><a class="btn ghost" href="{url(lang,'planner')}">{t['planner']}</a><a class="btn ghost" href="{url(lang,'glossary')}">{t['glossary']}</a></div></div></section></main>'
    save(lang,'toolkit',body,subject='programming')
    policy=pick(lang,
     [('هدف و حدود پوشش','این دانشنامه ۲۸ موضوع پژوهشی را در سه زبان پوشش می‌دهد و منابع و ابزارهای مرتبط را معرفی می‌کند. همه رشته‌ها، همه قوانین دانشگاه‌ها و همه داده‌های جهان در آن گردآوری نشده‌اند. هر راهنما یک نقطه شروع مستند برای تصمیم‌گیری و مطالعه بیشتر است.'),('انتخاب منابع','برای توضیح روش و ابزار، منابع اصلی، مستندات رسمی و راهنماهای دانشگاهی بر منابع تبلیغاتی مقدم‌اند. سیاست و نسخه مورد استفاده را در پروژه واقعی دوباره بررسی کنید. معرفی دانشگاه یا سرویس به معنی همکاری، تأیید یا وابستگی مؤسسه نیست.'),('تهیه محتوا و تصاویر','در آماده‌سازی متن، ترجمه، کد و تصاویر این نسخه از ابزارهای هوش مصنوعی استفاده شده است. منابع و مثال‌ها برای بازبینی قابل مشاهده‌اند. تصاویر خدمات مفهومی‌اند و کارکنان واقعی یا نتیجه یک مطالعه را نشان نمی‌دهند. نویسندگی به مؤسسه نسبت داده شده و ادعای تأیید یک متخصص نام‌برده مطرح نشده است.'),('بازبینی و اصلاح','تاریخ آخرین ویرایش کنار هر راهنما نمایش داده می‌شود؛ تاریخ ساخت بسته جای تاریخ بازبینی محتوا را نمی‌گیرد. سیاست‌ها و ابزارها ممکن است تغییر کنند. برای گزارش خطا، پیوند راهنما، بخش، دلیل و منبع اصلاح را از راه تماس مؤسسه ارسال کنید.'),('استفاده در پژوهش','منابع اصلی را بخوانید و در متن علمی به همان مدرکی استناد کنید که واقعاً بررسی کرده‌اید. مثال‌ها و الگوها آموزشی‌اند و باید با طراحی، مجوزها و شیوه‌نامه پروژه هماهنگ شوند. اصلاح علمی و اعلام کمک‌های دریافت‌شده بخشی از مسئولیت پژوهشگر است.')],
     [('Purpose and coverage','This library covers 28 research topics in three languages and points to relevant resources and tools. It does not contain every discipline, institutional rule or dataset. Each guide is a sourced starting point for further study and decisions.'),('Source selection','Primary publications, official documentation and university guidance are preferred for methods and tools. Recheck applicable policies and versions for the actual project. Listing an institution or service implies no partnership, endorsement or affiliation.'),('Preparation and imagery','AI tools assisted preparation of text, translations, code and images in this version. Sources and examples are visible for review. Service images are illustrative, not actual staff or study results. Authorship is attributed to the institute without claiming review by an identified specialist.'),('Revisions and corrections','Each guide displays its actual revision date rather than an automatically changing build date. Policies and tools can change. To report an error, send the guide link, passage, rationale and supporting correction source through the institute’s contact route.'),('Research use','Read original sources and cite documents you have actually consulted. Examples and templates are educational and need alignment with design, permissions and institutional requirements. Researchers remain responsible for corrections and disclosure of assistance.')],
     [('الهدف والتغطية','تغطي المكتبة ٢٨ موضوعاً بثلاث لغات وتوجّه إلى مصادر وأدوات مرتبطة. لا تجمع كل التخصصات أو قواعد الجامعات أو بيانات العالم. كل دليل نقطة بداية موثقة لمزيد من الدراسة والقرار.'),('اختيار المصادر','تُفضَّل المنشورات الأصلية والمستندات الرسمية وإرشادات الجامعات للطرق والأدوات. أعد فحص السياسة والنسخة في المشروع الفعلي. لا تعني إضافة مؤسسة أو خدمة شراكة أو اعتماداً أو علاقة بها.'),('الإعداد والصور','ساعدت أدوات الذكاء الاصطناعي في إعداد النص والترجمات والكود والصور بهذه النسخة. المصادر والأمثلة ظاهرة للمراجعة. صور الخدمات توضيحية ولا تمثل موظفين فعليين أو نتائج دراسة. تُنسب الكتابة إلى المؤسسة دون ادعاء مراجعة متخصص مسمى.'),('المراجعات والتصحيح','يعرض كل دليل تاريخ تعديله الفعلي لا تاريخ بناء متغيراً تلقائياً. قد تتغير السياسات والأدوات. للإبلاغ عن خطأ، أرسل الرابط والمقطع والسبب ومصدر التصحيح عبر تواصل المؤسسة.'),('الاستخدام البحثي','اقرأ المصادر الأصلية واستشهد بما اطلعت عليه فعلاً. الأمثلة والقوالب تعليمية وتحتاج مواءمة التصميم والتصاريح وتعليمات المؤسسة. يبقى الباحث مسؤولاً عن التصحيح والإفصاح عن المساعدة.')])
    policy=[(h,p.replace('۲۸','۴۵').replace('٢٨','٤٥').replace('28 research topics','45 research topics')) for h,p in policy]
    policy.append((pick(lang,'وضعیت علمی این نسخه','Scientific status of this edition','الحالة العلمية لهذه النسخة'),pick(lang,'این نسخه شامل تمرین‌ها و مثال‌های فرضی، هشت مسیر یادگیری و واژه‌نامه است. برای ترجمه‌ها و روش‌ها ادعای داوری تخصصی مستقل نداریم. راهنماهای سلامت، حقوق نشر و روش‌های پیچیده باید برای پروندۀ واقعی با متخصص مربوط بازبینی شوند. فهرست منابع برای کنترل اصل، دامنه و نسخه است؛ داشتن منبع یا چک‌لیست، اعتبار هر کاربرد را تضمین نمی‌کند.','This edition includes fictional worked cases, eight learning paths and a glossary. Independent specialist review of translations or methods is not claimed. Health, rights and complex-method guidance needs relevant review for the actual case. Sources support checking originals, scope and versions; references or checklists do not guarantee every application.','تضم النسخة حالات افتراضية وثمانية مسارات ومعجماً ولا تدعي مراجعة تخصصية مستقلة للترجمات أو الطرق. تحتاج الصحة والحقوق والطرق المعقدة مراجعة ملائمة للحالة الفعلية؛ المراجع والقوائم لا تضمن كل تطبيق.')))
    body='<main id="main">'+hero(lang,'editorial','scientific-writing')+'<section class="block"><div class="wrap prose legal">'+''.join('<h2>'+esc(h)+'</h2><p>'+esc(p)+'</p>' for h,p in policy)+f'<a class="cardlink" href="{url(lang)}#contact">{t["contactfield"]}</a></div></section></main>'
    save(lang,'editorial',body,subject='scientific-writing')
    byslug={a['slug']:a for a in D['articles'][lang]}
    pathnav='<nav class="guide-jumps" aria-label="'+t['learningpaths']+'">'+''.join('<a href="#'+p['id']+'">'+esc(p['title'][lang])+'</a>' for p in D['learning_paths'])+'</nav>'
    paths=''.join('<section class="path-detail prose" id="'+p['id']+'"><span class="eyebrow">'+str(i+1).zfill(2)+'</span><h2>'+esc(p['title'][lang])+'</h2><p>'+esc(p['desc'][lang])+'</p><ol>'+''.join('<li><a href="'+url(lang,'guides/'+s)+'">'+esc(byslug[s]['title'])+'</a><span>'+esc(byslug[s]['outcomes'][0])+'</span></li>' for s in p['guides'])+'</ol><p class="path-output"><strong>'+pick(lang,'معیار پایان مسیر: ','Completion output: ','مخرج المسار: ')+'</strong>'+esc(p['output'][lang])+'</p></section>' for i,p in enumerate(D['learning_paths']))
    pathnote=pick(lang,'این ترتیب، پیشنهاد یادگیری است؛ مراحل واقعی ممکن است تکرار شوند. پیش‌ثبت و داوری مرحلۀ اول باید در زمان مناسبِ پیش از شناخت نتایج انجام شوند. برای روش پیشرفته، ابتدا طراحی و مفاهیم پایه را بخوانید و تصمیم پروژه را با راهنما تطبیق دهید.','This is a learning order; actual work may iterate. Registration and Stage 1 review need appropriate timing before outcome knowledge. Learn design and foundations before advanced methods and align project decisions with supervision.','هذا ترتيب تعلم وقد تتكرر مراحل العمل. يلزم توقيت مناسب للتسجيل ومراجعة المرحلة الأولى قبل معرفة النتائج. تعلم الأساس والتصميم قبل الطرق المتقدمة ووائم القرار مع الإشراف.')
    save(lang,'learning-paths','<main id="main">'+hero(lang,'learning-paths','library')+'<section class="block"><div class="wrap"><p class="note">'+pathnote+'</p>'+pathnav+paths+f'<a class="cardlink" href="{url(lang,"glossary")}">{t["glossary"]}</a></div></section></main>',subject='library')
    glossary=''.join('<article class="card glossarycard" id="term-'+g['id']+'" data-searchable data-category="'+g['category']+'" data-search-terms="'+esc(g['title']['en'])+'"><dl><dt>'+esc(g['title'][lang])+'</dt><dd>'+esc(g['definition'][lang])+'</dd></dl><a class="cardlink" href="'+url(lang,'guides/'+g['guide'])+'">'+t['read']+'</a></article>' for g in D['glossary'])
    save(lang,'glossary','<main id="main">'+hero(lang,'glossary','library')+'<section class="block"><div class="wrap">'+searchcontrols(lang,pick(lang,'جست‌وجوی اصطلاح یا مخفف','Search a term or acronym','ابحث عن مصطلح أو اختصار'))+'<p class="searchcount" role="status" aria-live="polite">'+str(len(D['glossary']))+'</p><div class="grid">'+glossary+'</div></div></section></main>',subject='library')

(ROOT/'index.html').write_bytes((ROOT/'fa/index.html').read_bytes())
(ROOT/'404.html').write_text('<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>صفحه پیدا نشد | دکتر دیدگر</title><meta name="robots" content="noindex, follow"><link rel="stylesheet" href="/style.css"></head><body id="top"><main id="main" class="wrap notfound"><span class="eyebrow">404</span><h1>این صفحه پیدا نشد.</h1><img class="footerlogo" src="/assets/logo.png" width="512" height="512" alt="نشان مؤسسه پژوهشی دکتر دیدگر"><p><span lang="en">Page not found</span> · <span lang="ar">الصفحة غير موجودة</span></p><nav aria-label="انتخاب زبان"><a class="btn" lang="fa" href="/">خانه فارسی</a> <a class="btn" lang="en" href="/en/">English home</a> <a class="btn" lang="ar" href="/ar/">الرئيسية العربية</a></nav></main></body></html>')
NS='http://www.sitemaps.org/schemas/sitemap/0.9'; X='http://www.w3.org/1999/xhtml'; IM='http://www.google.com/schemas/sitemap-image/1.1'
root=etree.Element('{'+NS+'}urlset',nsmap={None:NS,'xhtml':X,'image':IM})
for route in ROUTES:
    e=etree.SubElement(root,'{'+NS+'}url');etree.SubElement(e,'{'+NS+'}loc').text=ORIGIN+route;etree.SubElement(e,'{'+NS+'}lastmod').text=LASTMOD[route]
    path=route.split('/',2)[2].strip('/') if route!='/' else ''
    for l in LANGS: etree.SubElement(e,'{'+X+'}link',rel='alternate',hreflang=l,href=ORIGIN+url(l,path))
    etree.SubElement(e,'{'+X+'}link',rel='alternate',hreflang='x-default',href=ORIGIN+url('fa',path))
    im=etree.SubElement(e,'{'+IM+'}image');etree.SubElement(im,'{'+IM+'}loc').text=ORIGIN+f'/assets/images/{PAGE_IMAGES[route]}-1200.webp'
(ROOT/'sitemap.xml').write_bytes(etree.tostring(root,encoding='UTF-8',xml_declaration=True,pretty_print=True))
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(ROOT/'content/routes.json').write_text(json.dumps(ROUTES))
# Preserve legacy redirects and add permanent aliases for newly introduced URLs.
config=json.loads((ROOT/'vercel.json').read_text()); aliases={r['source']:r for r in config['redirects']}
for route in ROUTES:
    if route=='/': continue
    base=route.rstrip('/')
    for source in [base+'.html',route+'index.html',route+'index',route+'index/']:
        aliases[source]={'source':source,'destination':route,'permanent':True}
config['redirects']=list(aliases.values())
(ROOT/'vercel.json').write_text(json.dumps(config,indent=2)+'\n')
print(f'Generated {len(ROUTES)} canonical pages, {len(D["articles"]["fa"])} guides per language and image sitemap entries.')
