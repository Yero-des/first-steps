from math import ceil
from sys import exception
from typing import List, Literal, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.posts import reposity
from app.core.db import get_db
from app.core.security import get_current_user, oauth2_scheme

from .reposity import PostReposity
from .schemas import PaginatedPost, PostCreate, PostPublic, PostSummary, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


def get_fake_user():
    return {"username": "ricardo", "role": "admin"}


@router.get("/me")
def read_me(user: dict = Depends(get_fake_user)):
    return {"user": user}


@router.get("", response_model=PaginatedPost, response_model_exclude_none=True)
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

    repository = PostReposity(db)

    query = query or text

    total, items = repository.search(query, order_by, direction, page, per_page)

    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

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


@router.get("/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="Una o mas etiquetas Ejemplo: ?tags=python&tags=fastapi",
    ),
    db: Session = Depends(get_db),
):

    reposity = PostReposity(db)

    return reposity.by_tags(tags)


@router.get(
    "/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post encontrado",
    status_code=status.HTTP_200_OK,
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

    repository = PostReposity(db)

    post = repository.get(post_id)

    if not post:
        # Error en caso no se logre encontrar un post
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado"
        )

    return (
        PostPublic.model_validate(post, from_attributes=True)
        if include_content
        else PostSummary.model_validate(post, from_attributes=True)
    )


@router.post(
    "",
    response_model=PostPublic,
    response_description="Post Creado (OK)",
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):

    reposity = PostReposity(db)

    try:
        new_post = reposity.create_post(
            title=post.title,
            content=post.content,
            author=(post.author.model_dump() if post.author else None),
            tags=[tag.model_dump() for tag in post.tags],
        )
        db.commit()
        return new_post

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El titulo ya existe prueba con otro",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el post",
        )


@router.put(
    "/{post_id}",
    response_model=PostPublic,
    response_description="Post Actualizado (OK)",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):

    repository = PostReposity(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado"
        )

    try:
        updates = data.model_dump(exclude_unset=True)
        update_post = repository.update_post(post, updates)

        db.commit()
        return update_post

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el post",
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):

    repository = PostReposity(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not encontrado"
        )

    try:
        repository.delete_post(post)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el post",
        )


@router.get("/secure")
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Acceso con token", "token_recibido": token}
