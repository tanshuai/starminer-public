# Tan Shuai — Selected Work

Approved public portfolio: <https://work.tanshuai.com/>. The first project is StarMiner; future projects use the same hostname and separate directories.

## Build

```sh
python3 build.py --out dist
```

Only Python's standard library is needed. `catalog.json` contains approved public copy, episode titles/transcripts and stable delivery URLs. `assets/` contains the stylesheet, favicon and public covers. `delivery-manifest.json` preserves the original Release snapshot.

## Add another project

1. Add an entry to `catalog.json` under `projects`, using a stable lowercase, hyphenated `slug`.
2. Describe the goal, the actual contribution and delivered results. Identify measured outcomes and pending review accurately.
3. Add an approved public delivery collection under `batches`. Each episode requires a stable slug, public media links, cover, transcript, unique description and actual first-publication date.
4. Add covers under `assets/<project-slug>/`, build, check local links/metadata, and visually inspect the result.
5. Publish the generated static site to the existing Worker. Do not upload videos into Git history. Keep credentials and provider job state under local `runs/` only.

Non-video projects can omit `batches` and supply `kind`, `goal`, `role`, `contributions`, `delivered`, optional `review_note`, optional `image`, and approved public `links` with `label`/`url`. They gain a portfolio card and case page without empty video controls. This supports software demonstrations, reports and useful tools under the same hostname.

Video batches require a factual `technical_qa` status and their own `disclosure`; a passed check or a partner disclosure from another project must never be copied as a default claim.

## Public paths

- `/`: portfolio and contact/profile links.
- `/<project>/`: project case study.
- `/<project>/<batch>/`: compact client-review directory.
- `/<project>/<batch>/<episode>/`: indexable watch page, transcript and VideoObject metadata.
- `/<project>/<batch>/<episode>/posting-kit/`: public posting/download page, marked noindex to keep utility copy out of search results.

The builder generates sitemap.xml, video-sitemap.xml, robots.txt, canonical URLs, Open Graph tags and legacy redirects. All public download/video links keep using the original GitHub Release, so rebuilding the website does not duplicate video uploads.

Search Console submission and Google live URL results must be recorded separately from indexing. A local browser or proxy-mediated test is not mainland no-proxy acceptance. No ranking, reachability, social-publication or platform-performance guarantee is made by the build.
