import time
import threading

start = time.time()
print("Starting...")

# ==================================================
# IMPORTS
# ==================================================
t = time.time()
from assistant.assistant import XenovaController
print(f"assistant import: {time.time() - t:.2f}s")

t = time.time()
from memory.database import init_db
print(f"database import: {time.time() - t:.2f}s")

# ==================================================
# DATABASE
# ==================================================
t = time.time()
init_db()
print(f"database init: {time.time() - t:.2f}s")
print(f"Total startup before UI: {time.time() - start:.2f}s")


def preload_whisper():
    try:
        print("🔥 Whisper background preload started...")
        from voice.speech_to_text import get_model
        t = time.time()
        get_model()
        print(f"✅ Whisper ready in background: {time.time() - t:.2f}s")
    except Exception as e:
        print(f"⚠️ Whisper preload failed: {e}")


def preload_fast_tts():
    try:
        print("🔥 Kokoro background preload started...")
        from voice.text_to_speech import preload_tts
        t = time.time()
        preload_tts()
        print(f"✅ Kokoro ready in background: {time.time() - t:.2f}s")
    except Exception as e:
        print(f"⚠️ Kokoro preload failed: {e}")


# ==================================================
# APPLICATION
# ==================================================
def main():
    from interface import XenovaInterface

    print("=" * 50)
    print("🤖 XENOVA")
    print("Personal AI Interface")
    print("=" * 50)

    controller = XenovaController()

    interface = XenovaInterface(
        on_command=controller.handle_text,
        on_voice=controller.handle_voice
    )

    controller.interface = interface

    print("✅ XENOVA interface connected")
    print("✅ Text pipeline connected")
    print("✅ Voice pipeline connected")
    print("=" * 50)

    # Preload only the models needed for the normal fast path.
    # XTTS is intentionally lazy and remains available as the
    # high-quality/character-voice fallback.
    threading.Thread(
        target=preload_whisper,
        daemon=True,
        name="WhisperPreloader"
    ).start()

    threading.Thread(
        target=preload_fast_tts,
        daemon=True,
        name="KokoroPreloader"
    ).start()

    interface.run()


if __name__ == "__main__":
    main()
