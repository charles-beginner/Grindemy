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
