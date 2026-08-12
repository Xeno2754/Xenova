import time
from voice.fast_tts import get_model, speak

print("Loading fast TTS...")
s = time.time()
get_model()
print(f"Model ready in {time.time() - s:.2f}s")

s = time.time()
speak("Hello. I am Xenova, your offline artificial intelligence assistant.")
print(f"Speech test finished in {time.time() - s:.2f}s")
