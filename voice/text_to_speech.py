import time
import threading


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
            # Another thread is already loading XTTS.
            # Wait instead of starting a second 20-60 second load.
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
            model_name="tts_models/multilingual/multi-dataset/xtts_v2"
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


def speak(text):
    import sounddevice as sd
    import soundfile as sf

    filename = "response.wav"
    start_total = time.time()

    engine = get_tts()

    start_tts = time.time()
    print("🗣️ Generating speech...")

    engine.tts_to_file(
        text=text,
        speaker=DEFAULT_SPEAKER,
        language="en",
        file_path=filename
    )

    tts_time = time.time() - start_tts
    print(f"⚡ Speech generation: {tts_time:.2f}s")

    start_playback = time.time()
    audio, samplerate = sf.read(filename)
    sd.play(audio, samplerate)
    sd.wait()

    playback_time = time.time() - start_playback
    total_time = time.time() - start_total

    print(f"🔊 Playback: {playback_time:.2f}s")
    print(f"⚡ Total TTS: {total_time:.2f}s")
