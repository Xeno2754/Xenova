import tkinter as tk
import threading
import math
import random


class XenovaInterface:
    """Neon glass XENOVA interface inspired by the supplied reference image."""

    BG_TOP = "#05091b"
    BG_BOTTOM = "#09b8b7"
    GLASS = "#071225"
    GLASS_EDGE = "#3d7181"
    TEXT = "#e9fbff"
    MUTED = "#74869a"
    CYAN = "#20f4ed"
    CYAN_SOFT = "#56d9e1"
    PURPLE = "#8b78ff"
    GOLD = "#ffd56a"
    RED = "#ff6070"

    def __init__(self, on_command=None, on_voice=None):
        self.on_command = on_command
        self.on_voice = on_voice

        self.root = tk.Tk()
        self.root.title("XENOVA")
        self.root.geometry("1100x760")
        self.root.minsize(900, 650)
        self.root.configure(bg=self.BG_TOP)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.status = "IDLE"
        self.processing = False
        self.pulse = 0
        self.wave_phase = 0
        self.messages = []

        self.setup_ui()
        self.animate()

    # ==================================================
    # WINDOW / BACKGROUND
    # ==================================================

    def setup_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            bg=self.BG_TOP,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Button-1>", self.canvas_click)

        self.draw_background()
        self.draw_panel()
        self.draw_navigation()
        self.draw_controls()
        self.draw_orb()
        self.draw_bottom_bar()

        # Invisible/overlaid entry: visually integrated into the glass UI.
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            self.root,
            textvariable=self.input_var,
            font=("Segoe UI", 10),
            fg=self.TEXT,
            bg="#11233a",
            insertbackground=self.CYAN,
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.input_entry.place(relx=0.725, rely=0.505, relwidth=0.13, height=30)
        self.input_entry.bind("<Return>", self.submit_text)
        self.input_entry.bind("<FocusIn>", self.clear_placeholder)
        self.input_entry.insert(0, "Ask XENOVA")

        self.add_message("XENOVA", "Systems online. How can I help?")

    def draw_background(self):
        self.canvas.delete("background")
        w = max(self.root.winfo_width(), 900)
        h = max(self.root.winfo_height(), 650)

        steps = 80
        for i in range(steps):
            t = i / (steps - 1)
            # dark navy at top -> saturated cyan/teal at bottom
            r = int(5 * (1 - t) + 5 * t)
            g = int(9 * (1 - t) + 188 * t)
            b = int(27 * (1 - t) + 185 * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(h * i / steps)
            y1 = int(h * (i + 1) / steps) + 1
            self.canvas.create_rectangle(0, y0, w, y1, fill=color, outline="", tags="background")

        # dark vignette bands
        self.canvas.create_rectangle(0, 0, w, int(h * 0.35), fill="#05091b", outline="", tags="background")
        self.canvas.tag_lower("background")

    # ==================================================
    # GLASS PANEL
    # ==================================================

    def rounded_rect(self, x1, y1, x2, y2, radius=28, fill="", outline="", width=1, tags=None):
        # Smooth rounded rectangle using arcs + rectangles.
        self.canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, 180, 90, fill=fill, outline=outline, width=width, tags=tags)
        self.canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, 90, 90, fill=fill, outline=outline, width=width, tags=tags)
        self.canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, 180, -90, fill=fill, outline=outline, width=width, tags=tags)
        self.canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, 0, -90, fill=fill, outline=outline, width=width, tags=tags)
        self.canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=fill, outline="", tags=tags)
        self.canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=fill, outline="", tags=tags)
        if outline:
            # clean border using a second transparent-ish line made from arcs
            self.canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, 90, 90, style="arc", outline=outline, width=width, tags=tags)
            self.canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, 0, 90, style="arc", outline=outline, width=width, tags=tags)
            self.canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, 180, 90, style="arc", outline=outline, width=width, tags=tags)
            self.canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, 270, 90, style="arc", outline=outline, width=width, tags=tags)
            self.canvas.create_line(x1 + radius, y1, x2 - radius, y1, fill=outline, width=width, tags=tags)
            self.canvas.create_line(x1 + radius, y2, x2 - radius, y2, fill=outline, width=width, tags=tags)
            self.canvas.create_line(x1, y1 + radius, x1, y2 - radius, fill=outline, width=width, tags=tags)
            self.canvas.create_line(x2, y1 + radius, x2, y2 - radius, fill=outline, width=width, tags=tags)

    def draw_panel(self):
        self.canvas.delete("panel")
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w < 100:
            return

        x1, y1 = 88, 238
        x2, y2 = w - 88, h - 108

        # subtle outer glow
        self.rounded_rect(x1 - 4, y1 - 4, x2 + 4, y2 + 4, 30, fill="#07182b", outline="#17465b", width=1, tags="panel")
        self.rounded_rect(x1, y1, x2, y2, 28, fill="#061426", outline="#4a7784", width=1, tags="panel")

        # top glass highlight
        self.canvas.create_line(x1 + 35, y1 + 1, x2 - 35, y1 + 1, fill="#76aeb6", width=1, tags="panel")

    # ==================================================
    # NAVIGATION
    # ==================================================

    def draw_navigation(self):
        self.canvas.delete("nav")
        w = self.root.winfo_width()
        if w < 100:
            return

        # logo orb
        self.canvas.create_oval(115, 264, 138, 287, fill="#19aeb9", outline="#42f5ee", width=1, tags="nav")
        for i in range(3):
            self.canvas.create_line(149, 268 + i * 6, 181 - i * 6, 268 + i * 6, fill="#8295a4", width=2, tags="nav")

        # nav labels
        self.text(615, 274, "Home", 9, self.MUTED, "nav")
        self.text(700, 274, "Systems", 9, self.MUTED, "nav")
        self.text(785, 274, "Memory", 9, self.MUTED, "nav")

        # active pill
        self.rounded_rect(805, 258, 915, 291, 22, fill="#12cfc9", outline="#72fff9", width=1, tags="nav")
        self.text(860, 274, "XENOVA", 9, "#eaffff", "nav", anchor="center")

    # ==================================================
    # RIGHT CONTROLS
    # ==================================================

    def draw_controls(self):
        self.canvas.delete("controls")
        w = self.root.winfo_width()
        if w < 100:
            return

        x = w - 255

        self.rounded_rect(x - 8, 382, w - 118, 412, 16, fill="#1a334a", outline="#31566a", width=1, tags="controls")
        self.text(x + 20, 397, "VOICE", 8, self.MUTED, "controls")
        self.text(w - 140, 397, "›", 16, self.TEXT, "controls", anchor="center")

        # tiny equalizer / status lines
        for i in range(3):
            y = 445 + i * 8
            self.canvas.create_line(x - 30, y, w - 150, y, fill="#5c7c8b", width=1, tags="controls")
            self.canvas.create_line(x + 4, y, x + 4 + (35 + i * 12), y, fill="#3ee8e2", width=1, tags="controls")

        self.text(w - 106, 445, "AI", 8, self.MUTED, "controls")
        self.text(w - 106, 469, "READY", 8, self.CYAN, "controls")

    # ==================================================
    # ORB + WAVEFORM
    # ==================================================

    def draw_orb(self):
        self.canvas.delete("orb")
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w < 100:
            return

        cx = w * 0.50
        cy = h * 0.60

        # waveform behind orb
        points = []
        for i in range(110):
            x = 105 + i * ((w - 210) / 109)
            envelope = max(0.25, 1.0 - abs(x - cx) / (w * 0.43))
            wave = (
                math.sin(i * 0.72 + self.wave_phase) * 22
                + math.sin(i * 1.91 + self.wave_phase * 1.7) * 11
                + math.sin(i * 3.3) * 5
            ) * envelope
            points.extend([x, cy + wave])

        self.canvas.create_line(*points, fill="#2ee7df", width=1, smooth=True, tags="orb")

        # vertical waveform bars
        for i in range(76):
            x = 105 + i * ((w - 210) / 75)
            env = max(0.15, 1 - abs(x - cx) / (w * 0.45))
            amp = (18 + 32 * abs(math.sin(i * 1.17 + self.wave_phase))) * env
            self.canvas.create_line(x, cy - amp, x, cy + amp, fill="#19c9d0", width=1, tags="orb")

        # electric rays
        random.seed(7 + self.pulse // 8)
        for ray in range(22):
            a = random.random() * math.pi * 2
            r0 = 94 + random.random() * 12
            r1 = r0 + 18 + random.random() * 35
            x0 = cx + math.cos(a) * r0
            y0 = cy + math.sin(a) * r0
            x1 = cx + math.cos(a) * r1
            y1 = cy + math.sin(a) * r1
            self.canvas.create_line(x0, y0, x1, y1, fill="#5ffef7", width=1, tags="orb")

        # glow rings
        for r, color, width in [
            (116, "#0b6470", 2),
            (108, "#13aeb3", 2),
            (101, "#53f9f1", 2),
        ]:
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color, width=width, tags="orb")

        # glass sphere
        self.canvas.create_oval(cx-93, cy-93, cx+93, cy+93, fill="#0b4d5b", outline="#8cffff", width=2, tags="orb")
        self.canvas.create_oval(cx-82, cy-82, cx+82, cy+82, outline="#58f4ef", width=1, tags="orb")
        self.canvas.create_oval(cx-61, cy-61, cx+61, cy+61, outline="#2cd5d5", width=1, tags="orb")

        # internal cracked energy
        for k in range(12):
            a = k * math.pi / 6 + self.pulse * 0.008
            length = 42 + 18 * math.sin(k * 2.4 + self.pulse * 0.03)
            x0 = cx + math.cos(a) * 5
            y0 = cy + math.sin(a) * 5
            xm = cx + math.cos(a) * length * 0.52 + math.sin(a * 5) * 7
            ym = cy + math.sin(a) * length * 0.52 + math.cos(a * 4) * 7
            x1 = cx + math.cos(a) * length
            y1 = cy + math.sin(a) * length
            self.canvas.create_line(x0, y0, xm, ym, x1, y1, fill="#7ffff8", width=1, tags="orb")

        # highlights / reflection blocks
        for dx, dy, s in [(-53, -35, 15), (42, -48, 18), (-62, 24, 12), (35, 39, 14)]:
            self.canvas.create_polygon(
                cx+dx, cy+dy,
                cx+dx+s, cy+dy+7,
                cx+dx+s+6, cy+dy+s,
                cx+dx+4, cy+dy+s-4,
                fill="#c4ffff", outline="", tags="orb"
            )

        # central energy core
        core = 14 + int(3 * math.sin(self.pulse / 4))
        self.canvas.create_oval(cx-core, cy-core, cx+core, cy+core, fill="#9ffff8", outline="#ffffff", width=1, tags="orb")

        self.text(cx, cy + 128, self.status_text(), 10, self.TEXT, "orb", anchor="center")

    def status_text(self):
        return {
            "LISTENING": "LISTENING",
            "THINKING": "PROCESSING",
            "SPEAKING": "RESPONDING",
            "ERROR": "SYSTEM ERROR",
        }.get(self.status, "SYSTEMS ONLINE")

    # ==================================================
    # BOTTOM BAR
    # ==================================================

    def draw_bottom_bar(self):
        self.canvas.delete("bottom")
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w < 100:
            return

        y = h - 78
        self.text(115, y, "XENOVA CORE", 8, self.MUTED, "bottom")
        self.text(115, y + 18, "LOCAL • PRIVATE • ONLINE", 8, self.CYAN_SOFT, "bottom")

        self.text(w - 145, y, "◉", 12, self.CYAN, "bottom")
        self.text(w - 112, y, "●", 8, self.MUTED, "bottom")
        self.text(w - 84, y, "◉", 11, self.TEXT, "bottom")

    # ==================================================
    # DRAW HELPERS
    # ==================================================

    def text(self, x, y, value, size=10, color=None, tags=None, anchor="center"):
        self.canvas.create_text(
            x, y,
            text=value,
            fill=color or self.TEXT,
            font=("Segoe UI", size, "bold" if size >= 9 else "normal"),
            anchor=anchor,
            tags=tags
        )

    def redraw(self):
        self.draw_background()
        self.draw_panel()
        self.draw_navigation()
        self.draw_controls()
        self.draw_orb()
        self.draw_bottom_bar()

    # ==================================================
    # ANIMATION
    # ==================================================

    def animate(self):
        if not self.root.winfo_exists():
            return
        self.pulse += 1
        self.wave_phase += 0.16
        self.draw_orb()
        self.root.after(50, self.animate)

    # ==================================================
    # STATUS
    # ==================================================

    def set_status(self, status, message=None):
        self.status = str(status).upper()
        self.redraw()

    def update_voice_status(self, status, message=None):
        self.set_status(status, message)

    # ==================================================
    # CHAT / MESSAGE OVERLAY
    # ==================================================

    def add_message(self, sender, message):
        if not message:
            return
        self.messages.append((str(sender), str(message)))
        self.messages = self.messages[-3:]
        self.root.after(0, self.draw_message_overlay)

    def draw_message_overlay(self):
        self.canvas.delete("messages")
        if not self.messages:
            return

        w = self.root.winfo_width()
        h = self.root.winfo_height()
        latest_sender, latest_message = self.messages[-1]
        msg = latest_message.replace("\n", " ")
        if len(msg) > 74:
            msg = msg[:71] + "..."

        # subtle glass message capsule on the lower-right side
        x1, y1 = w - 395, h - 170
        x2, y2 = w - 115, h - 112
        self.rounded_rect(x1, y1, x2, y2, 18, fill="#0a1d30", outline="#2c5e6c", width=1, tags="messages")
        self.text(x1 + 15, y1 + 15, latest_sender.upper(), 7, self.CYAN, "messages", anchor="w")
        self.canvas.create_text(
            x1 + 15, y1 + 34,
            text=msg,
            fill=self.TEXT,
            font=("Segoe UI", 8),
            anchor="w",
            width=x2-x1-30,
            tags="messages"
        )

    # ==================================================
    # INPUT / VOICE
    # ==================================================

    def clear_placeholder(self, event=None):
        if self.input_entry.get() == "Ask XENOVA":
            self.input_entry.delete(0, tk.END)

    def submit_text(self, event=None):
        text = self.input_entry.get().strip()
        if not text or text == "Ask XENOVA" or self.processing:
            return

        self.input_entry.delete(0, tk.END)
        self.add_message("YOU", text)
        self.processing = True
        self.set_status("THINKING", "Processing your request...")

        if self.on_command:
            threading.Thread(target=self.command_worker, args=(text,), daemon=True).start()

    def command_worker(self, text):
        try:
            result = self.on_command(text)
            if result:
                self.add_message("XENOVA", result)
            self.root.after(0, lambda: self.set_status("IDLE"))
        except Exception as e:
            error_message = str(e)
            print(f"XENOVA text error: {error_message}")
            self.add_message("XENOVA", f"Error: {error_message}")
            self.root.after(0, lambda msg=error_message: self.set_status("ERROR", msg))
        finally:
            self.processing = False

    def start_voice(self):
        if self.processing:
            return

        self.processing = True
        self.set_status("LISTENING", "Speak now...")

        threading.Thread(target=self.voice_worker, daemon=True).start()

    def voice_worker(self):
        try:
            if not self.on_voice:
                raise RuntimeError("Voice callback is not connected.")

            # XenovaController.handle_voice() already updates UI status.
            # Do not pass an extra callback argument.
            result = self.on_voice()

            if result:
                self.add_message("XENOVA", result)

            self.root.after(0, lambda: self.set_status("IDLE"))

        except Exception as e:
            error_message = str(e)
            print(f"XENOVA voice error: {error_message}")
            self.add_message("XENOVA", f"Voice error: {error_message}")
            self.root.after(0, lambda msg=error_message: self.set_status("ERROR", msg))
        finally:
            self.processing = False

    # ==================================================
    # MOUSE / WINDOW
    # ==================================================

    def canvas_click(self, event):
        # Clicking the central orb starts voice interaction.
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        cx, cy = w * 0.50, h * 0.60
        if (event.x - cx) ** 2 + (event.y - cy) ** 2 < 120 ** 2:
            self.start_voice()

    def close(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()
