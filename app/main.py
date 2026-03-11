from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import discussions, health, news, research

app = FastAPI(title="Grindemy Backend", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(health.router)
app.include_router(news.router)
app.include_router(research.router)
app.include_router(discussions.router)
