"""Check the real generated routes, watch markup, metadata and public boundary."""
import argparse, html.parser, json, pathlib, re, xml.etree.ElementTree as ET

p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--receipt',type=pathlib.Path);a=p.parse_args();root=a.out.resolve()
catalog=json.loads((pathlib.Path(__file__).parent/'catalog.json').read_text());origin=catalog['origin'];indexable=[];watch=[];link_count=0
class Check(html.parser.HTMLParser):
    def __init__(self,path):super().__init__();self.path=path;self.canonical=None;self.robots=None;self.video=[];self.description=None
    def handle_starttag(self,tag,attrs):
        global link_count
        x=dict(attrs)
        if tag=='meta' and x.get('name')=='description':self.description=x.get('content')
        if tag=='meta' and x.get('name')=='robots':self.robots=x.get('content')
        if tag=='link' and x.get('rel')=='canonical':self.canonical=x.get('href')
        if tag=='video':self.video.append(x)
        for key in ['href','src','poster']:
            val=x.get(key,'')
            if val.startswith('/'):
                f=root/val.lstrip('/');f=f/'index.html' if val.endswith('/') else f
                assert f.is_file(),(str(self.path),val);link_count+=1
for f in root.rglob('index.html'):
    text=f.read_text();check=Check(f);check.feed(text);url=origin+'/'+str(f.relative_to(root)).removesuffix('index.html')
    assert check.canonical==url,(str(f),check.canonical,url)
    assert check.description and check.robots
    if check.robots=='index,follow':indexable.append(url)
    assert not any(s in text for s in ['/Users/','file:///','finance-secrets','BEGIN PRIVATE KEY','{E(','verification.json'])
    schemas=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text)]
    for schema in schemas:
        if schema.get('@type')=='VideoObject':
            assert len(check.video)==1
            assert all(schema.get(k) for k in ['name','description','thumbnailUrl','uploadDate','contentUrl','duration'])
            assert schema['contentUrl']==check.video[0]['src']
            assert check.video[0].get('poster')
            assert check.robots=='index,follow'
            watch.append(url)
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','v':'http://www.google.com/schemas/sitemap-video/1.1'}
sm=ET.parse(root/'sitemap.xml');vm=ET.parse(root/'video-sitemap.xml');urls=[x.text for x in sm.findall('.//s:loc',ns)];vurls=[x.text for x in vm.findall('.//s:loc',ns)]
assert set(urls)==set(indexable) and len(urls)==len(set(urls))
assert set(vurls)==set(watch) and len(vurls)==len(set(vurls))
assert 'Disallow: /\n' not in (root/'robots.txt').read_text()
assert len(watch)==sum(len(b['episodes']) for pr in catalog['projects'] for b in pr.get('batches',[]))
receipt={'pass':True,'indexable_pages':len(indexable),'watch_pages':len(watch),'posting_pages':sum(pr.get('batches',[])!=[] and sum(len(b['episodes']) for b in pr['batches']) for pr in catalog['projects']),'internal_links_checked':link_count,'sitemap_matches_routes':True,'video_sitemap_matches_watch_pages':True,'static_watch_video_and_metadata':True,'public_boundary':True}
if a.receipt:a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
