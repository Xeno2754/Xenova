import time
import threading

from voice.recorder import record
from voice.speech_to_text import transcribe
from voice.text_to_speech import speak, speak_stream
from agent.agent import process

history = []


class XenovaController:

    def __init__(self, interface=None):
        self.interface = interface
        self.running = True
        self.voice_running = False

    def set_status(self, status, message=None):
        if not self.interface:
            return
        try:
            self.interface.root.after(
                0,
                lambda: self.interface.set_status(status, message)
            )
        except Exception as e:
            print(f"UI status error: {e}")

    def add_message(self, sender, message):
        if not self.interface:
            return
        try:
            self.interface.root.after(
                0,
                lambda: self.interface.add_message(sender, message)
            )
        except Exception as e:
            print(f"UI message error: {e}")

    def _speak_response(self, response):
        """Use sentence streaming for voice replies."""
        self.set_status("SPEAKING", "XENOVA is speaking...")
        print("🔊 Speaking...")
        speak_stream(str(response))

    def handle_text(self, text):
        global history
        if not text or not text.strip():
            return
        try:
            self.add_message("YOU", text)
            self.set_status("THINKING", "Processing your request...")
            print(f"\n🧑 You: {text}")
            print("🧠 Thinking...")

            start = time.time()
            response, history = process(text, history)
            print(f"⚡ Agent: {time.time() - start:.2f}s")

            if response:
                print(f"🤖 Xenova: {response}")
                self.add_message("XENOVA", str(response))
                self._speak_response(response)

            self.set_status("IDLE", "Ready for your command")
        except Exception as e:
            print(f"❌ Text error: {e}")
            self.add_message("XENOVA", f"Error: {e}")
            self.set_status("IDLE", "Error")

    def handle_voice(self, *args, **kwargs):
        global history
        if self.voice_running:
            print("⚠️ Voice already running.")
            return

        self.voice_running = True
        try:
            self.set_status("LISTENING", "XENOVA is listening...")
            print("\n🎤 Recording...")
            start = time.time()
            audio = record()
            print(f"⚡ Recording: {time.time() - start:.2f}s")

            self.set_status("THINKING", "Transcribing...")
            print("📝 Transcribing...")
            start = time.time()
            user_text = transcribe(audio)
            print(f"⚡ Whisper: {time.time() - start:.2f}s")

            if not user_text:
                print("⚠️ No speech detected.")
                self.set_status("IDLE", "I didn't hear anything")
                return

            print(f"\n🧑 You: {user_text}")
            self.add_message("YOU", user_text)
            self.set_status("THINKING", "Thinking...")
            print("🧠 Thinking...")

            start = time.time()
            response, history = process(user_text, history)
            print(f"⚡ Agent: {time.time() - start:.2f}s")

            if response:
                print(f"🤖 Xenova: {response}")
                self.add_message("XENOVA", str(response))
                self._speak_response(response)
            else:
                print("⚠️ No response from agent.")

            self.set_status("IDLE", "Ready for your command")

        except Exception as e:
            print(f"❌ XENOVA voice error: {e}")
            self.add_message("XENOVA", f"Voice error: {e}")
            self.set_status("IDLE", "Voice error")
        finally:
            self.voice_running = False

    def start_voice(self, *args, **kwargs):
        print("🎤 Voice button pressed")
        if self.voice_running:
            print("⚠️ Voice already running.")
            return
        threading.Thread(target=self.handle_voice, daemon=True).start()


def run():
    from interface import XenovaInterface

    controller = XenovaController()
    interface = XenovaInterface(on_command=controller.handle_text)
    controller.interface = interface

    def voice_callback(*args, **kwargs):
        controller.start_voice(*args, **kwargs)

    interface.start_voice = voice_callback

    # Preload XTTS while the UI is already starting.
    def preload_voice_models():
        try:
            from voice.speech_to_text import get_model
            start = time.time()
            get_model()
            print(f"✅ Whisper background preload finished in {time.time() - start:.2f}s")
        except Exception as e:
            print(f"⚠️ Whisper preload failed: {e}")

        try:
            from voice.text_to_speech import preload_tts
            start = time.time()
            preload_tts()
            print(f"✅ XTTS background preload finished in {time.time() - start:.2f}s")
        except Exception as e:
            print(f"⚠️ XTTS preload failed: {e}")

    threading.Thread(target=preload_voice_models, daemon=True).start()

    print("=" * 50)
    print("🤖 XENOVA")
    print("Personal AI Interface")
    print("=" * 50)

    interface.run()


if __name__ == "__main__":
    run()
