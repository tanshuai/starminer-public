"""Build independently localized case pages with shared navigation and media."""
import argparse, html, json, pathlib, shutil, xml.etree.ElementTree as ET
HERE=pathlib.Path(__file__).resolve().parent
E=html.escape

def load(path):return json.loads(path.read_text())
def j(value):return json.dumps(value,ensure_ascii=False).replace('<','\\u003c')
def a(url,label,cls=''):return f'<a class="{cls}" href="{E(url,quote=True)}">{E(label)}</a>'
def local(code,path):return path if code=='en' else '/'+code+path

def build(out, language_codes=None):
    site=load(HERE/'site.json');origin=site['origin'];languages=site['languages'];author=site['author']
    if language_codes:languages=[x for x in languages if x['code'] in language_codes]
    cases=[load(HERE/'content/cases'/f'{id}.json') for id in site['cases']]
    registry={x['id']:x for x in load(HERE/'content/media.json')}
    out.mkdir(parents=True,exist_ok=True);shutil.copytree(HERE/'assets',out/'assets',dirs_exist_ok=True)
    routes=[];video_entries=[];redirects=[]
    def write(path,text):
        f=out/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text)
    def page(code,path,title,description,body,ui,index=True,schemas=(),image=None,kind='website'):
        route=local(code,path);url=origin+route;lang=next(x for x in languages if x['code']==code)
        alternatives=''.join(f'<link rel="alternate" hreflang="{x["code"]}" href="{origin+local(x["code"],path)}">' for x in languages) if index else ''
        if index:alternatives+=f'<link rel="alternate" hreflang="x-default" href="{origin+path}">'
        choices=''.join(f'<a lang="{x["code"]}" hreflang="{x["code"]}" href="{local(x["code"],path)}"'+(' aria-current="true"' if x['code']==code else '')+f'>{E(x["name"])}</a>' for x in languages)
        header=f'<header><a class="brand" href="{local(code,"/")}">Tan Shuai<span>{E(ui["work"])}</span></a><nav>{a(author["home"],ui["home"])}<details class="languages"><summary>{E(lang["name"])} <span aria-hidden="true">⌄</span></summary><div class="language-menu" aria-label="{E(ui["language"])}">{choices}</div></details></nav></header>'
        footer=f'<footer><span>© 2026 Tan Shuai</span>{a(author["home"],ui["home"])}{a("mailto:"+author["email"],ui["contact"])}{a(local(code,"/privacy/"),ui["privacy"])}</footer>'
        consent=f'<aside id="consent" hidden><p>{E(ui["consent"])}</p><div><button data-consent="yes">{E(ui["accept"])}</button><button data-consent="no" class="quiet">{E(ui["decline"])}</button>{a(local(code,"/privacy/"),ui["privacy"])}</div></aside>'
        metadata={'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'url':url,'inLanguage':code,'author':{'@type':'Person','name':author['name'],'url':author['home']}}
        ld=''.join('<script type="application/ld+json">'+j(x)+'</script>' for x in [metadata,*schemas])
        head=f'<title>{E(title)} | Tan Shuai</title><meta name="description" content="{E(description,quote=True)}"><meta name="robots" content="{"index,follow" if index else "noindex,follow"}"><link rel="canonical" href="{url}">{alternatives}<meta property="og:title" content="{E(title,quote=True)}"><meta property="og:description" content="{E(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:type" content="{kind}"><meta property="og:site_name" content="Tan Shuai"><meta name="twitter:card" content="summary_large_image">'
        if image:head+=f'<meta property="og:image" content="{origin+image}">'
        doc=f'<!doctype html><html lang="{code}" dir="{lang["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{head}<link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/site.css">{ld}<script src="/assets/site.js" defer data-ga="{site["analytics"]["measurement_id"]}"></script></head><body>{header}<main>{body}</main>{footer}{consent}</body></html>'
        write(route.strip('/')+'/index.html' if route!='/' else 'index.html',doc)
        routes.append({'path':route,'index':index,'language':code})
    def crumbs(code,ui,items):
        return '<nav class="crumbs">'+'<span aria-hidden="true">/</span>'.join(a(local(code,p),t) for t,p in [(ui['work'],'/'),*items])+'</nav>'
    def files(m,ui):
        return '<div class="downloads">'+''.join(a(url,ui.get(key,key),'download') for key,url in m['links'].items())+'</div>'
    def title(m,text):
        base=text['topics'][m['topic']][0]
        if m.get('show_edition'):
            base+=f' · {text["ui"]["edition"]} {m["sequence"]:02}'
        return base
    for case in cases:
        items=[registry[id] for id in case.get('media',[])]
        for group in case.get('collections',[]):
            for n,m in enumerate([x for x in items if x['group']==group],1):m['sequence']=n
    for lang in languages:
        code=lang['code'];base=load(HERE/'locales'/f'{code}.json');ui=base['ui']
        index_rows=''
        for case in cases:
            text=load(HERE/'content/cases'/case['id']/'locales'/f'{code}.json');text['ui']=ui;c=text['case'];cp='/'+case['slug']+'/'
            items=[registry[id] for id in case.get('media',[])];groups=case.get('collections',[])
            photo=f'<img src="{items[0]["poster"]}" width="72" height="96" alt="" loading="lazy">' if items else ''
            count=f'{len(items)} {ui["videos"]}' if items else ui.get(case['kind'],case['kind'])
            index_rows+=f'<article class="case-row" data-search="{E(c["title"]+" "+case.get("client","")+" "+c["summary"]+" "+" ".join(text["topics"][m["topic"]][0] for m in items),quote=True)}">{photo}<div><div class="eyebrow">{E(ui.get(case["kind"],case["kind"]))} <span>· {E(c.get("credit",""))}</span></div><h2>{a(local(code,cp),c["title"])}</h2><p>{E(c["summary"])}</p></div><div class="case-tail"><small>{E(count)}</small>{a(local(code,cp),ui["open"]+' ↗')}</div></article>'
            body=crumbs(code,ui,[])+f'<section class="case-intro"><div><p class="eyebrow">{E(c.get("credit",""))}</p><h1>{E(c["title"])}</h1><p class="lead">{E(c["summary"])}</p></div>'+photo+'</section><section class="case-notes">'+''.join(f'<div><h2>{E(ui[k])}</h2><p>{E(c[k])}</p></div>' for k in ['role','scope','results'] if c.get(k))+'</section>'
            if case.get('links'):body+='<div class="actions">'+''.join(a(x['url'],x['label']) for x in case['links'])+'</div>'
            if groups:body+=f'<div class="section-heading"><h2>{E(ui["collections"])}</h2><span>{len(items)} {E(ui["videos"])}</span></div><div class="collection-index">'
            for group in groups:
                members=[x for x in items if x['group']==group];gt,gd=text['collections'][group];gp=cp+group+'/'
                body+=f'<a class="collection-row" href="{local(code,gp)}"><img src="{members[0]["poster"]}" width="48" height="64" alt="" loading="lazy"><div><h3>{E(gt)}</h3><p>{E(gd)}</p></div><small>{len(members)} <span aria-hidden="true">↗</span></small></a>'
                rows='';playlist=[]
                for m in members:
                    wp=gp+m['slug']+'/';fp=wp+'files/';mt=title(m,text);md=text['topics'][m['topic']][1]
                    rows+=f'<article class="video-row" data-search="{E(mt+" "+md,quote=True)}"><span class="number">{m["sequence"]:02}</span><div><a data-pick="{len(playlist)}" href="{local(code,wp)}">{E(mt)}</a><small>{E(md)}</small></div><time>{m["duration_s"]:.0f}s</time>{a(local(code,wp),ui["watch"]+' ↗')}</article>'
                    playlist.append({'title':mt,'poster':m['poster'],'main':m['links']['main'],'no_music':m['links'].get('no_music'),'url':local(code,wp)})
                    player=f'<section class="watch-player"><video id="video" controls playsinline preload="none" poster="{m["poster"]}" src="{E(m["links"]["main"],quote=True)}" data-case="{case["id"]}" data-media="{m["id"]}"></video><div class="actions">'+(f'<button data-audio-main="{E(m["links"]["main"],quote=True)}" data-audio-alt="{E(m["links"]["no_music"],quote=True)}" data-label-main="{E(ui["main"])}" data-label-alt="{E(ui["no_music"])}">{E(ui["no_music"])}</button>' if m['links'].get('no_music') else '')+a(m['links']['main'],ui['main']+' ↓','download')+'</div></section>'
                    source='<details class="transcript"><summary>'+E(ui['source'])+'</summary><div lang="en" dir="ltr">'+''.join('<p>'+E(t)+'</p>' for t in m['transcript'])+'</div></details>' if m['transcript'] else ''
                    pos=m['sequence']-1;near=[]
                    if pos>0:near.append(a(local(code,gp+members[pos-1]['slug']+'/'),'← '+ui['previous']))
                    if pos+1<len(members):near.append(a(local(code,gp+members[pos+1]['slug']+'/'),ui['next']+' →'))
                    watch=crumbs(code,ui,[(c['title'],cp),(gt,gp)])+f'<section class="watch-layout">{player}<div><p class="eyebrow">{E(gt)} · {m["sequence"]:02} · {m["duration_s"]:.0f}s</p><h1>{E(mt)}</h1><p class="lead">{E(md)}</p><p class="note">{E(c["original"])}</p><div class="actions">{a(local(code,fp),ui["files"]+" ↓")}{a(local(code,gp),ui["back"])}</div>{source}<p class="note">{E(c["caveat"])}</p>'+ (f'<p class="note">{E(c["historical"])}</p>' if m.get('historical') else '')+'<div class="next-links">'+' '.join(near)+'</div></div></section>'
                    video={'@context':'https://schema.org','@type':'VideoObject','name':mt,'description':md,'thumbnailUrl':[origin+m['poster']],'uploadDate':m['upload_date'],'duration':f'PT{m["duration_s"]:g}S','contentUrl':m['links']['main'],'embedUrl':origin+local(code,wp),'inLanguage':m['original_language'],'isPartOf':{'@type':'CreativeWorkSeries','name':gt}}
                    assert m['upload_date'],f'Missing actual public release date: {m["id"]}'
                    page(code,wp,mt+' · '+gt+(' · '+case['client'] if case.get('client') else ''),md,watch,ui,index=m['index'],schemas=[video],image=m['poster'],kind='video.other')
                    if m['index']:video_entries.append({'page':origin+local(code,wp),'poster':origin+m['poster'],'title':mt,'description':md,'content':m['links']['main'],'date':m['upload_date']})
                    fb=crumbs(code,ui,[(c['title'],cp),(gt,gp),(mt,wp)])+f'<h1>{E(ui["files"])}</h1><p>{E(mt)}</p>'+files(m,ui)+f'<p class="note">{E(c["original"])}</p><p class="note">{E(c["caveat"])}</p>'
                    page(code,fp,ui['files']+' · '+mt,md,fb,ui,index=False,image=m['poster'])
                    if code=='en' and group=='desk-miner-101' and case.get('legacy_slugs'):
                        old='/'+case['legacy_slugs'][0]+'/'+group+'/'+m['slug']+'/'
                        redirects.extend([old+' '+wp+' 301',old+'posting-kit/ '+fp+' 301','/kits/'+m['id']+'.html '+fp+' 301','/kits/'+m['id']+' '+fp+' 301','/covers/'+m['id']+'.jpg '+m['poster']+' 301'])
                cb=crumbs(code,ui,[(c['title'],cp)])+f'<div class="collection-title"><div><p class="eyebrow">{E(case.get('client',''))} · {len(members)} {E(ui["videos"])}</p><h1>{E(gt)}</h1><p>{E(gd)}</p></div>{a(local(code,cp),ui["more"]+" ↗")}</div>'
                if group=='alternate-cuts':cb+=f'<p class="note">{E(ui["archive_note"])}</p>'
                cb+=f'<div class="preview-layout"><section class="preview-player"><p id="preview-title">{E(playlist[0]["title"])}</p><video id="video" controls playsinline preload="none" poster="{members[0]["poster"]}" src="{E(members[0]["links"]["main"],quote=True)}" data-case="{case["id"]}"></video><div class="actions"><button data-prev>← {E(ui["previous"])}</button><button data-next>{E(ui["next"])} →</button></div><a id="preview-link" href="{playlist[0]["url"]}">{E(ui["watch"])} ↗</a><p class="note">{E(c["original"])}</p></section><section><label class="search"><span>{E(ui["search"])}</span><input type="search" data-search-input placeholder="{E(ui["search"],quote=True)}"></label><div class="video-list">{rows}</div><p class="empty" hidden>{E(ui["empty"])}</p></section></div><script type="application/json" id="playlist">{j(playlist)}</script>'
                page(code,gp,gt+(' · '+case['client'] if case.get('client') else ''),gd,cb,ui,index=any(m['index'] for m in members),image=members[0]['poster'])
            if groups:body+='</div>'
            page(code,cp,c['title']+(' · '+case['client'] if case.get('client') else ''),c['summary'],body,ui,image=items[0]['poster'] if items else None)
        root=f'<section class="home-intro"><p class="eyebrow">Tan Shuai · 谭帅</p><h1>{E(ui["work"])}</h1><p>{E(ui["intro"])}</p></section><div class="section-heading"><h2>{E(ui["index"])}</h2><label class="search"><span>{E(ui["search"])}</span><input type="search" data-search-input placeholder="{E(ui["search"],quote=True)}"></label></div><section class="work-index">{index_rows}</section><p class="empty" hidden>{E(ui["empty"])}</p><div class="home-contact">{a("mailto:"+author["email"],ui["contact"]+" ↗")}{a(author["home"],ui["home"]+" ↗")}</div>'
        website={'@context':'https://schema.org','@type':'WebSite','name':'Tan Shuai · '+ui['work'],'url':origin+local(code,'/'),'inLanguage':code,'publisher':{'@type':'Person','name':author['name'],'url':author['home']}}
        page(code,'/',ui['work'],ui['intro'],root,ui,schemas=[website],image=registry[cases[0]['media'][0]]['poster'] if cases and cases[0].get('media') else None)
        pb=f'<h1>{E(ui["privacy"])}</h1><p>{E(ui["privacy_text"])}</p><button data-reset-consent>{E(ui["change"])}</button><p>'+a('https://policies.google.com/privacy','Google')+' · '+a('https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement','GitHub')+'</p>'
        page(code,'/privacy/',ui['privacy'],ui['privacy_text'],pb,ui,index=False)
    
    for case in cases:
        for slug in case.get('legacy_slugs',[]):
            redirects.extend(['/'+slug+'/ /'+case['slug']+'/ 301','/'+slug+'/* /'+case['slug']+'/:splat 301'])
    write('_redirects','\n'.join(redirects)+'\n')
    write('_headers','/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n')
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';vn='http://www.google.com/schemas/sitemap-video/1.1';ET.register_namespace('',ns);ET.register_namespace('video',vn)
    sm=ET.Element('{'+ns+'}urlset')
    for r in routes:
        if r['index']:ET.SubElement(ET.SubElement(sm,'{'+ns+'}url'),'{'+ns+'}loc').text=origin+r['path']
    write('sitemap.xml',ET.tostring(sm,encoding='unicode',xml_declaration=True))
    vm=ET.Element('{'+ns+'}urlset')
    for item in video_entries:
        u=ET.SubElement(vm,'{'+ns+'}url');ET.SubElement(u,'{'+ns+'}loc').text=item['page'];v=ET.SubElement(u,'{'+vn+'}video')
        for k,key in [('thumbnail_loc','poster'),('title','title'),('description','description'),('content_loc','content'),('publication_date','date')]:ET.SubElement(v,'{'+vn+'}'+k).text=item[key]
    write('video-sitemap.xml',ET.tostring(vm,encoding='unicode',xml_declaration=True))
    write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\nSitemap: '+origin+'/video-sitemap.xml\n')
    write('404.html','<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found · Tan Shuai</title><a href="/">Tan Shuai · Selected work</a></html>')
    receipt={'languages':len(languages),'cases':len(cases),'unique_videos':len(registry),'watch_pages':len(registry)*len(languages),'indexable_pages':sum(r['index'] for r in routes),'total_pages':len(routes),'video_sitemap_entries':len(video_entries),'redirects':len(redirects)}
    write('site-catalog.json',j({'origin':origin,'cases':site['cases'],'languages':languages,'counts':receipt}))
    print(j(receipt))
    return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--languages',help='Optional development subset, comma-separated');args=p.parse_args();build(args.out.resolve(),args.languages.split(',') if args.languages else None)
