import json
from collections import defaultdict

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import glob

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "articles": grouped_articles,
            "topic_scores": topic_scores,
        },
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=5001, reload=True)
