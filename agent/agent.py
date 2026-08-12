from brain.ai import chat
from brain.planner import plan

from memory.manager import remember, recall
from tools.executor import execute_tool


def process(user_input, history):

    # The planner already uses the LLM. For normal chat, reuse its
    # response instead of sending the same request to the LLM again.
    decision = plan(user_input)

    action = decision.get("action")

    memory = decision.get("memory", {})

    if memory.get("remember"):
        remember(
            memory.get("key", ""),
            memory.get("value", "")
        )

    if action == "remember":
        result = remember(
            decision.get("key", ""),
            decision.get("value", "")
        )
        return result, history

    if action == "recall":
        key = decision.get("key", "")
        value = recall(key)

        if value:
            return f"Your {key} is {value}.", history

        return "I don't remember that yet.", history

    if action == "tool":
        tool_result = execute_tool(decision)

        print("\n===== TOOL RESULT =====")
        print(tool_result)
        print("=======================\n")

        if not tool_result:
            return "I couldn't complete that action.", history

        # Tool results are already factual. Avoid another LLM request
        # just to rephrase them; this saves several seconds per command.
        return str(tool_result), history

    # Normal chat: planner's response is already the answer.
    response = decision.get("response", "")

    if response:
        return response, history

    # Fallback for an incomplete planner response.
    return chat(user_input, history)
