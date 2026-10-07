// Exercise shipped application events with a small DOM adapter.
// This checks behavior and unsafe inputs; it is not a browser rendering test.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
class Element{
 constructor(tag='div'){this.tag=tag;this.children=[];this.events={};this.dataset={};this.textContent='';this.value='';this.hidden=false;this.disabled=false;}
 addEventListener(name,fn){this.events[name]=fn;}
 append(...x){this.children.push(...x);}
 replaceChildren(...x){this.children=x;this.textContent='';}
 reportValidity(){return true;}
 querySelector(key){return this.select?.[key]||null;}
 setAttribute(key,value){this[key]=String(value);}
}
const event={preventDefault(){}};
function boot(lang='fa',{searchText='',category='all',cards=[],form=null,offline=false}={}){
 const search=new Element('input');search.value=searchText;
 const select=new Element('select');select.value=category;
 const count=new Element();const out=new Element();const days=new Element('input');days.value='90';
 const planner=new Element('form');planner.formData={days:'90'};
 const doi=new Element();doi.dataset={invalid:'Invalid DOI',ready:'Ready',copy:'Copy',copied:'Copied',copyFailed:'Copy failed'};
 const df=new Element('form'),di=new Element('input'),dr=new Element();doi.select={'form':df,'input':di,'[data-doi-result]':dr};
 const elems={'[data-search]':search,'[data-category-filter]':select,'.searchcount':count,'[data-doi-tool]':doi,'#planner':planner,'#planresult':out,'#consultation':form};
 const doc={documentElement:{lang,hasAttribute:()=>offline},querySelector:key=>elems[key]||null,querySelectorAll:()=>cards,createElement:tag=>new Element(tag)};
 let fetches=0;
 const ctx={document:doc,window:{},location:{protocol:offline?'file:':'http:'},navigator:{clipboard:{writeText:async value=>{ctx.copied=value;}}},FormData:class {constructor(e){this.e=e;}[Symbol.iterator](){return Object.entries(this.e.formData)[Symbol.iterator]();}get(key){return this.e.formData[key];}},URL,encodeURIComponent,decodeURIComponent,Intl,TypeError,fetch:async()=>{fetches++;return {ok:true,json:async()=>({url:'https://wa.me/989124067596?text=Test'})};}};
 vm.runInNewContext(fs.readFileSync('app.js','utf8'),ctx);
 return {search,select,count,planner,out,doi,df,di,dr,ctx,fetches:()=>fetches};
}
const cards=[new Element(),new Element(),new Element()];cards[0].textContent='مدیریت داده پژوهشی';cards[0].dataset.category='data';cards[1].textContent='تحلیل آماری';cards[1].dataset.category='analysis';cards[2].textContent='منابع جهانی';cards[2].dataset.category='search';
let b=boot('fa',{cards,searchText:'مديريت داده'});b.search.events.input();assert.equal(cards[0].hidden,false);assert.equal(cards[1].hidden,true);assert.equal(cards[2].hidden,true);
b.search.value='';b.select.value='analysis';b.select.events.change();assert.equal(cards[1].hidden,false);assert.equal(cards[0].hidden,true);
b.search.value='absent-xyz';b.search.events.input();assert(cards.every(c=>c.hidden));assert.equal(b.count.textContent,'مطلبی پیدا نشد.');
const advanced=[new Element(),new Element(),new Element()];
advanced[0].textContent='پیش ثبت پژوهش';advanced[0].dataset={category:'design'};
advanced[1].textContent='فاصله اطمینان';advanced[1].dataset={category:'analysis',searchTerms:'Confidence interval (CI)'};
advanced[2].textContent='إعادة الإنتاج ۲۰۲۵';advanced[2].dataset={category:'data'};
for(const query of ['پیشثبت','پيش‌ثبت','پیش ثبت']){
 const run=boot('fa',{cards:advanced,searchText:query});assert.equal(advanced[0].hidden,false,query);assert.equal(advanced[1].hidden,true,query);
}
for(const query of ['اعادة','إعادة','2025','٢٠٢٥','۲۰۲۵']){
 const run=boot('ar',{cards:advanced,searchText:query});assert.equal(advanced[2].hidden,false,query);
}
let acronym=boot('fa',{cards:advanced,searchText:'CI'});assert.equal(advanced[1].hidden,false);assert.equal(advanced[0].hidden,true);
acronym.select.value='data';acronym.select.events.change();assert(advanced.every(c=>c.hidden),'Acronym search must respect the category.');
for(const lang of ['fa','en','ar']){
 b=boot(lang);
 for(const input of ['10.1038/sdata.2016.18','https://doi.org/10.1038/sdata.2016.18','doi:10.1038/sdata.2016.18']){b.di.value=input;b.df.events.submit(event);const a=b.dr.children.find(c=>c.tag==='a');assert.equal(a.href,'https://doi.org/10.1038/sdata.2016.18');}
 for(const input of ['javascript:alert(1)','https://evil.example/10.1234/a','10.1234/<script>','10.1234/a b','10.1234/%00bad','10.1234/%ZZ']){b.di.value=input;b.df.events.submit(event);assert.equal(b.dr.children.length,0,input);assert.equal(b.dr.textContent,'Invalid DOI');}
 for(const n of [14,90,730]){b.planner.formData={days:String(n)};b.planner.events.submit(event);assert.equal(b.out.children[0].children.length,5);assert(b.out.children[0].children.at(-1).textContent.endsWith(String(n)));assert.equal(b.out.hidden,false);}
 const form=new Element('form');form.formData={name:'Test Researcher',contact:'test@example.org',service:'Proposal',topic:'Synthetic test request',degree:'Doctoral',deadline:'2026-12-01',consent:'on'};
 const status=new Element(),button=new Element('button');form.select={'[role=status]':status,'button[type=submit]':button};
 b=boot(lang,{form});await form.events.submit(event);assert.equal(b.fetches(),1);assert.equal(button.disabled,false);assert(status.children.find(c=>c.tag==='a').href.startsWith('https://wa.me/'));
 b=boot(lang,{form,offline:true});await form.events.submit(event);assert.equal(b.fetches(),0);const link=status.children.find(c=>c.tag==='a').href;assert(decodeURIComponent(link).includes('Synthetic test request'));assert.equal(button.disabled,false);
}
for(const invalid of [{name:'  '},{topic:'          '},{deadline:'2026-02-30'},{consent:''},{website:'spam'}]){
 const form=new Element('form');
 form.formData={name:'Test Researcher',contact:'test@example.org',service:'Proposal',topic:'Synthetic research request',degree:'Doctoral',deadline:'2026-12-01',consent:'on',website:'',...invalid};
 const status=new Element(),button=new Element('button');
 form.select={'[role=status]':status,'button[type=submit]':button};
 const b=boot('en',{form,offline:true});await form.events.submit(event);
 assert.equal(status.children.length,0);assert.equal(status.textContent,'Check the details and try again.');assert.equal(b.fetches(),0);
}
const report={passed:true,search:['Arabic/Persian letters','half-space and joined words','Arabic/Persian/Latin numerals','acronym metadata','category intersection','empty results'],doi:true,plannerLanguages:['fa','en','ar'],consultation:['online preparation','offline preparation','invalid input rejection'],messagesSent:0,browserRendering:false};
fs.mkdirSync('reference/qa',{recursive:true});fs.writeFileSync('reference/qa/interaction-check.json',JSON.stringify(report,null,2));
console.log('PASS: shipped JS; multilingual letters/numerals, half-spaces, acronym search, categories, DOI unsafe inputs, timelines and online/offline consultation preparation. No messages sent.');
