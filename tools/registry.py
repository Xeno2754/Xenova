import json

TOOLS_FILE = "tools/tools.json"


def load_tools():
    with open(TOOLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["tools"]


def get_tool_descriptions():

    tools = load_tools()

    text = ""

    for tool in tools:

        if tool.get("enabled", True):

            text += f"""
Tool: {tool['name']}
Description: {tool['description']}

"""

    return text