"""
Advanced AI Features Routes
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.routers.auth import get_current_user
from app.services.advanced_prediction import advanced_prediction_service
from app.services.yield_calculator import yield_calculator
from app.services.soil_health import soil_health_analyzer
from app.services.fertilizer_recommender import fertilizer_recommender
from app.database import get_db
from datetime import datetime
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class AdvancedPredictionRequest(BaseModel):
    crop_type: Optional[str] = None
    region: Optional[str] = None
    soil_data: Optional[dict] = None
    weather_data: Optional[dict] = None


class YieldCalculationRequest(BaseModel):
    crop_type: str
    disease_severity: str
    area_hectares: float
    infected_percentage: float


class SoilAnalysisRequest(BaseModel):
    pH: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    organic_matter: Optional[float] = None
    moisture: Optional[float] = None


@router.post("/predict-advanced")
async def predict_advanced(
    file: UploadFile = File(...),
    crop_type: Optional[str] = None,
    region: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Advanced prediction with all AI features"""
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save file
    file_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Get weather data if region provided
        weather_data = None
        if region:
            from app.services.weather import weather_service
            weather_data = await weather_service.get_weather_data(region)
        
        # Advanced prediction
        result = await advanced_prediction_service.predict_advanced(
            str(file_path),
            weather_data=weather_data,
            soil_data=None  # Can be added from request
        )
        
        # Save to database
        db = get_db()
        await db.advanced_predictions.insert_one({
            "user_id": current_user["id"],
            "image_path": str(file_path),
            "prediction": result,
            "crop_type": crop_type,
            "region": region,
            "created_at": datetime.utcnow()
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-image-quality")
async def check_image_quality(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Check image quality before prediction"""
    
    file_path = UPLOAD_DIR / f"quality_check_{datetime.now().timestamp()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    quality = advanced_prediction_service.detect_image_quality(str(file_path))
    return quality


@router.post("/calculate-yield-loss")
async def calculate_yield_loss(
    request: YieldCalculationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Calculate yield loss and financial impact"""
    
    result = yield_calculator.calculate_yield_loss(
        crop_type=request.crop_type,
        disease_severity=request.disease_severity,
        area_hectares=request.area_hectares,
        infected_percentage=request.infected_percentage
    )
    
    # Save calculation
    db = get_db()
    await db.yield_calculations.insert_one({
        "user_id": current_user["id"],
        "calculation": result,
        "created_at": datetime.utcnow()
    })
    
    return result


@router.post("/analyze-soil")
async def analyze_soil(
    request: SoilAnalysisRequest,
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Analyze soil health"""
    
    soil_data = request.dict(exclude_none=True)
    analysis = soil_health_analyzer.analyze_soil(soil_data)
    
    # Get fertilizer recommendation if crop type provided
    fertilizer_rec = None
    if crop_type:
        fertilizer_rec = soil_health_analyzer.recommend_fertilizer(crop_type, soil_data)
        analysis['fertilizer_recommendation'] = fertilizer_rec
    
    # Save analysis
    db = get_db()
    await db.soil_analyses.insert_one({
        "user_id": current_user["id"],
        "soil_data": soil_data,
        "analysis": analysis,
        "crop_type": crop_type,
        "created_at": datetime.utcnow()
    })
    
    return analysis


@router.get("/weather")
async def get_weather(
    region: str,
    current_user: dict = Depends(get_current_user)
):
    """Get weather data and disease risk for a region"""
    from app.services.weather import weather_service
    data = await weather_service.get_weather_data(region)
    if not data:
        raise HTTPException(status_code=400, detail="Could not fetch weather for this region")
    return data


@router.get("/disease-risk-prediction")
async def predict_disease_risk(
    region: str,
    soil_pH: Optional[float] = None,
    soil_nitrogen: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    """Predict disease risk from weather and soil data"""
    
    # Get weather data
    from app.services.weather import weather_service
    weather_data = await weather_service.get_weather_data(region)
    
    if not weather_data:
        raise HTTPException(status_code=400, detail="Could not fetch weather data")
    
    # Prepare soil data
    soil_data = {}
    if soil_pH:
        soil_data['pH'] = soil_pH
    if soil_nitrogen:
        soil_data['nitrogen'] = soil_nitrogen
    
    risk_result = advanced_prediction_service.predict_disease_risk(
        weather_data, soil_data
    )
    
    return {
        "weather_data": weather_data,
        "soil_data": soil_data,
        "risk_prediction": risk_result
    }


@router.post("/recommend-fertilizer")
async def recommend_fertilizer(
    crop_type: str,
    soil_data: dict,
    growth_stage: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get intelligent fertilizer recommendation"""
    
    recommendation = fertilizer_recommender.recommend_fertilizer(
        crop_type=crop_type,
        soil_data=soil_data,
        growth_stage=growth_stage
    )
    
    return recommendation


@router.post("/recommend-pesticide")
async def recommend_pesticide(
    disease_name: str,
    severity: str,
    crop_type: str,
    prefer_organic: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get pesticide recommendation"""
    
    recommendation = fertilizer_recommender.recommend_pesticide(
        disease_name=disease_name,
        severity=severity,
        crop_type=crop_type,
        prefer_organic=prefer_organic
    )
    
    return recommendation


@router.get("/fertilizer-schedule")
async def get_fertilizer_schedule(
    crop_type: str,
    planting_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Get fertilizer application schedule"""
    
    schedule = fertilizer_recommender.get_fertilizer_schedule(
        crop_type=crop_type,
        planting_date=planting_date
    )
    
    return {"schedule": schedule}
