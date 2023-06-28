import asyncio
import json
import re
from typing import List, Tuple

import openai
import requests
from pydantic import BaseSettings
import datetime

from app.helpers import process_urls


class Settings(BaseSettings):
    """This config is a main config"""

    OPENAI_API_KEY: str = "OPENAI_API_KEY"
    PORT: int = 5001
    DEBUG: bool = False
    openapi_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
openai.api_key = settings.OPENAI_API_KEY


def get_topstories(max_stories=30):
    # Get top stories
    topstories = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
    if (code := topstories.status_code) != 200:
        raise ValueError(f"topstories status code: {code}")

    topstories_ids = topstories.json()

    # Filter stores
    return topstories_ids[:max_stories]


def fix_asyncio_loop_for_jupyer():
    import sys

    if "ipykernel" in sys.modules:
        import nest_asyncio

        nest_asyncio.apply()  # Allow nested event loops in Jupyter Notebook


def get_items(list_of_items: List[int], batch_size=12):
    # Prepare API requests to get all items
    URL_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    urls = [URL_ITEM.format(t_s) for t_s in list_of_items]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(process_urls(urls, batch_size))
    return results


def get_openai_prompt(topics: List[str]) -> Tuple[dict, dict]:
    system_message = {
        "role": "system",
        "content": (
            "You are an assistant that can group news articles from hackernews (news.ycombinator.com) into topics"
        ),
    }

    user_message = {
        "role": "user",
        "content": (
            "Group the following news articles into topics\n\n"
            + topics
            + "\n\nUse the following format:\n"
            + "topic_name_1\n- title\turl\n- title\turl\ntopic_name_2\n\ttitle\turl"
        ),
    }

    return system_message, user_message


def betterhacker_news_worker():
    fix_asyncio_loop_for_jupyer()
    topstories_shortlist = get_topstories()
    results = get_items(topstories_shortlist)
    results_parsed = [f"{el['title']} URL: {el['url']}" for el in results if el.get("url", None) is not None]
    topics = "\n\n".join(results_parsed)

    # Working with OpenAI
    s_m, u_m = get_openai_prompt(topics=topics)  # system & user messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[s_m, u_m],
        max_tokens=2200,
    )

    res = response["choices"][0]["message"]["content"].split("\n")

    # Parse results
    current_topic = None
    dict_ = {}
    titles_returned = {}
    for l in res:
        if l == "\n":
            continue

        if not ("http://" in l.lower() or "https://" in l.lower()):
            current_topic = l
            continue

        if current_topic not in dict_:
            dict_[current_topic] = {}

        pattern = r"- (.+?)\s*URL:"
        pattern2 = r"- (.+?)\s*http"
        match = re.search(pattern, l)
        match2 = re.search(pattern2, l)
        if match:
            substring = str(match.group(1))
            titles_returned[substring] = current_topic
        elif match2:
            substring = str(match2.group(1))
            titles_returned[substring] = current_topic
        else:
            print(l)

    data = {}
    for r in results:
        if "url" not in r or "score" not in r:
            print("Skip: ", r)
            continue
        data[r["title"]] = {"url": r["url"], "score": r["score"]}

    for k in data:
        if k in titles_returned:
            data[k]["topic"] = titles_returned[k]
            continue

        data[k]["topic"] = "Other"

    prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    fname = f"data/{prefix}_articles.json"
    json.dump(data, open(fname, "w"))


if __name__ == "__main__":
    betterhacker_news_worker()
