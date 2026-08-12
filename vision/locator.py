import json
import re
import time
import ollama

from PIL import Image

from vision.screen import capture_screen


VISION_MODEL = "qwen2.5vl:3b"


def locate_on_screen(target):

    start = time.time()

    # Capture the screen
    image_path = capture_screen()

    print(f"👁️ Locating: {target}")

    try:
        # Load screenshot
        image = Image.open(image_path)

        original_width, original_height = image.size

        # Resize for better vision-model processing
        max_width = 1600

        if original_width > max_width:
            scale = max_width / original_width

            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            image = image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )

        locator_image = "cache/locator.png"
        image.save(locator_image)

        print(
            f"🖼️ Locator image: "
            f"{image.size[0]}x{image.size[1]}"
        )

        prompt = f"""
You are XENOVA's visual computer-use system.

Look carefully at the ENTIRE screenshot.

Find this UI element:

"{target}"

Return ONLY valid JSON.

If found:

{{
    "found": true,
    "x": 0,
    "y": 0,
    "width": 0,
    "height": 0,
    "description": "short description"
}}

If not found:

{{
    "found": false,
    "x": null,
    "y": null,
    "width": null,
    "height": null,
    "description": "not found"
}}

IMPORTANT:

1. x and y are the CENTER of the target.
2. Coordinates must refer to the screenshot you received.
3. Carefully inspect the top, middle and bottom of the screen.
4. Look specifically for the requested UI element.
5. Do not give explanations.
6. Return JSON only.
"""

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [locator_image]
                }
            ]
        )

        answer = response["message"]["content"].strip()

        # Remove markdown fences
        answer = re.sub(
            r"```json\s*",
            "",
            answer,
            flags=re.IGNORECASE
        )

        answer = answer.replace("```", "").strip()

        result = json.loads(answer)

        # Convert resized coordinates back to original screen coordinates
        if result.get("found") and result.get("x") is not None:

            resized_width, resized_height = image.size

            scale_x = original_width / resized_width
            scale_y = original_height / resized_height

            result["x"] = round(
                result["x"] * scale_x
            )

            result["y"] = round(
                result["y"] * scale_y
            )

            if result.get("width") is not None:
                result["width"] = round(
                    result["width"] * scale_x
                )

            if result.get("height") is not None:
                result["height"] = round(
                    result["height"] * scale_y
                )

        print(
            f"👁️ Locator: {time.time() - start:.2f}s"
        )

        print(f"📍 Result: {result}")

        return result

    except Exception as e:

        result = {
            "found": False,
            "x": None,
            "y": None,
            "width": None,
            "height": None,
            "description": f"Locator error: {e}"
        }

        print(f"❌ {result['description']}")

        return result