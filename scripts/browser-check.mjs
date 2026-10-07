import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
let playwright;
try{playwright=require('playwright');}catch{playwright=require(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'playwright'));}
const browser=await playwright.chromium.launch({headless:true,args:['--no-sandbox']});
const origin=process.env.TEST_ORIGIN||'http://127.0.0.1:3017';
const checks=[]; const problems=[];
const sizes=[{name:'desktop',width:1440,height:1000},{name:'mobile',width:375,height:900}];
async function inspect(page,label){
  await page.evaluate(()=>document.fonts.ready);
  const metrics=await page.evaluate(async()=>{
    const first=document.querySelector('main img'); if(first)await first.decode();
    return {overflow:document.documentElement.scrollWidth>window.innerWidth+1,headings:document.querySelectorAll('h1').length,main:!!document.querySelector('main'),font:getComputedStyle(document.body).fontFamily,failed:[...document.querySelectorAll('main img')].filter(i=>i.loading!=='lazy'&&(!i.complete||i.naturalWidth===0)).map(i=>i.src)};
  });
  assert.equal(metrics.headings,1,label); assert(metrics.main,label); assert.equal(metrics.overflow,false,'Overflow: '+label); assert.deepEqual(metrics.failed,[],label);
  checks.push({label,...metrics});
}
try{
  for(const viewport of sizes){
    const context=await browser.newContext({viewport:{width:viewport.width,height:viewport.height}});
    const page=await context.newPage();
    page.on('pageerror',e=>problems.push(String(e)));
    page.on('response',r=>{if(r.url().startsWith(origin)&&r.status()>=400)problems.push(r.status()+' '+r.url());});
    for(const lang of ['fa','en','ar']){
      const home=lang==='fa'?'/':'/'+lang+'/';
      await page.goto(origin+home); await inspect(page,viewport.name+' '+lang+' home');
      if(lang!=='en')assert(checks.at(-1).font.includes(lang==='fa'?'Vazirmatn':'Cairo'));
      await page.screenshot({path:`reference/qa/${lang}-home-${viewport.name}.png`,fullPage:viewport.name==='desktop'});
      for(const route of ['guides/','guides/literature-search/','guides/research-proposal/','guides/reporting-guidelines/','guides/registered-reports/','guides/computational-thesis-quarto/','guides/equivalence-testing/','learning-paths/','glossary/','resources/','toolkit/','planner/','privacy/','editorial/']){
        await page.goto(origin+'/'+lang+'/'+route);await inspect(page,viewport.name+' '+lang+' '+route);
      }
    }
    for(const service of ['proposal','data-analysis','programming','scientific-writing','editing','originality']){await page.goto(origin+'/fa/services/'+service+'/');await inspect(page,viewport.name+' service '+service);}
    await context.close();
  }
  const context=await browser.newContext({viewport:{width:1280,height:900}});const page=await context.newPage();
  page.on('pageerror',e=>problems.push(String(e)));
  await page.goto(origin+'/fa/guides/');
  await page.locator('[data-search]').fill('مديريت داده');
  assert(await page.locator('[data-searchable]:visible').count()>0,'Arabic/Persian character normalization');
  await page.locator('[data-search]').fill('');await page.locator('[data-category-filter]').selectOption('analysis');
  const content=JSON.parse(fs.readFileSync('content/site-content.json','utf8'));
  assert.equal(await page.locator('[data-searchable]:visible').count(),content.articles.fa.filter(a=>a.category==='analysis').length);
  await page.locator('[data-search]').fill('no-such-guide-999');assert.equal(await page.locator('[data-searchable]:visible').count(),0);
  await page.goto(origin+'/en/toolkit/');await page.locator('[name=doi]').fill('https://doi.org/10.1038/sdata.2016.18');await page.locator('[data-doi-form] button').click();
  assert.equal(await page.locator('[data-doi-result] a').getAttribute('href'),'https://doi.org/10.1038/sdata.2016.18');
  await page.locator('[name=doi]').fill('javascript:alert(1)');await page.locator('[data-doi-form] button').click();assert.equal(await page.locator('[data-doi-result] a').count(),0);
  for(const days of [14,90,730]){await page.goto(origin+'/en/planner/');await page.locator('[name=days]').fill(String(days));await page.locator('#planner button').click();assert.equal(await page.locator('#planresult li').count(),5);assert((await page.locator('#planresult li').last().textContent()).endsWith(String(days)));}
  await page.goto(origin+'/en/');await page.locator('[name=name]').fill('Test Researcher');await page.locator('[name=contact]').fill('test@example.org');await page.locator('[name=topic]').fill('Synthetic browser test of consultation preparation.');await page.locator('[name=consent]').check();await page.locator('#consultation button[type=submit]').click();await page.locator('#consultation [role=status] a').waitFor();assert((await page.locator('#consultation [role=status] a').getAttribute('href')).startsWith('https://wa.me/989124067596?text='));
  await page.goto('file://'+path.resolve('../deliverables/didgar-preview.html'));
  for(const route of ['/en/','/ar/guides/missing-data/','/fa/toolkit/','/fa/resources/','/fa/guides/critical-appraisal/','/']){
    await page.evaluate(route=>{location.hash='#'+route;},route);await page.waitForFunction(route=>document.querySelector('link[rel=canonical]').href.endsWith(route),route);
    await inspect(page,'offline '+route);assert.equal(await page.locator('main img').evaluate(i=>i.currentSrc.startsWith('data:')),true);
  }
  await page.evaluate(()=>{location.hash='#/fa/toolkit/';});await page.locator('a[download]').first().waitFor();assert((await page.locator('a[download]').first().getAttribute('href')).startsWith('data:text/markdown'));
  await page.screenshot({path:'reference/qa/offline-toolkit.png',fullPage:true});
  await context.close();
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}});const p=await nojs.newPage();await p.goto(origin+'/fa/guides/research-proposal/');assert(await p.locator('.prose').isVisible());assert(await p.locator('.navlinks').isVisible());assert.equal(await p.locator('h1').count(),1);await nojs.close();
  assert.deepEqual(problems,[]);
  fs.writeFileSync('reference/qa/browser-results.json',JSON.stringify({passed:true,checks,search:true,doi:true,planner:true,consultation:true,offline:true,nojs:true,problems},null,2));
  console.log('PASS:',checks.length,'browser layouts; fonts, topic images, search, DOI, planner, consultation, offline routes and templates, no-JS article access.');
}finally{await browser.close();}
