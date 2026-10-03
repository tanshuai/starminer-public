(()=>{
  const script=document.currentScript,ga=script?.dataset.ga,storageKey='work-statistics-v1';
  let consent=null,started=false;
  try{consent=localStorage.getItem(storageKey)}catch{}
  const banner=document.querySelector('#consent');
  function start(){
    if(started||!ga)return;started=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=function(){window.dataLayer.push(arguments)};
    gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    gtag('consent','update',{analytics_storage:'granted'});
    gtag('js',new Date());gtag('config',ga,{page_location:location.origin+location.pathname,page_referrer:(()=>{try{const r=new URL(document.referrer);return r.origin+r.pathname}catch{return ''}})(),allow_google_signals:false,allow_ad_personalization_signals:false});
    const tag=document.createElement('script');tag.async=true;tag.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(ga);document.head.append(tag);
  }
  function event(name,data){if(consent==='yes'&&started)window.gtag?.('event',name,data)}
  if(consent==='yes')start();else if(consent===null&&banner)banner.hidden=false;
  document.querySelectorAll('[data-consent]').forEach(b=>b.addEventListener('click',()=>{
    consent=b.dataset.consent;try{localStorage.setItem(storageKey,consent)}catch{};banner.hidden=true;if(consent==='yes')start();
  }));
  document.querySelector('[data-reset-consent]')?.addEventListener('click',()=>{try{localStorage.removeItem(storageKey)}catch{};location.reload()});
  document.querySelectorAll('.language-menu a').forEach(a=>a.addEventListener('click',()=>event('language_change',{language:a.lang})));
  document.querySelectorAll('a.download').forEach(a=>a.addEventListener('click',()=>event('work_download',{file_name:a.href.split('/').pop(),link_url:a.href})));
  const search=document.querySelector('[data-search-input]');
  search?.addEventListener('input',()=>{
    const q=search.value.toLocaleLowerCase().trim();let visible=0;
    document.querySelectorAll('[data-search]').forEach(row=>{row.hidden=!row.dataset.search.toLocaleLowerCase().includes(q);if(!row.hidden)visible++});
    const empty=document.querySelector('.empty');if(empty)empty.hidden=visible>0;
  });
  const v=document.querySelector('#video');
  v?.addEventListener('play',()=>event('video_play',{case_id:v.dataset.case||'',video_id:v.dataset.media||'',video_title:document.title}));
  v?.addEventListener('ended',()=>event('video_complete',{case_id:v.dataset.case||'',video_id:v.dataset.media||''}));
  const toggle=document.querySelector('[data-audio-main]');let alternate=false;
  toggle?.addEventListener('click',()=>{const time=v.currentTime,playing=!v.paused;v.pause();alternate=!alternate;v.src=alternate?toggle.dataset.audioAlt:toggle.dataset.audioMain;toggle.textContent=alternate?toggle.dataset.labelMain:toggle.dataset.labelAlt;v.addEventListener('loadedmetadata',()=>{v.currentTime=Math.min(time,v.duration);if(playing)v.play().catch(()=>{})},{once:true});v.load()});
  const list=document.querySelector('#playlist');
  if(list&&v){const items=JSON.parse(list.textContent);let n=0;
    function pick(index,play){n=(index+items.length)%items.length;const item=items[n];v.pause();v.src=item.main;v.poster=item.poster;v.dataset.media=item.id;document.querySelector('#preview-title').textContent=item.title;document.querySelector('#preview-link').href=item.url;document.querySelectorAll('[data-pick]').forEach(a=>a.closest('.video-row').classList.toggle('active',Number(a.dataset.pick)===n));if(play)v.play().catch(()=>{})}
    document.querySelectorAll('[data-pick]').forEach(a=>a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();pick(Number(a.dataset.pick),true)}));
    document.querySelector('[data-prev]')?.addEventListener('click',()=>pick(n-1,true));document.querySelector('[data-next]')?.addEventListener('click',()=>pick(n+1,true));pick(0,false);
  }
  document.addEventListener('click',e=>{const menu=document.querySelector('.languages');if(menu&&!menu.contains(e.target))menu.open=false});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){const menu=document.querySelector('.languages');if(menu)menu.open=false}});
})();
