
import time

start = time.time()

print("Starting...")

# ==================================================
# IMPORTS
# ==================================================

t = time.time()

from assistant.assistant import XenovaController

print(
    f"assistant import: "
    f"{time.time() - t:.2f}s"
)

t = time.time()

from memory.database import init_db

print(
    f"database import: "
    f"{time.time() - t:.2f}s"
)

# ==================================================
# DATABASE
# ==================================================

t = time.time()

init_db()

print(
    f"database init: "
    f"{time.time() - t:.2f}s"
)

print(
    f"Total startup before UI: "
    f"{time.time() - start:.2f}s"
)

# ==================================================
# APPLICATION
# ==================================================

def main():

    from interface import XenovaInterface

    print("=" * 50)
    print("🤖 XENOVA")
    print("Personal AI Interface")
    print("=" * 50)

    # Create controller first
    controller = XenovaController()

    # Create UI and connect BOTH pipelines
    interface = XenovaInterface(
        on_command=controller.handle_text,
        on_voice=controller.handle_voice
    )

    # Give controller access to UI
    controller.interface = interface

    print("✅ XENOVA interface connected")
    print("✅ Text pipeline connected")
    print("✅ Voice pipeline connected")
    print("=" * 50)

    # Start UI
    interface.run()


# ==================================================
# START
# ==================================================

if __name__ == "__main__":
    main()

