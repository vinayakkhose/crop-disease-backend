"""
Contact Forms Route — stores messages in the 'contact_messages' collection.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class ContactMessage(BaseModel):
    name: str
    email: str
    message: str


@router.post("/")
async def submit_contact_form(contact: ContactMessage):
    """Save a contact form submission to the contact_messages collection."""
    try:
        from app.database import get_db
        db = get_db()
        await db.contact_messages.insert_one({
            "name":       contact.name,
            "email":      contact.email,
            "message":    contact.message,
            "created_at": datetime.utcnow(),
            "status":     "unread",
        })
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save message: {str(exc)}"
        )

    return {"message": "Message received! We'll get back to you soon."}
