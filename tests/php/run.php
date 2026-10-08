<?php
declare(strict_types=1);

// Plain-PHP tests for the Mini App (no PHPUnit needed): php tests/php/run.php

require __DIR__ . '/../../miniapp/lib/auth.php';

$failures = 0;
function check(string $name, bool $ok): void
{
    global $failures;
    echo ($ok ? 'ok   ' : 'FAIL ') . $name . PHP_EOL;
    $failures += $ok ? 0 : 1;
}

/** Builds initData the way Telegram does, signed with $token. */
function sign_init_data(array $fields, string $token): string
{
    ksort($fields);
    $lines = [];
    foreach ($fields as $k => $v) {
        $lines[] = "$k=$v";
    }
    $secret = hash_hmac('sha256', $token, 'WebAppData', true);
    $fields['hash'] = hash_hmac('sha256', implode("\n", $lines), $secret);
    return http_build_query($fields, '', '&', PHP_QUERY_RFC3986);
}

$token = '12345:TEST_TOKEN';
$now = 1_800_000_000;
$fields = [
    'auth_date' => (string) $now,
    'query_id' => 'AAH',
    'user' => json_encode(['id' => 101, 'first_name' => 'Ab dul', 'language_code' => 'am']),
    'start_param' => 'group_7',
];
$good = sign_init_data($fields, $token);

$result = validate_init_data($good, $token, 86400, $now + 60);
check('valid initData is accepted', $result !== null);
check('user is decoded', ($result['user']['id'] ?? null) === 101 && $result['user']['first_name'] === 'Ab dul');
check('start_param is kept', ($result['start_param'] ?? null) === 'group_7');
check('wrong bot token is rejected', validate_init_data($good, '999:OTHER', 86400, $now) === null);
check('tampered field is rejected', validate_init_data(str_replace('group_7', 'group_8', $good), $token, 86400, $now) === null);
check('missing hash is rejected', validate_init_data(preg_replace('/&?hash=[0-9a-f]+/', '', $good), $token, 86400, $now) === null);
check('stale auth_date is rejected', validate_init_data($good, $token, 86400, $now + 86401) === null);
check('future auth_date is rejected', validate_init_data($good, $token, 86400, $now - 3600) === null);
check('garbage is rejected', validate_init_data('not init data', $token) === null);
check('empty is rejected', validate_init_data('', $token) === null);

check('group_ start param parses', group_id_from_start_param('group_42') === 42);
foreach ([null, '', 'group_', 'group_0', 'group_-1', 'group_1x', 'setup_3'] as $p) {
    check('start param ' . var_export($p, true) . ' is ignored', group_id_from_start_param($p) === null);
}

exit($failures ? 1 : 0);
