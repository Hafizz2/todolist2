<?php
declare(strict_types=1);

/**
 * Telegram Mini App initData validation.
 * https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
 */

const INIT_DATA_MAX_AGE = 86400; // seconds; initData isn't refreshed while the app stays open

/**
 * Returns the validated fields (with `user` JSON-decoded), or null if the data is forged,
 * malformed or older than $maxAge seconds.
 */
function validate_init_data(string $initData, string $botToken, int $maxAge = INIT_DATA_MAX_AGE, ?int $now = null): ?array
{
    $fields = [];
    foreach (explode('&', $initData) as $pair) {
        if ($pair === '' || !str_contains($pair, '=')) {
            return null;
        }
        [$key, $value] = explode('=', $pair, 2);
        $fields[urldecode($key)] = urldecode($value);
    }

    $hash = $fields['hash'] ?? '';
    unset($fields['hash']);
    if ($hash === '' || !isset($fields['auth_date'], $fields['user'])) {
        return null;
    }

    ksort($fields, SORT_STRING);
    $lines = [];
    foreach ($fields as $key => $value) {
        $lines[] = $key . '=' . $value;
    }
    $secret = hash_hmac('sha256', $botToken, 'WebAppData', true);
    $expected = hash_hmac('sha256', implode("\n", $lines), $secret);
    if (!hash_equals($expected, strtolower($hash))) {
        return null;
    }

    $age = ($now ?? time()) - (int) $fields['auth_date'];
    if ($age > $maxAge || $age < -300) {
        return null;
    }

    $user = json_decode($fields['user'], true);
    if (!is_array($user) || !isset($user['id']) || !is_int($user['id'])) {
        return null;
    }
    $fields['user'] = $user;
    return $fields;
}

/** `group_<id>` start_param (set by the bot's /setup link) -> group id, else null. */
function group_id_from_start_param(?string $startParam): ?int
{
    if ($startParam !== null && preg_match('/^group_([1-9][0-9]{0,18})$/', $startParam, $m)) {
        return (int) $m[1];
    }
    return null;
}
