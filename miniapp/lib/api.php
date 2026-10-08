<?php
declare(strict_types=1);

/** Common bootstrap for api/*.php: JSON errors, DB, and the authenticated user. */

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/db.php';
require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/http.php';
require_once __DIR__ . '/users.php';

set_exception_handler(static function (Throwable $e): void {
    error_log('miniapp: ' . $e);
    json_error('server_error', 500);
});

/**
 * Validates the initData sent in the X-Telegram-Init-Data header and returns
 * ['user' => users row, 'init' => validated initData fields]. Responds 401 otherwise.
 */
function authenticate(): array
{
    $initData = $_SERVER['HTTP_X_TELEGRAM_INIT_DATA'] ?? '';
    $init = $initData === '' ? null : validate_init_data($initData, config('BOT_TOKEN'));
    if ($init === null) {
        json_error('unauthorized', 401);
    }
    return ['user' => upsert_user(db(), $init['user']), 'init' => $init];
}
