"""
Geo-tagged Disease Mapping Routes
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.routers.auth import get_current_user
from app.database import get_db
from datetime import datetime

router = APIRouter()


class LocationData(BaseModel):
    latitude: float
    longitude: float
    region: Optional[str] = None


class DiseaseReport(BaseModel):
    disease_name: str
    crop_type: str
    severity: str
    confidence: float
    location: LocationData
    image_url: Optional[str] = None


@router.post("/report-disease")
async def report_disease(
    report: DiseaseReport,
    current_user: dict = Depends(get_current_user)
):
    """Report disease with geo-location"""
    
    db = get_db()
    
    disease_report = {
        "user_id": current_user["id"],
        "disease_name": report.disease_name,
        "crop_type": report.crop_type,
        "severity": report.severity,
        "confidence": report.confidence,
        "location": {
            "type": "Point",
            "coordinates": [report.location.longitude, report.location.latitude]
        },
        "region": report.location.region,
        "image_url": report.image_url,
        "created_at": datetime.utcnow()
    }
    
    # Create geospatial index if not exists
    try:
        db.disease_reports.create_index([("location", "2dsphere")])
    except:
        pass
    
    result = await db.disease_reports.insert_one(disease_report)
    
    return {
        "id": str(result.inserted_id),
        "message": "Disease reported successfully"
    }


@router.get("/disease-map")
async def get_disease_map(
    latitude: float,
    longitude: float,
    radius_km: float = 50,
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get disease reports in a radius"""
    
    db = get_db()
    
    # MongoDB geospatial query
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": radius_km * 1000  # Convert km to meters
            }
        }
    }
    
    if crop_type:
        query["crop_type"] = crop_type
    
    cursor = db.disease_reports.find(query).limit(100)
    reports = await cursor.to_list(length=100)
    
    return [
        {
            "id": str(item["_id"]),
            "disease_name": item["disease_name"],
            "crop_type": item["crop_type"],
            "severity": item["severity"],
            "confidence": item["confidence"],
            "latitude": item["location"]["coordinates"][1],
            "longitude": item["location"]["coordinates"][0],
            "region": item.get("region"),
            "created_at": item["created_at"]
        }
        for item in reports
    ]


@router.get("/disease-hotspots")
async def get_disease_hotspots(
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get disease hotspots (areas with high disease frequency)"""
    
    db = get_db()
    
    match_filter = {}
    if crop_type:
        match_filter["crop_type"] = crop_type
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": {
                "lat": {"$arrayElemAt": ["$location.coordinates", 1]},
                "lng": {"$arrayElemAt": ["$location.coordinates", 0]}
            },
            "count": {"$sum": 1},
            "diseases": {"$push": "$disease_name"},
            "avg_severity": {"$avg": {
                "$cond": [
                    {"$eq": ["$severity", "Severe"]}, 3,
                    {"$cond": [
                        {"$eq": ["$severity", "Moderate"]}, 2, 1
                    ]}
                ]
            }}
        }},
        {"$match": {"count": {"$gte": 3}}},  # At least 3 reports
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    
    hotspots = await db.disease_reports.aggregate(pipeline).to_list(length=20)
    
    return [
        {
            "latitude": item["_id"]["lat"],
            "longitude": item["_id"]["lng"],
            "report_count": item["count"],
            "diseases": list(set(item["diseases"])),
            "severity_score": round(item["avg_severity"], 2)
        }
        for item in hotspots
    ]
