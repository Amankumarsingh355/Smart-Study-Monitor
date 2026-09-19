import os
from dataclasses import dataclass, field

# Base directory for sound assets
SOUNDS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "sounds"
)

# ---------------------------------------------------------
# Global Temporal & Threshold Parameters
# ---------------------------------------------------------
DROWSY_THRESHOLD = 2.5            # Eyes closed seconds to trigger DROWSY
FACE_BLOCK_THRESHOLD = 1.5        # Face obscured seconds to trigger FACE_BLOCKED
PHONE_PERSISTENCE_SECONDS = 1.0   # Phone detected seconds to trigger PHONE_USAGE
ALERT_COOLDOWN_SECONDS = 5.0      # Cooldown seconds between repeated audio triggers
AUDIO_ENABLED = True              # Master audio toggle

# Backward compatibility alias
ALERT_COOLDOWN = ALERT_COOLDOWN_SECONDS

# ---------------------------------------------------------
# Alert Configuration (Audio + Screen Synchronization)
# ---------------------------------------------------------
ALERT_CONFIG = {
    "DROWSY": {
        "enabled": True,
        "audio": "wake_up_hi.wav",
        "screen_text": "WAKE UP & STUDY!",
        "priority": 1,  # Highest priority
        "severity": "CRITICAL"
    },
    "PHONE_USAGE": {
        "enabled": True,
        "audio": "phone_usage_hi.wav",
        "screen_text": "PUT THE PHONE AWAY!",
        "priority": 2,
        "severity": "HIGH"
    },
    "FACE_BLOCKED": {
        "enabled": True,
        "audio": "face_blocked_hi.wav",
        "screen_text": "DON'T COVER YOUR FACE!",
        "priority": 3,
        "severity": "MEDIUM"
    }
}

# Explicit priority hierarchy: lower index = higher priority
ALERT_PRIORITY_ORDER = ["DROWSY", "PHONE_USAGE", "FACE_BLOCKED"]


@dataclass
class CameraSettings:
    camera_index: int = 0
    width: int = 1280
    height: int = 720


@dataclass
class EyeSettings:
    ear_threshold: float = 0.20
    drowsy_duration_seconds: float = DROWSY_THRESHOLD  # Eyes closed >= threshold triggers DROWSY


@dataclass
class PhoneSettings:
    confidence_threshold: float = 0.40
    persistence_seconds: float = PHONE_PERSISTENCE_SECONDS  # Phone visible >= threshold triggers PHONE_USAGE


@dataclass
class FaceSettings:
    no_face_duration_seconds: float = 2.0  # Missing face >= 2.0s triggers AWAY / NO_FACE
    face_block_threshold_seconds: float = FACE_BLOCK_THRESHOLD  # Face blocked >= threshold triggers FACE_BLOCKED


@dataclass
class AlertSettings:
    cooldown_seconds: float = ALERT_COOLDOWN_SECONDS
    audio_enabled: bool = AUDIO_ENABLED


@dataclass
class ScoringSettings:
    initial_score: float = 100.0
    phone_penalty_per_second: float = 5.0
    drowsy_penalty_per_second: float = 3.0
    away_penalty_per_second: float = 4.0
    focused_recovery_per_second: float = 2.0


@dataclass
class DatabaseSettings:
    db_path: str = "data/study_monitor.db"
    sample_interval_seconds: float = 2.0  # Periodic behavior sampling rate


@dataclass
class AppConfig:
    camera: CameraSettings = field(default_factory=CameraSettings)
    eye: EyeSettings = field(default_factory=EyeSettings)
    phone: PhoneSettings = field(default_factory=PhoneSettings)
    face: FaceSettings = field(default_factory=FaceSettings)
    alert: AlertSettings = field(default_factory=AlertSettings)
    scoring: ScoringSettings = field(default_factory=ScoringSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)


# Singleton default configuration instance
default_config = AppConfig()
