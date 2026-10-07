import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';

const base={...process.env};
for(const key of ['SITE_URL','VERCEL_ENV','VERCEL_URL','VERCEL_PROJECT_PRODUCTION_URL','GOOGLE_SITE_VERIFICATION'])delete base[key];
function build(extra={},success=true){
  const result=spawnSync(process.execPath,['scripts/build.mjs'],{env:{...base,...extra},encoding:'utf8'});
  assert.equal(result.status===0,success,result.stderr);
  if(success)return fs.readFileSync('dist/index.html','utf8');
}
function htmlFiles(dir){
  return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?htmlFiles(path.join(dir,e.name)):e.name.endsWith('.html')?[path.join(dir,e.name)]:[]);
}
let home=build({VERCEL_ENV:'production',VERCEL_PROJECT_PRODUCTION_URL:'research.example',VERCEL_URL:'ephemeral-preview.vercel.app'});
assert(home.includes('rel="canonical" href="https://research.example/"'));
for(const file of htmlFiles('dist')){
  const html=fs.readFileSync(file,'utf8');
  assert(!html.includes('https://dr17.vercel.app'));
  assert(!html.includes('ephemeral-preview.vercel.app'));
  if(!file.endsWith('404.html'))assert(html.includes('index, follow, max-image-preview:large'));
}
assert(fs.readFileSync('dist/sitemap.xml','utf8').includes('https://research.example/fa/guides/'));
assert(fs.readFileSync('dist/robots.txt','utf8').includes('Sitemap: https://research.example/sitemap.xml'));
assert(fs.readFileSync('dist/assets/downloads/fa/registered-reports-workbook.md','utf8').includes('https://research.example/fa/guides/registered-reports/'));
assert(!fs.readFileSync('dist/assets/downloads/fa/registered-reports-workbook.md','utf8').includes('https://dr17.vercel.app'));
assert(!fs.existsSync('dist/reference')&&!fs.existsSync('dist/content')&&!fs.existsSync('dist/scripts'));
home=build({SITE_URL:'https://final-domain.example/',VERCEL_PROJECT_PRODUCTION_URL:'research.example',GOOGLE_SITE_VERIFICATION:'test-token_123'});
assert(home.includes('href="https://final-domain.example/"'));
assert(home.includes('name="google-site-verification" content="test-token_123"'));
home=build({VERCEL_ENV:'preview',VERCEL_PROJECT_PRODUCTION_URL:'research.example',VERCEL_URL:'ephemeral-preview.vercel.app'});
for(const file of htmlFiles('dist'))assert(fs.readFileSync(file,'utf8').includes('name="robots" content="noindex, follow"'));
assert(home.includes('href="https://research.example/"'));
const previewRobots=fs.readFileSync('dist/robots.txt','utf8');
assert(!previewRobots.includes('Disallow: /\n')&&!previewRobots.includes('Sitemap:'));
home=build({VERCEL_ENV:'preview',VERCEL_URL:'ephemeral-preview.vercel.app'});
assert(home.includes('href="https://dr17.vercel.app/"'));
for(const SITE_URL of ['http://example.com','https://example.com/subdir','https://user:pass@example.com','https://example.com/?x=1','https://example.com/#frag'])build({SITE_URL},false);
build({GOOGLE_SITE_VERIFICATION:'bad-token"<script>'},false);
build();
fs.mkdirSync('reference/qa',{recursive:true});fs.writeFileSync('reference/qa/build-check.json',JSON.stringify({passed:true,productionOrigin:true,explicitOrigin:true,markdownOrigin:true,previewNoindex:true,verificationToken:true,invalidOriginRejection:true,privateFilesExcluded:true,finalOrigin:'https://dr17.vercel.app'},null,2));
console.log('PASS: production origin, explicit origin, preview noindex, optional verification, invalid input rejection and clean publication output.');
