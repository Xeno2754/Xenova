import torch

# ===========================
# AI MODELS
# ===========================

OLLAMA_MODEL = "llama3.2:latest"

WHISPER_MODEL = "base"

XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

XTTS_SPEAKER = "Claribel Dervla"

LANGUAGE = "en"

# ===========================
# DEVICE
# ===========================

USE_GPU = torch.cuda.is_available()

WHISPER_DEVICE = "cuda" if USE_GPU else "cpu"

WHISPER_COMPUTE_TYPE = "float16" if USE_GPU else "int8"

# ===========================
# MEMORY
# ===========================

DATABASE_PATH = "memory/memory.db"

MAX_HISTORY = 10

# ===========================
# AUDIO
# ===========================

RESPONSE_AUDIO = "response.wav"

RECORD_SAMPLE_RATE = 16000

# ===========================
# APPLICATION
# ===========================

APP_NAME = "XENOVA"

VERSION = "0.5.0"