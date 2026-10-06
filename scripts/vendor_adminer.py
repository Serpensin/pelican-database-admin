#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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


def vendor_entries(manifest_path: Path) -> list[tuple[dict, Path]]:
    manifest = load_manifest(manifest_path)
    files = manifest.get('files') or []
    if not files:
        raise SystemExit(f'{manifest_path} contains no files')

    entries: list[tuple[dict, Path]] = []
    for entry in files:
        rel = Path(entry['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise SystemExit(f'unsafe vendor path in manifest: {entry["path"]}')
        entries.append((entry, rel))

    return entries


def fetch(manifest_path: Path, target: Path, *, update_lock: bool = False) -> int:
    changed = False
    for entry, rel in vendor_entries(manifest_path):
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
        manifest = load_manifest(manifest_path)
        for entry, _ in vendor_entries(manifest_path):
            entry['sha256'] = hashlib.sha256(download(entry['url'])).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
        print(f'updated {manifest_path}')

    return 0


def verify(manifest_path: Path, target: Path) -> int:
    entries = vendor_entries(manifest_path)
    expected_paths = {rel for _, rel in entries}
    failures: list[str] = []

    for entry, rel in entries:
        expected = entry.get('sha256')
        if not expected:
            failures.append(f'{rel}: missing sha256 in {manifest_path}')
            continue

        data = download(entry['url'])
        source_hash = hashlib.sha256(data).hexdigest()
        if source_hash != expected:
            failures.append(f'{rel}: upstream hash {source_hash} does not match pinned {expected}')
            continue

        target_file = target / rel
        if not target_file.is_file():
            failures.append(f'{rel}: missing committed vendor file')
            continue

        target_hash = hashlib.sha256(target_file.read_bytes()).hexdigest()
        if target_hash != expected:
            failures.append(f'{rel}: committed hash {target_hash} does not match pinned {expected}')
            continue

        print(f'verified {rel} {expected}')

    allowed_paths = {Path('index.php')}
    custom_dir = target / 'plugins-custom'
    if custom_dir.is_dir():
        allowed_paths.update(path.relative_to(target) for path in custom_dir.rglob('*') if path.is_file())

    actual_paths = {path.relative_to(target) for path in target.rglob('*') if path.is_file()}
    unexpected = sorted(actual_paths - expected_paths - allowed_paths)
    if unexpected:
        failures.append('unexpected vendor files: ' + ', '.join(str(path) for path in unexpected))

    if failures:
        raise SystemExit('Vendor verification failed:\n- ' + '\n- '.join(failures))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Fetch, lock, or verify the pinned Adminer vendor tree.')
    parser.add_argument(
        'action',
        choices=['fetch', 'lock', 'verify'],
        help='fetch writes checksum-verified files; lock refreshes checksums; verify checks committed files without writing',
    )
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--target', type=Path, default=ROOT / 'resources' / 'adminer')
    args = parser.parse_args()

    if args.action == 'verify':
        return verify(args.manifest, args.target)

    return fetch(args.manifest, args.target, update_lock=args.action == 'lock')


if __name__ == '__main__':
    raise SystemExit(main())
