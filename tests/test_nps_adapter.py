from src.adapters.nps_adapter import load_raw_zion_response, naive_parse, safe_parse


def test_naive_parser_drops_records_with_nested_geometry():
    raw = load_raw_zion_response()
    result = naive_parse(raw)
    assert len(result) < len(raw["data"]), "naive parser should silently drop malformed records"


def test_safe_parser_keeps_every_record():
    raw = load_raw_zion_response()
    result = safe_parse(raw)
    assert len(result) == len(raw["data"]), "safe parser must never drop a record"


def test_safe_parser_flags_invalid_geometry_instead_of_dropping():
    raw = load_raw_zion_response()
    result = safe_parse(raw)
    flagged = [r for r in result if not r["has_valid_geometry"]]
    assert len(flagged) == 3
    assert {r["name"] for r in flagged} == {"Watchman Trail", "Canyon Overlook", "Riverside Walk"}
