import numpy as np
import sounddevice as sd
from openwakeword.model import Model

# Load the wake word model
model = Model()

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80 ms of audio


def listen_for_wake_word():
    print("👂 Waiting for wake word...")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE,
    ) as stream:

        while True:
            audio, overflowed = stream.read(CHUNK_SIZE)

            if overflowed:
                continue

            audio = audio.flatten()

            prediction = model.predict(audio)

            for wakeword, score in prediction.items():
                if score > 0.5:
                    print(f"✅ Wake word detected: {wakeword}")
                    return