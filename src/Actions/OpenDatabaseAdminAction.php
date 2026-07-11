<?php

namespace Serpensin\DatabaseAdmin\Actions;

use App\Enums\SubuserPermission;
use App\Models\Database;
use Filament\Actions\Action;
use Filament\Facades\Filament;

class OpenDatabaseAdminAction extends Action
{
    public static function getDefaultName(): ?string
    {
        return 'serpensin_database_admin_open';
    }

    protected function setUp(): void
    {
        parent::setUp();

        $this->hiddenLabel();
        $this->icon('tabler-database-edit');
        $this->tooltip(trans('serpensin-database-admin::strings.open'));
        $this->color('info');
        $this->openUrlInNewTab();
        $this->visible(fn (Database $database) => (bool) config('serpensin-database-admin.enabled', true) && $this->canOpen($database));
        $this->url(fn (Database $database) => route('serpensin-database-admin.open', ['database' => $database->id]));
    }

    private function canOpen(Database $database): bool
    {
        $server = Filament::getTenant() ?: $database->server;

        return (bool) user()?->can(SubuserPermission::DatabaseRead, $server)
            && (bool) user()?->can(SubuserPermission::DatabaseViewPassword, $server);
    }
}
