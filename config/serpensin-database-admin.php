<?php

return [
    'enabled' => env('SERPENSIN_DATABASE_ADMIN_ENABLED', true),
    'query_timeout_seconds' => (int) env('SERPENSIN_DATABASE_ADMIN_QUERY_TIMEOUT', 15),
    'allow_export' => env('SERPENSIN_DATABASE_ADMIN_ALLOW_EXPORT', true),
    'allow_import' => env('SERPENSIN_DATABASE_ADMIN_ALLOW_IMPORT', true),
    'route_prefix' => env('SERPENSIN_DATABASE_ADMIN_ROUTE_PREFIX', 'database-admin'),
];
