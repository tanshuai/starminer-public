"""Build the public portfolio from the curated, credential-free catalogue."""
import argparse, html, json, pathlib, re, shutil, xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=pathlib.Path, required=True)
args = parser.parse_args()
OUT = args.out.resolve()
C = json.loads((HERE / 'catalog.json').read_text())
ORIGIN = C['origin'].rstrip('/')
A = C['author']
E = html.escape
pages = []
videos = []
redirects = []

def write(name, text):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

def page(path, title, description, body, schemas=(), image=None, index=True):
    url = ORIGIN + path
    graph = [{'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'url':url,'author':{'@type':'Person','name':A['name'],'url':A['profile']}}] + list(schemas)
    ld = ''.join('<script type="application/ld+json">' + json.dumps(x,ensure_ascii=False).replace('<','\\u003c') + '</script>' for x in graph)
    browser_title = title if title.startswith('Tan Shuai') else title+' | Tan Shuai'
    head = f'<title>{E(browser_title)}</title><meta name="description" content="{E(description,quote=True)}"><meta name="robots" content="{"index,follow" if index else "noindex,follow"}"><link rel="canonical" href="{url}"><meta property="og:title" content="{E(title,quote=True)}"><meta property="og:description" content="{E(description,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website"><meta property="og:site_name" content="Tan Shuai — Selected Work"><meta name="twitter:card" content="summary_large_image">'
    if image: head += f'<meta property="og:image" content="{ORIGIN+image}">'
    header = f'<header class="site-header"><a class="brand" href="/">Tan Shuai <span>Selected Work</span></a><nav aria-label="Main navigation"><a href="{A["profile"]}">About</a><a href="{A["blog"]}">Writing</a><a href="mailto:{A["email"]}">Contact</a></nav></header>'
    footer = f'<footer class="site-footer"><span>© 2026 Tan Shuai · 谭帅作品集</span><a href="{A["profile"]}">About Tan Shuai</a><a href="mailto:{A["email"]}">{A["email"]}</a></footer>'
    document = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{head}<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css">{ld}</head><body>{header}<main>{body}</main>{footer}</body></html>'
    write(('index.html' if path=='/' else path.strip('/')+'/index.html'),document)
    if index: pages.append(url)

def crumb(parts):
    items = [('Selected Work','/')] + parts
    markup = '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span>/</span> '.join(f'<a href="{p}">{E(n)}</a>' for n,p in items) + '</nav>'
    schema = {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':ORIGIN+p} for i,(n,p) in enumerate(items)]}
    return markup,schema

def link(url, text, cls=''):
    return f'<a class="{cls}" href="{E(url,quote=True)}">{E(text)}</a>'

def kit_sections(text):
    result = ''
    for heading in ['Caption · CLEAN COPY','Pinned comment · CLEAN COPY','发布前核对']:
        match = re.search(r'## '+re.escape(heading)+r'\s*(.*?)(?=\n## |\Z)',text,re.S)
        if match: result += '<h2>'+E(heading.replace(' · CLEAN COPY',''))+'</h2><div class="copy">'+E(match[1].strip())+'</div>'
    return result

OUT.mkdir(parents=True,exist_ok=True)
shutil.copytree(HERE/'assets',OUT/'assets',dirs_exist_ok=True)
write('manifest.json',(HERE/'delivery-manifest.json').read_text())
cards = ''
hero_image = None
for project in C['projects']:
    pp = '/'+project['slug']+'/'
    batches = project.get('batches',[])
    first = batches[0]['episodes'][0] if batches else None
    image = '/assets/'+project['slug']+'/'+first['id']+'.jpg' if first else project.get('image')
    if image and hero_image is None: hero_image = image
    ep_count = sum(len(b['episodes']) for b in batches)
    photo = f'<img src="{image}" alt="{E(first["title"] if first else project["name"],quote=True)}" width="120" height="213">' if image else ''
    metric = f'<p class="note">{ep_count} episodes · {ep_count*2} video files · Public review collection</p>' if ep_count else ''
    cards += f'<article class="project-card">{photo}<div><p class="eyebrow">{E(project.get("kind","Selected project"))}</p><h2>{link(pp,project["name"])}</h2><p>{E(project["summary"])}</p>{metric}{link(pp,"Explore the project →","button")}</div></article>'
    project_body, breadcrumb = crumb([(project['name'],pp)])
    project_body += f'<section class="intro"><p class="eyebrow">{E(project.get("kind","Selected project"))}</p><h1>{E(project["name"])}</h1><p>{E(project["summary"])}</p></section><section class="case-grid"><div><h2>The goal</h2><p>{E(project["goal"])}</p><h2>My contribution</h2><p>{E(project["role"])}</p><p>{E(project.get("contributions",""))}</p></div><div><h2>Delivered</h2><ul>'+''.join('<li>'+E(x)+'</li>' for x in project['delivered'])+'</ul><p class="note">'+E(project.get('review_note',''))+'</p></div></section>'
    if project.get('links'): project_body += '<div class="actions">'+''.join(link(x['url'],x['label'],'button') for x in project['links'])+'</div>'
    for batch in batches:
        bp = pp+batch['slug']+'/'
        project_body += f'<section class="collection"><h2>{E(batch["name"])}</h2><p>{E(batch["description"])}</p><div class="actions">{link(bp,"Preview all "+str(len(batch["episodes"]))+" episodes","button")}{link(batch["release_url"],"Delivery files")}</div></section>'
        rows = ''; data = []; first = batch['episodes'][0]
        for ep in batch['episodes']:
            wp = bp+ep['slug']+'/'
            kp = wp+'posting-kit/'
            poster = '/assets/'+project['slug']+'/'+ep['id']+'.jpg'
            rows += f'<tr><td>{ep["n"]:02d}</td><td><a class="pick" data-index="{ep["n"]-1}" href="{wp}">{E(ep["title_zh"])}</a><small>{E(ep["title"])}</small></td><td>{ep["duration_s"]:.1f}s</td><td>{link(wp,"Watch")}&nbsp;·&nbsp;{link(kp,"发布包")}</td></tr>'
            data.append({'n':ep['n'],'title':ep['title'],'title_zh':ep['title_zh'],'duration':round(ep['duration_s'],1),'main':ep['links']['main'],'no_music':ep['links']['no_music'],'poster':poster,'watch':wp})
            vobject = {'@context':'https://schema.org','@type':'VideoObject','name':ep['title'],'description':ep['description'],'thumbnailUrl':[ORIGIN+poster],'uploadDate':batch['upload_date'],'duration':f'PT{ep["duration_s"]:g}S','contentUrl':ep['links']['main'],'embedUrl':ORIGIN+wp,'inLanguage':'en','transcript':' '.join(ep['transcript']),'isPartOf':{'@type':'CreativeWorkSeries','name':batch['name']}}
            videos.append({'page':ORIGIN+wp,'poster':ORIGIN+poster,'title':ep['title'],'description':ep['description'],'content':ep['links']['main'],'date':batch['upload_date']})
            watch_body, wc = crumb([(project['name'],pp),(batch['name'],bp)])
            watch_body += f'<h1 class="watch-title">{E(ep["title"])}</h1><p class="subtitle" lang="zh-CN">{E(ep["title_zh"])} · {ep["duration_s"]:.1f}s · Episode {ep["n"]}</p><section class="watch-layout"><div class="player"><video id="video" controls playsinline preload="metadata" poster="{poster}" src="{ep["links"]["main"]}"></video><div class="actions"><button id="audio-toggle" class="button" type="button">Switch to no music</button>{link(ep["links"]["main"],"Download main")}</div><p class="note">The no-music version retains narration and sound effects.</p></div><div><p>{E(ep["description"])}</p><h2>Transcript</h2><div class="transcript">'+''.join('<p>'+E(t)+'</p>' for t in ep['transcript'])+'</div><p class="note">'+E(batch['disclosure'])+'</p><div class="actions">'+link(kp,'Posting copy & downloads','button')+link(bp,'All episodes')+'</div><p class="note">Public preview. Creator listening, physical-phone playback, TikTok preview and director publication approval remain pending.</p></div></section>'
            watch_body += '<script>const toggle=document.querySelector("#audio-toggle"),v=document.querySelector("#video");const sources='+json.dumps([ep['links']['main'],ep['links']['no_music']])+';let alt=false;toggle.onclick=()=>{v.pause();alt=!alt;v.src=sources[alt?1:0];toggle.textContent=alt?"Switch to main":"Switch to no music";v.play().catch(()=>{});};</script>'
            page(wp,ep['title'],ep['description'],watch_body,[wc,vobject],poster)
            kit_body,kc = crumb([(project['name'],pp),(batch['name'],bp),(ep['title'],wp)])
            kit_body += '<h1 class="watch-title">Posting kit · '+E(ep['title'])+'</h1>'
            if ep['draft']: kit_body += '<p class="note">Codex draft from Claude outline; director review pending.</p>'
            kit_body += kit_sections(ep['kit'])+'<h2>Files</h2><div class="file-links">'
            labels={'main':'Main video','no_music':'No-music video','subtitles':'SRT subtitles','cover':'9:16 cover','cover_3x4':'3:4 cover','posting_kit':'Posting kit (Markdown)'}
            kit_body += ''.join(link(url,labels[k]) for k,url in ep['links'].items())+'</div>'
            page(kp,'Posting kit — '+ep['title'],'Captions, pinned comment, publication checklist and delivery files for '+ep['title'],kit_body,[kc],poster,index=False)
            redirects.append('/kits/'+ep['id']+'.html '+ORIGIN+kp+' 301')
            redirects.append('/kits/'+ep['id']+' '+ORIGIN+kp+' 301')
            redirects.append('/covers/'+ep['id']+'.jpg '+ORIGIN+poster+' 301')
        bc,bs = crumb([(project['name'],pp)])
        total = round(sum(e['duration_s'] for e in batch['episodes']))
        batch_body = bc+f'<div class="batch-heading"><div><h1>{E(batch["name"])}</h1><p>{len(batch["episodes"])} 集 · Total {total//60}:{total%60:02d} · {"Technical checks passed" if batch.get("technical_qa")=="PASS" else "Review collection"}</p></div>{link(batch["release_url"],"全部文件")}</div><div class="batch-layout"><section class="player"><div id="label">01 · {E(first["title_zh"])}</div><video id="video" controls playsinline preload="metadata" poster="/assets/{project["slug"]}/{first["id"]}.jpg" src="{first["links"]["main"]}"></video><div class="player-buttons"><button id="prev">← 上一集</button><button id="audio-toggle">切换无配乐</button><button id="next">下一集 →</button></div><p class="note">点击集名直接预览；Watch 打开独立播放页。无配乐版保留旁白与音效。</p></section><section><table><tbody>{rows}</tbody></table><p class="note">{E(batch["disclosure"])} Public preview; creator/director publication review pending.</p></section></div>'
        batch_body += '<script>const items='+json.dumps(data,ensure_ascii=False)+';let current=0,alt=false;const v=document.querySelector("#video");function show(i,play=true){current=(i+items.length)%items.length;const e=items[current];v.pause();v.src=alt?e.no_music:e.main;v.poster=e.poster;document.querySelector("#label").textContent=String(e.n).padStart(2,"0")+" · "+e.title_zh;document.querySelector("#audio-toggle").textContent=alt?"切换主片":"切换无配乐";document.querySelectorAll("tr").forEach((r,j)=>r.classList.toggle("active",j===current));if(play)v.play().catch(()=>{});}document.querySelectorAll(".pick").forEach(a=>a.onclick=event=>{if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();show(+a.dataset.index);});document.querySelector("#prev").onclick=()=>show(current-1);document.querySelector("#next").onclick=()=>show(current+1);document.querySelector("#audio-toggle").onclick=()=>{alt=!alt;show(current);};show(0,false);</script>'
        page(bp,batch['name']+' — Bitcoin explainer videos',batch['description'],batch_body,[bs],image)
    page(pp,project['name']+' — Production case study',project['summary'],project_body,[breadcrumb],image)

root_body = '<section class="intro home-intro"><p class="eyebrow">Tan Shuai · 谭帅</p><h1>Selected Work</h1><p class="lead">Client projects, useful tools, and practical experiments.</p><p lang="zh-CN">项目、作品与可复用的工具。看看我做过什么，以及能一起完成什么。</p><div class="actions">'+link(A['profile'],'About me')+link('mailto:'+A['email'],'Discuss a project','button')+'</div></section><section aria-label="Selected projects">'+cards+'</section>'
website={'@context':'https://schema.org','@type':'WebSite','name':C['name'],'alternateName':'谭帅作品集','url':ORIGIN+'/','publisher':{'@type':'Person','name':A['name'],'url':A['profile']}}
page('/',C['name'],'Selected client projects, practical tools and production work by Tan Shuai. Explore the results and get in touch.',root_body,[website],hero_image)
write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\nSitemap: '+ORIGIN+'/video-sitemap.xml\n')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';vn='http://www.google.com/schemas/sitemap-video/1.1';ET.register_namespace('',ns);ET.register_namespace('video',vn)
sm=ET.Element('{'+ns+'}urlset')
for url in pages: ET.SubElement(ET.SubElement(sm,'{'+ns+'}url'),'{'+ns+'}loc').text=url
write('sitemap.xml',ET.tostring(sm,encoding='unicode',xml_declaration=True))
vm=ET.Element('{'+ns+'}urlset')
for item in videos:
    u=ET.SubElement(vm,'{'+ns+'}url');ET.SubElement(u,'{'+ns+'}loc').text=item['page'];v=ET.SubElement(u,'{'+vn+'}video')
    for k,key in [('thumbnail_loc','poster'),('title','title'),('description','description'),('content_loc','content'),('publication_date','date')]:ET.SubElement(v,'{'+vn+'}'+k).text=item[key]
write('video-sitemap.xml',ET.tostring(vm,encoding='unicode',xml_declaration=True))
write('_redirects','\n'.join(redirects)+'\n')
write('_headers','/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n')
write('404.html','<!doctype html><html lang="en"><meta charset="utf-8"><title>Page not found | Tan Shuai</title><meta name="robots" content="noindex"><h1>Page not found</h1><a href="/">Selected Work</a></html>')
write('site-catalog.json',json.dumps({'name':C['name'],'origin':ORIGIN,'projects':[{'slug':p['slug'],'name':p['name'],'url':ORIGIN+'/'+p['slug']+'/'} for p in C['projects']]},ensure_ascii=False,indent=2))
print('Built',len(pages),'indexable pages,',len(videos),'watch pages,',len(redirects),'redirects.')
