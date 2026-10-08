# Zikr Circle

A Telegram bot + Mini App for daily group worship challenges. See [CLAUDE.md](CLAUDE.md) for the full design.

- `bot/` — Python (aiogram 3) bot: commands, group registration, scheduled posts.
- `miniapp/` — plain PHP 8 Mini App + JSON API (shared-hosting friendly).
- `db/` — numbered MySQL migrations, the single source of truth for the schema.

## Local development

```sh
docker compose up -d            # MySQL on :3306 (runs db/*.sql on first start), PHP on :8080

cd bot
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # set BOT_TOKEN (from @BotFather) and MINIAPP_URL
python -m zikr_bot              # long polling
```

For the Mini App: `cp miniapp/config.example.php miniapp/config.php` and fill it in. Telegram only
opens Mini Apps over HTTPS, so expose `:8080` through a tunnel (e.g. ngrok/cloudflared) and use that
URL as `MINIAPP_URL`.

New migrations only run automatically on a fresh volume; apply them by hand otherwise
(`docker compose exec -T db mysql -uzikr -pzikr zikr_circle < db/002_....sql`), or reset with
`docker compose down -v`.

## Tests

```sh
cd bot
ruff format --check . && ruff check .
pytest                                                          # unit tests
TEST_DB_HOST=127.0.0.1 TEST_DB_USER=root TEST_DB_PASS=root pytest  # + end-to-end flows against MySQL
```

The legacy HTML/CSS/JS to-do list files at the repo root (`index.html`, `script.js`, `style.css`,
`images/`) are from the original project and are not part of Zikr Circle.
