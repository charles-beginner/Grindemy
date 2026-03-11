<<<<<<< codex/build-grindemy-webpage-for-news-and-research-rd9adc
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
=======
from fastapi import FastAPI
>>>>>>> main

from app.database import create_db_and_tables
from app.routers import discussions, health, news, research

<<<<<<< codex/build-grindemy-webpage-for-news-and-research-rd9adc
app = FastAPI(title="Grindemy Backend", version="0.2.0")

allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
=======
app = FastAPI(title="Grindemy Backend", version="0.1.0")
>>>>>>> main


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(health.router)
app.include_router(news.router)
app.include_router(research.router)
app.include_router(discussions.router)
