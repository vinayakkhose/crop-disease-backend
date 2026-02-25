"""
AI Farming Chatbot Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.routers.auth import get_current_user
from app.services.chatbot import farming_chatbot
from app.database import get_db
from datetime import datetime

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    context: Optional[dict] = None  # crop_type, region, etc.


class ChatResponse(BaseModel):
    answer: str
    suggestions: List[str]
    type: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Chat with AI farming assistant"""
    
    try:
        response = await farming_chatbot.chat(
            chat_message.message,
            context=chat_message.context
        )
        
        # Save conversation
        db = get_db()
        await db.chat_history.insert_one({
            "user_id": current_user["id"],
            "user_message": chat_message.message,
            "bot_response": response['answer'],
            "context": chat_message.context,
            "created_at": datetime.utcnow()
        })
        
        return ChatResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-history")
async def get_chat_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat history"""
    
    db = get_db()
    cursor = db.chat_history.find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1).limit(limit)
    
    history = await cursor.to_list(length=limit)
    
    return [
        {
            "id": str(item["_id"]),
            "user_message": item["user_message"],
            "bot_response": item["bot_response"],
            "created_at": item["created_at"]
        }
        for item in history
    ]


@router.get("/suggestions")
async def get_suggestions(
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get suggested questions based on context"""
    
    suggestions = [
        "How do I prevent crop diseases?",
        "What fertilizer should I use?",
        "How often should I water my crops?",
        "How to identify pest problems?",
        "What are the best practices for crop rotation?",
        "How to improve soil health?",
        "When is the best time to harvest?",
        "How to store harvested crops?"
    ]
    
    if crop_type:
        suggestions.insert(0, f"How to care for {crop_type}?")
        suggestions.insert(1, f"What diseases affect {crop_type}?")
    
    return {"suggestions": suggestions}
