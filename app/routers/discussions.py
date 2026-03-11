from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import DiscussionMessage, DiscussionThread, TopicCluster
from app.schemas import MessageCreate, ThreadCreate

router = APIRouter(prefix="/discussions", tags=["discussions"])


@router.post("/seed")
def seed_threads_from_topics(session: Session = Depends(get_session)) -> dict[str, int]:
    topics = session.exec(select(TopicCluster)).all()
    created = 0
    for topic in topics:
        exists = session.exec(select(DiscussionThread).where(DiscussionThread.topic == topic.hashtag)).first()
        if exists:
            continue
        session.add(DiscussionThread(topic=topic.hashtag))
        created += 1
    session.commit()
    return {"created": created}


@router.get("/threads")
def list_threads(session: Session = Depends(get_session)) -> list[DiscussionThread]:
    return session.exec(select(DiscussionThread).order_by(DiscussionThread.created_at.desc())).all()


@router.post("/threads")
def create_thread(payload: ThreadCreate, session: Session = Depends(get_session)) -> DiscussionThread:
    thread = DiscussionThread(topic=payload.topic)
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


@router.get("/threads/{thread_id}/messages")
def list_messages(thread_id: int, session: Session = Depends(get_session)) -> list[DiscussionMessage]:
    return session.exec(
        select(DiscussionMessage).where(DiscussionMessage.thread_id == thread_id).order_by(DiscussionMessage.created_at.asc())
    ).all()


@router.post("/threads/{thread_id}/messages")
def create_message(
    thread_id: int,
    payload: MessageCreate,
    session: Session = Depends(get_session),
) -> DiscussionMessage:
    thread = session.get(DiscussionThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    message = DiscussionMessage(thread_id=thread_id, author=payload.author, content=payload.content)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
