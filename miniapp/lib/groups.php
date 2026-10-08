<?php
declare(strict_types=1);

/* Group settings and goals, editable only by the group's owner (checked by the API). */

const PRIVACY_MODES = ['completion', 'group_total_only', 'full_counts'];
const GOAL_TYPES = ['counter', 'checkbox', 'quantity'];
const MAX_TARGET = 100000;
const MAX_LABEL = 100;

/** Well-known goals the owner can add in one tap. Labels come from lang/*.php (goal_<key>). */
const GOAL_PRESETS = [
    'salat_fajr' => ['checkbox', 1],
    'salat_dhuhr' => ['checkbox', 1],
    'salat_asr' => ['checkbox', 1],
    'salat_maghrib' => ['checkbox', 1],
    'salat_isha' => ['checkbox', 1],
    'salat_duha' => ['checkbox', 1],
    'salat_tahajjud' => ['checkbox', 1],
    'morning_adhkar' => ['checkbox', 1],
    'evening_adhkar' => ['checkbox', 1],
    'istighfar' => ['counter', 100],
    'salawat' => ['counter', 100],
    'tasbih' => ['counter', 33],
    'quran_pages' => ['quantity', 2],
    'sadaqah' => ['checkbox', 1],
];

/** Active group by id, or null. */
function find_group(PDO $pdo, int $groupId): ?array
{
    $stmt = $pdo->prepare(
        'SELECT id, title, owner_id, timezone, morning_time, night_time, privacy_mode
         FROM `groups` WHERE id = ? AND active = 1'
    );
    $stmt->execute([$groupId]);
    return $stmt->fetch() ?: null;
}

function group_view(array $group): array
{
    return [
        'id' => (int) $group['id'],
        'title' => $group['title'],
        'timezone' => $group['timezone'],
        'morning_time' => substr($group['morning_time'], 0, 5),
        'night_time' => substr($group['night_time'], 0, 5),
        'privacy_mode' => $group['privacy_mode'],
    ];
}

function list_group_goals(PDO $pdo, int $groupId): array
{
    $stmt = $pdo->prepare(
        'SELECT id, goal_key, label, type, target, active FROM goals WHERE group_id = ? ORDER BY id'
    );
    $stmt->execute([$groupId]);
    return array_map(static fn (array $g): array => [
        'id' => (int) $g['id'],
        'key' => $g['goal_key'],
        'label' => $g['label'],
        'type' => $g['type'],
        'target' => (int) $g['target'],
        'active' => (bool) $g['active'],
    ], $stmt->fetchAll());
}

function is_valid_time(mixed $value): bool
{
    return is_string($value) && preg_match('/^([01][0-9]|2[0-3]):[0-5][0-9]$/', $value) === 1;
}

function is_valid_target(mixed $value): bool
{
    return is_int($value) && $value >= 1 && $value <= MAX_TARGET;
}

/** Trimmed label, or null if empty / too long. */
function clean_label(mixed $value): ?string
{
    if (!is_string($value)) {
        return null;
    }
    $label = trim(preg_replace('/\s+/u', ' ', $value) ?? '');
    return ($label === '' || mb_strlen($label) > MAX_LABEL) ? null : $label;
}

function update_group_settings(PDO $pdo, int $groupId, string $timezone, string $morning, string $night, string $privacy): void
{
    $pdo->prepare(
        'UPDATE `groups` SET timezone = ?, morning_time = ?, night_time = ?, privacy_mode = ? WHERE id = ?'
    )->execute([$timezone, $morning . ':00', $night . ':00', $privacy, $groupId]);
}

/** Returns false if the group already has a goal with this key. */
function add_goal(PDO $pdo, int $groupId, string $key, string $label, string $type, int $target): bool
{
    $stmt = $pdo->prepare(
        'INSERT IGNORE INTO goals (group_id, goal_key, label, type, target) VALUES (?, ?, ?, ?, ?)'
    );
    $stmt->execute([$groupId, $key, $label, $type, $target]);
    return $stmt->rowCount() === 1;
}

/** Key and type never change: entries are stored by key, and other groups may share it. */
function update_goal(PDO $pdo, int $groupId, int $goalId, string $label, int $target, bool $active): bool
{
    $stmt = $pdo->prepare('SELECT type FROM goals WHERE id = ? AND group_id = ?');
    $stmt->execute([$goalId, $groupId]);
    $type = $stmt->fetchColumn();
    if ($type === false) {
        return false;
    }
    if ($type === 'checkbox') {
        $target = 1;
    }
    $pdo->prepare('UPDATE goals SET label = ?, target = ?, active = ? WHERE id = ?')
        ->execute([$label, $target, (int) $active, $goalId]);
    return true;
}
