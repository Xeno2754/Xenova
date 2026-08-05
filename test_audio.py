import sounddevice as sd
import soundfile as sf

audio, samplerate = sf.read("output.wav")

sd.play(audio, samplerate)
sd.wait()

print("Finished playing.")