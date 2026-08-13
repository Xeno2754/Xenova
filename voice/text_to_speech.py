import atexit
import json
import re
import subprocess
import threading
import time
from pathlib import Path


# Kokoro requires Python 3.12 + NumPy 1.26.4, so it runs in the dedicated
# environment while the main Xenova application stays on Python 3.13.
KOKORO_PYTHON = Path(__file__).resolve().parents[1] / "kokoro_venv" / "Scripts" / "python.exe"

DEFAULT_SPEAKER = "Claribel Dervla"
DEFAULT_KOKORO_VOICE = "af_heart"

_worker = None
_worker_lock = threading.Lock()

# This code is intentionally kept here so the user only needs one Xenova repo.
# The subprocess stays alive between replies, keeping Kokoro's model in RAM/VRAM.
_KOKORO_WORKER_CODE = r'''
import json
import sys
import numpy as np
import sounddevice as sd
from kokoro import KPipeline

pipeline = KPipeline(lang_code="a")
print("READY", flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
        if req.get("command") == "shutdown":
            print("BYE", flush=True)
            break

        text = str(req.get("text", "")).strip()
        voice = str(req.get("voice", "af_heart"))
        speed = float(req.get("speed", 1.0))

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
        print("DONE", flush=True)
    except Exception as exc:
        print("ERROR", flush=True)
        print(f"Kokoro worker error: {exc}", file=sys.stderr, flush=True)
'''


def _start_kokoro_worker():
    global _worker

    if not KOKORO_PYTHON.exists():
        raise RuntimeError(f"Kokoro Python not found: {KOKORO_PYTHON}")

    with _worker_lock:
        if _worker is not None and _worker.poll() is None:
            return _worker

        print("🔊 Starting persistent Kokoro worker...")
        start = time.time()
        _worker = subprocess.Popen(
            [str(KOKORO_PYTHON), "-c", _KOKORO_WORKER_CODE],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,
            text=True,
            bufsize=1,
        )

        ready = _worker.stdout.readline().strip()
        if ready != "READY":
            output = ready or "no READY signal"
            _worker.kill()
            _worker = None
            raise RuntimeError(f"Kokoro worker failed to start: {output}")

        print(f"✅ Kokoro worker ready in {time.time() - start:.2f}s")
        return _worker


def preload_tts():
    """Preload the FAST default voice. XTTS is deliberately not loaded at startup."""
    try:
        _start_kokoro_worker()
        return True
    except Exception as exc:
        print(f"⚠️ Kokoro preload failed: {exc}")
        return False


def speak_fast(text, voice=DEFAULT_KOKORO_VOICE, speed=1.0):
    if not text or not str(text).strip():
        return False

    start = time.time()
    worker = _start_kokoro_worker()

    with _worker_lock:
        if worker.poll() is not None:
            raise RuntimeError("Kokoro worker stopped")

        worker.stdin.write(json.dumps({
            "command": "speak",
            "text": str(text),
            "voice": voice,
            "speed": speed,
        }) + "\n")
        worker.stdin.flush()

        result = worker.stdout.readline().strip()

    if result != "DONE":
        raise RuntimeError("Kokoro worker failed while generating speech")

    print(f"⚡ Fast TTS total: {time.time() - start:.2f}s")
    return True


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


def _get_xtts():
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
    engine = engine.to(device)
    print(f"✅ XTTS loaded in {time.time() - start:.2f}s")
    return engine


_xtts = None
_xtts_lock = threading.Lock()


def speak_xtts(text):
    global _xtts
    import sounddevice as sd
    import soundfile as sf

    with _xtts_lock:
        if _xtts is None:
            _xtts = _get_xtts()
        engine = _xtts

    filename = "response.wav"
    start = time.time()
    engine.tts_to_file(
        text=str(text),
        speaker=DEFAULT_SPEAKER,
        language="en",
        file_path=filename,
    )
    print(f"⚡ XTTS generation: {time.time() - start:.2f}s")

    audio, samplerate = sf.read(filename)
    sd.play(audio, samplerate)
    sd.wait()


def speak(text):
    """Fast Kokoro by default; XTTS is fallback/high-quality mode only."""
    if not text or not str(text).strip():
        return

    try:
        speak_fast(text)
    except Exception as exc:
        print(f"⚠️ Kokoro unavailable: {exc}")
        print("↩️ Falling back to XTTS v2...")
        speak_xtts(text)


def speak_stream(text):
    """Sentence-level fast speech while reusing the same Kokoro worker."""
    sentences = _split_sentences(text)
    if not sentences:
        return

    total_start = time.time()
    print(f"🗣️ Fast streaming speech: {len(sentences)} sentence(s)")

    for index, sentence in enumerate(sentences, 1):
        start = time.time()
        try:
            speak_fast(sentence)
        except Exception as exc:
            print(f"⚠️ Kokoro sentence {index} failed: {exc}")
            speak_xtts(sentence)
        print(f"⚡ Sentence {index}: {time.time() - start:.2f}s")

    print(f"⚡ Total fast streaming TTS: {time.time() - total_start:.2f}s")


def shutdown():
    global _worker
    with _worker_lock:
        if _worker is None or _worker.poll() is not None:
            return
        try:
            _worker.stdin.write(json.dumps({"command": "shutdown"}) + "\n")
            _worker.stdin.flush()
            _worker.wait(timeout=2)
        except Exception:
            try:
                _worker.kill()
            except Exception:
                pass
        finally:
            _worker = None


atexit.register(shutdown)
