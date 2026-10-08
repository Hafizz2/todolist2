<?php
declare(strict_types=1);

// Mini App shell. Data comes from api/*.php, authenticated with Telegram initData.

require_once __DIR__ . '/lib/lang.php';

header('Content-Type: text/html; charset=utf-8');

$i18n = json_encode(lang_tables(), JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP | JSON_THROW_ON_ERROR);
$asset = static fn (string $path): string => htmlspecialchars(
    $path . '?v=' . (string) @filemtime(__DIR__ . '/' . $path),
    ENT_QUOTES
);
?><!doctype html>
<html lang="<?= htmlspecialchars(DEFAULT_LANG, ENT_QUOTES) ?>">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Zikr Circle</title>
  <link rel="stylesheet" href="<?= $asset('assets/style.css') ?>">
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
  <main>
    <section id="view-loading" class="view center"><div class="spinner"></div></section>

    <section id="view-message" class="view center" hidden>
      <p id="message"></p>
    </section>

    <section id="view-day" class="view" hidden>
      <header class="day-header">
        <h1 data-i18n="my_day"></h1>
        <p id="day-progress" class="hint"></p>
        <div class="progress"><div id="day-bar"></div></div>
      </header>
      <p id="notice" class="notice" hidden></p>
      <p id="day-empty" class="hint center-text" data-i18n="empty" hidden></p>
      <ul id="goal-list" class="goals"></ul>
    </section>

    <section id="view-counter" class="view counter" hidden>
      <h2 id="counter-label"></h2>
      <p id="counter-target" class="hint"></p>
      <button id="counter-tap" class="tap" type="button">
        <span id="counter-count">0</span>
        <small data-i18n="tap"></small>
      </button>
      <p id="counter-done" class="done-msg" data-i18n="counter_done" hidden></p>
      <button id="counter-reset" class="link" type="button" data-i18n="reset"></button>
    </section>

    <section id="view-settings" class="view" hidden>
      <header class="day-header">
        <h1 id="settings-title"></h1>
        <p class="hint" data-i18n="group_settings"></p>
      </header>

      <h2 class="section-title" data-i18n="goals"></h2>
      <ul id="settings-goals" class="goals"></ul>

      <h2 class="section-title" data-i18n="add_goal"></h2>
      <div class="card">
        <label class="row"><select id="add-preset"></select></label>
        <div id="add-custom" hidden>
          <label class="row"><input id="add-label" type="text" maxlength="100"></label>
          <label class="row"><select id="add-type"></select></label>
        </div>
        <label id="add-target-row" class="row">
          <span data-i18n="daily_target"></span>
          <input id="add-target" class="target-input" type="number" min="1" max="100000" inputmode="numeric">
        </label>
        <div class="row"><button id="add-goal" class="button" type="button" data-i18n="add"></button></div>
      </div>

      <h2 class="section-title" data-i18n="schedule"></h2>
      <div class="card">
        <label class="row"><span data-i18n="morning_time"></span><input id="set-morning" type="time"></label>
        <label class="row"><span data-i18n="night_time"></span><input id="set-night" type="time"></label>
        <label class="row"><span data-i18n="timezone"></span><select id="set-timezone"></select></label>
      </div>

      <h2 class="section-title" data-i18n="privacy"></h2>
      <div id="set-privacy" class="card"></div>
    </section>
  </main>
  <div id="toast" class="toast" hidden></div>

  <script id="i18n" type="application/json"><?= $i18n ?></script>
  <script src="<?= $asset('assets/core.js') ?>"></script>
  <script src="<?= $asset('assets/settings.js') ?>"></script>
  <script src="<?= $asset('assets/app.js') ?>"></script>
</body>
</html>
