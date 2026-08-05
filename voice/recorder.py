import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000


def record(filename="temp.wav", duration=5):
    print("\n🎤 Speak...")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )

    sd.wait()

    sf.write(filename, audio, SAMPLE_RATE)

    return filename