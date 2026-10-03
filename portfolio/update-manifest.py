"""Export hashes for project-owned portfolio inputs; never package video bytes."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True)
    args = parser.parse_args()
    case_file = ROOT / 'content/cases' / (args.case + '.json')
    case = json.loads(case_file.read_text())
    media = json.loads((ROOT / 'content/media.json').read_text())
    selected = [item for item in media if item['id'] in case.get('media', [])]
    assert len(selected) == len(case.get('media', []))
    sources = [case_file, ROOT / 'content/media.json']
    sources += sorted((ROOT / 'content/cases' / args.case / 'locales').glob('*.json'))
    sources += sorted({ROOT / item['poster'].lstrip('/') for item in selected})
    records = []
    for path in sources:
        source = path.relative_to(ROOT).as_posix()
        assert source.startswith(('content/', 'assets/media/'))
        assert path.suffix.lower() in ('.json', '.jpg', '.jpeg', '.png', '.webp', '.svg')
        data = path.read_bytes()
        destination = source.removeprefix('content/')
        records.append({'source': source, 'path': destination,
                        'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    manifest = {'schema_version': 1, 'case_id': case['id'], 'files': records}
    out = ROOT / 'portfolio/manifest.json'
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'files': len(records), 'case': case['id'],
                      'manifest_sha256': hashlib.sha256(out.read_bytes()).hexdigest()}))

if __name__ == '__main__':
    main()
