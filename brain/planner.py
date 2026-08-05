import json
from brain.ai import chat

PLANNER_PROMPT = """
You are the master planner for XENOVA.

Your job is to analyze the user's request and decide what should happen.

Return ONLY valid JSON.

Schema:

{
    "action": "chat" | "tool" | "remember" | "recall",

    "response": "",

    "tool": {
        "name": "",
        "input": ""
    },

    "memory": {
        "remember": false,
        "key": "",
        "value": ""
    },

    "key": "",
    "value": ""
}

Rules:

1. Use "chat" for normal conversation.

2. Use "tool" if current internet information or desktop actions are required.

3. Use "remember" ONLY if the user explicitly says:
   - remember...
   - save...
   - store...

4. Use "recall" if the user asks:
   - what is my...
   - do you remember...

5. If the user naturally reveals useful personal information
   (college, birthday, favorite game, city, etc.)

then keep:

"action":"chat"

but also set

"memory":{
    "remember": true,
    "key":"...",
    "value":"..."
}

Return ONLY JSON.
"""


def plan(user_input):
    """
    Uses the LLM to decide what XENOVA should do.
    """

    reply, _ = chat(
        message=user_input,
        history=[],
        system_prompt=PLANNER_PROMPT,
        stream=False
    )

    try:
        return json.loads(reply)

    except Exception:
        return {
            "action": "chat",
            "response": "",
            "tool": None,
            "memory": {
                "remember": False,
                "key": "",
                "value": ""
            },
            "key": "",
            "value": ""
        }