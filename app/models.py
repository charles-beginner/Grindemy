from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class NewsArticle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: str = Field(index=True, unique=True)
    source: str
    category: str
    summary: Optional[str] = None
    published_at: datetime = Field(default_factory=datetime.utcnow)


class TopicCluster(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashtag: str = Field(index=True)
    label: str
    article_count: int = 0
    score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NetworkMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    degree_centrality: float
    betweenness_centrality: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiscussionThread(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiscussionMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="discussionthread.id", index=True)
    author: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
