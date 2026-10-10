from fastapi import FastAPI, Query

app = FastAPI(title="Mini Blog")

BLOG_POST = [
    {"id": 1, "title": "Hola desde FastAPI", "Content": "Mi primer post con fastAPI"},
    {
        "id": 2,
        "title": "Mi segundo post con FastAPI",
        "Content": "Mi segundo post con fastAPI",
    },
    {"id": 3, "title": "Django vs FastAPI", "Content": "FastAPI es mas rapido"},
]


@app.get("/")
def home():
    json = {"message": "Bienvenidos a Mini Blog por Yeromi", "name": "Yeromi"}
    return json


@app.get("/posts")
def list_posts(
    query: str | None = Query(default=None, description="Texto para buscar por titulo")
):

    if query:
        results = [post for post in BLOG_POST if query.lower() in post["title"].lower()]

        return {"data": results, "query": query}

    return {"data": BLOG_POST}
