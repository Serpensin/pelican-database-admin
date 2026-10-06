# Database Admin

Pelican Panel plugin that adds a database edit button to the server `Databases` table and opens the selected database in a bundled, Pelican-authenticated Adminer instance.

## Features

- Adds an icon button next to Pelican's database view action.
- Uses the database credentials already stored by Pelican.
- No public free-form Adminer login form.
- Restricts Adminer to the selected database through an Adminer plugin.
- Uses [Adminer](https://www.adminer.org/) 6.1.1 for database management.
- Active Adminer plugins: query timeout, table filter, improved table structure, textarea editing, dated ZIP exports, and disabled version checks.
- Imports are enabled by default.

## Security model

Users must be authenticated in Pelican and must have `DatabaseRead` plus `DatabaseViewPassword` for the current server. The plugin connects with the per-database MariaDB user stored by Pelican. MariaDB grants remain the final isolation boundary.

Do not grant Pelican database users global privileges. They should only have privileges on their own database.

## Install

Install it from PelicanHub, or copy the repository folder to `plugins/serpensin-database-admin` and run:

```bash
php artisan p:plugin:install serpensin-database-admin
```

This plugin is licensed under [MIT](LICENSE). Bundled Adminer is separately dual-licensed under Apache License 2.0 or GPL 2.0; its upstream license notice is retained at [`resources/adminer/LICENSE`](resources/adminer/LICENSE).
