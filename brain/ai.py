from ollama import chat

# Stores conversation history
conversation = []

def ask_jarvis(user_message):
    conversation.append({
        "role": "user",
        "content": user_message
    })

    response = chat(
        model="qwen3:8b",
        messages=conversation
    )

    assistant_message = response["message"]["content"]

    conversation.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message