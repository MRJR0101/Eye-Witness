from eye_witness import __all__ as top_all
from eye_witness.v1 import __all__ as v1_all


def test_top_level_and_v1_api_parity():
    top = set(top_all) - {"init_observability", "get_structured_logger"}
    v1 = set(v1_all)
    assert top == v1
