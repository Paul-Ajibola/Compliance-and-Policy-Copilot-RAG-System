"""
Receives thumbs up/down feedback from the frontend on generated answers.
Stored in Postgres so the eval harness (Phase 6) can pull real user
feedback into future golden/trap set refinement.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.models import Feedback

router = APIRouter()


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str  # "up" or "down"
    comment: str | None = None


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, session: AsyncSession = Depends(get_session)):
    session.add(Feedback(
        question=request.question,
        answer=request.answer,
        rating=request.rating,
        comment=request.comment,
    ))
    await session.commit()
    return {"status": "recorded"}