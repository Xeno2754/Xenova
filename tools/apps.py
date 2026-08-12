import subprocess
import webbrowser

APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vscode": r"C:\Users\Ainesh\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "cmd": "cmd.exe",
}

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "chatgpt": "https://chat.openai.com",
    "spotify": "https://open.spotify.com",
}


def open_app(name):
    name = name.lower().strip()

    # Open installed application
    if name in APPS:
        try:
            subprocess.Popen(APPS[name])
            return f"Opening {name}."
        except Exception as e:
            return f"Failed to open {name}: {e}"

    # Open website
    if name in WEBSITES:
        webbrowser.open(WEBSITES[name])
        return f"Opening {name}."

    return f"I don't know how to open '{name}'."