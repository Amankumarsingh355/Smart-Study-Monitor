from types import SimpleNamespace
from src.ml.recommendations import RecommendationEngine


def test_recommendation_empty_sessions():
    engine = RecommendationEngine()
    recs = engine.generate_recommendations([])
    assert len(recs) == 1
    assert recs[0]["category"] == "ROUTINE"


def test_recommendation_fatigue_pattern():
    engine = RecommendationEngine()
    # Mock sessions: short sessions have 92% focus, long sessions have 74% focus
    s1 = SimpleNamespace(duration=25*60, focus_score=94.0, phone_time=0.0, posture_issue_time=0.0)
    s2 = SimpleNamespace(duration=30*60, focus_score=90.0, phone_time=0.0, posture_issue_time=0.0)
    s3 = SimpleNamespace(duration=55*60, focus_score=72.0, phone_time=0.0, posture_issue_time=0.0)
    s4 = SimpleNamespace(duration=60*60, focus_score=76.0, phone_time=0.0, posture_issue_time=0.0)

    recs = engine.generate_recommendations([s1, s2, s3, s4])
    categories = [r["category"] for r in recs]
    assert "FATIGUE" in categories
    fatigue_rec = next(r for r in recs if r["category"] == "FATIGUE")
    assert "Pomodoro" in fatigue_rec["action"]


def test_recommendation_phone_pattern():
    engine = RecommendationEngine()
    s1 = SimpleNamespace(duration=30*60, focus_score=85.0, phone_time=180.0, posture_issue_time=0.0)
    recs = engine.generate_recommendations([s1])
    categories = [r["category"] for r in recs]
    assert "DISTRACTION" in categories
