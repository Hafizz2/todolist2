<?php
declare(strict_types=1);

/** Creates the user on first contact (they may open the app before ever messaging the bot). */
function upsert_user(PDO $pdo, array $tgUser): array
{
    $name = trim(($tgUser['first_name'] ?? '') . ' ' . ($tgUser['last_name'] ?? ''));
    $pdo->prepare(
        'INSERT INTO users (telegram_id, name) VALUES (?, ?)
         ON DUPLICATE KEY UPDATE name = VALUES(name)'
    )->execute([$tgUser['id'], mb_substr($name, 0, 255)]);

    $stmt = $pdo->prepare('SELECT id, telegram_id, name, lang FROM users WHERE telegram_id = ?');
    $stmt->execute([$tgUser['id']]);
    return $stmt->fetch();
}
