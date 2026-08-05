import time

model = None


def get_model():
    global model

    if model is None:
        from faster_whisper import WhisperModel

        print("Loading Whisper model...")

        start = time.time()

        model = WhisperModel(
            "base",
            device="cuda",
            compute_type="float16"
        )

        print(f"✅ Whisper loaded in {time.time() - start:.2f}s")

    return model


def transcribe(audio_file):
    whisper = get_model()

    segments, info = whisper.transcribe(audio_file)

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()