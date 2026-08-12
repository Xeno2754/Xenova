
import time

model = None


def get_model():
    global model

    if model is None:
        from faster_whisper import WhisperModel

        print("Loading Whisper model...")

        start = time.time()

        model = WhisperModel(
            "tiny.en",
            device="cuda",
            compute_type="float16",
            cpu_threads=4,
            num_workers=1
        )

        print(
            f"Whisper loaded in "
            f"{time.time() - start:.2f}s"
        )

    return model


def transcribe(audio_file):

    start = time.time()

    whisper = get_model()

    print("Transcribing...")

    segments, info = whisper.transcribe(
        audio_file,
        language="en",
        beam_size=1,
        best_of=1,
        temperature=0,
        condition_on_previous_text=False,
        vad_filter=True
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    ).strip()

    elapsed = time.time() - start

    print(
        f"Whisper transcription: "
        f"{elapsed:.2f}s"
    )

    return text

