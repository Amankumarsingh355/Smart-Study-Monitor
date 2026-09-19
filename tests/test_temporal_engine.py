import pytest
from src.behavior.temporal_engine import TemporalEngine


def test_temporal_engine_update_and_duration():
    engine = TemporalEngine()
    base_t = 100.0

    # Signal active at t=100.0
    engine.update("phone", active=True, current_time=base_t)
    assert "phone" in engine.active_since
    assert engine.duration("phone", current_time=base_t) == 0.0

    # Check duration at t=101.5
    assert engine.duration("phone", current_time=base_t + 1.5) == pytest.approx(1.5)
    assert engine.active_for("phone", 1.0, current_time=base_t + 1.5)
    assert not engine.active_for("phone", 2.0, current_time=base_t + 1.5)

    # Signal inactive -> removed
    engine.update("phone", active=False, current_time=base_t + 2.0)
    assert "phone" not in engine.active_since
    assert engine.duration("phone", current_time=base_t + 2.5) == 0.0
    assert not engine.active_for("phone", 1.0, current_time=base_t + 2.5)


def test_temporal_engine_reset():
    engine = TemporalEngine()
    engine.update("eyes_closed", active=True, current_time=100.0)
    engine.update("phone", active=True, current_time=100.0)
    assert len(engine.active_since) == 2

    engine.reset()
    assert len(engine.active_since) == 0
    assert engine.duration("eyes_closed") == 0.0
