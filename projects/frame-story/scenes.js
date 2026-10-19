'use strict';
// Original demo. Each frame depends only on t; no stateful simulation or unseeded random.
function path(u){return [350+1220*u,540-170*Math.sin(Math.PI*u)];}
Vibe.register('hook',({lt,ball,line,text,box,ease})=>{
 const u=(lt%4)/4,[x,y]=path(u);line(300,650,1620,650);for(let i=0;i<7;i++){const k=Math.max(0,u-i*.035),pt=path(k);ball(...pt,20-i*2,`rgba(233,200,142,${.22-i*.025})`,false);}ball(x,y,28);
 text('它在移动。',960,330,76);text('可屏幕每次画出的，都是静止的一帧。',960,760,31,'#a1b1ca');
});
Vibe.register('frames',({lt,box,ball,text,ease})=>{
 for(let i=0;i<6;i++){const x=150+i*275,y=400;box(x,y,245,230);const u=i/5;ball(x+30+u*185,y+145-65*Math.sin(u*Math.PI),14);text('FRAME '+String(i+1).padStart(2,'0'),x+122,685,25,'#9aaac2');}
 const k=Math.min(5,Math.floor(lt*2));box(150+k*275,400,245,230,'#00000000','#e9c88e');
 text('把运动，拆成一组位置。',960,300,40,'#d5dfef');
});
Vibe.register('compare',({lt,text,line,ball,box})=>{
 const u=(lt%3)/3;
 for(const [row,fps,label,col] of [[0,4,'4 帧 / 秒','#a3b9d9'],[1,24,'24 帧 / 秒','#e9c88e']]){
 const y=430+row*260,q=Math.floor(lt*fps)/fps%3/3;line(420,y,1610,y);text(label,290,y,36,col);ball(440+1140*q,y,26,col);for(let i=0;i<=fps;i++){const x=440+1140*i/fps;line(x,y+55,x,y+66,col,1);} }
 text('相同路径，相同时长，不同采样密度。',960,780,32,'#a1b1ca');
});
Vibe.register('clock',({lt,text,line,ball,box,ease})=>{
 const u=(lt%4)/4;line(360,570,1560,570);for(let i=0;i<=10;i++){line(360+i*120,552,360+i*120,588,'#6e809e');}
 ball(360+1200*u,570,22);text('t = '+(u*4).toFixed(2)+' s',960,385,85,'#e9c88e');text('位置 = 起点 + 速度 × 时间',960,725,48);text('0 s',360,640,28,'#9aaac2');text('4 s',1560,640,28,'#9aaac2');
});
Vibe.register('pipeline',({lt,text,box,line,ball,ease,ctx})=>{
 const labels=['第 0 帧','第 1 帧','第 2 帧','…','视频'];for(let i=0;i<5;i++){let x=170+i*330;box(x,420,260,190);text(labels[i],x+130,515,43,i===4?'#e9c88e':'#dce4f2');if(i<4)line(x+275,515,x+315,515,'#ad9365',3);}
 const k=Math.floor(lt*12);text('30 fps × 10 s = 300 帧',960,740,48,'#e9c88e');text('计算 → 绘制 → 编码',960,310,35,'#a1b1ca');
});
Vibe.register('end',({lt,text,ball,line,box,ease,ctx})=>{
 const u=(lt%4)/4,[x,y]=path(u);for(let i=0;i<30;i++){const pt=path(i/29);ball(...pt,5,'#4f607b',false);}ball(x,y,26);text('先把每一帧讲清楚',960,315,68,'#e9c88e');text('再让它们连成一个故事',960,760,46); });
