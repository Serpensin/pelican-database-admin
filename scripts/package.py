#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = 'serpensin-database-admin'
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)
zip_path = DIST / f'{PLUGIN_ID}.zip'

# Keep the install archive runtime-only. CI scripts, update metadata, VCS files,
# release manifests, and other repository maintenance files do not belong in the
# Pelican plugin ZIP.
RUNTIME_FILES = [
    Path('plugin.json'),
    Path('LICENSE'),
]

RUNTIME_DIRS = [
    Path('config'),
    Path('lang'),
    Path('resources/adminer'),
    Path('routes'),
    Path('src'),
]

VENDORED_ADMINER_PATHS = {
    Path('resources/adminer/adminer.php'),
}

VENDORED_ADMINER_DIRS = {
    Path('resources/adminer/plugins'),
}


def is_under(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def is_vendored_adminer_path(rel: Path) -> bool:
    if rel in VENDORED_ADMINER_PATHS:
        return True

    return any(is_under(rel, vendor_dir) for vendor_dir in VENDORED_ADMINER_DIRS)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


with tempfile.TemporaryDirectory(prefix='pelican-database-admin-package-') as tmp:
    build_root = Path(tmp) / PLUGIN_ID

    for rel in RUNTIME_FILES:
        copy_file(ROOT / rel, build_root / rel)

    for runtime_dir in RUNTIME_DIRS:
        for path in sorted((ROOT / runtime_dir).rglob('*')):
            if path.is_dir():
                continue

            rel = path.relative_to(ROOT)
            if is_vendored_adminer_path(rel):
                continue

            copy_file(path, build_root / rel)

    subprocess.run(
        [
            'python3',
            str(ROOT / 'scripts' / 'vendor_adminer.py'),
            'fetch',
            '--manifest',
            str(ROOT / 'adminer-vendor.json'),
            '--target',
            str(build_root / 'resources' / 'adminer'),
        ],
        check=True,
    )

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(build_root.rglob('*')):
            if path.is_dir():
                continue
            zf.write(path, path.relative_to(Path(tmp)))

print(zip_path)
