from rankingbot import Wiki


def test_has_header(tmp_path):
    headers = ["timestamp", "userid", "type", "title", "ns"]
    current = tmp_path / "current"
    current.write_text("timestamp,userid,type,title,ns\n", encoding="utf-8")
    old = tmp_path / "old"
    old.write_text("timestamp,userid,type,title\n", encoding="utf-8")
    empty = tmp_path / "empty"
    empty.write_text("", encoding="utf-8")

    assert Wiki._has_header(current, headers)
    assert not Wiki._has_header(old, headers)
    assert not Wiki._has_header(empty, headers)
    assert not Wiki._has_header(tmp_path / "missing", headers)
