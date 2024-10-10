import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_github_repos(days=60):
    github_repos = []
    end_date = datetime.now()

    for i in range(days):
        date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        fname = f"data/{date}_articles.json"
        if os.path.exists(fname):
            with open(fname, "r") as json_file:
                articles = json.load(json_file)
                for title, article in articles.items():
                    if "github.com" in article["url"]:
                        github_repos.append({"title": title, "url": article["url"], "score": article["score"]})

    return sorted(github_repos, key=lambda x: x["score"], reverse=True)


@app.get("/")
def get_articles(request: Request):
    fname = sorted(glob.glob("data/*_articles.json"), reverse=True)[0]
    with open(fname, "r") as json_file:
        articles = json.load(json_file)

    grouped_articles = {}

    for title, article in articles.items():
        topic = article["topic"]
        if topic in grouped_articles:
            grouped_articles[topic][title] = article
        else:
            grouped_articles[topic] = {title: article}

    # Calculate total score for each topic/group
    topic_scores = defaultdict(lambda: 0)
    for topic, data in articles.items():
        topic_scores[data["topic"]] += data["score"]

    # Get popular GitHub repos
    popular_github_repos = get_github_repos()
    print(popular_github_repos)
    print(len(popular_github_repos))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "articles": grouped_articles,
            "topic_scores": topic_scores,
            "popular_github_repos": popular_github_repos,
        },
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5556, reload=True)
