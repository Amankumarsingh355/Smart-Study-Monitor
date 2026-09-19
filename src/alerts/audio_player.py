import os
import logging
from typing import Optional, Dict

from config import ALERT_CONFIG, ALERT_PRIORITY_ORDER, AUDIO_ENABLED, SOUNDS_DIR

logger = logging.getLogger(__name__)


class AudioPlayer:
    """
    Reusable, non-blocking spoken audio player powered by pygame.mixer.
    
    Supports:
    - Multi-scenario alert dispatch (DROWSY, FACE_BLOCKED, PHONE_USAGE)
    - Priority-based interruption (DROWSY > PHONE_USAGE > FACE_BLOCKED)
    - Re-entrancy suppression (does not restart audio while already playing)
    - Fault-tolerant missing file and hardware error handling
    """

    def __init__(
        self,
        sounds_dir: Optional[str] = None,
        sound_path: Optional[str] = None  # Preserved for backwards compatibility
    ):
        self.sounds_dir = sounds_dir or SOUNDS_DIR
        self._initialized = False
        self._channel = None
        self._current_playing_type: Optional[str] = None
        self._loaded_sounds: Dict[str, Any] = {}

        # Default legacy fallback chime if requested directly
        self.default_legacy_sound = sound_path or os.path.join(self.sounds_dir, "alert_phone.wav")

    def _init_mixer(self) -> bool:
        """Initialize pygame.mixer safely on first play request."""
        if self._initialized:
            return True

        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._channel = pygame.mixer.Channel(0)
            self._initialized = True
            return True
        except Exception as e:
            print(f"[WARN] Audio mixer initialization notice: {e}")
            self._initialized = False
            return False

    @staticmethod
    def _normalize_alert_type(alert_type: str) -> str:
        """Normalize alert aliases to canonical configuration keys."""
        normalized = alert_type.upper().strip()
        if normalized in ("PHONE", "PHONE_DETECTED"):
            return "PHONE_USAGE"
        if normalized in ("DROWSINESS", "EYES_CLOSED"):
            return "DROWSY"
        if normalized in ("FACE_COVERED", "FACE_OBSTRUCTED"):
            return "FACE_BLOCKED"
        return normalized

    def get_priority(self, alert_type: str) -> int:
        """
        Return the numeric priority for an alert type (lower number = higher priority).
        Defaults to 99 for unknown alerts.
        """
        norm = self._normalize_alert_type(alert_type)
        if norm in ALERT_CONFIG:
            return ALERT_CONFIG[norm].get("priority", 99)
        if norm in ALERT_PRIORITY_ORDER:
            return ALERT_PRIORITY_ORDER.index(norm) + 1
        return 99

    def is_playing(self) -> bool:
        """Check if any alert audio is currently actively playing."""
        if not self._initialized or self._channel is None:
            return False
        try:
            busy = self._channel.get_busy()
            if not busy:
                self._current_playing_type = None
            return bool(busy)
        except Exception:
            return False

    @property
    def current_playing_type(self) -> Optional[str]:
        """Return the canonical alert type currently playing, or None."""
        if not self.is_playing():
            self._current_playing_type = None
        return self._current_playing_type

    def stop(self) -> None:
        """Stop any currently playing audio immediately."""
        if self._initialized and self._channel is not None:
            try:
                self._channel.stop()
            except Exception:
                pass
        self._current_playing_type = None

    def play(self, alert_type: str) -> bool:
        """
        Play the audio alert for the given alert type.

        Priority & Debounce Policy:
        1. If same audio is currently playing: do NOT restart.
        2. If lower-priority alert is playing and higher-priority arrives: stop lower and play higher.
        3. If higher-priority alert is playing and lower-priority arrives: suppress lower.

        Returns:
            True if audio playback started, False otherwise.
        """
        if not AUDIO_ENABLED:
            return False

        norm_type = self._normalize_alert_type(alert_type)
        alert_info = ALERT_CONFIG.get(norm_type)

        if not alert_info or not alert_info.get("enabled", True):
            return False

        audio_filename = alert_info.get("audio")
        if not audio_filename:
            return False

        # Priority & Re-entrancy Check
        if self.is_playing():
            if self._current_playing_type == norm_type:
                # Case 1: Same event continues while audio is playing -> do NOT restart
                return False

            current_priority = self.get_priority(self._current_playing_type or "")
            new_priority = self.get_priority(norm_type)

            if new_priority < current_priority:
                # Case 3: Higher priority preempts lower priority (e.g. DROWSY preempts PHONE_USAGE)
                self.stop()
            else:
                # Lower or equal priority suppressed while higher priority is active
                return False

        # Initialize audio engine
        if not self._init_mixer():
            return False

        # Verify sound file existence
        audio_path = os.path.join(self.sounds_dir, audio_filename)
        if not os.path.exists(audio_path):
            print(f"[WARNING] Audio file not found: {audio_filename}")
            return False

        # Load and play sound non-blockingly
        try:
            import pygame
            if audio_path not in self._loaded_sounds:
                self._loaded_sounds[audio_path] = pygame.mixer.Sound(audio_path)

            sound = self._loaded_sounds[audio_path]
            self._channel.play(sound)
            self._current_playing_type = norm_type
            return True
        except Exception as e:
            print(f"[WARN] Audio playback failed for {audio_filename}: {e}")
            return False

    def play_phone_alert(self) -> bool:
        """Legacy helper preserving backwards compatibility with Phase 4."""
        return self.play("PHONE_USAGE")

    def close(self) -> None:
        """Release audio resources."""
        self.stop()
        self._loaded_sounds.clear()
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception:
            pass
        self._initialized = False
