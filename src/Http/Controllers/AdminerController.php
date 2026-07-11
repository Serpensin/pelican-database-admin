<?php

namespace Serpensin\DatabaseAdmin\Http\Controllers;

use App\Enums\SubuserPermission;
use App\Filament\Server\Resources\Databases\DatabaseResource;
use App\Models\Database;
use Filament\Facades\Filament;
use Illuminate\Http\Request;
use Illuminate\Routing\Controller;
use Serpensin\DatabaseAdmin\Support\AdminerContext;
use Symfony\Component\HttpFoundation\Response;

class AdminerController extends Controller
{
    public function __invoke(Request $request, Database $database): Response
    {
        abort_unless((bool) config('serpensin-database-admin.enabled', true), 404, trans('serpensin-database-admin::strings.disabled'));

        $database->loadMissing(['host', 'server']);
        $server = Filament::getTenant() ?: $database->server;

        abort_unless($server && $database->server_id === $server->id, 404);
        abort_unless(user()?->can(SubuserPermission::DatabaseRead, $server), 403, trans('serpensin-database-admin::strings.not_allowed'));
        abort_unless(user()?->can(SubuserPermission::DatabaseViewPassword, $server), 403, trans('serpensin-database-admin::strings.not_allowed'));

        $context = new AdminerContext(
            server: $database->host->host . ':' . $database->host->port,
            database: $database->database,
            username: $database->username,
            password: $database->password,
            backUrl: DatabaseResource::getUrl(panel: 'server', tenant: $server),
            queryTimeoutSeconds: (int) config('serpensin-database-admin.query_timeout_seconds', 15),
            allowExport: (bool) config('serpensin-database-admin.allow_export', true),
            allowImport: (bool) config('serpensin-database-admin.allow_import', true),
        );

        $previousContext = $GLOBALS['SERPENSIN_DATABASE_ADMIN_CONTEXT'] ?? null;
        $GLOBALS['SERPENSIN_DATABASE_ADMIN_CONTEXT'] = $context;

        ob_start();
        try {
            require plugin_path('serpensin-database-admin', 'resources/adminer/index.php');
            $content = ob_get_clean();
        } catch (\Throwable $throwable) {
            if (ob_get_level() > 0) {
                ob_end_clean();
            }

            throw $throwable;
        } finally {
            if ($previousContext instanceof AdminerContext) {
                $GLOBALS['SERPENSIN_DATABASE_ADMIN_CONTEXT'] = $previousContext;
            } else {
                unset($GLOBALS['SERPENSIN_DATABASE_ADMIN_CONTEXT']);
            }
        }

        return response($content);
    }
}
