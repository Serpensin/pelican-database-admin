<?php

namespace Serpensin\DatabaseAdmin\Providers;

use App\Filament\Server\Resources\Databases\DatabaseResource;
use Filament\Tables\Table;
use Illuminate\Support\ServiceProvider;
use Serpensin\DatabaseAdmin\Actions\OpenDatabaseAdminAction;

class SerpensinDatabaseAdminProvider extends ServiceProvider
{
    public function register(): void
    {
        DatabaseResource::modifyTable(function (Table $table): Table {
            $actions = $table->getRecordActions();
            array_splice($actions, 1, 0, [OpenDatabaseAdminAction::make()]);

            return $table->recordActions($actions);
        });
    }

    public function boot(): void {}
}
