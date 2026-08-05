import subprocess
import os

APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vscode": r"C:\Users\Ainesh\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "cmd": "cmd.exe"
}


def open_app(app_name):
    app_name = app_name.lower()

    if app_name not in APPS:
        return f"I don't know how to open {app_name}."

    try:
        subprocess.Popen(APPS[app_name])
        return f"Opening {app_name}."
    except Exception as e:
        return str(e)