"""
FastAPI Backend for Crop Disease Detection
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from app.routers import auth, predictions, admin, analytics, advanced, chatbot, alerts, mapping, voice, contact
from app.database import connect_db, close_db

load_dotenv()

app = FastAPI(
    title="Crop Disease Detection API",
    description="AI-powered crop disease detection and management system",
    version="1.0.0",
)

# Allowed frontend origins (dev + production from env)
_frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip()
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "*",
]
if _frontend_origin:
    origins.append(_frontend_origin.rstrip("/"))

# CORS middleware - MUST be added before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(advanced.router, prefix="/api/advanced", tags=["Advanced AI"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["AI Chatbot"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(mapping.router, prefix="/api/mapping", tags=["Disease Mapping"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(contact.router, prefix="/api/contact", tags=["Contact"])

@app.on_event("startup")
async def startup_event():
    """Initialize database connection"""
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection"""
    await close_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Crop Disease Detection API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
