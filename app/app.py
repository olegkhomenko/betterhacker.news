import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def get_articles(request: Request):
    with open("articles.json", "r") as json_file:
        articles = json.load(json_file)

    grouped_articles = {}

    for title, article in articles.items():
        topic = article["topic"]
        if topic in grouped_articles:
            grouped_articles[topic][title] = article
        else:
            grouped_articles[topic] = {title: article}

    return templates.TemplateResponse(
        "index.html", {"request": request, "articles": grouped_articles}
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=5001, reload=True)
