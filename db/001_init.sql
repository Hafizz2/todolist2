-- 001_init.sql — initial Zikr Circle schema (MySQL 8, utf8mb4).
-- Single source of truth for the schema shared by bot/ (Python) and miniapp/ (PHP).
-- Note: `groups` is a reserved word in MySQL 8 and must always be backticked.

SET NAMES utf8mb4;

CREATE TABLE users (
    id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    telegram_id  BIGINT          NOT NULL,
    name         VARCHAR(255)    NOT NULL DEFAULT '',
    lang         VARCHAR(8)      NOT NULL DEFAULT 'am',
    created_at   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_telegram_id (telegram_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `groups` (
    id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    chat_id       BIGINT          NOT NULL,          -- Telegram chat ids for groups are negative
    title         VARCHAR(255)    NOT NULL DEFAULT '',
    owner_id      BIGINT UNSIGNED NULL,              -- NULL until someone runs /setup
    timezone      VARCHAR(64)     NOT NULL DEFAULT 'Africa/Addis_Ababa',
    morning_time  TIME            NOT NULL DEFAULT '06:00:00',
    night_time    TIME            NOT NULL DEFAULT '21:00:00',
    privacy_mode  ENUM('completion','group_total_only','full_counts') NOT NULL DEFAULT 'completion',
    active        BOOLEAN         NOT NULL DEFAULT 1, -- 0 once the bot is removed from the chat
    created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_groups_chat_id (chat_id),
    KEY ix_groups_owner (owner_id),
    CONSTRAINT fk_groups_owner FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE group_members (
    group_id       BIGINT UNSIGNED NOT NULL,
    user_id        BIGINT UNSIGNED NOT NULL,
    joined_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hide_my_stats  BOOLEAN         NOT NULL DEFAULT 0,
    PRIMARY KEY (group_id, user_id),
    KEY ix_group_members_user (user_id),
    CONSTRAINT fk_group_members_group FOREIGN KEY (group_id) REFERENCES `groups` (id) ON DELETE CASCADE,
    CONSTRAINT fk_group_members_user  FOREIGN KEY (user_id)  REFERENCES users (id)    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE goals (
    id        BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    group_id  BIGINT UNSIGNED NOT NULL,
    goal_key  VARCHAR(64)     NOT NULL,              -- e.g. istighfar, salat_fajr, quran_pages
    label     VARCHAR(255)    NOT NULL,
    type      ENUM('counter','checkbox','quantity') NOT NULL,
    target    INT UNSIGNED    NOT NULL DEFAULT 1,
    active    BOOLEAN         NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_goals_group_key (group_id, goal_key),
    KEY ix_goals_key (goal_key),
    CONSTRAINT fk_goals_group FOREIGN KEY (group_id) REFERENCES `groups` (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Log once, applies everywhere: entries are per user + goal_key + date, not per group.
CREATE TABLE entries (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id     BIGINT UNSIGNED NOT NULL,
    goal_key    VARCHAR(64)     NOT NULL,
    entry_date  DATE            NOT NULL,
    amount      INT UNSIGNED    NOT NULL DEFAULT 0,
    updated_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_entries_user_key_date (user_id, goal_key, entry_date),
    KEY ix_entries_date_key (entry_date, goal_key),
    CONSTRAINT fk_entries_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
