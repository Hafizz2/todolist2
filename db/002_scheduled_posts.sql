-- 002_scheduled_posts.sql — remembers which scheduled posts were sent, so the bot's minute tick
-- posts each one exactly once per local day, even across restarts or with missed ticks.

CREATE TABLE group_posts (
    group_id   BIGINT UNSIGNED NOT NULL,
    kind       ENUM('morning','night') NOT NULL,
    post_date  DATE            NOT NULL,          -- the group's local date
    sent_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, kind, post_date),
    CONSTRAINT fk_group_posts_group FOREIGN KEY (group_id) REFERENCES `groups` (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
