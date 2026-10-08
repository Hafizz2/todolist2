<?php
declare(strict_types=1);

/** Reads a value from miniapp/config.php (copy config.example.php to create it). */
function config(string $key): string
{
    static $config = null;
    if ($config === null) {
        $path = __DIR__ . '/../config.php';
        if (!is_file($path)) {
            throw new RuntimeException('miniapp/config.php is missing; copy config.example.php');
        }
        $config = require $path;
    }
    if (!isset($config[$key])) {
        throw new RuntimeException("Missing config key $key");
    }
    return (string) $config[$key];
}
