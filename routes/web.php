<?php

use Illuminate\Support\Facades\Route;
use Serpensin\DatabaseAdmin\Http\Controllers\AdminerController;

Route::match(['get', 'post'], '/databases/{database}', AdminerController::class)
    ->name('serpensin-database-admin.open');
