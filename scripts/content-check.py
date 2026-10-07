"""Cross-check the authored edition, workbooks and actual executable examples."""
from pathlib import Path
import hashlib, json, zipfile
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'content/site-content.json').read_text())
ROUTES=json.loads((ROOT/'content/routes.json').read_text())
assert len(ROUTES)==183
assert len(D['learning_paths'])==8 and len(D['glossary'])==40 and len(D['resources'])==61
assert len(D['upgrade']['added_guides'])==17 and len(D['upgrade']['expanded_guides'])==28
slugs={a['slug'] for a in D['articles']['en']}
assert set(s for p in D['learning_paths'] for s in p['guides'])==slugs, 'A guide lacks a learning route.'
assert len({s['url'] for s in D['source_registry'].values()})==len(D['source_registry']), 'Duplicated registry source.'
download_count=0; words={}; cases=0
for lang in ('fa','en','ar'):
    assert {a['slug'] for a in D['articles'][lang]}==slugs
    assert len(D['articles'][lang])==45
    words[lang]=0
    for a in D['articles'][lang]:
        body=html.fragment_fromstring(a['body'],create_parent='div')
        words[lang]+=len(body.text_content().split())
        assert len(body.xpath('.//table'))>=1 and len(a['worksheet'])>=5
        assert a.get('outcomes') and a.get('paths')
        assert a['revised']==D['revision']
        if a['slug'] in D['upgrade']['expanded_guides']:
            assert len(body.xpath('.//section[@data-teaching-case]'))==1
            assert 'Abstract length, defense duration' not in body.text_content()
        else:
            assert a['created']==D['revision'] and len(body.xpath('.//h2'))>=6
        cases+=1
        page=html.parse(str(ROOT/lang/'guides'/a['slug']/'index.html'))
        graph=json.loads(page.xpath('string(//script[@type="application/ld+json"])'))['@graph']
        article=next(g for g in graph if g['@type']=='Article')
        assert article['citation']==[D['source_registry'][s]['url'] for s in a['sources']]
        assert article['wordCount']==len(' '.join(body.text_content().split()).split())
        if 'created' in a: assert article['dateCreated']==a['created']
        assert 'datePublished' not in article, 'Actual public deployment date is not established.'
        for entry in a['downloads']:
            file=ROOT/'assets/downloads'/entry['file']
            assert file.is_file()
            assert page.xpath('//a[@download and @href=$href]',href='/assets/downloads/'+entry['file'])
        file=ROOT/'assets/downloads'/lang/(a['slug']+'-workbook.md')
        content=file.read_text()
        assert a['title'] in content
        assert all(D['source_registry'][s]['url'] in content for s in a['sources'])
        assert '| __________' in content
        download_count+=1
    glossary=html.parse(str(ROOT/lang/'glossary/index.html'))
    assert len(glossary.xpath('//article[contains(@class,"glossarycard")]'))==40
    paths=html.parse(str(ROOT/lang/'learning-paths/index.html'))
    assert len(paths.xpath('//section[contains(@class,"path-detail")]'))==8

project=ROOT/'examples/research-demo'
summary=json.loads((project/'outputs/summary.json').read_text())
assert summary['source_sha256']==hashlib.sha256((project/'synthetic.csv').read_bytes()).hexdigest()
assert summary['n']==12 and abs(summary['mean_score']-808/12)<1e-12
equivalence=json.loads((project/'outputs/equivalence.json').read_text())
assert equivalence[0]['equivalent'] and not equivalence[0]['different_from_zero']
assert not equivalence[1]['equivalent']
archive=ROOT/'assets/downloads/common/research-examples.zip'
with zipfile.ZipFile(archive) as zip:
    assert zip.testzip() is None
    assert all(not n.startswith('/') and '..' not in Path(n).parts and '__pycache__' not in n for n in zip.namelist())
    for file in project.rglob('*'):
        if file.is_file() and '__pycache__' not in file.parts and file.suffix!='.pyc':
            assert zip.read('research-demo/'+file.relative_to(project).as_posix())==file.read_bytes()
report={'passed':True,'edition':D['revision'],'pages':len(ROUTES),'localized_guides':cases,
        'workbooks':download_count,'foundation_templates':18,'resources_per_language':len(D['resources']),
        'learning_paths_per_language':8,'terms_per_language':40,'article_body_words':words,
        'verified_example_output':summary,'quarto_rendering':'not run; Quarto is unavailable',
        'expert_peer_review':'not claimed'}
(ROOT/'reference/qa').mkdir(parents=True,exist_ok=True)
(ROOT/'reference/qa/content-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'PASS: {cases} guide cases, {download_count} workbooks, complete learning-route coverage, sourced article metadata and exact example ZIP agreement.')
