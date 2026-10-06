# Database Admin

Pelican Panel plugin that adds a database edit button to the server `Databases` table and opens the selected database in a bundled, Pelican-authenticated Adminer instance.

## Features

- Adds an icon button next to Pelican's database view action.
- Uses the database credentials already stored by Pelican.
- No public free-form Adminer login form.
- Restricts Adminer to the selected database through an Adminer plugin.
- Includes Adminer 6.1.1 and its active upstream plugins directly in the repository, so PelicanHub can install from the repository without a separate release artifact.
- Active Adminer plugins: query timeout, table filter, improved table structure, textarea editing, dated ZIP exports, and disabled version checks.
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

Install it from PelicanHub, or copy the repository folder to `plugins/serpensin-database-admin` and run:

```bash
php artisan p:plugin:install serpensin-database-admin
```

## Update URL

`plugin.json` points to:

```text
https://gitlab.com/Serpensin/pelican-database-admin/-/raw/main/update.json
```


## Version tags and Adminer updates

This project does not publish GitLab releases or package-registry archives. Each plugin update points to the ZIP archive GitLab generates for its matching `vX.Y.Z` tag. When publishing a version, keep `plugin.json` and `update.json` aligned and commit the change; the default-branch pipeline creates and pushes the matching tag.

Adminer and the enabled plugins are committed under `resources/adminer/`. `adminer-vendor.json` records their versioned upstream URLs and SHA-256 checksums. CI downloads the declared files and verifies that the committed vendor tree matches them.

This plugin is licensed under [MIT](LICENSE). Bundled Adminer is separately dual-licensed under Apache License 2.0 or GPL 2.0; its upstream license notice is retained at [`resources/adminer/LICENSE`](resources/adminer/LICENSE).

To intentionally update Adminer or an active Adminer plugin:

```bash
# edit adminer-vendor.json first, e.g. bump the Adminer release URL/version
python3 scripts/vendor_adminer.py lock
```

`lock` refreshes the pinned SHA-256 checksums and writes the configured source into `resources/adminer/`. CI uses `fetch`, which verifies those checksums and fails if the committed vendor files differ from their declared source.
