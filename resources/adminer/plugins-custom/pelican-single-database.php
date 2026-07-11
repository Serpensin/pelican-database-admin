<?php

use Serpensin\DatabaseAdmin\Support\AdminerContext;

class PelicanSingleDatabaseAdminer extends Adminer\Plugin
{
    public function __construct(private readonly AdminerContext $context)
    {
        // This runs from Adminer's runtime after its helper functions have been
        // declared. Let Adminer encrypt the password itself when it has an
        // adminer_key cookie; never place the raw password into the session.
        Adminer\set_password('server', $context->server, $context->username, $context->password);
        $_SESSION['db']['server'][$context->server][$context->username][$context->database] = true;
    }

    public function name()
    {
        return 'Pelican Database Admin';
    }

    public function credentials()
    {
        return [$this->context->server, $this->context->username, $this->context->password];
    }

    public function database()
    {
        return $this->context->database;
    }

    public function databases($flush = true)
    {
        return [$this->context->database];
    }

    public function login($login, $password)
    {
        return true;
    }

    public function head($dark = null)
    {
        echo "<style>#lang{display:none!important}</style>\n";
    }

    public function loginForm()
    {
        echo '<p>' . Adminer\h(trans('serpensin-database-admin::strings.open_from_panel')) . '</p>';
        echo '<p><a href="' . Adminer\h($this->context->backUrl) . '">' . Adminer\h(trans('serpensin-database-admin::strings.back_to_panel')) . '</a></p>';
    }

    public function navigation($missing)
    {
        echo '<p><a href="' . Adminer\h($this->context->backUrl) . '">← ' . Adminer\h(trans('serpensin-database-admin::strings.back_to_panel')) . '</a></p>';
    }

    public function dumpOutput()
    {
        if (!$this->context->allowExport) {
            return [];
        }
    }

    public function importServerPath()
    {
        return $this->context->allowImport ? null : false;
    }

    public function importPath()
    {
        return $this->context->allowImport ? null : false;
    }
}
