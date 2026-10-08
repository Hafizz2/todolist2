from zikr_bot.keyboards import group_start_param, miniapp_link


def test_miniapp_link():
    assert miniapp_link("zikr_bot", "app") == "https://t.me/zikr_bot/app"
    assert (
        miniapp_link("zikr_bot", "app", "group_7") == "https://t.me/zikr_bot/app?startapp=group_7"
    )


def test_group_start_param_matches_miniapp_contract():
    # miniapp/lib/auth.php parses this exact shape (see group_id_from_start_param()).
    assert group_start_param(42) == "group_42"
