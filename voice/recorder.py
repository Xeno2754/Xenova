import time

import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 480  # 30 ms
MAX_RECORD_SECONDS = 15.0
SILENCE_AFTER_SPEECH = 1.2
CALIBRATION_SECONDS = 0.35
MIN_SPEECH_SECONDS = 0.25


def _rms(audio):
    audio = np.asarray(audio, dtype=np.float32)
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio))))


def record(filename="temp.wav", duration=None):
    """Record until the speaker stops talking instead of always waiting 5 seconds.

    The microphone starts immediately. Ambient noise is measured briefly, then
    recording ends after ~1.2 seconds of silence following detected speech.
    A 15-second safety limit prevents the assistant from listening forever.
    """
    print("\n🎤 Speak...")
    print("🎙️ Listening for speech...")

    max_seconds = float(duration) if duration else MAX_RECORD_SECONDS
    calibration_blocks = max(1, int(CALIBRATION_SECONDS * SAMPLE_RATE / BLOCK_SIZE))

    frames = []
    noise_levels = []

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=BLOCK_SIZE,
    ) as stream:
        # Brief ambient-noise calibration.
        for _ in range(calibration_blocks):
            data, _ = stream.read(BLOCK_SIZE)
            data = np.asarray(data, dtype=np.float32).copy()
            frames.append(data)
            noise_levels.append(_rms(data))

        noise_floor = float(np.median(noise_levels)) if noise_levels else 0.005
        threshold = max(0.012, noise_floor * 2.8)

        speech_started = False
        speech_time = 0.0
        silence_time = 0.0
        elapsed = CALIBRATION_SECONDS
        last_log = 0.0

        while elapsed < max_seconds:
            data, _ = stream.read(BLOCK_SIZE)
            data = np.asarray(data, dtype=np.float32).copy()
            frames.append(data)

            block_seconds = BLOCK_SIZE / SAMPLE_RATE
            elapsed += block_seconds
            level = _rms(data)

            if level >= threshold:
                if not speech_started:
                    print("🗣️ Speech detected")
                speech_started = True
                speech_time += block_seconds
                silence_time = 0.0
            elif speech_started:
                silence_time += block_seconds

                if (
                    silence_time >= SILENCE_AFTER_SPEECH
                    and speech_time >= MIN_SPEECH_SECONDS
                ):
                    print("⏹️ Silence detected — processing...")
                    break

            if elapsed - last_log >= 3.0:
                print(f"🎙️ Listening... {elapsed:.1f}s")
                last_log = elapsed

    audio = np.concatenate(frames, axis=0)
    sf.write(filename, audio, SAMPLE_RATE)

    if speech_started:
        print(f"🎤 Recording complete: {elapsed:.2f}s")
    else:
        print("⚠️ No speech detected during listening window.")

    return filename
