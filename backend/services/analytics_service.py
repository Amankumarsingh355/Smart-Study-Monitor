from typing import Optional, Dict
from backend.services.session_service import SessionService, get_session_service
from backend.schemas.analytics import SessionAnalyticsResponse, AggregatedAnalyticsResponse


class AnalyticsService:
    """
    Computes statistical and analytical metrics for individual study sessions
    and historical aggregate performance over time.
    """

    def __init__(self, session_service: Optional[SessionService] = None):
        self.session_service = session_service or get_session_service()

    def get_session_analytics(self, session_id: str) -> Optional[SessionAnalyticsResponse]:
        """Compute detailed analytics for a single session."""
        session = self.session_service.get_session(session_id)
        if not session:
            return None

        events = self.session_service.get_session_events(session_id)
        events_breakdown: Dict[str, int] = {}
        for ev in events:
            events_breakdown[ev.event_type] = events_breakdown.get(ev.event_type, 0) + 1

        return SessionAnalyticsResponse(
            session_id=session.id,
            duration=session.duration,
            focus_score=session.focus_score,
            focused_time=session.focused_time,
            reading_time=session.reading_time,
            distracted_time=session.distracted_time,
            phone_time=session.phone_time,
            drowsy_time=session.drowsy_time,
            no_face_time=session.no_face_time,
            posture_issue_time=session.posture_issue_time,
            distraction_count=session.distraction_count,
            longest_streak=session.longest_streak,
            events_count=len(events),
            events_breakdown=events_breakdown
        )

    def get_aggregated_analytics(self) -> AggregatedAnalyticsResponse:
        """Compute aggregate performance across all stored study sessions."""
        sessions = self.session_service.get_sessions(limit=500)
        if not sessions:
            return AggregatedAnalyticsResponse(
                total_sessions=0,
                total_study_time=0.0,
                average_focus_score=100.0,
                total_distractions=0,
                total_phone_time=0.0,
                total_reading_time=0.0,
                longest_focus_streak=0.0
            )

        total_sessions = len(sessions)
        total_study_time = sum(s.duration for s in sessions)
        average_focus_score = sum(s.focus_score for s in sessions) / total_sessions
        total_distractions = sum(s.distraction_count for s in sessions)
        total_phone_time = sum(s.phone_time for s in sessions)
        total_reading_time = sum(s.reading_time for s in sessions)
        longest_focus_streak = max((s.longest_streak for s in sessions), default=0.0)

        return AggregatedAnalyticsResponse(
            total_sessions=total_sessions,
            total_study_time=round(total_study_time, 1),
            average_focus_score=round(average_focus_score, 1),
            total_distractions=total_distractions,
            total_phone_time=round(total_phone_time, 1),
            total_reading_time=round(total_reading_time, 1),
            longest_focus_streak=round(longest_focus_streak, 1)
        )

    def get_recommendations(self) -> list:
        """Generate personalized AI recommendations based on historical sessions."""
        from src.ml.recommendations import RecommendationEngine
        engine = RecommendationEngine()
        sessions = self.session_service.get_sessions(limit=100)
        return engine.generate_recommendations(sessions=sessions)


_analytics_service_instance: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    global _analytics_service_instance
    if _analytics_service_instance is None:
        _analytics_service_instance = AnalyticsService()
    return _analytics_service_instance


def set_analytics_service(service: AnalyticsService) -> None:
    global _analytics_service_instance
    _analytics_service_instance = service
