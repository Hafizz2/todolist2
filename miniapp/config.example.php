<?php
declare(strict_types=1);

// Copy to config.php (git-ignored) and fill in real values.
// With docker-compose, DB_HOST is "db"; on cPanel it is usually "localhost".
return [
    'BOT_TOKEN'   => '123456:replace-me',
    'DB_HOST'     => 'db',
    'DB_NAME'     => 'zikr_circle',
    'DB_USER'     => 'zikr',
    'DB_PASS'     => 'zikr',
    'MINIAPP_URL' => 'https://example.com/miniapp/',
];
