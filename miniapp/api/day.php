<?php
declare(strict_types=1);

// GET: the signed-in user's My Day checklist for today.

require_once __DIR__ . '/../lib/api.php';
require_once __DIR__ . '/../lib/entries.php';

require_method('GET');
$auth = authenticate();
$user = $auth['user'];
$date = user_today(db(), (int) $user['id']);

json_response([
    'user' => ['name' => $user['name'], 'lang' => $user['lang']],
    'date' => $date,
    'group_id' => group_id_from_start_param($auth['init']['start_param'] ?? null),
    'goals' => my_goals(db(), (int) $user['id'], $date),
]);
