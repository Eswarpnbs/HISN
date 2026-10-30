from app.core.stats import wilson, with_ci

def test_wilson_small_samples():
    lo, hi = wilson(4, 4)
    assert 0.50 < lo < 0.52 and hi == 1.0
    assert with_ci("13/14") == "13/14 (69-99%)"
    assert with_ci("7/14") == "7/14 (27-73%)"

def test_non_fraction_unchanged():
    assert with_ci("-") == "-" and with_ci("0") == "0"
