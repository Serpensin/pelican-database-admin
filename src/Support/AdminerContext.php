<?php

namespace Serpensin\DatabaseAdmin\Support;

final class AdminerContext
{
    public function __construct(
        public readonly string $server,
        public readonly string $database,
        public readonly string $username,
        public readonly string $password,
        public readonly string $backUrl,
        public readonly int $queryTimeoutSeconds = 15,
        public readonly bool $allowExport = true,
        public readonly bool $allowImport = true,
    ) {}
}
