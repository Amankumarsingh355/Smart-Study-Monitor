from typing import Dict, List, Any, Union
from .study_state import StudyState


class SessionMetrics:
    """
    Phase 7 Longitudinal Session Analytics.
    
    Tracks cumulative study durations, focus ratio, focus streaks,
    distraction episodes, and distraction recovery times.
    """

    PRODUCTIVE_STATES = {StudyState.FOCUSED, StudyState.READING}
    DISTRACTION_STATES = {
        StudyState.PHONE_USAGE,
        StudyState.DROWSY,
        StudyState.DISTRACTED,
        StudyState.LOOKING_AWAY,
        StudyState.POOR_POSTURE,
        StudyState.AWAY_FROM_DESK,
        StudyState.NO_FACE
    }

    def __init__(self):
        # Time accumulators (in seconds)
        self.total_time: float = 0.0
        self.focused_time: float = 0.0
        self.distracted_time: float = 0.0
        self.phone_time: float = 0.0
        self.drowsy_time: float = 0.0
        self.no_face_time: float = 0.0
        self.posture_issue_time: float = 0.0
        self.reading_time: float = 0.0

        # Focus Streaks
        self.current_focus_streak: float = 0.0
        self.longest_focus_streak: float = 0.0

        # Distraction Episodes & Durations
        self.distraction_count: int = 0
        self.distraction_episodes: List[float] = []
        self._current_distraction_duration: float = 0.0
        self._in_distraction: bool = False

        # Recovery Times
        self.recovery_times: List[float] = []

    # -------------------------------------------------------------------------
    # Backward Compatibility Aliases for Phase 5 / Tests
    # -------------------------------------------------------------------------
    @property
    def total_duration(self) -> float:
        return self.total_time

    @total_duration.setter
    def total_duration(self, value: float):
        self.total_time = value

    @property
    def focused_duration(self) -> float:
        return self.focused_time

    @focused_duration.setter
    def focused_duration(self, value: float):
        self.focused_time = value

    @property
    def phone_duration(self) -> float:
        return self.phone_time

    @phone_duration.setter
    def phone_duration(self, value: float):
        self.phone_time = value

    @property
    def drowsy_duration(self) -> float:
        return self.drowsy_time

    @drowsy_duration.setter
    def drowsy_duration(self, value: float):
        self.drowsy_time = value

    @property
    def no_face_duration(self) -> float:
        return self.no_face_time

    @no_face_duration.setter
    def no_face_duration(self, value: float):
        self.no_face_time = value

    @property
    def distracted_duration(self) -> float:
        return self.distracted_time

    @distracted_duration.setter
    def distracted_duration(self, value: float):
        self.distracted_time = value

    # -------------------------------------------------------------------------
    # Analytical Properties
    # -------------------------------------------------------------------------
    @property
    def focus_ratio(self) -> float:
        """
        Ratio of productive study time (Focused + Reading) to Total time.
        Returns float between 0.0 and 1.0.
        """
        if self.total_time <= 0.0:
            return 1.0
        productive_time = self.focused_time + self.reading_time
        return max(0.0, min(1.0, productive_time / self.total_time))

    @property
    def focus_percentage(self) -> float:
        """Focus ratio expressed as a percentage 0.0 - 100.0."""
        return round(self.focus_ratio * 100.0, 1)

    @property
    def average_recovery_time(self) -> float:
        """
        Average time taken to recover back to focus from a distraction episode.
        """
        if not self.recovery_times:
            return 0.0
        return sum(self.recovery_times) / len(self.recovery_times)

    @property
    def total_distraction_time(self) -> float:
        """Sum of all completed distraction episodes + current ongoing."""
        return sum(self.distraction_episodes) + self._current_distraction_duration

    # -------------------------------------------------------------------------
    # Core Update Engine
    # -------------------------------------------------------------------------
    def update(self, current_state: Union[StudyState, str], dt: float):
        """
        Update cumulative time and track streaks, distraction episodes,
        and recovery times given an elapsed timestep `dt`.
        """
        if dt <= 0.0:
            return

        # Normalize string to StudyState if needed
        state = current_state
        if isinstance(state, str):
            try:
                state = StudyState(state)
            except ValueError:
                for s in StudyState:
                    if s.name.lower() == state.lower() or s.value.lower() == state.lower():
                        state = s
                        break

        self.total_time += dt

        # Accumulate category time
        if state == StudyState.FOCUSED:
            self.focused_time += dt
        elif state == StudyState.READING:
            self.reading_time += dt
        elif state == StudyState.PHONE_USAGE:
            self.phone_time += dt
            self.distracted_time += dt
        elif state == StudyState.DROWSY:
            self.drowsy_time += dt
            self.distracted_time += dt
        elif state in (StudyState.DISTRACTED, StudyState.LOOKING_AWAY):
            self.distracted_time += dt
        elif state in (StudyState.NO_FACE, StudyState.AWAY_FROM_DESK):
            self.no_face_time += dt
            self.distracted_time += dt
        elif state == StudyState.POOR_POSTURE:
            self.posture_issue_time += dt

        # Determine if state is productive or a distraction
        is_productive = state in self.PRODUCTIVE_STATES
        is_distraction = state in self.DISTRACTION_STATES

        # Streak and Distraction Transition Logic
        if is_productive:
            if self._in_distraction:
                # Recovered from distraction!
                completed_episode = self._current_distraction_duration
                self.distraction_episodes.append(completed_episode)
                self.recovery_times.append(completed_episode)
                self._current_distraction_duration = 0.0
                self._in_distraction = False

            # Grow focus streak
            self.current_focus_streak += dt
            if self.current_focus_streak > self.longest_focus_streak:
                self.longest_focus_streak = self.current_focus_streak

        elif is_distraction:
            if not self._in_distraction:
                # Starting a new distraction episode
                self._in_distraction = True
                self.distraction_count += 1
                self.current_focus_streak = 0.0  # Streak broken

            self._current_distraction_duration += dt

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format seconds into MMm SSs or HHh MMm format."""
        secs = int(round(seconds))
        if secs < 60:
            return f"{secs:02d}s"
        mins = secs // 60
        rem_secs = secs % 60
        if mins < 60:
            return f"{mins:02d}m {rem_secs:02d}s"
        hours = mins // 60
        rem_mins = mins % 60
        return f"{hours:02d}h {rem_mins:02d}m"

    def summary(self) -> Dict[str, Any]:
        """Return a dictionary of the session's longitudinal metrics."""
        return {
            "total_time": round(self.total_time, 1),
            "focused_time": round(self.focused_time, 1),
            "reading_time": round(self.reading_time, 1),
            "distracted_time": round(self.distracted_time, 1),
            "phone_time": round(self.phone_time, 1),
            "drowsy_time": round(self.drowsy_time, 1),
            "no_face_time": round(self.no_face_time, 1),
            "posture_issue_time": round(self.posture_issue_time, 1),
            "focus_ratio": round(self.focus_ratio, 3),
            "focus_percentage": self.focus_percentage,
            "distraction_count": self.distraction_count,
            "distraction_episodes": [round(e, 1) for e in self.distraction_episodes],
            "average_recovery_time": round(self.average_recovery_time, 1),
            "current_focus_streak": round(self.current_focus_streak, 1),
            "longest_focus_streak": round(self.longest_focus_streak, 1)
        }

    def reset(self):
        """Reset all session accumulators."""
        self.__init__()
