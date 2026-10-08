from zikr_bot.summary import (
    GoalInfo,
    MemberInfo,
    leaderboard,
    member_progress,
    morning_text,
    night_text,
    today_text,
)

GOALS = [
    GoalInfo("salat_fajr", "Fajr", "checkbox", 1),
    GoalInfo("istighfar", "Istighfar", "counter", 100),
    GoalInfo("custom_1", "Visit <family>", "checkbox", 1),
]
AMINA = MemberInfo(1, "Amina", False)
BILAL = MemberInfo(2, "Bilal", False)
HIDDEN = MemberInfo(3, "Secret Sam", True)
IDLE = MemberInfo(4, "Idle Ibrahim", False)
MEMBERS = [AMINA, BILAL, HIDDEN, IDLE]
ENTRIES = {
    (1, "salat_fajr"): 1,
    (1, "istighfar"): 40,  # not reached
    (2, "salat_fajr"): 1,
    (2, "istighfar"): 350,
    (2, "custom_1"): 1,
    (3, "istighfar"): 1000,
}


def test_progress_counts_targets_reached():
    p = member_progress(GOALS, AMINA, ENTRIES)
    assert (p.done, p.total) == (1, 3)


def test_leaderboard_ranks_by_completion_not_counts_and_skips_idle_members():
    names = [p.member.name for p in leaderboard(GOALS, MEMBERS, ENTRIES)]
    # Secret Sam has the biggest istighfar count but only 1 goal done.
    assert names == ["Bilal", "Amina", "Secret Sam"]


def test_completion_mode_hides_counts_and_hidden_names():
    text = night_text("en", "Circle", "completion", GOALS, MEMBERS, ENTRIES)
    assert "Bilal — 3/3 ✅" in text
    assert "Amina — 1/3" in text
    assert "A member — 1/3" in text
    assert "Secret Sam" not in text
    assert "Idle" not in text
    assert "350" not in text and "1000" not in text and "1,000" not in text
    assert "3 of 4 members" in text


def test_group_total_only_shows_no_individuals():
    text = night_text("en", "Circle", "group_total_only", GOALS, MEMBERS, ENTRIES)
    for name in ("Amina", "Bilal", "Sam", "A member"):
        assert name not in text
    assert "Fajr prayer: 2 completed" in text
    assert "Istighfar: 2 completed · 1,390 together" in text


def test_full_counts_shows_amounts():
    text = night_text("en", "Circle", "full_counts", GOALS, MEMBERS, ENTRIES)
    assert "Istighfar 350" in text
    assert "Istighfar 1,000" in text
    assert "Secret Sam" not in text


def test_nobody_logged():
    text = night_text("en", "Circle", "completion", GOALS, MEMBERS, {})
    assert "No progress logged today" in text


def test_known_keys_are_translated_and_custom_labels_escaped():
    text = morning_text("am", "<Circle>", GOALS)
    assert "የፈጅር ሶላት" in text
    assert "ኢስቲግፋር × 100" in text
    assert "Visit &lt;family&gt;" in text
    assert "&lt;Circle&gt;" in text


def test_today_shows_marks_not_counts():
    p = member_progress(GOALS, AMINA, ENTRIES)
    text = today_text("en", "Amina", GOALS, p)
    assert "Amina, today: 1/3" in text
    assert "✅ Fajr prayer" in text
    assert "▫️ Istighfar" in text
    assert "40" not in text
