# StarMiner portfolio inputs

This public project repository owns the published StarMiner deliverables and the curated data used to display them. The shared Work website implementation belongs to the independent PRIVATE [`tanshuai/work-site`](https://github.com/tanshuai/work-site) repository.

Keep the videos in the existing GitHub Releases, covers in `assets/media/`, case metadata and translations in `content/cases/`, and original media descriptions/transcripts/URLs in `content/media.json`. Delivery hash manifests remain here. Production source and private review records remain in their existing private production repositories.

After an authorized project-content update:

```sh
python3 portfolio/update-manifest.py --case bitcoin-solo-miner
git diff -- portfolio/manifest.json content/ assets/media/
```

Commit the specific changed project files and `portfolio/manifest.json`, with an Agent trailer when an agent authors the change. Publish them to this repository, then update `projects.lock.json` in `work-site` to the new immutable commit and manifest SHA256. Build and verify the complete website before deployment. A project commit alone does not update the website.

The manifest describes curated JSON and covers with relative destinations, exact byte sizes and SHA256 hashes. It contains no credentials, production records or video bytes. The website fetches these files into ignored build caches and publishes the resulting static pages; visitors do not fetch a private repository or authenticate to GitHub.

Preserve existing Release tags, asset names and anonymous download URLs. Changing the website source repository requires no re-upload of the videos. Do not make this delivery repository private while public pages depend on its assets.
