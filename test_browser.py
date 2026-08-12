import time

from tools.browser import (
    search_youtube,
    get_youtube_results,
    click_youtube_result
)

print(search_youtube("GTA 6"))

print(get_youtube_results())

print(click_youtube_result(1))

print("Browser will stay open for 60 seconds...")

time.sleep(60)