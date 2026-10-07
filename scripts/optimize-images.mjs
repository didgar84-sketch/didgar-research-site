import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
let sharp;
try { sharp=require('sharp'); } catch {
  if(!process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES)throw new Error('For image maintenance install sharp locally.');
  sharp=require(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'sharp'));
}
const manifest=JSON.parse(fs.readFileSync('content/image-inputs.json','utf8'));
fs.mkdirSync('assets/images',{recursive:true});
const dimensions={};
for (const [name,file] of Object.entries(manifest)) {
  for (const width of [480,800,1200]) {
    const height=Math.round(width*2/3);
    const base=`assets/images/${name}-${width}`;
    const resized=sharp(file).rotate().resize(width,height,{fit:'cover',position:'centre'});
    await resized.clone().webp({quality:86,effort:5}).toFile(base+'.webp');
    await resized.clone().avif({quality:58,effort:4}).toFile(base+'.avif');
    dimensions['/'+base+'.webp']=[width,height];
    dimensions['/'+base+'.avif']=[width,height];
  }
  await sharp(file).rotate().resize(1200,630,{fit:'cover'}).jpeg({quality:88,mozjpeg:true}).toFile(`assets/images/${name}-social.jpg`);
  dimensions[`/assets/images/${name}-social.jpg`]=[1200,630];
}
for (const [file,size] of [['logo.png',512],['favicon-96.png',96],['apple-touch-icon.png',180],['icon-192.png',192]]) {
  await sharp('assets/logo.svg').resize(size,size).png().toFile('assets/'+file);
  dimensions['/assets/'+file]=[size,size];
}
fs.copyFileSync('assets/logo.svg','favicon.svg');
const logo=await sharp('assets/logo.svg').resize(184,184).png().toBuffer();
const overlay=Buffer.from('<svg width="1200" height="630"><rect y="414" width="1200" height="216" fill="#071c2c" fill-opacity=".94"/><text x="86" y="499" font-family="sans-serif" font-size="42" font-weight="600" fill="#edcc83">DR. DIDGAR</text><text x="88" y="548" font-family="sans-serif" font-size="23" letter-spacing="5" fill="#ffffff">RESEARCH &amp; INSIGHT</text></svg>');
for(const lang of ['fa','en','ar'])await sharp(manifest.library).resize(1200,630,{fit:'cover'}).composite([{input:overlay},{input:logo,left:930,top:418}]).jpeg({quality:90,mozjpeg:true}).toFile(`assets/social-${lang}.jpg`);
fs.writeFileSync('content/image-dimensions.json',JSON.stringify(dimensions,null,2));
console.log('Optimized',Object.keys(manifest).length,'photo subjects; AVIF/WebP sizes, social images and brand icons.');
