#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r'^v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$')


def normalize_tag(version: str) -> str | None:
    match = SEMVER_RE.match(version.strip())
    return f'v{match.group(1)}' if match else None


def collect_versions(value: Any) -> set[str]:
    versions: set[str] = set()

    if isinstance(value, dict):
        for key, child in value.items():
            tag = normalize_tag(str(key))
            if tag:
                versions.add(tag)

            if key == 'version' and isinstance(child, str):
                tag = normalize_tag(child)
                if tag:
                    versions.add(tag)
            else:
                versions.update(collect_versions(child))
    elif isinstance(value, list):
        for child in value:
            versions.update(collect_versions(child))

    return versions


def tag_to_create() -> str | None:
    versions = collect_versions(json.loads(Path('update.json').read_text()))
    tags = set(
        subprocess.run(['git', 'tag', '--list'], text=True, check=True, capture_output=True).stdout.splitlines()
    )
    missing = sorted(versions - tags)

    print(f"Versions found in update.json: {', '.join(sorted(versions)) or '(none)'}")
    print(f"Existing matching tags: {', '.join(sorted(versions & tags)) or '(none)'}")
    print(f"Missing tags: {', '.join(missing) or '(none)'}")

    if len(missing) > 1:
        raise SystemExit('ERROR: update.json contains multiple untagged versions. Add one version at a time.')

    return missing[0] if missing else None


def create_tag_with_git(tag: str, ref: str) -> int:
    name = os.environ.get('GITLAB_USER_NAME') or 'GitLab CI'
    email = os.environ.get('GITLAB_USER_EMAIL') or 'gitlab-ci@example.invalid'
    subprocess.run(['git', 'config', 'user.name', name], check=True)
    subprocess.run(['git', 'config', 'user.email', email], check=True)

    existing = subprocess.run(['git', 'tag', '--list', tag], text=True, check=True, capture_output=True)
    if existing.stdout.strip() != tag:
        subprocess.run(['git', 'tag', '-a', tag, ref, '-m', f'Version {tag}'], check=True)

    subprocess.run(['git', 'push', 'origin', tag], check=True)
    print(f'Created version tag {tag} at {ref} via git push')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Create the single version tag declared in update.json.')
    parser.add_argument('--dry-run', action='store_true', help='Report the tag that would be created without changing GitLab.')
    args = parser.parse_args()

    tag = tag_to_create()
    if tag is None:
        print('No untagged update.json version found; tag creation skipped.')
        return 0

    if args.dry_run:
        print(f'Would create version tag {tag}.')
        return 0

    token = os.environ.get('RELEASE_TOKEN') or os.environ.get('CI_JOB_TOKEN')
    if not token:
        print('ERROR: Set RELEASE_TOKEN (preferred) or allow CI_JOB_TOKEN for tag creation.')
        return 1

    project_id = os.environ['CI_PROJECT_ID']
    api = os.environ['CI_API_V4_URL'].rstrip('/')
    ref = os.environ['CI_COMMIT_SHA']
    url = f'{api}/projects/{project_id}/repository/tags'
    data = urllib.parse.urlencode({
        'tag_name': tag,
        'ref': ref,
        'message': f'Version {tag}',
    }).encode()
    headers = {
        'User-Agent': 'pelican-database-admin-ci',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    if os.environ.get('RELEASE_TOKEN'):
        headers['PRIVATE-TOKEN'] = token
    else:
        headers['JOB-TOKEN'] = token

    request = urllib.request.Request(url, data=data, method='POST', headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            print(response.read().decode('utf-8', 'replace'))
            print(f'Created version tag {tag} at {ref}')
            return 0
    except urllib.error.HTTPError as error:
        body = error.read().decode('utf-8', 'replace')
        if error.code == 400 and 'already exists' in body.lower():
            print(f'Tag {tag} already exists; nothing to do.')
            return 0
        if 'JOB-TOKEN' in headers and error.code in {401, 403, 405}:
            print(f'Repository Tags API rejected CI_JOB_TOKEN with HTTP {error.code}; trying git push fallback.')
            try:
                return create_tag_with_git(tag, ref)
            except subprocess.CalledProcessError as git_error:
                print(f'ERROR: git push fallback failed with exit code {git_error.returncode}')
                print('Enable CI job-token repository pushes for this project or set a masked RELEASE_TOKEN variable with API/write_repository access.')
                return git_error.returncode or 1
        print(f'ERROR: failed to create tag {tag}: HTTP {error.code}')
        print(body)
        if 'JOB-TOKEN' in headers:
            print('If CI_JOB_TOKEN is not allowed to create repository tags on this GitLab instance, enable CI job-token repository pushes for this project or set a masked RELEASE_TOKEN variable with API/write_repository access.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
