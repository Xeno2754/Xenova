import time
import threading

from voice.recorder import record
from voice.speech_to_text import transcribe
from voice.text_to_speech import speak
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
                lambda: self.interface.set_status(
                    status,
                    message
                )
            )
        except Exception as e:
            print(f"UI status error: {e}")

    def add_message(self, sender, message):

        if not self.interface:
            return

        try:
            self.interface.root.after(
                0,
                lambda: self.interface.add_message(
                    sender,
                    message
                )
            )
        except Exception as e:
            print(f"UI message error: {e}")

    # ==========================================
    # TEXT
    # ==========================================

    def handle_text(self, text):

        global history

        if not text or not text.strip():
            return

        try:

            self.add_message("YOU", text)

            self.set_status(
                "THINKING",
                "Processing your request..."
            )

            print(f"\n🧑 You: {text}")
            print("🧠 Thinking...")

            start = time.time()

            response, history = process(
                text,
                history
            )

            print(
                f"⚡ Agent: {time.time() - start:.2f}s"
            )

            if response:

                print(f"🤖 Xenova: {response}")

                self.add_message(
                    "XENOVA",
                    str(response)
                )

                self.set_status(
                    "SPEAKING",
                    "XENOVA is responding..."
                )

                speak(str(response))

            self.set_status(
                "IDLE",
                "Ready for your command"
            )

        except Exception as e:

            print(f"❌ Text error: {e}")

            self.add_message(
                "XENOVA",
                f"Error: {e}"
            )

            self.set_status(
                "IDLE",
                "Error"
            )

    # ==========================================
    # VOICE
    # ==========================================

    def handle_voice(self, *args, **kwargs):

        global history

        if self.voice_running:
            print("⚠️ Voice already running.")
            return

        self.voice_running = True

        try:

            # LISTENING
            self.set_status(
                "LISTENING",
                "XENOVA is listening..."
            )

            print("\n🎤 Recording...")

            start = time.time()

            audio = record()

            print(
                f"⚡ Recording: "
                f"{time.time() - start:.2f}s"
            )

            # TRANSCRIBING
            self.set_status(
                "THINKING",
                "Transcribing..."
            )

            print("📝 Transcribing...")

            start = time.time()

            user_text = transcribe(audio)

            print(
                f"⚡ Whisper: "
                f"{time.time() - start:.2f}s"
            )

            if not user_text:

                print("⚠️ No speech detected.")

                self.set_status(
                    "IDLE",
                    "I didn't hear anything"
                )

                return

            # USER MESSAGE
            print(f"\n🧑 You: {user_text}")

            self.add_message(
                "YOU",
                user_text
            )

            # THINKING
            self.set_status(
                "THINKING",
                "Thinking..."
            )

            print("🧠 Thinking...")

            start = time.time()

            response, history = process(
                user_text,
                history
            )

            print(
                f"⚡ Agent: "
                f"{time.time() - start:.2f}s"
            )

            # RESPONSE
            if response:

                print(f"🤖 Xenova: {response}")

                self.add_message(
                    "XENOVA",
                    str(response)
                )

                # SPEAKING
                self.set_status(
                    "SPEAKING",
                    "XENOVA is speaking..."
                )

                print("🔊 Speaking...")

                speak(str(response))

            else:

                print("⚠️ No response from agent.")

            self.set_status(
                "IDLE",
                "Ready for your command"
            )

        except Exception as e:

            print(f"❌ XENOVA voice error: {e}")

            self.add_message(
                "XENOVA",
                f"Voice error: {e}"
            )

            self.set_status(
                "IDLE",
                "Voice error"
            )

        finally:

            self.voice_running = False

    # ==========================================
    # VOICE BUTTON CALLBACK
    # ==========================================

    def start_voice(self, *args, **kwargs):

        print("🎤 Voice button pressed")

        if self.voice_running:
            print("⚠️ Voice already running.")
            return

        threading.Thread(
            target=self.handle_voice,
            daemon=True
        ).start()


# ==========================================
# APPLICATION
# ==========================================

def run():

    from interface import XenovaInterface

    controller = XenovaController()

    interface = XenovaInterface(
        on_command=controller.handle_text
    )

    controller.interface = interface

    # IMPORTANT:
    # UI may pass an argument to this callback.
    # Accept everything and ignore it.

    def voice_callback(*args, **kwargs):

        controller.start_voice(
            *args,
            **kwargs
        )

    interface.start_voice = voice_callback

    print("=" * 50)
    print("🤖 XENOVA")
    print("Personal AI Interface")
    print("=" * 50)

    interface.run()


if __name__ == "__main__":
    run()