import time

tts = None

DEFAULT_SPEAKER = "Claribel Dervla"


def get_tts():
    global tts

    if tts is None:

        import torch
        from TTS.api import TTS

        print("🔊 Loading XTTS v2...")

        start = time.time()

        device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"🖥️ TTS device: {device}")

        tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2"
        )

        tts = tts.to(device)

        print(
            f"✅ XTTS loaded in {time.time() - start:.2f}s"
        )

    return tts


def speak(text):

    import sounddevice as sd
    import soundfile as sf

    filename = "response.wav"

    # ---------------------------------
    # LOAD MODEL
    # ---------------------------------

    start_total = time.time()

    engine = get_tts()

    # ---------------------------------
    # GENERATE SPEECH
    # ---------------------------------

    start_tts = time.time()

    print("🗣️ Generating speech...")

    engine.tts_to_file(
        text=text,
        speaker=DEFAULT_SPEAKER,
        language="en",
        file_path=filename
    )

    tts_time = time.time() - start_tts

    print(
        f"⚡ Speech generation: {tts_time:.2f}s"
    )

    # ---------------------------------
    # PLAY AUDIO
    # ---------------------------------

    start_playback = time.time()

    audio, samplerate = sf.read(filename)

    sd.play(audio, samplerate)
    sd.wait()

    playback_time = time.time() - start_playback
    total_time = time.time() - start_total

    print(
        f"🔊 Playback: {playback_time:.2f}s"
    )

    print(
        f"⚡ Total TTS: {total_time:.2f}s"
    )