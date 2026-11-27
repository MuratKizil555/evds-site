// Claude artifact sürümünün veri yükleyicisi: veriyi görüntüleyenin TCMB EVDS bağlantısından canlı çeker.
// İş günü serileri 2 yıllık parçalarla (EVDS ~1000 gözlem sınırı); önce son 2 yıl, eski tarih seçilince 2015'e kadar geriye.
const SERVER='TCMB MCP',TOOL='get_series_data';let mcp=null,loadedFrom=null;const pending=new Set();
const SWAP0=Date.UTC(2021,0,1);
function status(t,err){const s=$('status');s.textContent=t;s.className='status'+(err?' err':'')}
function pdate(s){let m=/^(\d{2})-(\d{2})-(\d{4})$/.exec(s);if(m)return Date.UTC(+m[3],+m[2]-1,+m[1]);m=/^(\d{4})-(\d{2})-(\d{2})/.exec(s);return m?Date.UTC(+m[1],+m[2]-1,+m[3]):null}
function strs(x,o=[]){if(typeof x==='string')o.push(x);else if(Array.isArray(x))x.forEach(y=>strs(y,o));else if(x&&typeof x==='object')Object.values(x).forEach(y=>strs(y,o));return o}
function rowsOf(p){const r=[];for(const s of strs(p))for(const line of s.split('\n')){const c=line.split('|').map(z=>z.trim()).filter(z=>z!=='');if(c.length<2)continue;const d=pdate(c[0]),n=parseFloat(c[c.length-1]);if(d!=null&&isFinite(n))r.push([d,n])}return r}
let first=true;
function watch(k,s,e){const tag=k+s;pending.add(tag);
  mcp.watchTool(SERVER,TOOL,{series_code:NS[k],start_date:iso(s),end_date:iso(e),full_data:true},ev=>{
    if(ev.type==='data'){for(const [d,v] of rowsOf(ev.result&&ev.result.payload))data[k].set(d,v);pending.delete(tag);
      status(pending.size?'EVDS\'ten yükleniyor…':'Canlı EVDS verisi · güncellendi '+new Date().toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'}));
      if(first&&!pending.size){first=false;setPreset(preset??'ytd')}else if(!first)render()}
    else if(ev.type==='error'){pending.delete(tag);status('EVDS bağlantısında hata: '+String((ev.error&&(ev.error.code||ev.error.message))||'bilinmiyor'),true)}})}
function chunk(s,e){for(const k in NS){if((k==='swA'||k==='swS')&&e<SWAP0)continue;watch(k,Math.max(s,k[0]==='s'?SWAP0:s),e)}}
function ensure(from){if(!mcp||loadedFrom==null)return;while(loadedFrom>from&&loadedFrom>MIN){const e=loadedFrom-864e5;const s=new Date(loadedFrom);s.setUTCFullYear(s.getUTCFullYear()-2);const st=Math.max(s.getTime(),MIN);chunk(st,e);loadedFrom=st}}
(async()=>{status('EVDS bağlantısı kuruluyor…');try{mcp=await window.claude.use('mcp')}catch(e){mcp=null}
  if(!mcp){status('Bu sayfa verileri sizin TCMB EVDS bağlantınızla çeker. Bağlantı bu görünümde kullanılamıyor.',true);return}
  const s=new Date(today);s.setUTCFullYear(s.getUTCFullYear()-2);chunk(s.getTime(),today.getTime());loadedFrom=s.getTime()})();
