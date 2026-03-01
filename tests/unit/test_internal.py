from eye_witness.internal import clamp_rate, safe_json_dumps, stable_keys


def test_clamp_rate_bounds():
    assert clamp_rate(-1.0) == 0.0
    assert clamp_rate(2.0) == 1.0
    assert clamp_rate(0.5) == 0.5


def test_safe_json_dumps():
    out = safe_json_dumps({"b": 2, "a": 1})
    assert out.startswith("{")
    assert '"a": 1' in out


def test_stable_keys():
    assert stable_keys({"b": 1, "a": 2}) == ["a", "b"]
