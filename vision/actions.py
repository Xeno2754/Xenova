import pyautogui

from vision.analyzer import locate_on_screen


def click_at(x, y):
    """
    Move the mouse to the specified coordinates and click.
    """

    try:

        print(f"🖱️ Clicking at ({x}, {y})")

        pyautogui.moveTo(
            x,
            y,
            duration=0.2
        )

        pyautogui.click()

        return f"Clicked at ({x}, {y})"

    except Exception as e:

        return f"Mouse click error: {e}"


def click_on_screen(target):
    """
    Find an element on the screen using vision
    and click its center.
    """

    print(f"🎯 Finding: {target}")

    result = locate_on_screen(target)

    if not result.get("found"):

        return (
            f"Could not find '{target}' "
            "on the screen."
        )

    x = result.get("x")
    y = result.get("y")

    if x is None or y is None:

        return (
            f"Vision found '{target}' "
            "but returned invalid coordinates."
        )

    return click_at(x, y)


def type_text(text):
    """
    Type text using the keyboard.
    """

    try:

        print(f"⌨️ Typing: {text}")

        pyautogui.write(
            text,
            interval=0.03
        )

        return f"Typed: {text}"

    except Exception as e:

        return f"Keyboard typing error: {e}"


def click_and_type(target, text):
    """
    Find an element on the screen,
    click it, then type the requested text.
    """

    print(f"🎯 Finding: {target}")

    result = locate_on_screen(target)

    if not result.get("found"):

        return (
            f"Could not find '{target}' "
            "on the screen."
        )

    x = result.get("x")
    y = result.get("y")

    if x is None or y is None:

        return (
            f"Vision found '{target}' "
            "but returned invalid coordinates."
        )

    click_result = click_at(x, y)

    if "error" in click_result.lower():

        return click_result

    type_result = type_text(text)

    return (
        f"{click_result}\n"
        f"{type_result}"
    )