from tools.apps import open_app
from tools.web import web_search


def execute(user_input):
    text = user_input.lower()

    if text.startswith("open "):
        app = text.replace("open ", "").strip()
        return open_app(app)

    if text.startswith("search "):
        query = text.replace("search ", "").strip()
        return web_search(query)

    return None