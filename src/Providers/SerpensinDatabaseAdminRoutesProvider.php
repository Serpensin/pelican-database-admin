<?php

namespace Serpensin\DatabaseAdmin\Providers;

use Illuminate\Foundation\Support\Providers\RouteServiceProvider;
use Illuminate\Support\Facades\Route;

class SerpensinDatabaseAdminRoutesProvider extends RouteServiceProvider
{
    public function boot(): void
    {
        $this->routes(function () {
            Route::middleware(['web', 'auth'])
                ->prefix(config('serpensin-database-admin.route_prefix', 'database-admin'))
                ->group(plugin_path('serpensin-database-admin', 'routes/web.php'));
        });
    }
}
