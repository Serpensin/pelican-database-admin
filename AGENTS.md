# Pelican Database Admin

This repository is a PHP 8.3 Pelican Panel plugin. It inserts a database-table action and renders bundled Adminer with the selected database's Pelican credentials and permissions.

## Layout

- `src/Actions/` adds the Filament table action; `src/Http/Controllers/AdminerController.php` authorizes and supplies the Adminer context.
- `src/Providers/` registers the database-table action and authenticated route group; `routes/web.php` owns the `GET`/`POST` Adminer route.
- `config/serpensin-database-admin.php` maps Panel `.env` variables to runtime configuration.
- `resources/adminer/` contains the pinned Adminer tree, upstream plugins, `index.php`, and custom plugins in `plugins-custom/`.
- `plugin.json` is the Pelican manifest; `update.json` is the update history and active release descriptor.

## Development environment

Run commands from the repository root (the directory containing `plugin.json`). CI uses `php:8.3-cli`; vendor verification uses Alpine 3.20 with Python 3 and PHP CLI.

The plugin reads these values from the host Pelican Panel `.env`, not from a Panel settings screen: `SERPENSIN_DATABASE_ADMIN_ENABLED`, `SERPENSIN_DATABASE_ADMIN_QUERY_TIMEOUT`, `SERPENSIN_DATABASE_ADMIN_ALLOW_EXPORT`, `SERPENSIN_DATABASE_ADMIN_ALLOW_IMPORT`, and `SERPENSIN_DATABASE_ADMIN_ROUTE_PREFIX`. Refresh the Panel configuration cache/PHP-FPM after changing them.

## Build and verification

```bash
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool update.json >/dev/null
python3 -m json.tool adminer-vendor.json >/dev/null
VENDOR_VERIFY_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pelican-database-admin-vendor-verify.XXXXXX")"
python3 scripts/vendor_adminer.py fetch --target "$VENDOR_VERIFY_DIR"
python3 scripts/ci_create_release_tag.py --dry-run
docker run --rm -v "$PWD":/work:ro -w /work php:8.3-cli sh -c \
  'find . -name "*.php" -print0 | xargs -0 -n1 php -l'
```

CI also runs `python3 scripts/vendor_adminer.py verify --target resources/adminer` and PHP syntax checks on the committed vendor tree.

## Conventions

- Use the `Serpensin\DatabaseAdmin` namespace. PHP source uses PSR-style class-per-file paths, strict scalar return types, constructor property promotion, and `trans('serpensin-database-admin::strings.*')` for UI text.
- Keep authorization parity between `OpenDatabaseAdminAction::canOpen()` and `AdminerController::__invoke()`: both require `DatabaseRead` and `DatabaseViewPassword` for the current server.
- Route names use `serpensin-database-admin.*`; config keys use `serpensin-database-admin.*`; environment variables use `SERPENSIN_DATABASE_ADMIN_*`.
- Keep panel-facing content in `README.md` limited to installation, operation, security, and licensing; maintainership detail belongs in `DEVNOTES.md`.

## Vendored Adminer

- Do not patch upstream files in `resources/adminer/`. Their source URLs and SHA-256 pins are in `adminer-vendor.json`.
- For intentional Adminer/plugin upgrades, update the manifest and run `python3 scripts/vendor_adminer.py lock`; then adjust `resources/adminer/index.php` for plugin-class changes and update README version/plugin text. Adminer 6.1.1 does not provide `pretty-json-column.php`.
- `verify` rejects unexpected files in the vendor tree except `index.php` and files under `plugins-custom/`.

## Releases

- On every release, set `plugin.json.version`, append a new immutable `releases[version]` entry in `update.json`, and make `update.json["*"]` exactly match it. Never alter or remove release history.
- The default-branch `create-release-tag` CI job runs only when `plugin.json` or `update.json` changes and creates the current `vX.Y.Z` tag. Do not add an unpublished version to `update.json`.
