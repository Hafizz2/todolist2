<?php
declare(strict_types=1);

const SUPPORTED_LANGS = ['am', 'en'];
const DEFAULT_LANG = 'am';

/** All string tables, keyed by language. */
function lang_tables(): array
{
    $tables = [];
    foreach (SUPPORTED_LANGS as $lang) {
        $tables[$lang] = require __DIR__ . "/../lang/$lang.php";
    }
    return $tables;
}
