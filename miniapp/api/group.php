<?php
declare(strict_types=1);

// Group settings (owner only).
// GET ?id=N  -> settings, goals, presets, timezones
// POST {id, timezone, morning_time, night_time, privacy_mode} -> updated settings

require_once __DIR__ . '/../lib/api.php';
require_once __DIR__ . '/../lib/groups.php';

$auth = authenticate();

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET') {
    $id = filter_var($_GET['id'] ?? null, FILTER_VALIDATE_INT);
    $group = require_owned_group($auth, $id === false ? null : $id);
    json_response([
        'group' => group_view($group),
        'goals' => list_group_goals(db(), (int) $group['id']),
        'presets' => array_map(
            static fn (string $key, array $p): array => ['key' => $key, 'type' => $p[0], 'target' => $p[1]],
            array_keys(GOAL_PRESETS),
            GOAL_PRESETS
        ),
        'timezones' => DateTimeZone::listIdentifiers(),
    ]);
}

require_method('POST');
$body = read_json_body();
$group = require_owned_group($auth, $body['id'] ?? null);

$timezone = $body['timezone'] ?? null;
$morning = $body['morning_time'] ?? null;
$night = $body['night_time'] ?? null;
$privacy = $body['privacy_mode'] ?? null;
if (!is_string($timezone) || !in_array($timezone, DateTimeZone::listIdentifiers(), true)) {
    json_error('invalid_timezone', 400);
}
if (!is_valid_time($morning) || !is_valid_time($night)) {
    json_error('invalid_time', 400);
}
// The night summary covers the group's local day, so it must come after the morning post.
if (strcmp($morning, $night) >= 0) {
    json_error('night_before_morning', 400);
}
if (!in_array($privacy, PRIVACY_MODES, true)) {
    json_error('invalid_privacy_mode', 400);
}

update_group_settings(db(), (int) $group['id'], $timezone, $morning, $night, $privacy);
json_response(['group' => group_view(find_group(db(), (int) $group['id']))]);
