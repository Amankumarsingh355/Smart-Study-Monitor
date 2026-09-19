"""
Recommendation & Study Pattern Intelligence Engine for Phase 12.
Analyzes longitudinal study sessions and event episodes to uncover behavioral trends
and generate personalized, actionable recommendations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np


class Recommendation:
    def __init__(
        self,
        rec_id: str,
        category: str,
        title: str,
        insight: str,
        action: str,
        confidence: float = 0.85,
        evidence: Optional[Dict[str, Any]] = None
    ):
        self.rec_id = rec_id
        self.category = category
        self.title = title
        self.insight = insight
        self.action = action
        self.confidence = confidence
        self.evidence = evidence or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.rec_id,
            "category": self.category,
            "title": self.title,
            "insight": self.insight,
            "action": self.action,
            "confidence": round(self.confidence, 2),
            "evidence": self.evidence
        }


class RecommendationEngine:
    """
    Analyzes historical study patterns and generates personalized insights.
    """

    def generate_recommendations(
        self,
        sessions: List[Any],
        events: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate list of personalized recommendations from historical sessions.
        """
        recommendations: List[Recommendation] = []

        if not sessions:
            return [{
                "id": "REC-INIT",
                "category": "ROUTINE",
                "title": "Welcome to Smart Study Monitor",
                "insight": "Complete your first study session to unlock personalized behavioral pattern analysis.",
                "action": "Start a 25-minute focused study block.",
                "confidence": 1.0,
                "evidence": {"sessions_count": 0}
            }]

        total_sessions = len(sessions)
        durations = [getattr(s, "duration", 0.0) / 60.0 for s in sessions if getattr(s, "duration", 0.0) > 60.0]
        focus_scores = [getattr(s, "focus_score", 100.0) for s in sessions if getattr(s, "duration", 0.0) > 60.0]
        phone_times = [getattr(s, "phone_time", 0.0) for s in sessions]
        posture_times = [getattr(s, "posture_issue_time", 0.0) for s in sessions]

        # 1. Fatigue & Duration Pattern Analysis
        if len(durations) >= 2:
            long_sessions = [d for d in durations if d >= 40.0]
            short_sessions = [d for d in durations if d < 40.0]

            long_scores = [focus_scores[i] for i, d in enumerate(durations) if d >= 40.0]
            short_scores = [focus_scores[i] for i, d in enumerate(durations) if d < 40.0]

            if long_scores and short_scores and np.mean(long_scores) < (np.mean(short_scores) - 8.0):
                avg_long = round(float(np.mean(long_scores)), 1)
                avg_short = round(float(np.mean(short_scores)), 1)
                recommendations.append(Recommendation(
                    rec_id="REC-FATIGUE-01",
                    category="FATIGUE",
                    title="Fatigue Onset in Long Sessions",
                    insight=f"Your average focus score drops from {avg_short}% in shorter sessions to {avg_long}% in sessions exceeding 40 minutes.",
                    action="Adopt the Pomodoro technique: study in 35-minute focused blocks followed by a 5-minute break.",
                    confidence=0.88,
                    evidence={"short_avg": avg_short, "long_avg": avg_long, "threshold_minutes": 40}
                ))

        # 2. Posture Degradation Pattern
        total_posture_seconds = sum(posture_times)
        if total_posture_seconds > 180.0:
            recommendations.append(Recommendation(
                rec_id="REC-POSTURE-01",
                category="POSTURE",
                title="Ergonomic Slouch Detection",
                insight=f"Detected {int(total_posture_seconds / 60)} minutes of shoulder tilt or forward head slouching across your sessions.",
                action="Elevate your monitor/screen to eye level and adjust your chair backrest to maintain lumbar support.",
                confidence=0.84,
                evidence={"total_slouch_seconds": total_posture_seconds}
            ))

        # 3. Phone Distraction Pattern
        total_phone_seconds = sum(phone_times)
        if total_phone_seconds > 120.0:
            recommendations.append(Recommendation(
                rec_id="REC-PHONE-01",
                category="DISTRACTION",
                title="Phone Habit Reduction",
                insight=f"Phone checks accounted for {int(total_phone_seconds / 60)} minutes of lost study focus.",
                action="Place your phone outside arm's reach or in another room during high-focus study sprints.",
                confidence=0.92,
                evidence={"total_phone_seconds": total_phone_seconds}
            ))

        # 4. Consistency & Streak Insight
        streaks = [getattr(s, "longest_streak", 0.0) / 60.0 for s in sessions if hasattr(s, "longest_streak")]
        if streaks and np.mean(streaks) >= 15.0:
            avg_streak = round(float(np.mean(streaks)), 1)
            recommendations.append(Recommendation(
                rec_id="REC-STREAK-01",
                category="FOCUS",
                title="Strong Deep Work Capacity",
                insight=f"You achieve sustained focus streaks averaging {avg_streak} uninterrupted minutes.",
                action="Schedule your most challenging topics or problem sets during your peak streak hours.",
                confidence=0.90,
                evidence={"average_streak_minutes": avg_streak}
            ))

        return [r.to_dict() for r in recommendations]
