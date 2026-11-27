// Claude artifact sürümünün veri yükleyicisi: veriyi görüntüleyenin TCMB EVDS bağlantısından canlı çeker.
let mcp=null;const pending=new Set();
function status(t,err){const s=$('status');s.textContent=t;s.className='status'+(err?' err':'')}
function watch(key,s,e){
  const tag=key+iso(s);pending.add(tag);
  const inp={series_code:ALL[key],start_date:iso(s),end_date:iso(e),full_data:true};if(NS[key]){inp.frequency='3';inp.aggregation='last'}
  mcp.watchTool(SERVER,TOOL,inp,ev=>{
    if(ev.type==='data'){for(const [d,v] of rowsOf(ev.result&&ev.result.payload,ALL[key]))data[key].set(d,v);pending.delete(tag);
      if(preset!=null&&preset!==0&&range.to==null){}
      status(pending.size?'EVDS\'ten yükleniyor…':'Canlı EVDS verisi · güncellendi '+new Date().toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'}));
      if(range.to==null){const a=curSeries();if(a.length)setPreset(preset??'ytd');}else render()}
    else if(ev.type==='error'){pending.delete(tag);errors++;status('EVDS bağlantısında hata: '+String((ev.error&&(ev.error.code||ev.error.message))||'bilinmiyor')+'. Sayfayı yenileyin ya da TCMB bağlantınızı kontrol edin.',true)}
  });
}
function watchPx(s,e){const tag='px'+iso(s);pending.add(tag);
  mcp.watchTool(SERVER,TOOL,{series_code:'TP.ALTINPIYASA.KAP03',start_date:iso(s),end_date:iso(e),full_data:true},ev=>{
    if(ev.type==='data'){for(const [d,v] of rowsOf(ev.result&&ev.result.payload,'TP.ALTINPIYASA.KAP03'))px.set(d,v);pxArr=[...px.entries()].sort((a,b)=>a[0]-b[0]);pending.delete(tag);if(!pending.size)status('Canlı EVDS verisi · güncellendi '+new Date().toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'}));renderPie()}
    else if(ev.type==='error'){pending.delete(tag);status('Altın fiyatı yüklenemedi: '+String((ev.error&&(ev.error.code||ev.error.message))||'bilinmiyor'),true)}})}
// Net rezerv günlük görünümü: analitik bilanço kalemleri, USD ve swap stokları iş günü değerleri 2015'ten, 2 yıllık parçalarla (EVDS ~1000 gözlem sınırı)
let dLoaded=false;
function ensureD(){if(!mcp||dLoaded)return;dLoaded=true;const DK={};for(const k in NS)DK['d'+k]=NS[k];
  for(let y=2015;y<=today.getUTCFullYear();y+=2){const s=new Date(Date.UTC(y,0,1)),e0=new Date(Date.UTC(y+1,11,31)),e=e0>today?today:e0;
    for(const k in DK){const tag=k+y;pending.add(tag);status('EVDS\'ten günlük veri yükleniyor…');
      mcp.watchTool(SERVER,TOOL,{series_code:DK[k],start_date:iso(s),end_date:iso(e),full_data:true},ev=>{
        if(ev.type==='data'){for(const [d,v] of rowsOf(ev.result&&ev.result.payload,DK[k]))data[k].set(d,v);pending.delete(tag);if(!pending.size)status('Canlı EVDS verisi · güncellendi '+new Date().toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'}));if(mode==='net'&&freq==='d'){if(preset)setPreset(preset);else render()}}
        else if(ev.type==='error'){pending.delete(tag);status('Günlük veri yüklenemedi: '+String((ev.error&&(ev.error.code||ev.error.message))||'bilinmiyor'),true)}})}}}
function ensure(from){
  if(!mcp||loadedFrom==null)return;
  while(loadedFrom>from&&loadedFrom>MIN.getTime()){const e=new Date(loadedFrom-864e5);const s=new Date(loadedFrom);s.setUTCFullYear(s.getUTCFullYear()-15);const st=s<MIN?MIN:s;for(const k in ALL)watch(k,st,e);loadedFrom=st.getTime()}
}
(async()=>{
  status('EVDS bağlantısı kuruluyor…');
  try{mcp=await window.claude.use('mcp')}catch(e){mcp=null}
  if(!mcp){status('Bu sayfa verileri sizin TCMB EVDS bağlantınızla çeker. Bağlantı bu görünümde kullanılamıyor; Claude içinde açıp TCMB bağlantısına izin verin.',true);return}
  const s=new Date(today);s.setUTCFullYear(s.getUTCFullYear()-15);
  for(const k in ALL)watch(k,s,today);loadedFrom=s.getTime();
  for(let y=2018;y<=today.getUTCFullYear();y+=3){const a=new Date(Date.UTC(y,6,1)),b=new Date(Date.UTC(y+3,5,30));watchPx(a,b>today?today:b)}
})();
