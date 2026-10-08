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

/** The active group with this id if the signed-in user owns it; responds 404/403 otherwise. */
function require_owned_group(array $auth, mixed $groupId): array
{
    require_once __DIR__ . '/groups.php';
    $group = is_int($groupId) ? find_group(db(), $groupId) : null;
    if ($group === null) {
        json_error('group_not_found', 404);
    }
    if ((int) $group['owner_id'] !== (int) $auth['user']['id']) {
        json_error('not_owner', 403);
    }
    return $group;
}
