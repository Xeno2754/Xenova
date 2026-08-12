import re
import time
import threading
from pathlib import Path


tts = None
_tts_lock = threading.Lock()
_tts_ready = threading.Event()
_tts_loading = False
_tts_error = None

DEFAULT_SPEAKER = "Claribel Dervla"


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
    """Load XTTS in the background before the first response."""
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
    """Original complete-response TTS API, kept for compatibility."""
    import sounddevice as sd
    import soundfile as sf

    filename = "response.wav"
    start_total = time.time()
    engine = get_tts()

    start_tts = time.time()
    print("🗣️ Generating speech...")
    engine.tts_to_file(
        text=str(text),
        speaker=DEFAULT_SPEAKER,
        language="en",
        file_path=filename,
    )
    print(f"⚡ Speech generation: {time.time() - start_tts:.2f}s")

    start_playback = time.time()
    audio, samplerate = sf.read(filename)
    sd.play(audio, samplerate)
    sd.wait()
    print(f"🔊 Playback: {time.time() - start_playback:.2f}s")
    print(f"⚡ Total TTS: {time.time() - start_total:.2f}s")


def speak_stream(text):
    """Generate and play one sentence at a time.

    This reduces perceived latency for longer replies while preserving the
    existing XTTS model and audio backend.
    """
    import sounddevice as sd
    import soundfile as sf

    sentences = _split_sentences(text)
    if not sentences:
        return

    engine = get_tts()
    total_start = time.time()
    print(f"🗣️ Streaming speech: {len(sentences)} sentence(s)")

    for index, sentence in enumerate(sentences, 1):
        filename = Path(f"cache/tts_{threading.get_ident()}_{index}.wav")
        filename.parent.mkdir(parents=True, exist_ok=True)

        start = time.time()
        engine.tts_to_file(
            text=sentence,
            speaker=DEFAULT_SPEAKER,
            language="en",
            file_path=str(filename),
        )
        print(f"⚡ Sentence {index} generation: {time.time() - start:.2f}s")

        audio, samplerate = sf.read(str(filename))
        sd.play(audio, samplerate)
        sd.wait()

        try:
            filename.unlink(missing_ok=True)
        except Exception:
            pass

    print(f"⚡ Total streaming TTS: {time.time() - total_start:.2f}s")
