# Zikr Circle — Telegram Group Worship Challenge Bot

Muslims form daily worship challenges inside their Telegram groups. A Python bot posts reminders and nightly summaries. A simple PHP Mini App provides a zikr counter and a daily checklist. Both share one MySQL database.

## Stack
- `bot/` — Python 3.11+, aiogram 3, APScheduler (timezone-aware jobs), aiomysql or SQLAlchemy (async) + PyMySQL
- `miniapp/` — Plain PHP 8 + PDO, vanilla JS, one small CSS file. No framework, no build step. Must run on ordinary shared hosting (cPanel).
- `db/` — MySQL 8. Plain numbered SQL migration files (`001_init.sql`, `002_...sql`). These are the single source of truth for the schema, shared by Python and PHP.
- Local dev: docker-compose with MySQL + PHP-Apache. The bot runs locally with long polling.
- Config: `.env` for the bot, `miniapp/config.php` (git-ignored) with a `config.example.php` template. Keys: BOT_TOKEN, DB_HOST, DB_NAME, DB_USER, DB_PASS, MINIAPP_URL, MINIAPP_SHORT_NAME (bot only: the Mini App's BotFather short name)
- i18n: Amharic (default) + English. Bot strings in `bot/locales/*.json`, Mini App strings in `miniapp/lang/*.php`.

## Responsibility split
- **Python bot**: commands, group registration, membership, scheduled morning/night posts, leaderboard calculation.
- **PHP Mini App**: all user-facing screens and a small JSON API (`miniapp/api/*.php`) that reads and writes entries and goals.
- They never call each other. They only share the database.

## Core concepts
- **User**: a Telegram user. Can own many groups and join many group challenges.
- **Group**: a Telegram group chat the bot was added to. It has one owner (the user who ran /setup), a timezone (default `Africa/Addis_Ababa`), a morning time, a night time, and a privacy mode.
- **Goal**: belongs to a group. Fields: type (`counter` | `checkbox` | `quantity`), key (e.g. `istighfar`, `salat_fajr`, `quran_pages`), label, daily target.
- **Entry**: a user's progress for a goal key on a date. **Log once, applies everywhere.** Entries are stored per user + goal key + date, not per group. Every group with a goal of the same key reads the same entry. Each group's leaderboard is still computed separately.

## Schema (MySQL, utf8mb4)
users(id, telegram_id UNIQUE, name, lang, created_at)
`groups`(id, chat_id UNIQUE, title, owner_id NULL until /setup, timezone, morning_time, night_time, privacy_mode ENUM('completion','group_total_only','full_counts') DEFAULT 'completion', active BOOL (0 once the bot is removed), created_at)
group_members(group_id, user_id, joined_at, hide_my_stats BOOL DEFAULT 0) — PK(group_id, user_id)
goals(id, group_id, goal_key, label, type ENUM('counter','checkbox','quantity'), target INT, active BOOL) — UNIQUE(group_id, goal_key)
entries(id, user_id, goal_key, entry_date DATE, amount INT, updated_at) — UNIQUE(user_id, goal_key, entry_date)
group_posts(group_id, kind ENUM('morning','night'), post_date DATE, sent_at) — PK(group_id, kind, post_date); the scheduler's record of what it has posted

Note: `groups` is a reserved word in MySQL 8, so always backtick it (or name the table `tg_groups`).

## Privacy / riya guidelines (important)
- The default nightly post shows **completion** ("4/5 goals ✅") and **streaks**, never raw worship counts.
- `privacy_mode`: `completion` (default) | `group_total_only` | `full_counts` (owner opt-in).
- Members can set `hide_my_stats`, which shows them as "a member" in summaries.
- Never rank people by raw istighfar/zikr counts by default.

## Bot behavior
- `/start` (private): welcome, language choice, "Add me to your group" button.
- Added to group → owner runs `/setup` → button opens the Mini App in group-config mode. The first `/setup` seeds starter goals (5 prayers, istighfar, salawat, Qur'an pages).
- Opening the Mini App: Telegram forbids web_app buttons in groups, so the bot always uses direct links `https://t.me/<bot>/<MINIAPP_SHORT_NAME>?startapp=<param>`. Group-config mode is `startapp=group_<groups.id>`, read from the validated initData `start_param`. The private-chat menu button opens MINIAPP_URL.
- `/join` in group: registers the member.
- `/today` in group: the member's progress, with a button to open the Mini App.
- Morning job: posts today's challenge + Mini App button.
- Night job: posts the summary according to privacy_mode.
- Only the owner can edit goals or settings. Enforce this in PHP too.
- Jobs: one APScheduler job every minute checks which groups are due in their own timezone (30 min grace for late ticks). It claims each post in `group_posts` before sending, so a post goes out once per local day; a failed send releases the claim and is retried, and a kicked bot deactivates the group. Times are read from the DB on every tick, so nothing needs rescheduling.
- Group posts (morning, night) use the owner's language. Only groups that finished /setup and have active goals get posts.

## PHP Mini App
- Load `https://telegram.org/js/telegram-web-app.js` and send `Telegram.WebApp.initData` with every API request.
- `miniapp/lib/auth.php` validates initData with HMAC-SHA256 (secret = HMAC("WebAppData", BOT_TOKEN)) and checks `auth_date` freshness. Reject everything that fails.
- Use PDO prepared statements only. Escape all output with `htmlspecialchars`.
- Pages: My Day (checklist across all goal keys from all my groups), Zikr Counter (big tap button, `HapticFeedback`, saves in batches every few taps and on close), My Groups (each group's progress), Group Settings (owner only: goals, times, privacy).
- Follow Telegram theme colors via `--tg-theme-*` CSS variables. Mobile-first.
- Goals: owners add well-known presets (`GOAL_PRESETS` in `lib/groups.php`) or custom goals (key `custom_<random>`, so they don't share entries across groups). A goal's key and type never change; goals are switched off (`active = 0`), not deleted. Only custom goals' labels are editable, since presets are shown translated by key.
- Group times: `morning_time` must be earlier than `night_time`, because the night summary covers the group's local day.
- JS: `assets/core.js` (shared helpers, `window.ZC`), `assets/settings.js`, `assets/app.js` (My Day, counter, startup), loaded in that order.

## Build phases
1. Repo structure, docker-compose, `001_init.sql`, bot /start, /setup, /join, group registration.
2. PHP Mini App: initData auth, My Day checklist, zikr counter, entries API.
3. Owner goal settings page, minute-tick scheduler, morning/night posts.
4. Streaks, privacy modes, hide_my_stats, i18n polish.
5. (Later) Prayer-time reminders, badges, Ramadan mode.

## Conventions
- Python: type hints, ruff formatting, pytest for leaderboard/streak logic.
- PHP: `declare(strict_types=1);`, small include files, no global state beyond config.
- Dates are calculated in the group's timezone (Python `zoneinfo`, PHP `DateTimeZone`). Store `entry_date` as DATE.
- A user's "today" for entries (which aren't per group) uses the timezone of the first active group they joined, else `Africa/Addis_Ababa`.
- Known goal keys are translated by key (`goal_<key>` in both bot locales and Mini App lang files); `goals.label` is the fallback.
- Write small, focused commits per feature.
