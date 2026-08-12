import time
import json
import re
import ollama

from vision.screen import capture_screen


VISION_MODEL = "qwen2.5vl:3b"


def analyze_screen(question="What is currently visible on my screen?"):

    start = time.time()

    image_path = capture_screen()

    print("👁️ Analyzing screen...")

    try:

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
You are XENOVA's screen vision system.

Analyze the screenshot carefully.

Answer ONLY what the user asked.

Be concise and factual.

Do not give tutorials.
Do not suggest next steps.
Do not repeat the user's question.
Do not describe how to build XENOVA.

If identifying an application, give its name.

If identifying a website, give its name and important visible page information.

If describing the screen, summarize the important visible elements in 2-4 sentences.
"""
                },
                {
                    "role": "user",
                    "content": question,
                    "images": [image_path]
                }
            ]
        )

        answer = response["message"]["content"].strip()

        print(
            f"👁️ Vision: {time.time() - start:.2f}s"
        )

        return answer

    except Exception as e:

        return f"Vision error: {e}"


def locate_on_screen(target):

    start = time.time()

    image_path = capture_screen()

    print(f"👁️ Locating: {target}")

    try:

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
You are XENOVA's visual locator.

Find the requested element in the screenshot.

Return ONLY valid JSON.

If the element is found:

{
    "found": true,
    "x": 500,
    "y": 300,
    "description": "short description"
}

The x and y coordinates must represent the CENTER
of the element.

If the element is not found:

{
    "found": false,
    "x": null,
    "y": null,
    "description": "not found"
}

Do not return markdown.
Do not return explanations.
Do not return code fences.
"""
                },
                {
                    "role": "user",
                    "content": f"Locate this element: {target}",
                    "images": [image_path]
                }
            ]
        )

        raw = response["message"]["content"].strip()

        # Remove accidental markdown fences
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

        result = json.loads(raw)

        print(
            f"👁️ Locator: {time.time() - start:.2f}s"
        )

        print(f"📍 Result: {result}")

        return result

    except Exception as e:

        print(
            f"👁️ Locator error: {e}"
        )

        return {
            "found": False,
            "x": None,
            "y": None,
            "description": f"locator error: {e}"
        }