from ddgs import DDGS
import time


def web_search(query):
    """
    Search the internet using DDGS.
    """

    try:
        start = time.time()

        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    max_results=5
                )
            )

        elapsed = time.time() - start

        print(f"🌐 Web Search: {elapsed:.2f}s")

        if not results:
            return "No search results found."

        answer = "Here are the top search results:\n\n"

        for i, result in enumerate(results, 1):

            title = result.get("title", "No title")
            url = result.get("href", "")
            body = result.get("body", "")

            answer += (
                f"{i}. {title}\n"
                f"URL: {url}\n"
                f"Summary: {body}\n\n"
            )

        return answer

    except Exception as e:

        print(f"❌ Web search error: {e}")

        return f"Web search failed: {e}"