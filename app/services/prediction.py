"""
Prediction Service
"""

import cv2
import numpy as np
from pathlib import Path
import json
from typing import Dict, Optional, List, Any
import sys
import os

# Add project root to import path so we can use src.inference.predict
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
try:
    from src.inference.predict import AdvancedPredictor
except ModuleNotFoundError:
    AdvancedPredictor = None

from app.services.disease_medicine_lookup import get_disease_medicine_lookup
from app.services.fertilizer_recommender import fertilizer_recommender


class PredictionService:
    """Service for crop disease prediction"""

    def __init__(self):
        """
        Initialize prediction service.

        We resolve model and mapping paths relative to the project root so the
        backend works out-of-the-box without requiring a .env file.
        """
        project_root = Path(__file__).resolve().parents[3]

        default_model_path = project_root / "models" / "crop_disease_model.h5"
        default_mapping_path = project_root / "data" / "processed" / "class_mapping.json"

        model_path = os.getenv("MODEL_PATH", str(default_model_path))
        class_mapping_path = os.getenv("CLASS_MAPPING_PATH", str(default_mapping_path))

        self.predictor = None
        self.initialization_error: Optional[str] = None

        try:
            if AdvancedPredictor is None:
                raise FileNotFoundError("Inference module not found (Backend running in lightweight mode).")
            self.predictor = AdvancedPredictor(model_path, class_mapping_path)
        except FileNotFoundError as e:
            # Model or mapping file is missing – keep backend running and provide clear error later
            self.initialization_error = (
                "Model or class mapping file not found. "
                "Make sure you have run preprocessing and training to create:\n"
                f"  - Model path: {model_path}\n"
                f"  - Class mapping: {class_mapping_path}\n"
                f"Original error: {e}"
            )
            print(self.initialization_error)
        except Exception as e:
            # Catch other initialization errors so the app can start
            self.initialization_error = f"Failed to initialize prediction model: {e}"
            print(self.initialization_error)

        self.disease_info = self._load_disease_info()
        self.demo_mode = self.predictor is None
    
    def _load_disease_info(self) -> Dict:
        """Load disease information"""
        return {
            "Tomato_Bacterial_spot": {
                "treatment": "Apply copper-based fungicides. Remove infected leaves. Maintain proper spacing.",
                "prevention": ["Use disease-free seeds", "Practice crop rotation", "Avoid overhead watering"],
                "severity": "moderate"
            },
            "Tomato_Early_blight": {
                "treatment": "Apply fungicides containing chlorothalonil or mancozeb. Remove lower leaves.",
                "prevention": ["Mulch around plants", "Water at base", "Remove plant debris"],
                "severity": "moderate"
            },
            # Add more disease info
        }
    
    async def predict_disease(
        self,
        image_path: str,
        crop_type: Optional[str] = None,
        region: Optional[str] = None,
        soil_type: Optional[str] = None,
    ) -> Dict:
        """
        Predict crop disease
        
        Args:
            image_path: Path to uploaded image
            crop_type: Type of crop
            region: Region/location
            soil_type: Soil type
            
        Returns:
            Prediction result dictionary
        """
        # First check if it's remotely a plant using simple heuristic
        if not self._is_valid_image(image_path):
            return self._sanitize_result({
                "disease_name": "Not a plant leaf",
                "confidence": 0.0,
                "confidence_percent": 0.0,
                "top_3_predictions": [],
                "treatment": "",
                "prevention": [],
                "crop_health_score": 0.0,
                "fertilizer_suggestion": None,
                "risk_level": "low",
                "quality": "poor",
                "not_plant": True,
                "message": "This is not a disease prediction. The image does not appear to be a crop or plant leaf (e.g. it may be a person, bird, animal, or soil). Please upload a clear photo of a plant leaf for disease detection.",
            })

        if self.predictor is None:
            # Model is not available – return demo prediction for testing
            # This allows the app to work even without trained model
            return self.get_demo_prediction(crop_type or "Tomato")

        # Get prediction
        result = self.predictor.predict_with_confidence(image_path, top_k=3)
        
        if 'error' in result:
            return result
        
        top_prediction = result['top_prediction']
        confidence = top_prediction['confidence']
        
        # If confidence is very low, image likely not a plant/leaf (e.g. human, object)
        NOT_PLANT_CONFIDENCE_THRESHOLD = 0.28
        if confidence < NOT_PLANT_CONFIDENCE_THRESHOLD:
            return self._sanitize_result({
                "disease_name": "Not a plant leaf",
                "confidence": float(confidence),
                "confidence_percent": float(top_prediction.get('confidence_percent', 0)),
                "top_3_predictions": [
                    {"disease": pred.get('disease_name', ''), "confidence": float(pred.get('confidence_percent', 0))}
                    for pred in result.get('predictions', [])
                ],
                "treatment": "",
                "prevention": [],
                "crop_health_score": 0.0,
                "fertilizer_suggestion": None,
                "risk_level": "low",
                "quality": result.get('quality'),
                "not_plant": True,
                "message": "This is not a disease prediction. The image does not appear to be a crop or plant leaf (e.g. it may be a person, bird, animal, or soil). Please upload a clear photo of a plant leaf for disease detection.",
            })
        
        disease_class = top_prediction['class']
        disease_name_display = top_prediction['disease_name']
        effective_crop = crop_type or self._crop_from_class(disease_class)

        # Look up medicine and disease analysis from CSV datasets
        lookup = get_disease_medicine_lookup()
        csv_info = lookup.get(effective_crop, disease_name_display, disease_class)

        if csv_info:
            treatment = lookup.build_treatment_text(csv_info)
            prevention = lookup.build_prevention_list(csv_info)
            severity_from_csv = csv_info.get("severity") or "unknown"
        else:
            disease_info = self.disease_info.get(disease_class, {
                "treatment": "Consult agricultural expert",
                "prevention": ["Maintain proper crop hygiene", "Monitor regularly"],
                "severity": "unknown"
            })
            treatment = disease_info["treatment"]
            prevention = disease_info["prevention"]
            severity_from_csv = disease_info["severity"]

        # Calculate crop health score
        health_score = self._calculate_health_score(top_prediction['confidence'])
    
        # Fertilizer suggestion: use recommender (crop-based) from CSV-backed logic
        fertilizer = self._get_fertilizer_suggestion(effective_crop, soil_type, csv_info)

        # Soil and field recommendations to help farmers
        soil_recommendations = self._get_soil_recommendations(
            effective_crop,
            soil_type,
            risk_level_hint=severity_from_csv,
        )

        # Determine risk level (use CSV severity when available)
        risk_level = self._determine_risk_level(top_prediction['confidence'], severity_from_csv)
    
        out: Dict[str, Any] = {
            "disease_name": disease_name_display,
            "confidence": top_prediction['confidence'],
            "confidence_percent": top_prediction['confidence_percent'],
            "top_3_predictions": [
                {
                    "disease": pred['disease_name'],
                    "confidence": pred['confidence_percent']
                }
                for pred in result['predictions']
            ],
            "treatment": treatment,
            "prevention": prevention,
            "crop_health_score": health_score,
            "fertilizer_suggestion": fertilizer,
            "soil_recommendations": soil_recommendations,
            "risk_level": risk_level,
            "quality": result['quality'],
        }
        # Disease analysis from CSV (pathogen, symptoms, severity)
        if csv_info:
            if csv_info.get("pathogen"):
                out["pathogen"] = csv_info["pathogen"]
            if csv_info.get("symptoms"):
                out["symptoms"] = csv_info["symptoms"]
            if csv_info.get("symptoms_list"):
                out["symptoms_list"] = csv_info["symptoms_list"]
            if csv_info.get("severity"):
                out["severity"] = {
                    "severity": csv_info["severity"],
                    "confidence": float(top_prediction['confidence']),
                }
        return self._sanitize_result(out)
    
    def _is_valid_image(self, image_path: str) -> bool:
        """
        Heuristic check to detect non-plant images (e.g., human photos).
        Returns False if the image is detected as not a plant.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return True
                
            # Face detection using OpenCV Haar Cascades
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
            
            if len(faces) > 0:
                # If a large face is detected (more than 5% of image area), reject it
                for (x, y, w, h) in faces:
                    if (w * h) > (img.shape[0] * img.shape[1] * 0.05):
                        return False
            
            # Color heuristic: Plant leaves usually have some green/yellow/brown
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # define ranges for plant colors
            lower_green = np.array([25, 40, 40])
            upper_green = np.array([90, 255, 255])
            mask_g = cv2.inRange(hsv, lower_green, upper_green)
            
            lower_yb = np.array([10, 40, 40])
            upper_yb = np.array([30, 255, 255])
            mask_yb = cv2.inRange(hsv, lower_yb, upper_yb)
            
            plant_pixels = cv2.countNonZero(mask_g) + cv2.countNonZero(mask_yb)
            total_pixels = img.shape[0] * img.shape[1]
            
            # Less than 1% plant colors -> likely not a plant
            if total_pixels > 0 and (plant_pixels / total_pixels) < 0.01:
                return False
                
            return True
        except Exception:
            return True

    def _crop_from_class(self, disease_class: str) -> str:
        """Infer crop from model class e.g. Tomato_Early_blight -> Tomato."""
        if not disease_class or "_" not in disease_class:
            return "Tomato"
        return disease_class.split("_", 1)[0].strip().title()

    def _get_fertilizer_suggestion(
        self,
        crop_type: Optional[str],
        soil_type: Optional[str],
        csv_info: Optional[Dict],
    ) -> Optional[str]:
        """Suggest fertilizer using recommender (CSV-backed crop requirements)."""
        if not crop_type:
            return "Consult soil test for specific recommendations."
        try:
            rec = fertilizer_recommender.recommend_fertilizer(
                crop_type, {}, growth_stage=None
            )
            fert = rec.get("fertilizer")
            timing = rec.get("application_timing", "")
            if fert and timing:
                return f"{fert}. Apply: {timing}."
            return fert or "Balanced NPK fertilizer."
        except Exception:
            return "Balanced NPK fertilizer. Consult soil test for specific recommendations."

    def _get_soil_recommendations(
        self,
        crop_type: Optional[str],
        soil_type: Optional[str],
        risk_level_hint: Optional[str] = None,
    ) -> List[str]:
        """
        High-level soil and field advice to help farmers.

        This does not require lab soil data – it gives practical tips
        based on crop type, soil type selection, and disease severity.
        """
        tips: List[str] = []

        # Generic best practices
        tips.append("Avoid waterlogging and ensure proper drainage around the crop.")
        tips.append("Add well‑decomposed organic matter (compost or farmyard manure) to improve soil structure.")

        if soil_type:
            st = soil_type.lower()
            if "sandy" in st:
                tips.append("Sandy soil: increase organic matter and use mulching to reduce moisture loss.")
                tips.append("Irrigate more frequently with smaller amounts to avoid nutrient leaching.")
            elif "clay" in st:
                tips.append("Clay soil: avoid working the soil when very wet to prevent compaction.")
                tips.append("Create raised beds or ridges to improve drainage and root aeration.")
            elif "loam" in st or "loamy" in st:
                tips.append("Loamy soil: maintain organic matter levels to keep the soil friable and fertile.")

        if crop_type:
            ct = crop_type.lower()
            if "tomato" in ct:
                tips.append("Tomato prefers well‑drained loamy soil with pH 6.0–7.0 and good organic matter.")
            elif "potato" in ct:
                tips.append("Potato does best in loose, well‑drained sandy‑loam soil to allow tuber expansion.")
            elif "corn" in ct or "maize" in ct:
                tips.append("Corn needs fertile, well‑drained soil; keep adequate nitrogen and avoid hardpan layers.")
            elif "rice" in ct:
                tips.append("Rice prefers puddled clay or clay‑loam soil with good water‑holding capacity.")
            elif "wheat" in ct:
                tips.append("Wheat grows well in well‑drained loam with moderate organic matter and pH 6.0–7.5.")

        if risk_level_hint and str(risk_level_hint).lower() in {"high", "severe"}:
            tips.append("Because disease risk/severity is high, avoid excessive nitrogen and keep the field clean of residues.")

        # Remove duplicates while preserving order
        seen = set()
        unique_tips: List[str] = []
        for tip in tips:
            if tip not in seen:
                seen.add(tip)
                unique_tips.append(tip)

        return unique_tips

    def _sanitize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all numeric values are native Python for JSON serialization; ensure required keys exist."""
        def to_float(x: Any) -> float:
            if x is None:
                return 0.0
            try:
                return float(x)
            except (TypeError, ValueError):
                return 0.0

        out = dict(result)
        out["disease_name"] = str(out.get("disease_name") or "Unknown")
        out["confidence"] = to_float(out.get("confidence"))
        out["confidence_percent"] = to_float(out.get("confidence_percent"))
        out["crop_health_score"] = to_float(out.get("crop_health_score"))
        out["treatment"] = str(out.get("treatment") or "")
        prev = out.get("prevention")
        out["prevention"] = list(prev) if isinstance(prev, list) else []
        out["risk_level"] = str(out.get("risk_level") or "low")
        soil_recs = out.get("soil_recommendations")
        if isinstance(soil_recs, list):
            out["soil_recommendations"] = [str(t) for t in soil_recs]
        else:
            out["soil_recommendations"] = []
        preds = out.get("top_3_predictions") or []
        out["top_3_predictions"] = [
            {"disease": str(p.get("disease", "")), "confidence": to_float(p.get("confidence"))}
            for p in preds
        ]
        if "severity" in out and isinstance(out["severity"], dict):
            s = out["severity"]
            out["severity"] = {"severity": str(s.get("severity", "")), "confidence": to_float(s.get("confidence"))}
        return out

    def _calculate_health_score(self, confidence: float) -> float:
        """Calculate crop health score"""
        # Higher confidence in disease = lower health score
        health_score = (1 - confidence) * 100
        return round(health_score, 2)
    
    def _determine_risk_level(self, confidence: float, severity: str) -> str:
        """Determine risk level"""
        if confidence > 0.8 and severity in ["high", "moderate"]:
            return "high"
        elif confidence > 0.6:
            return "moderate"
        return "low"
    
    def get_demo_prediction(self, crop_type: str = "Tomato") -> Dict:
        """Return a demo prediction for testing when model is not available."""
        demo_diseases = {
            "Tomato": {
                "disease_name": "Bacterial Spot",
                "class": "Tomato_Bacterial_spot",
                "confidence": 0.85,
                "confidence_percent": 85,
            },
            "Potato": {
                "disease_name": "Early Blight",
                "class": "Potato_Early_blight",
                "confidence": 0.78,
                "confidence_percent": 78,
            },
            "Corn": {
                "disease_name": "Common Rust",
                "class": "Corn_Common_rust",
                "confidence": 0.72,
                "confidence_percent": 72,
            },
            "Sugarcane": {
                "disease_name": "Red Rot",
                "class": "Sugarcane_Red_rot",
                "confidence": 0.75,
                "confidence_percent": 75,
            },
        }
        demo = demo_diseases.get(crop_type, demo_diseases["Tomato"])
        lookup = get_disease_medicine_lookup()
        csv_info = lookup.get(crop_type, demo["disease_name"], demo["class"])
        if csv_info:
            treatment = lookup.build_treatment_text(csv_info)
            prevention = lookup.build_prevention_list(csv_info)
            severity_from_csv = csv_info.get("severity") or "moderate"
        else:
            treatment = "Apply appropriate fungicides. Consult agricultural expert for specific treatment."
            prevention = ["Use disease-free seeds", "Practice crop rotation", "Maintain proper spacing", "Monitor regularly"]
            severity_from_csv = "moderate"

        fertilizer = self._get_fertilizer_suggestion(crop_type, None, csv_info)
        out: Dict[str, Any] = {
            "disease_name": demo["disease_name"],
            "confidence": demo["confidence"],
            "confidence_percent": demo["confidence_percent"],
            "top_3_predictions": [
                {"disease": demo["disease_name"], "confidence": demo["confidence_percent"]},
                {"disease": f"{crop_type} Healthy", "confidence": 10},
                {"disease": f"{crop_type} Other", "confidence": 5},
            ],
            "treatment": treatment,
            "prevention": prevention,
            "crop_health_score": round((1 - demo["confidence"]) * 100, 2),
            "fertilizer_suggestion": fertilizer,
            "risk_level": "moderate" if demo["confidence_percent"] > 70 else "low",
            "quality": "good",
            "demo": True,
            "message": "This is a demo prediction. Train the model for accurate results.",
        }
        if csv_info:
            if csv_info.get("pathogen"):
                out["pathogen"] = csv_info["pathogen"]
            if csv_info.get("symptoms"):
                out["symptoms"] = csv_info["symptoms"]
            if csv_info.get("symptoms_list"):
                out["symptoms_list"] = csv_info["symptoms_list"]
            if csv_info.get("severity"):
                out["severity"] = {"severity": csv_info["severity"], "confidence": float(demo["confidence"])}
        return self._sanitize_result(out)
    
    def generate_gradcam(self, image_path: str) -> np.ndarray:
        """Generate Grad-CAM visualization"""
        if self.predictor is None:
            raise RuntimeError(
                self.initialization_error
                or "Prediction model is not initialized. Please train the model first."
            )
        _, gradcam_img = self.predictor.generate_gradcam(image_path)
        return gradcam_img


# Global instance (lazy-safe: will not crash app even if model files are missing)
prediction_service = PredictionService()
