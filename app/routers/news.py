from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import NetworkMetric, NewsArticle, TopicCluster
from app.services.analytics import build_keyword_network, build_topic_clusters
from app.services.scraper import ingest_google_news

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/ingest")
def ingest_news(session: Session = Depends(get_session)) -> dict[str, int]:
    inserted = ingest_google_news(session)
    return {"inserted": inserted}


@router.get("/articles")
def list_articles(
    category: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    session: Session = Depends(get_session),
) -> list[NewsArticle]:
    query = select(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(limit)
    if category:
        query = select(NewsArticle).where(NewsArticle.category == category).order_by(NewsArticle.published_at.desc()).limit(limit)
    return session.exec(query).all()


@router.post("/clusters")
def run_clusters(session: Session = Depends(get_session)) -> list[TopicCluster]:
    return build_topic_clusters(session)


@router.get("/clusters")
def get_clusters(session: Session = Depends(get_session)) -> list[TopicCluster]:
    return session.exec(select(TopicCluster).order_by(TopicCluster.article_count.desc())).all()


@router.post("/network")
def run_network(session: Session = Depends(get_session)) -> list[NetworkMetric]:
    return build_keyword_network(session)


@router.get("/network")
def get_network(session: Session = Depends(get_session)) -> list[NetworkMetric]:
    return session.exec(select(NetworkMetric).order_by(NetworkMetric.degree_centrality.desc())).all()
