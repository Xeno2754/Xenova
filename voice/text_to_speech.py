import re
import time
import threading
from pathlib import Path
import subprocess
import sys


# Fast TTS runs in the dedicated Python 3.12 environment because Kokoro
# requires NumPy 1.26.4, while the main Xenova environment uses Python 3.13.
KOKORO_PYTHON = Path(__file__).resolve().parents[1] / "kokoro_venv" / "Scripts" / "python.exe"


tts = None
_tts_lock = threading.Lock()
_tts_ready = threading.Event()
_tts_loading = False
_tts_error = None

DEFAULT_SPEAKER = "Claribel Dervla"
DEFAULT_KOKORO_VOICE = "af_heart"


def _kokoro_available():
    return KOKORO_PYTHON.exists()


def _kokoro_code():
    return r'''
import sys
import numpy as np
import sounddevice as sd
from kokoro import KPipeline

text = sys.argv[1]
voice = sys.argv[2] if len(sys.argv) > 2 else "af_heart"
speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

pipeline = KPipeline(lang_code="a")
chunks = []
for _, _, audio in pipeline(text, voice=voice, speed=speed):
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    chunks.append(np.asarray(audio, dtype=np.float32))

if not chunks:
    raise RuntimeError("Kokoro generated no audio")

audio = np.concatenate(chunks)
sd.play(audio, 24000)
sd.wait()
'''


def speak_fast(text, voice=DEFAULT_KOKORO_VOICE, speed=1.0):
    """Use the isolated Python 3.12 Kokoro environment for fast local speech."""
    if not text or not str(text).strip():
        return False
    if not _kokoro_available():
        raise RuntimeError(f"Kokoro environment not found: {KOKORO_PYTHON}")

    start = time.time()
    print("⚡ Fast TTS: Kokoro")
    subprocess.run(
        [str(KOKORO_PYTHON), "-c", _kokoro_code(), str(text), voice, str(speed)],
        check=True,
    )
    print(f"⚡ Fast TTS total: {time.time() - start:.2f}s")
    return True


def get_tts():
    global tts, _tts_loading, _tts_error

    if tts is not None:
        return tts

    with _tts_lock:
        if tts is not None:
            return tts
        if _tts_loading:
            loader = False
        else:
            _tts_loading = True
            loader = True

    if not loader:
        _tts_ready.wait()
        if tts is not None:
            return tts
        raise RuntimeError(f"XTTS failed to load: {_tts_error}")

    try:
        import torch
        from TTS.api import TTS

        print("🔊 Loading XTTS v2...")
        start = time.time()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖥️ TTS device: {device}")

        engine = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=False,
        )
        tts = engine.to(device)
        print(f"✅ XTTS loaded in {time.time() - start:.2f}s")
        return tts

    except Exception as e:
        _tts_error = e
        raise
    finally:
        _tts_loading = False
        _tts_ready.set()


def preload_tts():
    """Keep XTTS preload available for character/high-quality mode."""
    try:
        get_tts()
        print("✅ XTTS ready.")
        return True
    except Exception as e:
        print(f"⚠️ XTTS preload failed: {e}")
        return False


def _split_sentences(text, max_chars=220):
    text = re.sub(r"\s+", " ", str(text)).strip()
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)
    result = []
    for part in parts:
        part = part.strip()
        while len(part) > max_chars:
            cut = part.rfind(" ", 0, max_chars)
            if cut < 80:
                cut = max_chars
            result.append(part[:cut].strip())
            part = part[cut:].strip()
        if part:
            result.append(part)
    return result


def speak(text):
    """Fast default speech. Falls back to XTTS if Kokoro is unavailable."""
    start = time.time()
    try:
        if speak_fast(text):
            return
    except Exception as e:
        print(f"⚠️ Fast TTS unavailable: {e}")
        print("↩️ Falling back to XTTS v2...")

    import sounddevice as sd
    import soundfile as sf

    filename = "response.wav"
    engine = get_tts()

    start_tts = time.time()
    print("🗣️ Generating XTTS speech...")
    engine.tts_to_file(
        text=str(text),
        speaker=DEFAULT_SPEAKER,
        language="en",
        file_path=filename,
    )
    print(f"⚡ XTTS generation: {time.time() - start_tts:.2f}s")

    start_playback = time.time()
    audio, samplerate = sf.read(filename)
    sd.play(audio, samplerate)
    sd.wait()
    print(f"🔊 Playback: {time.time() - start_playback:.2f}s")
    print(f"⚡ Total TTS: {time.time() - start:.2f}s")


def speak_stream(text):
    """Fast default streaming API; uses Kokoro sentence by sentence."""
    sentences = _split_sentences(text)
    if not sentences:
        return

    total_start = time.time()
    print(f"🗣️ Fast streaming speech: {len(sentences)} sentence(s)")

    for index, sentence in enumerate(sentences, 1):
        start = time.time()
        try:
            speak_fast(sentence)
        except Exception as e:
            print(f"⚠️ Kokoro sentence {index} failed: {e}")
            # Fall back to the existing XTTS path for this sentence.
            speak(sentence)
        print(f"⚡ Sentence {index}: {time.time() - start:.2f}s")

    print(f"⚡ Total fast streaming TTS: {time.time() - total_start:.2f}s")
