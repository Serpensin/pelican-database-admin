#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
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


def existing_tags() -> set[str]:
    result = subprocess.run(["git", "tag", "--list"], text=True, check=True, capture_output=True)
    return set(result.stdout.splitlines())


def main() -> int:
    update_json = json.loads(Path("update.json").read_text())
    versions = collect_versions(update_json)
    tags = existing_tags()
    missing = sorted(tag for tag in versions if tag not in tags)

    Path("release.env").write_text(
        "\n".join(
            [
                f"UPDATE_JSON_TAGS={' '.join(sorted(versions))}",
                f"EXISTING_MATCHING_TAGS={' '.join(sorted(versions & tags))}",
                f"MISSING_TAGS={' '.join(missing)}",
                f"SHOULD_CREATE_TAG={'true' if missing else 'false'}",
                f"RELEASE_TAG={missing[0] if len(missing) == 1 else ''}",
                f"RELEASE_VERSION={(missing[0][1:] if len(missing) == 1 else '')}",
                "",
            ]
        )
    )

    print(f"Versions found in update.json: {', '.join(sorted(versions)) or '(none)'}")
    print(f"Existing matching tags: {', '.join(sorted(versions & tags)) or '(none)'}")
    print(f"Missing tags: {', '.join(missing) or '(none)'}")

    if len(missing) > 1:
        print("ERROR: update.json contains multiple untagged versions. Add/release one version at a time.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
