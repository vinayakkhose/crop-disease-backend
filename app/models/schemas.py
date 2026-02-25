"""
Pydantic Models for API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    FARMER = "farmer"
    ADMIN = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: Role = Role.FARMER
    region: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: Role
    region: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(BaseModel):
    """Login returns token + user so frontend doesn't need a separate /me call."""
    access_token: str
    token_type: str
    user: UserResponse

class PredictionRequest(BaseModel):
    crop_type: Optional[str] = None
    region: Optional[str] = None
    soil_type: Optional[str] = None

class PredictionResult(BaseModel):
    disease_name: str
    confidence: float
    confidence_percent: float
    top_3_predictions: List[Dict[str, Any]]  # e.g. [{"disease": str, "confidence": float}]
    treatment: str
    prevention: List[str]  # list of prevention tips
    crop_health_score: float
    fertilizer_suggestion: Optional[str] = None
    risk_level: str
    demo: Optional[bool] = None
    message: Optional[str] = None
    quality: Optional[str] = None
    not_plant: Optional[bool] = None  # True when image does not appear to be a plant/leaf
    # Disease analysis from CSV (pathogen, symptoms)
    pathogen: Optional[str] = None
    symptoms: Optional[str] = None
    symptoms_list: Optional[List[str]] = None
    severity: Optional[Dict[str, Any]] = None  # e.g. {"severity": "Moderate", "confidence": 0.85}
    soil_recommendations: Optional[List[str]] = None

    class Config:
        extra = "allow"  # allow demo, message, quality from backend

class PredictionHistory(BaseModel):
    id: str
    user_id: str
    image_url: str
    prediction: PredictionResult
    crop_type: Optional[str]
    region: Optional[str]
    created_at: datetime

class DiseaseInfo(BaseModel):
    disease_name: str
    crop_type: str
    symptoms: List[str]
    treatment: str
    prevention: List[str]
    severity: str

class DiseaseInfoCreate(DiseaseInfo):
    pass

class AnalyticsFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    crop_type: Optional[str] = None
    region: Optional[str] = None

class WeatherData(BaseModel):
    humidity: float
    temperature: float
    precipitation: float
    risk_level: str
