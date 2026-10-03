# Tan Shuai · Selected work

Public portfolio: <https://work.tanshuai.com/>. English uses the root; other languages use a locale prefix. All cases share this domain.

## Build and check

```sh
python3 build.py --out /path/to/site
python3 verify.py --out /path/to/site --receipt /path/to/verification.json
```

Python standard library only. To preview a smaller development build, use `--languages en,zh-hans` with the builder. Publish the complete build.

## Content boundaries

- `site.json`: author links, domain, ordered language menu, existing analytics ID and the case index.
- `locales/<language>.json`: common navigation and interface text, maintained once per language.
- `content/cases/<id>.json`: stable case ID, descriptive URL slug, kind, client credit, optional media IDs, optional collections and public links.
- `content/cases/<id>/locales/<language>.json`: this case's translated introduction, role, scope, results, collection text and video topics.
- `content/media.json`: one record per finished work, shared media URLs, actual public-release date, original language, transcript and index policy. Alternative audio versions are files of the same work.
- `assets/`: shared styles, behavior, favicon and one local poster per work. Video bytes stay in GitHub Releases.
- `media-manifest.json`: public file sizes and SHA256 hashes for the additional historical library.

The flat homepage lists cases. Large video cases optionally add collection views; each video has its own watch page. Download pages and repetitive alternative editions remain accessible with `noindex,follow`. Non-video cases omit `media` and `collections`, and use role, scope, results and public links. They do not inherit video controls or StarMiner credits.

To add a case, create its case record and translated text modules, add its stable ID to `site.json`, then build and inspect it. Common layout, language controls, analytics and personal-site links remain shared. For external links, put stable IDs and URLs in the case record and translate labels in each case locale's `links` mapping. Optional case-locale `ui` overrides can label different original audio or subtitle languages without changing the shared interface. Add case-specific disclosures in that case's text. Product specs, results and client contributions must reflect verified or owner-supplied facts.

Language pages have independent self-canonical URLs, reciprocal `hreflang` and English `x-default`. Translated titles and summaries accompany the original English videos, subtitles and explicitly identified source transcripts. The original media is not dubbed. Language menus retain the same case, collection or video when switching languages.

## Analytics

Every page loads one shared module using the personal site's existing GA4 property. The Google script loads only after optional statistics consent. Advertising features are disabled. Page and referrer URLs omit query strings. Consent can be changed on the shared privacy page. Video-play, completion, `work_download` and language-change events use the same implementation across cases. Events being collected is separate from creating reports or registering custom dimensions in the Analytics dashboard.

## Deployment

Publish static build output to the existing Cloudflare Worker `starminer-public`, with its current custom domain. Preserve old StarMiner links with redirects. Keep credentials out of this repository. The original production repository remains private; only curated public content belongs here.

Google crawl eligibility and submitted sitemaps do not establish actual indexing or rankings. Mainland HTTP-node results do not establish mainland video playback. Existing production and publisher records retain source provenance and platform requirements separately from portfolio copy.
