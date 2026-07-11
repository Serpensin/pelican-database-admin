#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / 'adminer-vendor.json'
USER_AGENT = 'pelican-database-admin-build/1.0'


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())


def fetch(manifest_path: Path, target: Path, *, update_lock: bool = False) -> int:
    manifest = load_manifest(manifest_path)
    files = manifest.get('files') or []
    if not files:
        raise SystemExit(f'{manifest_path} contains no files')

    changed = False
    for entry in files:
        rel = Path(entry['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise SystemExit(f'unsafe vendor path in manifest: {entry["path"]}')

        data = download(entry['url'])
        sha256 = hashlib.sha256(data).hexdigest()
        expected = entry.get('sha256')

        if expected and expected != sha256 and not update_lock:
            raise SystemExit(
                f'sha256 mismatch for {entry["path"]}: expected {expected}, got {sha256}. '
                'Run scripts/vendor_adminer.py lock after intentionally updating the vendor source.'
            )

        if update_lock and expected != sha256:
            entry['sha256'] = sha256
            changed = True

        out = target / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        print(f'fetched {entry["path"]} {sha256}')

    if update_lock and changed:
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
        print(f'updated {manifest_path}')

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Fetch Adminer and configured Adminer plugins for packaging.')
    parser.add_argument('action', choices=['fetch', 'lock'], help='fetch verifies pinned checksums; lock refreshes checksums after intentional updates')
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--target', type=Path, default=ROOT / 'resources' / 'adminer')
    args = parser.parse_args()

    return fetch(args.manifest, args.target, update_lock=args.action == 'lock')


if __name__ == '__main__':
    raise SystemExit(main())
