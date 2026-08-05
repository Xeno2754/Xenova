import json
from brain.ai import chat

SEMANTIC_MEMORY_PROMPT = """
You are an AI that extracts useful long-term memories.

Read the user's message.

If it contains information worth remembering,
return ONLY valid JSON.

Example:

{
    "remember": true,
    "key": "college",
    "value": "TCET"
}

If nothing should be remembered:

{
    "remember": false
}

Return ONLY JSON.
"""


def extract_memory(user_input):

    reply, _ = chat(
        user_input,
        [],
        system_prompt=SEMANTIC_MEMORY_PROMPT,
        stream=False
    )

    try:
        return json.loads(reply)

    except Exception:
        return {
            "remember": False
        }