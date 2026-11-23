import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const tabs=await (await fetch('http://127.0.0.1:9236/json')).json();
const socket=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(resolve=>socket.addEventListener('open',resolve,{once:true}));
let id=0;const pending=new Map();
socket.addEventListener('message',e=>{const r=JSON.parse(e.data);if(r.id){const p=pending.get(r.id);pending.delete(r.id);r.error?p.reject(r.error):p.resolve(r.result)}});
function call(method,params={}){return new Promise((resolve,reject)=>{const i=++id;pending.set(i,{resolve,reject});socket.send(JSON.stringify({id:i,method,params}))})}
await call('Page.enable');
const manifest=JSON.parse(await fs.readFile(path.join(root,'screen-manifest.json'),'utf8'));
const findings=[];
for(const screen of manifest.screens){
  for(const width of screen.desktop?[1440]:[390,360]){
    await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
    const loaded=new Promise(resolve=>{function handler(e){if(JSON.parse(e.data).method==='Page.loadEventFired'){socket.removeEventListener('message',handler);resolve()}}socket.addEventListener('message',handler)});
    await call('Page.navigate',{url:pathToFileURL(path.join(root,'screens',screen.key+'.html')).href});await loaded;
    const r=await call('Runtime.evaluate',{expression:`JSON.stringify({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('main *')].filter(n=>n.getBoundingClientRect().right>innerWidth+1).map(n=>n.tagName+'.'+n.className).filter(n=>!n.includes('hero-art'))})`,returnByValue:true});
    findings.push({screen:screen.key,...JSON.parse(r.result.value)});
    if(width===390&&['farmer-home','buyer-lot'].includes(screen.key)||screen.key==='admin-overview'){
      const image=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
      await fs.writeFile(path.join(root,screen.key+'.png'),Buffer.from(image.data,'base64'));
    }
  }
}
await fs.writeFile(path.join(root,'layout-check.json'),JSON.stringify(findings,null,2));
console.log(JSON.stringify({checked:findings.length,issues:findings.filter(x=>x.scrollWidth>x.width||x.overflow.length)}));
socket.close();
