from typing import Optional

from fastapi import Body, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

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


class PostBase(BaseModel):
    title: str
    content: Optional[str] = "Contenido no disponible"


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (mínimo 3 caracteres, maximo 100)",
        examples=["Mi primer post con FastAPI"],
    )

    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (mínimo 10 caracteres)",
        examples=["Este es un contenido valido con 10 caracteres o mas"],
    )


class PostUpdate(BaseModel):
    title: str
    content: Optional[str] = None


@app.get("/")
def home():
    json = {"message": "Bienvenidos a Mini Blog por Yeromi", "name": "Yeromi"}
    return json


@app.get("/section")
def section():
    return {"message": "Bienvenido a mi nueva sección"}


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
def create_post(post: PostCreate):
    """
    Crear un post mediante Pydantic
    """
    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1
    new_post = {"id": new_id, "title": post.title, "content": post.content}

    BLOG_POST.append(new_post)

    return {"message": "Post Creado", "data": new_post}


@app.put("/posts/{post_id}")
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            playload = data.model_dump(exclude_unset=True)
            if "title" in playload:
                post["title"] = playload["title"]
            if "content" in playload:
                post["content"] = playload["content"]

            return {"message": "Post actualizado", "data": post}

    raise HTTPException(status_code=404, detail="Post no encontrado")


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return

    raise HTTPException(status_code=404, detail="Post no encontrado")
