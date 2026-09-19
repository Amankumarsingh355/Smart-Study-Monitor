import time
import cv2
from typing import Optional, Dict, Any

from config import ALERT_CONFIG, ALERT_COOLDOWN_SECONDS
from .audio_player import AudioPlayer


class AlertManager:
    """
    Coordinates synchronized visual warnings, spoken Hindi audio alarms,
    and EventBus WebSocket dispatches.
    
    Enforces per-alert cooldowns, priority preemption, and debouncing.
    """

    def __init__(
        self,
        cooldown_seconds: float = ALERT_COOLDOWN_SECONDS,
        audio_player: Optional[AudioPlayer] = None
    ):
        self.cooldown_seconds = cooldown_seconds
        self.audio_player = audio_player or AudioPlayer()

        # Cooldown timestamps per alert type
        self._last_alert_times: Dict[str, float] = {}
        self._visual_alert_active: bool = False
        self._current_alert_type: Optional[str] = None
        self._current_alert_message: str = ""

    @staticmethod
    def _normalize_event(event: Optional[str]) -> Optional[str]:
        """Normalize event string to canonical ALERT_CONFIG key."""
        if not event:
            return None
        norm = event.upper().strip()
        if norm in ("PHONE", "PHONE_DETECTED"):
            return "PHONE_USAGE"
        if norm in ("DROWSINESS", "EYES_CLOSED"):
            return "DROWSY"
        if norm in ("FACE_COVERED", "FACE_OBSTRUCTED"):
            return "FACE_BLOCKED"
        return norm

    def process_event(
        self,
        event: Optional[str],
        current_time: Optional[float] = None,
        confidence: float = 0.95
    ) -> bool:
        """
        Process an incoming behavioral event (e.g. 'DROWSY', 'FACE_BLOCKED', 'PHONE_USAGE').

        Args:
            event: Event type string or None if state is normal.
            current_time: Optional float timestamp.
            confidence: State detection confidence (0.0 - 1.0).

        Returns:
            True if audio playback was triggered on this frame,
            False if suppressed by cooldown, playing audio, or inactive event.
        """
        now = current_time if current_time is not None else time.time()
        norm_type = self._normalize_event(event)

        if not norm_type or norm_type not in ALERT_CONFIG:
            self._visual_alert_active = False
            self._current_alert_type = None
            self._current_alert_message = ""
            return False

        alert_info = ALERT_CONFIG[norm_type]
        if not alert_info.get("enabled", True):
            self._visual_alert_active = False
            return False

        # Visual banner is active whenever the condition persists
        self._visual_alert_active = True
        self._current_alert_type = norm_type
        self._current_alert_message = alert_info.get("screen_text", "")

        # Check per-alert cooldown
        last_time = self._last_alert_times.get(norm_type, 0.0)
        time_since_last = now - last_time

        if time_since_last >= self.cooldown_seconds:
            # Attempt to trigger spoken audio alert
            if hasattr(self.audio_player, "play"):
                audio_played = self.audio_player.play(norm_type)
            elif hasattr(self.audio_player, "play_phone_alert") and norm_type == "PHONE_USAGE":
                self.audio_player.play_phone_alert()
                audio_played = True
            else:
                audio_played = False

            # Record alert trigger timestamp
            self._last_alert_times[norm_type] = now

            # Broadcast structured event to EventBus -> WebSocket -> Dashboard
            try:
                from src.events.event_bus import event_bus
                event_payload = {
                    "type": "ALERT",
                    "event_type": norm_type,
                    "alert_type": norm_type,
                    "screen_message": self._current_alert_message,
                    "audio": alert_info.get("audio", ""),
                    "severity": alert_info.get("severity", "WARNING"),
                    "confidence": round(confidence, 2),
                    "timestamp": now
                }
                event_bus.publish("ALERT", event_payload)
            except Exception as e:
                print(f"[WARN] Event bus dispatch notice: {e}")

            return audio_played

        return False

    @property
    def is_visual_alert_active(self) -> bool:
        """Whether a visual warning banner should be displayed."""
        return self._visual_alert_active

    @property
    def alert_message(self) -> str:
        """Current alert banner text."""
        return self._current_alert_message

    @property
    def current_alert_type(self) -> Optional[str]:
        """Current active alert type."""
        return self._current_alert_type

    def get_cooldown_remaining(
        self,
        alert_type: str = "PHONE_USAGE",
        current_time: Optional[float] = None
    ) -> float:
        """Return remaining cooldown seconds until specified audio alert can play again."""
        norm_type = self._normalize_event(alert_type) or "PHONE_USAGE"
        now = current_time if current_time is not None else time.time()
        last_time = self._last_alert_times.get(norm_type, 0.0)
        elapsed = now - last_time
        return max(0.0, self.cooldown_seconds - elapsed)

    def draw_visual_warning(self, frame):
        """
        Render a high-visibility, high-contrast warning banner onto the OpenCV frame.
        """
        if not self._visual_alert_active or not self._current_alert_message:
            return frame

        height, width, _ = frame.shape

        # Semi-transparent high-contrast alert card at bottom
        banner_height = 68
        y_top = height - 95
        y_bottom = y_top + banner_height

        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (0, y_top),
            (width, y_bottom),
            (0, 0, 180),  # Dark crimson red
            -1
        )
        # Blend overlay (alpha = 0.80)
        cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

        # Pulsing / prominent red perimeter border
        cv2.rectangle(frame, (0, 0), (width - 1, height - 1), (0, 0, 255), 4)

        # Warning icon and text
        text = f"! {self._current_alert_message}"
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.05
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = y_top + (banner_height + text_size[1]) // 2

        # Bright white text on red banner
        cv2.putText(
            frame,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )

        return frame

    def close(self):
        """Release audio resources."""
        self.audio_player.close()
