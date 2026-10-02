#!/usr/bin/env python3
"""CyberBuddy - a Telegram study buddy for the OWASP cybersecurity roadmap.

Modes:
  python3 cyberbot/bot.py morning     process commands, then send today's lesson
  python3 cyberbot/bot.py evening     process commands, then nudge if today isn't done
  python3 cyberbot/bot.py sync        only process commands (/done, /challenge, ...)
  python3 cyberbot/bot.py poll        run forever and reply instantly (laptop / Raspberry Pi / Termux)
  python3 cyberbot/bot.py preview N   print day N in the terminal (no Telegram needed)

Environment:
  TELEGRAM_BOT_TOKEN   token from @BotFather (without it, messages are printed instead of sent)
  TELEGRAM_CHAT_ID     your chat id; the bot ignores everyone else
  BOT_TZ               your time zone, default Asia/Kolkata
  STATE_FILE           where progress is stored, default cyberbot/state.json
"""

import hashlib
import html
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
CURRICULUM = json.loads((HERE / "curriculum.json").read_text())
DAYS = CURRICULUM["days"]
CHALLENGES = json.loads((HERE / "challenges.json").read_text())["challenges"]
TOTAL = len(DAYS)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
TZ = ZoneInfo(os.environ.get("BOT_TZ", "Asia/Kolkata"))
STATE_FILE = Path(os.environ.get("STATE_FILE", HERE / "state.json"))
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "").strip()
MORNING_HOUR = int(os.environ.get("MORNING_HOUR", "8"))   # used by poll mode only
EVENING_HOUR = int(os.environ.get("EVENING_HOUR", "20"))

DEFAULT_STATE = {
    "chat_id": None,
    "current_day": 1,
    "completed": {},
    "skipped": [],
    "last_done_date": None,
    "streak": 0,
    "best_streak": 0,
    "update_offset": 0,
    "pending_challenge": None,
    "solved": [],
    "last_morning": None,
    "last_evening": None,
}

HELP = """<b>CyberBuddy commands</b>
/today - today's lesson
/done - mark today's lesson complete
/skip - skip to the next day
/back - go back one day
/day N - look at day N (doesn't change progress)
/goto N - jump to day N
/plan - the next 7 days
/progress - your stats
/challenge - a random bonus puzzle
/hint - hint for the current puzzle
/answer X - answer the current puzzle
/help - this message

I send your lesson every morning and check in every evening."""


# ------------------------------------------------------------------ state

def load_state():
    state = dict(DEFAULT_STATE)
    if STATE_FILE.exists():
        state.update(json.loads(STATE_FILE.read_text()))
    return state


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")


def today():
    return datetime.now(TZ).date()


# --------------------------------------------------------------- telegram

def api(method, **params):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=70) as resp:
        body = json.loads(resp.read())
    if not body.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {body}")
    return body["result"]


def send(chat_id, text):
    if not TOKEN:
        print("----- (dry run, no TELEGRAM_BOT_TOKEN) -----")
        print(re.sub(r"<[^>]+>", "", html.unescape(text)))
        return
    api("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML", disable_web_page_preview="true")


def get_updates(offset, timeout=0):
    if not TOKEN:
        return []
    return api("getUpdates", offset=offset, timeout=timeout, allowed_updates='["message"]')


# ------------------------------------------------------------- formatting

def fmt(text):
    """Escape for Telegram HTML and turn `code` into <code>code</code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(text, quote=False))


def lesson_text(n, header=""):
    d = DAYS[n - 1]
    lines = []
    if header:
        lines += [header, ""]
    lines += [f"🛡️ <b>Day {n}/{TOTAL}</b> · {html.escape(d['phase_name'])}",
              f"<b>{fmt(d['title'])}</b>", "", "📋 <b>Tasks</b>"]
    lines += [f"{i}. {fmt(t)}" for i, t in enumerate(d["tasks"], 1)]
    if d["links"]:
        lines += ["", "🔗 <b>Links</b>"]
        lines += [f'• <a href="{html.escape(l["url"])}">{html.escape(l["name"])}</a>' for l in d["links"]]
    if d["tools"]:
        lines += ["", "🧰 <b>Tools:</b> " + ", ".join(fmt(t) for t in d["tools"])]
    if d["challenge"]:
        lines += ["", "🎯 <b>Challenge</b>", fmt(d["challenge"])]
    lines += ["", "Reply /done when finished · /challenge for a bonus puzzle"]
    return "\n".join(lines)


def bar(done, total, width=12):
    filled = round(width * done / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def progress_text(state):
    done = len(state["completed"])
    lines = [f"📊 <b>Progress</b>",
             f"{bar(done, TOTAL)} {done}/{TOTAL} days ({100 * done // TOTAL}%)",
             f"📍 Current: Day {state['current_day']} - {fmt(DAYS[state['current_day'] - 1]['title'])}",
             f"🔥 Streak: {state['streak']} (best {state['best_streak']})",
             f"🧩 Bonus puzzles solved: {len(state['solved'])}/{len(CHALLENGES)}", "", "<b>Phases</b>"]
    for key, name in CURRICULUM["phases"].items():
        days = [d["day"] for d in DAYS if d["phase"] == key]
        n = sum(1 for d in days if str(d) in state["completed"])
        mark = "✅" if n == len(days) else "▫️"
        lines.append(f"{mark} {html.escape(name.split(' - ')[1])}: {n}/{len(days)}")
    if DASHBOARD_URL:
        lines += ["", f'<a href="{html.escape(DASHBOARD_URL)}">Open dashboard</a>']
    return "\n".join(lines)


def plan_text(state):
    start = state["current_day"]
    lines = ["🗓️ <b>Next 7 days</b>"]
    for n in range(start, min(start + 7, TOTAL + 1)):
        lines.append(f"Day {n}: {fmt(DAYS[n - 1]['title'])}")
    return "\n".join(lines)


def challenge_text(c):
    stars = "⭐" * c["difficulty"]
    text = f"🧩 <b>Bonus puzzle #{c['id']}</b> · {html.escape(c['category'])} {stars}\n\n{fmt(c['prompt'])}"
    if c["tool"]:
        text += f"\n\n🧰 Try: {fmt(c['tool'])}"
    return text + "\n\nReply <code>/answer your-answer</code> · /hint"


# ---------------------------------------------------------------- actions

def normalize(answer):
    return " ".join(answer.strip().lower().split())


def check_answer(c, answer):
    return hashlib.sha256(normalize(answer).encode()).hexdigest() in c["answers"]


def pick_challenge(state):
    unsolved = [c for c in CHALLENGES if c["id"] not in state["solved"]]
    return random.choice(unsolved or CHALLENGES)


def mark_done(state):
    n = state["current_day"]
    d = today()
    state["completed"][str(n)] = d.isoformat()
    last = state["last_done_date"]
    if last != d.isoformat():
        yesterday = (d - timedelta(days=1)).isoformat()
        state["streak"] = state["streak"] + 1 if last == yesterday else 1
        state["last_done_date"] = d.isoformat()
    state["best_streak"] = max(state["best_streak"], state["streak"])
    if n >= TOTAL:
        return ("🎓 <b>You finished the whole roadmap!</b> Incredible work.\n"
                "Keep going with /challenge and your specialization plan.")
    state["current_day"] = n + 1
    return (f"✅ Day {n} complete! 🔥 Streak: {state['streak']}\n\n"
            f"Next up: <b>{fmt(DAYS[n]['title'])}</b>\n"
            "Send /today to start it now, or I'll send it tomorrow morning.")


def handle(state, text):
    """Handle one command and return the reply text."""
    parts = text.strip().split(maxsplit=1)
    cmd = parts[0].split("@")[0].lower() if parts else ""
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/start", "/help"):
        return HELP
    if cmd == "/today":
        return lesson_text(state["current_day"])
    if cmd == "/done":
        return mark_done(state)
    if cmd == "/skip":
        n = state["current_day"]
        if n >= TOTAL:
            return "This is the last day already."
        state["skipped"] = sorted(set(state["skipped"]) | {n})
        state["current_day"] = n + 1
        return lesson_text(n + 1, f"⏭️ Skipped day {n}. You can come back with /goto {n}.")
    if cmd == "/back":
        state["current_day"] = max(1, state["current_day"] - 1)
        return lesson_text(state["current_day"], "⏮️ Went back one day.")
    if cmd in ("/day", "/goto"):
        if not arg.isdigit() or not 1 <= int(arg) <= TOTAL:
            return f"Usage: {cmd} N (1-{TOTAL})"
        n = int(arg)
        if cmd == "/goto":
            state["current_day"] = n
            return lesson_text(n, f"📍 Jumped to day {n}.")
        return lesson_text(n, "👀 Preview only - your progress didn't change.")
    if cmd == "/plan":
        return plan_text(state)
    if cmd in ("/progress", "/stats"):
        return progress_text(state)
    if cmd == "/challenge":
        c = pick_challenge(state)
        state["pending_challenge"] = c["id"]
        return challenge_text(c)
    if cmd in ("/hint", "/answer"):
        cid = state["pending_challenge"]
        if not cid:
            return "No puzzle open. Send /challenge first."
        c = next(c for c in CHALLENGES if c["id"] == cid)
        if cmd == "/hint":
            return f"💡 {fmt(c['hint'])}"
        if not arg:
            return "Usage: <code>/answer your-answer</code>"
        if check_answer(c, arg):
            state["solved"] = sorted(set(state["solved"]) | {cid})
            state["pending_challenge"] = None
            return f"🎉 Correct! Puzzles solved: {len(state['solved'])}/{len(CHALLENGES)}. Another? /challenge"
        return "❌ Not quite. Try again, or /hint"
    return "I didn't get that. Send /help for commands."


def process_updates(state, timeout=0):
    """Fetch new Telegram messages and reply to commands from the owner."""
    owner = CHAT_ID or state["chat_id"]
    for upd in get_updates(state["update_offset"], timeout):
        state["update_offset"] = upd["update_id"] + 1
        msg = upd.get("message") or {}
        text = msg.get("text", "")
        chat = str(msg.get("chat", {}).get("id", ""))
        if not chat or not text:
            continue
        if not owner:
            # First person to message the bot (poll mode without TELEGRAM_CHAT_ID) becomes the owner.
            owner = state["chat_id"] = chat
            print(f"Registered chat id {chat}. Set TELEGRAM_CHAT_ID={chat} to lock the bot to you.")
        if chat != str(owner):
            send(chat, "This is a private study bot. Fork the repo to make your own!")
            continue
        send(chat, handle(state, text))
    save_state(state)


def morning(state):
    chat = CHAT_ID or state["chat_id"]
    n = state["current_day"]
    yesterday = (today() - timedelta(days=1)).isoformat()
    header = f"☀️ Good morning! 🔥 Streak: {state['streak']}"
    if state["last_done_date"] not in (today().isoformat(), yesterday) and state["completed"]:
        header = "☀️ Good morning! Let's get back on track - one lesson today restarts your streak."
    send(chat, lesson_text(n, header))


def evening(state):
    chat = CHAT_ID or state["chat_id"]
    n = state["current_day"]
    if state["last_done_date"] == today().isoformat():
        c = pick_challenge(state)
        state["pending_challenge"] = c["id"]
        send(chat, f"🌙 Great work today! 🔥 Streak: {state['streak']}\n\nFeeling sharp? Here's a bonus:\n\n"
                   + challenge_text(c))
    else:
        d = DAYS[n - 1]
        send(chat, f"🌙 Reminder: Day {n} - <b>{fmt(d['title'])}</b> isn't done yet.\n\n"
                   f"🎯 {fmt(d['challenge'])}\n\n"
                   "Even 20 minutes counts. Reply /done when finished, or /today to see the full lesson.")


def scheduled(state):
    """Send morning/evening messages once a day each (poll mode's built-in scheduler)."""
    now, d = datetime.now(TZ), today().isoformat()
    if not (CHAT_ID or state["chat_id"]):
        return
    if now.hour >= MORNING_HOUR and state["last_morning"] != d:
        state["last_morning"] = d
        if now.hour >= EVENING_HOUR:  # started late: don't send both at once
            state["last_evening"] = d
        morning(state)
    if now.hour >= EVENING_HOUR and state["last_evening"] != d:
        state["last_evening"] = d
        evening(state)
    save_state(state)


def main(argv):
    mode = argv[1] if len(argv) > 1 else "help"
    if mode == "preview":
        n = int(argv[2]) if len(argv) > 2 else 1
        print(re.sub(r"<[^>]+>", "", html.unescape(lesson_text(n))))
        return
    if mode not in ("morning", "evening", "sync", "poll"):
        print(__doc__)
        return

    state = load_state()
    if TOKEN and not (CHAT_ID or state["chat_id"]) and mode != "poll":
        sys.exit("Set TELEGRAM_CHAT_ID (send /start to your bot, then see README for how to find it).")

    if mode == "poll":
        print("CyberBuddy is listening. Ctrl+C to stop.")
        while True:
            try:
                process_updates(state, timeout=50)
                scheduled(state)
            except KeyboardInterrupt:
                return
            except Exception as exc:  # network hiccups shouldn't kill the bot
                print("error:", exc)
                time.sleep(5)

    process_updates(state)
    if mode == "morning":
        state["last_morning"] = today().isoformat()
        morning(state)
    elif mode == "evening":
        state["last_evening"] = today().isoformat()
        evening(state)
    save_state(state)


if __name__ == "__main__":
    main(sys.argv)
