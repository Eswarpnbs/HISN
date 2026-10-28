from app.network.act1 import network_inject

def test_inject_is_reproducible_and_rain_exceeds_heat():
    a, ta = network_inject("rainy", days=3); b, tb = network_inject("rainy", days=3)
    assert a == b and ta == tb
    _, th = network_inject("hot", days=3)
    assert ta > th
    assert a["events"][-1]["audience"] == ["tdra"]
