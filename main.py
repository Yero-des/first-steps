from typing import List, Optional, Union

from fastapi import Body, FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, field_validator

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

BAD_WORD = ["fuck", "wtf", "retard", "omg", "xxx", "porn"]


class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
        examples=["Javascript"],
    )


class Author(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Autor del post",
        examples=["Yeromi"],
    )
    email: EmailStr = Field(
        ..., description="Email del autor", examples=["123@example.com"]
    )
    age: int = Field(
        ..., description="Edad del autor", gt=0, lt=100, examples=[22, 10, 50]
    )


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None


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

    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        for word in BAD_WORD:
            if word in value.lower():
                raise ValueError(f"El titulo no puede contener la palabra: '{word}'")
        return value

    @field_validator("content")
    @classmethod
    def not_allowed_content(cls, value: str) -> str:
        for word in BAD_WORD:
            if word in value.lower():
                raise ValueError(f"El contenido no puede contener la palabra: '{word}'")
        return value


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=10)


class PostPublic(PostBase):
    id: int


class PostSummary(BaseModel):
    id: int
    title: str


@app.get("/")
def home():
    json = {"message": "Bienvenidos a Mini Blog por Yeromi", "name": "Yeromi"}
    return json


@app.get("/section")
def section():
    return {"message": "Bienvenido a mi nueva sección"}


@app.get("/posts", response_model=List[PostPublic], response_model_exclude_none=True)
def list_posts(
    query: str | None = Query(default=None, description="Texto para buscar por titulo")
):

    if query:
        return [
            post
            for post in BLOG_POST
            if query.lower() in post["title"].lower()
            or query.lower() in post["content"].lower()
        ]

    return BLOG_POST


@app.get(
    "/posts/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post encontrado",
)
def get_post(
    post_id: int,
    include_content: bool = Query(
        default=True, description="Booleano para saber si incluir el contenido o no"
    ),
):
    for post in BLOG_POST:

        # Buscamos el post por id unico
        if post["id"] == post_id:

            # Validar si se quiere mostrar o no el content
            if not include_content:
                return {"id": post["id"], "title": post["title"]}

            return post

    # Error en caso no se logre encontrar un post
    return HTTPException(status_code=404, detail="Post no encontrado")


@app.post("/posts", response_model=PostPublic, response_description="Post Creado (OK)")
def create_post(post: PostCreate):
    """
    Crear un post mediante Pydantic
    """
    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1
    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        "author": post.author.model_dump() if post.author else None,
        "tags": [tag.model_dump() for tag in post.tags],
    }

    BLOG_POST.append(new_post)

    return new_post


@app.put(
    "/posts/{post_id}",
    response_model=PostPublic,
    response_description="Post Actualizado (OK)",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            playload = data.model_dump(exclude_unset=True)
            if "title" in playload:
                post["title"] = playload["title"]
            if "content" in playload:
                post["content"] = playload["content"]

            return post

    raise HTTPException(status_code=404, detail="Post no encontrado")


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return

    raise HTTPException(status_code=404, detail="Post no encontrado")
