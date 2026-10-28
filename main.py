import os
from datetime import UTC, datetime
from math import ceil
from typing import List, Literal, Optional, Union

from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import DateTime, Integer, String, Text, create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
print("Contectado a:", DATABASE_URL)

engine_kwargs = {"echo": True, "future": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


class Base(DeclarativeBase):
    pass


class PostORM(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))


Base.metadata.create_all(bind=engine)  # dev


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Mini Blog")

BLOG_POST = [
    {"id": 1, "title": "Hola desde FastAPI", "content": "Mi primer post con fastAPI"},
    {
        "id": 2,
        "title": "Mi segundo post con FastAPI",
        "content": "Mi segundo post con fastAPI",
    },
    {
        "id": 3,
        "title": "Django vs FastAPI",
        "content": "FastAPI es mas rapido",
        "tags": [{"name": "Python"}, {"name": "fastapi"}, {"name": "django"}],
    },
    {
        "id": 4,
        "title": "FastAPI y APIs REST",
        "content": "FastAPI facilita la creación de APIs REST",
    },
    {
        "id": 5,
        "title": "Validación de datos",
        "content": "Con FastAPI puedes validar entradas con Pydantic",
    },
    {
        "id": 6,
        "title": "Documentación automática",
        "content": "FastAPI genera Swagger y Redoc al instante",
    },
    {
        "id": 7,
        "title": "Microservicios con FastAPI",
        "content": "Es ideal para construir microservicios ligeros",
    },
    {
        "id": 8,
        "title": "Deploy sencillo",
        "content": "FastAPI se despliega fácilmente en producción",
    },
    {"id": 9, "title": "Hola desde FastAPI", "content": "Mi primer post con fastAPI"},
    {"id": 10, "title": "Django vs FastAPI", "content": "FastAPI es mas rapido"},
    {
        "id": 11,
        "title": "FastAPI y APIs REST",
        "content": "FastAPI facilita la creación de APIs REST",
    },
    {
        "id": 12,
        "title": "Validación de datos",
        "content": "Con FastAPI puedes validar entradas con Pydantic",
    },
    {
        "id": 13,
        "title": "Documentación automática",
        "content": "FastAPI genera Swagger y Redoc al instante",
    },
    {
        "id": 14,
        "title": "Microservicios con FastAPI",
        "content": "Es ideal para construir microservicios ligeros",
    },
    {
        "id": 15,
        "title": "Deploy sencillo",
        "content": "FastAPI se despliega fácilmente en producción",
    },
    {
        "id": 16,
        "title": "Mi segundo post con FastAPI",
        "content": "Mi segundo post con fastAPI",
    },
    {
        "id": 17,
        "title": "Mi segundo post con FastAPI",
        "content": "Mi segundo post con fastAPI",
    },
    {
        "id": 18,
        "title": "Mi segundo post con FastAPI",
        "content": "Mi segundo post con fastAPI",
    },
    {
        "id": 19,
        "title": "Mi segundo post con FastAPI",
        "content": "Mi segundo post con fastAPI",
    },
    {
        "id": 20,
        "title": "Mi segundo post con FastAPI",
        "content": "Mi segundo post con fastAPI",
    },
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

    model_config = ConfigDict(from_attributes=True)


class PostPublic(PostBase):
    id: int

    # Nos sirve para validar objetos
    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str]
    items: List[PostPublic]


@app.get("/")
def home():
    json = {"message": "Bienvenidos a Mini Blog por Yeromi", "name": "Yeromi"}
    return json


@app.get("/section")
def section():
    return {"message": "Bienvenido a mi nueva sección"}


@app.get("/posts", response_model=PaginatedPost, response_model_exclude_none=True)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Parámetro obsoleto, usa 'query o search' en su lugar.",
    ),
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar por titulo",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z]+$",
    ),
    per_page: int = Query(
        default=10, ge=1, le=50, description="Número de resultados (1-50)"
    ),
    page: int = Query(default=1, ge=1, description="Numero de pagina"),
    order_by: Literal["id", "title"] = Query(
        default="id",
        description="Campo de orden",
    ),
    direction: Literal["asc", "desc"] = Query(
        default="asc", description="Dirección de orden"
    ),
    db: Session = Depends(get_db),
):

    results = select(PostORM)

    query = query or text

    if query:
        results = results.where(PostORM.title.ilike(f"%{query}%"))

    total = db.scalar(select(func.count()).select_from(results.subquery())) or 0
    total_pages = ceil(total / per_page) if total > 0 else 0

    current_page = 1 if total_pages == 0 else min(page, total_pages)

    if order_by == "id":
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)

    results = results.order_by(
        order_col.asc() if direction == "asc" else order_col.desc()
    )
    # results = sorted(
    #     results, key=lambda post: post[order_by], reverse=(direction == "desc")
    # )

    if total_pages == 0:
        items: List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        items = db.execute(results.limit(per_page).offset(start)).scalars().all()

    has_prev = current_page > 1
    has_next = current_page < total_pages

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,
    )


@app.get(
    "/posts/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post encontrado",
)
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        title="ID del post",
        description="Identificador entero del post. Debe ser mayor a 1",
        examples=[1],
    ),
    include_content: bool = Query(
        default=True, description="Booleano para saber si incluir el contenido o no"
    ),
    db: Session = Depends(get_db),
):

    post_find = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(post_find).scalar_one_or_none()

    # post = db.get(PostORM, post_id)

    if not post:
        # Error en caso no se logre encontrar un post
        raise HTTPException(status_code=404, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@app.get("/post/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="Una o mas etiquetas Ejemplo: ?tags=python&tags=fastapi",
    )
):
    tags_lower = [tag.lower() for tag in tags]

    return [
        post
        for post in BLOG_POST
        if any(tag["name"].lower() in tags_lower for tag in post.get("tags", []))
    ]


@app.post(
    "/posts",
    response_model=PostPublic,
    response_description="Post Creado (OK)",
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Session = Depends(get_db)):

    new_post = PostORM(title=post.title, content=post.content)

    try:
        db.add(new_post)
        db.commit()
        db.refresh(
            new_post
        )  # Trae los valores de la base de datos, created_at, id, etc
        return new_post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")


@app.put(
    "/posts/{post_id}",
    response_model=PostPublic,
    response_description="Post Actualizado (OK)",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):

    # finder = select(PostORM).where(PostORM.id == post_id)
    # post = db.execute(finder).scalar_one_or_none()

    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    updates = data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(post, key, value)

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):

    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not encontrado")

    db.delete(post)
    db.commit()
    return
