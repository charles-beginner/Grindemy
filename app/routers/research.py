from fastapi import APIRouter, Query

from app.services.research import daily_concept, fetch_research_papers

router = APIRouter(prefix="/research", tags=["research"])


@router.get("/papers")
def get_papers(topic: str = Query(..., min_length=2)):
    return fetch_research_papers(topic)


@router.get("/concept")
def get_daily_concept():
    return daily_concept()
