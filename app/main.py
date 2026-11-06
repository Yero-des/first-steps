from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.api.v1.auth.router import router as auth_router
from app.api.v1.posts.router import router as post_router
from app.core.db import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")

    # Migracion temporal
    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)

    return app


app = create_app()
