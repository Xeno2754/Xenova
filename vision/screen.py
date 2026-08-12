import os
import time

import mss
from PIL import Image


SCREENSHOT_PATH = os.path.join(
    "cache",
    "screen.png"
)


def capture_screen():

    os.makedirs("cache", exist_ok=True)

    start = time.time()

    with mss.mss() as sct:

        monitor = sct.monitors[1]

        screenshot = sct.grab(monitor)

        image = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        image.save(SCREENSHOT_PATH)

    elapsed = time.time() - start

    print(f"📸 Screenshot captured in {elapsed:.2f}s")
    print(f"🖼️ Saved to: {SCREENSHOT_PATH}")

    return SCREENSHOT_PATH