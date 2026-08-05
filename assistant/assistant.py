
import time

t = time.time()
from voice.recorder import record
print(f"recorder import: {time.time()-t:.2f}s")

t = time.time()
from voice.speech_to_text import transcribe
print(f"speech_to_text import: {time.time()-t:.2f}s")

t = time.time()
from voice.text_to_speech import speak
print(f"text_to_speech import: {time.time()-t:.2f}s")

t = time.time()
from agent.agent import process
print(f"agent import: {time.time()-t:.2f}s")

history = []


def run():
    global history

    print("=" * 50)
    print("🤖 XENOVA Voice Assistant")
    print("Press Enter to start recording.")
    print("Type 'exit' after recording to quit.")
    print("=" * 50)

    while True:
        input("\nPress Enter to start recording...")

        print("\n🎤 Recording...")
        audio = record()

        start = time.time()
        print("📝 Transcribing...")
        user = transcribe(audio)
        print(f"⚡ Whisper: {time.time() - start:.2f}s")

        if not user:
            print("❌ I couldn't hear anything.")
            continue

        print(f"\n🧑 You: {user}")

        if user.lower() in ["exit", "quit", "stop"]:
            print("👋 Goodbye!")
            break

        start = time.time()
        print("🧠 Thinking...")
        reply, history = process(user, history)
        print(f"⚡ LLM: {time.time() - start:.2f}s")

        print(f"\n🤖 Xenova: {reply}")

        start = time.time()
        print("🔊 Speaking...")
        speak(reply)
        print(f"⚡ XTTS: {time.time() - start:.2f}s")


if __name__ == "__main__":
    run()