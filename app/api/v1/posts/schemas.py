from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

BAD_WORD = ["fuck", "wtf", "retard", "omg", "xxx", "porn"]


class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Nombre de la etiqueta",
        examples=["Javascript"],
    )

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None

    model_config = ConfigDict(from_attributes=True)


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
    # author: Optional[Author] = None

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

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        for word in BAD_WORD:
            if word in value.lower():
                raise ValueError(f"El titulo no puede contener la palabra: {word}")
        return value

    @field_validator("content")
    @classmethod
    def not_allowed_content(cls, value: str) -> str:
        for word in BAD_WORD:
            if word in value.lower():
                raise ValueError(f"El contenido no puede contener la palabra: '{word}'")
        return value


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
