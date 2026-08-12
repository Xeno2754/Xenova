from brain.ai import chat
from brain.planner import plan

from memory.manager import remember, recall
from tools.executor import execute_tool


def process(user_input, history):

    # ==========================================
    # PLANNER
    # ==========================================

    decision = plan(user_input)

    print("\n===== PLANNER OUTPUT =====")
    print(decision)
    print("==========================\n")

    action = decision.get("action")

    # ==========================================
    # AUTOMATIC MEMORY
    # ==========================================

    memory = decision.get("memory", {})

    if memory.get("remember"):

        remember(
            memory.get("key", ""),
            memory.get("value", "")
        )

    # ==========================================
    # EXPLICIT MEMORY
    # ==========================================

    if action == "remember":

        result = remember(
            decision.get("key", ""),
            decision.get("value", "")
        )

        return result, history

    # ==========================================
    # RECALL MEMORY
    # ==========================================

    if action == "recall":

        value = recall(
            decision.get("key", "")
        )

        if value:

            return (
                f"Your {decision.get('key')} is {value}.",
                history
            )

        return "I don't remember that yet.", history

    # ==========================================
    # TOOL
    # ==========================================

    if action == "tool":

        tool_result = execute_tool(decision)

        print("\n===== TOOL RESULT =====")
        print(tool_result)
        print("=======================\n")

        # If the tool failed
        if not tool_result:

            return "I couldn't complete that action.", history

        # Let XENOVA explain the result naturally
        prompt = f"""
You are XENOVA.

The user said:

{user_input}

A tool was executed.

Tool result:

{tool_result}

Respond naturally and concisely.

Do not claim that an action was completed unless the tool result confirms it.

Always respond in English unless the user requested another language.
"""

        return chat(
            prompt,
            history
        )

    # ==========================================
    # NORMAL CHAT
    # ==========================================

    return chat(
        user_input,
        history
    )