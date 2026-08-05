import ollama
from config.settings import OLLAMA_MODEL

SYSTEM_PROMPT = """
You are XENOVA.

You are a professional AI voice assistant.

Rules:
- Be concise unless the user asks for details.
- Be helpful and accurate.
- If information may be outdated or requires current knowledge, use the available tools.
- Keep responses conversational.
"""


def chat(
    message,
    history=None,
    system_prompt=None,
    stream=True
):
    """
    Chat with the LLM.

    Args:
        message (str): User message
        history (list): Conversation history
        system_prompt (str): Optional custom system prompt
        stream (bool): Stream response to console or not

    Returns:
        tuple:
            assistant_reply (str),
            updated_history (list)
    """

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

    # ---------------- Streaming Mode ----------------

    if stream:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            stream=True
        )

        print("\n🤖 Xenova: ", end="", flush=True)

        for chunk in response:

            if "message" in chunk:

                content = chunk["message"]["content"]

                assistant_reply += content

                print(content, end="", flush=True)

        print()

    # ---------------- Silent Mode ----------------

    else:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            stream=False
        )

        assistant_reply = response["message"]["content"]

    # ---------------- Save Conversation ----------------

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

    return assistant_reply, history