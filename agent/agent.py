from brain.ai import chat
from brain.planner import plan

from memory.manager import remember, recall
from tools.executor import execute_tool

import time

t = time.time()
from brain.ai import chat
print(f"brain.ai: {time.time()-t:.2f}s")

t = time.time()
from brain.planner import plan
print(f"brain.planner: {time.time()-t:.2f}s")

t = time.time()
from memory.manager import remember, recall
print(f"memory: {time.time()-t:.2f}s")

t = time.time()
from tools.executor import execute_tool
print(f"tools: {time.time()-t:.2f}s") 

def process(user_input, history):

    decision = plan(user_input)

    action = decision.get("action")

    # ---------- Automatic Memory ----------

    memory = decision.get("memory", {})

    if memory.get("remember"):
        remember(
            memory["key"],
            memory["value"]
        )

    # ---------- Explicit Memory ----------

    if action == "remember":

        return remember(
            decision["key"],
            decision["value"]
        ), history

    elif action == "recall":

        value = recall(decision["key"])

        if value:
            return f"Your {decision['key']} is {value}.", history

        return "I don't remember that yet.", history

    # ---------- Tools ----------

    elif action == "tool":

        tool_result = execute_tool(decision)

        prompt = f"""
User Question:

{user_input}

Tool Output:

{tool_result}

Answer naturally.
"""

        return chat(prompt, history)

    # ---------- Normal Chat ----------

    return chat(user_input, history)