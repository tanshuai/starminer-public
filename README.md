# StarMiner public delivery

Public portfolio: [work.tanshuai.com](https://work.tanshuai.com/bitcoin-solo-miner/). This PUBLIC project repository owns the approved StarMiner delivery assets and project-specific portfolio content.

The shared website source is maintained only in independent PRIVATE [tanshuai/work-site](https://github.com/tanshuai/work-site). Website code, common interface translations, analytics, SEO and deployment do not belong in this repository. Start with [AGENTS.md](AGENTS.md) and [portfolio maintenance](portfolio/README.md).

## Published assets

- [Desk Miner 101](https://github.com/tanshuai/starminer-public/releases/tag/desk-miner-101-v1): 22 works and their companion files.
- [StarMiner historical library](https://github.com/tanshuai/starminer-public/releases/tag/starminer-library-v1): the other completed public works and companion files.

Together these Releases retain 115 distinct works and 219 MP4 editions. Videos stay in the existing Releases; their tags, filenames and anonymous download URLs are unchanged. Original production and private client delivery remain in their original private repositories.

## Project-owned portfolio inputs

- `content/cases/`: stable case metadata, client credit, collection definitions and project-specific translated presentation text.
- `content/media.json`: media IDs, descriptions, original transcripts, durations, language, index policy and public Release URLs.
- `assets/media/`: one cover per work.
- `delivery-manifest.json`, `media-manifest.json`: delivery file sizes and SHA256 evidence.
- `portfolio/manifest.json`: curated build input paths, sizes and SHA256, regenerated with `python3 portfolio/update-manifest.py --case bitcoin-solo-miner`.

The website pins an immutable commit and manifest hash, fetches these public inputs during its build, and publishes static pages. A project update becomes visible only after updating the website reference, building, verifying and deploying. No visitor needs GitHub authentication.

The former shared website implementation has been removed from the active branch. Earlier commits remain intact for recovery; Git history was not rewritten. Do not make this repository private while public website pages depend on its assets.
