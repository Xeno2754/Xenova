from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus
import time


_browser = None
_page = None
_playwright = None


def get_browser():
    global _browser
    global _page
    global _playwright

    if _browser is None:
        _playwright = sync_playwright().start()

        _browser = _playwright.chromium.launch(
            headless=False
        )

        _page = _browser.new_page(
            viewport={
                "width": 1280,
                "height": 720
            }
        )

    return _page


def open_website(url):
    try:
        page = get_browser()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=15000
        )

        return (
            f"Opened website.\n"
            f"Title: {page.title()}\n"
            f"URL: {page.url}"
        )

    except Exception as e:
        return f"Browser error: {e}"


def search_google(query):
    try:
        page = get_browser()

        url = (
            "https://www.google.com/search?q="
            + quote_plus(query)
        )

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=15000
        )

        return (
            f"Searching Google for {query}\n"
            f"URL: {page.url}"
        )

    except Exception as e:
        return f"Browser error: {e}"


def search_youtube(query):
    try:
        page = get_browser()

        url = (
            "https://www.youtube.com/results?search_query="
            + quote_plus(query)
        )

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=15000
        )

        # Wait for YouTube results
        page.locator(
            "ytd-video-renderer"
        ).first.wait_for(
            state="visible",
            timeout=15000
        )

        return (
            f"YouTube search completed for: {query}\n"
            f"URL: {page.url}"
        )

    except Exception as e:
        return f"YouTube search error: {e}"


def get_youtube_results():
    try:
        page = get_browser()

        results = page.locator(
            "ytd-video-renderer"
        )

        count = results.count()

        if count == 0:
            return "No YouTube results found."

        output = "YouTube results:\n\n"

        limit = min(count, 5)

        for i in range(limit):

            item = results.nth(i)

            title = item.locator(
                "a#video-title"
            ).get_attribute("title")

            href = item.locator(
                "a#video-title"
            ).get_attribute("href")

            if title and href:

                output += (
                    f"{i + 1}. {title}\n"
                    f"https://www.youtube.com{href}\n\n"
                )

        return output

    except Exception as e:
        return f"Could not read YouTube results: {e}"


def click_youtube_result(index=1):
    try:
        page = get_browser()

        results = page.locator(
            "ytd-video-renderer"
        )

        count = results.count()

        if count == 0:
            return "No YouTube results are available."

        if index < 1 or index > count:
            return (
                f"Invalid result number {index}. "
                f"There are {count} results."
            )

        item = results.nth(index - 1)

        title = item.locator(
            "a#video-title"
        ).get_attribute("title")

        link = item.locator(
            "a#video-title"
        ).get_attribute("href")

        item.locator(
            "a#video-title"
        ).click()

        page.wait_for_load_state(
            "domcontentloaded",
            timeout=15000
        )

        return (
            f"Opened YouTube result {index}.\n"
            f"Title: {title}\n"
            f"URL: {page.url}"
        )

    except Exception as e:
        return f"Could not open YouTube result: {e}"


def click_first_youtube_result():
    return click_youtube_result(1)


def go_back():
    try:
        page = get_browser()

        page.go_back(
            wait_until="domcontentloaded",
            timeout=15000
        )

        return (
            f"Went back.\n"
            f"Title: {page.title()}\n"
            f"URL: {page.url}"
        )

    except Exception as e:
        return f"Could not go back: {e}"


def go_forward():
    try:
        page = get_browser()

        page.go_forward(
            wait_until="domcontentloaded",
            timeout=15000
        )

        return (
            f"Went forward.\n"
            f"Title: {page.title()}\n"
            f"URL: {page.url}"
        )

    except Exception as e:
        return f"Could not go forward: {e}"


def current_page():
    try:
        page = get_browser()

        return (
            f"Current page:\n"
            f"Title: {page.title()}\n"
            f"URL: {page.url}"
        )

    except Exception as e:
        return f"Could not read current page: {e}"