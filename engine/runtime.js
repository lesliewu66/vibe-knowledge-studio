'use strict';
window.Vibe=(()=>{
 let c,p,ctx;const renderers={};let issues=[];
 const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
 const ease=v=>{v=clamp(v);return v*v*(3-2*v);};
 function text(str,x,y,size=40,color='#eef2fa',align='center',max=1700){
  ctx.font=`${size}px "PingFang SC","Microsoft YaHei",sans-serif`;ctx.textAlign=align;ctx.textBaseline='middle';
  const width=ctx.measureText(str).width;
  if(width>max)issues.push({kind:'text-width',text:str,width,max});
  ctx.fillStyle=color;ctx.fillText(str,x,y);
 }
 function line(x1,y1,x2,y2,color='#46516b',width=2){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}
 function ball(x,y,r=22,color='#e8c58c',glow=true){ctx.save();ctx.fillStyle=color;if(glow){ctx.shadowColor=color;ctx.shadowBlur=25;}ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();}
 function box(x,y,w,h,color='#151f32',stroke='#35425b'){ctx.fillStyle=color;ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.beginPath();ctx.roundRect(x,y,w,h,18);ctx.fill();ctx.stroke();}
 function grid(){for(let x=90;x<1920;x+=80)line(x,240,x,820,'#142034',1);for(let y=240;y<=820;y+=80)line(90,y,1830,y,'#142034',1);}
 function render(t){
  issues=[];ctx.save();ctx.setTransform(c.width/1920,0,0,c.height/1080,0,0);
  const bg=ctx.createRadialGradient(960,420,20,960,420,1100);bg.addColorStop(0,'#15243b');bg.addColorStop(1,'#070c17');ctx.fillStyle=bg;ctx.fillRect(0,0,1920,1080);
  for(let i=0;i<65;i++){const x=(i*347+51)%1920,y=(i*173+9)%1080;ball(x,y,1,'#40506c',false);}
  const index=p.scenes.findIndex(s=>t>=s.start&&t<s.end),s=p.scenes[index];
  if(!s){ctx.restore();throw Error('No scene at '+t);}
  const lt=t-s.start;
  text('V I B E   /   K N O W L E D G E',100,82,23,'#8d9db9','left');
  text(String(index+1).padStart(2,'0')+' / '+String(p.scenes.length).padStart(2,'0'),1820,82,25,'#8d9db9','right');
  const appear=.18+.82*ease(lt/.65);ctx.save();ctx.globalAlpha=appear;
  text(s.title,960,178,58,'#e9c88e');
  (renderers[s.visual]||renderers.cards)({ctx,t,lt,s,p,clamp,ease,text,line,ball,box,grid});ctx.restore();
  line(160,884,1760,884,'#34415b',1);
  const sub=p.subtitles.find(v=>t>=v.start&&t<v.end);
  if(sub){(sub.text.split('\n')).forEach((v,i,lines)=>text(v,960,950+(i-(lines.length-1)/2)*52,40,'#f1f4fa','center',1640));}
  text(p.series||'把知识演出来',100,1032,22,'#71829f','left');
  text(s.note||'',1820,1032,21,'#71829f','right',1200);
  ctx.restore();return {scene:s.id,issues:[...issues]};
 }
 renderers.cards=({s,lt,box,text,ease,ctx})=>{const items=s.items||[s.title];const n=items.length,w=Math.min(500,1500/n-35),gap=40,total=n*w+(n-1)*gap;items.forEach((v,i)=>{ctx.save();ctx.globalAlpha=ease((lt-i*.25)/.7);const x=(1920-total)/2+i*(w+gap);box(x,390,w,250);text(String(i+1).padStart(2,'0'),x+w/2,450,34,'#e9c88e');text(v,x+w/2,540,34,'#eef2fa','center',w-40);ctx.restore();});};
 return {init(project){p=project;c=document.getElementById('film');c.width=p.width;c.height=p.height;ctx=c.getContext('2d');},render,register(name,fn){renderers[name]=fn;},get canvas(){return c;}};
})();
