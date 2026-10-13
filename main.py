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
        results = [
            post
            for post in BLOG_POST
            if query.lower() in post["title"].lower()
            or query.lower() in post["Content"]
        ]

        return {"data": results, "query": query}

    return {"data": BLOG_POST}


@app.get("/posts/{post_id}")
def get_post(
    post_id: int,
    include_content: str | None = Query(
        default=None, description="Booleano para saber si incluir el contenido o no"
    ),
):
    """
    Ruta para encontrar un post mediante su id
    """

    for post in BLOG_POST:

        # Buscamos el post por id unico
        if post["id"] == post_id:

            # Validar si se quiere mostrar o no el content
            if include_content:

                if include_content.lower() == "false":

                    copy_post = post.copy()
                    del copy_post["Content"]

                    return {"data": copy_post}

            return {"data": post}

    # Error en caso no se logre encontrar un post
    return {"error": "Post no encontrado"}


# Esto es una prueba
# Esto es otra prueba 2
