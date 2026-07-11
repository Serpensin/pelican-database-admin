<?php

use Serpensin\DatabaseAdmin\Support\AdminerContext;

$context = $GLOBALS['SERPENSIN_DATABASE_ADMIN_CONTEXT'] ?? null;

if (!$context instanceof AdminerContext) {
    http_response_code(403);
    echo '<!doctype html><meta charset="utf-8"><p>Please open Adminer from the Pelican Panel.</p>';
    return;
}

$_GET['server'] = $context->server;
$_GET['username'] = $context->username;
$_GET['db'] = $context->database;
$_GET['driver'] = 'server';

if (!isset($_SESSION) || !is_array($_SESSION)) {
    $_SESSION = [];
}


$adminerLanguage = static function (): string {
    $supported = [
        'en', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'da', 'de', 'el', 'es', 'et', 'fa', 'fi', 'fr', 'gl',
        'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'ka', 'ko', 'lt', 'lv', 'ms', 'nl', 'no', 'pl', 'pt',
        'pt-br', 'ro', 'ru', 'sk', 'sl', 'sr', 'sv', 'ta', 'th', 'tr', 'uk', 'uz', 'vi', 'zh', 'zh-tw',
    ];

    $locale = (string) (user()?->language ?: app()->getLocale() ?: 'en');
    $locale = strtolower(str_replace('_', '-', $locale));

    if (in_array($locale, $supported, true)) {
        return $locale;
    }

    $baseLocale = preg_replace('/-.*/', '', $locale);

    return in_array($baseLocale, $supported, true) ? $baseLocale : 'en';
};

$_COOKIE['adminer_lang'] = $adminerLanguage();
$_SESSION['lang'] = $_COOKIE['adminer_lang'];

function adminer_object() {
    include_once __DIR__ . '/plugins/timeout.php';
    include_once __DIR__ . '/plugins/tables-filter.php';
    include_once __DIR__ . '/plugins/table-structure.php';
    include_once __DIR__ . '/plugins/edit-textarea.php';
    include_once __DIR__ . '/plugins/pretty-json-column.php';
    include_once __DIR__ . '/plugins/dump-date.php';
    include_once __DIR__ . '/plugins/dump-zip.php';
    include_once __DIR__ . '/plugins/version-noverify.php';
    include_once __DIR__ . '/plugins-custom/pelican-single-database.php';

    $context = $GLOBALS['SERPENSIN_DATABASE_ADMIN_CONTEXT'];

    return new Adminer\Plugins([
        new PelicanSingleDatabaseAdminer($context),
        new AdminerTimeout($context->queryTimeoutSeconds),
        new AdminerTablesFilter(),
        new AdminerTableStructure(),
        new AdminerEditTextarea(),
        new AdminerPrettyJsonColumn(),
        new AdminerDumpDate(),
        new AdminerDumpZip(),
        new AdminerVersionNoverify(),
    ]);
}

require __DIR__ . '/adminer.php';
