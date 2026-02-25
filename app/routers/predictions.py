"""
Prediction Routes
"""

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
from pathlib import Path
from datetime import datetime

from app.models.schemas import PredictionRequest, PredictionResult
from app.services.prediction import prediction_service
from app.services.weather import weather_service
from app.services.sms import sms_service
from app.routers.auth import get_current_user
from app.database import get_db
from bson import ObjectId
import cv2
import numpy as np

router = APIRouter()

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/predict", response_model=PredictionResult)
async def predict_disease(
    file: UploadFile = File(...),
    crop_type: Optional[str] = Form(None),
    region: Optional[str] = Form(None),
    soil_type: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Predict crop disease from uploaded image"""
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Get prediction (returns demo if model not available)
        result = await prediction_service.predict_disease(
            str(file_path),
            crop_type=crop_type,
            region=region,
            soil_type=soil_type
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Do not save to history when image is not a plant/leaf
        if result.get('not_plant'):
            return PredictionResult(**result)
        
        # Get weather data if region provided
        if region:
            await weather_service.get_weather_data(region)
        
        # Save prediction history
        db = get_db()
        prediction_record = {
            "user_id": current_user["id"],
            "image_url": str(file_path),
            "prediction": result,
            "crop_type": crop_type,
            "region": region,
            "created_at": datetime.utcnow(),
            "demo": result.get("demo", False)
        }
        await db.predictions.insert_one(prediction_record)
        
        # Send SMS alert if high risk (skip for demo)
        if not result.get("demo") and result.get("risk_level") == "high" and current_user.get("phone"):
            try:
                alert_message = sms_service.format_disease_alert(
                    result["disease_name"],
                    result["confidence_percent"],
                    crop_type or "Unknown"
                )
                await sms_service.send_alert(current_user["phone"], alert_message)
            except Exception:
                pass
        
        return PredictionResult(**result)
    
    except HTTPException:
        raise
    except RuntimeError as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=503,
            detail="Prediction model is not available. Please train the model first by running preprocessing and training scripts."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/history")
async def get_prediction_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's prediction history"""
    db = get_db()
    
    cursor = db.predictions.find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1).limit(limit)
    
    predictions = await cursor.to_list(length=limit)
    
    return [
        {
            "id": str(pred["_id"]),
            "disease_name": pred["prediction"]["disease_name"],
            "confidence": pred["prediction"]["confidence_percent"],
            "crop_type": pred.get("crop_type"),
            "created_at": pred["created_at"]
        }
        for pred in predictions
    ]

@router.get("/gradcam/{prediction_id}")
async def get_gradcam(
    prediction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get Grad-CAM visualization for a prediction"""
    db = get_db()
    
    prediction = await db.predictions.find_one({
        "_id": prediction_id,
        "user_id": current_user["id"]
    })
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    image_path = prediction["image_url"]
    gradcam_img = prediction_service.generate_gradcam(image_path)
    
    # Save and return path (or convert to base64)
    gradcam_path = UPLOAD_DIR / f"gradcam_{prediction_id}.jpg"
    cv2.imwrite(str(gradcam_path), cv2.cvtColor(gradcam_img, cv2.COLOR_RGB2BGR))
    
    return {"gradcam_url": str(gradcam_path)}


@router.get("/{prediction_id}")
async def get_prediction_detail(
    prediction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get full prediction details for a specific history item.

    Used by the Reports page when the user clicks a row in Prediction History.
    """
    db = get_db()

    try:
        obj_id = ObjectId(prediction_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid prediction ID")

    prediction = await db.predictions.find_one({
        "_id": obj_id,
        "user_id": current_user["id"]
    })

    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Merge metadata with stored prediction payload
    payload = dict(prediction.get("prediction", {}))
    payload["id"] = str(prediction["_id"])
    payload["created_at"] = prediction.get("created_at")
    payload["crop_type"] = prediction.get("crop_type")
    payload["region"] = prediction.get("region")
    payload["image_url"] = prediction.get("image_url")

    return payload

@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a prediction from history"""
    db = get_db()
    
    try:
        obj_id = ObjectId(prediction_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid prediction ID")
        
    result = await db.predictions.delete_one({
        "_id": obj_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prediction not found or not authorized to delete")
        
    return {"message": "Prediction deleted successfully"}
