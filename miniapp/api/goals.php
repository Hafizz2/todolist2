<?php
declare(strict_types=1);

// Group goals (owner only). Returns the group's full goal list.
// POST {group_id, action: "add", preset: key, target}
// POST {group_id, action: "add", label, type, target}             (custom goal)
// POST {group_id, action: "update", goal_id, label, target, active}

require_once __DIR__ . '/../lib/api.php';
require_once __DIR__ . '/../lib/groups.php';
require_once __DIR__ . '/../lib/lang.php';

require_method('POST');
$auth = authenticate();
$body = read_json_body();
$group = require_owned_group($auth, $body['group_id'] ?? null);
$groupId = (int) $group['id'];
$target = $body['target'] ?? null;

switch ($body['action'] ?? null) {
    case 'add':
        if (!is_valid_target($target)) {
            json_error('invalid_target', 400);
        }
        $preset = $body['preset'] ?? null;
        if ($preset !== null) {
            if (!is_string($preset) || !isset(GOAL_PRESETS[$preset])) {
                json_error('invalid_preset', 400);
            }
            $key = $preset;
            $type = GOAL_PRESETS[$preset][0];
            $lang = in_array($auth['user']['lang'], SUPPORTED_LANGS, true) ? $auth['user']['lang'] : DEFAULT_LANG;
            $label = lang_tables()[$lang]["goal_$key"];
        } else {
            $label = clean_label($body['label'] ?? null);
            $type = $body['type'] ?? null;
            if ($label === null) {
                json_error('invalid_label', 400);
            }
            if (!in_array($type, GOAL_TYPES, true)) {
                json_error('invalid_type', 400);
            }
            $key = 'custom_' . bin2hex(random_bytes(6));
        }
        if ($type === 'checkbox') {
            $target = 1;
        }
        if (!add_goal(db(), $groupId, $key, $label, $type, $target)) {
            json_error('goal_exists', 409);
        }
        break;

    case 'update':
        $label = clean_label($body['label'] ?? null);
        $active = $body['active'] ?? null;
        $goalId = $body['goal_id'] ?? null;
        if ($label === null) {
            json_error('invalid_label', 400);
        }
        if (!is_valid_target($target) || !is_bool($active) || !is_int($goalId)) {
            json_error('invalid_request', 400);
        }
        if (!update_goal(db(), $groupId, $goalId, $label, $target, $active)) {
            json_error('goal_not_found', 404);
        }
        break;

    default:
        json_error('invalid_action', 400);
}

json_response(['goals' => list_group_goals(db(), $groupId)]);
