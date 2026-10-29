from app.core.gateway import PolicyGateway
from app.windtunnel.engine import _overlay_condition

def test_max_condition_bounds_emergency_age():
    cond = {"emergency_minutes_max": 4320}
    assert PolicyGateway._matches(None, cond, {"emergency_minutes": 100})
    assert not PolicyGateway._matches(None, cond, {"emergency_minutes": 5000})
    assert not PolicyGateway._matches(None, cond, {})

def test_no_stated_limit_means_no_expiry_in_rule():
    assert _overlay_condition({"params": {"hours": 72}})["emergency_minutes_max"] == 4320
    assert "emergency_minutes_max" not in _overlay_condition({"params": {"hours": None}})