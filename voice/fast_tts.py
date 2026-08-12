import os
import re
import time
import wave
import threading
from pathlib import Path

_model = None
_lock = threading.Lock()


def get_model():
    global _model
    if _model is not None:
        return _model

    with _lock:
        if _model is None:
            try:
                from kokoro import KPipeline
            except ImportError as e:
                raise RuntimeError(
                    "Kokoro is not installed. Install it with: pip install kokoro soundfile"
                ) from e

            print("🔊 Loading Kokoro TTS...")
            start = time.time()
            # American English, natural fast voice. The pipeline automatically
            # uses the available supported backend.
            _model = KPipeline(lang_code="a")
            print(f"✅ Kokoro loaded in {time.time() - start:.2f}s")

    return _model


def preload():
    get_model()


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def speak(text, voice="af_heart", speed=1.0):
    """Fast local TTS. Generates each sentence and plays it immediately."""
    if not text or not text.strip():
        return

    import sounddevice as sd
    import soundfile as sf

    pipeline = get_model()
    out_dir = Path("cache") / "tts"
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, sentence in enumerate(_sentences(text)):
        path = out_dir / f"sentence_{i}.wav"
        start = time.time()
        generator = pipeline(sentence, voice=voice, speed=speed)
        audio, sample_rate = next(generator)[2:]
        sf.write(str(path), audio, sample_rate)
        print(f"⚡ Kokoro sentence {i + 1}: {time.time() - start:.2f}s")
        data, sr = sf.read(str(path), dtype="float32")
        sd.play(data, sr)
        sd.wait()


def speak_stream(text, voice="af_heart", speed=1.0):
    speak(text, voice=voice, speed=speed)
