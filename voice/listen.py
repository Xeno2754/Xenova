import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

print("Loading Whisper...")
model = WhisperModel("base", device="cpu", compute_type="int8")

sample_rate = 16000
duration = 5

print("\n🎤 Speak now...")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="float32"
)

sd.wait()

sf.write("temp.wav", audio, sample_rate)

print("🧠 Understanding...")

segments, info = model.transcribe("temp.wav")

text = ""

for segment in segments:
    text += segment.text

print("\nYou said:")
print(text)