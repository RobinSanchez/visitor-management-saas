from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import get_current_user
from ai_service import ask_ai

router = APIRouter()

@router.post("/chat")
def chat(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    message = request.message

    response, department = ask_ai(message)

    conversation = models.Conversation(
        message=message,
        response=response,
        department=department,
        institution_id=current_user.institution_id
    )

    db.add(conversation)
    db.commit()

    return {
        "response": response,
        "department": department
    }