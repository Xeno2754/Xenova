from faster_whisper import WhisperModel

print("Loading Whisper model... (first run may take a few minutes)")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

segments, info = model.transcribe("test.wav")

print("\nDetected Language:", info.language)
print("\nTranscription:\n")

for segment in segments:
    print(segment.text)