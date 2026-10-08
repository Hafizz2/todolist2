<?php
declare(strict_types=1);

/*
 * My Day + entries. Log once, applies everywhere: an entry is per user + goal_key + date and
 * counts for every group that has a goal with that key.
 */

const DEFAULT_TIMEZONE = 'Africa/Addis_Ababa';
const MAX_AMOUNT = 1000000;
const MAX_DELTA = 10000;

/**
 * A user's "today". Entries aren't per group, so we use the timezone of the first group the
 * user joined (groups in one circle normally share a timezone), else the default.
 */
function user_today(PDO $pdo, int $userId, ?DateTimeImmutable $now = null): string
{
    $stmt = $pdo->prepare(
        'SELECT g.timezone FROM group_members m
         JOIN `groups` g ON g.id = m.group_id AND g.active = 1
         WHERE m.user_id = ? ORDER BY m.joined_at, g.id LIMIT 1'
    );
    $stmt->execute([$userId]);
    $tzName = $stmt->fetchColumn() ?: DEFAULT_TIMEZONE;
    try {
        $tz = new DateTimeZone($tzName);
    } catch (Exception) {
        $tz = new DateTimeZone(DEFAULT_TIMEZONE);
    }
    return ($now ?? new DateTimeImmutable())->setTimezone($tz)->format('Y-m-d');
}

/**
 * The user's goals across all their active groups, one row per goal_key, with today's amount.
 * When groups disagree on a key, the strictest (highest-target) goal wins.
 */
function my_goals(PDO $pdo, int $userId, string $date): array
{
    $stmt = $pdo->prepare(
        'SELECT x.goal_key, x.label, x.type, x.target, x.group_count,
                COALESCE(e.amount, 0) AS amount
         FROM (
             SELECT g.goal_key, g.label, g.type, g.target,
                    ROW_NUMBER() OVER (PARTITION BY g.goal_key ORDER BY g.target DESC, g.id) AS rn,
                    COUNT(*)     OVER (PARTITION BY g.goal_key) AS group_count,
                    MIN(g.id)    OVER (PARTITION BY g.goal_key) AS first_id
             FROM goals g
             JOIN group_members m ON m.group_id = g.group_id AND m.user_id = ?
             JOIN `groups` gr ON gr.id = g.group_id AND gr.active = 1
             WHERE g.active = 1
         ) x
         LEFT JOIN entries e
                ON e.user_id = ? AND e.goal_key = x.goal_key AND e.entry_date = ?
         WHERE x.rn = 1
         ORDER BY x.first_id'
    );
    $stmt->execute([$userId, $userId, $date]);
    return array_map(static fn (array $row): array => [
        'key' => $row['goal_key'],
        'label' => $row['label'],
        'type' => $row['type'],
        'target' => (int) $row['target'],
        'groups' => (int) $row['group_count'],
        'amount' => (int) $row['amount'],
    ], $stmt->fetchAll());
}

function find_goal(array $goals, string $key): ?array
{
    foreach ($goals as $goal) {
        if ($goal['key'] === $key) {
            return $goal;
        }
    }
    return null;
}

/**
 * Applies `amount` (absolute) or `delta` (increment, used by the zikr counter's batched taps)
 * to today's entry. Returns the stored amount.
 */
function save_entry(PDO $pdo, int $userId, string $date, array $goal, ?int $amount, ?int $delta): int
{
    if ($delta !== null) {
        $pdo->prepare(
            'INSERT INTO entries (user_id, goal_key, entry_date, amount) VALUES (?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE amount = LEAST(amount + VALUES(amount), ' . MAX_AMOUNT . ')'
        )->execute([$userId, $goal['key'], $date, $delta]);
    } else {
        if ($goal['type'] === 'checkbox') {
            $amount = min($amount, 1);
        }
        $pdo->prepare(
            'INSERT INTO entries (user_id, goal_key, entry_date, amount) VALUES (?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE amount = VALUES(amount)'
        )->execute([$userId, $goal['key'], $date, $amount]);
    }

    $stmt = $pdo->prepare(
        'SELECT amount FROM entries WHERE user_id = ? AND goal_key = ? AND entry_date = ?'
    );
    $stmt->execute([$userId, $goal['key'], $date]);
    return (int) $stmt->fetchColumn();
}
