from datetime import datetime
from typing import Iterable

import feedparser
from sqlmodel import Session, select

from app.models import NewsArticle

RSS_FEEDS = {
    "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS",
    "technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY",
    "politics": "https://news.google.com/rss/search?q=politics",
    "sustainability": "https://news.google.com/rss/search?q=sustainability",
}


def ingest_google_news(session: Session, categories: Iterable[str] | None = None) -> int:
    targets = categories or RSS_FEEDS.keys()
    inserted = 0

    for category in targets:
        feed_url = RSS_FEEDS.get(category)
        if not feed_url:
            continue

        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            link = entry.get("link")
            if not link:
                continue

            exists = session.exec(select(NewsArticle).where(NewsArticle.link == link)).first()
            if exists:
                continue

            published = datetime.utcnow()
            if entry.get("published_parsed"):
                published = datetime(*entry.published_parsed[:6])

            article = NewsArticle(
                title=entry.get("title", "Untitled"),
                link=link,
                source=entry.get("source", {}).get("title", "Google News"),
                category=category,
                summary=entry.get("summary"),
                published_at=published,
            )
            session.add(article)
            inserted += 1

    session.commit()
    return inserted
