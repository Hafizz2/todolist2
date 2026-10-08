<?php
declare(strict_types=1);

// POST {goal_key, amount} sets today's amount; POST {goal_key, delta} adds to it.

require_once __DIR__ . '/../lib/api.php';
require_once __DIR__ . '/../lib/entries.php';

require_method('POST');
$auth = authenticate();
$body = read_json_body();

$key = $body['goal_key'] ?? null;
$amount = $body['amount'] ?? null;
$delta = $body['delta'] ?? null;
if (!is_string($key) || ($amount === null) === ($delta === null)) {
    json_error('invalid_request', 400);
}
if ($amount !== null && (!is_int($amount) || $amount < 0 || $amount > MAX_AMOUNT)) {
    json_error('invalid_amount', 400);
}
if ($delta !== null && (!is_int($delta) || $delta < 1 || $delta > MAX_DELTA)) {
    json_error('invalid_delta', 400);
}

$userId = (int) $auth['user']['id'];
$date = user_today(db(), $userId);
$goal = find_goal(my_goals(db(), $userId, $date), $key);
if ($goal === null) {
    json_error('unknown_goal', 404);
}
if ($delta !== null && $goal['type'] === 'checkbox') {
    json_error('invalid_delta', 400);
}

json_response([
    'goal_key' => $goal['key'],
    'date' => $date,
    'amount' => save_entry(db(), $userId, $date, $goal, $amount, $delta),
]);
