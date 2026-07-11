#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"^v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$")


def normalize_tag(version: str) -> str | None:
    match = SEMVER_RE.match(version.strip())
    if not match:
        return None
    return f"v{match.group(1)}"


def collect_versions(value: Any) -> set[str]:
    versions: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            tag = normalize_tag(str(key))
            if tag:
                versions.add(tag)
            if key == "version" and isinstance(child, str):
                tag = normalize_tag(child)
                if tag:
                    versions.add(tag)
            else:
                versions.update(collect_versions(child))
    elif isinstance(value, list):
        for child in value:
            versions.update(collect_versions(child))
    return versions


tag = os.environ.get("CI_COMMIT_TAG", "")
versions = collect_versions(json.loads(Path("update.json").read_text()))
print(f"Tag: {tag}")
print(f"update.json versions: {', '.join(sorted(versions)) or '(none)'}")
if tag not in versions:
    raise SystemExit(f"ERROR: refusing release for {tag}; tag is not declared as a version in update.json")
