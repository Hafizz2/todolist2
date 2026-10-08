"""Morning challenge, nightly summary and /today texts. Pure functions (pytest-covered).

Privacy (see CLAUDE.md): by default only completion ("5/8 ✅") is shown, never raw worship counts;
members with hide_my_stats appear as "a member"; members who logged nothing aren't listed.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

from .i18n import has_key, t


@dataclass(frozen=True)
class GoalInfo:
    key: str
    label: str
    type: str  # counter | checkbox | quantity
    target: int


@dataclass(frozen=True)
class MemberInfo:
    user_id: int
    name: str
    hide_stats: bool


# (user_id, goal_key) -> amount for one date
Entries = dict[tuple[int, str], int]


@dataclass(frozen=True)
class Progress:
    member: MemberInfo
    done: int
    total: int
    amounts: dict[str, int]

    @property
    def logged(self) -> bool:
        return any(self.amounts.values())


def goal_label(lang: str, goal: GoalInfo) -> str:
    key = f"goal_{goal.key}"
    return t(lang, key) if has_key(lang, key) else goal.label


def member_progress(goals: list[GoalInfo], member: MemberInfo, entries: Entries) -> Progress:
    amounts = {g.key: entries.get((member.user_id, g.key), 0) for g in goals}
    done = sum(1 for g in goals if amounts[g.key] >= g.target)
    return Progress(member=member, done=done, total=len(goals), amounts=amounts)


def leaderboard(
    goals: list[GoalInfo], members: list[MemberInfo], entries: Entries
) -> list[Progress]:
    """Members who logged anything today, most goals completed first. Never ranked by counts."""
    rows = [member_progress(goals, m, entries) for m in members]
    rows = [p for p in rows if p.logged]
    rows.sort(key=lambda p: (-p.done, p.member.hide_stats, p.member.name.casefold()))
    return rows


def _display_name(lang: str, member: MemberInfo) -> str:
    return t(lang, "a_member") if member.hide_stats else escape(member.name)


def _completion(p: Progress) -> str:
    return f"{p.done}/{p.total} ✅" if p.done == p.total else f"{p.done}/{p.total}"


def _amount(goal: GoalInfo, amount: int) -> str:
    return "✓" if goal.type == "checkbox" else f"{amount:,}"


def morning_text(lang: str, title: str, goals: list[GoalInfo]) -> str:
    lines = [t(lang, "morning_header", title=escape(title)), ""]
    for g in goals:
        label = escape(goal_label(lang, g))
        lines.append(f"• {label}" if g.type == "checkbox" else f"• {label} × {g.target}")
    lines += ["", t(lang, "morning_footer")]
    return "\n".join(lines)


def night_text(
    lang: str,
    title: str,
    privacy_mode: str,
    goals: list[GoalInfo],
    members: list[MemberInfo],
    entries: Entries,
) -> str:
    rows = leaderboard(goals, members, entries)
    header = t(lang, "night_header", title=escape(title))
    if not rows:
        return f"{header}\n\n{t(lang, 'night_nobody')}"

    lines = [header, t(lang, "night_participation", active=len(rows), total=len(members)), ""]
    if privacy_mode == "group_total_only":
        for g in goals:
            completed = sum(1 for p in rows if p.amounts[g.key] >= g.target)
            line = t(lang, "night_goal_total", label=escape(goal_label(lang, g)), done=completed)
            if g.type != "checkbox":
                together = sum(p.amounts[g.key] for p in rows)
                line += " · " + t(lang, "night_together", amount=f"{together:,}")
            lines.append(line)
    else:
        for p in rows:
            lines.append(f"{_display_name(lang, p.member)} — {_completion(p)}")
            if privacy_mode == "full_counts":
                parts = [
                    f"{escape(goal_label(lang, g))} {_amount(g, p.amounts[g.key])}"
                    for g in goals
                    if p.amounts[g.key]
                ]
                lines.append(f"    <i>{' · '.join(parts)}</i>")
    lines += ["", t(lang, "night_footer")]
    return "\n".join(lines)


def today_text(lang: str, name: str, goals: list[GoalInfo], progress: Progress) -> str:
    """A member's own progress, posted in the group: completion marks only, no counts."""
    lines = [t(lang, "today_header", name=escape(name), progress=_completion(progress)), ""]
    for g in goals:
        mark = "✅" if progress.amounts[g.key] >= g.target else "▫️"
        lines.append(f"{mark} {escape(goal_label(lang, g))}")
    return "\n".join(lines)
