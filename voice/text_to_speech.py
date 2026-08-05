import time

tts = None
DEFAULT_SPEAKER = "Claribel Dervla"


def get_tts():
    global tts

    if tts is None:
        import torch
        from TTS.api import TTS

        print("Loading XTTS v2...")

        start = time.time()

        tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            gpu=torch.cuda.is_available()
        )

        print(f"✅ XTTS loaded in {time.time()-start:.2f}s")

    return tts


def speak(text):
    import sounddevice as sd
    import soundfile as sf

    engine = get_tts()

    filename = "response.wav"

    engine.tts_to_file(
        text=text,
        speaker=DEFAULT_SPEAKER,
        language="en",
        file_path=filename
    )

    audio, samplerate = sf.read(filename)

    sd.play(audio, samplerate)
    sd.wait()