"""Starter goals a group gets on its first /setup; the owner edits them in the Mini App."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DefaultGoal:
    key: str
    type: str  # counter | checkbox | quantity
    target: int


DEFAULT_GOALS: tuple[DefaultGoal, ...] = (
    DefaultGoal("salat_fajr", "checkbox", 1),
    DefaultGoal("salat_dhuhr", "checkbox", 1),
    DefaultGoal("salat_asr", "checkbox", 1),
    DefaultGoal("salat_maghrib", "checkbox", 1),
    DefaultGoal("salat_isha", "checkbox", 1),
    DefaultGoal("istighfar", "counter", 100),
    DefaultGoal("salawat", "counter", 100),
    DefaultGoal("quran_pages", "quantity", 2),
)
