import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const child=spawn(process.execPath,['scripts/serve.mjs'],{cwd:process.cwd(),env:{...process.env,PORT:'0'},stdio:['ignore','pipe','pipe']});
try{
  const origin=await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Server readiness timeout')),5000);
    child.stdout.once('data',d=>{clearTimeout(timer);resolve(d.toString().trim());});
    child.once('error',reject);child.stderr.once('data',d=>reject(new Error(d.toString())));
  });
  const routes=JSON.parse(fs.readFileSync('content/routes.json','utf8'));
  for(const route of routes){
    const response=await fetch(origin+route,{redirect:'manual'});
    assert.equal(response.status,200,route);
    const html=await response.text();
    const lang=route==='/'?'fa':route.split('/')[1];
    assert(html.includes(`lang="${lang}"`),route);
    assert(response.headers.get('content-type').startsWith('text/html'));
    assert(response.headers.get('content-security-policy').includes("script-src 'self'"));
  }
  const redirects=JSON.parse(fs.readFileSync('vercel.json','utf8')).redirects;
  for(const r of redirects){
    const response=await fetch(origin+r.source+'?utm_source=seo-check',{redirect:'manual'});
    assert.equal(response.status,308,r.source);
    assert.equal(response.headers.get('location'),r.destination+'?utm_source=seo-check');
    const target=await fetch(origin+r.destination,{redirect:'manual'});
    assert.equal(target.status,200,r.destination);
  }
  let response=await fetch(origin+'/fa/guides/research-proposal',{redirect:'manual'});
  assert.equal(response.status,308);assert.equal(response.headers.get('location'),'/fa/guides/research-proposal/');
  for(const route of ['/missing-page/','/reference/original.html','/content/site-content.json','/scripts/build.mjs']){
    response=await fetch(origin+route);assert.equal(response.status,404,route);
    assert.equal(response.headers.get('x-robots-tag'),'noindex');
    assert((await response.text()).includes('name="robots" content="noindex, follow"'));
  }
  response=await fetch(origin+'/',{method:'HEAD'});assert.equal(response.status,200);assert.equal(await response.text(),'');
  response=await fetch(origin+'/assets/social-fa.jpg');assert.equal(response.status,200);assert.equal(response.headers.get('content-type'),'image/jpeg');
  response=await fetch(origin+'/assets/images/proposal-480.avif');assert.equal(response.status,200);assert.equal(response.headers.get('content-type'),'image/avif');
  response=await fetch(origin+'/assets/downloads/fa/research-readme.md');assert.equal(response.status,200);assert(response.headers.get('content-type').startsWith('text/markdown'));assert((await response.text()).includes('README'));
  assert.equal(response.headers.get('x-robots-tag'),'noindex');
  response=await fetch(origin+'/assets/downloads/common/research-examples.zip');assert.equal(response.status,200);assert.equal(response.headers.get('content-type'),'application/zip');assert.equal(response.headers.get('x-robots-tag'),'noindex');
  assert.deepEqual(Buffer.from(await response.arrayBuffer()),fs.readFileSync('dist/assets/downloads/common/research-examples.zip'));
  response=await fetch(origin+'/assets/downloads/ar/equivalence-testing-workbook.md');assert.equal(response.status,200);assert((await response.text()).includes('TOST'));
  response=await fetch(origin+'/sitemap.xml');assert.equal(response.status,200);assert((await response.text()).includes('<loc>'));
  response=await fetch(origin+'/api/consultation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'Student',contact:'student@example.org',topic:'A research methods consultation',service:'Proposal',degree:'Doctoral',lang:'en',consent:'on'})});
  assert.equal(response.status,200);const data=await response.json();assert.equal(data.status,'ready_to_send');assert(data.url.startsWith('https://wa.me/989124067596?text='));
  fs.mkdirSync('reference/qa',{recursive:true});fs.writeFileSync('reference/qa/http-check.json',JSON.stringify({passed:true,pages:routes.length,aliases:redirects.length,queryPreservation:true,slashNormalization:true,noindex404:true,downloadBytes:true,downloadNoindex:true,apiPreparationOnly:true},null,2));
  console.log(`PASS: ${routes.length} HTTP pages, ${redirects.length} permanent aliases, query preservation, slash normalization, 404/noindex, HEAD, exact downloads and consultation API.`);
}finally{child.kill();}
