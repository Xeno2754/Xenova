from tools.web import web_search
from tools.apps import open_app


TOOLS = {
    "web_search": web_search,
    "open_app": open_app,
}


def execute_tool(plan):
    """
    Executes the tool selected by the AI planner.
    """

    tool = plan.get("tool")

    if not tool:
        return None

    tool_name = tool.get("name")
    tool_input = tool.get("input")

    if tool_name not in TOOLS:
        return f"Unknown tool: {tool_name}"

    return TOOLS[tool_name](tool_input)