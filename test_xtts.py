from TTS.api import TTS
import torch

print("Loading XTTS v2...")

tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    gpu=torch.cuda.is_available()
)

print("Model loaded!")

tts.tts_to_file(
    text="Hello. I am Xenova. Your offline artificial intelligence assistant.",
    speaker="Claribel Dervla",
    language="en",
    file_path="output.wav"
)

print("Done! Check output.wav")