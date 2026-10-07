'use strict';
export default async function handler(req,res){
 res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');
 if(req.method!=='POST'){res.setHeader('Allow','POST');return res.status(405).json({error:'Method not allowed'});}
 const type=req.headers['content-type']||'';if(!/^application\/json(?:\s*;|$)/i.test(type))return res.status(415).json({error:'JSON required'});
 let d;try{d=typeof req.body==='string'?JSON.parse(req.body):req.body;}catch{return res.status(400).json({error:'Invalid JSON'});}
 if(!d||Array.isArray(d)||typeof d!=='object')return res.status(400).json({error:'Invalid payload'});
 if(d.website)return res.status(400).json({error:'Invalid request'});
 const clean=v=>typeof v==='string'?v.trim().replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,''):'';
 const name=clean(d.name),contact=clean(d.contact),topic=clean(d.topic),service=clean(d.service),degree=clean(d.degree),deadline=clean(d.deadline);
 if(name.length<2||name.length>100||contact.length<5||contact.length>150||topic.length<10||topic.length>2000||service.length>200||degree.length>100||!['fa','en','ar'].includes(d.lang)||d.consent!=='on')return res.status(400).json({error:'Invalid fields'});
 if(deadline && (!/^\d{4}-\d{2}-\d{2}$/.test(deadline)||!Number.isFinite(Date.parse(deadline))||new Date(deadline).toISOString().slice(0,10)!==deadline))return res.status(400).json({error:'Invalid deadline'});
 const labels={fa:['درخواست مشاوره پژوهشی','نام','راه تماس','خدمت','مقطع','مهلت','موضوع'],en:['Research consultation','Name','Contact','Service','Degree','Deadline','Topic'],ar:['طلب استشارة بحثية','الاسم','التواصل','الخدمة','المرحلة','الموعد','الموضوع']}[d.lang];
 const text=[labels[0],...([name,contact,service,degree,deadline,topic].map((v,i)=>`${labels[i+1]}: ${v||'—'}`))].join('\n');
 // Privacy by design: compose a message; never imply it has been delivered or retain research data.
 return res.status(200).json({status:'ready_to_send',url:'https://wa.me/989124067596?text='+encodeURIComponent(text)});
};
