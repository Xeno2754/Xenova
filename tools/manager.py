from tools.apps import open_app
from tools.web import web_search

TOOLS = {
    "open_app": open_app,
    "web_search": web_search,
}


def run_tool(tool_name, tool_input):
    """
    Execute a tool by name.
    """
    tool = TOOLS.get(tool_name)

    if tool is None:
        return f"Unknown tool: {tool_name}"

    return tool(tool_input)