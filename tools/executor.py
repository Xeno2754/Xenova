from tools.web import web_search
from tools.apps import open_app

from tools.browser import (
    open_website,
    search_google,
    search_youtube,
    get_youtube_results,
    click_youtube_result,
    click_first_youtube_result,
    go_back,
    go_forward,
    current_page
)

from vision.analyzer import analyze_screen
from vision.actions import click_on_screen, click_and_type


TOOLS = {
    "web_search": web_search,
    "open_app": open_app,

    "open_website": open_website,
    "search_google": search_google,
    "search_youtube": search_youtube,
    "get_youtube_results": get_youtube_results,

    "click_youtube_result": click_youtube_result,
    "click_first_youtube_result": click_first_youtube_result,

    "go_back": go_back,
    "go_forward": go_forward,
    "current_page": current_page,

    "analyze_screen": analyze_screen,

    "click_on_screen": click_on_screen,
    "click_and_type": click_and_type,
}


def execute_tool(plan):
    """
    Executes the tool selected by the AI planner.
    """

    tool = plan.get("tool")

    if not tool:
        return "No tool selected."

    tool_name = tool.get("name", "").lower()
    tool_input = tool.get("input", "")

    if tool_name not in TOOLS:
        return f"Unknown tool: {tool_name}"

    try:

        print(f"🔧 Tool: {tool_name}")
        print(f"📥 Input: {tool_input}")

        # ------------------------------------------------
        # TOOLS THAT REQUIRE NO ARGUMENT
        # ------------------------------------------------

        if tool_name in {
            "get_youtube_results",
            "click_first_youtube_result",
            "go_back",
            "go_forward",
            "current_page"
        }:

            result = TOOLS[tool_name]()

        # ------------------------------------------------
        # CLICK YOUTUBE RESULT
        # ------------------------------------------------

        elif tool_name == "click_youtube_result":

            try:

                index = int(tool_input)

            except (ValueError, TypeError):

                return (
                    f"Invalid YouTube result number: "
                    f"{tool_input}"
                )

            result = TOOLS[tool_name](index)

        # ------------------------------------------------
        # CLICK AND TYPE
        # ------------------------------------------------

        elif tool_name == "click_and_type":

            if not isinstance(tool_input, dict):

                return (
                    "click_and_type requires "
                    "target and text."
                )

            target = tool_input.get("target")
            text = tool_input.get("text")

            if not target:

                return "Missing target for click_and_type."

            if text is None:

                return "Missing text for click_and_type."

            result = TOOLS[tool_name](
                target,
                text
            )

        # ------------------------------------------------
        # NORMAL ONE-ARGUMENT TOOLS
        # ------------------------------------------------

        else:

            result = TOOLS[tool_name](tool_input)

        print(f"📤 Result: {result}")

        return result

    except Exception as e:

        return f"Tool execution error: {e}"