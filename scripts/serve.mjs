import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import api from '../api/consultation.mjs';

const root=path.resolve('dist');
if (!fs.existsSync(path.join(root,'index.html'))) throw new Error('Run npm run build first');
const config=JSON.parse(fs.readFileSync('vercel.json','utf8'));
const redirects=new Map(config.redirects.map(r=>[r.source,r.destination]));
const common=Object.fromEntries(config.headers.find(r=>r.source==='/(.*)').headers.map(h=>[h.key,h.value]));
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.woff2':'font/woff2','.webp':'image/webp','.avif':'image/avif','.md':'text/markdown; charset=utf-8','.zip':'application/zip','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.xml':'application/xml; charset=utf-8','.txt':'text/plain; charset=utf-8','.webmanifest':'application/manifest+json'};
const server=http.createServer(async(req,res)=>{
  for(const [key,value] of Object.entries(common))res.setHeader(key,value);
  let url;
  try{url=new URL(req.url,'http://localhost');}catch{res.writeHead(400);res.end();return;}
  let pathname;
  try{pathname=decodeURIComponent(url.pathname);}catch{res.writeHead(400);res.end();return;}
  if(pathname==='/api/consultation'||pathname==='/api/consultation/'){
    let body='';
    for await(const chunk of req){body+=chunk;if(body.length>10000){res.writeHead(413);res.end();return;}}
    try{req.body=JSON.parse(body);}catch{req.body=body;}
    res.status=n=>{res.statusCode=n;return res;};
    res.json=d=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(d));};
    return api(req,res);
  }
  if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405,{'Allow':'GET, HEAD'});res.end();return;}
  if(redirects.has(pathname)){res.writeHead(308,{'Location':redirects.get(pathname)+url.search});res.end();return;}
  if(pathname.includes('\0')||pathname.split('/').includes('..')){res.writeHead(400);res.end();return;}
  let file=path.resolve(root,'.'+pathname);
  if(file!==root&&!file.startsWith(root+path.sep)){res.writeHead(400);res.end();return;}
  if(fs.existsSync(file)&&fs.statSync(file).isDirectory()){
    if(!pathname.endsWith('/')){res.writeHead(308,{'Location':pathname+'/'+url.search});res.end();return;}
    file=path.join(file,'index.html');
  }
  if(!fs.existsSync(file)||!fs.statSync(file).isFile()){
    res.writeHead(404,{'Content-Type':types['.html'],'X-Robots-Tag':'noindex'});
    res.end(req.method==='HEAD'?undefined:fs.readFileSync(path.join(root,'404.html')));return;
  }
  res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');
  if(pathname.startsWith('/assets/'))res.setHeader('Cache-Control','public, max-age=86400');
  if(pathname.startsWith('/assets/downloads/'))res.setHeader('X-Robots-Tag','noindex');
  if(file.endsWith('404.html'))res.setHeader('X-Robots-Tag','noindex');
  res.writeHead(200);
  if(req.method==='HEAD')res.end();else fs.createReadStream(file).pipe(res);
});
server.listen(Number(process.env.PORT||3000),'127.0.0.1',()=>console.log(`http://127.0.0.1:${server.address().port}`));
