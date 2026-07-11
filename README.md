# Database Admin

Pelican Panel plugin that adds a database edit button to the server `Databases` table and opens the selected database in a bundled, Pelican-authenticated Adminer instance.

## Features

- Adds an icon button next to Pelican's database view action.
- Uses the database credentials already stored by Pelican.
- No public free-form Adminer login form.
- Restricts Adminer to the selected database through an Adminer plugin.
- Fetches Adminer and the active upstream Adminer plugins during release packaging; third-party Adminer source is not committed to this repository.
- Active Adminer plugins: query timeout, table filter, improved table structure, textarea editing, pretty JSON, dated ZIP exports, and disabled version checks.
- Imports are enabled by default.

## Security model

Users must be authenticated in Pelican and must have `DatabaseRead` plus `DatabaseViewPassword` for the current server. The plugin connects with the per-database MariaDB user stored by Pelican. MariaDB grants remain the final isolation boundary.

Do not grant Pelican database users global privileges. They should only have privileges on their own database.

## Configuration

```env
SERPENSIN_DATABASE_ADMIN_ENABLED=true
SERPENSIN_DATABASE_ADMIN_QUERY_TIMEOUT=15
SERPENSIN_DATABASE_ADMIN_ALLOW_EXPORT=true
SERPENSIN_DATABASE_ADMIN_ALLOW_IMPORT=true
SERPENSIN_DATABASE_ADMIN_ROUTE_PREFIX=database-admin
```

## Install

Download the ZIP from the GitLab release/package link, upload it through Pelican's plugin importer, or copy the folder to `plugins/serpensin-database-admin` and run:

```bash
php artisan p:plugin:install serpensin-database-admin
```

## Update URL

`plugin.json` points to:

```text
https://gitlab.com/Serpensin/pelican-database-admin/-/raw/main/update.json
```


## Release workflow

Do not commit ZIPs or other binary release artifacts. To release a new version, edit `update.json` so it contains the new version number. The default-branch pipeline detects an untagged version in `update.json`, creates the matching `vX.Y.Z` tag, and the tag pipeline builds/uploads the ZIP to the GitLab Generic Package Registry and release assets.

Release packaging runs `scripts/package.py`, which fetches Adminer and the active upstream Adminer plugins from `adminer-vendor.json` into the temporary package tree before the ZIP is created. The source repository stays free of third-party Adminer source files, archives, and binaries.

To intentionally update Adminer or an active Adminer plugin:

```bash
# edit adminer-vendor.json first, e.g. bump the Adminer release URL/version
python3 scripts/vendor_adminer.py lock --target /tmp/adminer-vendor
python3 scripts/package.py
```

`lock` refreshes the pinned SHA-256 checksums after downloading the configured files. CI uses `fetch`, which verifies those checksums and fails if upstream content changed unexpectedly.

If GitLab does not allow `CI_JOB_TOKEN` to create repository tags, configure a masked CI/CD variable named `RELEASE_TOKEN` with permission to create tags for this project.
