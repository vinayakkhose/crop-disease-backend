"""
Advanced Prediction Service with All AI Features
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.inference.advanced_predictor import AdvancedAIPredictor, ImageQualityDetector
from src.model_training.advanced_models import DiseaseRiskPredictor
import os
import cv2
import numpy as np
from typing import Dict, Optional


class AdvancedPredictionService:
    """Advanced prediction service with all AI features"""
    
    def __init__(self):
        # Model paths from environment
        model_paths = {
            'disease_model': os.getenv('MODEL_PATH', 'models/crop_disease_model.h5'),
            'severity_model': os.getenv('SEVERITY_MODEL_PATH', 'models/severity_model.h5'),
            'segmentation_model': os.getenv('SEGMENTATION_MODEL_PATH', 'models/segmentation_model.h5'),
            'pest_model': os.getenv('PEST_MODEL_PATH', 'models/pest_model.h5'),
            'growth_stage_model': os.getenv('GROWTH_STAGE_MODEL_PATH', 'models/growth_stage_model.h5'),
        }
        
        self.predictor = None
        self.quality_detector = ImageQualityDetector()
        self.risk_predictor = DiseaseRiskPredictor(use_lstm=True)
        
        try:
            # Try to load advanced predictor (may fail if models don't exist)
            self.predictor = AdvancedAIPredictor(model_paths)
        except Exception as e:
            print(f"Advanced models not available: {e}")
            print("Using basic prediction only")
    
    async def predict_advanced(
        self,
        image_path: str,
        weather_data: Optional[Dict] = None,
        soil_data: Optional[Dict] = None
    ) -> Dict:
        """
        Advanced prediction with all features
        
        Returns:
            Complete prediction with severity, segmentation, pests, etc.
        """
        if self.predictor is None:
            return {
                'error': 'Advanced models not loaded',
                'message': 'Please train advanced models first'
            }
        
        try:
            result = self.predictor.predict_complete(image_path, weather_data, soil_data)
            return result
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Prediction failed'
            }
    
    def detect_image_quality(self, image_path: str) -> Dict:
        """Detect image quality"""
        img = cv2.imread(image_path)
        if img is None:
            return {'error': 'Could not read image'}
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return self.quality_detector.detect_quality(img_rgb)
    
    def predict_disease_risk(self, weather_data: Dict, soil_data: Dict) -> Dict:
        """Predict disease risk from weather and soil data"""
        try:
            return self.risk_predictor.predict_risk(weather_data, soil_data)
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Risk prediction failed'
            }


# Global instance
advanced_prediction_service = AdvancedPredictionService()
