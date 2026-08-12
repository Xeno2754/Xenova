import ollama
from config.settings import OLLAMA_MODEL

SYSTEM_PROMPT = """
You are XENOVA, a professional AI voice assistant.

LANGUAGE:
- Always respond in English unless the user explicitly requests another language.

STYLE:
- Be concise and conversational.
- Answer directly.
- Do not add unnecessary explanations.
"""


def chat(
    message,
    history=None,
    system_prompt=None,
    stream=True
):
    """Chat with the local Ollama model."""

    if history is None:
        history = []

    system = system_prompt if system_prompt else SYSTEM_PROMPT

    messages = [
        {
            "role": "system",
            "content": system
        }
    ]

    messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    assistant_reply = ""

    options = {
        "temperature": 0.1,
        "num_predict": 256,
    }

    if stream:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            stream=True,
            options=options,
            keep_alive="30m"
        )

        print("\n🤖 Xenova: ", end="", flush=True)

        for chunk in response:
            if "message" in chunk:
                content = chunk["message"].get("content", "")
                assistant_reply += content
                print(content, end="", flush=True)

        print()

    else:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            stream=False,
            options=options,
            keep_alive="30m"
        )

        assistant_reply = response["message"]["content"].strip()

    history.append(
        {
            "role": "user",
            "content": message
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": assistant_reply
        }
    )

    # Keep the conversation small so inference stays fast.
    if len(history) > 10:
        del history[:-10]

    return assistant_reply, history
