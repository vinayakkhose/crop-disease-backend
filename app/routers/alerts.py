"""
SMS/WhatsApp Alerts Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.routers.auth import get_current_user
from app.services.sms import sms_service
from app.database import get_db
from datetime import datetime

router = APIRouter()


class AlertRequest(BaseModel):
    message: str
    alert_type: str = "sms"  # sms or whatsapp
    phone_number: Optional[str] = None


@router.post("/send-alert")
async def send_alert(
    request: AlertRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send SMS/WhatsApp alert"""
    
    phone = request.phone_number or current_user.get("phone")
    
    if not phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number is required"
        )
    
    try:
        if request.alert_type == "sms":
            success = await sms_service.send_alert(phone, request.message)
        else:
            # WhatsApp integration can be added here
            success = False
        
        if success:
            # Save alert record
            db = get_db()
            await db.alerts.insert_one({
                "user_id": current_user["id"],
                "phone": phone,
                "message": request.message,
                "alert_type": request.alert_type,
                "status": "sent",
                "created_at": datetime.utcnow()
            })
            
            return {"status": "sent", "message": "Alert sent successfully"}
        else:
            return {"status": "failed", "message": "Failed to send alert"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disease-alert")
async def send_disease_alert(
    disease_name: str,
    severity: str,
    confidence: float,
    crop_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Send automated disease alert"""
    
    message = sms_service.format_disease_alert(
        disease_name, confidence, crop_type
    )
    
    message += f"\nSeverity: {severity}"
    
    if severity == "Severe":
        message += "\n⚠️ URGENT: Take immediate action!"
    
    return await send_alert(
        AlertRequest(message=message, alert_type="sms"),
        current_user
    )


@router.get("/alert-history")
async def get_alert_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user's alert history"""
    
    db = get_db()
    cursor = db.alerts.find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1).limit(limit)
    
    alerts = await cursor.to_list(length=limit)
    
    return [
        {
            "id": str(item["_id"]),
            "message": item["message"],
            "alert_type": item["alert_type"],
            "status": item["status"],
            "created_at": item["created_at"]
        }
        for item in alerts
    ]
