# 🛡️ CyberBuddy: your daily cybersecurity study bot

CyberBuddy splits the [OWASP PCCOE Cybersecurity Roadmap](https://github.com/owasppccoe/cybersecurity-roadmap/blob/main/ROADMAP.md)
into a **182-day plan** (about 6 months at 1.5–2 hours a day). It then:

- ☀️ **sends you each morning's lesson on Telegram**: tasks, links, tools and a challenge
- 🌙 **checks in each evening**: it nudges you if the day isn't done, or gives you a bonus puzzle if it is
- 🧩 **has 34 bonus puzzles** (encoding, crypto, networking, web, Linux, Windows) with answers checked by hash, so the answers aren't stored in the repo
- 🔥 **tracks your streak and progress** for each roadmap phase
- 🌐 **comes with a web dashboard** (`/cyber/`) that shows the same plan and your bot progress

You only move forward when you send `/done`. If you miss a day, the bot repeats that lesson instead of skipping ahead.

| File | What it is |
|---|---|
| [`PLAN.md`](PLAN.md) | The full day-by-day plan, readable on GitHub |
| `build_curriculum.py` | **Edit this** to change the plan, then run `python3 cyberbot/build_curriculum.py` |
| `curriculum.json` | Generated plan, read by the bot and the dashboard |
| `challenges.json` | Bonus puzzles (answers stored as SHA-256 hashes) |
| `bot.py` | The Telegram bot (Python standard library only, nothing to install) |
| `state.json` | Your progress. GitHub Actions commits it after each run |
| `../.github/workflows/cyberbot.yml` | The daily schedule |
| `../cyber/` | The web dashboard |

## Setup (about 10 minutes)

### 1. Create your Telegram bot
1. In Telegram, open **@BotFather** and send `/newbot`. Pick a name and you'll get a **token** like `123456:ABC...`.
2. Open your new bot and send it `/start`.
3. To find your **chat id**, open `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser and copy `"chat":{"id": 123456789}`.

### 2. Add the secrets to GitHub
Go to the repo → **Settings → Secrets and variables → Actions**:
- **Secrets**: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- **Variables** (optional): `BOT_TZ` (default `Asia/Kolkata`), and `DASHBOARD_URL` (e.g. `https://hafizz2.github.io/todolist2/cyber/`)

### 3. Turn it on
- Scheduled workflows only run from the **default branch**, so merge this branch into `main`.
- Go to **Actions → CyberBuddy → Run workflow → morning** to get your first lesson right away.
- To use the dashboard, enable **Settings → Pages** (deploy from `main`, root). It will be at `/cyber/`.

### Schedule
The times are in `.github/workflows/cyberbot.yml`, in UTC and set for India:

| Run | UTC | IST |
|---|---|---|
| Morning lesson | 02:21 | 07:51 |
| Evening check-in | 14:21 | 19:51 |
| Reply to your commands | :47 each hour, 03–18 | 08:17 – 23:47 |

On GitHub Actions the bot replies to commands **within about an hour**, and GitHub may delay scheduled runs by a few minutes. For instant replies, use poll mode instead (see below).

## Commands

| Command | What it does |
|---|---|
| `/today` | Today's lesson |
| `/done` | Mark today's lesson complete and move to the next day |
| `/skip`, `/back` | Move forward or back one day |
| `/day N` | Preview day N |
| `/goto N` | Jump to day N |
| `/plan` | The next 7 days |
| `/progress` | Stats, streak and progress for each phase |
| `/challenge`, `/hint`, `/answer X` | Bonus puzzles |

## Instant replies: poll mode (optional)

Run the bot on any always-on machine: a laptop, a Raspberry Pi, or Android with Termux:

```bash
export TELEGRAM_BOT_TOKEN=...   TELEGRAM_CHAT_ID=...
python3 cyberbot/bot.py poll
```

Poll mode replies instantly and sends the morning and evening messages itself (`MORNING_HOUR` and `EVENING_HOUR` env vars, default 8 and 20).
Progress is saved in the local `state.json`. **Use either poll mode or GitHub Actions, not both**, because each one keeps its own progress. If you choose poll mode, disable the workflow.

## Try it without Telegram

```bash
python3 cyberbot/bot.py preview 12   # print day 12
python3 cyberbot/bot.py morning      # with no token, messages are printed instead of sent
```

## Adding bonus puzzles

Each puzzle in `challenges.json` stores `sha256(answer)`, where the answer is lowercased with spaces collapsed:

```bash
python3 -c "import hashlib;print(hashlib.sha256('your answer'.encode()).hexdigest())"
```

> ⚖️ Ethics reminder from the roadmap: only test systems you own or have written permission to test.
> Every lab in this plan uses your own VMs or legal practice platforms.
