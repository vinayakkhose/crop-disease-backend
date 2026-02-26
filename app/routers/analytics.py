"""
Analytics Routes
"""

from fastapi import APIRouter, Depends
from typing import List, Optional
from datetime import datetime
from app.models.schemas import AnalyticsFilter
from app.routers.auth import get_current_user
from app.database import get_db
from pymongo import DESCENDING

router = APIRouter()

@router.get("/available-crops")
async def get_available_crops(
    current_user: dict = Depends(get_current_user)
):
    """Get list of unique crops the user has predicted"""
    db = get_db()
    
    pipeline = [
        {"$match": {"user_id": current_user["id"], "crop_type": {"$exists": True, "$ne": None, "$ne": ""}}},
        {"$group": {"_id": "$crop_type"}},
        {"$sort": {"_id": 1}}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(length=100)
    return [item["_id"] for item in results if item["_id"]]
@router.get("/disease-frequency")
async def get_disease_frequency(
    crop_type: Optional[str] = None,
    region: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get disease frequency statistics"""
    db = get_db()
    
    match_filter = {"user_id": current_user["id"]}
    if crop_type:
        match_filter["crop_type"] = crop_type
    if region:
        match_filter["region"] = region
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": "$prediction.disease_name",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(length=50)
    
    return [
        {"disease": item["_id"], "count": item["count"]}
        for item in results
    ]

@router.get("/crop-health")
async def get_crop_health_stats(
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get crop health statistics (overall or filtered by crop)"""
    db = get_db()
    
    match_filter = {"user_id": current_user["id"]}
    if crop_type:
        match_filter["crop_type"] = crop_type
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": "$crop_type",
            "avg_health_score": {"$avg": "$prediction.crop_health_score"},
            "count": {"$sum": 1}
        }}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(length=20)
    
    return [
        {
            "crop": item["_id"] if item["_id"] else "Not specified",
            "avg_health_score": round(item["avg_health_score"] or 0, 2),
            "total_predictions": item["count"]
        }
        for item in results
    ]

@router.get("/monthly-trends")
async def get_monthly_trends(
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get monthly disease trends (overall or filtered by crop)"""
    db = get_db()
    
    match_filter = {"user_id": current_user["id"]}
    if crop_type:
        match_filter["crop_type"] = crop_type
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"}
            },
            "count": {"$sum": 1},
            "diseases": {"$push": "$prediction.disease_name"}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(length=24)
    
    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return [
        {
            "year": item["_id"]["year"],
            "month": item["_id"]["month"],
            "month_label": f"{month_names[item['_id']['month']]} {item['_id']['year']}",
            "total_predictions": item["count"],
            "unique_diseases": len(set(item["diseases"])) if item.get("diseases") else 0
        }
        for item in results
    ]

@router.get("/region-wise")
async def get_region_wise_stats(
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get region-wise disease spread (only predictions that have region set)"""
    db = get_db()
    
    match_filter = {
        "user_id": current_user["id"],
        "region": {"$exists": True, "$nin": [None, ""]}
    }
    if crop_type:
        match_filter["crop_type"] = crop_type
    
    pipeline = [
        {"$match": match_filter},
        {"$group": {
            "_id": "$region",
            "count": {"$sum": 1},
            "diseases": {"$push": "$prediction.disease_name"}
        }},
        {"$sort": {"count": -1}}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(length=50)
    
    return [
        {
            "region": item["_id"],
            "total_predictions": item["count"],
            "unique_diseases": len(set(item["diseases"]))
        }
        for item in results
    ]

@router.get("/summary")
async def get_analytics_summary(
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Combined endpoint: disease-frequency + crop-health + monthly-trends
    in one round-trip running all three aggregations concurrently.
    """
    import asyncio

    db = get_db()
    uid = current_user["id"]
    base: dict = {"user_id": uid}
    if crop_type:
        base["crop_type"] = crop_type

    disease_pipe = [
        {"$match": base},
        {"$group": {"_id": "$prediction.disease_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    health_pipe = [
        {"$match": base},
        {"$group": {
            "_id": "$crop_type",
            "avg_health_score": {"$avg": "$prediction.crop_health_score"},
            "count": {"$sum": 1},
        }},
        {"$limit": 10},
    ]
    trends_pipe = [
        {"$match": base},
        {"$group": {
            "_id": {"year": {"$year": "$created_at"}, "month": {"$month": "$created_at"}},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {"$limit": 12},
    ]

    d_res, h_res, t_res = await asyncio.gather(
        db.predictions.aggregate(disease_pipe).to_list(length=10),
        db.predictions.aggregate(health_pipe).to_list(length=10),
        db.predictions.aggregate(trends_pipe).to_list(length=12),
    )

    months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return {
        "diseaseFrequency": [
            {"disease": r["_id"], "count": r["count"]} for r in d_res
        ],
        "cropHealth": [
            {
                "crop": r["_id"] or "Not specified",
                "avg_health_score": round(r["avg_health_score"] or 0, 2),
                "total_predictions": r["count"],
            }
            for r in h_res
        ],
        "trends": [
            {
                "year": r["_id"]["year"],
                "month": r["_id"]["month"],
                "month_label": f"{months[r['_id']['month']]} {r['_id']['year']}",
                "total_predictions": r["count"],
            }
            for r in t_res
        ],
    }
