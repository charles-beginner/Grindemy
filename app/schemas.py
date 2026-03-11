from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ThreadCreate(BaseModel):
    topic: str


class MessageCreate(BaseModel):
    author: str
    content: str


class ResearchPaper(BaseModel):
    title: str
    authors: str
    abstract: Optional[str] = None
    doi: Optional[str] = None
    link: Optional[str] = None


class ConceptCard(BaseModel):
    finance_concept: str
    sustainability_concept: str
    date: datetime


class KMeansPoint(BaseModel):
    article_id: int
    title: str
    category: str
    cluster_id: int
    cluster_hashtag: str
    x: float
    y: float


class KMeansVisualization(BaseModel):
    points: list[KMeansPoint]


class NetworkNode(BaseModel):
    id: str
    label: str
    degree_centrality: float
    betweenness_centrality: float


class NetworkEdge(BaseModel):
    source: str
    target: str
    weight: float


class NetworkVisualization(BaseModel):
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
