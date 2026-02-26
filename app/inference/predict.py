"""
Inference module - imports from src/inference/predict
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    from src.inference.predict import AdvancedPredictor
except ModuleNotFoundError:
    AdvancedPredictor = None

__all__ = ['AdvancedPredictor']
