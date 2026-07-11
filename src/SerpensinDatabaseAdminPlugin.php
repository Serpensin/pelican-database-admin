<?php

namespace Serpensin\DatabaseAdmin;

use Filament\Contracts\Plugin;
use Filament\Panel;

class SerpensinDatabaseAdminPlugin implements Plugin
{
    public function getId(): string
    {
        return 'serpensin-database-admin';
    }

    public function register(Panel $panel): void {}

    public function boot(Panel $panel): void {}
}
