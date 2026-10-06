# Development Notes

This document is for maintainers. Keep panel-facing information in `README.md` limited to installation, operation, security, and licensing.

## Environment configuration

The plugin does not currently implement Pelican's `HasPluginSettings` contract, so it has no Panel settings screen. Its configuration is read from the Panel `.env` file:

```env
SERPENSIN_DATABASE_ADMIN_ENABLED=true
SERPENSIN_DATABASE_ADMIN_QUERY_TIMEOUT=15
SERPENSIN_DATABASE_ADMIN_ALLOW_EXPORT=true
SERPENSIN_DATABASE_ADMIN_ALLOW_IMPORT=true
SERPENSIN_DATABASE_ADMIN_ROUTE_PREFIX=database-admin
```

Changing these values requires the normal Panel configuration-cache/PHP-FPM refresh procedure. Do not describe them as Panel UI settings until an actual `HasPluginSettings` implementation exists.

## Repository distribution

PelicanHub ingests the repository directly. Required Adminer source and enabled Adminer plugins are therefore committed under `resources/adminer/`; no GitLab Release or Package Registry artifact is published.

`plugin.json.update_url` uses the committed `update.json` on the default branch. Each download URL points to GitLab's generated ZIP archive for an immutable `vX.Y.Z` tag.

## Version publishing

`update.json` has two distinct sections:

- `releases` is an append-only history keyed by plugin version. Every published version must retain its original tag archive URL permanently.
- `*` is Pelican's active update descriptor. It must match the current version in `plugin.json` and the matching entry under `releases`.

To publish a version:

1. Change `plugin.json.version`.
2. Append `releases[version]` in `update.json`; never modify or remove existing history entries.
3. Set `update.json["*"]` to the exact same object as the new history entry.
4. Commit the change. The default-branch `create-release-tag` CI job validates this alignment and creates only the tag for the current manifest version.

A version that was never published must not be added to the history: its tag archive is not available.

## Vendored Adminer

Adminer and each enabled upstream plugin are declared in `adminer-vendor.json` with a versioned URL and SHA-256 checksum. Do not patch bundled upstream files.

To update Adminer or the enabled plugin set:

1. Update `adminer-vendor.json` to versioned upstream URLs. Remove entries for plugins that upstream no longer provides.
2. Run:

   ```bash
   python3 scripts/vendor_adminer.py lock
   ```

   This refreshes checksums and writes the declared files into `resources/adminer/`.
3. Update `resources/adminer/index.php` for any changed plugin classes or removed plugin files.
4. Update the Adminer version and enabled-plugin description in `README.md`.
5. Run the checks below before committing.

Adminer 6.1.1 no longer provides `pretty-json-column.php`; it must not be declared or loaded.

## Verification

```bash
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool update.json >/dev/null
python3 -m json.tool adminer-vendor.json >/dev/null
python3 scripts/vendor_adminer.py fetch --target /tmp/Yoshi-Temp/pelican-database-admin-vendor-verify
python3 scripts/ci_create_release_tag.py --dry-run
docker run --rm -v "$PWD":/work:ro -w /work php:8.3-cli sh -c \
  'find . -name "*.php" -print0 | xargs -0 -n1 php -l'
```

CI repeats the PHP syntax and byte-for-byte vendor verification.
