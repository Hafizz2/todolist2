from zikr_bot.keyboards import parse_setup_payload, setup_payload, with_query


def test_setup_payload_round_trip():
    assert parse_setup_payload(setup_payload(42)) == 42


def test_parse_setup_payload_rejects_other_payloads():
    for payload in (None, "", "setup_", "setup_-1", "setup_abc", "hello"):
        assert parse_setup_payload(payload) is None


def test_with_query_appends_params():
    assert with_query("https://x.test/app/", group=5) == "https://x.test/app/?group=5"
    assert with_query("https://x.test/app/?v=2", group=5) == "https://x.test/app/?v=2&group=5"
