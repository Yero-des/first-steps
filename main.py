from fastapi import Body, FastAPI, Query

app = FastAPI(title="Mini Blog")

BLOG_POST = [
    {"id": 1, "title": "Hola desde FastAPI", "content": "Mi primer post con fastAPI"},
    {
        "id": 2,
        "title": "Mi segundo post con FastAPI",
        "content": "Mi segundo post con fastAPI",
    },
    {"id": 3, "title": "Django vs FastAPI", "content": "FastAPI es mas rapido"},
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
            or query.lower() in post["content"]
        ]

        return {"data": results, "query": query}

    return {"data": BLOG_POST}


@app.get("/posts/{post_id}")
def get_post(
    post_id: int,
    include_content: bool = Query(
        default=True, description="Booleano para saber si incluir el contenido o no"
    ),
):
    """
    Ruta para encontrar un post mediante su id
    """

    for post in BLOG_POST:

        # Buscamos el post por id unico
        if post["id"] == post_id:

            # Validar si se quiere mostrar o no el content
            if not include_content:
                copy_post = post.copy()
                del copy_post["content"]

                return {"data": copy_post}

            return {"data": post}

    # Error en caso no se logre encontrar un post
    return {"error": "Post no encontrado"}


@app.post("/posts")
def create_post(post: dict = Body(...)):
    """
    Crear un post mediante Body
    """
    if "title" not in post or "content" not in post:
        return {"error", "Title y content son requeridos"}

    if not str(post["title"]).strip():
        return {"error": "Title no puede estar vacío"}

    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1
    new_post = {"id": new_id, "title": post["title"], "content": post["content"]}

    BLOG_POST.append(new_post)

    return {"message": "Post Creado", "data": new_post}


# Comentario de 14/10
# Comentario de 15/10
