from duckduckgo_search import DDGS
import time


def web_search(query):
    try:
        start = time.time()

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        print(f"🌐 DuckDuckGo: {time.time() - start:.2f}s")

        if not results:
            return "No results found."

        answer = "Here are the top search results:\n\n"

        for i, result in enumerate(results, 1):
            answer += (
                f"{i}. {result['title']}\n"
                f"{result['href']}\n\n"
            )

        return answer

    except Exception as e:
        return str(e)