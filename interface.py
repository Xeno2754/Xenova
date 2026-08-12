
import tkinter as tk
import threading
import math


class XenovaInterface:

    BG = "#05070d"
    PANEL = "#0b101a"
    PANEL_2 = "#0e1522"
    TEXT = "#f4f7ff"
    MUTED = "#69758a"
    BLUE = "#55a8ff"
    PURPLE = "#9b7cff"
    GREEN = "#55e39a"
    GOLD = "#f5c451"
    RED = "#ff5f6d"

    def __init__(
        self,
        on_command=None,
        on_voice=None
    ):
        self.on_command = on_command
        self.on_voice = on_voice

        self.root = tk.Tk()
        self.root.title("XENOVA — Personal AI")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=self.BG)

        self.status = "IDLE"
        self.pulse = 0
        self.processing = False

        self.setup_ui()
        self.animate()

    # ==================================================
    # UI
    # ==================================================

    def setup_ui(self):

        # ---------- TOP BAR ----------

        top = tk.Frame(
            self.root,
            bg=self.BG
        )
        top.pack(
            fill="x",
            padx=35,
            pady=(25, 0)
        )

        title = tk.Label(
            top,
            text="XENOVA",
            font=("Segoe UI", 25, "bold"),
            fg=self.TEXT,
            bg=self.BG
        )
        title.pack(side="left")

        subtitle = tk.Label(
            top,
            text="   PERSONAL AI SYSTEM",
            font=("Segoe UI", 9, "bold"),
            fg=self.MUTED,
            bg=self.BG
        )
        subtitle.pack(
            side="left",
            pady=(9, 0)
        )

        self.status_label = tk.Label(
            top,
            text="● SYSTEM READY",
            font=("Segoe UI", 9, "bold"),
            fg=self.GREEN,
            bg=self.BG
        )
        self.status_label.pack(
            side="right",
            pady=8
        )

        # ---------- MAIN ----------

        main = tk.Frame(
            self.root,
            bg=self.BG
        )

        main.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

        # ---------- LEFT ----------

        left = tk.Frame(
            main,
            bg=self.BG
        )

        left.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            left,
            width=430,
            height=430,
            bg=self.BG,
            highlightthickness=0
        )

        self.canvas.pack(
            pady=(5, 0)
        )

        self.draw_core()

        self.action_label = tk.Label(
            left,
            text="XENOVA ONLINE",
            font=("Segoe UI", 18, "bold"),
            fg=self.TEXT,
            bg=self.BG
        )

        self.action_label.pack()

        self.description_label = tk.Label(
            left,
            text="Ready for your command",
            font=("Segoe UI", 10),
            fg=self.MUTED,
            bg=self.BG
        )

        self.description_label.pack(
            pady=(5, 15)
        )

        # ---------- VOICE BUTTON ----------

        self.voice_button = tk.Button(
            left,
            text="🎙  TALK TO XENOVA",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT,
            bg="#121c2d",
            activebackground="#1b2a43",
            activeforeground=self.TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=28,
            pady=12,
            command=self.start_voice
        )

        self.voice_button.pack(
            pady=(5, 15)
        )

        # ---------- RIGHT / CHAT ----------

        right = tk.Frame(
            main,
            bg=self.PANEL,
            highlightbackground="#182235",
            highlightthickness=1
        )

        right.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(20, 0)
        )

        chat_title = tk.Label(
            right,
            text="CONVERSATION",
            font=("Segoe UI", 10, "bold"),
            fg=self.MUTED,
            bg=self.PANEL
        )

        chat_title.pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        self.chat = tk.Text(
            right,
            bg=self.PANEL,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            wrap="word",
            state="disabled"
        )

        self.chat.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        self.add_message(
            "XENOVA",
            "Systems online. How can I help?"
        )

        # ---------- TEXT INPUT ----------

        input_frame = tk.Frame(
            right,
            bg=self.PANEL_2,
            highlightbackground="#202c40",
            highlightthickness=1
        )

        input_frame.pack(
            fill="x",
            padx=15,
            pady=15
        )

        self.input_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg=self.PANEL_2,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            bd=0
        )

        self.input_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15,
            pady=14
        )

        self.input_entry.insert(
            0,
            "Ask XENOVA anything..."
        )

        self.input_entry.bind(
            "<FocusIn>",
            self.clear_placeholder
        )

        self.input_entry.bind(
            "<Return>",
            self.submit_text
        )

        send = tk.Button(
            input_frame,
            text="➤",
            font=("Segoe UI", 13, "bold"),
            fg=self.TEXT,
            bg="#172338",
            activebackground="#243653",
            activeforeground=self.TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.submit_text
        )

        send.pack(
            side="right",
            padx=6,
            pady=6
        )

        # ---------- SYSTEM BAR ----------

        bottom = tk.Frame(
            self.root,
            bg=self.BG
        )

        bottom.pack(
            fill="x",
            padx=35,
            pady=(0, 20)
        )

        self.create_status(
            bottom,
            "AI",
            "ONLINE"
        )

        self.create_status(
            bottom,
            "VISION",
            "READY"
        )

        self.create_status(
            bottom,
            "BROWSER",
            "READY"
        )

        self.create_status(
            bottom,
            "VOICE",
            "READY"
        )

    # ==================================================
    # CORE
    # ==================================================

    def draw_core(self):

        self.canvas.delete("all")

        cx = 215
        cy = 215

        for radius, outline, width in [
            (185, "#101b2d", 1),
            (160, "#15243b", 2),
            (135, "#1b3352", 2),
            (108, "#24476d", 2),
        ]:

            self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                outline=outline,
                width=width
            )

        glow = 72 + int(
            8 * math.sin(self.pulse / 5)
        )

        self.canvas.create_oval(
            cx - glow,
            cy - glow,
            cx + glow,
            cy + glow,
            fill="#101d31",
            outline=self.core_color(),
            width=2
        )

        inner = 48 + int(
            5 * math.sin(self.pulse / 4)
        )

        self.canvas.create_oval(
            cx - inner,
            cy - inner,
            cx + inner,
            cy + inner,
            fill="#172c49",
            outline=self.core_color(),
            width=2
        )

        core = 22 + int(
            4 * math.sin(self.pulse / 3)
        )

        self.canvas.create_oval(
            cx - core,
            cy - core,
            cx + core,
            cy + core,
            fill=self.core_color(),
            outline=""
        )

    def core_color(self):

        if self.status == "LISTENING":
            return self.BLUE

        if self.status == "THINKING":
            return self.PURPLE

        if self.status == "SPEAKING":
            return self.GOLD

        if self.status == "ERROR":
            return self.RED

        return self.BLUE

    # ==================================================
    # ANIMATION
    # ==================================================

    def animate(self):

        self.pulse += 1

        self.draw_core()

        if self.status == "LISTENING":

            self.action_label.config(
                text="LISTENING..."
            )

        elif self.status == "THINKING":

            self.action_label.config(
                text="THINKING..."
            )

        elif self.status == "SPEAKING":

            self.action_label.config(
                text="SPEAKING..."
            )

        elif self.status == "ERROR":

            self.action_label.config(
                text="ERROR"
            )

        else:

            self.action_label.config(
                text="XENOVA ONLINE"
            )

        self.root.after(
            50,
            self.animate
        )

    # ==================================================
    # STATUS
    # ==================================================

    def set_status(
        self,
        status,
        message=None
    ):

        self.status = status.upper()

        if self.status == "LISTENING":

            self.status_label.config(
                text="● LISTENING",
                fg=self.BLUE
            )

            self.description_label.config(
                text="Speak now..."
            )

        elif self.status == "THINKING":

            self.status_label.config(
                text="● THINKING",
                fg=self.PURPLE
            )

            self.description_label.config(
                text=message or "Processing your request..."
            )

        elif self.status == "SPEAKING":

            self.status_label.config(
                text="● SPEAKING",
                fg=self.GOLD
            )

            self.description_label.config(
                text="XENOVA is responding..."
            )

        elif self.status == "ERROR":

            self.status_label.config(
                text="● ERROR",
                fg=self.RED
            )

            self.description_label.config(
                text=message or "Something went wrong."

            )

        else:

            self.status_label.config(
                text="● SYSTEM READY",
                fg=self.GREEN
            )

            self.description_label.config(
                text=message or "Ready for your command"
            )

    # ==================================================
    # CHAT
    # ==================================================

    def add_message(
        self,
        sender,
        message
    ):

        if not message:
            return

        def update():

            self.chat.config(
                state="normal"
            )

            self.chat.insert(
                tk.END,
                f"\n{sender}\n",
                ("sender",)
            )

            self.chat.insert(
                tk.END,
                str(message) + "\n"
            )

            self.chat.tag_config(
                "sender",
                foreground=self.BLUE,
                font=("Segoe UI", 9, "bold")
            )

            self.chat.see(
                tk.END
            )

            self.chat.config(
                state="disabled"
            )

        self.root.after(
            0,
            update
        )

    # ==================================================
    # TEXT INPUT
    # ==================================================

    def clear_placeholder(
        self,
        event=None
    ):

        if self.input_entry.get() == "Ask XENOVA anything...":

            self.input_entry.delete(
                0,
                tk.END
            )

    def submit_text(
        self,
        event=None
    ):

        text = self.input_entry.get().strip()

        if (
            not text
            or text == "Ask XENOVA anything..."
            or self.processing
        ):
            return

        self.input_entry.delete(
            0,
            tk.END
        )

        self.add_message(
            "YOU",
            text
        )

        self.set_status(
            "THINKING"
        )

        self.processing = True

        if self.on_command:

            threading.Thread(
                target=self.command_worker,
                args=(text,),
                daemon=True
            ).start()

    def command_worker(
        self,
        text
    ):

        try:

            result = self.on_command(text)

            if result:
                self.add_message(
                    "XENOVA",
                    result
                )

            self.root.after(
                0,
                lambda: self.set_status("IDLE")
            )

        except Exception as e:

         error_message = str(e)

         print(
        f"XENOVA voice error: {error_message}"
    )

         self.add_message(
        "XENOVA",
        f"Voice error: {error_message}"
    )

         self.root.after(
        0,
        lambda msg=error_message: self.set_status(
            "ERROR",
            msg
        )
    )
        finally:

            self.processing = False

    # ==================================================
    # VOICE
    # ==================================================

    def start_voice(self):

        if self.processing:
            return

        self.processing = True

        self.set_status(
            "LISTENING"
        )

        self.voice_button.config(
            state="disabled",
            text="🎙  LISTENING..."
        )

        threading.Thread(
            target=self.voice_worker,
            daemon=True
        ).start()

    def voice_worker(self):

        try:

            if not self.on_voice:

                raise RuntimeError(
                    "Voice callback is not connected."
                )

            # The backend handles:
            # recording
            # transcription
            # planning
            # tools
            # LLM response
            # TTS

            result = self.on_voice(
                self.update_voice_status
            )

            if result:

                self.add_message(
                    "XENOVA",
                    result
                )

            self.root.after(
                0,
                lambda: self.set_status(
                    "IDLE"
                )
            )

        except Exception as e:

            print(
                f"XENOVA voice error: {e}"
            )

            self.add_message(
                "XENOVA",
                f"Voice error: {e}"
            )

            self.root.after(
                0,
                lambda: self.set_status(
                    "ERROR",
                    str(e)
                )
            )

        finally:

            self.processing = False

            self.root.after(
                0,
                lambda: self.voice_button.config(
                    state="normal",
                    text="🎙  TALK TO XENOVA"
                )
            )

    def update_voice_status(
        self,
        status,
        message=None
    ):

        self.root.after(
            0,
            lambda: self.set_status(
                status,
                message
            )
        )

    # ==================================================
    # SYSTEM BAR
    # ==================================================

    def create_status(
        self,
        parent,
        name,
        value
    ):

        frame = tk.Frame(
            parent,
            bg=self.PANEL
        )

        frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=4
        )

        tk.Label(
            frame,
            text=name,
            font=("Segoe UI", 8, "bold"),
            fg=self.MUTED,
            bg=self.PANEL
        ).pack(
            pady=(7, 0)
        )

        tk.Label(
            frame,
            text="● " + value,
            font=("Segoe UI", 8),
            fg=self.GREEN,
            bg=self.PANEL
        ).pack(
            pady=(2, 7)
        )

    # ==================================================
    # RUN
    # ==================================================

    def run(self):

        self.root.mainloop()


if __name__ == "__main__":

    app = XenovaInterface()

    app.run()

