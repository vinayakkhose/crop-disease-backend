"""
Disease–Medicine and Fertilizer lookup from CSV datasets.
Uses final_merged_crop_disease_medicine_dataset.csv and
huge_crop_dataset_tomato_potato_corn_sugarcane.csv for medicine and disease analysis.
"""

import os
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any

# Default paths: backend/data/ or user's Downloads (set env to override)
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BACKEND_DIR.parent / "data"
_FNAME_MEDICINE = "final_merged_crop_disease_medicine_dataset.csv"
_FNAME_CROP = "huge_crop_dataset_tomato_potato_corn_sugarcane.csv"
_DEFAULT_MEDICINE_CSV = _DATA_DIR / _FNAME_MEDICINE
_DEFAULT_CROP_CSV = _DATA_DIR / _FNAME_CROP


def _first_existing_path(*paths: Path) -> Optional[Path]:
    """Return the first path that exists."""
    for p in paths:
        if p and p.exists():
            return p
    return None


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def _normalize_disease_for_key(disease: str) -> str:
    """e.g. 'Early Blight' -> 'early blight', 'Tomato_Early_blight' (disease part) -> 'early blight'."""
    s = (disease or "").strip()
    if "_" in s:
        # e.g. "Tomato_Early_blight" -> take "Early blight"
        parts = s.split("_", 1)
        s = parts[1] if len(parts) > 1 else s
    return s.replace("_", " ").strip().lower()


def _parse_class_to_crop_disease(model_class: str) -> tuple:
    """Parse model class e.g. 'Tomato_Early_blight' -> ('Tomato', 'Early Blight')."""
    s = (model_class or "").strip()
    if "_" not in s:
        return ("", s.replace("_", " ").title())
    parts = s.split("_", 1)
    crop = (parts[0] or "").strip().title()
    disease = (parts[1] or "").replace("_", " ").strip().title()
    return (crop, disease)


class DiseaseMedicineLookup:
    """Lookup recommended medicine, pathogen, symptoms, and severity from CSV by crop + disease."""

    def __init__(
        self,
        medicine_csv_path: Optional[str] = None,
        crop_csv_path: Optional[str] = None,
    ):
        # Env or explicit path, then backend/data, then user's Downloads
        downloads = Path.home() / "Downloads"
        def _med_paths():
            if medicine_csv_path:
                yield Path(medicine_csv_path)
            env_med = (os.getenv("MEDICINE_CSV_PATH") or "").strip()
            if env_med:
                yield Path(env_med)
            yield _DEFAULT_MEDICINE_CSV
            yield downloads / _FNAME_MEDICINE
        def _crop_paths():
            if crop_csv_path:
                yield Path(crop_csv_path)
            env_crop = (os.getenv("CROP_DATASET_CSV_PATH") or "").strip()
            if env_crop:
                yield Path(env_crop)
            yield _DEFAULT_CROP_CSV
            yield downloads / _FNAME_CROP
        self.medicine_csv_path = _first_existing_path(*list(_med_paths())) or Path(_DEFAULT_MEDICINE_CSV)
        self.crop_csv_path = _first_existing_path(*list(_crop_paths())) or Path(_DEFAULT_CROP_CSV)
        self._lookup: Dict[tuple, List[Dict]] = {}
        self._load_all()

    def _load_csv(self, path: Path) -> List[Dict]:
        rows = []
        if not path.exists():
            return rows
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()})
        return rows

    def _load_all(self) -> None:
        self._lookup = {}
        for path in (self.medicine_csv_path, self.crop_csv_path):
            if not path.exists():
                continue
            rows = self._load_csv(path)
            for row in rows:
                crop = (row.get("Crop") or "").strip()
                disease = (row.get("Disease") or "").strip()
                if not crop and not disease:
                    continue
                key = (_normalize(crop), _normalize_disease_for_key(disease))
                if key not in self._lookup:
                    self._lookup[key] = []
                self._lookup[key].append(row)
        return None

    def get(
        self,
        crop: str,
        disease: str,
        model_class: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get first matching record for (crop, disease). If crop/disease are empty,
        try to parse model_class e.g. 'Tomato_Early_blight' -> crop=Tomato, disease=Early Blight.
        """
        c = (crop or "").strip()
        d = (disease or "").strip()
        if (not c or not d) and model_class:
            c, d = _parse_class_to_crop_disease(model_class)
        if not c:
            c = "Tomato"  # fallback for display
        key = (_normalize(c), _normalize_disease_for_key(d or model_class or ""))
        records = self._lookup.get(key)
        if not records:
            # Try disease-only match (any crop) for same disease name
            for (nc, nd), recs in self._lookup.items():
                if nd == key[1]:
                    records = recs
                    break
        if not records:
            return None
        r = records[0]
        pathogen = (r.get("Pathogen") or "").strip()
        symptoms = (r.get("Symptoms") or "").strip()
        medicine = (r.get("Recommended_Medicine") or "").strip()
        app_notes = (r.get("Application_Notes") or "").strip()
        severity = (r.get("Severity") or "").strip()
        return {
            "pathogen": pathogen or None,
            "symptoms": symptoms or None,
            "symptoms_list": [s.strip() for s in symptoms.split(";") if s.strip()] if symptoms else [],
            "recommended_medicine": medicine or None,
            "application_notes": app_notes or None,
            "severity": severity or None,
            "crop": c,
            "disease": d,
        }

    def build_treatment_text(self, info: Dict[str, Any]) -> str:
        """Build treatment string from medicine + application notes."""
        if not info:
            return "Consult agricultural expert for treatment."
        parts = []
        if info.get("recommended_medicine"):
            parts.append(f"Recommended medicine: {info['recommended_medicine']}.")
        if info.get("application_notes"):
            parts.append(f"Application: {info['application_notes']}.")
        return " ".join(parts) if parts else "Consult agricultural expert for treatment."

    def build_prevention_list(self, info: Dict[str, Any]) -> List[str]:
        """Optional: add generic prevention tips; can be extended from CSV if a column exists."""
        base = [
            "Use disease-free seeds and healthy planting material.",
            "Practice crop rotation and avoid planting same crop in same area repeatedly.",
            "Maintain proper spacing and avoid overhead watering when possible.",
            "Remove and destroy infected plant debris.",
        ]
        if info and info.get("application_notes"):
            base.insert(0, f"Apply treatment as directed: {info['application_notes']}")
        return base


# Singleton
_disease_medicine_lookup: Optional[DiseaseMedicineLookup] = None


def get_disease_medicine_lookup() -> DiseaseMedicineLookup:
    global _disease_medicine_lookup
    if _disease_medicine_lookup is None:
        _disease_medicine_lookup = DiseaseMedicineLookup()
    return _disease_medicine_lookup
