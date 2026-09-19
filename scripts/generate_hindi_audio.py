"""
Hindi Voice Alert Generator for Smart Study Monitor.

One-time synthesis script that produces local WAV assets:
- assets/sounds/wake_up_hi.wav ("उठ जा! उठ जा! उठ रे!")
- assets/sounds/face_blocked_hi.wav ("बाबू कोई नहीं देख रहा है, मुँह दिखाओ।")
- assets/sounds/phone_usage_hi.wav ("तुम एक काम करो, IAS की तैयारी छोड़ दो... छोड़ दो! तुम्हारी पढ़ाई और तुम्हारे बीच में फोन आ गया, इसका मतलब तुम्हारा पढ़ाई में मन नहीं लग रहा।")

Requires zero runtime internet connection once generated.
"""

import os
import sys
import asyncio
import wave
import numpy as np

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SOUNDS_DIR = os.path.join(PROJECT_ROOT, "assets", "sounds")

ALERT_VOICE_SCRIPTS = {
    "wake_up_hi.wav": {
        "text": "उठ जा! उठ जा! उठ रे!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+15%",
        "pitch": "+0Hz"
    },
    "face_blocked_hi.wav": {
        "text": "बाबू कोई नहीं देख रहा है, मुँह दिखाओ।",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+5%",
        "pitch": "+0Hz"
    },
    "phone_usage_hi.wav": {
        "text": "तुम एक काम करो, IAS की तैयारी छोड़ दो... छोड़ दो! तुम्हारी पढ़ाई और तुम्हारे बीच में फोन आ गया, इसका मतलब तुम्हारा पढ़ाई में मन नहीं लग रहा।",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+10%",
        "pitch": "+0Hz"
    }
}


async def synthesize_file(filename: str, config: dict):
    """Synthesize one Hindi alert file and save as uncompressed 44.1kHz WAV."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    temp_mp3 = os.path.join(SOUNDS_DIR, f"temp_{filename}.mp3")
    target_wav = os.path.join(SOUNDS_DIR, filename)

    print(f"[GEN] Synthesizing '{filename}'...")
    print(f"      Text: \"{config['text']}\"")

    try:
        import edge_tts
        communicate = edge_tts.Communicate(
            text=config["text"],
            voice=config["voice"],
            rate=config["rate"],
            pitch=config["pitch"]
        )
        await communicate.save(temp_mp3)

        # Decode MP3 to PCM and export standard WAV via pygame
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2)

        sound = pygame.mixer.Sound(temp_mp3)
        raw_pcm = pygame.sndarray.array(sound)

        # Write to WAV
        channels = 2 if raw_pcm.ndim > 1 else 1
        with wave.open(target_wav, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(44100)
            wf.writeframes(raw_pcm.tobytes())

        duration = sound.get_length()
        print(f"      -> SUCCESS: {target_wav} ({duration:.2f}s, {os.path.getsize(target_wav)} bytes)")

    finally:
        if os.path.exists(temp_mp3):
            try:
                os.remove(temp_mp3)
            except Exception:
                pass


async def generate_all_alerts():
    print("=" * 65)
    print("  SMART STUDY MONITOR — HINDI VOICE ALERT ASSET GENERATOR")
    print("=" * 65)

    for filename, config in ALERT_VOICE_SCRIPTS.items():
        await synthesize_file(filename, config)

    print("\n[INFO] All Hindi spoken alerts successfully created locally in:")
    print(f"       {SOUNDS_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(generate_all_alerts())
